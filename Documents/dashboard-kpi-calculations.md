# Dashboard KPI Calculations

**Project**: ca-lobby_mono (California Lobbying Dashboard)
**Last Updated**: 2025-11-19
**Purpose**: Document how each KPI metric on the dashboard is calculated from BigQuery data

---

## Overview

This document explains the calculation methodology for each Key Performance Indicator (KPI) displayed on the California Lobbying Dashboard. All data is sourced from BigQuery tables in the `ca-lobby.ca_lobby` dataset.

---

## KPI Definitions

### 1. Total Lobbying Expenditures

**Display**: `$XX.X M` (millions of dollars with comma formatting)
- Example: `$24.2M` (displays as "$24.2M" with comma if needed for larger numbers like "$1,234.5M")

**Plain English**:
This KPI shows the total amount of money spent on lobbying in California for the current year. It adds up all payments made by every organization (cities, counties, corporations, nonprofits, etc.) that filed lobbying disclosure forms. The number is displayed in millions of dollars with commas for readability (e.g., $24.2M means $24,200,000). Numbers are formatted with commas using JavaScript's `toLocaleString()` function.

**SQL Query**:
```sql
WITH yearly_spending AS (
    SELECT
        EXTRACT(YEAR FROM p.RPT_DATE_DATE) as year,
        p.FILER_ID as filer_id,
        CAST(pay.PER_TOTAL AS FLOAT64) as amount,
        CASE
            WHEN UPPER(p.FIRM_NAME) LIKE '%CITY OF%' THEN 'city'
            WHEN UPPER(p.FIRM_NAME) LIKE '%COUNTY%' THEN 'county'
            ELSE 'other'
        END as govt_type
    FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` p
    LEFT JOIN `ca-lobby.ca_lobby.lpay_cd` pay ON p.FILING_ID = pay.FILING_ID
    WHERE p.RPT_DATE_DATE IS NOT NULL
      AND p.RPT_DATE_DATE <= CURRENT_DATE()
      AND EXTRACT(YEAR FROM p.RPT_DATE_DATE) >= 2015
      AND EXTRACT(YEAR FROM p.RPT_DATE_DATE) <= EXTRACT(YEAR FROM CURRENT_DATE())
      AND pay.PER_TOTAL IS NOT NULL
      AND CAST(pay.PER_TOTAL AS FLOAT64) > 0
)
SELECT
    year,
    SUM(amount) as total_spending,
    SUM(CASE WHEN govt_type = 'city' THEN amount ELSE 0 END) as city_spending,
    SUM(CASE WHEN govt_type = 'county' THEN amount ELSE 0 END) as county_spending,
    COUNT(DISTINCT CASE WHEN govt_type = 'city' THEN filer_id END) as city_count,
    COUNT(DISTINCT CASE WHEN govt_type = 'county' THEN filer_id END) as county_count
FROM yearly_spending
GROUP BY year
ORDER BY year ASC
```

**Frontend Selection** (Dashboard.js line 123):
```javascript
// Get the latest year's data from the results array
const latestYear = spendingData[spendingData.length - 1];
const totalSpending = latestYear?.total_spending || 0;
```

**How to read the query**:
1. Look at all lobbying disclosure forms (`cvr_lobby_disclosure_cd`)
2. Join them with payment records (`lpay_cd`) to get dollar amounts
3. Filter to years 2015 through current year (returns data for ALL years, not just current)
4. Group by year and calculate total spending for each year
5. **Frontend selects only the latest year** from the results: `spendingData[spendingData.length - 1]`
6. Display the latest year's total in millions

**Important**: The query returns multiple years of data, but the dashboard displays only the most recent year's total.

**Data Source**:
- Table: `cvr_lobby_disclosure_cd` (disclosure forms) joined with `lpay_cd` (payment records)
- Field: `lpay_cd.PER_TOTAL` (payment amount)

**Frontend Code**: [Dashboard.js:168](../frontend/src/components/Dashboard.js#L168)
**API Endpoint**: `/api/analytics?type=spending`

---

### 2. City Government Lobby Organizations/Departments

**Display**: Whole number with comma formatting
- Example: `17` or `1,234` (larger numbers display with commas like "1,234")

**Plain English**:
This KPI counts how many city government organizations or departments are actively lobbying. It does NOT count the number of cities - it counts how many separate city entities are filing lobbying reports. For example, if Los Angeles has its Fire Department and Police Department both lobbying separately, that counts as 2, not 1. This shows the scale and complexity of city government lobbying activity.

**SQL Query**:
```sql
WITH yearly_spending AS (
    SELECT
        EXTRACT(YEAR FROM p.RPT_DATE_DATE) as year,
        p.FILER_ID as filer_id,
        CASE
            WHEN UPPER(p.FIRM_NAME) LIKE '%CITY OF%' THEN 'city'
            WHEN UPPER(p.FIRM_NAME) LIKE '%COUNTY%' THEN 'county'
            ELSE 'other'
        END as govt_type
    FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` p
    LEFT JOIN `ca-lobby.ca_lobby.lpay_cd` pay ON p.FILING_ID = pay.FILING_ID
    WHERE p.RPT_DATE_DATE IS NOT NULL
      AND EXTRACT(YEAR FROM p.RPT_DATE_DATE) = EXTRACT(YEAR FROM CURRENT_DATE())
      AND pay.PER_TOTAL IS NOT NULL
      AND CAST(pay.PER_TOTAL AS FLOAT64) > 0
)
SELECT
    COUNT(DISTINCT CASE WHEN govt_type = 'city' THEN filer_id END) as city_count
FROM yearly_spending
```

**How to read the query**:
1. Look at all lobbying disclosure forms for the current year
2. Identify which ones are from city governments (name contains "CITY OF")
3. Count how many different FILER_IDs (unique organization identifiers) there are
4. Each FILER_ID = one city department or organization filing separately

**Important Note**:
- This counts **organizations/departments**, NOT unique cities
- Example: "City of Los Angeles Fire Dept" (FILER_ID 123) = 1 count
- Example: "City of Los Angeles Police Dept" (FILER_ID 456) = 1 count
- Total for Los Angeles = 2 separate entities counted
- California has 482 cities, but this number will be different because it's counting department-level entities

**Data Source**:
- Table: `cvr_lobby_disclosure_cd`
- Field: `FIRM_NAME` (organization name) - used to identify city entities
- Field: `FILER_ID` (unique identifier for each filing organization) - used to count distinct entities

**Frontend Code**: [Dashboard.js:180](../frontend/src/components/Dashboard.js#L180)
**API Endpoint**: `/api/analytics?type=spending`

---

### 3. County Government Lobby Organizations/Departments

**Display**: Whole number with comma formatting
- Example: `72` (uses `toLocaleString()` to add commas for readability)

**Plain English**:
This KPI counts how many county government organizations or departments are actively lobbying. Like the city count, this does NOT count the number of counties - it counts how many separate county entities are filing lobbying reports. For example, if Los Angeles County has its Fire Department, Health Department, and Sheriff's Department all lobbying separately, that counts as 3, not 1. This shows the scale and complexity of county government lobbying activity.

**SQL Query**:
```sql
WITH yearly_spending AS (
    SELECT
        EXTRACT(YEAR FROM p.RPT_DATE_DATE) as year,
        p.FILER_ID as filer_id,
        CASE
            WHEN UPPER(p.FIRM_NAME) LIKE '%CITY OF%' THEN 'city'
            WHEN UPPER(p.FIRM_NAME) LIKE '%COUNTY%' THEN 'county'
            ELSE 'other'
        END as govt_type
    FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` p
    LEFT JOIN `ca-lobby.ca_lobby.lpay_cd` pay ON p.FILING_ID = pay.FILING_ID
    WHERE p.RPT_DATE_DATE IS NOT NULL
      AND EXTRACT(YEAR FROM p.RPT_DATE_DATE) = EXTRACT(YEAR FROM CURRENT_DATE())
      AND pay.PER_TOTAL IS NOT NULL
      AND CAST(pay.PER_TOTAL AS FLOAT64) > 0
)
SELECT
    COUNT(DISTINCT CASE WHEN govt_type = 'county' THEN filer_id END) as county_count
FROM yearly_spending
```

**How to read the query**:
1. Look at all lobbying disclosure forms for the current year
2. Identify which ones are from county governments (name contains "COUNTY")
3. Count how many different FILER_IDs (unique organization identifiers) there are
4. Each FILER_ID = one county department or organization filing separately

**Calculation Method**:
```sql
COUNT(DISTINCT CASE WHEN govt_type = 'county' THEN filer_id END) as county_count

WHERE govt_type = CASE
    WHEN UPPER(p.FIRM_NAME) LIKE '%COUNTY%' THEN 'county'
    ...
END
```

**What it counts**:
- **Unique FILER_IDs** where `FIRM_NAME` contains "COUNTY"
- Each filer ID represents a separate lobbying organization/department
- **Important**: This counts departments separately, NOT unique counties
  - Example: "Los Angeles County Fire Dept" (FILER_ID 789) = 1
  - Example: "Los Angeles County Health Dept" (FILER_ID 012) = 1
  - Total for Los Angeles County = 2 departments counted separately

**Why this matters**:
- Shows how many county government entities are engaged in lobbying
- Reflects organizational complexity (larger counties may have many departments lobbying)
- Should NOT be compared to California's 58 total counties (this counts departments, not counties)
- Current 2025 count of 72 means some counties have multiple departments filing separately

**Data Source**:
- Table: `cvr_lobby_disclosure_cd`
- Field: `FIRM_NAME` (organization name)
- Field: `FILER_ID` (unique identifier for each filing organization)

**Frontend Code**: [Dashboard.js:192](../frontend/src/components/Dashboard.js#L192)
**API Endpoint**: `/api/analytics?type=spending`

---

### 4. City Membership Spending

**Display**: `$XX.XX M` (millions of dollars with 2 decimal places and comma formatting)
- Example: `$12.34M` or `$1,234.56M` (uses `toLocaleString()` with 2 decimal places)

**Plain English**:
This KPI shows how much money city governments spend on membership dues to organizations like the League of California Cities. These membership organizations provide collective advocacy, training, and resources to cities. Instead of each city hiring their own lobbyists, they pool resources through memberships. This spending category is separate from direct lobbying services or lobbying firm contracts.

**SQL Query**:
```sql
SELECT
    SUM(total_spending) as total_amount
FROM `ca-lobby.ca_lobby.v_organization_summary`
WHERE (
    UPPER(organization_name) LIKE '%LEAGUE%'
    OR UPPER(organization_name) LIKE '%ASSOCIATION%'
    OR UPPER(organization_name) LIKE '%COALITION%'
)
AND UPPER(organization_name) LIKE '%CITY%'
AND spending_category = 'membership'
```

**How to read the query**:
1. Look at the pre-aggregated organization summary view (37K rows, much faster than raw data)
2. Find organizations with city-related names ("CITY")
3. Filter to membership organizations ("LEAGUE", "ASSOCIATION", "COALITION")
4. Sum up all the spending amounts
5. Display the total in millions of dollars

**Calculation Method**:
```sql
SUM(total_spending) as total_amount
FROM `ca-lobby.ca_lobby.v_organization_summary`
WHERE (
    UPPER(organization_name) LIKE '%LEAGUE%'
    OR UPPER(organization_name) LIKE '%ASSOCIATION%'
    OR UPPER(organization_name) LIKE '%COALITION%'
)
AND UPPER(organization_name) LIKE '%CITY%'
AND spending_category = 'membership'
```

**What it counts**:
- Total spending by city governments on membership dues
- Primarily captures:
  - League of California Cities membership dues
  - City associations and coalitions
- Uses the pre-aggregated `v_organization_summary` view for performance

**Categorization Logic**:
- **Membership**: Organization name contains "LEAGUE", "ASSOCIATION", or "COALITION"
- **City**: Organization name contains "CITY"

**Data Source**:
- View: `v_organization_summary` (pre-aggregated from 37K rows)
- Field: `total_spending`
- Benefits: ~150x faster than raw table JOINs

**Frontend Code**: [Dashboard.js:207](../frontend/src/components/Dashboard.js#L207)
**API Endpoint**: `/api/analytics?type=spending_breakdown`

---

### 5. City Other Lobbying Spending

**Display**: `$XX.XX M` (millions of dollars with 2 decimal places and comma formatting)
- Example: `$45.67M` (formatted with commas using `toLocaleString()`)

**Plain English**:
This KPI shows how much money city governments spend on direct lobbying activities outside of membership dues. This includes hiring lobbying firms, contracting individual lobbyists, or having city departments do lobbying work directly. These are targeted lobbying efforts for specific issues or legislation, separate from the collective advocacy provided by membership organizations like the League of California Cities.

**SQL Query**:
```sql
SELECT
    SUM(total_spending) as total_amount
FROM `ca-lobby.ca_lobby.v_organization_summary`
WHERE UPPER(organization_name) LIKE '%CITY%'
AND spending_category = 'other_lobbying'
```

**How to read the query**:
1. Look at the pre-aggregated organization summary view
2. Find organizations with city-related names ("CITY")
3. Filter to non-membership lobbying (organizations NOT containing "LEAGUE", "ASSOCIATION", or "COALITION")
4. Sum up all the spending amounts
5. Display the total in millions of dollars

**Calculation Method**:
```sql
SUM(total_spending) as total_amount
FROM `ca-lobby.ca_lobby.v_organization_summary`
WHERE UPPER(organization_name) LIKE '%CITY%'
AND spending_category = 'other_lobbying'
```

**What it counts**:
- Total spending by city governments on non-membership lobbying activities
- Includes:
  - Direct lobbying services
  - Lobbying firm contracts
  - Individual city department lobbying
- Excludes membership dues (counted separately above)

**Categorization Logic**:
- **Other Lobbying**: Organization name does NOT contain "LEAGUE", "ASSOCIATION", or "COALITION"
- **City**: Organization name contains "CITY"

**Data Source**:
- View: `v_organization_summary`
- Field: `total_spending`

**Frontend Code**: [Dashboard.js:219](../frontend/src/components/Dashboard.js#L219)
**API Endpoint**: `/api/analytics?type=spending_breakdown`

---

### 6. County Membership Spending

**Display**: `$XX.XX M` (millions of dollars with 2 decimal places and comma formatting)
- Example: `$23.45M` (formatted with commas using `toLocaleString()`)

**Plain English**:
This KPI shows how much money county governments spend on membership dues to organizations like the California State Association of Counties (CSAC). These membership organizations provide collective advocacy, training, and resources to counties. Instead of each county hiring their own lobbyists for every issue, they pool resources through memberships. This spending category is separate from direct lobbying services or lobbying firm contracts.

**SQL Query**:
```sql
SELECT
    SUM(total_spending) as total_amount
FROM `ca-lobby.ca_lobby.v_organization_summary`
WHERE (
    UPPER(organization_name) LIKE '%LEAGUE%'
    OR UPPER(organization_name) LIKE '%ASSOCIATION%'
    OR UPPER(organization_name) LIKE '%COALITION%'
    OR UPPER(organization_name) LIKE '%CSAC%'
)
AND UPPER(organization_name) LIKE '%COUNTY%'
AND spending_category = 'membership'
```

**How to read the query**:
1. Look at the pre-aggregated organization summary view (37K rows, much faster than raw data)
2. Find organizations with county-related names ("COUNTY")
3. Filter to membership organizations ("LEAGUE", "ASSOCIATION", "COALITION", "CSAC")
4. Sum up all the spending amounts
5. Display the total in millions of dollars

**Calculation Method**:
```sql
SUM(total_spending) as total_amount
FROM `ca-lobby.ca_lobby.v_organization_summary`
WHERE (
    UPPER(organization_name) LIKE '%LEAGUE%'
    OR UPPER(organization_name) LIKE '%ASSOCIATION%'
    OR UPPER(organization_name) LIKE '%COALITION%'
    OR UPPER(organization_name) LIKE '%CSAC%'
)
AND UPPER(organization_name) LIKE '%COUNTY%'
AND spending_category = 'membership'
```

**What it counts**:
- Total spending by county governments on membership dues
- Primarily captures:
  - California State Association of Counties (CSAC) dues
  - County associations and coalitions
- Uses the pre-aggregated `v_organization_summary` view

**Categorization Logic**:
- **Membership**: Organization name contains "LEAGUE", "ASSOCIATION", "COALITION", or "CSAC"
- **County**: Organization name contains "COUNTY"

**Data Source**:
- View: `v_organization_summary`
- Field: `total_spending`

**Frontend Code**: [Dashboard.js:231](../frontend/src/components/Dashboard.js#L231)
**API Endpoint**: `/api/analytics?type=spending_breakdown`

---

### 7. County Other Lobbying Spending

**Display**: `$XX.XX M` (millions of dollars with 2 decimal places and comma formatting)
- Example: `$67.89M` (formatted with commas using `toLocaleString()`)

**Plain English**:
This KPI shows how much money county governments spend on direct lobbying activities outside of membership dues. This includes hiring lobbying firms, contracting individual lobbyists, or having county departments do lobbying work directly. These are targeted lobbying efforts for specific issues or legislation, separate from the collective advocacy provided by membership organizations like CSAC.

**SQL Query**:
```sql
SELECT
    SUM(total_spending) as total_amount
FROM `ca-lobby.ca_lobby.v_organization_summary`
WHERE UPPER(organization_name) LIKE '%COUNTY%'
AND spending_category = 'other_lobbying'
```

**How to read the query**:
1. Look at the pre-aggregated organization summary view
2. Find organizations with county-related names ("COUNTY")
3. Filter to non-membership lobbying (organizations NOT containing "LEAGUE", "ASSOCIATION", "COALITION", or "CSAC")
4. Sum up all the spending amounts
5. Display the total in millions of dollars

**Calculation Method**:
```sql
SUM(total_spending) as total_amount
FROM `ca-lobby.ca_lobby.v_organization_summary`
WHERE UPPER(organization_name) LIKE '%COUNTY%'
AND spending_category = 'other_lobbying'
```

**What it counts**:
- Total spending by county governments on non-membership lobbying activities
- Includes:
  - Direct lobbying services
  - Lobbying firm contracts
  - Individual county department lobbying
- Excludes membership dues (counted separately above)

**Categorization Logic**:
- **Other Lobbying**: Organization name does NOT contain "LEAGUE", "ASSOCIATION", "COALITION", or "CSAC"
- **County**: Organization name contains "COUNTY"

**Data Source**:
- View: `v_organization_summary`
- Field: `total_spending`

**Frontend Code**: [Dashboard.js:243](../frontend/src/components/Dashboard.js#L243)
**API Endpoint**: `/api/analytics?type=spending_breakdown`

---

## Data Flow Architecture

```
BigQuery Tables
└── cvr_lobby_disclosure_cd (4.3M rows - disclosure forms)
└── lpay_cd (5.6M rows - payment records)
└── v_organization_summary (37K rows - pre-aggregated view)
    ↓
Python API Endpoints (/api/analytics.py)
├── /api/analytics?type=spending → Total, City/County spending and counts
├── /api/analytics?type=spending_breakdown → Membership vs Other Lobbying breakdown
    ↓
React Frontend (Dashboard.js)
├── Fetches data on component mount
├── Calculates KPIs in calculateKPIs() function
├── Formats with toLocaleString() for comma separators
    ↓
User's Browser
└── Displays KPI cards with formatted numbers
```

---

## Performance Optimization

### Why We Use v_organization_summary

**Before (Raw Tables)**:
- Query: JOIN 4.3M + 5.6M rows with GROUP BY
- Performance: 5-8 seconds per query
- Cost: High (scans ~10M rows)

**After (Pre-aggregated View)**:
- Query: SELECT from 37K pre-aggregated rows
- Performance: 100-200ms per query
- Cost: Low (scans 37K rows)
- **Speedup**: ~150x faster

### Caching Strategy
- Frontend fetches data on page load
- No automatic refresh (reduces API calls)
- User can manually refresh by reloading page

---

## Common Questions

### Q: Why is the county count (72) higher than California's 58 counties?

**A**: The KPI counts **organizations/departments**, not unique counties. Large counties like Los Angeles may have multiple departments (Fire, Health, Sheriff, etc.) each filing separately with different FILER_IDs. 72 departments across 58 counties is reasonable.

### Q: Why are city/county counts different for different years?

**A**: Not all cities/counties lobby every year. Some may:
- Only lobby when specific issues arise
- Have budget constraints
- Rely on membership organizations (League of Cities, CSAC) instead of direct lobbying

### Q: Why did city/county counts drop significantly in 2023-2025?

**A**: The data shows a notable drop (e.g., city_count went from 114 in 2022 to 17 in 2023). This could indicate:
- Data collection lag (recent years may not be complete)
- Change in lobbying patterns post-COVID
- Budget cuts reducing direct lobbying
- Shift to membership-based lobbying only

### Q: How accurate is "LIKE '%CITY OF%'" for identifying cities?

**A**: This pattern-matching approach has limitations:
- **Captures**: Most city government entities
- **May miss**: Cities using non-standard naming (e.g., "San Francisco City and County")
- **May include**: Non-government entities with "CITY OF" in the name
- **Recommended**: Review actual FIRM_NAME values in BigQuery for validation

---

## Validation Queries

To verify KPI calculations, run these queries directly in BigQuery:

### Verify City Count for 2025
```sql
SELECT
    COUNT(DISTINCT p.FILER_ID) as city_count,
    ARRAY_AGG(DISTINCT p.FIRM_NAME ORDER BY p.FIRM_NAME LIMIT 10) as sample_names
FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` p
LEFT JOIN `ca-lobby.ca_lobby.lpay_cd` pay ON p.FILING_ID = pay.FILING_ID
WHERE UPPER(p.FIRM_NAME) LIKE '%CITY OF%'
  AND EXTRACT(YEAR FROM p.RPT_DATE_DATE) = 2025
  AND pay.PER_TOTAL IS NOT NULL
  AND CAST(pay.PER_TOTAL AS FLOAT64) > 0
```

### Verify County Count for 2025
```sql
SELECT
    COUNT(DISTINCT p.FILER_ID) as county_count,
    ARRAY_AGG(DISTINCT p.FIRM_NAME ORDER BY p.FIRM_NAME LIMIT 10) as sample_names
FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` p
LEFT JOIN `ca-lobby.ca_lobby.lpay_cd` pay ON p.FILING_ID = pay.FILING_ID
WHERE UPPER(p.FIRM_NAME) LIKE '%COUNTY%'
  AND EXTRACT(YEAR FROM p.RPT_DATE_DATE) = 2025
  AND pay.PER_TOTAL IS NOT NULL
  AND CAST(pay.PER_TOTAL AS FLOAT64) > 0
```

### Verify Total Spending for 2025
```sql
SELECT
    SUM(CAST(pay.PER_TOTAL AS FLOAT64)) as total_spending,
    COUNT(*) as payment_count
FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` p
LEFT JOIN `ca-lobby.ca_lobby.lpay_cd` pay ON p.FILING_ID = pay.FILING_ID
WHERE EXTRACT(YEAR FROM p.RPT_DATE_DATE) = 2025
  AND pay.PER_TOTAL IS NOT NULL
  AND CAST(pay.PER_TOTAL AS FLOAT64) > 0
```

---

## Dashboard Charts

### 8. Lobbying Spending Trends (2015-Present)

**Display**: Line chart with broken Y-axis
**Component**: [SpendingLineChart.js](../frontend/src/components/charts/SpendingLineChart.js)

**Plain English**:
This chart shows how lobbying spending has changed over time from 2015 to the present. It displays three separate trend lines: total spending across all entities (blue line), city government spending (green line), and county government spending (purple line). The chart uses a broken Y-axis technique to show both the very large total spending amounts and the smaller city/county amounts on the same visualization without losing detail.

**SQL Query**:
```sql
WITH yearly_spending AS (
    SELECT
        EXTRACT(YEAR FROM p.RPT_DATE_DATE) as year,
        p.FILER_ID as filer_id,
        CAST(pay.PER_TOTAL AS FLOAT64) as amount,
        CASE
            WHEN UPPER(p.FIRM_NAME) LIKE '%CITY OF%' THEN 'city'
            WHEN UPPER(p.FIRM_NAME) LIKE '%COUNTY%' THEN 'county'
            ELSE 'other'
        END as govt_type
    FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` p
    LEFT JOIN `ca-lobby.ca_lobby.lpay_cd` pay ON p.FILING_ID = pay.FILING_ID
    WHERE p.RPT_DATE_DATE IS NOT NULL
      AND p.RPT_DATE_DATE <= CURRENT_DATE()
      AND EXTRACT(YEAR FROM p.RPT_DATE_DATE) >= 2015
      AND EXTRACT(YEAR FROM p.RPT_DATE_DATE) <= EXTRACT(YEAR FROM CURRENT_DATE())
      AND pay.PER_TOTAL IS NOT NULL
      AND CAST(pay.PER_TOTAL AS FLOAT64) > 0
)
SELECT
    year,
    SUM(amount) as total_spending,
    SUM(CASE WHEN govt_type = 'city' THEN amount ELSE 0 END) as city_spending,
    SUM(CASE WHEN govt_type = 'county' THEN amount ELSE 0 END) as county_spending,
    COUNT(DISTINCT CASE WHEN govt_type = 'city' THEN filer_id END) as city_count,
    COUNT(DISTINCT CASE WHEN govt_type = 'county' THEN filer_id END) as county_count
FROM yearly_spending
GROUP BY year
ORDER BY year ASC
```

**How to read the query**:
1. Create a CTE (Common Table Expression) that gets all payment records with year and government type
2. Filter to years 2015 through current year
3. Categorize each payment as city, county, or other based on firm name
4. Group by year and calculate:
   - Total spending across all entities
   - City spending (sum of payments from city entities)
   - County spending (sum of payments from county entities)
   - Count of unique city entities
   - Count of unique county entities
5. Order results chronologically (earliest to latest year)

**Chart Features**:
- **Broken Y-axis**: Upper segment shows total spending (~$40B-$45B range), lower segment shows city/county spending (~$0-$600M range)
- **Zigzag indicator**: White zigzag pattern indicates where the axis break occurs
- **Color coding**: Blue (total), Green (city), Purple (county)
- **Data points**: Circles mark actual data points on each line
- **Grid lines**: Horizontal lines with dollar value labels for reference

**Data Source**:
- Table: `cvr_lobby_disclosure_cd` (disclosure forms) joined with `lpay_cd` (payments)
- Field: `lpay_cd.PER_TOTAL` (payment amount per period)
- Time range: 2015 to current year

**API Endpoint**: `/api/analytics?type=spending`
**Frontend Component**: [SpendingLineChart.js](../frontend/src/components/charts/SpendingLineChart.js)

---

### 9. Top 10 Organizations by Total Spending

**Display**: Horizontal bar chart
**Component**: [TopOrganizationsChart.js](../frontend/src/components/charts/TopOrganizationsChart.js)

**Plain English**:
This chart shows the 10 organizations that have spent the most money on lobbying activities overall (across all years in the database). Each organization is shown with a horizontal bar representing their total spending, with the organization name and spending amount displayed. This helps identify which entities are the biggest players in California lobbying. Note: The field is called "filing_count" but actually contains total spending amounts due to the way the view was designed.

**SQL Query**:
```sql
SELECT
    CAST(organization_filer_id AS STRING) as filer_id,
    organization_name,
    CAST(ROUND(total_spending) AS INT64) as filing_count
FROM `ca-lobby.ca_lobby.v_organization_summary`
WHERE organization_name IS NOT NULL
  AND total_spending IS NOT NULL
  AND total_spending > 0
ORDER BY total_spending DESC
LIMIT 10
```

**How to read the query**:
1. Query the pre-aggregated `v_organization_summary` view (37K rows)
2. Filter out records with missing organization names or zero spending
3. Select the organization ID, name, and total spending amount
4. Sort by total spending (highest to lowest)
5. Return only the top 10 results

**Important Note**:
- The field is named `filing_count` in the result, but it actually contains `total_spending` values (dollar amounts)
- This is a legacy naming convention from when the query was migrated from counting filings to showing spending
- The view aggregates spending across **all years** (historical total)

**Chart Features**:
- **Horizontal bars**: Each bar's width represents the organization's spending relative to the #1 organization
- **Green color**: Uses #10b981 (emerald-500) for bar fills
- **Numbered list**: Shows ranking (1-10) before each organization name
- **Spending amounts**: Displayed in parentheses with comma formatting
- **Responsive**: Bar widths scale to 100% of the chart width

**Data Source**:
- View: `v_organization_summary` (pre-aggregated from raw lobbying data)
- Field: `total_spending` (cumulative spending across all years)
- Benefits: Much faster than querying raw tables (queries 37K rows instead of millions)

**API Endpoint**: `/api/analytics?type=top_organizations`
**Frontend Component**: [TopOrganizationsChart.js](../frontend/src/components/charts/TopOrganizationsChart.js)

---

### 10. Top 10 Recipients of City Lobbying Money

**Display**: Horizontal bar chart with green color scheme
**Component**: [CityRecipientsChart.js](../frontend/src/components/charts/CityRecipientsChart.js)

**Plain English**:
This chart shows the 10 lobbying firms and consultants that received the most money from city governments in 2025. When cities hire external lobbyists or lobbying firms to represent their interests in Sacramento, those payments are tracked in the CAL-ACCESS database. This chart reveals which lobbying firms are doing the most work for California cities, helping identify the key players in municipal lobbying.

**SQL Query**:
```sql
WITH city_payments AS (
    SELECT
        d.FILING_ID,
        d.RPT_DATE_DATE,
        pay.PAYEE_NAML as recipient_name,
        CAST(pay.PER_TOTAL AS FLOAT64) as amount
    FROM `ca-lobby.ca_lobby.lpay_cd` pay
    JOIN `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` d
        ON pay.FILING_ID = d.FILING_ID
        AND pay.AMEND_ID = d.AMEND_ID
    WHERE pay.PAYEE_NAML IS NOT NULL
      AND pay.PER_TOTAL IS NOT NULL
      AND CAST(pay.PER_TOTAL AS FLOAT64) > 0
      AND d.RPT_DATE_DATE IS NOT NULL
      AND EXTRACT(YEAR FROM d.RPT_DATE_DATE) = 2025
      AND (
        UPPER(pay.EMPLR_NAML) LIKE '%CITY OF%'
        OR UPPER(pay.EMPLR_NAML) LIKE '%LEAGUE%CITIES%'
      )
)
SELECT
    recipient_name,
    CAST(ROUND(SUM(amount)) AS INT64) as total_amount
FROM city_payments
GROUP BY recipient_name
HAVING total_amount > 0
ORDER BY total_amount DESC
LIMIT 10
```

**How to read the query**:
1. Start with the LPAY_CD table which contains payment records
2. Join with CVR_LOBBY_DISCLOSURE_CD to get reporting dates
3. Filter to 2025 payments only
4. Identify city clients using EMPLR_NAML field (employer name):
   - Organizations with "CITY OF" in the name
   - League of California Cities (membership organization)
5. Extract the PAYEE_NAML field (who received the payment)
6. Group by recipient and sum all payments they received
7. Sort by total amount (highest to lowest)
8. Return top 10 recipients

**Key Field Explanation**:
- **EMPLR_NAML**: The city/county that hired the lobbyist (the employer/client)
- **PAYEE_NAML**: The lobbying firm or consultant who received payment
- **PER_TOTAL**: Payment amount for that reporting period

**Important Notes**:
- This tracks the flow of money FROM cities TO lobbying firms
- Uses EMPLR_NAML (not FIRM_NAME) to identify the city client
- Uses PAYEE_NAML (not PAYEE_NAME) to identify the recipient
- Aggregates across all city clients to show total received by each firm
- Limited to 2025 data only (current year filter)

**Chart Features**:
- **Horizontal bars**: Each bar's width represents the recipient's total relative to the #1 recipient
- **Green color scheme**: Uses #10b981 (emerald-500) for bars, #065f46 (emerald-900) for amounts
- **Numbered list**: Shows ranking (1-10) before each recipient name
- **Dollar amounts**: Displayed in millions (e.g., "$12.34M") to the right of each bar
- **Responsive scaling**: Bar widths calculated as percentage of maximum amount

**Data Source**:
- Table: `lpay_cd` (payment records) joined with `cvr_lobby_disclosure_cd` (disclosure metadata)
- Primary field: `PAYEE_NAML` (recipient name - last name field)
- Filter field: `EMPLR_NAML` (employer name - identifies the city client)
- Amount field: `PER_TOTAL` (total payment for period)

**API Endpoint**: `/api/analytics?type=top_city_recipients`
**Frontend Component**: [CityRecipientsChart.js](../frontend/src/components/charts/CityRecipientsChart.js)

**Related Documentation**: See [tracking-city-county-lobbying-payments.md](./tracking-city-county-lobbying-payments.md) for detailed explanation of the LPAY_CD table structure and field naming conventions.

---

### 11. Top 10 Recipients of County Lobbying Money

**Display**: Horizontal bar chart with purple color scheme
**Component**: [CountyRecipientsChart.js](../frontend/src/components/charts/CountyRecipientsChart.js)

**Plain English**:
This chart shows the 10 lobbying firms and consultants that received the most money from county governments in 2025. When counties hire external lobbyists or lobbying firms to represent their interests in Sacramento, those payments are tracked in the CAL-ACCESS database. This chart reveals which lobbying firms are doing the most work for California counties, helping identify the key players in county-level lobbying.

**SQL Query**:
```sql
WITH county_payments AS (
    SELECT
        d.FILING_ID,
        d.RPT_DATE_DATE,
        pay.PAYEE_NAML as recipient_name,
        CAST(pay.PER_TOTAL AS FLOAT64) as amount
    FROM `ca-lobby.ca_lobby.lpay_cd` pay
    JOIN `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` d
        ON pay.FILING_ID = d.FILING_ID
        AND pay.AMEND_ID = d.AMEND_ID
    WHERE pay.PAYEE_NAML IS NOT NULL
      AND pay.PER_TOTAL IS NOT NULL
      AND CAST(pay.PER_TOTAL AS FLOAT64) > 0
      AND d.RPT_DATE_DATE IS NOT NULL
      AND EXTRACT(YEAR FROM d.RPT_DATE_DATE) = 2025
      AND (
        UPPER(pay.EMPLR_NAML) LIKE '%COUNTY%'
        OR UPPER(pay.EMPLR_NAML) LIKE '%CSAC%'
        OR UPPER(pay.EMPLR_NAML) LIKE '%ASSOCIATION OF COUNTIES%'
      )
)
SELECT
    recipient_name,
    CAST(ROUND(SUM(amount)) AS INT64) as total_amount
FROM county_payments
GROUP BY recipient_name
HAVING total_amount > 0
ORDER BY total_amount DESC
LIMIT 10
```

**How to read the query**:
1. Start with the LPAY_CD table which contains payment records
2. Join with CVR_LOBBY_DISCLOSURE_CD to get reporting dates
3. Filter to 2025 payments only
4. Identify county clients using EMPLR_NAML field (employer name):
   - Organizations with "COUNTY" in the name
   - CSAC (California State Association of Counties)
   - Other county associations
5. Extract the PAYEE_NAML field (who received the payment)
6. Group by recipient and sum all payments they received
7. Sort by total amount (highest to lowest)
8. Return top 10 recipients

**Key Field Explanation**:
- **EMPLR_NAML**: The county that hired the lobbyist (the employer/client)
- **PAYEE_NAML**: The lobbying firm or consultant who received payment
- **PER_TOTAL**: Payment amount for that reporting period

**Important Notes**:
- This tracks the flow of money FROM counties TO lobbying firms
- Uses EMPLR_NAML (not FIRM_NAME) to identify the county client
- Uses PAYEE_NAML (not PAYEE_NAME) to identify the recipient
- Aggregates across all county clients to show total received by each firm
- Includes CSAC (California State Association of Counties) payments
- Limited to 2025 data only (current year filter)

**Chart Features**:
- **Horizontal bars**: Each bar's width represents the recipient's total relative to the #1 recipient
- **Purple color scheme**: Uses #8b5cf6 (violet-500) for bars, #6b21a8 (violet-800) for amounts
- **Numbered list**: Shows ranking (1-10) before each recipient name
- **Dollar amounts**: Displayed in millions (e.g., "$23.45M") to the right of each bar
- **Responsive scaling**: Bar widths calculated as percentage of maximum amount

**Data Source**:
- Table: `lpay_cd` (payment records) joined with `cvr_lobby_disclosure_cd` (disclosure metadata)
- Primary field: `PAYEE_NAML` (recipient name - last name field)
- Filter field: `EMPLR_NAML` (employer name - identifies the county client)
- Amount field: `PER_TOTAL` (total payment for period)

**API Endpoint**: `/api/analytics?type=top_county_recipients`
**Frontend Component**: [CountyRecipientsChart.js](../frontend/src/components/charts/CountyRecipientsChart.js)

**Related Documentation**: See [tracking-city-county-lobbying-payments.md](./tracking-city-county-lobbying-payments.md) for detailed explanation of the LPAY_CD table structure and field naming conventions.

---

## Understanding LPAY_CD Payment Records

The recipient charts above use the **LPAY_CD** table, which has a specific structure for tracking payments:

### Field Naming Convention

CAL-ACCESS uses abbreviated field suffixes:
- `_NAML` = Name Last (for both individuals and organizations)
- `_NAMF` = Name First (for individuals)
- `_AMT` = Amount
- `_CD` = Code/Table designation

### Who Pays Whom

In the LPAY_CD table:
- **EMPLR_NAML** = The organization/city/county that is PAYING for lobbying services (the client/employer)
- **PAYEE_NAML** = The lobbying firm or individual who is RECEIVING the payment
- **PER_TOTAL** = The payment amount for that period

**Example**:
If the City of Sacramento pays Governmental Advocates $75,000:
- EMPLR_NAML = "CITY OF SACRAMENTO" (who paid)
- PAYEE_NAML = "GOVERNMENTAL ADVOCATES" (who got paid)
- PER_TOTAL = 75000.00

### Common Mistakes to Avoid

❌ **Don't use FIRM_NAME from CVR_LOBBY_DISCLOSURE_CD** - This is who filed the form, not necessarily who paid or who got paid

❌ **Don't look for PAYEE_NAME** - The field is called PAYEE_NAML (name last), not PAYEE_NAME

❌ **Don't use LEMP_CD for payment amounts** - That table tracks employer-lobbyist relationships, not actual payment amounts

✅ **Do use EMPLR_NAML to find the client** (city/county)

✅ **Do use PAYEE_NAML to find the recipient** (lobbying firm)

✅ **Do join to CVR_LOBBY_DISCLOSURE_CD for reporting dates**

---

## Related Files

- **Frontend Dashboard**: [frontend/src/components/Dashboard.js](../frontend/src/components/Dashboard.js)
- **Analytics API**: [api/analytics.py](../api/analytics.py)
- **API Configuration**: [frontend/src/config/api.js](../frontend/src/config/api.js)
- **Spending Line Chart**: [frontend/src/components/charts/SpendingLineChart.js](../frontend/src/components/charts/SpendingLineChart.js)
- **Top Organizations Chart**: [frontend/src/components/charts/TopOrganizationsChart.js](../frontend/src/components/charts/TopOrganizationsChart.js)
- **City Recipients Chart**: [frontend/src/components/charts/CityRecipientsChart.js](../frontend/src/components/charts/CityRecipientsChart.js)
- **County Recipients Chart**: [frontend/src/components/charts/CountyRecipientsChart.js](../frontend/src/components/charts/CountyRecipientsChart.js)
- **Payment Tracking Guide**: [Documents/tracking-city-county-lobbying-payments.md](./tracking-city-county-lobbying-payments.md)

---

## Changelog

### 2025-11-20 (Update 2)
- **Added recipient chart documentation**
- Documented Top 10 Recipients of City Lobbying Money chart (#10)
- Documented Top 10 Recipients of County Lobbying Money chart (#11)
- Added comprehensive section on Understanding LPAY_CD Payment Records
- Explained EMPLR_NAML vs PAYEE_NAML field usage
- Added common mistakes to avoid when querying payment data
- Cross-referenced tracking-city-county-lobbying-payments.md guide

### 2025-11-20 (Update 1)
- **Added chart documentation**
- Documented Lobbying Spending Trends (2015-Present) chart
- Documented Top 10 Organizations by Total Spending chart
- Clarified that "filing_count" in top organizations actually contains spending amounts

### 2025-11-19
- **Initial documentation created**
- Added detailed explanations for all 7 KPIs
- Clarified that city/county counts represent organizations/departments, not unique cities/counties
- Added validation queries
- Documented performance optimization strategy

---

**Maintained by**: Development Team
**Questions**: See session archives or create GitHub issue
