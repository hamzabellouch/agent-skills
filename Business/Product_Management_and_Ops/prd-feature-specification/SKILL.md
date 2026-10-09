---
name: prd-feature-specification
metadata:
  category: Product Management and Product Ops
description: Author comprehensive, actionable Product Requirements Documents (PRDs) and feature specifications. Define problem statements, target user personas, success metrics (OKRs/KPIs), functional & non-functional requirements, technical edge cases, out-of-scope boundaries, and release criteria. Trigger when drafting PRDs, scoping new features, or aligning cross-functional engineering teams.
compatibility: Agile, Scrum, Shape Up, Dual-Track Agile frameworks
---

# Product Requirements Document (PRD) Specification Skill Guide

This skill standardizes the formulation of rigorous, unambiguous, and engineer-ready Product Requirements Documents (PRDs).

---

## 1. The Anatomy of an Actionable PRD

```text
+------------------------------------------------------------------------+
| 1. Context & Why: Problem statement, customer evidence, business value|
+------------------------------------------------------------------------+
                               |
                               v
+------------------------------------------------------------------------+
| 2. Objectives & Measurable Success: Primary OKRs & North Star KPIs     |
+------------------------------------------------------------------------+
                               |
                               v
+------------------------------------------------------------------------+
| 3. User Personas & Core Journeys: Step-by-step user workflow           |
+------------------------------------------------------------------------+
                               |
                               v
+------------------------------------------------------------------------+
| 4. Functional Scope: Detailed requirements (P0 must-have, P1, P2)      |
+------------------------------------------------------------------------+
                               |
                               v
+------------------------------------------------------------------------+
| 5. Non-Functional, Security & Edge Cases: Latency, scale, failures    |
+------------------------------------------------------------------------+
```

---

## 2. Standard Production PRD Template

```markdown
# [PRD] Automated Merchant Payout Reconciliation

| Metadata | Value |
|---|---|
| **Author** | Principal Product Manager |
| **Status** | In Review / Approved |
| **Target Release** | 2026-Q4 |
| **Engineering Lead**| Staff Backend Engineer |

---

## 1. Problem Statement & Opportunity
Merchants currently spend an average of 4.2 hours per week manually matching bank deposit summaries with daily settled orders. This friction leads to support escalations, billing disputes, and delayed monthly closing. Providing real-time, automated payout reconciliation will eliminate manual bookkeeping and increase 30-day merchant retention by 15%.

---

## 2. Measurable Goals & Success Metrics

- **Primary KPI:** Percentage of monthly transactions reconciled automatically without human manual intervention (> 98.5%).
- **Secondary KPI:** Reduction in payout-related support tickets (target: -60% within 60 days of launch).
- **Guardrail Metric:** Zero false-positive ledger balances or undetected discrepancies > $0.01.

---

## 3. User Personas & Scenarios

- **Persona:** Sarah, Finance Lead at a mid-market e-commerce brand (Processing $500k/mo).
- **Core Workflow:**
  1. Sarah opens the Financial Dashboard every Monday morning.
  2. The system displays a single unified card: "All 1,420 transactions from last week reconciled with Chase deposit #9821."
  3. Sarah downloads an audited CSV export formatted directly for QuickBooks Online.

---

## 4. Functional Requirements & Prioritization

### P0 (Must Have for MVP Launch)
- **FR-101 (Automatic Matching Engine):** Match payouts against banking feed records using deterministic reference IDs and amount equality.
- **FR-102 (Discrepancy Triage UI):** If an amount does not match, flag the specific fee deduction or chargeback item and highlight variance in red.
- **FR-103 (Audit Export):** One-click download of reconciliation records with cryptographic SHA-256 batch hash.

### P1 (Post-MVP Fast Follow)
- **FR-201 (Webhook Alert):** Notify accounting software via Webhook on completed daily reconciliation.

### Out of Scope (Explicit Non-Goals)
- Multi-currency forex hedging calculation (handled in Phase 2).
- Automatic tax filing submission to tax authorities.

---

## 5. Non-Functional Requirements & Security
- **SLA & Latency:** Automated reconciliation batch must complete within 120 seconds of receiving banking webhook.
- **Security & Privacy:** All banking account identifiers must be masked (e.g., `****1234`).
- **Auditability:** Every manual override by a user must log user ID, timestamp, and rationale.

---

## 6. Release Checklist & Rollout Strategy
- [ ] Internal Dogfooding (Alpha: 2 weeks with 10 design partners)
- [ ] Feature Flag Canary Release: 5% -> 25% -> 100% over 10 business days
- [ ] Runbook verified with Support & Operations teams
```

---

## 3. Best Practices & Quality Filters

1. **State the Non-Goals Clearly:** Explicitly define what will NOT be built in this phase to prevent scope creep.
2. **Quantify Ambiguity:** Instead of "system should be fast", specify "p99 API response under 250ms under 500 concurrent RPS".
3. **Traceability:** Every functional requirement must directly link back to an identified user friction or business objective.
