---
name: wms-inventory-warehouse-control
metadata:
  category: Supply Chain and Logistics Tech
description: Architect Warehouse Management Systems (WMS) and multi-location inventory control engines. Implement SKU tracking, aisle-rack-bin location hierarchies, FIFO/FEFO expiration turnover, barcode/RFID scanning workflows, safety stock replenishment thresholds, and cycle count reconciliation. Trigger when building inventory management backends, warehouse logistics, or stock replenishment services.
compatibility: Relational databases (PostgreSQL/MySQL), Barcode GS1-128
---

# Warehouse Management & Inventory Control Skill Guide

This skill governs data modeling, stock movements, and operational workflows for high-reliability Warehouse Management Systems (WMS).

---

## 1. Physical Warehouse Hierarchy & Stock Movements

```text
[ Warehouse Facility ]
         |
         +---> [ Zone: Ambient / Cold Storage / Hazardous ]
                 |
                 +---> [ Aisle ]
                         |
                         +---> [ Rack / Shelf ]
                                 |
                                 +---> [ Bin: Specific Pick Location (e.g. A-04-02-B) ]
                                         |
                                         v
                      [ Inventory Lot (SKU + Lot # + Expiry Date) ]
```

---

## 2. Production Database Schema & Ledger Architecture

Inventory must **never** be managed by simply mutating an integer count; all stock changes must use an **immutable transaction ledger** (Stock Move Log).

```sql
-- 1. Locations Hierarchy
CREATE TABLE warehouse_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    warehouse_code VARCHAR(16) NOT NULL,
    zone VARCHAR(32) NOT NULL,
    aisle VARCHAR(16) NOT NULL,
    rack VARCHAR(16) NOT NULL,
    bin VARCHAR(16) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT uq_bin_code UNIQUE (warehouse_code, zone, aisle, rack, bin)
);

-- 2. Inventory Batches / Lots (Supports FEFO: First Expired, First Out)
CREATE TABLE inventory_lots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku VARCHAR(64) NOT NULL,
    lot_number VARCHAR(64) NOT NULL,
    manufactured_at DATE,
    expires_at DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT clock_timestamp()
);

-- 3. Immutable Stock Movement Ledger
CREATE TYPE movement_type AS ENUM ('RECEIPT', 'PUTAWAY', 'PICK', 'TRANSFER', 'CYCLE_COUNT_ADJUSTMENT');

CREATE TABLE stock_movements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lot_id UUID NOT NULL REFERENCES inventory_lots(id),
    from_location_id UUID REFERENCES warehouse_locations(id), -- NULL for inbound receipts
    to_location_id UUID REFERENCES warehouse_locations(id),   -- NULL for shipped orders
    quantity NUMERIC(12, 4) NOT NULL CHECK (quantity > 0),
    move_type movement_type NOT NULL,
    reference_order_id VARCHAR(64),
    performed_by_user UUID NOT NULL,
    recorded_at TIMESTAMPTZ DEFAULT clock_timestamp()
);

CREATE INDEX idx_stock_movements_lot ON stock_movements(lot_id);
CREATE INDEX idx_stock_movements_to ON stock_movements(to_location_id);
CREATE INDEX idx_stock_movements_from ON stock_movements(from_location_id);
```

### Automated Reorder / Replenishment Query

```sql
-- Identifies SKUs falling below calculated Safety Stock + Reorder Point
WITH current_stock AS (
    SELECT 
        l.sku,
        COALESCE(SUM(CASE WHEN m.to_location_id IS NOT NULL THEN m.quantity ELSE 0 END), 0) -
        COALESCE(SUM(CASE WHEN m.from_location_id IS NOT NULL THEN m.quantity ELSE 0 END), 0) AS on_hand_qty
    FROM inventory_lots l
    JOIN stock_movements m ON l.id = m.lot_id
    GROUP BY l.sku
)
SELECT 
    s.sku,
    s.on_hand_qty,
    p.reorder_point,
    p.safety_stock,
    (p.optimal_order_qty) AS suggested_replenishment_units
FROM current_stock s
JOIN product_reorder_policies p ON s.sku = p.sku
WHERE s.on_hand_qty <= p.reorder_point;
```

---

## 3. Operational Best Practices

1. **FEFO Allocation:** For perishable or medical goods, always prioritize picking from the lot with the earliest `expires_at` date to minimize waste.
2. **Two-Step Picking & Staging:** Separate high-speed bin picking from packing/staging to optimize worker travel paths.
3. **Discrepancy Approvals:** Cycle count variances exceeding a configured threshold (e.g., $100 or 5% of bin quantity) must require supervisor biometric or two-factor sign-off.
