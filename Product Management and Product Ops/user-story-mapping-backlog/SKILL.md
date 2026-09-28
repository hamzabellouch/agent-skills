---
name: user-story-mapping-backlog
metadata:
  category: Product Management and Product Ops
description: Facilitate User Story Mapping, backlog refinement, sprint decomposition, INVEST-compliant story authoring, Gherkin acceptance criteria (Given-When-Then), and WSJF (Weighted Shortest Job First) prioritization. Trigger when breaking down epics, planning sprint iterations, or structuring engineering work streams.
compatibility: Jira, Linear, GitHub Projects, Agile/Scrum/Kanban
---

# User Story Mapping & Backlog Refinement Skill Guide

This skill governs the breakdown of high-level feature initiatives into vertically sliced, testable user stories with rigorous acceptance criteria.

---

## 1. User Story Mapping Visual Framework

```text
[ Backbone / Activities ]     (Discover)       -->      (Configure)     -->     (Checkout)
                                  |                          |                      |
[ Walking Skeleton (Release 1) ]  |-- Browse Catalog         |-- Select Variant     |-- Pay via Card
                                  |                          |                      |
[ Enhancements (Release 2) ]      |-- Filter by Price        |-- Add Custom Text    |-- Apple / Google Pay
                                  |                          |                      |
[ Future Scope (Release 3) ]      |-- AI Recommendations     |-- 3D Preview AR      |-- Split Payment
```

---

## 2. Production User Story Format & Gherkin Criteria

### A. INVEST-Compliant Story Definition

- **Independent:** Can be developed and deployed without hard blockers from other stories.
- **Negotiable:** Focuses on the essence of the problem, allowing implementation flexibility.
- **Valuable:** Delivers demonstrable value to the end user or business.
- **Estimable:** Scoped small enough to be sized with reasonable engineering confidence.
- **Small:** Fits comfortably within a single sprint iteration (1 to 3 days of dev time).
- **Testable:** Has unambiguous acceptance criteria with binary pass/fail verification.

### B. Production Story Example with Gherkin BDD

```markdown
### US-402: Automatic Retry on Transient Payment Gateway Failures

**As a** customer making an online purchase,  
**I want** the payment service to automatically retry temporary network interruptions with Stripe,  
**So that** my transaction does not fail due to momentary carrier or network drops.

---

#### Technical Scope & Acceptance Criteria (Gherkin BDD)

```gherkin
Feature: Payment Gateway Transient Failure Retries

  Background:
    Given the user has entered valid credit card details
    And the order total is $125.00

  Scenario: Successful retry after momentary network timeout
    Given the payment gateway returns a transient HTTP 504 Gateway Timeout on attempt 1
    When the payment service triggers an automated retry with exponential backoff
    And attempt 2 succeeds with HTTP 200 and charge ID "ch_12345"
    Then the user should see the order confirmation screen
    And exactly 1 charge should be recorded in the database
    And the retry attempt should be logged with metric "payment.retry.success"

  Scenario: Idempotency protection against duplicate billing
    Given the payment service initiates an authorization request
    When a retry request is sent to the payment gateway
    Then the same unique "Idempotency-Key" header must be reused across all retry attempts
    And the customer must never be double charged
```

---

## 3. WSJF (Weighted Shortest Job First) Prioritization Formula

Prioritize candidate stories using the standard SAFe WSJF formula:

$$\text{WSJF} = \frac{\text{Cost of Delay (CoD)}}{\text{Job Size / Duration}}$$

Where:
$$\text{Cost of Delay} = \text{User-Business Value} + \text{Time Criticality} + \text{Risk Reduction / Opportunity Enablement}$$

| Story Name | User Value (1-13) | Time Criticality (1-13) | Risk Red. (1-13) | Total CoD | Job Size (1-13) | WSJF Score | Priority |
|---|---|---|---|---|---|---|---|
| Card Retry Idempotency | 8 | 8 | 13 | 29 | 3 | **9.66** | **P1 (Highest)** |
| 3D Product Preview AR | 5 | 2 | 2 | 9 | 8 | **1.12** | P3 |
| Apple Pay Express | 8 | 5 | 3 | 16 | 3 | **5.33** | P2 |
