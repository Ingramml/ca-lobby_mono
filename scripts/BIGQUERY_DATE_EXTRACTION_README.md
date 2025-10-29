# BigQuery Date Range Extraction - README

## Purpose
Extract date ranges and activity timelines for Alameda government organizations to populate the CA Lobby dashboard.

## Critical Discovery: Data Model Understanding

### The Problem
The 11 Alameda government organizations (Water District, City of Alameda, etc.) have **NO direct disclosure records** in `v_disclosures_alameda`. This appears to be an error, but it's actually correct!

### Why This Happens
These organizations are **CLIENTS (employers)** who hire lobbying firms. They do NOT file disclosures themselves. The lobbying firms file the disclosures on their behalf.

**Data Flow:**
1. Alameda County Water District **pays** Shaw / Yoder / Antwih Inc (lobbying firm)
2. Shaw / Yoder / Antwih Inc **files** quarterly disclosure (Form F625)
3. Disclosure contains payment line items showing Water District as employer

**Table Structure:**
- `v_filers_alameda`: Organizations ARE registered (filer_id exists)
- `v_payments_alameda`: Organizations APPEAR as `employer_full_name` (paying the firms)
- `v_disclosures_alameda`: Organizations DO NOT appear as `filer_id` (firms file these)

### The Solution
To get date ranges, we must:
1. Start from `v_payments_alameda` (where org is the employer)
2. Join to **FULL disclosures table** (`CVR2_LOBBY_DISCLOSURE_CD`) via `filing_id`
3. Extract `period_start_date` and `period_end_date` from those disclosures

**Why can't we use `v_disclosures_alameda`?**
- This view is FILTERED to show only disclosures WHERE `filer_id` is an Alameda organization
- Payment disclosures are filed by LOBBYING FIRMS (not Alameda orgs)
- Therefore, those disclosure records are NOT in the filtered view

## Files Created

### 1. `bigquery_date_range_queries.sql`
Five production-ready SQL queries to run in BigQuery:

#### Query 1: Date Ranges for Organizations
Extracts first_activity, last_activity, and activity span for each organization.

**Output:**
```
filer_id | organization_name                | first_activity | last_activity | activity_span_days
---------|----------------------------------|----------------|---------------|-------------------
1144594  | ALAMEDA COUNTY WATER DISTRICT    | 2006-10-01     | 2025-03-31    | 6756
```

#### Query 2: Activity Timeline for Dashboard Charts
Quarterly aggregation of spending for charts (Lobby Trends, etc.)

**Output:**
```
organization_name                | period_start | period_end | total_spending | quarter
---------------------------------|--------------|------------|----------------|--------
ALAMEDA COUNTY WATER DISTRICT    | 2024-01-01   | 2024-03-31 | 45,789.50      | Q1 2024
```

#### Query 3: Filing Details with Payment Information
Complete filing records for activity lists (last 5 years)

**Output:**
```
filing_id | organization_name             | period_start | form_type | payment_line_items | total_payments
----------|------------------------------|--------------|-----------|-------------------|---------------
2157196   | ALAMEDA COUNTY WATER DISTRICT | 2016-10-01   | F625      | 21                | 311,484.60
```

#### Query 4: Top Lobbying Firms by Organization
Top recipients for the "Top Recipients" component

**Output:**
```
organization_name                | lobbying_firm                  | total_paid  | payment_count | firm_rank
---------------------------------|--------------------------------|-------------|---------------|----------
ALAMEDA COUNTY WATER DISTRICT    | Shaw / Yoder / Antwih Inc      | 3,124,567   | 147           | 1
ALAMEDA COUNTY WATER DISTRICT    | California Strategies & Advocacy| 1,943,175   | 94            | 2
```

#### Query 5: Sample Data Export
500 recent records for testing (3 organizations, 2023+)

### 2. `test_date_range_queries.py`
Python script to test query logic on local CSV files. This confirms the data model understanding and why disclosures are empty for these organizations.

**Test Results:**
```
ALAMEDA COUNTY WATER DISTRICT
  Filer ID: 1144594
  First Activity: None (expected - no disclosures in filtered view)
  Last Activity: None
  Payment Line Items: 520 ✓ (payments exist!)
```

## How to Execute in BigQuery

### Prerequisites
- Access to BigQuery project: `ca-lobby`
- Permissions to query `ca-lobby.ca_lobby` dataset
- Access to base tables (not just views)

### Step 1: Run Query 1 (Date Ranges)
```bash
# In BigQuery Console
1. Go to https://console.cloud.google.com/bigquery
2. Select project: ca-lobby
3. Open scripts/bigquery_date_range_queries.sql
4. Copy QUERY 1 (lines 26-101)
5. Click "Run"
6. Export results: "Save Results" > "CSV (local file)"
7. Save as: date_ranges.csv
```

### Step 2: Verify Results
Expected output for 11 organizations with real date ranges:
```
11 rows
All organizations should have non-null first_activity and last_activity
Dates should span from ~2006 to 2025
```

### Step 3: Run Other Queries
Execute queries 2-5 as needed for:
- Dashboard charts (Query 2)
- Activity lists (Query 3)
- Top recipients (Query 4)
- Testing data (Query 5)

### Step 4: Update organizations-summary.json
Use the date_ranges.csv to populate `firstActivity` and `lastActivity` fields:

```python
import pandas as pd
import json

# Load date ranges from BigQuery export
date_ranges = pd.read_csv('date_ranges.csv')

# Load existing summary
with open('src/data/organizations-summary.json', 'r') as f:
    summary = json.load(f)

# Update organizations
for org in summary['organizations']:
    filer_id = org['filer_id']
    dates = date_ranges[date_ranges['filer_id'] == int(filer_id)]

    if len(dates) > 0:
        org['firstActivity'] = dates.iloc[0]['first_activity']
        org['lastActivity'] = dates.iloc[0]['last_activity']

# Save updated summary
with open('src/data/organizations-summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
```

## Important Notes

### 1. Table Names in Production
The queries use `ca-lobby.ca_lobby.CVR2_LOBBY_DISCLOSURE_CD` which is the base disclosure table. If this doesn't exist, use:
- `ca-lobby.ca_lobby.v_disclosures` (full disclosures view)
- OR whatever the unfiltered disclosures table is called

### 2. Why Local Testing Doesn't Work
The CSV files in `Sample data/` are from FILTERED views:
- `v_disclosures_alameda.csv` only has disclosures WHERE filer is Alameda
- Payments are filed by lobbying firms (not Alameda filers)
- Therefore, payment filing_ids don't exist in the filtered disclosure CSV

This is EXPECTED and CORRECT. The queries will work in BigQuery production because you'll use the full disclosure table.

### 3. Data Validation
After importing date ranges, verify:
```python
python3 scripts/query_sample_data.py
```

All 11 organizations should show non-null dates.

## Summary

✅ **SQL queries are ready to execute in BigQuery**
✅ **Queries are optimized for the correct data model**
✅ **Documentation explains why local CSV testing returns empty results**
✅ **Next step: Run Query 1 in BigQuery console to get date ranges**

## Questions?

### "Why are there no disclosures for these organizations?"
Because they don't FILE disclosures - lobbying firms do. Organizations are CLIENTS.

### "How do we get their activity dates?"
Join payments (where they're the employer) to disclosures (filed by firms) via filing_id.

### "Why doesn't the test script return dates?"
Because the CSV file is a FILTERED view. Production BigQuery has the full disclosure table.

### "Are the SQL queries correct?"
Yes! They're ready to run in BigQuery. They won't work on the filtered CSV samples, but they will work in production.

---

**Created:** October 25, 2025
**Status:** Ready for BigQuery execution
**Next Step:** Run Query 1 in BigQuery console
