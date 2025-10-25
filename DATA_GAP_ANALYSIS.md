# Data Gap Analysis: Frontend Requirements vs BigQuery Views

**Date:** October 25, 2025
**Project:** CA Lobby Database - Alameda Data
**Purpose:** Compare frontend data requirements with supplied BigQuery view exports

---

## Executive Summary

**The Problem:** Frontend needs complete transaction details including lobbying firm names and dates, but our filtered Alameda views are missing critical data because lobbying firms file from outside Alameda County.

**Impact:** 3,357+ payment transactions show as "Unknown Firm" with "N/A" dates in the frontend UI

**Solution:** Query the FULL disclosure table (CVR2_LOBBY_DISCLOSURE_CD) to get firm names and dates, then update activity JSON files

---

## Frontend Data Requirements

### Required Fields (from BIGQUERY_DATA_IMPORT_HANDOFF.md)

Each transaction needs:

| Field | Status | Description | Where It Should Come From |
|-------|--------|-------------|---------------------------|
| filing_id | ✅ HAVE | Reference to disclosure filing | v_payments_alameda.csv |
| line_item | ✅ HAVE | Line number in filing | v_payments_alameda.csv |
| amount | ✅ HAVE | Payment amount | v_payments_alameda.csv (period_total) |
| organization | ✅ HAVE | Who paid (employer) | v_payments_alameda.csv (employer_full_name) |
| **firm_name** | ❌ MISSING | **WHO WAS PAID** (lobbying firm) | CVR2_LOBBY_DISCLOSURE_CD.firm_name |
| **date** | ❌ MISSING | **WHEN payment was made** | CVR2_LOBBY_DISCLOSURE_CD.period_end_date |
| **from_date** | ❌ MISSING | **Quarter start date** | CVR2_LOBBY_DISCLOSURE_CD.period_start_date |
| **thru_date** | ❌ MISSING | **Quarter end date** | CVR2_LOBBY_DISCLOSURE_CD.period_end_date |
| **filing_date** | ❌ MISSING | **Date filed with state** | CVR2_LOBBY_DISCLOSURE_CD.report_date |

### Frontend File Locations

```
/Users/michaelingram/Documents/GitHub/CA_lobby/src/data/activities/
├── alameda-county-water-district-activities.json (520 transactions)
├── alameda-county-waste-management-authority-activities.json (462 transactions)
├── alameda-alliance-for-health-activities.json (371 transactions)
├── alameda-county-fair-activities.json (364 transactions)
├── alameda-corridor-east-construction-authority-activities.json (350 transactions)
├── alameda-corridor-transportation-authority-activities.json (322 transactions)
├── alameda-city-of-activities.json (289 transactions)
├── alameda-county-congestion-management-agency-activities.json (287 transactions)
├── alameda-county-transportation-improvement-authority-activities.json (252 transactions)
├── alameda-unified-school-district-activities.json (98 transactions)
└── alameda-county-employees-retirement-association-activities.json (42 transactions)

TOTAL: 3,357 transactions needing firm names and dates
```

---

## What We Have: BigQuery View Exports

### v_payments_alameda.csv (Current Export)

**Location:** `/Users/michaelingram/Documents/GitHub/CA_lobby_Database/alameda_data_exports/v_payments_alameda.csv`

**Row Count:** 9,698 rows

**Columns Available:**
```
filing_id              ✅ HAVE - Links to disclosure
amendment_id           ✅ HAVE - Amendment number
line_item              ✅ HAVE - Line number
employer_last_name     ✅ HAVE - Organization name (last)
employer_first_name    ✅ HAVE - Organization name (first)
employer_full_name     ✅ HAVE - Full organization name
fees_amount            ✅ HAVE - Lobbying fees paid
reimbursement_amount   ✅ HAVE - Reimbursements
advance_amount         ✅ HAVE - Advances
period_total           ✅ HAVE - Total payment amount
cumulative_total       ✅ HAVE - Year-to-date total
form_type              ✅ HAVE - Form type (F625P2, etc.)
payment_tier           ✅ HAVE - Payment size category
is_alameda             ✅ HAVE - Alameda flag
```

**Missing from v_payments:**
- ❌ firm_name (who was paid)
- ❌ period_start_date (quarter start)
- ❌ period_end_date (quarter end)
- ❌ report_date (filing date)

### v_disclosures_alameda.csv (Filtered View - NOT Useful)

**Location:** `/Users/michaelingram/Documents/GitHub/CA_lobby_Database/alameda_data_exports/v_disclosures_alameda.csv`

**Row Count:** 8,649 rows

**Why It's NOT Useful:**
- This view is filtered to disclosures WHERE filer is from Alameda County
- Our payments are TO lobbying firms in Sacramento/SF/other locations
- **Result:** ZERO matches when joining v_payments to v_disclosures_alameda

**Test Results:**
```
Water District payment filing IDs: 68 unique IDs
v_disclosures_alameda filing IDs: 987 unique IDs
Intersection: 0 matches ❌
```

**Columns in v_disclosures_alameda:**
```
filing_id, period_start_date, period_end_date, report_date, form_type,
amendment_id, filer_id, filer_name, entity_code, session_id, is_alameda
```

**The Problem Explained:**
```
Alameda County Water District (Alameda)
  └─> Pays Shaw / Yoder / Antwih Inc (Sacramento)
      └─> Shaw/Yoder files disclosure (filing #2155976)
          ├─ filer_location: Sacramento (NOT Alameda)
          └─ Result: NOT in v_disclosures_alameda ❌
```

---

## What We Need: Full Disclosure Table

### CVR2_LOBBY_DISCLOSURE_CD (BigQuery Base Table)

**Location:** `ca-lobby.ca_lobby.CVR2_LOBBY_DISCLOSURE_CD`

**Type:** Full unfiltered base table

**Row Count:** ~500,000+ disclosure filings (ALL California lobbying)

**Key Columns We Need:**
```sql
filing_id               -- JOIN KEY to v_payments
filer_id                -- Who filed (lobbying firm ID)
firm_name               -- ✅ MISSING DATA - Lobbying firm name
period_start_date       -- ✅ MISSING DATA - Quarter start (DATE)
period_end_date         -- ✅ MISSING DATA - Quarter end (DATE)
report_date             -- ✅ MISSING DATA - Date filed (DATE)
form_type               -- Form type
entity_code             -- Entity code
```

**Why This Works:**
- Contains ALL disclosure filings, regardless of location
- Includes Sacramento, SF, LA lobbying firms
- Has the firm names and dates we need
- Can join on filing_id from v_payments

---

## The Solution: Join Query

### SQL Query to Extract Missing Data

```sql
-- Extract complete payment transaction details
-- Joins v_payments_alameda to FULL disclosure table

SELECT
  p.filing_id,
  p.amendment_id,
  p.line_item,
  p.employer_full_name as organization,
  p.period_total as amount,
  p.fees_amount,
  p.reimbursement_amount,
  p.advance_amount,
  p.cumulative_total,
  p.form_type as payment_form_type,
  p.payment_tier,

  -- MISSING DATA FROM FULL DISCLOSURE TABLE:
  d.firm_name,              -- ✅ WHO WAS PAID
  d.period_start_date,      -- ✅ QUARTER START
  d.period_end_date,        -- ✅ QUARTER END
  d.report_date,            -- ✅ FILING DATE
  d.filer_id,
  d.entity_code,
  d.form_type as disclosure_form_type

FROM `ca-lobby.ca_lobby.v_payments_alameda` p
INNER JOIN `ca-lobby.ca_lobby.CVR2_LOBBY_DISCLOSURE_CD` d
  ON p.filing_id = d.filing_id

WHERE UPPER(p.employer_full_name) IN (
  'ALAMEDA COUNTY WATER DISTRICT',
  'ALAMEDA COUNTY WASTE MANAGEMENT AUTHORITY',
  'ALAMEDA ALLIANCE FOR HEALTH',
  'ALAMEDA COUNTY FAIR',
  'ALAMEDA CORRIDOR-EAST CONSTRUCTION AUTHORITY',
  'ALAMEDA CORRIDOR TRANSPORTATION AUTHORITY',
  'ALAMEDA, CITY OF',
  'ALAMEDA COUNTY CONGESTION MANAGEMENT AGENCY',
  'ALAMEDA COUNTY TRANSPORTATION IMPROVEMENT AUTHORITY',
  'ALAMEDA UNIFIED SCHOOL DISTRICT',
  'ALAMEDA COUNTY EMPLOYEES\' RETIREMENT ASSOCIATION'
)

ORDER BY p.employer_full_name, d.period_start_date DESC, p.line_item;
```

**Expected Result:** ~3,357+ rows with complete data

---

## Data Transformation Needed

### Current Activity JSON Structure (INCOMPLETE)

```json
{
  "id": "payment_2155976_1",
  "filing_id": 2155976,
  "line_item": 1,
  "amount": 12482.55,
  "firm_name": null,        ← NEEDS POPULATION
  "date": null,              ← NEEDS POPULATION
  "from_date": null,         ← NEEDS POPULATION
  "thru_date": null,         ← NEEDS POPULATION
  "filing_date": null        ← NEEDS POPULATION
}
```

### Target Activity JSON Structure (COMPLETE)

```json
{
  "id": "payment_2155976_1",
  "filing_id": 2155976,
  "line_item": 1,
  "amount": 12482.55,
  "firm_name": "Shaw / Yoder / Antwih Inc",
  "lobbyist": "Shaw / Yoder / Antwih Inc",
  "date": "2016-12-31",
  "from_date": "2016-10-01",
  "thru_date": "2016-12-31",
  "filing_date": "2017-01-30",
  "description": "Payment to Shaw / Yoder / Antwih Inc for services from 2016-10-01 to 2016-12-31"
}
```

---

## Comparison Table: Required vs Available

| Data Element | Frontend Needs | v_payments_alameda | v_disclosures_alameda | CVR2_LOBBY_DISCLOSURE_CD | Status |
|-------------|----------------|-------------------|----------------------|-------------------------|---------|
| filing_id | ✅ Required | ✅ Available | ✅ Available | ✅ Available | HAVE |
| line_item | ✅ Required | ✅ Available | ❌ N/A | ❌ N/A | HAVE |
| amount | ✅ Required | ✅ Available (period_total) | ❌ N/A | ❌ N/A | HAVE |
| organization | ✅ Required | ✅ Available (employer_full_name) | ❌ N/A | ❌ N/A | HAVE |
| **firm_name** | ✅ **Required** | ❌ **Missing** | ✅ Available | ✅ **Available** | **NEED QUERY** |
| **period_start_date** | ✅ **Required** | ❌ **Missing** | ✅ Available | ✅ **Available** | **NEED QUERY** |
| **period_end_date** | ✅ **Required** | ❌ **Missing** | ✅ Available | ✅ **Available** | **NEED QUERY** |
| **report_date** | ✅ **Required** | ❌ **Missing** | ✅ Available | ✅ **Available** | **NEED QUERY** |

**Summary:**
- ✅ **4/8 fields available** in v_payments_alameda
- ❌ **4/8 fields missing** - need to join to CVR2_LOBBY_DISCLOSURE_CD
- ⚠️ v_disclosures_alameda has the fields but **ZERO matching records**

---

## Why Existing Views Don't Work

### Problem 1: v_payments_alameda doesn't have firm names/dates

**Why:** The LPAY_CD base table (source for v_payments) only contains:
- Employer information (who paid)
- Payment amounts
- NOT firm information (that's in the disclosure header)

**Solution:** Must join to disclosure table

### Problem 2: v_disclosures_alameda is filtered

**Filter Applied:**
```sql
WHERE filer_city LIKE '%ALAMEDA%'
   OR filer_city LIKE '%OAKLAND%'
```

**Result:** Only includes firms/filers located in Alameda County

**Impact:** Excludes 100% of our payment disclosures because:
- Shaw / Yoder / Antwih Inc → Sacramento
- Platinum Advisors → San Francisco
- Nielsen Merksamer → Sacramento
- Capitol Advocacy → Sacramento
- KP Public Affairs → Sacramento

**None of these firms are in Alameda County!**

### Problem 3: Need FULL disclosure table

**Must Use:** `CVR2_LOBBY_DISCLOSURE_CD` (unfiltered base table)

**Why:** Contains ALL disclosure filings regardless of filer location

**Join Logic:**
```
v_payments_alameda (9,698 rows)
  └─> filing_id = CVR2_LOBBY_DISCLOSURE_CD.filing_id
      └─> Get: firm_name, period_start_date, period_end_date, report_date
```

---

## Action Items

### 1. Run BigQuery Query ⏳

**Query File:** `/Users/michaelingram/Documents/GitHub/CA_lobby/scripts/bigquery_date_range_queries.sql`

**Query #3:** "Get Filing Details with Payment Information"

**Expected Output:** ~3,357+ rows

### 2. Export Results ⏳

**Format:** CSV

**Filename:** `transaction_details_complete.csv`

**Location:** `/Users/michaelingram/Documents/GitHub/CA_lobby_Database/alameda_data_exports/`

### 3. Create Update Script ⏳

**Script:** `update_activity_json_with_firm_data.py`

**Purpose:** Read BigQuery export and update all activity JSON files

### 4. Update Activity Files ⏳

**Target:** 11 activity JSON files (3,357 transactions)

**Updates Per Transaction:**
- firm_name
- date (use period_end_date)
- from_date (period_start_date)
- thru_date (period_end_date)
- filing_date (report_date)
- description (generate human-readable)

### 5. Verify Results ✅

**Checks:**
- [ ] All 3,357 transactions have firm_name populated
- [ ] All transactions have dates (from_date, thru_date, filing_date)
- [ ] Descriptions are human-readable
- [ ] No NULL values in critical fields

---

## Expected Results

### Before Update (Current State)

```
Alameda County Water District
  Transaction #1
    Amount: $12,482.55
    Paid to: Unknown Firm
    Period: N/A
    Filed: N/A
```

### After Update (Target State)

```
Alameda County Water District
  Transaction #1
    Amount: $12,482.55
    Paid to: Shaw / Yoder / Antwih Inc
    Period: 2016-10-01 to 2016-12-31 (Q4 2016)
    Filed: 2017-01-30
    Description: Payment to Shaw / Yoder / Antwih Inc for lobbying services
```

---

## Summary

**Data We Have:** ✅
- 9,698 payment line items with amounts and organizations
- Complete Alameda organization information
- Payment tiers and form types

**Data We're Missing:** ❌
- Lobbying firm names (who received the payments)
- Quarter dates (when payments were made)
- Filing dates (when reported to state)
- Human-readable transaction descriptions

**Why It's Missing:**
- v_payments table doesn't include disclosure header information
- v_disclosures_alameda is filtered to Alameda-based filers only
- Our payments are TO firms outside Alameda County

**Solution:**
- Query FULL CVR2_LOBBY_DISCLOSURE_CD table
- Join on filing_id to get firm names and dates
- Update 3,357 activity JSON files with complete data

**Impact When Complete:**
- Frontend can display "Who paid who" for all transactions
- Transactions can be sorted/filtered by date and quarter
- Human-readable descriptions generated automatically
- Complete lobbying activity timeline visible

---

**Document Created:** October 25, 2025
**Status:** Analysis Complete - Ready for BigQuery Query Execution
**Priority:** HIGH - Required for frontend completion
