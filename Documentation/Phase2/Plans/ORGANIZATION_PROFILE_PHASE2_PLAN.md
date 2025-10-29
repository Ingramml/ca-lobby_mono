# Organization Profile Page - Phase 2 Implementation Plan
## Enhanced Data & Visualization

**Project:** California Lobby Search System
**Project Code:** CA_LOBBY
**Phase:** 2f.2 - Organization Profile Data Enhancement
**Duration:** Day 2 (6-8 hours)
**Start Date:** October 1, 2025 (estimated)
**Status:** ⏸️ PENDING (Awaits Phase 1 completion)

---

## 📋 Phase 2 Overview

Enhance the organization profile page with comprehensive data visualization and state management:
- Create dedicated Zustand store for organization data
- Implement data aggregation utilities
- Add spending trends visualization
- Build paginated activity list
- Display lobbyist network
- Show related organizations

---

## 🎯 Phase 2 Objectives

### Primary Goals
1. ✅ Create organizationStore with Zustand for profile state management
2. ✅ Build data aggregation utilities for metrics calculation
3. ✅ Integrate Recharts for spending trends visualization
4. ✅ Implement paginated activity list (10 items per page)
5. ✅ Display lobbyist network with activity counts
6. ✅ Show related organizations based on similarity scores

### Success Criteria
- [ ] organizationStore manages all profile state
- [ ] Spending trends chart displays time-series data
- [ ] Activity list paginates correctly (10 per page)
- [ ] Lobbyist network shows unique lobbyists with stats
- [ ] Related organizations ranked by similarity
- [ ] All sections integrate seamlessly with responsive layout

---

## 📊 Prerequisites

### ✅ Phase 1 Completed
- OrganizationProfile component exists
- Basic navigation and routing functional
- Organization filtering working
- CSS framework in place

### ✅ Infrastructure Available
- Zustand v5.0.8 installed
- Recharts v3.2.1 installed
- Existing store patterns (searchStore, userStore, appStore)
- Existing chart components (LobbyTrendsChart, OrganizationChart)
- Demo data with organization activities

---

## 🏗️ Implementation Tasks

### Task 2.1: Create organizationStore.js (20 min)

**Action:** Create new Zustand store for organization profile state management

**Files:**
- **CREATE**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/stores/organizationStore.js`

**Implementation:**
```javascript
import { create } from 'zustand';

const useOrganizationStore = create((set, get) => ({
  // State
  selectedOrganization: null,
  organizationData: null,
  activities: [],
  lobbyists: [],
  relatedOrganizations: [],
  spendingTrends: [],
  loading: false,
  error: null,

  // Pagination state
  currentPage: 1,
  itemsPerPage: 10,
  totalActivities: 0,

  // Actions
  setSelectedOrganization: (org) => set({ selectedOrganization: org }),

  setOrganizationData: (data) => set({
    organizationData: data,
    loading: false
  }),

  setActivities: (activities) => set({
    activities,
    totalActivities: activities.length,
    loading: false
  }),

  setLobbyists: (lobbyists) => set({ lobbyists }),

  setRelatedOrganizations: (orgs) => set({ relatedOrganizations: orgs }),

  setSpendingTrends: (trends) => set({ spendingTrends: trends }),

  setLoading: (loading) => set({ loading }),

  setError: (error) => set({ error, loading: false }),

  setCurrentPage: (page) => set({ currentPage: page }),

  // Reset organization state
  clearOrganization: () => set({
    selectedOrganization: null,
    organizationData: null,
    activities: [],
    lobbyists: [],
    relatedOrganizations: [],
    spendingTrends: [],
    currentPage: 1,
    error: null
  }),

  // Computed getters
  getPaginatedActivities: () => {
    const { activities, currentPage, itemsPerPage } = get();
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return activities.slice(startIndex, endIndex);
  },

  getTotalPages: () => {
    const { totalActivities, itemsPerPage } = get();
    return Math.ceil(totalActivities / itemsPerPage);
  }
}));

export default useOrganizationStore;
```

**Testing Checklist:**
- [ ] Import the store in a test file
- [ ] Verify all actions update state correctly
- [ ] Test pagination functions (getPaginatedActivities, getTotalPages)
- [ ] Verify clearOrganization resets all state
- [ ] Test setCurrentPage updates page number
- [ ] Confirm computed getters return correct values

**Estimated Time:** 20 minutes

---

### Task 2.2: Update stores/index.js (5 min)

**Action:** Export the new organizationStore from the stores index file

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/stores/index.js`

**Implementation:**

Add export for organizationStore:
```javascript
export { default as useOrganizationStore } from './organizationStore';
```

**Testing Checklist:**
- [ ] Verify import works: `import { useOrganizationStore } from '../stores'`
- [ ] Check no errors in console
- [ ] Verify other store exports still work

**Estimated Time:** 5 minutes

---

### Task 2.3: Create Aggregation Utilities (30 min)

**Action:** Add organization-specific data aggregation functions to sampleData.js

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/utils/sampleData.js`

**Implementation:**

Add these functions at the end of the file:

```javascript
// Aggregate organization summary metrics
export const aggregateOrganizationMetrics = (activities) => {
  if (!activities || activities.length === 0) {
    return {
      totalSpending: 0,
      totalActivities: 0,
      averageAmount: 0,
      firstActivity: null,
      lastActivity: null,
      topCategory: 'N/A'
    };
  }

  const totalSpending = activities.reduce((sum, a) => sum + (a.amount || 0), 0);
  const totalActivities = activities.length;
  const averageAmount = totalSpending / totalActivities;

  const sortedByDate = [...activities].sort((a, b) =>
    new Date(a.date || a.filing_date) - new Date(b.date || b.filing_date)
  );

  const firstActivity = sortedByDate[0]?.date || sortedByDate[0]?.filing_date;
  const lastActivity = sortedByDate[sortedByDate.length - 1]?.date ||
                       sortedByDate[sortedByDate.length - 1]?.filing_date;

  // Find top category
  const categoryCount = activities.reduce((acc, a) => {
    const cat = a.category || 'Unknown';
    acc[cat] = (acc[cat] || 0) + 1;
    return acc;
  }, {});

  const topCategory = Object.entries(categoryCount)
    .sort((a, b) => b[1] - a[1])[0]?.[0] || 'N/A';

  return {
    totalSpending,
    totalActivities,
    averageAmount,
    firstActivity,
    lastActivity,
    topCategory
  };
};

// Extract unique lobbyists from organization activities
export const extractLobbyistNetwork = (activities) => {
  const lobbyistMap = activities.reduce((acc, activity) => {
    const name = activity.lobbyist;
    if (!name) return acc;

    if (!acc[name]) {
      acc[name] = {
        name,
        activityCount: 0,
        totalAmount: 0,
        categories: new Set()
      };
    }

    acc[name].activityCount += 1;
    acc[name].totalAmount += activity.amount || 0;
    if (activity.category) {
      acc[name].categories.add(activity.category);
    }

    return acc;
  }, {});

  return Object.values(lobbyistMap)
    .map(l => ({
      ...l,
      categories: Array.from(l.categories)
    }))
    .sort((a, b) => b.totalAmount - a.totalAmount);
};

// Calculate spending trends by time period
export const calculateSpendingTrends = (activities, periodType = 'quarter') => {
  const trendMap = activities.reduce((acc, activity) => {
    const date = new Date(activity.date || activity.filing_date);
    let period;

    if (periodType === 'quarter') {
      const q = Math.floor(date.getMonth() / 3) + 1;
      period = `Q${q} ${date.getFullYear()}`;
    } else if (periodType === 'month') {
      period = date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    } else {
      period = date.getFullYear().toString();
    }

    if (!acc[period]) {
      acc[period] = { period, amount: 0, count: 0 };
    }

    acc[period].amount += activity.amount || 0;
    acc[period].count += 1;

    return acc;
  }, {});

  return Object.values(trendMap).sort((a, b) => {
    // Sort chronologically
    if (periodType === 'quarter') {
      const [qA, yearA] = a.period.split(' ');
      const [qB, yearB] = b.period.split(' ');
      return yearA !== yearB ? yearA - yearB : qA.replace('Q', '') - qB.replace('Q', '');
    }
    return new Date(a.period) - new Date(b.period);
  });
};

// Find related organizations (same category or similar spending patterns)
export const findRelatedOrganizations = (organizationName, allActivities, limit = 5) => {
  // Get current org activities
  const orgActivities = allActivities.filter(a => a.organization === organizationName);
  const orgCategories = [...new Set(orgActivities.map(a => a.category))];
  const orgTotalSpending = orgActivities.reduce((sum, a) => sum + (a.amount || 0), 0);

  // Group all other organizations
  const otherOrgs = allActivities
    .filter(a => a.organization !== organizationName)
    .reduce((acc, activity) => {
      const org = activity.organization;
      if (!acc[org]) {
        acc[org] = {
          name: org,
          totalSpending: 0,
          activityCount: 0,
          categories: new Set(),
          sharedCategories: 0
        };
      }

      acc[org].totalSpending += activity.amount || 0;
      acc[org].activityCount += 1;
      if (activity.category) {
        acc[org].categories.add(activity.category);
        if (orgCategories.includes(activity.category)) {
          acc[org].sharedCategories += 1;
        }
      }

      return acc;
    }, {});

  // Calculate similarity scores
  return Object.values(otherOrgs)
    .map(org => {
      const spendingDiff = Math.abs(org.totalSpending - orgTotalSpending);
      const spendingSimilarity = 1 / (1 + spendingDiff / 1000000); // Normalize
      const categorySimilarity = org.sharedCategories / orgCategories.length;

      return {
        ...org,
        categories: Array.from(org.categories),
        similarityScore: (spendingSimilarity * 0.4) + (categorySimilarity * 0.6)
      };
    })
    .sort((a, b) => b.similarityScore - a.similarityScore)
    .slice(0, limit);
};
```

**Testing Checklist:**
- [ ] Call `aggregateOrganizationMetrics(sampleActivities)` in console
- [ ] Verify all metrics are calculated correctly
- [ ] Test with empty array to ensure defaults work
- [ ] Check `extractLobbyistNetwork` returns unique lobbyists
- [ ] Verify lobbyists sorted by total amount descending
- [ ] Test `calculateSpendingTrends` with different period types
- [ ] Verify trends sort chronologically
- [ ] Test `findRelatedOrganizations` returns similar orgs
- [ ] Verify similarity score calculation is reasonable

**Estimated Time:** 30 minutes

---

### Task 2.4: Integrate organizationStore into OrganizationProfile (25 min)

**Action:** Update OrganizationProfile component to use new store and aggregation functions

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/OrganizationProfile.js`

**Implementation:**

Update imports and component logic:
```javascript
import React, { useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useOrganizationStore, useSearchStore } from '../stores';
import {
  aggregateOrganizationMetrics,
  extractLobbyistNetwork,
  calculateSpendingTrends,
  findRelatedOrganizations
} from '../utils/sampleData';

function OrganizationProfile() {
  const { organizationName } = useParams();
  const navigate = useNavigate();

  const {
    selectedOrganization,
    organizationData,
    loading,
    error,
    setSelectedOrganization,
    setOrganizationData,
    setLobbyists,
    setSpendingTrends,
    setRelatedOrganizations,
    setActivities,
    setLoading,
    clearOrganization
  } = useOrganizationStore();

  const { results } = useSearchStore();

  const decodedOrgName = useMemo(() =>
    decodeURIComponent(organizationName),
    [organizationName]
  );

  useEffect(() => {
    if (!decodedOrgName) {
      clearOrganization();
      return;
    }

    // Set loading state
    setLoading(true);
    setSelectedOrganization(decodedOrgName);

    // Filter activities for this organization from search results
    const orgActivities = results.filter(
      r => r.organization === decodedOrgName
    );

    // Aggregate all data
    const metrics = aggregateOrganizationMetrics(orgActivities);
    const lobbyists = extractLobbyistNetwork(orgActivities);
    const trends = calculateSpendingTrends(orgActivities, 'quarter');
    const related = findRelatedOrganizations(decodedOrgName, results, 5);

    // Update store
    setOrganizationData(metrics);
    setActivities(orgActivities);
    setLobbyists(lobbyists);
    setSpendingTrends(trends);
    setRelatedOrganizations(related);
  }, [decodedOrgName, results, setSelectedOrganization, setOrganizationData,
      setActivities, setLobbyists, setSpendingTrends, setRelatedOrganizations,
      setLoading, clearOrganization]);

  // ... rest of component logic remains similar
}
```

**Testing Checklist:**
- [ ] Navigate to organization profile
- [ ] Verify organizationStore populates with data
- [ ] Check loading state displays initially
- [ ] Verify data appears after aggregation completes
- [ ] Test with different organizations
- [ ] Verify store clears when navigating away
- [ ] Check React DevTools for store state updates

**Estimated Time:** 25 minutes

---

### Task 2.5: Create ActivitySummary Component (25 min)

**Action:** Build metrics dashboard showing key organization statistics

**Files:**
- **CREATE**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/ActivitySummary.js`

**Implementation:**

See Phase 2 detailed task breakdown (Task 2.5) in agent response for full implementation.

**Key Features:**
- Display 6 metric cards: Total Spending, Total Activities, Average Amount, Top Category, First Activity, Latest Activity
- Currency and date formatting
- Responsive metrics grid layout
- Icon indicators for each metric

**Testing Checklist:**
- [ ] Render component with populated organizationStore
- [ ] Verify all 6 metrics display correctly
- [ ] Check currency formatting (commas, decimals)
- [ ] Verify date formatting
- [ ] Confirm null data doesn't break component
- [ ] Test responsive grid on mobile

**Estimated Time:** 25 minutes

---

### Task 2.6: Create SpendingTrendsChart Component (25 min)

**Action:** Build line chart showing spending over time using Recharts

**Files:**
- **CREATE**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/charts/SpendingTrendsChart.js`

**Implementation:**

See Phase 2 detailed task breakdown (Task 2.6) in agent response for full implementation.

**Key Features:**
- Line chart with spending trends from organizationStore
- Mobile-responsive configuration
- Theme support (light/dark)
- Empty state handling
- Currency-formatted tooltips and axis

**Testing Checklist:**
- [ ] Verify chart renders with trend data
- [ ] Check mobile responsiveness (300px height on mobile)
- [ ] Test empty state displays properly
- [ ] Confirm tooltip shows correct currency values
- [ ] Test theme switching (if applicable)
- [ ] Verify chart legend displays

**Estimated Time:** 25 minutes

---

### Task 2.7: Create ActivityList Component with Pagination (30 min)

**Action:** Build paginated list of organization activities

**Files:**
- **CREATE**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/ActivityList.js`

**Implementation:**

See Phase 2 detailed task breakdown (Task 2.7) in agent response for full implementation.

**Key Features:**
- Display 10 activities per page
- Pagination controls (First, Previous, Next, Last)
- Page indicator showing current range
- Scroll to top on page change
- Empty state handling
- Currency and date formatting

**Testing Checklist:**
- [ ] Verify activities display correctly (10 per page)
- [ ] Test pagination buttons work (all 4 buttons)
- [ ] Check first/last/prev/next all function properly
- [ ] Confirm page count displays correctly (e.g., "Showing 1-10 of 23")
- [ ] Test empty state when no activities
- [ ] Verify scroll to top on page change
- [ ] Test with exactly 10 activities (no pagination)

**Estimated Time:** 30 minutes

---

### Task 2.8: Create LobbyistNetwork Component (25 min)

**Action:** Display lobbyists associated with the organization

**Files:**
- **CREATE**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/LobbyistNetwork.js`

**Implementation:**

See Phase 2 detailed task breakdown (Task 2.8) in agent response for full implementation.

**Key Features:**
- Display lobbyist cards with avatar, name, stats
- Show activity count and total amount per lobbyist
- Display focus areas (categories)
- Expand/collapse functionality (show 5 initially, expand to show all)
- Empty state handling

**Testing Checklist:**
- [ ] Verify lobbyist cards render with correct data
- [ ] Test expand/collapse functionality
- [ ] Check empty state displays
- [ ] Confirm category tags display properly
- [ ] Verify currency formatting for amounts
- [ ] Test with 0 lobbyists, 1 lobbyist, 5+ lobbyists

**Estimated Time:** 25 minutes

---

### Task 2.9: Create RelatedOrganizations Component (20 min)

**Action:** Show similar organizations widget with similarity scoring

**Files:**
- **CREATE**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/RelatedOrganizations.js`

**Implementation:**

See Phase 2 detailed task breakdown (Task 2.9) in agent response for full implementation.

**Key Features:**
- Display up to 5 related organizations
- Show similarity badge (Very Similar, Similar, Somewhat Similar, Related)
- Display total spending and activity count
- Show categories (limited to 3 + overflow)
- Click handler to navigate to related org profile
- Empty state handling

**Testing Checklist:**
- [ ] Verify related orgs display with similarity scores
- [ ] Test click handler navigates to new org profile
- [ ] Check empty state
- [ ] Confirm similarity badges show correct colors
- [ ] Verify compact currency formatting
- [ ] Test category overflow display (+2 more)

**Estimated Time:** 20 minutes

---

### Task 2.10: Integrate All Components into OrganizationProfile (20 min)

**Action:** Assemble all child components in the main profile page

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/OrganizationProfile.js`

**Implementation:**

Add imports and update render:
```javascript
import ActivitySummary from './ActivitySummary';
import SpendingTrendsChart from './charts/SpendingTrendsChart';
import ActivityList from './ActivityList';
import LobbyistNetwork from './LobbyistNetwork';
import RelatedOrganizations from './RelatedOrganizations';

// In return statement:
<div className="page-content">
  {/* Activity Summary Metrics */}
  <ActivitySummary />

  {/* Spending Trends Chart */}
  <div className="dashboard-card">
    <SpendingTrendsChart />
  </div>

  {/* Two-column layout for lists */}
  <div className="profile-grid">
    <div className="profile-main">
      <ActivityList />
    </div>

    <div className="profile-sidebar">
      <div className="dashboard-card">
        <LobbyistNetwork />
      </div>

      <div className="dashboard-card">
        <RelatedOrganizations
          onOrganizationClick={(orgName) => {
            navigate(`/organization/${encodeURIComponent(orgName)}`);
            window.scrollTo({ top: 0, behavior: 'smooth' });
          }}
        />
      </div>
    </div>
  </div>
</div>
```

**Testing Checklist:**
- [ ] Verify all sections render in correct layout
- [ ] Test responsive behavior on mobile (single column)
- [ ] Check related org click navigates correctly
- [ ] Confirm all data flows from store properly
- [ ] Verify no console errors
- [ ] Test complete user flow from search to profile

**Estimated Time:** 20 minutes

---

### Task 2.11: Update charts/index.js Export (5 min)

**Action:** Export new SpendingTrendsChart from charts index

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/charts/index.js`

**Implementation:**

Add export:
```javascript
export { default as SpendingTrendsChart } from './SpendingTrendsChart';
```

**Testing Checklist:**
- [ ] Verify import works: `import { SpendingTrendsChart } from './charts'`
- [ ] Verify other chart exports still work

**Estimated Time:** 5 minutes

---

### Task 2.12: Add CSS Styles for All Components (30 min)

**Action:** Add comprehensive styling for all profile components

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/App.css`

**Implementation:**

See Phase 2 detailed task breakdown (Task 2.12) in agent response for full CSS code.

**Key Styles:**
- Activity summary metrics grid
- Activity list and pagination
- Lobbyist network cards
- Related organizations styling
- Profile grid layout (2-column on desktop, 1-column on mobile)
- Responsive breakpoints

**Testing Checklist:**
- [ ] Verify all components styled correctly
- [ ] Test responsive breakpoints (320px, 768px, 1024px, 1200px)
- [ ] Check hover states work
- [ ] Confirm colors match design system
- [ ] Verify spacing and padding consistent
- [ ] Test dark mode if applicable

**Estimated Time:** 30 minutes

---

### Task 2.13: Enhance Demo Data in Search Component (15 min)

**Action:** Expand demo data to include 15-20 items with repeated organizations

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/Search.js`

**Implementation:**

Expand the demoData array to include multiple activities for each organization (see Task 1.9 from Phase 1 for pattern, expand further).

**Testing Checklist:**
- [ ] Run search with no filters to get all demo data
- [ ] Click "California Medical Association"
- [ ] Verify profile shows multiple activities (5+ activities)
- [ ] Check aggregation functions calculate correctly
- [ ] Test with other organizations
- [ ] Verify related organizations populate

**Estimated Time:** 15 minutes

---

### Task 2.14: Add Loading States to All Components (15 min)

**Action:** Implement loading indicators for data sections

**Files:**
- **MODIFY**: All component files created in Phase 2

**Implementation:**

For each component:
1. Get `loading` state from organizationStore
2. Show loading indicator or skeleton while loading
3. Display component content when loaded

**Testing Checklist:**
- [ ] Verify loading states display for all sections
- [ ] Test transition from loading to loaded state
- [ ] Ensure no layout shift during loading
- [ ] Test on slow network (Chrome throttling)

**Estimated Time:** 15 minutes

---

### Task 2.15: Add Error Boundaries (15 min)

**Action:** Wrap components in error boundaries for graceful failure handling

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/OrganizationProfile.js`

**Implementation:**

Use existing ErrorBoundary component (if available) or create simple error handling:
```javascript
// Add error display logic
if (error) {
  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Error Loading Profile</h1>
      </div>
      <div className="page-content">
        <div className="dashboard-card">
          <h3>Something went wrong</h3>
          <p>{error}</p>
          <button onClick={() => navigate('/search')} className="btn">
            Return to Search
          </button>
        </div>
      </div>
    </div>
  );
}
```

**Testing Checklist:**
- [ ] Test error state displays correctly
- [ ] Verify error message is clear
- [ ] Test return to search button works
- [ ] Ensure no console errors from components

**Estimated Time:** 15 minutes

---

### Task 2.16: Performance Testing and Optimization (20 min)

**Action:** Profile component performance and optimize as needed

**Files:**
- Multiple component files as needed

**Implementation:**

1. Use React DevTools Profiler
2. Measure render times for each component
3. Identify expensive re-renders
4. Add React.memo where appropriate
5. Optimize useMemo dependencies

**Testing Checklist:**
- [ ] Profile page load time < 1 second
- [ ] Component re-renders minimized
- [ ] No memory leaks on navigation
- [ ] Smooth pagination transitions
- [ ] Charts render quickly

**Estimated Time:** 20 minutes

---

### Task 2.17: Final Phase 2 Integration Testing (20 min)

**Action:** Complete end-to-end testing of all Phase 2 features

**Testing Checklist:**

**Store Functionality:**
- [ ] organizationStore initializes correctly
- [ ] All store actions work (set, clear, paginate)
- [ ] Store persists data during navigation

**Data Aggregation:**
- [ ] Metrics calculate correctly
- [ ] Lobbyist network extracts unique lobbyists
- [ ] Spending trends sort chronologically
- [ ] Related orgs ranked by similarity

**Components:**
- [ ] ActivitySummary displays all 6 metrics
- [ ] SpendingTrendsChart renders with data
- [ ] ActivityList paginates correctly
- [ ] LobbyistNetwork displays and expands
- [ ] RelatedOrganizations shows similar orgs

**Integration:**
- [ ] All components receive data from store
- [ ] Related org click navigates correctly
- [ ] Pagination updates activities display
- [ ] Responsive layout works on all devices

**User Flow:**
- [ ] Search → Click org → View profile (full workflow)
- [ ] Click related org → New profile loads
- [ ] Navigate back → Return to search
- [ ] All data accurate throughout

**Estimated Time:** 20 minutes

---

## 📊 Phase 2 Summary

### Time Breakdown
- **Store & Utilities** (Tasks 2.1-2.3): ~55 minutes
- **Core Components** (Tasks 2.4-2.9): ~2.5 hours
- **Integration & Styling** (Tasks 2.10-2.12): ~55 minutes
- **Enhancements** (Tasks 2.13-2.15): ~45 minutes
- **Testing & Optimization** (Tasks 2.16-2.17): ~40 minutes

**Total Estimated Time:** 6-8 hours

### Key Deliverables
1. ✅ organizationStore with Zustand state management
2. ✅ Data aggregation utilities (metrics, lobbyists, trends, related orgs)
3. ✅ ActivitySummary component with 6 metrics
4. ✅ SpendingTrendsChart with Recharts integration
5. ✅ ActivityList with pagination (10 items/page)
6. ✅ LobbyistNetwork with expand/collapse
7. ✅ RelatedOrganizations with similarity scoring
8. ✅ Comprehensive CSS styling
9. ✅ Loading states and error handling
10. ✅ Performance optimizations

### Files Created
- `/Users/michaelingram/Documents/GitHub/CA_lobby/src/stores/organizationStore.js`
- `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/ActivitySummary.js`
- `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/ActivityList.js`
- `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/LobbyistNetwork.js`
- `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/RelatedOrganizations.js`
- `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/charts/SpendingTrendsChart.js`

### Files Modified
- `/Users/michaelingram/Documents/GitHub/CA_lobby/src/stores/index.js`
- `/Users/michaelingram/Documents/GitHub/CA_lobby/src/utils/sampleData.js`
- `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/OrganizationProfile.js`
- `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/Search.js`
- `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/charts/index.js`
- `/Users/michaelingram/Documents/GitHub/CA_lobby/src/App.css`

### Success Criteria Met
- [ ] organizationStore manages all profile state
- [ ] Spending trends chart displays time-series data
- [ ] Activity list paginates correctly (10 per page)
- [ ] Lobbyist network shows unique lobbyists with stats
- [ ] Related organizations ranked by similarity
- [ ] All sections integrate seamlessly with responsive layout

---

## 🔄 Next Steps

After completing Phase 2:
1. **Review and Test**: Complete Task 2.17 thoroughly
2. **Commit Changes**: Use micro-save points strategy
3. **Document Issues**: Note any deviations or problems
4. **Proceed to Phase 3**: Export functionality, accessibility, deployment

---

**Last Updated:** September 30, 2025
**Status:** Pending (Awaits Phase 1 completion)
**Next Review:** After Phase 2 completion