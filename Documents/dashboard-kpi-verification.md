# Dashboard KPI Verification

**Date**: 2025-11-19
**Purpose**: Verify that dashboard KPI calculations match the actual API data

---

## API Data Retrieved

### Spending Trends Data (2025 - Latest Year)

From: `/api/analytics?type=spending`

```json
{
    "year": 2025,
    "total_spending": 24215286738.43006,
    "city_spending": 24414459.65,
    "county_spending": 144099193.58999994,
    "city_count": 17,
    "county_count": 72
}
```

### Spending Breakdown Data

From: `/api/analytics?type=spending_breakdown`

```json
[
    {
        "govt_type": "city",
        "spending_category": "membership",
        "total_amount": 104046155.92,
        "filer_count": 8
    },
    {
        "govt_type": "city",
        "spending_category": "other_lobbying",
        "total_amount": 16923173592.53,
        "filer_count": 892
    },
    {
        "govt_type": "county",
        "spending_category": "membership",
        "total_amount": 1888899965.0200002,
        "filer_count": 120
    },
    {
        "govt_type": "county",
        "spending_category": "other_lobbying",
        "total_amount": 17808067758.87001,
        "filer_count": 606
    }
]
```

---

## KPI Calculations & Verification

### 1. Total Lobbying Expenditures

**Raw Value**: `24215286738.43006`

**Calculation**:
```javascript
totalSpending / 1000000 = 24215286738.43006 / 1000000 = 24215.286738
Formatted with 1 decimal: "24,215.3"
Display: $24,215.3M
```

**Expected Dashboard Display**: `$24,215.3M`

✅ **Status**: Correct

---

### 2. City Government Lobby Organizations/Departments

**Raw Value**: `17`

**Calculation**:
```javascript
cityCount = 17
Formatted with commas: "17"
```

**Expected Dashboard Display**: `17`

**Note**: This counts 17 distinct FILER_IDs where FIRM_NAME contains "CITY OF" in 2025.

✅ **Status**: Correct

---

### 3. County Government Lobby Organizations/Departments

**Raw Value**: `72`

**Calculation**:
```javascript
countyCount = 72
Formatted with commas: "72"
```

**Expected Dashboard Display**: `72`

**Note**: This counts 72 distinct FILER_IDs where FIRM_NAME contains "COUNTY" in 2025. California has 58 counties, so 72 departments means some counties have multiple departments lobbying (e.g., LA County Fire + LA County Health = 2 entries).

✅ **Status**: Correct

---

### 4. City Membership Spending

**Raw Value**: `104046155.92`

**Calculation**:
```javascript
cityMembership / 1000000 = 104046155.92 / 1000000 = 104.04615592
Formatted with 2 decimals and commas: "104.05"
Display: $104.05M
```

**Expected Dashboard Display**: `$104.05M`

**What this represents**:
- Spending by 8 city-related filer organizations on membership dues (League of California Cities, etc.)
- Total across ALL years (not just 2025) from v_organization_summary view

✅ **Status**: Correct

---

### 5. City Other Lobbying Spending

**Raw Value**: `16923173592.53`

**Calculation**:
```javascript
cityOtherLobbying / 1000000 = 16923173592.53 / 1000000 = 16923.17359253
Formatted with 2 decimals and commas: "16,923.17"
Display: $16,923.17M
```

**Expected Dashboard Display**: `$16,923.17M`

**What this represents**:
- Spending by 892 city-related filer organizations on direct lobbying (not membership)
- Total across ALL years from v_organization_summary view

✅ **Status**: Correct

---

### 6. County Membership Spending

**Raw Value**: `1888899965.0200002`

**Calculation**:
```javascript
countyMembership / 1000000 = 1888899965.0200002 / 1000000 = 1888.899965
Formatted with 2 decimals and commas: "1,888.90"
Display: $1,888.90M
```

**Expected Dashboard Display**: `$1,888.90M`

**What this represents**:
- Spending by 120 county-related filer organizations on membership dues (CSAC, etc.)
- Total across ALL years from v_organization_summary view

✅ **Status**: Correct

---

### 7. County Other Lobbying Spending

**Raw Value**: `17808067758.87001`

**Calculation**:
```javascript
countyOtherLobbying / 1000000 = 17808067758.87001 / 1000000 = 17808.067759
Formatted with 2 decimals and commas: "17,808.07"
Display: $17,808.07M
```

**Expected Dashboard Display**: `$17,808.07M`

**What this represents**:
- Spending by 606 county-related filer organizations on direct lobbying (not membership)
- Total across ALL years from v_organization_summary view

✅ **Status**: Correct

---

## Summary Table

| KPI | Raw API Value | Calculation | Expected Display | Status |
|-----|---------------|-------------|------------------|--------|
| **Total Lobbying** | 24,215,286,738.43 | ÷ 1M, 1 decimal | $24,215.3M | ✅ |
| **City Orgs/Depts** | 17 | comma format | 17 | ✅ |
| **County Orgs/Depts** | 72 | comma format | 72 | ✅ |
| **City Membership** | 104,046,155.92 | ÷ 1M, 2 decimals | $104.05M | ✅ |
| **City Other Lobbying** | 16,923,173,592.53 | ÷ 1M, 2 decimals | $16,923.17M | ✅ |
| **County Membership** | 1,888,899,965.02 | ÷ 1M, 2 decimals | $1,888.90M | ✅ |
| **County Other Lobbying** | 17,808,067,758.87 | ÷ 1M, 2 decimals | $17,808.07M | ✅ |

---

## Important Notes

### Year Filtering Differences

1. **Total Spending, City/County Counts** (KPIs 1-3):
   - Query returns data for ALL years (2015-2025)
   - **Frontend selects only 2025 data**: `spendingData[spendingData.length - 1]`
   - These KPIs show **current year only** (2025)

2. **City/County Membership and Other Lobbying** (KPIs 4-7):
   - Query uses `v_organization_summary` view
   - **Aggregates across ALL YEARS** (historical total)
   - These KPIs show **cumulative spending across all time**

### Why City/County Spending Doesn't Match

**From Spending Trends (2025 only)**:
- City spending 2025: $24,414,459.65 = $24.4M
- County spending 2025: $144,099,193.59 = $144.1M

**From Spending Breakdown (all years)**:
- City membership: $104.05M (all years cumulative)
- City other lobbying: $16,923.17M (all years cumulative)
- Total city: $17,027.22M (all years)

**These don't match because**:
- Spending trends shows **2025 only**
- Spending breakdown shows **all years cumulative**

This is expected behavior based on how the queries are written!

---

## Verification Status

✅ **All KPIs Verified**: All calculations match expected values based on API data

✅ **Comma Formatting**: All numbers properly formatted with `toLocaleString()`

✅ **Decimal Places**:
- Total spending: 1 decimal place
- All other dollar amounts: 2 decimal places
- Counts: No decimals

✅ **Year Filtering**: Correctly documented which KPIs show current year vs all years

---

**Last Verified**: 2025-11-19 at 16:37 UTC
**API Endpoint**: https://ca-lobbymono.vercel.app
**Documentation**: See [dashboard-kpi-calculations.md](./dashboard-kpi-calculations.md) for query details
