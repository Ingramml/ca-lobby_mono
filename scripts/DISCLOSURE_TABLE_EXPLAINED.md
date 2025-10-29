# The Disclosure Table - Complete Explanation

## What is the Disclosure Table?

The **disclosure table** is the **MASTER record** of all lobbying disclosure filings submitted to the California Secretary of State. Think of it as the "cover sheet" or "header" for each quarterly lobbying report.

## Key Concept: Disclosure = Filing

**A disclosure is a FILING**, not a transaction. It's the official quarterly report that lobbying firms (or employers) submit to the state.

```
One Disclosure Filing
├── Filing Header (disclosure record)
│   ├── filing_id: 2157196
│   ├── filer: Shaw / Yoder / Antwih Inc
│   ├── period: 2016-10-01 to 2016-12-31 (Q4 2016)
│   └── form_type: F625 (Quarterly Report)
│
└── Contains Multiple Schedules:
    ├── Schedule 1: Employers (who hired them)
    ├── Schedule 2: Payments received (v_payments table)
    ├── Schedule 3: Expenditures made (v_expenditures table)
    └── Schedule 4: Other payments (v_other_payments table)
```

## Table Structure

### v_disclosures_alameda.csv

**Records**: 8,649 disclosure filings
**Base Table**: `CVR2_LOBBY_DISCLOSURE_CD` (or `CVR_LOBBY_DISCLOSURE_CD`)

### Columns Explained

| Column | Description | Example |
|--------|-------------|---------|
| `filing_id` | **Unique identifier** for this disclosure filing | 2157196 |
| `amendment_id` | Amendment version (0 = original, 1+ = amended) | 0 |
| `filer_id` | Who filed this disclosure | 1200953 |
| `filer_last_name` | Organization/firm name that filed | "Shaw / Yoder / Antwih Inc" |
| `filer_first_name` | Usually null for organizations | NaN |
| `firm_id` | If filer is a lobbying firm | 1200953 |
| `firm_name` | Lobbying firm name | "Shaw / Yoder / Antwih Inc" |
| `entity_code` | Type of entity filing | "LEM" (Lobbyist Employer) |
| `form_type` | California form type | "F625" (Quarterly), "F635" (Periodic) |
| `period_start_date` | **Start of reporting period** | 2016-10-01 |
| `period_end_date` | **End of reporting period** | 2016-12-31 |
| `report_date` | Date filed with state | 2017-01-30 |
| `is_alameda` | Filtered flag (Alameda-related) | True |

## Entity Codes

| Code | Meaning | Who Files |
|------|---------|-----------|
| **LEM** | Lobbyist Employer | Organizations that hire lobbyists (most common) |
| **LFM** | Lobbying Firm | Professional lobbying firms |
| **LPR** | Lobbyist (person) | Individual lobbyist registration |
| **CLB** | Candidate/Officeholder Lobbyist | Special case |

## Form Types

| Form | Description | Filing Frequency |
|------|-------------|------------------|
| **F625** | Lobbying Firm Quarterly Report | Every 3 months |
| **F635** | Lobbyist Employer Periodic Report | Every 3 months |
| **F615** | Lobbying Firm Registration | Once (initial) |
| **F640** | Amendment to prior filing | As needed |
| **F645** | Termination Report | Once (closing) |

## How Disclosures Relate to Transactions

### The Hierarchy:

```
1. Disclosure (Filing)
   └─ filing_id: 2157196
      ├── Filed by: Shaw / Yoder / Antwih Inc (lobbying firm)
      ├── Period: Q4 2016 (Oct 1 - Dec 31, 2016)
      │
      └── Contains 21 Payment Line Items (v_payments table):
          ├── Line 1: Water District paid $12,482.55
          ├── Line 2: Water District paid $15,247.03
          ├── Line 3: Water District paid $12,482.55
          ├── ... (18 more lines)
          └── Line 21: Water District paid $10,318.33

          Total for this filing: $311,484.60
```

### Visual Example:

**One Disclosure Filing (filing_id: 2157196)**
```
===========================================
FORM F625 - LOBBYING FIRM QUARTERLY REPORT
===========================================
Filed by: Shaw / Yoder / Antwih Inc
Filing ID: 2157196
Period: October 1, 2016 - December 31, 2016
Filed on: January 30, 2017
-------------------------------------------

SCHEDULE 2: PAYMENTS RECEIVED
(These become records in v_payments table)

Line 1:
  Employer: Alameda County Water District
  Fees: $12,482.55
  Reimbursements: $0.00
  Total: $12,482.55

Line 2:
  Employer: Alameda County Water District
  Fees: $15,247.03
  Reimbursements: $0.00
  Total: $15,247.03

... (19 more line items)

Line 21:
  Employer: Alameda County Water District
  Fees: $10,318.33
  Reimbursements: $0.00
  Total: $10,318.33

-------------------------------------------
TOTAL PAYMENTS THIS QUARTER: $311,484.60
===========================================
```

## Critical Understanding: The Alameda Filter Issue

### Why are Alameda organizations NOT in v_disclosures_alameda?

**The View is Filtered by WHO FILED IT, not WHO PAID**

```sql
-- v_disclosures_alameda is created like this:
CREATE VIEW v_disclosures_alameda AS
SELECT *
FROM CVR2_LOBBY_DISCLOSURE_CD
WHERE filer_id IN (
  -- Only filers from Alameda County
  SELECT filer_id FROM FILERS_CD WHERE city = 'Alameda'
);
```

**The Problem:**
- Alameda County Water District is an **EMPLOYER** (client)
- They **hire** Shaw / Yoder / Antwih Inc (lobbying firm in Sacramento)
- Shaw / Yoder / Antwih Inc **files the disclosure** (not Water District)
- Shaw / Yoder is NOT from Alameda
- Therefore, that disclosure is **NOT in v_disclosures_alameda**

### Example:

| Filing | Filer | Filer City | Employer | In v_disclosures_alameda? |
|--------|-------|------------|----------|---------------------------|
| 2157196 | Shaw / Yoder / Antwih Inc | Sacramento | Water District (Alameda) | ❌ NO |
| 2232477 | Waste Management Authority | Alameda | (self - in-house lobbyist) | ✅ YES |

**Solution:** Use the FULL disclosure table (`CVR2_LOBBY_DISCLOSURE_CD`) and join via payments:

```sql
-- Get disclosures FOR Alameda orgs (even if filed by non-Alameda firms)
SELECT DISTINCT d.*
FROM CVR2_LOBBY_DISCLOSURE_CD d
INNER JOIN v_payments_alameda p
  ON d.filing_id = p.filing_id
WHERE UPPER(p.employer_full_name) = 'ALAMEDA COUNTY WATER DISTRICT'
```

## How to Use Disclosures in Queries

### Get Date Ranges for Transactions

Since payments don't have dates directly, you join to disclosures:

```sql
SELECT
  p.employer_full_name as organization,
  p.period_total as amount,
  d.period_start_date,  -- From disclosure
  d.period_end_date,     -- From disclosure
  d.firm_name as paid_to
FROM v_payments_alameda p
INNER JOIN CVR2_LOBBY_DISCLOSURE_CD d
  ON p.filing_id = d.filing_id
WHERE UPPER(p.employer_full_name) = 'ALAMEDA COUNTY WATER DISTRICT'
```

### Count Filings per Organization

```sql
SELECT
  p.employer_full_name,
  COUNT(DISTINCT d.filing_id) as total_filings,
  MIN(d.period_start_date) as first_filing,
  MAX(d.period_end_date) as last_filing
FROM v_payments_alameda p
INNER JOIN CVR2_LOBBY_DISCLOSURE_CD d
  ON p.filing_id = d.filing_id
GROUP BY p.employer_full_name
```

### Get All Activity for a Quarter

```sql
SELECT
  d.filing_id,
  d.filer_last_name as lobbying_firm,
  d.period_start_date,
  d.period_end_date,
  COUNT(p.line_item) as payment_count,
  SUM(p.period_total) as total_amount
FROM CVR2_LOBBY_DISCLOSURE_CD d
LEFT JOIN v_payments_alameda p
  ON d.filing_id = p.filing_id
WHERE d.period_start_date = '2024-01-01'
  AND d.period_end_date = '2024-03-31'
GROUP BY d.filing_id, d.filer_last_name, d.period_start_date, d.period_end_date
```

## Summary: Key Takeaways

### 1. Disclosure = Filing (Not Transaction)
- One disclosure contains multiple payment line items
- Disclosure provides the date range and context
- Payments provide the actual transaction amounts

### 2. The Relationship
```
Disclosure (1) ──has many──> Payments (N)
   ↓                            ↓
filing_id                   filing_id
period_start_date           period_total
period_end_date             employer_full_name
```

### 3. Water District Example
- **520 payment line items** (v_payments table)
- **~161 disclosure filings** (estimated, grouping by filing_id)
- **Average: 8.5 payments per quarterly filing**

### 4. For Dashboard Activity List
You have TWO options:

**Option A: Show Filings (Recommended)**
- Group payment line items by `filing_id`
- Display ~161 quarterly reports
- Each activity = one quarterly disclosure
- Cleaner, more meaningful to users

**Option B: Show Line Items (Current)**
- Display all 520 individual payment line items
- Each activity = one payment to one lobbying firm
- More detailed, but overwhelming

### 5. Critical SQL Pattern
Always join payments → disclosures to get dates:

```sql
FROM v_payments_alameda p
INNER JOIN CVR2_LOBBY_DISCLOSURE_CD d  -- FULL table, not _alameda view
  ON p.filing_id = d.filing_id
WHERE UPPER(p.employer_full_name) = 'YOUR ORGANIZATION'
```

## Tables Reference

| Table/View | Records | Purpose |
|------------|---------|---------|
| **CVR2_LOBBY_DISCLOSURE_CD** | ~500K+ | Full disclosure table (all CA) |
| **v_disclosures_alameda** | 8,649 | Filtered: filed BY Alameda filers |
| **v_payments_alameda** | 9,698 | Payments involving Alameda orgs |

---

**Created**: October 25, 2025
**Purpose**: Explain disclosure table structure and usage
**Key Insight**: Disclosures are FILINGS (headers), not transactions (line items)
