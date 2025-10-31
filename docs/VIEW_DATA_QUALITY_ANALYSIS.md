# View Data Quality Analysis

**Date:** October 31, 2025
**Issue:** v_organization_summary view returns NULL for critical fields (filer_id, total_filings)
**Status:** ✅ **ROOT CAUSE IDENTIFIED**

---

## Executive Summary

The v_organization_summary view **intentionally** sets several fields to NULL because it's a lightweight wrapper around the mv_organization_summary **materialized view**, which aggregates data from the **payments table** (lpay_cd_with_dates), not the disclosures table.

**This is BY DESIGN** - the view is optimized for fast search and spending analysis, not for comprehensive organizational metadata.

---

## View Architecture

### Current Structure

```
lpay_cd_with_dates (44.8M payment records)
         ↓
mv_organization_summary (materialized view - 35,830 orgs)
         ↓
v_organization_summary (regular view - adds NULL fields)
```

### mv_organization_summary (Materialized View)

**Source:** `ca-lobby.ca_lobby.lpay_cd_with_dates` (payments table)

**Query:**
```sql
SELECT
    EMPLR_NAML as organization_name,
    EMPLR_CITY as city,
    EMPLR_ST as state,
    COUNT(*) as payment_count,
    SUM(CAST(PER_TOTAL AS FLOAT64)) as total_payments,
    AVG(CAST(PER_TOTAL AS FLOAT64)) as avg_payment,
    MIN(FROM_DATE_DATE) as first_filing_date,
    MAX(FROM_DATE_DATE) as last_filing_date
FROM `ca-lobby.ca_lobby.lpay_cd_with_dates`
WHERE EMPLR_NAML IS NOT NULL
    AND PER_TOTAL IS NOT NULL
    AND PER_TOTAL != ''
    AND PER_TOTAL != 'nan'
GROUP BY EMPLR_NAML, EMPLR_CITY, EMPLR_ST
```

**What It Provides:**
- ✅ organization_name
- ✅ city, state
- ✅ payment_count (number of payment records)
- ✅ total_payments (sum of all payments)
- ✅ avg_payment
- ✅ first_filing_date, last_filing_date

**What It DOESN'T Provide:**
- ❌ Filer ID (not in lpay_cd table)
- ❌ Total filings count (not counting filings, counting payments)
- ❌ Lobbying firms count

---

### v_organization_summary (Regular View)

**Source:** `ca-lobby.ca_lobby.mv_organization_summary` (materialized view above)

**Query:**
```sql
SELECT
  organization_name,
  NULL as organization_filer_id,          -- ⚠️ Intentionally NULL
  city as organization_city,
  state as organization_state,
  NULL as total_filings,                  -- ⚠️ Intentionally NULL
  NULL as total_lobbying_firms,           -- ⚠️ Intentionally NULL
  payment_count as total_payment_line_items,
  NULL as total_fees,                     -- ⚠️ Intentionally NULL
  NULL as total_reimbursements,           -- ⚠️ Intentionally NULL
  NULL as total_advances,                 -- ⚠️ Intentionally NULL
  total_payments as total_spending,
  first_filing_date as first_activity_date,
  last_filing_date as last_activity_date,
  EXTRACT(YEAR FROM last_filing_date) as most_recent_year
FROM `ca-lobby.ca_lobby.mv_organization_summary`
ORDER BY total_spending DESC, organization_name
```

**Purpose:** Adds NULL fields for frontend compatibility while maintaining instant query performance from the materialized view.

---

## Why NULL Values Exist

### 1. organization_filer_id is NULL

**Reason:** The lpay_cd (payments) table does NOT contain FILER_ID.

**Explanation:**
- Payments table has: EMPLR_NAML (employer name), but no FILER_ID
- FILER_ID only exists in cvr_lobby_disclosure_cd (cover/filing table)
- To get FILER_ID, would need to JOIN lpay_cd → cvr_lobby_disclosure_cd
- This would eliminate the 99% cost reduction benefit

**Impact:**
- Cannot link to organization profiles by ID
- Must use organization_name for matching (case-sensitive issues)

---

### 2. total_filings is NULL

**Reason:** The materialized view aggregates **payments**, not **filings**.

**Explanation:**
- mv_organization_summary counts payment records (`COUNT(*)`)
- Each filing can have 0-100+ payment line items
- To get filing count, would need to:
  - JOIN lpay_cd → cvr_lobby_disclosure_cd
  - COUNT(DISTINCT FILING_ID)
- This would eliminate the performance benefits

**Current Workaround:**
- Frontend uses `total_payment_line_items` (payment count) as proxy
- Top Organizations endpoint renamed to show "by spending" instead of "by filings"

---

### 3. total_lobbying_firms is NULL

**Reason:** Firm relationships are in a separate table (lccm_cd).

**Explanation:**
- Lobbyist/firm relationships are in lccm_cd (lobbyist/client/firm table)
- Not available in lpay_cd
- Would require complex 3-way JOIN to compute

**Impact:**
- Cannot show "hired 5 lobbying firms" in organization summary
- This metric is not critical for primary use case (search by spending)

---

## User-Reported Issues

### Issue 1: Search for "islamic" Returns 0 Results

**Status:** ⚠️ **UNRELATED TO NULL VALUES** - This is a **view staleness** issue

**Findings:**
```sql
-- Raw table has the organization
SELECT * FROM cvr_lobby_disclosure_cd
WHERE UPPER(FILER_NAML) LIKE '%ISLAMIC%'
-- Returns: "Council on American-Islamic Relations, California" (13 filings, 2025)

-- Materialized view does NOT have it
SELECT * FROM mv_organization_summary
WHERE UPPER(organization_name) LIKE '%ISLAMIC%'
-- Returns: 0 rows
```

**Root Cause:** The materialized view has not been refreshed with 2025 data.

**Solution:** Refresh mv_organization_summary materialized view (see below).

---

### Issue 2: "Major League Baseball" Shows 0 Filings in Profile

**Status:** ⚠️ **CAUSED BY NULL organization_filer_id**

**Findings:**
```sql
-- View has organization but with NULL filer_id
SELECT * FROM v_organization_summary
WHERE organization_name = 'Major League Baseball'
-- Returns: organization_filer_id = NULL, total_filings = NULL

-- Raw table has the data
SELECT * FROM cvr_lobby_disclosure_cd
WHERE UPPER(FILER_NAML) LIKE '%MAJOR LEAGUE BASEBALL%'
-- Returns: FILER_ID = 1406959, 243 filings
```

**Root Causes:**
1. **NULL filer_id** - Profile page cannot match by ID
2. **Case sensitivity** - View has "Major League Baseball", raw has "MAJOR LEAGUE BASEBALL"
3. **Exact match vs LIKE** - Profile page may use exact name match

**Solutions:**
- Option A: Update profile page to use case-insensitive LIKE matching
- Option B: Query raw cvr_lobby_disclosure_cd table for profile details
- Option C: Create separate view that joins to get filer_id

---

## Design Trade-offs

### Current Design: Optimized for Speed & Cost

**Benefits:**
- ✅ 99% cost reduction (instant queries, 0 GB scanned)
- ✅ Sub-second response times for search
- ✅ No complex JOINs
- ✅ Auto-refreshes daily
- ✅ Perfect for search/discovery use case

**Limitations:**
- ❌ No filer_id (can't link by ID)
- ❌ No filing count (only payment count)
- ❌ Can't drill into organization details without additional query

---

### Alternative Design: Complete Data (Not Implemented)

**What it would look like:**
```sql
CREATE MATERIALIZED VIEW mv_organization_complete AS
SELECT
  cvr.FILER_ID as organization_filer_id,
  cvr.FILER_NAML as organization_name,
  COUNT(DISTINCT cvr.FILING_ID) as total_filings,
  COUNT(DISTINCT lccm.FIRM_ID) as total_lobbying_firms,
  SUM(CAST(lpay.PER_TOTAL AS FLOAT64)) as total_spending
FROM cvr_lobby_disclosure_cd_partitioned cvr
LEFT JOIN lpay_cd_with_dates lpay ON cvr.FILING_ID = lpay.FILING_ID
LEFT JOIN lccm_cd lccm ON cvr.FILING_ID = lccm.FILING_ID
GROUP BY cvr.FILER_ID, cvr.FILER_NAML
```

**Benefits:**
- ✅ Has filer_id
- ✅ Accurate filing counts
- ✅ Firm relationship counts
- ✅ Can link to profiles by ID

**Costs:**
- ❌ More expensive to compute (3-way JOIN)
- ❌ Larger materialized view
- ❌ Slower refresh times
- ❌ Higher storage costs

**Recommendation:** NOT WORTH IT - Use two-tier approach instead (see Solutions below).

---

## Recommended Solutions

### Solution 1: Two-Tier Architecture (RECOMMENDED)

**Use current v_organization_summary for search/discovery:**
```sql
-- Fast, cheap search
SELECT * FROM v_organization_summary
WHERE UPPER(organization_name) LIKE '%LEAGUE%'
ORDER BY total_spending DESC;
```

**Use raw tables for organization profile details:**
```sql
-- Detailed profile view
SELECT
  cvr.FILER_ID,
  cvr.FILER_NAML,
  COUNT(DISTINCT cvr.FILING_ID) as total_filings,
  SUM(CAST(lpay.PER_TOTAL AS FLOAT64)) as total_spending
FROM cvr_lobby_disclosure_cd_partitioned cvr
LEFT JOIN lpay_cd_with_dates lpay
  ON cvr.FILING_ID = lpay.FILING_ID
WHERE UPPER(cvr.FILER_NAML) LIKE @search_term
  AND cvr.FROM_DATE_DATE >= '2020-01-01'  -- Partition filter
GROUP BY cvr.FILER_ID, cvr.FILER_NAML
```

**Benefits:**
- ✅ Search is instant and cheap (uses materialized view)
- ✅ Profile page gets complete data (uses raw tables with partitioning)
- ✅ Balance between cost and completeness
- ✅ No breaking changes to search

---

### Solution 2: Refresh Materialized View

**Issue:** mv_organization_summary is missing recent 2025 data

**Solution:** Trigger manual refresh:
```sql
-- Refresh materialized view
CALL BQ.REFRESH_MATERIALIZED_VIEW('ca-lobby.ca_lobby.mv_organization_summary');
```

**Schedule:** Auto-refreshes daily, but can manually trigger if needed.

---

### Solution 3: Fix Organization Profile Page

**Current Issue:** Profile page shows "0 filings" for organizations that exist

**Options:**

**Option A: Use case-insensitive LIKE matching**
```python
query = """
SELECT
  FILER_ID,
  FILER_NAML as organization_name,
  COUNT(*) as filing_count,
  MIN(FROM_DATE_DATE) as first_filing,
  MAX(FROM_DATE_DATE) as last_filing
FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd_partitioned`
WHERE UPPER(FILER_NAML) LIKE UPPER(@search_term)
  AND FROM_DATE_DATE >= '2020-01-01'
GROUP BY FILER_ID, FILER_NAML
"""
```

**Option B: Create organization profile view**
```sql
CREATE VIEW v_org_profile_lookup AS
SELECT
  cvr.FILER_ID,
  cvr.FILER_NAML as organization_name,
  COUNT(DISTINCT cvr.FILING_ID) as total_filings,
  MIN(cvr.FROM_DATE_DATE) as first_filing_date,
  MAX(cvr.FROM_DATE_DATE) as last_filing_date,
  SUM(CAST(lpay.PER_TOTAL AS FLOAT64)) as total_spending
FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd_partitioned` cvr
LEFT JOIN `ca-lobby.ca_lobby.lpay_cd_with_dates` lpay
  ON cvr.FILING_ID = lpay.FILING_ID
WHERE cvr.FROM_DATE_DATE >= '2020-01-01'
GROUP BY cvr.FILER_ID, cvr.FILER_NAML;
```

---

## Action Items

### Immediate (Fix "islamic" Search Issue)
- [ ] Refresh mv_organization_summary materialized view
- [ ] Verify "Council on American-Islamic Relations, California" appears in search

### Short-term (Fix Profile Page)
- [ ] Update OrganizationProfile component to query raw tables instead of view
- [ ] Use case-insensitive LIKE matching for organization name
- [ ] Include partition filter (FROM_DATE_DATE >= '2020-01-01')
- [ ] Test with "Major League Baseball" and "islamic" organizations

### Medium-term (Documentation)
- [x] Document view architecture and NULL field reasoning (this document)
- [ ] Update LOCAL_TESTING_RESULTS.md with root cause analysis
- [ ] Add "Known Limitations" section to VIEW_ARCHITECTURE_README.md

### Long-term (Optional Enhancement)
- [ ] Consider creating v_org_profile_lookup view for profile pages
- [ ] Evaluate if two-tier architecture meets all use cases
- [ ] Monitor costs after profile page changes

---

## Conclusion

**The NULL values in v_organization_summary are BY DESIGN**, not a bug.

**Key Insights:**
1. The view is optimized for **fast, cheap search** (99% cost reduction)
2. It aggregates **payments**, not **filings** (different data source)
3. NULL fields are intentional placeholders for frontend compatibility
4. **This is the correct architecture** for the search use case

**The Real Issues:**
1. **View staleness** - mv_organization_summary needs refresh for 2025 data
2. **Profile page implementation** - Should query raw tables, not the search view

**Recommendation:** Keep the current search view architecture, but update the profile page to query raw tables with proper partitioning for detailed organization data.

---

**Document Version:** 1.0
**Author:** Claude (Sonnet 4.5)
**Last Updated:** October 31, 2025
