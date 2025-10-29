# CA Lobby Transaction Tables Reference

## Overview
There are **3 main tables** that contain transaction data in the CA Lobby database:

## 1. v_payments_alameda.csv ⭐ PRIMARY TRANSACTION TABLE

**Description**: Payments from employers (like Alameda County Water District) TO lobbying firms

**Record Count**: **9,698 transactions**

**Key Columns**:
- `filing_id` - Links to disclosure filing
- `amendment_id` - Amendment version (0 = original)
- `line_item` - Line number in filing
- `employer_full_name` - **WHO IS PAYING** (e.g., "ALAMEDA COUNTY WATER DISTRICT")
- `fees_amount` - Lobbying fees paid
- `reimbursement_amount` - Reimbursements
- `advance_amount` - Advance payments
- `period_total` - **TOTAL AMOUNT** for this line item
- `cumulative_total` - Running total for the filing
- `form_type` - Form type (F625P2 = quarterly payment schedule)
- `payment_tier` - Payment size category (Low/Medium/High)

**Sample Record**:
```
filing_id: 1117003
employer_full_name: ALAMEDA ALLIANCE FOR HEALTH
fees_amount: 4,805.00
reimbursement_amount: 85.25
period_total: 4,890.25
form_type: F625P2
```

**BigQuery Tables**:
- CSV View: `v_payments_alameda`
- Production View: `ca-lobby.ca_lobby.v_payments_alameda`
- Base Table: `ca-lobby.ca_lobby.LPAY_CD`

**Use Case**:
- This is the **MAIN table** for analyzing lobbying spending
- Shows WHO paid WHOM and HOW MUCH
- Each row = 1 payment line item (multiple items per filing)

---

## 2. v_other_payments_alameda.csv

**Description**: Other lobbying-related payments (different reporting type)

**Record Count**: **198,986 transactions** (20x more than v_payments!)

**Key Columns**:
- `filing_id` - Links to disclosure filing
- `amendment_id` - Amendment version
- `line_item` - Line number
- `record_type` - Always "LOTH" (Lobbying Other Payments)
- `transaction_id` - Unique transaction identifier
- `firm_name` - Lobbying firm making the payment
- `subject_full_name` - **WHO RECEIVED THE PAYMENT** (e.g., "HERTZ CORPORATION")
- `amount` - Payment amount
- `payment_date` - Date of payment
- `form_type` - Form type (F625P3B = other payments schedule)

**Sample Record**:
```
filing_id: 1538317
firm_name: RFK CONSULTING
subject_full_name: HERTZ CORPORATION
amount: 8,250.00
payment_date: 2010-07-01
form_type: F625P3B
```

**BigQuery Tables**:
- CSV View: `v_other_payments_alameda`
- Production View: `ca-lobby.ca_lobby.v_other_payments_alameda`
- Base Table: `ca-lobby.ca_lobby.LOTH_CD`

**Use Case**:
- Payments made BY lobbying firms TO third parties
- Expenses like travel, entertainment, research
- Much larger volume than direct employer-to-firm payments

---

## 3. v_expenditures_alameda.csv

**Description**: Lobbying expenditures and expenses

**Record Count**: **231 transactions** (smallest table)

**Key Columns**:
- `filing_id` - Links to disclosure filing
- `amendment_id` - Amendment version
- `line_item` - Line number
- `payee_full_name` - **WHO WAS PAID** (e.g., "Alameda Produce Market")
- `amount` - Expenditure amount
- `expense_description` - **WHAT IT WAS FOR** (e.g., "snack", "meals")
- `transaction_id` - Unique transaction identifier
- `form_type` - Form type (F635P3C = expenditure schedule)

**Sample Record**:
```
filing_id: 984937
payee_full_name: Alameda Produce Market
amount: 7.62
expense_description: snack
form_type: F635P3C
```

**BigQuery Tables**:
- CSV View: `v_expenditures_alameda`
- Production View: `ca-lobby.ca_lobby.v_expenditures_alameda`
- Base Table: `ca-lobby.ca_lobby.LEXP_CD`

**Use Case**:
- Detailed expense items
- Smaller purchases and operational costs
- Provides transparency on spending details

---

## Transaction Table Comparison

| Table | Records | Primary Purpose | Key Amount Field | Typical Use |
|-------|---------|----------------|-----------------|-------------|
| **v_payments_alameda** | 9,698 | Employer → Firm payments | `period_total` | Main lobbying spending |
| **v_other_payments_alameda** | 198,986 | Firm → Third-party payments | `amount` | Lobbying expenses |
| **v_expenditures_alameda** | 231 | Miscellaneous expenses | `amount` | Detailed expense items |

---

## How to Get All Transactions for an Organization

### Option 1: Payments Only (Main Spending)
```sql
SELECT
  p.filing_id,
  p.employer_full_name as organization,
  p.period_total as amount,
  d.period_start_date as from_date,
  d.period_end_date as thru_date,
  d.firm_name as paid_to
FROM `ca-lobby.ca_lobby.v_payments_alameda` p
INNER JOIN `ca-lobby.ca_lobby.CVR2_LOBBY_DISCLOSURE_CD` d
  ON p.filing_id = d.filing_id
WHERE UPPER(p.employer_full_name) = 'ALAMEDA COUNTY WATER DISTRICT'
ORDER BY d.period_start_date DESC;
```

### Option 2: All Three Transaction Types (Complete Picture)
```sql
-- Payments (employer to firm)
SELECT
  'PAYMENT' as transaction_type,
  p.filing_id,
  p.employer_full_name as from_entity,
  d.firm_name as to_entity,
  p.period_total as amount,
  d.period_start_date as transaction_date,
  'Lobbying fees' as description
FROM `ca-lobby.ca_lobby.v_payments_alameda` p
INNER JOIN `ca-lobby.ca_lobby.CVR2_LOBBY_DISCLOSURE_CD` d
  ON p.filing_id = d.filing_id
WHERE UPPER(p.employer_full_name) = 'ALAMEDA COUNTY WATER DISTRICT'

UNION ALL

-- Other payments (firm to third parties)
SELECT
  'OTHER_PAYMENT' as transaction_type,
  op.filing_id,
  op.firm_name as from_entity,
  op.subject_full_name as to_entity,
  op.amount,
  op.payment_date as transaction_date,
  'Other lobbying expense' as description
FROM `ca-lobby.ca_lobby.v_other_payments_alameda` op
INNER JOIN `ca-lobby.ca_lobby.CVR2_LOBBY_DISCLOSURE_CD` d
  ON op.filing_id = d.filing_id
INNER JOIN `ca-lobby.ca_lobby.v_payments_alameda` p
  ON d.filing_id = p.filing_id
WHERE UPPER(p.employer_full_name) = 'ALAMEDA COUNTY WATER DISTRICT'

UNION ALL

-- Expenditures
SELECT
  'EXPENDITURE' as transaction_type,
  e.filing_id,
  d.filer_last_name as from_entity,
  e.payee_full_name as to_entity,
  e.amount,
  d.period_start_date as transaction_date,
  e.expense_description as description
FROM `ca-lobby.ca_lobby.v_expenditures_alameda` e
INNER JOIN `ca-lobby.ca_lobby.CVR2_LOBBY_DISCLOSURE_CD` d
  ON e.filing_id = d.filing_id
INNER JOIN `ca-lobby.ca_lobby.v_payments_alameda` p
  ON d.filing_id = p.filing_id
WHERE UPPER(p.employer_full_name) = 'ALAMEDA COUNTY WATER DISTRICT'

ORDER BY transaction_date DESC;
```

---

## Recommended Approach for Dashboard

For the **CA Lobby dashboard**, use **v_payments_alameda** as the primary transaction table because:

1. ✅ **Most Relevant**: Shows direct employer spending on lobbying
2. ✅ **Clean Data**: 9,698 records vs 198,986 in other_payments
3. ✅ **Clear Attribution**: Easy to identify WHO paid WHOM
4. ✅ **Already Implemented**: Current dashboard uses this table

**Current Implementation**:
```javascript
// src/data/organizations-summary.json
// Generated from v_payments_alameda.csv
{
  "organizations": [
    {
      "name": "ALAMEDA COUNTY WATER DISTRICT",
      "activityCount": 520,  // Line items from v_payments_alameda
      "totalSpending": 5067742.99  // Sum of period_total
    }
  ]
}
```

---

## Base Table Reference

All views are built on top of these CAL-ACCESS base tables:

| View | Base Table | Description |
|------|------------|-------------|
| v_payments_alameda | LPAY_CD | Lobbying payment schedule |
| v_other_payments_alameda | LOTH_CD | Lobbying other payments |
| v_expenditures_alameda | LEXP_CD | Lobbying expenditures |

**Note**: The "_alameda" suffix indicates these are FILTERED views showing only Alameda-related records.

---

## Summary

**For a complete list of transactions for Alameda organizations:**

1. **Primary Data**: Use `v_payments_alameda` (9,698 records)
   - This shows employer → lobbying firm payments
   - Already used in current dashboard

2. **Additional Context**: Add `v_other_payments_alameda` (198,986 records)
   - Shows lobbying firm → third-party payments
   - Provides complete money trail

3. **Detailed Expenses**: Include `v_expenditures_alameda` (231 records)
   - Miscellaneous expense items
   - Adds transparency to spending

**Total Available Transactions**: **208,915 records**

---

**Created**: October 25, 2025
**Purpose**: Reference for SQL queries and data analysis
**Status**: Current data structure
