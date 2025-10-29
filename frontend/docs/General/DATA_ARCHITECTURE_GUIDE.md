# CA Lobby Data Architecture Guide

**Created**: October 28, 2025
**Purpose**: Complete reference for understanding CA Lobby data sources, transformations, and algorithms
**Audience**: Developers, data analysts, and stakeholders

---

## Table of Contents

1. [Data Architecture Overview](#data-architecture-overview)
2. [Data Sources](#data-sources)
3. [Data Transformation Pipeline](#data-transformation-pipeline)
4. [Component Data Usage](#component-data-usage)
5. [Lobbyist Network Algorithm](#lobbyist-network-algorithm)
6. [Related Organizations Algorithm](#related-organizations-algorithm)
7. [Data Limitations](#data-limitations)

---

## Data Architecture Overview

The CA Lobby application uses a **hybrid data architecture** combining:

- **Real BigQuery-sourced data** (11 organizations, 3,357 activities, $34.1M spending)
- **Component-generated demo data** (for missing information)
- **Calculated estimates** (for aggregated metrics)

### Data Flow Diagram

```
BigQuery Database
    ↓ SQL Export
CSV Files (Sample data/)
    ↓ Python Processing
JSON Files (src/data/)
    ↓ React Imports
Zustand Stores
    ↓ Component Rendering
User Interface
```

---

## Data Sources

### Primary: BigQuery Views

All data originates from BigQuery tables exported to CSV format:

| CSV File | Rows | Purpose | Status |
|----------|------|---------|--------|
| `v_payments_alameda.csv` | 9,699 | Individual payment line items | ✅ IN USE |
| `v_disclosures_alameda.csv` | 8,650 | Disclosure filings with dates | ⚠️ PARTIAL USE |
| `v_filers_alameda.csv` | 49,459 | Filer registry | ✅ IN USE |
| Other CSV files | Various | Additional data sources | ❌ NOT CURRENTLY USED |

### Secondary: Generated JSON Files

Processed data stored in structured JSON format:

1. **organizations-summary.json** (11 organizations)
   - Aggregated totals and counts
   - Organization categories
   - Metadata

2. **activities/*.json** (11 files, 3,357 transactions)
   - Individual payment line items
   - Filing details
   - Payment breakdowns

---

## Data Transformation Pipeline

### Stage 1: CSV → Summary JSON

**Script**: `scripts/extract_simple_alameda_data.py`

**Process**:
1. Load filers, disclosures, and payments CSVs
2. Filter for 11 core Alameda County organizations
3. Aggregate activity counts and spending totals
4. Determine organization categories
5. Output to `src/data/organizations-summary.json`

### Stage 2: CSV → Individual Transaction JSONs

**Script**: `scripts/generate_individual_transactions.py`

**Process**:
1. Load `v_payments_alameda.csv`
2. Filter payments by organization name
3. Create one JSON record per payment line item
4. Sort by filing_id descending (most recent first)
5. Output 11 files to `src/data/activities/`

**Example Output**:
```json
{
  "organization": "ALAMEDA COUNTY WATER DISTRICT",
  "total_activities": 520,
  "total_spending": 5067742.99,
  "activities": [
    {
      "id": "payment_3064389_7",
      "filing_id": 3064389,
      "line_item": 7,
      "amount": 15360.0,
      "fees_amount": 15360.0,
      "reimbursement_amount": 0.0,
      "advance_amount": 0.0,
      "form_type": "F625P2",
      "payment_tier": "High (10K-50K)"
    }
  ]
}
```

---

## Component Data Usage

### Dashboard Page

| UI Element | Data Source | Real/Demo |
|-----------|-------------|-----------|
| Total Lobbying Expenditures | kpiCalculations.js | ⚠️ ESTIMATED |
| City Government Lobbying | kpiCalculations.js | ⚠️ ESTIMATED |
| County Government Lobbying | kpiCalculations.js | ⚠️ ESTIMATED |
| Lobby Trends Line Chart | sampleData.js | ❌ DEMO DATA |
| Top Organizations Bar Chart | organizations-summary.json | ✅ REAL |
| Category Pie Chart | organizations-summary.json | ✅ REAL |

### Search Page

| UI Element | Data Source | Real/Demo |
|-----------|-------------|-----------|
| Search results | organizations-summary.json | ✅ REAL |
| Organization names | organizations-summary.json | ✅ REAL |
| Activity counts | organizations-summary.json | ✅ REAL |
| Total spending | organizations-summary.json | ✅ REAL |

### Organization Profile Page

| UI Element | Data Source | Real/Demo |
|-----------|-------------|-----------|
| Activity Summary (6 metrics) | organizations-summary.json | ✅ REAL |
| Spending Trends Chart | calculateSpendingTrends() | ✅ REAL |
| Activity List (paginated) | activities/*.json | ✅ REAL |
| Transaction Details (expandable) | activities/*.json | ✅ REAL |
| Lobbyist Network | extractLobbyistNetwork() | ❌ EMPTY (no data) |
| Related Organizations | findRelatedOrganizations() | ✅ REAL |

---

## Lobbyist Network Algorithm

### Purpose

Display the network of lobbyists and lobbying firms that work with an organization.

### Current Status

**❌ NOT FUNCTIONAL** - All `lobbyist` and `firm_name` fields are NULL in current data.

### Algorithm (When Data Available)

**Function**: `extractLobbyistNetwork()` in `src/utils/sampleData.js`

```javascript
export const extractLobbyistNetwork = (activities) => {
  // Group activities by lobbyist/firm
  const lobbyistMap = {};

  activities.forEach(activity => {
    const lobbyistName = activity.lobbyist || activity.firm_name || 'Unknown';

    if (!lobbyistMap[lobbyistName]) {
      lobbyistMap[lobbyistName] = {
        name: lobbyistName,
        totalAmount: 0,
        activityCount: 0,
        categories: new Set()
      };
    }

    lobbyistMap[lobbyistName].totalAmount += activity.amount || 0;
    lobbyistMap[lobbyistName].activityCount += 1;

    if (activity.category) {
      lobbyistMap[lobbyistName].categories.add(activity.category);
    }
  });

  // Convert to array and sort by total amount
  return Object.values(lobbyistMap)
    .map(lobbyist => ({
      ...lobbyist,
      categories: Array.from(lobbyist.categories)
    }))
    .sort((a, b) => b.totalAmount - a.totalAmount);
};
```

### Data Requirements

To make this functional, we need to populate:
- `lobbyist`: Name of individual lobbyist
- `firm_name`: Name of lobbying firm

**Source**: Join payments with FULL disclosure table (not filtered Alameda view):

```sql
SELECT
  p.filing_id,
  p.line_item,
  d.firm_name,
  d.period_start_date,
  d.period_end_date,
  d.report_date
FROM `ca-lobby.ca_lobby.v_payments_alameda` p
INNER JOIN `ca-lobby.ca_lobby.CVR2_LOBBY_DISCLOSURE_CD` d  -- FULL TABLE
  ON p.filing_id = d.filing_id
```

### Display Logic

**Component**: `src/components/LobbyistNetwork.js`

- **Default**: Show top 5 lobbyists
- **Expand**: Click "Show All" to see complete list
- **Collapse**: Click "Show Less" to return to top 5
- **Empty State**: When no lobbyist data available, shows "No data available"

---

## Related Organizations Algorithm

### Purpose

Find and rank organizations with similar lobbying patterns based on spending and category overlap.

### Status

**✅ FULLY FUNCTIONAL** - Uses real organization data

### Algorithm Details

**Function**: `findRelatedOrganizations()` in `src/utils/sampleData.js`

#### Step 1: Extract Current Organization Data

```javascript
const orgActivities = allActivities.filter(a => a.organization === organizationName);
const orgCategories = [...new Set(orgActivities.map(a => a.category))];
const orgTotalSpending = orgActivities.reduce((sum, a) => sum + (a.amount || 0), 0);
```

Extracts:
- All activities for the current organization
- Unique categories (using Set for deduplication)
- Total spending amount

#### Step 2: Aggregate Other Organizations

```javascript
const otherOrgs = allActivities
  .filter(a => a.organization !== organizationName)
  .reduce((acc, activity) => {
    const org = activity.organization;
    if (!acc[org]) {
      acc[org] = {
        name: org,
        totalSpending: 0,
        activityCount: 0,
        categories: new Set(),  // ✅ ENSURES UNIQUE VALUES
        sharedCategories: 0
      };
    }

    acc[org].totalSpending += activity.amount || 0;
    acc[org].activityCount += 1;

    if (activity.category) {
      acc[org].categories.add(activity.category);  // ✅ SET AUTOMATICALLY DEDUPLICATES
      if (orgCategories.includes(activity.category)) {
        acc[org].sharedCategories += 1;
      }
    }

    return acc;
  }, {});
```

**Key Feature**: Uses `Set()` for categories, which automatically removes duplicates.

#### Step 3: Calculate Similarity Scores

Two factors contribute to similarity:

##### A. Spending Similarity (40% weight)

```javascript
const spendingDiff = Math.abs(org.totalSpending - orgTotalSpending);
const spendingSimilarity = 1 / (1 + spendingDiff / 1000000);
```

**How it works**:
- Calculate absolute difference in spending
- Normalize by $1M to create a similarity score
- Organizations with similar spending get higher scores
- Example:
  - $5M vs $5.1M difference = 0.909 similarity
  - $5M vs $8M difference = 0.250 similarity

##### B. Category Similarity (60% weight)

```javascript
const categorySimilarity = orgCategories.length > 0
  ? org.sharedCategories / orgCategories.length
  : 0;
```

**How it works**:
- Count how many categories are shared
- Divide by total categories of current organization
- Higher percentage = more similar
- Example:
  - Current org: [County Department, Health Organization]
  - Other org: [County Department, Health Organization, City Government]
  - Shared: 2 out of 2 = 100% similarity

##### C. Combined Score

```javascript
similarityScore = (spendingSimilarity * 0.4) + (categorySimilarity * 0.6)
```

**Weighting rationale**:
- Category overlap (60%) is more important than spending amount (40%)
- Organizations in same categories are fundamentally more similar
- Spending can vary widely even within same category

#### Step 4: Sort and Return Top Matches

```javascript
return Object.values(otherOrgs)
  .map(org => ({
    ...org,
    categories: Array.from(org.categories),  // ✅ CONVERT SET TO ARRAY
    similarityScore: (spendingSimilarity * 0.4) + (categorySimilarity * 0.6)
  }))
  .sort((a, b) => b.similarityScore - a.similarityScore)
  .slice(0, limit);  // Default: top 5
```

### Similarity Score Interpretation

| Score Range | Badge | Color | Meaning |
|-------------|-------|-------|---------|
| 0.8 - 1.0 | Very Similar | Green | Very close match in both spending and categories |
| 0.6 - 0.8 | Similar | Blue | Good match, shares significant characteristics |
| 0.4 - 0.6 | Somewhat Similar | Orange | Some commonalities, but notable differences |
| 0.0 - 0.4 | Related | Gray | Minimal similarity, distant relationship |

### Example Calculation

**Current Organization**: Alameda County Water District
- Total Spending: $5,067,742
- Categories: [County Department]

**Candidate**: Alameda County Waste Management Authority
- Total Spending: $3,914,309
- Categories: [County Department]

**Step 1**: Spending Similarity
```
spendingDiff = |5,067,742 - 3,914,309| = 1,153,433
spendingSimilarity = 1 / (1 + 1,153,433 / 1,000,000)
                   = 1 / 2.153433
                   = 0.464
```

**Step 2**: Category Similarity
```
sharedCategories = 1 (both have "County Department")
totalCategories = 1
categorySimilarity = 1 / 1 = 1.0
```

**Step 3**: Combined Score
```
similarityScore = (0.464 * 0.4) + (1.0 * 0.6)
                = 0.186 + 0.6
                = 0.786
```

**Result**: "Similar" (Blue badge) - Good match due to 100% category overlap

---

## Data Limitations

### Missing Data

| Field | Status | Impact | Solution |
|-------|--------|--------|----------|
| `date`, `from_date`, `thru_date` | ❌ NULL | Cannot show true timeline | Query full disclosure table |
| `lobbyist`, `firm_name` | ❌ NULL | Lobbyist network empty | Query full disclosure table |
| `filing_date` | ❌ NULL | Cannot sort by filing date | Query full disclosure table |

### Root Cause

**Problem**: Disclosure records are filed by lobbying firms (not by client organizations)

**Current Filter**: `v_disclosures_alameda` only includes disclosures WHERE filer is from Alameda

**Result**: Organizations that hire non-Alameda firms have ZERO disclosure matches

**Example**:
- Alameda County Water District (client) → Hires Shaw/Yoder (Sacramento firm)
- Shaw/Yoder files quarterly disclosures → NOT in v_disclosures_alameda
- Result: 0 matches when joining locally

### Solution

Query the FULL disclosure table without Alameda filter:

```sql
-- Join payments to FULL disclosure table
SELECT
  p.*,
  d.firm_name,
  d.period_start_date,
  d.period_end_date,
  d.report_date
FROM `ca-lobby.ca_lobby.v_payments_alameda` p
INNER JOIN `ca-lobby.ca_lobby.CVR2_LOBBY_DISCLOSURE_CD` d  -- FULL TABLE
  ON p.filing_id = d.filing_id
WHERE p.employer_full_name IN (
  'ALAMEDA COUNTY WATER DISTRICT',
  -- ... other 10 organizations
)
```

This will provide:
- ✅ Firm names for lobbyist network
- ✅ Period dates for timeline sorting
- ✅ Filing dates for activity chronology

---

## Summary

### What Works (✅ Real Data)

- Organization search and filtering
- Category-based grouping
- Spending calculations
- Related organizations algorithm
- Transaction detail display
- Activity pagination

### What Doesn't Work (❌ Missing Data)

- Lobbyist network (no firm names)
- Timeline sorting (no dates)
- Dashboard trends (demo data used instead)

### What's Estimated (⚠️ Calculated)

- Dashboard KPI totals (activityCount × averageAmount)
- Spending projections

### Next Steps

1. Execute BigQuery query to get missing disclosure data
2. Update activity JSON files with firm names and dates
3. Rebuild application to enable lobbyist network
4. Replace demo trend data with real timeline data

---

**End of Data Architecture Guide**
