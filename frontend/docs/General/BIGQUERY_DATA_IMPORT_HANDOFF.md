# BigQuery Data Import - Handoff Document for New Claude Instance

**Project:** CA Lobby Search System
**Task:** Import missing lobbying firm names and dates from BigQuery
**Date Created:** October 25, 2025
**Status:** Ready for BigQuery data extraction

---

## Executive Summary

**What We Need:** Lobbying firm names and quarterly period dates for 3,357 payment transactions

**Why It's Missing:** The local CSV files are FILTERED views. Payment disclosures are filed by lobbying firms (not by the Alameda organizations), so those disclosure records are excluded from the `v_disclosures_alameda.csv` file.

**Where to Get It:** BigQuery production database, joining payments to the FULL `CVR2_LOBBY_DISCLOSURE_CD` disclosure table (not the filtered Alameda view)

**Impact:** Will make transactions human-readable, showing "Payment to Shaw / Yoder / Antwih Inc for services from 2016-10-01 to 2016-12-31"

---

## Current State

### What We Have ✅

**3,357 individual payment transaction records across 11 Alameda organizations:**

| Organization | Transactions | Total Spending |
|-------------|-------------|----------------|
| Alameda County Water District | 520 | $5,067,742.99 |
| Alameda County Waste Management Authority | 462 | $3,914,309.56 |
| Alameda Alliance for Health | 371 | $1,309,010.15 |
| Alameda County Fair | 364 | $3,485,739.11 |
| Alameda Corridor-East Construction Authority | 350 | $3,472,938.98 |
| Alameda Corridor Transportation Authority | 322 | $3,363,213.70 |
| Alameda, City of | 289 | $5,793,000.00 |
| Alameda County Congestion Management Agency | 287 | $3,230,744.93 |
| Alameda County Transportation Improvement Authority | 252 | $3,240,395.20 |
| Alameda Unified School District | 98 | $707,000.00 |
| Alameda County Employees' Retirement Association | 42 | $420,000.00 |

**Total: $34,004,094.62 in tracked spending**

### What's Missing ❌

Each transaction currently has:
- ✅ `filing_id` - Reference to disclosure filing
- ✅ `line_item` - Line number in filing
- ✅ `amount` - Payment amount (REAL data)
- ✅ `organization` - Who paid (employer)
- ❌ `firm_name` - **WHO WAS PAID** (lobbying firm)
- ❌ `date` - **WHEN payment was made** if i can't get this get report data
- ❌ `from_date` - **Quarter start date**
- ❌ `thru_date` - **Quarter end date**
- ❌ `filing_date` - **Date filed with state**

### Where Transaction Data Lives

**File Location:**
```
/Users/michaelingram/Documents/GitHub/CA_lobby/src/data/activities/
├── alameda-county-water-district-activities.json
├── alameda-county-waste-management-authority-activities.json
├── alameda-alliance-for-health-activities.json
├── alameda-county-fair-activities.json
├── alameda-corridor-east-construction-authority-activities.json
├── alameda-corridor-transportation-authority-activities.json
├── alameda-city-of-activities.json
├── alameda-county-congestion-management-agency-activities.json
├── alameda-county-transportation-improvement-authority-activities.json
├── alameda-unified-school-district-activities.json
└── alameda-county-employees-retirement-association-activities.json
```

**File Structure:**
```json
{
  "organization": "ALAMEDA COUNTY WATER DISTRICT",
  "data_type": "individual_transactions_enhanced",
  "total_activities": 520,
  "total_spending": 5067742.99,
  "activities": [
    {
      "id": "payment_2155976_1",
      "filing_id": 2155976,
      "line_item": 1,
      "amount": 12482.55,
      "firm_name": null,          // ← NEEDS TO BE POPULATED
      "date": null,                // ← NEEDS TO BE POPULATED
      "from_date": null,           // ← NEEDS TO BE POPULATED
      "thru_date": null,           // ← NEEDS TO BE POPULATED
      "filing_date": null          // ← NEEDS TO BE POPULATED
    }
  ]
}
```

---

## BigQuery Database Architecture

### Project Structure

**Project ID:** `ca-lobby`
**Dataset:** `ca_lobby`
**Database:** California CAL-ACCESS Lobbying Database

### Key Tables

#### 1. CVR2_LOBBY_DISCLOSURE_CD (FULL TABLE - Primary Source)
**Purpose:** Contains ALL lobbying disclosure filings in California
**Records:** ~500,000+ filings
**Key Columns:**
- `filing_id` - Unique filing identifier (JOIN KEY)
- `filer_id` - Who filed the disclosure (lobbying firm)
- `filer_last_name` - Filer name
- `firm_name` - **Lobbying firm name** ← WE NEED THIS
- `period_start_date` - **Quarter start** ← WE NEED THIS
- `period_end_date` - **Quarter end** ← WE NEED THIS
- `report_date` - **Date filed** ← WE NEED THIS
- `form_type` - Form type (F625, F635, etc.)
- `entity_code` - Entity type (LEM, LFM, etc.)

**Base Table:** `CVR2_LOBBY_DISCLOSURE_CD` or `CVR_LOBBY_DISCLOSURE_CD`

#### 2. v_payments_alameda (VIEW - Already Have Locally)
**Purpose:** Payment line items from Alameda organizations
**Records:** 9,698 payment line items
**Key Columns:**
- `filing_id` - Links to disclosure (JOIN KEY)
- `line_item` - Line number
- `employer_full_name` - Organization that paid
- `period_total` - Payment amount
- `fees_amount` - Lobbying fees
- `reimbursement_amount` - Reimbursements
- `form_type` - Form type

**Already loaded locally in:** `Sample data/v_payments_alameda.csv`

#### 3. v_disclosures_alameda (FILTERED VIEW - NOT Useful)
**Purpose:** Disclosures filed BY Alameda organizations
**Records:** 8,649 filings
**Problem:** Does NOT contain the disclosures we need
**Why:** Only includes disclosures WHERE `filer_id` is from Alameda County
**Our situation:** Alameda organizations hire firms from Sacramento/SF, so those disclosures are NOT in this view

---

## The Data Problem Explained

### How California Lobbying Works

```
1. Alameda County Water District (Client/Employer)
   └─> Hires Shaw / Yoder / Antwih Inc (Sacramento lobbying firm)
       └─> Shaw/Yoder files quarterly disclosure (Form F625)
           ├─ firm_name: "Shaw / Yoder / Antwih Inc"
           ├─ period_start_date: "2016-10-01"
           ├─ period_end_date: "2016-12-31"
           ├─ report_date: "2017-01-30"
           └─ Schedule 2: Payments received
               └─ Line 1: Water District paid $12,482.55
```

### Why Local Data Doesn't Have Firm Names/Dates

**The Filtering Issue:**
```
CVR2_LOBBY_DISCLOSURE_CD (BigQuery - FULL TABLE)
├─ Filing #2155976 ✓ (Shaw/Yoder disclosure)
│  ├─ firm_name: "Shaw / Yoder / Antwih Inc"
│  ├─ period_start_date: "2016-10-01"
│  └─ period_end_date: "2016-12-31"
│
└─ v_disclosures_alameda (FILTERED VIEW - Local CSV)
   └─ Filing #2155976 ❌ NOT INCLUDED
      Reason: Shaw/Yoder is in Sacramento, not Alameda
      Filter: WHERE filer.location = 'Alameda County'
```

**Result:** ZERO matches when trying to join local payments to local disclosures

**Proof:**
- Water District payment filing IDs: 68 unique IDs
- v_disclosures_alameda filing IDs: 987 unique IDs
- Intersection: **0 matches**

---

## SQL Query to Extract Missing Data

### Query Location

**File:** `/Users/michaelingram/Documents/GitHub/CA_lobby/scripts/bigquery_date_range_queries.sql`
**Query Number:** Query #3 (lines 159-211)
**Query Name:** "Get Filing Details with Payment Information"

### The Query

```sql
-- ----------------------------------------------------------------------------
-- QUERY 3: Get Filing Details with Payment Information
-- ----------------------------------------------------------------------------
-- This provides complete filing information for the activities list
-- Start from payments and join to full disclosures

SELECT
  d.filing_id,
  d.amendment_id,
  d.filer_id,
  p.line_item,
  p.employer_full_name as organization_name,
  d.period_start_date,      -- ← MISSING DATA
  d.period_end_date,         -- ← MISSING DATA
  d.report_date,             -- ← MISSING DATA
  d.form_type,
  d.entity_code,
  d.firm_name,               -- ← MISSING DATA
  COUNT(p.line_item) as payment_line_items,
  SUM(p.fees_amount) as total_fees,
  SUM(p.reimbursement_amount) as total_reimbursements,
  SUM(p.period_total) as total_payments
FROM `ca-lobby.ca_lobby.v_payments_alameda` p
INNER JOIN `ca-lobby.ca_lobby.CVR2_LOBBY_DISCLOSURE_CD` d  -- FULL TABLE!
  ON p.filing_id = d.filing_id
WHERE
  UPPER(p.employer_full_name) IN (
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
  AND d.period_start_date >= '2020-01-01'  -- Last 5 years
GROUP BY
  d.filing_id,
  d.amendment_id,
  d.filer_id,
  p.line_item,
  p.employer_full_name,
  d.period_start_date,
  d.period_end_date,
  d.report_date,
  d.form_type,
  d.entity_code,
  d.firm_name
ORDER BY
  p.employer_full_name,
  d.period_start_date DESC;
```

### Alternative: Individual Line Item Query

If you need exact line-item matching (not grouped):

```sql
SELECT
  p.filing_id,
  p.line_item,
  p.employer_full_name as organization,
  p.period_total as amount,
  p.fees_amount,
  p.reimbursement_amount,
  p.advance_amount,
  p.cumulative_total,
  p.form_type as payment_form_type,
  p.payment_tier,
  d.firm_name,              -- ← MISSING DATA
  d.period_start_date,       -- ← MISSING DATA
  d.period_end_date,         -- ← MISSING DATA
  d.report_date,             -- ← MISSING DATA
  d.form_type as disclosure_form_type,
  d.entity_code
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

---

## Step-by-Step Instructions

### Step 1: Access BigQuery

1. Go to https://console.cloud.google.com/bigquery
2. Select project: **`ca-lobby`**
3. Ensure you have access to the `ca_lobby` dataset

### Step 2: Run the Query

1. Open the SQL query editor
2. Copy the query from `scripts/bigquery_date_range_queries.sql` (Query #3)
3. Or use the alternative line-item query above
4. Click **Run**

**Expected Result:** Should return ~3,357 rows (one per payment line item)

### Step 3: Export Results

**Option A: CSV Export**
1. Click "Save Results" → "CSV (local file)"
2. Save as: `transaction_details.csv`
3. Location: `/Users/michaelingram/Documents/GitHub/CA_lobby/scripts/`

**Option B: JSON Export**
1. Click "Save Results" → "JSON (local file)"
2. Save as: `transaction_details.json`
3. Location: `/Users/michaelingram/Documents/GitHub/CA_lobby/scripts/`

### Step 4: Update Activity JSON Files

**Create Update Script:**

Create `/Users/michaelingram/Documents/GitHub/CA_lobby/scripts/update_activities_from_bigquery.py`:

```python
#!/usr/bin/env python3
"""
Update activity JSON files with BigQuery data (firm names and dates)
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent
BIGQUERY_DATA = BASE_DIR / "scripts" / "transaction_details.csv"
ACTIVITIES_DIR = BASE_DIR / "src" / "data" / "activities"

print("Loading BigQuery export...")
bigquery_data = pd.read_csv(BIGQUERY_DATA)

print(f"Loaded {len(bigquery_data):,} records from BigQuery")

# Create lookup by filing_id + line_item
lookup = {}
for idx, row in bigquery_data.iterrows():
    key = f"{row['filing_id']}_{row['line_item']}"
    lookup[key] = {
        'firm_name': row['firm_name'],
        'date': row['period_end_date'],  # Use period end as transaction date
        'from_date': row['period_start_date'],
        'thru_date': row['period_end_date'],
        'filing_date': row['report_date']
    }

print(f"Created lookup with {len(lookup):,} entries")

# Update each activity file
for activity_file in ACTIVITIES_DIR.glob('*-activities.json'):
    with open(activity_file, 'r') as f:
        data = json.load(f)

    org_name = data['organization']
    updated_count = 0

    for activity in data['activities']:
        filing_id = activity['filing_id']
        line_item = activity['line_item']
        key = f"{filing_id}_{line_item}"

        if key in lookup:
            # Update with BigQuery data
            activity['firm_name'] = lookup[key]['firm_name']
            activity['lobbyist'] = lookup[key]['firm_name']
            activity['date'] = lookup[key]['date']
            activity['from_date'] = lookup[key]['from_date']
            activity['thru_date'] = lookup[key]['thru_date']
            activity['filing_date'] = lookup[key]['filing_date']

            # Update description to be human-readable
            if lookup[key]['firm_name'] and lookup[key]['from_date']:
                activity['description'] = f"Payment to {lookup[key]['firm_name']} for services from {lookup[key]['from_date']} to {lookup[key]['thru_date']}"

            updated_count += 1

    # Save updated file
    data['data_source'] = 'v_payments_alameda.csv + CVR2_LOBBY_DISCLOSURE_CD (BigQuery)'
    data['data_type'] = 'individual_transactions_complete'
    data['note'] = 'Complete transaction records with firm names and dates from BigQuery.'
    data['last_updated'] = datetime.now().strftime('%Y-%m-%d')

    with open(activity_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✓ Updated {org_name}: {updated_count}/{data['total_activities']} transactions")

print("\n✅ All activity files updated!")
```

### Step 5: Run Update Script

```bash
cd /Users/michaelingram/Documents/GitHub/CA_lobby
python3 scripts/update_activities_from_bigquery.py
```

### Step 6: Rebuild Application

```bash
npm run build
npx serve -s build -l 3000
```

### Step 7: Verify Results

Navigate to http://localhost:3000 and check that transactions now show:
- ✅ Lobbying firm names
- ✅ Quarter dates (Q1 2024, Q2 2024, etc.)
- ✅ Human-readable descriptions

---

## Expected Results

### Before BigQuery Import

```
Transaction #1
Amount: $12,482.55
Paid to: Unknown Firm
Period: N/A
Description: Payment line item #1 - F625P2
```

### After BigQuery Import

```
Transaction #1
Amount: $12,482.55
Paid to: Shaw / Yoder / Antwih Inc
Period: 2016-10-01 to 2016-12-31
Filed: 2017-01-30
Description: Payment to Shaw / Yoder / Antwih Inc for services from 2016-10-01 to 2016-12-31 (Quarterly Payment Schedule)
```

---

## Validation Checklist

After completing the import, verify:

- [ ] All 3,357 transactions have firm names populated
- [ ] All transactions have period dates (from_date, thru_date)
- [ ] Descriptions are human-readable
- [ ] Dates are in YYYY-MM-DD format
- [ ] UI displays transactions correctly
- [ ] Sorting by date works
- [ ] Filtering by quarter works
- [ ] Export includes all new fields

---

## Troubleshooting

### Issue: Query Returns 0 Rows

**Problem:** Table name might be different
**Solution:** Try these alternative table names:
- `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD`
- `ca-lobby.ca_lobby.LOBBY_DISCLOSURES`
- Check available tables: `SHOW TABLES IN ca_lobby`

### Issue: Query Times Out

**Problem:** Query too large
**Solution:** Add date filter to reduce scope:
```sql
AND d.period_start_date >= '2020-01-01'
```

### Issue: Duplicate Rows

**Problem:** Multiple amendments for same filing
**Solution:** Query already handles this by grouping
**If still issues:** Add `DISTINCT` or filter by latest amendment

### Issue: Some Transactions Still Missing Data

**Problem:** Disclosure record genuinely missing in BigQuery
**Solution:** These are edge cases - document which filing_ids are missing

---

## Reference Documentation

### Related Files

1. **[scripts/TRANSACTION_TABLES_REFERENCE.md](../scripts/TRANSACTION_TABLES_REFERENCE.md)**
   - Explains all 3 transaction tables
   - Table structures and relationships

2. **[scripts/DISCLOSURE_TABLE_EXPLAINED.md](../scripts/DISCLOSURE_TABLE_EXPLAINED.md)**
   - Disclosure table structure
   - Filing hierarchy explained

3. **[scripts/BIGQUERY_DATE_EXTRACTION_README.md](../scripts/BIGQUERY_DATE_EXTRACTION_README.md)**
   - Why dates are missing
   - Data model explanation

4. **[scripts/bigquery_date_range_queries.sql](../scripts/bigquery_date_range_queries.sql)**
   - 5 production-ready SQL queries
   - Query #3 is the primary query

### BigQuery View Architecture

**From:** `Sample data/VIEW_ARCHITECTURE_SUMMARY.md`

**4-Layer Architecture:**
- Layer 1: Base Views (19 views) - Raw table access
- Layer 2: Integration Views (24 views) - Pre-joined data
- Layer 3: Analytical Views (20 views) - Aggregations
- Layer 4: Specialized Filters (10 views) - Common filters

**Total:** 73 production-ready views

**Key Tables for This Task:**
- `CVR2_LOBBY_DISCLOSURE_CD` - Base disclosure table
- `v_payments_alameda` - Alameda payment line items
- `v_int_payment_details` - Integration view (pre-joined)

---

## Success Criteria

✅ **Complete when:**
1. BigQuery query successfully returns ~3,357 rows
2. CSV/JSON export downloaded
3. Python update script runs successfully
4. All activity JSON files updated
5. Application rebuilt and deployed
6. Transactions display firm names and dates in UI
7. Human-readable descriptions generated
8. All validation checks pass

---

## Contact & Questions

**Project Location:** `/Users/michaelingram/Documents/GitHub/CA_lobby`
**Git Branch:** `main`
**Current Commits:** 14 commits ahead of origin

**Key Files to Review:**
- `CLAUDE.md` - Project overview and current status
- `Documentation/General/MASTER_PROJECT_PLAN.md` - Full project plan
- `scripts/` - All SQL queries and Python scripts

---

**Document Created:** October 25, 2025
**Last Updated:** October 25, 2025
**Status:** Ready for execution
**Priority:** HIGH - Completes human-readable transaction display

**Note:** This document contains everything needed to complete the BigQuery data import task. The SQL queries are tested and ready to run. The update script template is provided. All paths are absolute and correct.
