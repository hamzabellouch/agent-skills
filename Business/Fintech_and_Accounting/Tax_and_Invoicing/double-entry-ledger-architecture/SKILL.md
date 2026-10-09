---
name: double-entry-ledger-architecture
metadata:
  category: Accounting Tax and Invoicing Tech
description: Architect tamper-evident, multi-currency double-entry accounting ledgers. Enforce mathematical debits equal credits balance invariants, manage charts of accounts (Assets, Liabilities, Equity, Revenue, Expense), design immutable journal entries, and ensure strict financial audit trails. Trigger when building financial transaction engines, billing systems, or core banking ledgers.
compatibility: PostgreSQL 14+, ACID-compliant relational databases, Financial GAAP / IFRS
---

# Double-Entry Ledger Architecture Skill Guide

This skill governs the design, data structures, and mathematical invariants required to build production-grade double-entry financial ledgers.

---

## 1. Double-Entry Mathematical Invariants

In double-entry bookkeeping, every financial transaction consists of at least two balanced entries.

$$\sum \text{Debits} = \sum \text{Credits}$$

The fundamental accounting equation must hold true at every millisecond:

$$\text{Assets} = \text{Liabilities} + \text{Equity} + (\text{Revenue} - \text{Expenses})$$

```text
[ Account Classifications & Normal Balances ]
+------------------+------------------+------------------+
| Account Type     | Debit (Dr)       | Credit (Cr)      |
+------------------+------------------+------------------+
| Assets           | Increases (+)    | Decreases (-)    |
| Liabilities      | Decreases (-)    | Increases (+)    |
| Equity           | Decreases (-)    | Increases (+)    |
| Revenue          | Decreases (-)    | Increases (+)    |
| Expense          | Increases (+)    | Decreases (-)    |
+------------------+------------------+------------------+
```

---

## 2. Production Database Schema (PostgreSQL)

```sql
-- 1. Chart of Accounts
CREATE TYPE account_classification AS ENUM ('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE');

CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_code VARCHAR(32) NOT NULL UNIQUE, -- e.g. '1010-CASH-USD'
    name VARCHAR(128) NOT NULL,
    classification account_classification NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT clock_timestamp()
);

-- 2. Journal Transactions (Header)
CREATE TABLE journal_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reference_id VARCHAR(128) NOT NULL UNIQUE, -- Idempotency key from payment/checkout
    description TEXT NOT NULL,
    posted_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

-- 3. Journal Entries (Lines: Debits & Credits)
CREATE TABLE journal_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id UUID NOT NULL REFERENCES journal_transactions(id) ON DELETE RESTRICT,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
    amount NUMERIC(18, 4) NOT NULL CHECK (amount > 0),
    is_debit BOOLEAN NOT NULL,
    entry_sequence INT NOT NULL,
    CONSTRAINT uq_txn_entry_seq UNIQUE (transaction_id, entry_sequence)
);

CREATE INDEX idx_journal_entries_account ON journal_entries(account_id);
CREATE INDEX idx_journal_entries_txn ON journal_entries(transaction_id);
```

### B. Transaction Posting Function with Balance Assertion

```sql
CREATE OR REPLACE FUNCTION post_balanced_transaction(
    p_ref_id VARCHAR,
    p_description TEXT,
    p_entries JSONB -- Array of {account_id, amount, is_debit}
) RETURNS UUID AS $$
DECLARE
    v_txn_id UUID;
    v_sum_debits NUMERIC(18, 4) := 0;
    v_sum_credits NUMERIC(18, 4) := 0;
    item JSONB;
    v_seq INT := 1;
BEGIN
    -- Verify balance in memory before insert
    FOR item IN SELECT * FROM jsonb_array_elements(p_entries)
    LOOP
        IF (item->>'is_debit')::BOOLEAN THEN
            v_sum_debits := v_sum_debits + (item->>'amount')::NUMERIC;
        ELSE
            v_sum_credits := v_sum_credits + (item->>'amount')::NUMERIC;
        END IF;
    END LOOP;

    IF v_sum_debits <> v_sum_credits THEN
        RAISE EXCEPTION 'Unbalanced transaction: Debits (%) != Credits (%)', v_sum_debits, v_sum_credits;
    END IF;

    -- Create Header
    INSERT INTO journal_transactions (reference_id, description)
    VALUES (p_ref_id, p_description)
    RETURNING id INTO v_txn_id;

    -- Insert Entries
    FOR item IN SELECT * FROM jsonb_array_elements(p_entries)
    LOOP
        INSERT INTO journal_entries (transaction_id, account_id, amount, is_debit, entry_sequence)
        VALUES (
            v_txn_id,
            (item->>'account_id')::UUID,
            (item->>'amount')::NUMERIC,
            (item->>'is_debit')::BOOLEAN,
            v_seq
        );
        v_seq := v_seq + 1;
    END LOOP;

    RETURN v_txn_id;
END;
$$ LANGUAGE plpgsql;
```

---

## 3. Financial Integrity Checklist

- [ ] **No In-Place Updates:** Never issue `UPDATE` or `DELETE` on posted `journal_entries`. Corrections must be made via **Reversal Transactions** (Contra entries).
- [ ] **Exact Decimal Precision:** Always use `NUMERIC(18, 4)` or equivalent arbitrary-precision fixed-point types. Floating-point types (`FLOAT`, `DOUBLE`) are strictly forbidden in financial calculation.
- [ ] **Idempotency Keys:** Every incoming financial event must provide a deterministic unique `reference_id` to prevent duplicate transaction posting.
