# Dashboard KPI Redesign Plan

**Project:** CA Lobby Search System
**Phase:** 2h - Dashboard KPI Metrics
**Created:** October 24, 2025
**Status:** Planning

## Executive Summary

Redesign the Dashboard page to display 3 key performance indicators (KPIs) focused on California lobbying expenditures:
1. Total amount spent on lobbying for current year
2. Total amount spent on lobbying by all city governments
3. Total amount spent on lobbying by all county governments

~~This replaces the current system status cards with meaningful financial metrics that provide immediate insight into California lobbying activity.~~
These Three KPI are above CA Lobby Data Insights

## Current State

### Current Dashboard Layout
- **System Status Cards:**
  - API Health Check
  - System Status
  - Cache Performance
  - Recent Search Activity
  - User Stats

- **Charts:**
  - Lobby Trends Chart (line chart over time)
  - Organization Chart (bar chart - top 8 organizations)
  - Category Chart (category distribution)

### Issues with Current Design
- ❌ System status is developer-focused, not user-focused
- ❌ No financial metrics visible
- ❌ No year-to-date totals
- ❌ No government entity breakdown
- ❌ User must navigate to search to see spending data

## Proposed State

### New Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│                    Dashboard Header                      │
│    "California Lobbying Activity - [Current Year]"      │
└─────────────────────────────────────────────────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   KPI Card   │  │   KPI Card   │  │   KPI Card   │
│              │  │              │  │              │
│ Total Spent  │  │ City Govt    │  │ County Govt  │
│ [Current Yr] │  │   Spending   │  │   Spending   │
│              │  │              │  │              │
│ $XX,XXX,XXX  │  │ $XX,XXX,XXX  │  │ $XX,XXX,XXX  │
│              │  │              │  │              │
│   YTD 2025   │  │  All Cities  │  │ All Counties │
└──────────────┘  └──────────────┘  └──────────────┘

┌─────────────────────────────────────────────────────────┐
│              Existing Charts Section                    │
│  - Lobby Trends Chart                                   │
│  - Organization Chart                                   │
│  - Category Chart                                       │
└─────────────────────────────────────────────────────────┘
```

### KPI Card Specifications

#### KPI #1: Total Amount Spent on Lobbying (Current Year)
**Title:** "Total Lobbying Expenditures"
**Subtitle:** "Year-to-Date 2025"
**Metric:** Sum of all lobby spending amounts for current calendar year
**Icon:** 💰
**Color:** Blue (#2563eb)

**Data Source:**
- Sum `amount` field from all lobby activities
- Filter by `date >= '2025-01-01'` AND `date <= '2025-12-31'`
- Currently using demo data (all amounts are $0 or generated)

**Calculation:**
```javascript
const currentYear = new Date().getFullYear();
const totalYearSpending = activities
  .filter(activity => {
    const activityYear = new Date(activity.date).getFullYear();
    return activityYear === currentYear;
  })
  .reduce((sum, activity) => sum + (activity.amount || 0), 0);
```

#### KPI #2: Total City Government Spending
**Title:** "City Government Lobbying"
**Subtitle:** "All California Cities"
**Metric:** Sum of all spending by organizations with type = "City Government" or category = "City Government"
**Icon:** 🏛️
**Color:** Green (#10b981)

**Data Source:**
- Filter organizations where `category === 'City Government'` OR `organization_type === 'PURCHASER'` AND name includes "CITY OF"
- Sum all spending amounts for these organizations
- Examples: "ALAMEDA, CITY OF", "LOS ANGELES, CITY OF", etc.

**Calculation:**
```javascript
const cityOrganizations = organizations.filter(org =>
  org.category === 'City Government' ||
  org.name.includes('CITY OF')
);

const cityTotalSpending = cityOrganizations.reduce((sum, org) =>
  sum + (org.totalSpending || 0), 0
);
```

#### KPI #3: Total County Government Spending
**Title:** "County Government Lobbying"
**Subtitle:** "All California Counties"
**Metric:** Sum of all spending by organizations with type = "County Government" or category = "County Government"
**Icon:** 🏢
**Color:** Purple (#8b5cf6)

**Data Source:**
- Filter organizations where `category === 'County Government'` OR name includes "COUNTY" AND does NOT include "CITY"
- Sum all spending amounts for these organizations
- Examples: "ALAMEDA COUNTY", "LOS ANGELES COUNTY", etc.

**Calculation:**
```javascript
const countyOrganizations = organizations.filter(org =>
  org.category === 'County Government' ||
  (org.name.includes('COUNTY') && !org.name.includes('CITY OF'))
);

const countyTotalSpending = countyOrganizations.reduce((sum, org) =>
  sum + (org.totalSpending || 0), 0
);
```

## Data Considerations

### Current Demo Data Limitation
**Issue:** All organizations currently show `totalSpending: 0.0` because payment data doesn't match lobby data in sample CSVs.

**Options:**

**Option A: Use Real Spending from BigQuery Backend (Future)**
- Wait for backend API integration
- Query actual payment amounts from BigQuery
- Most accurate, but requires backend work

**Option B: Calculate from Activity Counts (Demo Mode - Recommended)**
- Generate estimated spending based on activity counts
- Formula: `estimatedSpending = activityCount × averageAmountPerActivity`
- Example: 875 activities × $5,000 = $4,375,000
- Provides realistic demo data immediately

**Option C: Use Generated Random Amounts**
- Generate realistic spending amounts for demo
- Based on organization type and activity count
- Easier to implement, less accurate representation

**Decision:** Use **Option B** for demo mode with clear indicator that data is estimated. Switch to **Option A** when backend is integrated.

### Estimated Spending Calculation

```javascript
// Realistic average amounts per activity by organization type
const AVERAGE_AMOUNTS = {
  'County Government': 8000,
  'City Government': 6000,
  'City Department': 5000,
  'County Department': 5500,
  'Health Organization': 7000,
  'Construction Authority': 6500,
  'School District': 4500,
  'Business': 10000,
  'default': 5000
};

function calculateEstimatedSpending(org) {
  const avgAmount = AVERAGE_AMOUNTS[org.category] || AVERAGE_AMOUNTS['default'];
  return org.activityCount * avgAmount;
}
```

## Implementation Plan

### Step 1: Create KPI Data Service

**File:** `src/utils/kpiCalculations.js`

```javascript
import organizationsSummary from '../data/organizations-summary.json';

// Calculate estimated spending for demo mode
export const calculateEstimatedSpending = (org) => {
  const AVERAGE_AMOUNTS = {
    'County Government': 8000,
    'City Government': 6000,
    'City Department': 5000,
    'County Department': 5500,
    'Health Organization': 7000,
    'Construction Authority': 6500,
    'School District': 4500,
    'default': 5000
  };

  const avgAmount = AVERAGE_AMOUNTS[org.category] || AVERAGE_AMOUNTS['default'];
  return org.activityCount * avgAmount;
};

// Get total spending for current year
export const getTotalYearSpending = () => {
  const useEstimates = true; // Switch to false when backend API available

  if (useEstimates) {
    // Demo mode: use estimated spending
    return organizationsSummary.organizations.reduce((total, org) => {
      return total + calculateEstimatedSpending(org);
    }, 0);
  } else {
    // Backend mode: use real spending data
    return organizationsSummary.organizations.reduce((total, org) => {
      return total + (org.totalSpending || 0);
    }, 0);
  }
};

// Get total city government spending
export const getCityGovernmentSpending = () => {
  const cityOrgs = organizationsSummary.organizations.filter(org =>
    org.category === 'City Government' ||
    org.name.includes('CITY OF')
  );

  return cityOrgs.reduce((total, org) => {
    return total + calculateEstimatedSpending(org);
  }, 0);
};

// Get total county government spending
export const getCountyGovernmentSpending = () => {
  const countyOrgs = organizationsSummary.organizations.filter(org =>
    org.category === 'County Government' ||
    (org.name.includes('COUNTY') && !org.name.includes('CITY OF'))
  );

  return countyOrgs.reduce((total, org) => {
    return total + calculateEstimatedSpending(org);
  }, 0);
};

// Get count of organizations by category
export const getOrganizationCounts = () => {
  const cityOrgs = organizationsSummary.organizations.filter(org =>
    org.category === 'City Government' || org.name.includes('CITY OF')
  );

  const countyOrgs = organizationsSummary.organizations.filter(org =>
    org.category === 'County Government' ||
    (org.name.includes('COUNTY') && !org.name.includes('CITY OF'))
  );

  return {
    totalOrganizations: organizationsSummary.organizations.length,
    cityOrganizations: cityOrgs.length,
    countyOrganizations: countyOrgs.length
  };
};
```

### Step 2: Create KPI Card Component

**File:** `src/components/KPICard.js`

```javascript
import React from 'react';
import './KPICard.css';

const KPICard = ({ title, subtitle, value, icon, color, isEstimate }) => {
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  return (
    <div className="kpi-card" style={{ borderTop: `4px solid ${color}` }}>
      <div className="kpi-header">
        <span className="kpi-icon">{icon}</span>
        <h3 className="kpi-title">{title}</h3>
      </div>
      <div className="kpi-value">
        {formatCurrency(value)}
      </div>
      <div className="kpi-subtitle">
        {subtitle}
        {isEstimate && (
          <span className="kpi-estimate-badge">Estimated</span>
        )}
      </div>
    </div>
  );
};

export default KPICard;
```

### Step 3: Create KPI Styles

**File:** `src/components/KPICard.css`

```css
.kpi-card {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.kpi-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.kpi-icon {
  font-size: 32px;
}

.kpi-title {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.kpi-value {
  font-size: 36px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
  font-variant-numeric: tabular-nums;
}

.kpi-subtitle {
  font-size: 14px;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 8px;
}

.kpi-estimate-badge {
  display: inline-block;
  background: #fef3c7;
  color: #92400e;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

/* Responsive design */
@media (max-width: 768px) {
  .kpi-card {
    padding: 16px;
  }

  .kpi-value {
    font-size: 28px;
  }

  .kpi-title {
    font-size: 14px;
  }
}
```

### Step 4: Update Dashboard Component

**File:** `src/components/Dashboard.js`

```javascript
import React, { useMemo } from 'react';
import { useUser } from '@clerk/clerk-react';
import KPICard from './KPICard';
import {
  getTotalYearSpending,
  getCityGovernmentSpending,
  getCountyGovernmentSpending,
  getOrganizationCounts
} from '../utils/kpiCalculations';
import { LobbyTrendsChart, OrganizationChart, CategoryChart } from './charts';
import './Dashboard.css';

function Dashboard() {
  const { user, isLoaded } = useUser();
  const currentYear = new Date().getFullYear();

  // Calculate KPI values
  const kpiData = useMemo(() => ({
    totalYearSpending: getTotalYearSpending(),
    citySpending: getCityGovernmentSpending(),
    countySpending: getCountyGovernmentSpending(),
    counts: getOrganizationCounts()
  }), []);

  if (!isLoaded) {
    return <div className="loading-container">Loading dashboard...</div>;
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>California Lobbying Dashboard</h1>
        <p className="page-description">
          Year-to-date lobbying expenditure analysis for {currentYear}
        </p>
      </div>

      <div className="page-content">
        {/* KPI Section */}
        <div className="kpi-section">
          <div className="kpi-grid">
            <KPICard
              title="Total Lobbying Expenditures"
              subtitle={`Year-to-Date ${currentYear}`}
              value={kpiData.totalYearSpending}
              icon="💰"
              color="#2563eb"
              isEstimate={true}
            />
            <KPICard
              title="City Government Lobbying"
              subtitle={`${kpiData.counts.cityOrganizations} California Cities`}
              value={kpiData.citySpending}
              icon="🏛️"
              color="#10b981"
              isEstimate={true}
            />
            <KPICard
              title="County Government Lobbying"
              subtitle={`${kpiData.counts.countyOrganizations} California Counties`}
              value={kpiData.countySpending}
              icon="🏢"
              color="#8b5cf6"
              isEstimate={true}
            />
          </div>
        </div>

        {/* Charts Section */}
        <div className="dashboard-section">
          <h2>CA Lobby Data Insights</h2>
          <div className="charts-grid">
            <LobbyTrendsChart />
            <OrganizationChart />
            <CategoryChart />
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
```

### Step 5: Update Dashboard Styles

**File:** `src/components/Dashboard.css` (additions)

```css
.kpi-section {
  margin-bottom: 40px;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

@media (min-width: 1024px) {
  .kpi-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .kpi-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}
```

## Testing Plan

### Manual Testing
1. ✅ Navigate to Dashboard
2. ✅ Verify all 3 KPI cards display
3. ✅ Verify amounts are formatted correctly
4. ✅ Verify "Estimated" badge shows
5. ✅ Verify counts are accurate
6. ✅ Test responsive design (mobile, tablet, desktop)
7. ✅ Verify charts still display below KPIs

### Data Validation
1. ✅ Calculate expected totals manually
2. ✅ Compare with displayed values
3. ✅ Verify city vs county categorization is correct
4. ✅ Ensure no organizations are double-counted

### Edge Cases
1. ✅ All organizations have zero spending (should show $0)
2. ✅ Very large amounts (should format correctly: $1,234,567,890)
3. ✅ No city governments in data
4. ✅ No county governments in data

## Sample Data Calculations

### Based on Current Alameda County Sample Data

| Organization | Category | Activity Count | Estimated Spending |
|--------------|----------|---------------|-------------------|
| ALAMEDA COUNTY | County Government | 875 | 875 × $8,000 = $7,000,000 |
| ALAMEDA, CITY OF | City Government | 406 | 406 × $6,000 = $2,436,000 |
| ALAMEDA COUNTY WASTE MGMT | County Department | 611 | 611 × $5,500 = $3,360,500 |
| ALAMEDA UNIFIED SCHOOL DIST | City Department | 77 | 77 × $5,000 = $385,000 |
| ALAMEDA ALLIANCE FOR HEALTH | Health Organization | 266 | 266 × $7,000 = $1,862,000 |
| ALAMEDA CORRIDOR-EAST CONST | Construction Authority | 588 | 588 × $6,500 = $3,822,000 |

**Expected KPI Values:**
- **Total Spending:** $18,865,500
- **City Government:** $2,436,000 (1 city)
- **County Government:** $7,000,000 + $3,360,500 = $10,360,500 (2 county entities)

## Future Enhancements

### Phase 2 (After Backend Integration)
- ✅ Use real spending data from BigQuery
- ✅ Remove "Estimated" badges
- ✅ Add trend indicators (↑ 15% vs last year)
- ✅ Add drill-down capability (click to see details)

### Phase 3 (Advanced Features)
~~- ✅ Add time period selector (YTD, Last Quarter, Last Year)~~
- ✅ Add comparison to previous periods
- ✅ Add sparkline charts within KPI cards
~~- ✅ Add export KPI summary to PDF~~

## Success Metrics

- ✅ All 3 KPIs display correctly on Dashboard
- ✅ Values update when underlying data changes
- ✅ Mobile responsive design works properly
- ✅ Page load time remains under 3 seconds
- ✅ Bundle size increase is minimal (<10KB)

## Deployment Strategy

1. ✅ Create KPI utilities and components
2. ✅ Update Dashboard component
3. ✅ Test locally with sample data
4. ✅ Commit and push to GitHub
5. ✅ Deploy to Vercel
6. ✅ Verify in production
7. ✅ Monitor for errors

## Rollback Plan

If issues occur:
1. Revert Dashboard.js to previous version
2. Keep charts section functional
3. Remove KPI components
4. Redeploy stable version

## Dependencies

- ✅ `organizations-summary.json` with category field
- ✅ React hooks (useMemo for performance)
- ✅ Existing Dashboard CSS structure
- ⚠️ Backend API (future - for real spending data)

## Sign-Off

**Plan Status:** ⏳ AWAITING APPROVAL
**Estimated Duration:** 1 day
**Dependencies:** None (uses existing data)
**Risk Level:** Low (purely additive)

---

**Last Updated:** October 24, 2025
**Author:** CA Lobby Development Team
**Next Review:** After implementation
