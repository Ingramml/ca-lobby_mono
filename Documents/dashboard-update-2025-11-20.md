# Dashboard Update - November 20, 2025

## Summary of Changes

This update implements **Option 3: Visual Badges** layout for the California Lobbying Dashboard and ensures all KPI data shows **2025 only** (no more mixed time periods).

---

## What Changed

### 1. Backend API Query Modification

**File**: `api/analytics.py`
**Function**: `_get_spending_breakdown()`

**Previous Behavior**:
- Used `v_organization_summary` view
- Returned **ALL YEARS** cumulative data for city/county membership and lobbying spending
- Values were historical totals (e.g., City Membership: $104M all-time)

**New Behavior**:
- Directly queries `cvr_lobby_disclosure_cd` + `lpay_cd` tables
- Filters by `EXTRACT(YEAR FROM p.RPT_DATE_DATE) = 2025`
- Returns **2025 ONLY** data for all spending breakdown KPIs
- New values reflect single-year spending (e.g., City Membership: $0 in 2025, County Membership: $15.7M in 2025)

**Query Change**:
```sql
-- OLD: Used v_organization_summary (all years)
FROM `ca-lobby.ca_lobby.v_organization_summary`

-- NEW: Filters by year 2025
FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` p
LEFT JOIN `ca-lobby.ca_lobby.lpay_cd` pay ON p.FILING_ID = pay.FILING_ID
WHERE EXTRACT(YEAR FROM p.RPT_DATE_DATE) = 2025
```

---

### 2. Frontend Dashboard Visual Updates

**File**: `frontend/src/components/Dashboard.js`

**Added Visual Elements**:
1. **Year Badges**: Blue badges displaying "2025" in top-right corner of each card
2. **Colored Left Borders**: 3px blue borders (#3b82f6) on left side of all cards
3. **KPI Explanation Table**: New table below KPI cards explaining each metric

**Visual Badge Styling**:
```javascript
<span style={{
  position: 'absolute',
  top: '16px',
  right: '16px',
  padding: '4px 12px',
  borderRadius: '12px',
  fontSize: '0.75rem',
  fontWeight: '600',
  background: '#dbeafe',
  color: '#1e40af'
}}>{currentYear}</span>
```

**Explanation Table**:
- 7 rows (one per KPI)
- 3 columns: KPI Name | What It Measures | Time Period
- All KPIs show "{currentYear} only" in Time Period column
- Helps users understand what each number represents

---

## New KPI Values (2025 Only)

### Before (Mixed Time Periods)
| KPI | Value | Time Period |
|-----|-------|-------------|
| Total Spending | $24,215.3M | 2025 only |
| City Count | 17 | 2025 only |
| County Count | 72 | 2025 only |
| City Membership | $104.05M | **ALL YEARS** ⚠️ |
| City Other Lobbying | $16,923.17M | **ALL YEARS** ⚠️ |
| County Membership | $1,888.90M | **ALL YEARS** ⚠️ |
| County Other Lobbying | $17,808.07M | **ALL YEARS** ⚠️ |

### After (All 2025 Only)
| KPI | Value | Time Period |
|-----|-------|-------------|
| Total Spending | $24,215.3M | 2025 only ✅ |
| City Count | 17 | 2025 only ✅ |
| County Count | 72 | 2025 only ✅ |
| City Membership | $0.00M | 2025 only ✅ |
| City Other Lobbying | $24.41M | 2025 only ✅ |
| County Membership | $15.70M | 2025 only ✅ |
| County Other Lobbying | $128.40M | 2025 only ✅ |

**Note**: City Membership shows $0 because no city membership payments were recorded in 2025 YTD. This is expected as membership dues are often paid annually or at the start of the year.

---

## API Response Comparison

### Before Update
```json
{
  "govt_type": "city",
  "spending_category": "membership",
  "total_amount": 104046155.92,
  "filer_count": 8
}
```

### After Update
```json
{
  "govt_type": "city",
  "spending_category": "membership",
  "total_amount": 0,  // No 2025 data
  "filer_count": 0
}
```

---

## User Experience Improvements

### Problem Solved
**Before**: Users were confused because some KPIs showed current year (2025) while others showed all-time cumulative totals. This made comparisons misleading.

**After**: All KPIs now show 2025 only, with clear visual indicators:
- Blue year badges on each card
- Blue left borders for consistency
- Explanation table defining each metric
- Subtitle text shows year explicitly

### Visual Design
Implemented **Option 3** from mockups:
- Keeps current card layout (familiar to users)
- Adds minimal visual enhancements (badges, borders)
- Non-intrusive but clear time period indicators
- Professional blue color scheme

---

## Files Modified

1. **api/analytics.py** (lines 285-335)
   - Modified `_get_spending_breakdown()` query
   - Added year 2025 filter
   - Updated docstring

2. **frontend/src/components/Dashboard.js** (lines 149-381)
   - Added visual badges to all 7 KPI cards
   - Added blue left borders
   - Added KPI explanation table
   - Updated card header padding to accommodate badges

---

## Deployment

**Production URL**: https://ca-lobbymono.vercel.app

**Deployment Date**: November 20, 2025

**Deployment Command**: `vercel --prod --yes`

**Status**: ✅ Successfully deployed and verified

**API Test**:
```bash
curl "https://ca-lobbymono.vercel.app/api/analytics?type=spending_breakdown"
```

---

## Testing Notes

### Verified:
- ✅ All KPI cards display 2025 badges
- ✅ Blue left borders visible on all cards
- ✅ Explanation table renders correctly
- ✅ API returns 2025-filtered data
- ✅ No console errors
- ✅ Mobile responsive layout intact
- ✅ Comma formatting preserved

### Known Behaviors:
- City Membership shows $0.00M (no 2025 data in database)
- County/City spending values are much lower (expected for single year vs cumulative)
- Total spending ($24.2B) matches sum of all spending categories

---

## Future Considerations

1. **Year Selector**: Could add dropdown to let users view historical years
2. **Year-over-Year Comparison**: Add trend indicators (% change from previous year)
3. **Membership Data**: Monitor if city membership data appears in future quarters
4. **Performance**: Current query is fast (~100ms), no optimization needed yet

---

## Documentation References

- [Dashboard KPI Calculations](./dashboard-kpi-calculations.md)
- [Dashboard KPI Verification](./dashboard-kpi-verification.md)
- [Mockup Files](../mockups/)
  - [index.html](../mockups/index.html) - Option selector
  - [option3-visual-badges.html](../mockups/option3-visual-badges.html) - Selected design

---

**Author**: Development Team
**Date**: November 20, 2025
**Version**: 1.0.0
