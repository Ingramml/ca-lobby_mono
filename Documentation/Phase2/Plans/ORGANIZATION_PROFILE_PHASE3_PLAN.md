# Organization Profile Page - Phase 3 Implementation Plan
## Polish, Export & Deployment

**Project:** California Lobby Search System
**Project Code:** CA_LOBBY
**Phase:** 2f.3 - Organization Profile Finalization
**Duration:** Day 3 (4-6 hours)
**Start Date:** October 2, 2025 (estimated)
**Status:** ⏸️ PENDING (Awaits Phase 2 completion)

---

## 📋 Phase 3 Overview

Finalize the organization profile feature with production-ready polish:
- Export functionality (CSV/JSON)
- Loading states and error handling
- Accessibility improvements (ARIA, keyboard navigation)
- Mobile-responsive optimization
- Performance optimizations
- Production deployment

---

## 🎯 Phase 3 Objectives

### Primary Goals
1. ✅ Implement CSV and JSON export functionality
2. ✅ Add comprehensive loading skeletons and error states
3. ✅ Ensure WCAG 2.1 AA accessibility compliance
4. ✅ Optimize for mobile devices (touch-friendly, responsive)
5. ✅ Implement performance optimizations (lazy loading, memoization)
6. ✅ Deploy to production with monitoring

### Success Criteria
- [ ] Export downloads work for CSV and JSON formats
- [ ] Loading states prevent layout shift (CLS < 0.1)
- [ ] Lighthouse accessibility score ≥95
- [ ] Mobile experience is touch-friendly (44px targets)
- [ ] Page load time <2 seconds on 3G
- [ ] Production deployment succeeds without errors

---

## 📊 Prerequisites

### ✅ Phase 1 & 2 Completed
- OrganizationProfile component fully functional
- All data sections implemented
- Charts and visualizations working
- State management operational

### ✅ Infrastructure Available
- Vercel deployment pipeline configured
- Chrome DevTools for testing
- React DevTools for profiling
- Lighthouse for auditing

---

## 🏗️ Implementation Tasks

### Task 3.1: Create Export Utility Functions (20 min)

**Action:** Build reusable export helper functions for CSV and JSON data downloads

**Files:**
- **CREATE**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/utils/exportHelpers.js`

**Implementation:**
```javascript
// Convert array of objects to CSV format
export const exportToCSV = (data, filename) => {
  if (!data || data.length === 0) {
    console.warn('No data to export');
    return;
  }

  // Get headers from first object
  const headers = Object.keys(data[0]);
  const csvContent = [
    headers.join(','),
    ...data.map(row =>
      headers.map(header =>
        JSON.stringify(row[header] || '')
      ).join(',')
    )
  ].join('\n');

  triggerDownload(csvContent, filename, 'text/csv');
};

// Generate downloadable JSON file
export const exportToJSON = (data, filename) => {
  if (!data) {
    console.warn('No data to export');
    return;
  }

  const jsonContent = JSON.stringify(data, null, 2);
  triggerDownload(jsonContent, filename, 'application/json');
};

// Format organization profile for CSV export
export const generateOrganizationSummaryCSV = (orgData) => {
  return {
    Organization: orgData.selectedOrganization,
    'Total Activities': orgData.organizationData?.totalActivities || 0,
    'Total Spending': orgData.organizationData?.totalSpending || 0,
    'Average Amount': orgData.organizationData?.averageAmount || 0,
    'Unique Lobbyists': orgData.lobbyists?.length || 0,
    'First Activity': orgData.organizationData?.firstActivity || 'N/A',
    'Latest Activity': orgData.organizationData?.lastActivity || 'N/A',
    'Top Category': orgData.organizationData?.topCategory || 'N/A'
  };
};

// Format activity list for CSV export
export const generateActivitiesCSV = (activities) => {
  return activities.map(activity => ({
    Date: activity.date || activity.filing_date || 'N/A',
    Lobbyist: activity.lobbyist || 'Unknown',
    Amount: activity.amount || 0,
    Category: activity.category || 'N/A',
    Description: activity.description || activity.activity_description || 'No description'
  }));
};

// Handle browser download
const triggerDownload = (content, filename, type) => {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};
```

**Testing Checklist:**
- [ ] Create test object with sample organization data
- [ ] Call exportToCSV() and verify CSV file downloads
- [ ] Call exportToJSON() and verify JSON file downloads
- [ ] Verify filenames contain organization name
- [ ] Test with special characters in organization names
- [ ] Test with empty data (should warn, not crash)
- [ ] Open downloaded files to verify format correctness

**Estimated Time:** 20 minutes

---

### Task 3.2: Add Export Buttons to Organization Header (15 min)

**Action:** Add CSV/JSON export buttons to OrganizationProfile component header

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/OrganizationProfile.js`

**Implementation:**

```javascript
import {
  exportToCSV,
  exportToJSON,
  generateOrganizationSummaryCSV
} from '../utils/exportHelpers';

// Add export handlers
const handleExportCSV = () => {
  const summaryData = generateOrganizationSummaryCSV({
    selectedOrganization,
    organizationData,
    lobbyists
  });
  exportToCSV([summaryData], `${selectedOrganization}_summary.csv`);
};

const handleExportJSON = () => {
  const exportData = {
    organization: selectedOrganization,
    data: organizationData,
    activities: activities,
    lobbyists: lobbyists,
    spendingTrends: spendingTrends,
    relatedOrganizations: relatedOrganizations
  };
  exportToJSON(exportData, `${selectedOrganization}_profile.json`);
};

// Add export buttons to header
<div className="page-header">
  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
    <div>
      <button
        onClick={() => navigate('/search')}
        className="btn btn-secondary"
        style={{ marginBottom: '16px' }}
      >
        ← Back to Search
      </button>
      <h1>{selectedOrganization}</h1>
      <p className="page-description">Comprehensive lobbying activity profile</p>
    </div>
    <div style={{ display: 'flex', gap: '8px' }}>
      <button
        onClick={handleExportCSV}
        className="btn btn-secondary"
        aria-label="Export organization summary as CSV"
      >
        📊 Export CSV
      </button>
      <button
        onClick={handleExportJSON}
        className="btn btn-secondary"
        aria-label="Export complete profile as JSON"
      >
        📁 Export JSON
      </button>
    </div>
  </div>
</div>
```

**Testing Checklist:**
- [ ] Click "Export CSV" button on profile page
- [ ] Verify CSV file downloads with correct data
- [ ] Open CSV in spreadsheet app, verify formatting
- [ ] Click "Export JSON" button
- [ ] Verify JSON file downloads with correct structure
- [ ] Open JSON, verify all sections included
- [ ] Test on organization with special characters
- [ ] Verify export works on mobile devices

**Estimated Time:** 15 minutes

---

### Task 3.3: Add Export for Activity List (15 min)

**Action:** Add separate export functionality for the activity list section

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/ActivityList.js`

**Implementation:**

```javascript
import { exportToCSV, generateActivitiesCSV } from '../utils/exportHelpers';

// Add in ActivityList component
const handleExportActivities = () => {
  const { activities, selectedOrganization } = useOrganizationStore.getState();
  const csvData = generateActivitiesCSV(activities);
  exportToCSV(csvData, `${selectedOrganization}_activities.csv`);
};

// Add export button above activity list
<div className="activity-list-header">
  <h2>Recent Activities</h2>
  <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
    <div className="activity-count">
      Showing {startIndex}-{endIndex} of {totalActivities} activities
    </div>
    <button
      onClick={handleExportActivities}
      className="btn btn-sm"
      aria-label="Export all activities as CSV"
    >
      📥 Export Activities
    </button>
  </div>
</div>
```

**Testing Checklist:**
- [ ] Navigate to organization profile with activities
- [ ] Click "Export Activities" button
- [ ] Verify CSV contains all activities (not just visible page)
- [ ] Check CSV has proper headers: Date, Lobbyist, Amount, Category, Description
- [ ] Test with organization having 10+ activities
- [ ] Verify pagination doesn't affect export (exports all)
- [ ] Open downloaded CSV to verify data integrity

**Estimated Time:** 15 minutes

---

### Task 3.4: Create Loading Skeleton Component (25 min)

**Action:** Build reusable loading skeleton components for data sections

**Files:**
- **CREATE**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/LoadingSkeleton.js`

**Implementation:**

```javascript
import React from 'react';
import '../styles/components/loading.css'; // Use existing loading styles

export const OrganizationHeaderSkeleton = () => (
  <div className="skeleton-header">
    <div className="skeleton-line" style={{ width: '200px', height: '40px' }} />
    <div className="skeleton-line" style={{ width: '300px', height: '20px', marginTop: '8px' }} />
  </div>
);

export const ChartSkeleton = ({ height = 350 }) => (
  <div className="skeleton-chart" style={{ height: `${height}px` }}>
    <div className="skeleton-line" style={{ width: '150px', height: '24px', marginBottom: '16px' }} />
    <div className="skeleton-rect" style={{ width: '100%', height: `${height - 50}px` }} />
  </div>
);

export const ActivityListSkeleton = ({ count = 5 }) => (
  <div className="skeleton-list">
    {Array.from({ length: count }).map((_, i) => (
      <div key={i} className="skeleton-item">
        <div className="skeleton-line" style={{ width: '60%', height: '20px' }} />
        <div className="skeleton-line" style={{ width: '80%', height: '16px', marginTop: '8px' }} />
        <div className="skeleton-line" style={{ width: '40%', height: '14px', marginTop: '8px' }} />
      </div>
    ))}
  </div>
);

export const NetworkSkeleton = ({ count = 3 }) => (
  <div className="skeleton-network">
    {Array.from({ length: count }).map((_, i) => (
      <div key={i} className="skeleton-card">
        <div style={{ display: 'flex', gap: '12px' }}>
          <div className="skeleton-circle" style={{ width: '48px', height: '48px' }} />
          <div style={{ flex: 1 }}>
            <div className="skeleton-line" style={{ width: '70%', height: '18px' }} />
            <div className="skeleton-line" style={{ width: '50%', height: '14px', marginTop: '8px' }} />
          </div>
        </div>
      </div>
    ))}
  </div>
);

// Add CSS for skeletons if not in existing loading.css
const styles = `
.skeleton-line,
.skeleton-rect,
.skeleton-circle,
.skeleton-card {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s ease-in-out infinite;
}

@keyframes skeleton-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.skeleton-line {
  border-radius: 4px;
}

.skeleton-circle {
  border-radius: 50%;
}

.skeleton-card {
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.skeleton-item {
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 12px;
}
`;
```

**Testing Checklist:**
- [ ] Import LoadingSkeleton in OrganizationProfile
- [ ] Temporarily set loading=true in organizationStore
- [ ] Verify skeleton displays correctly
- [ ] Check skeleton matches final component layout
- [ ] Test skeleton responsive on mobile (320px width)
- [ ] Verify smooth transition when data loads
- [ ] Check shimmer animation works

**Estimated Time:** 25 minutes

---

### Task 3.5: Implement Loading States in OrganizationProfile (20 min)

**Action:** Add loading states to all data sections using skeletons

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/OrganizationProfile.js`

**Implementation:**

```javascript
import {
  OrganizationHeaderSkeleton,
  ChartSkeleton,
  ActivityListSkeleton,
  NetworkSkeleton
} from './LoadingSkeleton';

// In render, add conditional loading states
if (loading) {
  return (
    <div className="page-container">
      <OrganizationHeaderSkeleton />
      <div className="page-content">
        <div className="dashboard-card">
          <ChartSkeleton />
        </div>
        <div className="profile-grid">
          <div className="profile-main">
            <ActivityListSkeleton count={5} />
          </div>
          <div className="profile-sidebar">
            <NetworkSkeleton count={3} />
          </div>
        </div>
      </div>
    </div>
  );
}

// For individual sections, wrap with loading checks
{loading ? <ChartSkeleton height={300} /> : <SpendingTrendsChart />}
{loading ? <ActivityListSkeleton /> : <ActivityList />}
{loading ? <NetworkSkeleton /> : <LobbyistNetwork />}
```

**Testing Checklist:**
- [ ] Navigate to organization profile
- [ ] Observe loading skeletons appear first
- [ ] Verify smooth transition to actual data
- [ ] Test on slow network (Chrome DevTools throttling)
- [ ] Check all sections show appropriate loading states
- [ ] Verify no layout shift when data loads (CLS)
- [ ] Test rapid navigation (skeletons should appear briefly)

**Estimated Time:** 20 minutes

---

### Task 3.6: Add Error Handling and Empty States (25 min)

**Action:** Create error messages and empty state components

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/OrganizationProfile.js`

**Implementation:**

```javascript
// Add error state component
const ErrorState = ({ error, onRetry }) => (
  <div className="page-container">
    <div className="page-header">
      <h1>Error Loading Profile</h1>
    </div>
    <div className="page-content">
      <div className="dashboard-card error-card">
        <h3>⚠️ Something Went Wrong</h3>
        <p>{error || 'An unexpected error occurred while loading the organization profile.'}</p>
        <div style={{ display: 'flex', gap: '8px', marginTop: '16px' }}>
          <button onClick={onRetry} className="btn">
            🔄 Retry
          </button>
          <button onClick={() => navigate('/search')} className="btn btn-secondary">
            ← Return to Search
          </button>
        </div>
      </div>
    </div>
  </div>
);

// Add empty state component
const EmptyState = () => (
  <div className="page-container">
    <div className="page-header">
      <h1>{decodedOrgName}</h1>
    </div>
    <div className="page-content">
      <div className="dashboard-card empty-state-card">
        <h3>📭 No Data Available</h3>
        <p>
          No lobbying activities found for this organization in the current search results.
        </p>
        <p style={{ marginTop: '12px', color: '#666', fontSize: '0.9rem' }}>
          Try performing a new search to find activities for this organization.
        </p>
        <button
          onClick={() => navigate('/search')}
          className="btn"
          style={{ marginTop: '16px' }}
        >
          Go to Search
        </button>
      </div>
    </div>
  </div>
);

// Use in component
if (error) {
  return <ErrorState error={error} onRetry={() => window.location.reload()} />;
}

if (!loading && (!activities || activities.length === 0)) {
  return <EmptyState />;
}
```

**Testing Checklist:**
- [ ] Navigate to non-existent organization URL manually
- [ ] Verify "Organization not found" message displays
- [ ] Click "Retry" button, verify data refetch
- [ ] Test with organization having no activities
- [ ] Verify empty state shows helpful message
- [ ] Test back navigation from error/empty states
- [ ] Force an error, verify error boundary catches it

**Estimated Time:** 25 minutes

---

### Task 3.7: Add ARIA Labels to Interactive Elements (20 min)

**Action:** Implement comprehensive ARIA attributes for accessibility

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/OrganizationProfile.js`
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/Search.js`

**Implementation:**

```javascript
// In OrganizationProfile.js
<div
  className="page-container"
  role="main"
  aria-label={`Organization profile for ${selectedOrganization}`}
>
  <nav className="breadcrumb" aria-label="Breadcrumb navigation">
    {/* breadcrumb items */}
  </nav>

  <button
    onClick={() => navigate('/search')}
    className="btn btn-secondary"
    aria-label="Back to search results"
  >
    ← Back to Search
  </button>

  <h1 id="org-name">{selectedOrganization}</h1>

  <div aria-live="polite" aria-busy={loading}>
    {/* Loading sections */}
  </div>

  <button
    onClick={handleExportCSV}
    className="btn btn-secondary"
    aria-label={`Export ${selectedOrganization} summary as CSV file`}
  >
    📊 Export CSV
  </button>
</div>

// In Search.js
<h4
  className="organization-link"
  onClick={() => navigate(`/organization/${encodeURIComponent(result.organization)}`)}
  role="link"
  tabIndex={0}
  aria-label={`View profile for ${result.organization}`}
  onKeyPress={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      navigate(`/organization/${encodeURIComponent(result.organization)}`);
    }
  }}
>
  {result.organization}
</h4>
```

**Testing Checklist:**
- [ ] Use Chrome Lighthouse accessibility audit
- [ ] Test with macOS VoiceOver (Cmd+F5)
- [ ] Navigate profile page with keyboard only
- [ ] Tab through all interactive elements
- [ ] Verify screen reader announces all content correctly
- [ ] Check Lighthouse accessibility score ≥95
- [ ] Test with NVDA on Windows (if available)

**Estimated Time:** 20 minutes

---

### Task 3.8: Implement Keyboard Navigation (20 min)

**Action:** Ensure full keyboard accessibility throughout profile page

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/OrganizationProfile.js`
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/App.css`

**Implementation:**

```javascript
// Add keyboard shortcuts
useEffect(() => {
  const handleKeyDown = (e) => {
    // Escape key to go back
    if (e.key === 'Escape') {
      navigate('/search');
    }
  };

  window.addEventListener('keydown', handleKeyDown);
  return () => window.removeEventListener('keydown', handleKeyDown);
}, [navigate]);

// Add skip-to-content link
<a href="#main-content" className="skip-link">
  Skip to main content
</a>

<main id="main-content" tabIndex={-1}>
  {/* Main content */}
</main>
```

**CSS for focus styles:**
```css
/* Focus indicators */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: #000;
  color: #fff;
  padding: 8px;
  text-decoration: none;
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}

*:focus-visible {
  outline: 2px solid #007bff;
  outline-offset: 2px;
}

button:focus-visible,
a:focus-visible {
  outline: 2px solid #007bff;
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(0, 123, 255, 0.1);
}
```

**Testing Checklist:**
- [ ] Tab through entire profile page
- [ ] Verify focus visible on all interactive elements
- [ ] Press Enter on organization links in search
- [ ] Press Escape on profile page (should go back)
- [ ] Use only keyboard to export data
- [ ] Verify no keyboard traps
- [ ] Test skip-to-content link appears on Tab

**Estimated Time:** 20 minutes

---

### Task 3.9: Mobile Breakpoint Optimization (30 min)

**Action:** Optimize layout for mobile devices and small screens

**Files:**
- **CREATE**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/OrganizationProfile.css`

**Implementation:**

```css
/* Mobile-first responsive design */

/* Base mobile styles (320px - 767px) */
.organization-profile {
  padding: 16px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 1.5rem;
  word-break: break-word;
  margin-bottom: 8px;
}

.export-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 16px;
}

.export-buttons button {
  width: 100%;
  min-height: 44px; /* Touch-friendly */
}

.profile-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.metrics-grid {
  grid-template-columns: 1fr;
}

/* Tablet (768px - 1023px) */
@media (min-width: 768px) {
  .organization-profile {
    padding: 24px;
  }

  .page-header h1 {
    font-size: 2rem;
  }

  .export-buttons {
    flex-direction: row;
    margin-top: 0;
  }

  .export-buttons button {
    width: auto;
  }

  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .profile-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
  }
}

/* Desktop (1024px+) */
@media (min-width: 1024px) {
  .metrics-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .profile-grid {
    grid-template-columns: 2fr 1fr;
  }
}

/* Touch-friendly elements */
button,
a,
.clickable {
  min-width: 44px;
  min-height: 44px;
  padding: 12px 16px;
}

/* Reduce chart height on mobile */
@media (max-width: 767px) {
  .spending-trends-chart {
    height: 250px !important;
  }
}
```

**Testing Checklist:**
- [ ] Test on iPhone SE (375px width) in Chrome DevTools
- [ ] Test on iPad (768px width)
- [ ] Test on desktop (1440px width)
- [ ] Rotate device to test portrait/landscape
- [ ] Verify all touch targets ≥44px
- [ ] Check chart responsiveness at all breakpoints
- [ ] Test export buttons on mobile (no overlap)
- [ ] Verify horizontal scrolling never occurs
- [ ] Test with real mobile device if available

**Estimated Time:** 30 minutes

---

### Task 3.10: Optimize Chart Rendering for Mobile (20 min)

**Action:** Make Recharts responsive and mobile-friendly

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/charts/SpendingTrendsChart.js`

**Implementation:**

```javascript
// Already using ResponsiveContainer, enhance mobile config
const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);

useEffect(() => {
  const handleResize = () => setIsMobile(window.innerWidth <= 768);
  window.addEventListener('resize', handleResize);
  return () => window.removeEventListener('resize', handleResize);
}, []);

// Adjust chart configuration for mobile
const chartConfig = isMobile ? {
  height: 250,
  margin: { top: 10, right: 10, left: 0, bottom: 40 },
  fontSize: 10,
  tickCount: 4
} : {
  height: 350,
  margin: { top: 20, right: 30, left: 20, bottom: 20 },
  fontSize: 12,
  tickCount: 8
};

<ResponsiveContainer width="100%" height={chartConfig.height}>
  <LineChart data={spendingTrends} margin={chartConfig.margin}>
    <XAxis
      dataKey="period"
      tick={{ fontSize: chartConfig.fontSize }}
      angle={isMobile ? -45 : -30}
    />
    <YAxis
      tick={{ fontSize: chartConfig.fontSize }}
      tickCount={chartConfig.tickCount}
    />
    {/* ... rest of chart */}
  </LineChart>
</ResponsiveContainer>
```

**Testing Checklist:**
- [ ] View spending chart on mobile device
- [ ] Verify chart fits viewport width
- [ ] Check all labels are readable
- [ ] Test chart interactions (tooltips) on touch devices
- [ ] Verify legend doesn't overflow on mobile
- [ ] Compare chart quality mobile vs desktop
- [ ] Test rotation (portrait/landscape)

**Estimated Time:** 20 minutes

---

### Task 3.11: Add Focus Management for Navigation (15 min)

**Action:** Implement focus management when navigating between pages

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/OrganizationProfile.js`

**Implementation:**

```javascript
// Add ref for main heading
const headingRef = useRef(null);

// Focus heading on mount
useEffect(() => {
  if (headingRef.current && !loading) {
    headingRef.current.focus();
    // Announce to screen readers
    headingRef.current.setAttribute('tabindex', '-1');
  }
}, [loading, selectedOrganization]);

// In render
<h1
  ref={headingRef}
  tabIndex={-1}
  style={{ outline: 'none' }}
>
  {selectedOrganization}
</h1>
```

**Testing Checklist:**
- [ ] Use screen reader and navigate from search to profile
- [ ] Verify heading is announced immediately
- [ ] Navigate back to search, verify focus returns correctly
- [ ] Trigger error state, verify focus moves to error
- [ ] Test with keyboard navigation only
- [ ] Verify focus doesn't show visible outline on heading

**Estimated Time:** 15 minutes

---

### Task 3.12: Performance Optimization - Code Splitting (20 min)

**Action:** Implement lazy loading for OrganizationProfile component

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/App.js`

**Implementation:**

```javascript
import React, { lazy, Suspense } from 'react';

// Convert to lazy import
const OrganizationProfile = lazy(() => import('./components/OrganizationProfile'));

// In routes
<Route
  path="/organization/:organizationName"
  element={
    <Suspense fallback={<LoadingSpinner />}>
      <OrganizationProfile />
    </Suspense>
  }
/>
```

**Testing Checklist:**
- [ ] Run production build: `npm run build`
- [ ] Check build output for code splitting (multiple JS chunks)
- [ ] Verify OrganizationProfile.chunk.js is separate
- [ ] Test navigation delay (should be minimal)
- [ ] Check Network tab in DevTools for lazy loading
- [ ] Verify fallback loading state displays briefly
- [ ] Check bundle sizes are reasonable

**Estimated Time:** 20 minutes

---

### Task 3.13: Performance Optimization - Memoization (25 min)

**Action:** Add React.memo and useMemo for expensive calculations

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/OrganizationProfile.js`

**Implementation:**

```javascript
// Wrap expensive calculations in useMemo
const aggregatedData = useMemo(() => {
  if (!results.length) return null;
  return {
    metrics: aggregateOrganizationMetrics(orgActivities),
    lobbyists: extractLobbyistNetwork(orgActivities),
    trends: calculateSpendingTrends(orgActivities, 'quarter'),
    related: findRelatedOrganizations(decodedOrgName, results, 5)
  };
}, [results, decodedOrgName]);

// Memoize export handlers
const handleExportCSV = useCallback(() => {
  const summaryData = generateOrganizationSummaryCSV({
    selectedOrganization,
    organizationData,
    lobbyists
  });
  exportToCSV([summaryData], `${selectedOrganization}_summary.csv`);
}, [selectedOrganization, organizationData, lobbyists]);

// Wrap child components
const ActivitySummary = React.memo(ActivitySummaryComponent);
const LobbyistNetwork = React.memo(LobbyistNetworkComponent);
```

**Testing Checklist:**
- [ ] Use React DevTools Profiler
- [ ] Navigate to organization profile
- [ ] Check component re-renders (should minimize)
- [ ] Change organization, verify only necessary components update
- [ ] Verify export functions don't cause re-renders
- [ ] Profile rendering time (should be <100ms)
- [ ] Check memory usage doesn't increase on navigation

**Estimated Time:** 25 minutes

---

### Task 3.14: Cross-Browser Testing (30 min)

**Action:** Test feature in Chrome, Safari, Firefox, and mobile browsers

**Testing Checklist:**

**Chrome Desktop:**
- [ ] Profile page loads and displays correctly
- [ ] Export CSV/JSON works
- [ ] Charts render properly
- [ ] Keyboard navigation works
- [ ] DevTools console shows no errors

**Safari Desktop:**
- [ ] Same as Chrome tests
- [ ] Focus styles visible
- [ ] Export downloads work
- [ ] Chart animations smooth

**Firefox Desktop:**
- [ ] Same as Chrome tests
- [ ] ARIA attributes working with NVDA screen reader
- [ ] Performance acceptable

**Chrome Mobile (iOS):**
- [ ] Layout responsive
- [ ] Touch interactions work (44px targets)
- [ ] Export works on mobile
- [ ] Charts render correctly
- [ ] No horizontal scrolling

**Safari Mobile (iOS):**
- [ ] Same as Chrome mobile tests
- [ ] VoiceOver compatibility
- [ ] Smooth scrolling

**Estimated Time:** 30 minutes

---

### Task 3.15: Production Build and Pre-Deployment Testing (20 min)

**Action:** Create production build and test locally before deployment

**Commands:**
```bash
# Run production build
npm run build

# Check build output
ls -lh build/static/js/

# Test production build locally
npx serve -s build

# Or test with Vercel CLI
vercel dev
```

**Testing Checklist:**
- [ ] Build completes without errors or warnings
- [ ] Check bundle size (main chunk should be <500KB)
- [ ] Test production build locally at http://localhost:3000
- [ ] Verify no console errors in production mode
- [ ] Check all environment variables are set
- [ ] Test all critical paths in production build
- [ ] Verify source maps are generated (for debugging)
- [ ] Check performance in Lighthouse (production mode)

**Estimated Time:** 20 minutes

---

### Task 3.16: Deploy to Vercel Staging (15 min)

**Action:** Deploy to Vercel preview environment for final testing

**Commands:**
```bash
# Commit changes
git add .
git commit -m "Feature: Organization Profile Page - Phase 3 complete

- Export functionality (CSV/JSON)
- Loading states and error handling
- Mobile-responsive optimization
- Accessibility improvements (ARIA, keyboard nav)
- Performance optimizations (lazy loading, memoization)
- Cross-browser tested

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to trigger Vercel preview
git push origin [current-branch]
```

**Testing Checklist:**
- [ ] Wait for Vercel preview deployment to complete
- [ ] Click preview URL from Vercel dashboard
- [ ] Test full user flow: search → click org → view profile → export
- [ ] Verify all features work in preview
- [ ] Check Vercel logs for any runtime errors
- [ ] Test on real mobile device using preview URL
- [ ] Share preview link for feedback (if needed)
- [ ] Verify build time is reasonable (<5 minutes)

**Estimated Time:** 15 minutes

---

### Task 3.17: Production Deployment (10 min)

**Action:** Merge to main branch and deploy to production

**Commands:**
```bash
# Merge to main for production deployment
git checkout main
git merge [feature-branch]
git push origin main

# Vercel auto-deploys main branch to production
```

**Testing Checklist:**
- [ ] Verify production deployment succeeds in Vercel dashboard
- [ ] Visit production URL: https://ca-lobby-webapp.vercel.app
- [ ] Test critical user flows in production
- [ ] Monitor Vercel analytics for first 30 minutes
- [ ] Check error tracking (if configured)
- [ ] Verify no 404 errors for new routes
- [ ] Test from multiple geographic locations if possible
- [ ] Verify HTTPS certificate is valid

**Estimated Time:** 10 minutes

---

### Task 3.18: Post-Deployment Monitoring (15 min)

**Action:** Monitor production deployment and verify health

**Monitoring Checklist:**
- [ ] Monitor Vercel dashboard for errors (first hour)
- [ ] Check Web Vitals scores in Vercel Analytics:
  - LCP (Largest Contentful Paint) < 2.5s
  - FID (First Input Delay) < 100ms
  - CLS (Cumulative Layout Shift) < 0.1
- [ ] Verify no spike in error rates
- [ ] Check function execution logs
- [ ] Monitor bandwidth usage
- [ ] Test from different devices and networks
- [ ] Review user feedback channels
- [ ] Document any post-deployment issues

**Estimated Time:** 15 minutes

---

### Task 3.19: Accessibility Audit with Lighthouse (15 min)

**Action:** Run comprehensive Lighthouse audit and fix any issues

**Audit Procedure:**
1. Open production site in Chrome
2. Open DevTools → Lighthouse tab
3. Select: Performance, Accessibility, Best Practices, SEO
4. Run audit in incognito mode
5. Fix any issues with score <90

**Target Scores:**
- [ ] Accessibility score ≥95
- [ ] Performance score ≥80 (mobile)
- [ ] Performance score ≥90 (desktop)
- [ ] Best Practices score ≥90
- [ ] SEO score ≥90

**Common Issues to Check:**
- [ ] All images have alt text
- [ ] Color contrast ratios meet WCAG AA
- [ ] Form inputs have associated labels
- [ ] Links have discernible text
- [ ] Tap targets are appropriately sized
- [ ] Page has a `<title>` element

**Estimated Time:** 15 minutes

---

### Task 3.20: Update Documentation (15 min)

**Action:** Document the feature for future developers and update project docs

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/CLAUDE.md`
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/Documentation/General/MASTER_PROJECT_PLAN.md`

**Updates to CLAUDE.md:**
```markdown
## 🔧 Common Tasks

### Organization Profile Feature
Navigate to organization profiles by clicking organization names in search results.

**URL Pattern**: `/organization/:organizationName`

**Features**:
- Comprehensive statistics and metrics
- Spending trends visualization
- Paginated activity list
- Lobbyist network display
- Related organizations
- Export to CSV/JSON

**Testing**:
```bash
# Run development server
npm start

# Navigate to search, click organization name
# Or access directly:
# http://localhost:3000/organization/California%20Medical%20Association
```
```

**Updates to MASTER_PROJECT_PLAN.md:**
```markdown
#### Phase 2f: Organization Profile Page ✅ COMPLETED
**Duration:** October 1-3, 2025 (3 days)
**Status:** ✅ COMPLETED

**Deliverables Achieved:**
- ✅ Clickable organization links in search
- ✅ Organization profile pages with comprehensive data
- ✅ Spending trends visualization with Recharts
- ✅ Paginated activity list (10 items/page)
- ✅ Lobbyist network display
- ✅ Related organizations based on similarity
- ✅ Export functionality (CSV/JSON)
- ✅ Accessibility compliance (WCAG 2.1 AA)
- ✅ Mobile-responsive design
- ✅ Performance optimizations

**Reference Documents:**
- **Phase 1 Plan**: [`Documentation/Phase2/Plans/ORGANIZATION_PROFILE_PHASE1_PLAN.md`](Documentation/Phase2/Plans/ORGANIZATION_PROFILE_PHASE1_PLAN.md)
- **Phase 2 Plan**: [`Documentation/Phase2/Plans/ORGANIZATION_PROFILE_PHASE2_PLAN.md`](Documentation/Phase2/Plans/ORGANIZATION_PROFILE_PHASE2_PLAN.md)
- **Phase 3 Plan**: [`Documentation/Phase2/Plans/ORGANIZATION_PROFILE_PHASE3_PLAN.md`](Documentation/Phase2/Plans/ORGANIZATION_PROFILE_PHASE3_PLAN.md)
- **Completion Report**: [`Documentation/Phase2/Reports/ORGANIZATION_PROFILE_COMPLETION_REPORT.md`](Documentation/Phase2/Reports/ORGANIZATION_PROFILE_COMPLETION_REPORT.md)
```

**Estimated Time:** 15 minutes

---

## 📊 Phase 3 Summary

### Time Breakdown
- **Export Functionality** (Tasks 3.1-3.3): ~50 minutes
- **Loading & Error States** (Tasks 3.4-3.6): ~70 minutes
- **Accessibility** (Tasks 3.7-3.8, 3.11): ~55 minutes
- **Mobile Optimization** (Tasks 3.9-3.10): ~50 minutes
- **Performance** (Tasks 3.12-3.13): ~45 minutes
- **Testing & Deployment** (Tasks 3.14-3.20): ~120 minutes

**Total Estimated Time:** 4-6 hours

### Key Deliverables
1. ✅ CSV and JSON export functionality
2. ✅ Loading skeleton components
3. ✅ Error handling and empty states
4. ✅ ARIA labels and keyboard navigation
5. ✅ Mobile-responsive optimization
6. ✅ Chart mobile optimization
7. ✅ Focus management
8. ✅ Code splitting and lazy loading
9. ✅ React.memo and useMemo optimizations
10. ✅ Cross-browser testing
11. ✅ Production deployment
12. ✅ Lighthouse accessibility audit
13. ✅ Documentation updates

### Files Created
- `/Users/michaelingram/Documents/GitHub/CA_lobby/src/utils/exportHelpers.js`
- `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/LoadingSkeleton.js`
- `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/OrganizationProfile.css`

### Files Modified
- `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/OrganizationProfile.js`
- `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/ActivityList.js`
- `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/Search.js`
- `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/charts/SpendingTrendsChart.js`
- `/Users/michaelingram/Documents/GitHub/CA_lobby/src/App.js`
- `/Users/michaelingram/Documents/GitHub/CA_lobby/src/App.css`
- `/Users/michaelingram/Documents/GitHub/CA_lobby/CLAUDE.md`
- `/Users/michaelingram/Documents/GitHub/CA_lobby/Documentation/General/MASTER_PROJECT_PLAN.md`

### Success Criteria Met
- [ ] Export downloads work for CSV and JSON formats
- [ ] Loading states prevent layout shift (CLS < 0.1)
- [ ] Lighthouse accessibility score ≥95
- [ ] Mobile experience is touch-friendly (44px targets)
- [ ] Page load time <2 seconds on 3G
- [ ] Production deployment succeeds without errors

### Production Metrics
- **Bundle Size**: <500KB main chunk
- **Lighthouse Scores**:
  - Performance: 80+ (mobile), 90+ (desktop)
  - Accessibility: 95+
  - Best Practices: 90+
  - SEO: 90+
- **Web Vitals**:
  - LCP: <2.5s
  - FID: <100ms
  - CLS: <0.1

---

## 🎉 Feature Complete

The Organization Profile Page feature is now production-ready with:
- ✅ Full functionality (search, navigation, display)
- ✅ Export capabilities (CSV/JSON)
- ✅ Accessibility compliance (WCAG 2.1 AA)
- ✅ Mobile optimization
- ✅ Performance optimizations
- ✅ Production deployment
- ✅ Comprehensive testing
- ✅ Documentation updates

---

**Last Updated:** September 30, 2025
**Status:** Pending (Awaits Phase 2 completion)
**Next Review:** After Phase 3 completion and production deployment