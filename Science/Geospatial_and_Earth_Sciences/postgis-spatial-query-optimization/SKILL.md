---
name: postgis-spatial-query-optimization
metadata:
  category: Geospatial and GIS Engineering
description: Architect, index, and optimize spatial databases using PostgreSQL and PostGIS. Master geometry vs geography data types, spatial reference systems (SRID 4326 vs 3857), GiST and SP-GiST indexing, spatial joins, K-Nearest Neighbor (KNN) distance queries, and spatial clustering with ST_ClusterDBSCAN. Trigger when designing GIS schemas, optimizing geo-queries, or processing spatial datasets.
compatibility: PostgreSQL 14+, PostGIS 3.3+
---

# PostGIS Spatial Query Optimization Skill Guide

This skill establishes database modeling standards and query optimization strategies for high-volume geospatial systems using PostgreSQL and the PostGIS extension.

---

## 1. Spatial Indexing & Coordinate Systems

```text
[ Coordinate System Reference (SRID) ]
  |-- EPSG:4326 (WGS 84): Unprojected Lat/Long in degrees (GPS standard)
  |-- EPSG:3857 (Web Mercator): Projected coordinates in meters (Tile rendering)
  |
  v
[ PostGIS Column Storage ]
  |-- GEOMETRY: Flat Euclidean planar calculations (Fast, accurate on local scales)
  |-- GEOGRAPHY: Spheroidal great-circle calculations (Accurate globally across poles/equator)
  |
  v
[ Spatial Indexing (GiST / SP-GiST) ]
  +---> R-Tree Bounding Box (BBOX) index eliminates 99%+ of non-intersecting shapes
```

---

## 2. Production SQL Patterns & Optimization

### A. Schema Definition with Spatial Indexing

```sql
-- Enable PostGIS extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- High-performance delivery zones table
CREATE TABLE delivery_zones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL,
    zone_name VARCHAR(100) NOT NULL,
    boundary GEOMETRY(Polygon, 4326) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT clock_timestamp()
);

-- Bounding Box R-Tree Index
CREATE INDEX idx_delivery_zones_boundary ON delivery_zones USING GIST (boundary);

-- Driver tracking with Geography for real-world meter accuracy
CREATE TABLE driver_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    driver_id UUID NOT NULL,
    current_location GEOGRAPHY(Point, 4326) NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_driver_locations_geog ON driver_locations USING GIST (current_location);
```

### B. K-Nearest Neighbor (KNN) Index-Accelerated Query

```sql
-- Finds the 5 closest available drivers within 10 km (10,000 meters)
-- PostGIS `<->` operator performs indexed bounding box distance search
WITH target_pickup AS (
    SELECT ST_SetSRID(ST_MakePoint(-122.4194, 37.7749), 4326)::geography AS pickup_geom
)
SELECT 
    d.driver_id,
    ST_Distance(d.current_location, t.pickup_geom) AS distance_meters
FROM driver_locations d, target_pickup t
WHERE ST_DWithin(d.current_location, t.pickup_geom, 10000) -- Restricts search radius
ORDER BY d.current_location <-> t.pickup_geom
LIMIT 5;
```

### C. Spatial Join with Bounding Box Pre-Filter

```sql
-- Check which orders fall inside active merchant delivery zones
SELECT 
    o.id AS order_id,
    z.zone_name,
    z.merchant_id
FROM orders o
JOIN delivery_zones z 
    ON z.boundary && o.delivery_location -- Fast Bounding Box overlap pre-filter
    AND ST_Contains(z.boundary, o.delivery_location) -- Exact polygon evaluation
WHERE z.merchant_id = 'c38a264a-251f-4ffb-88a4-0ef6630f9ec9';
```

---

## 3. Performance Best Practices

1. **Bounding Box Pre-Filtering (`&&`):** PostGIS functions like `ST_Intersects` and `ST_Contains` automatically use bounding box checks, but when writing custom filters, always leverage `&&` to engage GiST indexes.
2. **Transformations in Queries:** Never run `ST_Transform(column, 3857)` in a `WHERE` clause without a functional index; transform input literals instead:
   ```sql
   -- FAST: transforms literal, keeps index active
   WHERE geom && ST_Transform(ST_MakePoint(...), 4326)
   ```
3. **Clustering & Vacuuming:** Regularly execute `CLUSTER delivery_zones USING idx_delivery_zones_boundary` on read-heavy spatial tables to align on-disk storage with Hilbert curve spatial locality.
