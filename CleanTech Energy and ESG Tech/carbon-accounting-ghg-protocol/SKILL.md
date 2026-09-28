---
name: carbon-accounting-ghg-protocol
metadata:
  category: CleanTech Energy and ESG Tech
description: Implement carbon footprint calculation engines and sustainability reporting according to the Greenhouse Gas (GHG) Protocol Corporate Standard. Calculate Scope 1 (direct fuel combustion, mobile emissions), Scope 2 (market-based and location-based electricity grids via eGRID/DEFRA factors), and Scope 3 (value chain, travel, procurement). Trigger when building ESG compliance software, carbon calculators, or corporate sustainability ledgers.
compatibility: GHG Protocol Corporate Standard, ISO 14064-1, DEFRA/EPA Emission Factors
---

# Carbon Accounting & GHG Protocol Skill Guide

This skill governs mathematical modeling, emission factor ingestion, and audit trail generation for enterprise carbon accounting engines compliant with the GHG Protocol.

---

## 1. Greenhouse Gas Scope Architecture

The GHG Protocol categorizes greenhouse gas emissions into three operational scopes:

```text
[ Global Corporate Boundary ]
  |
  |-- SCOPE 1 (Direct Emissions)
  |   |-- Stationary combustion (boilers, natural gas)
  |   +-- Mobile fleet combustion (gasoline/diesel company vehicles)
  |
  |-- SCOPE 2 (Indirect Energy Emissions)
  |   |-- Location-based: Regional grid average factor (eGRID / IEA)
  |   +-- Market-based: Supplier-specific contracts / Renewable Energy Certificates (RECs)
  |
  +-- SCOPE 3 (Value Chain Indirect)
      |-- Category 1: Purchased Goods and Services
      |-- Category 6: Business Travel (flights, hotels)
      +-- Category 7: Employee Commuting & Remote Work
```

---

## 2. Production Code Implementation (Python)

### A. Carbon Footprint Calculation Engine

```python
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel


class EmissionFactor(BaseModel):
    activity_unit: str  # e.g. "kWh", "liter_diesel", "passenger_km"
    co2e_factor_kg: Decimal  # kg CO2e per activity unit
    source: str  # e.g. "EPA 2024", "DEFRA 2023"


class ActivityRecord(BaseModel):
    id: str
    facility_id: str
    scope: Literal["SCOPE_1", "SCOPE_2", "SCOPE_3"]
    activity_type: str
    quantity: Decimal
    unit: str


class CarbonLedgerEngine:
    def __init__(self, factors: dict[str, EmissionFactor]):
        self.factors = factors

    def calculate_emission_kg(self, record: ActivityRecord) -> Decimal:
        factor_key = f"{record.activity_type}_{record.unit}"
        factor = self.factors.get(factor_key)

        if not factor:
            raise ValueError(f"No emission factor found for {factor_key}")

        # Total kg CO2e = Activity Quantity * Emission Factor
        co2e_kg = record.quantity * factor.co2e_factor_kg
        return co2e_kg

    def compute_facility_summary(self, records: list[ActivityRecord]) -> dict:
        summary = {
            "scope_1_mt": Decimal("0.0"),
            "scope_2_mt": Decimal("0.0"),
            "scope_3_mt": Decimal("0.0"),
            "total_co2e_metric_tonnes": Decimal("0.0"),
        }

        for r in records:
            kg = self.calculate_emission_kg(r)
            metric_tonnes = kg / Decimal("1000.0")

            if r.scope == "SCOPE_1":
                summary["scope_1_mt"] += metric_tonnes
            elif r.scope == "SCOPE_2":
                summary["scope_2_mt"] += metric_tonnes
            elif r.scope == "SCOPE_3":
                summary["scope_3_mt"] += metric_tonnes

        summary["total_co2e_metric_tonnes"] = (
            summary["scope_1_mt"] + summary["scope_2_mt"] + summary["scope_3_mt"]
        )
        return summary
```

---

## 3. Best Practices & Audit Principles

1. **Dual Scope 2 Reporting:** The GHG Protocol Scope 2 Guidance requires reporting both Location-Based (local regional grid factor) and Market-Based (incorporating PPA and REC instruments) emissions.
2. **Global Warming Potential (GWP):** Standardize all calculations to 100-year GWP metrics from the IPCC Fifth (AR5) or Sixth (AR6) Assessment Report (e.g. $\text{CH}_4 = 28$, $\text{N}_2\text{O} = 265$).
3. **Immutability of Activity Feeds:** Store raw utility bills and fuel receipts with immutable digital hashes to withstand third-party financial and ESG assurance audits.
