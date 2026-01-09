# Query Edge Cases Documentation

> **Comprehensive edge case analysis** for all SQL queries in the CA Lobby Mono application
>
> **Created**: January 8, 2026
>
> **Purpose**: Document known edge cases, potential data issues, and handling strategies for each query

---

## Table of Contents

1. [Analytics Endpoint Edge Cases](#analytics-endpoint-edge-cases)
2. [Search Endpoint Edge Cases](#search-endpoint-edge-cases)
3. [Common Edge Cases](#common-edge-cases)
4. [Data Quality Issues](#data-quality-issues)
5. [Mitigation Strategies](#mitigation-strategies)

---

## Analytics Endpoint Edge Cases

**File**: `/api/analytics.py`

### Query 1: Summary Analytics (`type=summary`)

**Purpose**: Count total organizations, filings, and latest filing date

**Edge Cases**:

| Edge Case | Description | Impact | Handling |
|-----------|-------------|--------|----------|
| **No data for current year** | If queried in early January, 2026 data may not exist | Returns 0 or outdated stats | Filter uses `>= 2000`, so historical data always returned |
| **NULL RPT_DATE_DATE** | Some filings have NULL report dates | Excluded from count | `WHERE RPT_DATE_DATE IS NOT NULL` filters these |
| **Future-dated filings** | Data entry errors with future dates | Could inflate counts | `RPT_DATE_DATE <= CURRENT_DATE()` filters these |
| **Duplicate FILER_IDs** | Same organization with multiple IDs | Overcounts organizations | COUNT(DISTINCT FILER_ID) handles this |
| **Empty result set** | No filings match criteria | Empty response | Returns `{}` - frontend should handle |

**Test Queries**:
```sql
-- Check for NULL report dates
SELECT COUNT(*) FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` WHERE RPT_DATE_DATE IS NULL;

-- Check for future-dated filings
SELECT COUNT(*) FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` WHERE RPT_DATE_DATE > CURRENT_DATE();
```

---

### Query 2: Trends Analytics (`type=trends`)

**Purpose**: Filing trends by year/period (last 12 periods)

**Edge Cases**:

| Edge Case | Description | Impact | Handling |
|-----------|-------------|--------|----------|
| **Missing periods** | Some quarters may have zero filings | Gaps in timeline | Frontend should handle missing periods |
| **RPT_DATE variations** | Period format inconsistency (Q1 vs Q1 2024) | Grouping issues | Extracted separately: year + period |
| **Year boundary** | December filings for next year's period | Misclassification | RPT_DATE reflects actual period, not filing date |
| **2020 cutoff** | Data before 2020 excluded | May miss historical trends | Intentional - filters to recent data |
| **More than 12 periods** | LIMIT 12 may not show all years | Incomplete yearly view | By design - shows last 12 periods only |

**Known Data Issues**:
- RPT_DATE format: Some entries use "Q1 2024", others use "1st Quarter 2024"
- Empty RPT_DATE: Some filings have NULL RPT_DATE but valid RPT_DATE_DATE

---

### Query 3: Top Organizations (`type=top_organizations`)

**Purpose**: Top 10 organizations by spending (uses v_organization_summary view)

**Edge Cases**:

| Edge Case | Description | Impact | Handling |
|-----------|-------------|--------|----------|
| **NULL organization_name** | Some orgs have no name | Empty rows in results | `WHERE organization_name IS NOT NULL` |
| **NULL total_spending** | Orgs with filings but no payments | Missing from list | `WHERE total_spending IS NOT NULL` |
| **Zero spending** | Orgs with $0 in payments | Would appear as 0 | `AND total_spending > 0` filters |
| **Negative spending** | Data entry errors | Would affect ranking | Not explicitly handled - could add ABS() |
| **Ties at position 10** | Multiple orgs with same spending | Arbitrary cutoff | ORDER BY may vary - consider adding secondary sort |
| **organization_filer_id NULL** | View has NULL filer_id for some orgs | Can't link to details | Known issue - see search query fix |

**View Limitations**:
- v_organization_summary has ~37K orgs with payment data only
- Orgs with only filings (no LPAY_CD records) are not in view
- total_filings and total_lobbying_firms are often NULL

---

### Query 4: Spending Trends (`type=spending`)

**Purpose**: Yearly city/county spending trends (2015-present)

**Edge Cases**:

| Edge Case | Description | Impact | Handling |
|-----------|-------------|--------|----------|
| **Classification misses** | EMPLR_NAML doesn't match city/county patterns | Goes to 'other' bucket | Pattern covers most cases, may miss edge cases |
| **Special districts** | "Water District", "Fire District" | Classified as 'other' | Not city/county per business logic |
| **Multi-county orgs** | "Los Angeles/Orange County..." | May match county pattern | First match wins |
| **Case sensitivity** | "city of" vs "CITY OF" | Could miss matches | `UPPER()` handles this |
| **NULL EMPLR_NAML** | Some payments have no employer name | Excluded | Goes to 'other' if not NULL |
| **NULL PER_TOTAL** | Payment without amount | Excluded | `AND pay.PER_TOTAL IS NOT NULL` |
| **Zero/negative amounts** | Invalid amounts | Excluded | `AND CAST(pay.PER_TOTAL AS FLOAT64) > 0` |
| **Future years** | Current year filter issue | No data for 2026 in early 2026 | `<= EXTRACT(YEAR FROM CURRENT_DATE())` |
| **Year with no data** | Gap year in data | Missing from results | Will show 0 or skip year |

**Classification Pattern Limitations**:
```sql
-- These patterns are used:
'%CITY OF%'           -- Matches: "CITY OF LOS ANGELES", "CITY OF..."
'%LEAGUE%CITIES%'     -- Matches: "LEAGUE OF CALIFORNIA CITIES"
'%COUNTY%'            -- Matches: "COUNTY OF LOS ANGELES", "LOS ANGELES COUNTY"
'%CSAC%'              -- Matches: "CSAC" (California State Association of Counties)
'%ASSOCIATION OF COUNTIES%'  -- Matches: "CALIFORNIA STATE ASSOCIATION OF COUNTIES"

-- May miss:
-- "Town of Mammoth Lakes" (not city/county)
-- "City and County of San Francisco" (matches city first)
```

---

### Query 5: Spending Breakdown (`type=spending_breakdown`)

**Purpose**: City/county spending breakdown for 2025

**Edge Cases**:

| Edge Case | Description | Impact | Handling |
|-----------|-------------|--------|----------|
| **No 2025 data** | Query hardcoded to 2025 | Returns empty | Returns default zero structure |
| **Partial year data** | Only Q1-Q2 data available | Lower totals | Expected - shows YTD |
| **Membership detection removed** | Previously had membership category | Simplified output | Now shows only city/county totals |

**Year Hardcoding Issue**:
- Query uses `EXTRACT(YEAR FROM p.RPT_DATE_DATE) = 2025`
- Should be updated yearly or made dynamic
- In 2026, this will show 2025 data (may be intentional or not)

---

### Query 6: Organization Spending by Govt Type (`type=org_spending_by_govt`)

**Purpose**: Top 10 lobbying firms with city/county breakdown

**Edge Cases**:

| Edge Case | Description | Impact | Handling |
|-----------|-------------|--------|----------|
| **Same issues as Query 5** | Hardcoded 2025, classification patterns | See Query 5 | See Query 5 |
| **Firm name variations** | Same firm with multiple PAYEE_NAML spellings | Split into multiple entries | Not deduplicated |
| **Ties at position 10** | Same as Query 3 | Arbitrary cutoff | By design |

**Firm Name Standardization Issues**:
- "TOWNSEND PUBLIC AFFAIRS" vs "TOWNSEND PUBLIC AFFAIRS INC"
- "NIELSEN MERKSAMER" vs "NIELSEN, MERKSAMER, PARRINELLO"
- These appear as separate entries

---

### Query 7 & 8: Top City/County Recipients (`type=top_city_recipients`, `type=top_county_recipients`)

**Purpose**: Top 10 lobbying firms paid by cities/counties (last 3 years)

**Edge Cases**:

| Edge Case | Description | Impact | Handling |
|-----------|-------------|--------|----------|
| **Empty PAYEE_NAML** | Payments with no recipient name | Excluded | `WHERE pay.PAYEE_NAML IS NOT NULL AND pay.PAYEE_NAML != ''` |
| **3-year window** | Uses `>= CURRENT_DATE() - 2` years | May miss older firms | By design - recent data only |
| **Firm name variations** | Same as Query 6 | Split entries | Not deduplicated |
| **Cross-classification** | Firm paid by both city AND county | Appears in both lists | Expected behavior |

---

## Search Endpoint Edge Cases

**File**: `/api/search.py`

### Query 9: Organization Filings

**Purpose**: Get all filings for a specific organization

**Edge Cases**:

| Edge Case | Description | Impact | Handling |
|-----------|-------------|--------|----------|
| **No matches** | Organization name not found | Empty results | Returns empty array |
| **Partial matches** | "CITY OF" matches multiple cities | Returns all matches | LIKE with wildcards |
| **Case mismatch** | "city of los angeles" vs "CITY OF LOS ANGELES" | Could miss | `UPPER()` handles this |
| **Name variations** | "LA CITY" vs "CITY OF LOS ANGELES" | May not match | User must know exact name format |
| **Recent partition only** | FROM_DATE_DATE >= 2020 filter | No pre-2020 data | By design - partitioned table |
| **Year 2000-2025 filter** | Hardcoded year range | Needs update in 2026 | `BETWEEN 2000 AND 2025` should be dynamic |

**Partition Table Considerations**:
- Uses `cvr_lobby_disclosure_cd_partitioned` for cost savings
- Only has data from 2020 onwards
- Older data available in main table but not searched

---

### Query 10: Main Search Query

**Purpose**: Paginated organization search with spending data

**Edge Cases**:

| Edge Case | Description | Impact | Handling |
|-----------|-------------|--------|----------|
| **filer_id NULL from view** | v_organization_summary has NULL filer_id | Can't link to details | **FIXED**: Now joins with raw table to get FILER_ID |
| **Name mismatch in join** | View org name != raw table FILER_NAML | filer_id = 0 | Case-insensitive UPPER() join helps |
| **Org in both CTEs** | Could appear twice | Duplicate results | NOT IN clause prevents this |
| **Empty search term** | @search_term = NULL or empty | Returns all orgs | `@search_term IS NULL OR` handles this |
| **Special characters** | Searching "O'Brien" or "Smith & Jones" | SQL escaping needed | Parameterized query handles this |
| **Very long search terms** | 100+ character search | Performance impact | No limit enforced |
| **Pagination edge** | Page 999 with 25 results | May return nothing | Returns empty if offset > total |

**filer_id Resolution Logic** (after fix):
```sql
-- View results get filer_id from separate CTE join
LEFT JOIN filer_ids f ON UPPER(vr.organization_name) = UPPER(f.organization_name)
-- Returns 0 if no match found (COALESCE)
```

---

### Query 11: Count Query

**Purpose**: Total count for pagination

**Edge Cases**:

| Edge Case | Description | Impact | Handling |
|-----------|-------------|--------|----------|
| **Count mismatch** | Count query may differ from main query | Wrong pagination | Uses same WHERE clauses |
| **Large counts** | 50,000+ results | Slow count | Could add APPROX_COUNT_DISTINCT() for large sets |

---

## Common Edge Cases

These apply across multiple queries:

### Date Handling

| Edge Case | Affected Queries | Impact | Recommendation |
|-----------|------------------|--------|----------------|
| **Timezone issues** | All with dates | Off-by-one errors | BigQuery uses UTC - consider timezone |
| **Leap year** | Date comparisons | Edge day issues | Use DATE functions, not strings |
| **Year boundary** | Yearly aggregations | Dec 31 / Jan 1 misclass | Ensure RPT_DATE_DATE is used consistently |

### NULL Handling

| Edge Case | Affected Queries | Impact | Recommendation |
|-----------|------------------|--------|----------------|
| **NULL in aggregations** | SUM, AVG, COUNT | Ignored by default | Handled correctly by SQL |
| **NULL in WHERE** | All queries | May exclude valid rows | Use IS NOT NULL explicitly |
| **NULL in LIKE** | Search queries | Won't match | Pre-filter NULLs |

### Numeric Precision

| Edge Case | Affected Queries | Impact | Recommendation |
|-----------|------------------|--------|----------------|
| **Float precision** | Spending amounts | Rounding errors | ROUND() for display |
| **Large numbers** | Total spending | Overflow possible | FLOAT64 handles up to 10^308 |
| **String to number** | PER_TOTAL casts | Failed casts = NULL | SAFE_CAST returns NULL on failure |

---

## Data Quality Issues

### Known Data Issues in CAL-ACCESS

| Issue | Tables Affected | Description | Workaround |
|-------|-----------------|-------------|------------|
| **Inconsistent org names** | All | Same org with different spellings | No automatic resolution |
| **Missing amendments** | cvr_lobby_disclosure_cd | Some AMEND_ID sequences have gaps | Filter to MAX(AMEND_ID) only |
| **Orphaned payments** | lpay_cd | Payments with no matching disclosure | JOIN filters these out |
| **Future dates** | cvr_lobby_disclosure_cd | Some RPT_DATE_DATE > today | Filter with `<= CURRENT_DATE()` |
| **Negative amounts** | lpay_cd | Some PER_TOTAL < 0 | Filter with `> 0` |
| **Empty strings** | Multiple | Fields with '' instead of NULL | Check for both |

### View Limitations

| View | Limitation | Impact |
|------|------------|--------|
| v_organization_summary | Only orgs with payments | ~37K orgs, misses filing-only orgs |
| v_organization_summary | NULL organization_filer_id | Can't link to raw data |
| v_organization_summary | NULL total_filings | Can't show filing counts |

---

## Mitigation Strategies

### Frontend Handling

```javascript
// Handle empty results
if (!data || data.length === 0) {
  return <NoDataMessage />;
}

// Handle NULL values
const displayValue = value ?? 'N/A';

// Handle filer_id = 0 (unresolved)
if (filer_id === 0 || filer_id === null) {
  return <span className="unavailable">ID unavailable</span>;
}
```

### Backend Handling

```python
# Return default structure on empty results
if not result:
    return [
        {'govt_type': 'city', 'total_amount': 0, 'filer_count': 0},
        {'govt_type': 'county', 'total_amount': 0, 'filer_count': 0}
    ]

# Handle query exceptions
try:
    result = client.execute_query(query)
except Exception as e:
    logger.error(f"Query failed: {e}")
    return default_response
```

### SQL Defensive Patterns

```sql
-- Use COALESCE for NULL handling
COALESCE(filer_id, 0) as filer_id

-- Use SAFE_CAST for type conversion
SAFE_CAST(PER_TOTAL AS FLOAT64)

-- Use IFNULL for defaults
IFNULL(total_spending, 0) as total_spending

-- Use explicit NULL checks
WHERE field IS NOT NULL AND field != ''
```

---

## Testing Recommendations

### Unit Test Queries

```sql
-- Test 1: Verify no NULL filer_ids in search results
SELECT COUNT(*) FROM (...search query...) WHERE filer_id IS NULL;
-- Expected: 0

-- Test 2: Verify amendment filtering
SELECT COUNT(*) FROM cvr_lobby_disclosure_cd
WHERE (FILING_ID, AMEND_ID) NOT IN (
    SELECT FILING_ID, MAX(AMEND_ID) FROM cvr_lobby_disclosure_cd GROUP BY FILING_ID
);
-- Expected: > 0 (there ARE amendments to filter)

-- Test 3: Verify city/county patterns match expected orgs
SELECT DISTINCT EMPLR_NAML FROM lpay_cd
WHERE UPPER(EMPLR_NAML) LIKE '%CITY OF%'
LIMIT 10;
-- Expected: All results should be cities
```

### Edge Case Test Scenarios

1. **Empty search**: Search with `q=` (empty string) - should return all
2. **No results**: Search with `q=XYZNONEXISTENT` - should return empty array
3. **Special chars**: Search with `q=O'Brien` - should not cause SQL error
4. **Large pagination**: Request `page=9999` - should return empty, not error
5. **Future year**: Request spending for 2030 - should return zeros

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-08 | 1.0 | Initial edge case documentation |

---

**References**:
- [QUERY_ANALYSIS_REPORT.md](QUERY_ANALYSIS_REPORT.md) - Full query analysis
- [CLAUDE.md](CLAUDE.md) - SQL query standards
- [database_docs/](database_docs/) - CAL-ACCESS documentation
