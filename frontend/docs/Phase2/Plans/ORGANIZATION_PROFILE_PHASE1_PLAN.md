# Organization Profile Page - Phase 1 Implementation Plan
## Basic Profile Page Foundation

**Project:** California Lobby Search System
**Project Code:** CA_LOBBY
**Phase:** 2f.1 - Organization Profile Foundation
**Duration:** Day 1 (6-8 hours)
**Start Date:** September 30, 2025
**Status:** 🎯 READY TO START

---

## 📋 Phase 1 Overview

Create the foundational structure for organization profile pages including:
- Clickable organization links in search results
- Basic profile page with routing
- Organization data filtering and display
- Navigation between search and profile pages

**Important Note:** Phase 1 focuses on demo data only. Backend API integration will be addressed in future phases. The organization profile page will filter and display data from the existing Zustand searchStore results.

---

## 🎯 Phase 1 Objectives

### Primary Goals
1. ✅ Create OrganizationProfile component with React Router integration
2. ✅ Make organization names clickable in search results
3. ✅ Display basic organization information on profile page
4. ✅ Implement navigation breadcrumbs and back buttons
5. ✅ Show filtered activities for selected organization

### Success Criteria
- [ ] Organization names in search results are clickable
- [ ] Clicking org name navigates to `/organization/:organizationName`
- [ ] Profile page displays organization details
- [ ] Basic statistics show (total spending, activity count, lobbyists)
- [ ] Navigation back to search works seamlessly
- [ ] No regressions in existing search functionality

---

## 📊 Prerequisites

### ✅ Infrastructure Ready
- React Router DOM v6.8.0 installed
- Zustand stores operational (searchStore, userStore, appStore)
- Search component with demo data
- Existing CSS framework and components

### ✅ Required Knowledge
- React functional components and hooks
- React Router v6 navigation
- Zustand state management patterns
- CSS styling conventions

---

## 🏗️ Implementation Tasks

### Task 1.1: Create OrganizationProfile Component Foundation (20 min)

**Action:** Create the basic OrganizationProfile component file with component structure and imports

**Files:**
- **CREATE**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/OrganizationProfile.js`

**Implementation:**
```javascript
import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSearchStore } from '../stores';

function OrganizationProfile() {
  const { organizationName } = useParams();
  const navigate = useNavigate();

  return (
    <div className="page-container">
      <div className="page-header">
        <button
          onClick={() => navigate('/search')}
          className="btn btn-secondary"
          style={{ marginBottom: '16px' }}
        >
          ← Back to Search
        </button>
        <h1>{decodeURIComponent(organizationName)}</h1>
        <p className="page-description">Organization Profile</p>
      </div>
      <div className="page-content">
        <p>Profile content will go here</p>
      </div>
    </div>
  );
}

export default OrganizationProfile;
```

**Testing Checklist:**
- [ ] File created successfully at correct path
- [ ] No syntax errors (run `npm start` and check console)
- [ ] Component imports are correct
- [ ] File follows project naming conventions

**Estimated Time:** 20 minutes

---

### Task 1.2: Add React Router Route for Organization Profile (15 min)

**Action:** Register the new route in App.js

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/App.js`

**Implementation:**

1. Add import after the Settings component import (look for `import Settings from './components/Settings';`):
```javascript
import OrganizationProfile from './components/OrganizationProfile';
```

2. Add route at line 108 (after settings route, before closing Routes tag):
```javascript
<Route path="/organization/:organizationName" element={<OrganizationProfile />} />
```

**Testing Checklist:**
- [ ] Navigate manually to `http://localhost:3000/organization/TestOrg`
- [ ] Verify OrganizationProfile component renders
- [ ] Verify "Back to Search" button is visible
- [ ] Click back button, verify navigation to /search works
- [ ] Check browser console for routing errors
- [ ] Test with URL parameters containing spaces: `/organization/Test%20Org`

**Estimated Time:** 15 minutes

---

### Task 1.3: Make Organization Names Clickable in Search Results (25 min)

**Action:** Convert organization names in search results to clickable links

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/Search.js`

**Implementation:**

1. Add import at line 2 (update existing import):
```javascript
import { useSearchStore } from '../stores';
import { useNavigate } from 'react-router-dom';
```

2. Add navigate hook after store destructuring (around line 123):
```javascript
const navigate = useNavigate();
```

3. Replace the result item h4 tag (line 363) with clickable organization name:
```javascript
<h4
  onClick={() => navigate(`/organization/${encodeURIComponent(result.organization)}`)}
  style={{
    cursor: 'pointer',
    color: '#007bff',
    textDecoration: 'underline'
  }}
>
  {result.organization || result.lobbyist || 'Lobby Entry'}
</h4>
```

**Testing Checklist:**
- [ ] Run a search (any query or filters)
- [ ] Click on an organization name in results
- [ ] Verify navigation to organization profile page
- [ ] Verify organization name displays correctly in URL and header
- [ ] Test with organization names containing special characters (spaces, ampersands)
- [ ] Test with organization names with single quote: "John's Association"
- [ ] Verify clicking same org multiple times works correctly
- [ ] Test keyboard navigation (Tab to focus, Enter to navigate)
- [ ] Test with screen reader (organization name announced correctly)

**Estimated Time:** 25 minutes

---

### Task 1.4: Add CSS Styles for Clickable Organization Names (15 min)

**Action:** Add hover effects and proper styling for organization links

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/App.css`

**Implementation:**

Add after line 505 (after .result-meta):
```css
/* Organization Link Styles */
.result-item h4.organization-link {
  cursor: pointer;
  color: var(--color-primary-600);
  transition: all 0.2s ease;
  text-decoration: none;
  border-bottom: 2px solid transparent;
}

.result-item h4.organization-link:hover {
  color: var(--color-primary-700);
  border-bottom: 2px solid var(--color-primary-500);
  transform: translateX(4px);
}

.result-item h4.organization-link:active {
  transform: translateX(2px);
}
```

**Testing Checklist:**
- [ ] Hover over organization names in search results
- [ ] Verify smooth color transition and underline animation
- [ ] Verify visual feedback on click (transform animation)
- [ ] Test in both light and dark themes (if applicable)
- [ ] Test on touch devices (hover states should not stick)

**Estimated Time:** 15 minutes

---

### Task 1.5: Update Search.js to Use CSS Class (10 min)

**Action:** Replace inline styles with CSS class from Task 1.4

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/Search.js`

**Implementation:**

Replace the h4 tag from Task 1.3 (around line 363) with:
```javascript
<h4
  className="organization-link"
  onClick={() => navigate(`/organization/${encodeURIComponent(result.organization)}`)}
>
  {result.organization || result.lobbyist || 'Lobby Entry'}
</h4>
```

**Testing Checklist:**
- [ ] Verify styling still works after class change
- [ ] Verify hover effects match design
- [ ] Verify click navigation still works
- [ ] Compare before/after behavior (should be identical)

**Estimated Time:** 10 minutes

---

### Task 1.6: Filter Search Results for Selected Organization (30 min)

**Action:** Display organization-specific data on profile page by filtering search results

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/OrganizationProfile.js`

**Implementation:**

Replace component content:
```javascript
import React, { useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSearchStore } from '../stores';

function OrganizationProfile() {
  const { organizationName } = useParams();
  const navigate = useNavigate();
  const { results } = useSearchStore();

  const decodedOrgName = decodeURIComponent(organizationName);

  // Filter results for this organization
  const organizationData = useMemo(() => {
    return results.filter(
      result => result.organization === decodedOrgName
    );
  }, [results, decodedOrgName]);

  return (
    <div className="page-container">
      <div className="page-header">
        <button
          onClick={() => navigate('/search')}
          className="btn btn-secondary"
          style={{ marginBottom: '16px' }}
        >
          ← Back to Search
        </button>
        <h1>{decodedOrgName}</h1>
        <p className="page-description">
          {organizationData.length} lobbying {organizationData.length === 1 ? 'activity' : 'activities'} found
        </p>
      </div>

      <div className="page-content">
        <div className="dashboard-card">
          <h3>Recent Activities</h3>
          {organizationData.length === 0 ? (
            <p>No data available for this organization. Try searching first.</p>
          ) : (
            <div className="result-preview">
              {organizationData.map((activity, index) => (
                <div key={index} className="result-item">
                  <h4>{activity.lobbyist || 'Unknown Lobbyist'}</h4>
                  <p>{activity.description || activity.activity_description}</p>
                  <span className="result-meta">
                    Amount: ${activity.amount?.toLocaleString() || 'N/A'} |
                    Date: {activity.date || activity.filing_date || 'N/A'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default OrganizationProfile;
```

**Testing Checklist:**
- [ ] Run a search that returns multiple organizations
- [ ] Click on "California Medical Association"
- [ ] Verify only activities for that organization display
- [ ] Verify count in description is correct
- [ ] Navigate back and click different organization
- [ ] Verify data updates correctly
- [ ] Test with organization having 0 activities
- [ ] Test with organization having 1 activity (singular "activity")

**Estimated Time:** 30 minutes

---

### Task 1.7: Add Basic Statistics Card (25 min)

**Action:** Calculate and display summary statistics for the organization

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/OrganizationProfile.js`

**Implementation:**

1. Add calculations after organizationData useMemo (around line 19):
```javascript
// Calculate statistics
const stats = useMemo(() => {
  if (organizationData.length === 0) return null;

  const totalAmount = organizationData.reduce((sum, item) => sum + (item.amount || 0), 0);
  const avgAmount = totalAmount / organizationData.length;
  const uniqueLobbyists = new Set(organizationData.map(item => item.lobbyist)).size;
  const categories = [...new Set(organizationData.map(item => item.category))];

  return {
    totalAmount,
    avgAmount,
    activityCount: organizationData.length,
    uniqueLobbyists,
    categories
  };
}, [organizationData]);
```

2. Add statistics card before "Recent Activities" card (around line 37):
```javascript
{stats && (
  <div className="dashboard-card">
    <h3>Summary Statistics</h3>
    <div className="placeholder-content">
      <ul style={{ listStyle: 'none', padding: 0 }}>
        <li><strong>Total Activities:</strong> {stats.activityCount}</li>
        <li><strong>Total Amount:</strong> ${stats.totalAmount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</li>
        <li><strong>Average Amount:</strong> ${stats.avgAmount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</li>
        <li><strong>Unique Lobbyists:</strong> {stats.uniqueLobbyists}</li>
        <li><strong>Categories:</strong> {stats.categories.join(', ') || 'N/A'}</li>
      </ul>
    </div>
  </div>
)}
```

**Testing Checklist:**
- [ ] Navigate to an organization profile
- [ ] Verify statistics calculate correctly
- [ ] Verify currency formatting is correct (commas, 2 decimals)
- [ ] Verify categories display as comma-separated list
- [ ] Test with organization that has only 1 activity
- [ ] Test with organization that has no data (stats should not render)
- [ ] Test with activities missing amount field
- [ ] Test with activities missing category field

**Estimated Time:** 25 minutes

---

### Task 1.8: Add Grid Layout for Profile Cards (15 min)

**Action:** Organize profile page content in responsive grid

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/OrganizationProfile.js`

**Implementation:**

Wrap the dashboard cards in a grid container (around line 35):
```javascript
<div className="page-content">
  <div className="dashboard-grid">
    {stats && (
      <div className="dashboard-card">
        {/* Statistics content from Task 1.7 */}
      </div>
    )}

    <div className="dashboard-card" style={{ gridColumn: '1 / -1' }}>
      <h3>Recent Activities</h3>
      {/* Activities content from Task 1.6 */}
    </div>
  </div>
</div>
```

**Testing Checklist:**
- [ ] Verify cards display in grid layout on desktop
- [ ] Verify responsive behavior on mobile (cards stack)
- [ ] Verify "Recent Activities" card spans full width
- [ ] Test at different screen widths (320px, 768px, 1200px)
- [ ] Verify no horizontal scrolling at any width
- [ ] Check grid gap spacing is consistent

**Estimated Time:** 15 minutes

---

### Task 1.9: Add Demo Data Generator for Organization Profiles (20 min)

**Action:** Generate additional demo data for richer organization profiles

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/Search.js`

**Implementation:**

Update generateDemoSearchResults function (line 6-107) to include more varied data per organization:
```javascript
const generateDemoSearchResults = (query, filters) => {
  const demoData = [
    // California Medical Association entries
    {
      organization: 'California Medical Association',
      lobbyist: 'John Smith',
      description: 'Healthcare legislation advocacy and medical professional representation',
      amount: 125000,
      date: '2024-09-15',
      filing_date: '2024-09-15',
      category: 'healthcare',
      activity_description: 'Lobbying activities related to healthcare reform and medical licensing'
    },
    {
      organization: 'California Medical Association',
      lobbyist: 'Dr. Maria Garcia',
      description: 'Telemedicine policy advocacy and physician licensing reform',
      amount: 87500,
      date: '2024-08-20',
      filing_date: '2024-08-20',
      category: 'healthcare',
      activity_description: 'Remote healthcare delivery and cross-state licensing advocacy'
    },
    {
      organization: 'California Medical Association',
      lobbyist: 'Robert Thompson',
      description: 'Medical liability reform and insurance regulation',
      amount: 65000,
      date: '2024-07-10',
      filing_date: '2024-07-10',
      category: 'healthcare',
      activity_description: 'Tort reform and medical malpractice insurance legislation'
    },
    // Tech Innovation Coalition entries
    {
      organization: 'Tech Innovation Coalition',
      lobbyist: 'Sarah Johnson',
      description: 'Technology policy development and regulatory advocacy',
      amount: 89000,
      date: '2024-09-10',
      filing_date: '2024-09-10',
      category: 'technology',
      activity_description: 'Advocacy for technology innovation policies and startup support'
    },
    {
      organization: 'Tech Innovation Coalition',
      lobbyist: 'Kevin Zhang',
      description: 'AI regulation and data privacy policy',
      amount: 95000,
      date: '2024-08-15',
      filing_date: '2024-08-15',
      category: 'technology',
      activity_description: 'Artificial intelligence ethics and consumer data protection'
    },
    // Environmental Defense Alliance entries
    {
      organization: 'Environmental Defense Alliance',
      lobbyist: 'Michael Chen',
      description: 'Environmental protection and climate change policy advocacy',
      amount: 67500,
      date: '2024-09-05',
      filing_date: '2024-09-05',
      category: 'environment',
      activity_description: 'Climate change legislation and environmental protection lobbying'
    },
    {
      organization: 'Environmental Defense Alliance',
      lobbyist: 'Jennifer Martinez',
      description: 'Renewable energy development and green infrastructure',
      amount: 72000,
      date: '2024-08-01',
      filing_date: '2024-08-01',
      category: 'environment',
      activity_description: 'Clean energy transition and sustainable infrastructure investment'
    },
    {
      organization: 'Education Reform Society',
      lobbyist: 'Emily Rodriguez',
      description: 'Public education policy and funding advocacy',
      amount: 52000,
      date: '2024-08-28',
      filing_date: '2024-08-28',
      category: 'education',
      activity_description: 'Educational funding and policy reform advocacy'
    },
    {
      organization: 'Small Business Coalition',
      lobbyist: 'David Wilson',
      description: 'Small business interests and regulatory reform',
      amount: 43200,
      date: '2024-08-20',
      filing_date: '2024-08-20',
      category: 'finance',
      activity_description: 'Small business regulatory relief and economic development'
    }
  ];

  // Existing filter logic stays the same...
  return demoData.filter(item => {
    // ... existing filter code from line 61-106
  }).slice(0, 20); // Increase limit to 20 results
};
```

**Note:** This is a significant restructuring of demo data. Take time to test multiple activities per organization thoroughly.

**Testing Checklist:**
- [ ] Search for "California Medical Association"
- [ ] Click on organization name
- [ ] Verify multiple activities display (3 entries)
- [ ] Verify statistics show correct totals
- [ ] Repeat for "Tech Innovation Coalition" and "Environmental Defense Alliance"
- [ ] Verify different lobbyists show for same organization
- [ ] Test that filtering still works correctly

**Estimated Time:** 30 minutes

---

### Task 1.10: Add Category Badge Display (20 min)

**Action:** Display category as a colored badge in activity items

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/App.css`
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/OrganizationProfile.js`

**Implementation:**

**Changes to App.css** (add after line 505):
```css
/* Category Badge Styles */
.category-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  margin-right: 8px;
  white-space: nowrap;
}

.category-badge.healthcare {
  background-color: #e3f2fd;
  color: #1565c0;
}

.category-badge.technology {
  background-color: #f3e5f5;
  color: #6a1b9a;
}

.category-badge.environment {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.category-badge.education {
  background-color: #fff3e0;
  color: #e65100;
}

.category-badge.finance {
  background-color: #fce4ec;
  color: #c2185b;
}

.category-badge.default {
  background-color: #f5f5f5;
  color: #616161;
}
```

**Changes to OrganizationProfile.js** (update activity display):
```javascript
// Helper function at top of component
const getCategoryClass = (category) => {
  const normalizedCategory = category?.toLowerCase() || 'default';
  return `category-badge ${normalizedCategory}`;
};

// Update activity item display (in the map function):
<div key={index} className="result-item">
  <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
    <span className={getCategoryClass(activity.category)}>
      {activity.category || 'Other'}
    </span>
    <h4 style={{ margin: 0, display: 'inline' }}>
      {activity.lobbyist || 'Unknown Lobbyist'}
    </h4>
  </div>
  <p>{activity.description || activity.activity_description}</p>
  <span className="result-meta">
    Amount: ${activity.amount?.toLocaleString() || 'N/A'} |
    Date: {activity.date || activity.filing_date || 'N/A'}
  </span>
</div>
```

**Testing Checklist:**
- [ ] Navigate to organization profile
- [ ] Verify each activity shows colored category badge
- [ ] Verify colors match category (blue for healthcare, purple for tech, etc.)
- [ ] Verify badges are readable and properly styled
- [ ] Test with activity that has no category (should show "Other" with default gray)
- [ ] Test badge display on mobile devices
- [ ] Verify badge doesn't wrap to multiple lines

**Estimated Time:** 20 minutes

---

### Task 1.11: Add Sort Options for Activities (25 min)

**Action:** Add ability to sort activities by date or amount

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/OrganizationProfile.js`

**Implementation:**

1. Add state for sort option (after organizationData useMemo):
```javascript
const [sortBy, setSortBy] = React.useState('date-desc'); // date-desc, date-asc, amount-desc, amount-asc
```

2. Add sorting logic:
```javascript
const sortedActivities = useMemo(() => {
  const sorted = [...organizationData];

  switch(sortBy) {
    case 'date-desc':
      return sorted.sort((a, b) => new Date(b.date) - new Date(a.date));
    case 'date-asc':
      return sorted.sort((a, b) => new Date(a.date) - new Date(b.date));
    case 'amount-desc':
      return sorted.sort((a, b) => (b.amount || 0) - (a.amount || 0));
    case 'amount-asc':
      return sorted.sort((a, b) => (a.amount || 0) - (b.amount || 0));
    default:
      return sorted;
  }
}, [organizationData, sortBy]);
```

3. Add sort controls before activities list:
```javascript
<div className="dashboard-card" style={{ gridColumn: '1 / -1' }}>
  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
    <h3 style={{ margin: 0 }}>Recent Activities</h3>
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <label htmlFor="sort-select" style={{ fontSize: '0.9rem', color: '#666' }}>
        Sort by:
      </label>
      <select
        id="sort-select"
        value={sortBy}
        onChange={(e) => setSortBy(e.target.value)}
        style={{
          padding: '6px 12px',
          borderRadius: '4px',
          border: '1px solid #ddd',
          fontSize: '0.9rem'
        }}
      >
        <option value="date-desc">Date (Newest First)</option>
        <option value="date-asc">Date (Oldest First)</option>
        <option value="amount-desc">Amount (Highest First)</option>
        <option value="amount-asc">Amount (Lowest First)</option>
      </select>
    </div>
  </div>
  {/* Use sortedActivities instead of organizationData in map */}
  {sortedActivities.length === 0 ? (
    // ... no data message
  ) : (
    <div className="result-preview">
      {sortedActivities.map((activity, index) => (
        // ... activity display
      ))}
    </div>
  )}
</div>
```

**Testing Checklist:**
- [ ] Navigate to organization with multiple activities
- [ ] Change sort to "Date (Oldest First)" - verify order changes
- [ ] Change to "Amount (Highest First)" - verify highest amount appears first
- [ ] Change to "Amount (Lowest First)" - verify lowest amount appears first
- [ ] Change back to "Date (Newest First)" - verify default order restored
- [ ] Test with activities having same date (should maintain stable sort)
- [ ] Test sort persistence when navigating away and back

**Estimated Time:** 25 minutes

---

### Task 1.12: Add Direct Navigation from Search to Profile (15 min)

**Action:** Ensure smooth navigation and state preservation

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/Search.js`

**Implementation:**

Update organization click handler to ensure data is available (around line 363):
```javascript
<h4
  className="organization-link"
  onClick={() => {
    // Ensure this result is in the store
    console.log('Navigating to profile for:', result.organization);
    navigate(`/organization/${encodeURIComponent(result.organization)}`);
  }}
>
  {result.organization || result.lobbyist || 'Lobby Entry'}
</h4>
```

**Testing Checklist:**
- [ ] Perform search
- [ ] Click organization name
- [ ] Verify navigation is immediate (no delay)
- [ ] Check browser console for navigation log
- [ ] Verify URL updates correctly
- [ ] Use browser back button, verify returns to search with results intact
- [ ] Test rapid clicking (should not cause errors)
- [ ] Verify state persists across navigation

**Estimated Time:** 15 minutes

---

### Task 1.13: Add Loading State for Profile Page (15 min)

**Action:** Show loading indicator when no data available yet

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/OrganizationProfile.js`

**Implementation:**

Add conditional rendering for empty results state:
```javascript
const { results, loading } = useSearchStore();

// Add early return for no data
if (results.length === 0 && !loading) {
  return (
    <div className="page-container">
      <div className="page-header">
        <button
          onClick={() => navigate('/search')}
          className="btn btn-secondary"
          style={{ marginBottom: '16px' }}
        >
          ← Back to Search
        </button>
        <h1>{decodedOrgName}</h1>
      </div>
      <div className="page-content">
        <div className="dashboard-card">
          <h3>No Data Available</h3>
          <p>
            Please perform a search first to view organization data.
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
}
```

**Testing Checklist:**
- [ ] Clear browser cache and reload
- [ ] Navigate directly to `/organization/TestOrg` without searching
- [ ] Verify "No Data Available" message displays
- [ ] Click "Go to Search" button
- [ ] Verify navigation to search page
- [ ] Perform search, then navigate to profile
- [ ] Verify profile loads correctly with data
- [ ] Test loading state displays properly

**Estimated Time:** 15 minutes

---

### Task 1.14: Add Breadcrumb Navigation (20 min)

**Action:** Add breadcrumb trail for better navigation context

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/App.css`
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/OrganizationProfile.js`

**Implementation:**

**Changes to App.css** (add after line 274):
```css
/* Breadcrumb Navigation */
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  flex-wrap: wrap;
}

.breadcrumb-link {
  color: var(--color-primary-600);
  text-decoration: none;
  cursor: pointer;
  transition: color 0.2s ease;
}

.breadcrumb-link:hover {
  color: var(--color-primary-700);
  text-decoration: underline;
}

.breadcrumb-separator {
  color: var(--color-text-secondary);
  user-select: none;
}

.breadcrumb-current {
  color: var(--color-text-primary);
  font-weight: 500;
}
```

**Changes to OrganizationProfile.js** (add before page header):
```javascript
<div className="page-container">
  <div className="breadcrumb">
    <span
      className="breadcrumb-link"
      onClick={() => navigate('/')}
    >
      Home
    </span>
    <span className="breadcrumb-separator">/</span>
    <span
      className="breadcrumb-link"
      onClick={() => navigate('/search')}
    >
      Search
    </span>
    <span className="breadcrumb-separator">/</span>
    <span className="breadcrumb-current">{decodedOrgName}</span>
  </div>

  <div className="page-header">
    {/* existing header content */}
  </div>
  {/* rest of component */}
</div>
```

**Testing Checklist:**
- [ ] Navigate to organization profile
- [ ] Verify breadcrumb displays: "Home / Search / [Organization Name]"
- [ ] Click "Home" - verify navigation to dashboard
- [ ] Navigate back to profile
- [ ] Click "Search" - verify navigation to search page
- [ ] Verify current page (organization name) is not clickable
- [ ] Test breadcrumb wrapping on mobile (320px width)
- [ ] Test with very long organization names

**Estimated Time:** 20 minutes

---

### Task 1.15: Add Activity Count Badge to Search Results (15 min)

**Action:** Show number of activities per organization in search results

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/Search.js`

**Implementation:**

Update result item display to show activity count:
```javascript
// Add memoized helper function at component level (after useSearchStore)
const getOrganizationActivityCount = React.useMemo(
  () => (orgName) => results.filter(r => r.organization === orgName).length,
  [results]
);

// Update result item h4 (around line 363):
<div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
  <h4
    className="organization-link"
    style={{ margin: 0, display: 'inline' }}
    onClick={() => navigate(`/organization/${encodeURIComponent(result.organization)}`)}
  >
    {result.organization || result.lobbyist || 'Lobby Entry'}
  </h4>
  {result.organization && getOrganizationActivityCount(result.organization) > 1 && (
    <span style={{
      backgroundColor: '#e3f2fd',
      color: '#1565c0',
      padding: '2px 8px',
      borderRadius: '12px',
      fontSize: '0.75rem',
      fontWeight: '600'
    }}>
      {getOrganizationActivityCount(result.organization)} activities
    </span>
  )}
</div>
```

**Testing Checklist:**
- [ ] Perform search returning multiple activities for same organization
- [ ] Verify activity count badge appears next to organization name
- [ ] Verify badge shows correct count
- [ ] Verify badge only appears when count > 1
- [ ] Click organization name, verify navigation still works
- [ ] Verify badge styling matches design
- [ ] Test badge on mobile devices

**Estimated Time:** 15 minutes

---

### Task 1.16: Add Print Styles for Profile Page (15 min)

**Action:** Optimize profile page for printing

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/App.css`

**Implementation:**

Add print styles at end of file:
```css
/* Print Styles for Organization Profile */
@media print {
  .main-nav,
  .breadcrumb,
  .btn,
  button {
    display: none !important;
  }

  .page-container {
    max-width: 100%;
    padding: 0;
  }

  .dashboard-card {
    page-break-inside: avoid;
    box-shadow: none;
    border: 1px solid #ddd;
  }

  .result-item {
    page-break-inside: avoid;
  }

  .category-badge {
    border: 1px solid currentColor;
  }
}
```

**Testing Checklist:**
- [ ] Navigate to organization profile
- [ ] Open print preview (Cmd/Ctrl + P)
- [ ] Verify navigation elements are hidden
- [ ] Verify buttons are hidden
- [ ] Verify content is readable and well-formatted
- [ ] Verify cards don't break across pages
- [ ] Verify category badges are visible with borders
- [ ] Test print output in PDF format

**Estimated Time:** 15 minutes

---

### Task 1.17: Add URL Validation and 404 Handling (20 min)

**Action:** Handle invalid organization names gracefully

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/OrganizationProfile.js`

**Implementation:**

Add validation for organization name:
```javascript
const organizationData = useMemo(() => {
  return results.filter(
    result => result.organization === decodedOrgName
  );
}, [results, decodedOrgName]);

// Add validation check
const isValidOrganization = useMemo(() => {
  // Check if this organization exists in any search results
  if (results.length === 0) return null; // Don't validate if no search performed
  return organizationData.length > 0;
}, [organizationData, results.length]);

// Add conditional rendering for invalid organization
if (isValidOrganization === false) {
  return (
    <div className="page-container">
      <div className="breadcrumb">
        {/* breadcrumb content */}
      </div>
      <div className="page-header">
        <h1>Organization Not Found</h1>
      </div>
      <div className="page-content">
        <div className="dashboard-card">
          <h3>No Data Found</h3>
          <p>
            The organization "{decodedOrgName}" was not found in the current search results.
          </p>
          <p style={{ marginTop: '16px', color: '#666' }}>
            This could mean:
          </p>
          <ul style={{ textAlign: 'left', color: '#666' }}>
            <li>The organization name is misspelled</li>
            <li>No search has been performed yet</li>
            <li>The organization is not in the current search results</li>
          </ul>
          <button
            onClick={() => navigate('/search')}
            className="btn"
            style={{ marginTop: '16px' }}
          >
            Return to Search
          </button>
        </div>
      </div>
    </div>
  );
}
```

**Testing Checklist:**
- [ ] Navigate to `/organization/InvalidOrgName`
- [ ] After performing a search, verify "Organization Not Found" page displays
- [ ] Verify error message is clear and helpful
- [ ] Verify "Return to Search" button works
- [ ] Test with special characters in URL: `/organization/Test%20&%20Invalid`
- [ ] Verify no console errors occur
- [ ] Test with valid organization name - verify normal page loads

**Estimated Time:** 20 minutes

---

### Task 1.18: Add Performance Optimization with React.memo (15 min)

**Action:** Optimize component re-renders

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/OrganizationProfile.js`

**Implementation:**

1. Wrap component with React.memo:
```javascript
import React, { useMemo } from 'react';
// ... other imports

const OrganizationProfile = React.memo(() => {
  // ... existing component code
});

export default OrganizationProfile;
```

2. Create memoized ActivityItem component:
```javascript
// Add before OrganizationProfile component
const ActivityItem = React.memo(({ activity, getCategoryClass }) => (
  <div className="result-item">
    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
      <span className={getCategoryClass(activity.category)}>
        {activity.category || 'Other'}
      </span>
      <h4 style={{ margin: 0, display: 'inline' }}>
        {activity.lobbyist || 'Unknown Lobbyist'}
      </h4>
    </div>
    <p>{activity.description || activity.activity_description}</p>
    <span className="result-meta">
      Amount: ${activity.amount?.toLocaleString() || 'N/A'} |
      Date: {activity.date || activity.filing_date || 'N/A'}
    </span>
  </div>
));

// Use in map:
{sortedActivities.map((activity, index) => (
  <ActivityItem
    key={`${activity.organization}-${activity.lobbyist}-${activity.date}-${index}`}
    activity={activity}
    getCategoryClass={getCategoryClass}
  />
))}
```

**Testing Checklist:**
- [ ] Install React DevTools browser extension
- [ ] Enable "Highlight updates" in DevTools
- [ ] Navigate to organization profile
- [ ] Change sort order
- [ ] Verify only the activities list re-renders (not the entire page)
- [ ] Verify no performance warnings in console
- [ ] Test with large dataset (if available)
- [ ] Profile component rendering time

**Estimated Time:** 15 minutes

---

### Task 1.19: Add Mobile Responsive Styles (20 min)

**Action:** Ensure profile page works well on mobile devices

**Files:**
- **MODIFY**: `/Users/michaelingram/Documents/GitHub/CA_lobby/src/App.css`

**Implementation:**

Add mobile-specific styles after line 644:
```css
/* Organization Profile Mobile Styles */
@media (max-width: 768px) {
  .breadcrumb {
    font-size: 0.8rem;
    margin-bottom: 12px;
  }

  .breadcrumb-current {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 150px;
  }

  .dashboard-card h3 {
    font-size: 1.1rem;
  }

  .result-item h4 {
    font-size: 1rem;
  }

  .category-badge {
    font-size: 0.65rem;
    padding: 3px 8px;
  }

  /* Stack sort controls vertically on mobile */
  .dashboard-card > div:first-child {
    flex-direction: column !important;
    align-items: flex-start !important;
    gap: 12px !important;
  }

  .dashboard-card select {
    width: 100%;
  }
}

@media (max-width: 576px) {
  .page-header h1 {
    font-size: 1.5rem;
    word-break: break-word;
  }

  .result-item {
    padding: 12px;
  }

  .result-meta {
    font-size: 0.75rem;
    display: block;
    margin-top: 4px;
  }
}
```

**Testing Checklist:**
- [ ] Open Chrome DevTools device emulation
- [ ] Test at 320px width (iPhone SE)
- [ ] Verify breadcrumb truncates long organization names
- [ ] Verify sort controls stack vertically
- [ ] Test at 375px width (iPhone X)
- [ ] Test at 768px width (tablet)
- [ ] Verify all text remains readable
- [ ] Verify touch targets are at least 44px (buttons, links)
- [ ] Test landscape orientation on mobile

**Estimated Time:** 20 minutes

---

### Task 1.20: Final Integration Testing and Bug Fixes (30 min)

**Action:** Complete end-to-end testing and fix any issues

**Files:**
- Multiple files as needed for bug fixes

**Testing Checklist:**

**1. Search to Profile Flow:**
- [ ] Perform search with query
- [ ] Click organization name
- [ ] Verify profile loads with correct data
- [ ] Verify statistics are accurate
- [ ] Verify activities display correctly

**2. Navigation:**
- [ ] Test breadcrumb links (Home, Search)
- [ ] Test back button
- [ ] Test browser forward/back buttons
- [ ] Test direct URL access

**3. Data Display:**
- [ ] Verify all statistics calculate correctly
- [ ] Verify currency formatting
- [ ] Verify date formatting
- [ ] Verify category badges display

**4. Sorting:**
- [ ] Test all 4 sort options
- [ ] Verify sort order is correct each time
- [ ] Verify sort persists when returning to page

**5. Edge Cases:**
- [ ] Organization with 1 activity
- [ ] Organization with many activities (10+)
- [ ] Invalid organization name
- [ ] No search performed (empty state)
- [ ] Special characters in organization name

**6. Responsive Design:**
- [ ] Test on mobile (320px-576px)
- [ ] Test on tablet (768px-1024px)
- [ ] Test on desktop (1200px+)
- [ ] Test in portrait and landscape

**7. Performance:**
- [ ] Check for console errors
- [ ] Check for console warnings
- [ ] Verify page loads quickly
- [ ] Verify smooth animations

**8. Cross-browser:**
- [ ] Test in Chrome
- [ ] Test in Firefox
- [ ] Test in Safari (if available)

**Estimated Time:** 45-60 minutes

**Note:** This comprehensive testing checklist has 8 categories with 40+ individual tests. Allow sufficient time for thorough validation.

---

## 📊 Phase 1 Summary

### Time Breakdown
- **Setup & Basic Structure** (Tasks 1-5): ~1.5 hours
- **Data Display & Filtering** (Tasks 6-9): ~1.75 hours
- **Styling & Enhancements** (Tasks 10-12): ~1 hour
- **Navigation & States** (Tasks 13-17): ~1.5 hours
- **Optimization & Polish** (Tasks 18-19): ~35 minutes
- **Testing & Fixes** (Task 20): ~45-60 minutes

**Total Estimated Time:** 7-9 hours (includes 1-1.5 hour testing buffer)

### Key Deliverables
1. ✅ Clickable organization links in search results
2. ✅ Organization profile page at `/organization/:organizationName`
3. ✅ Basic statistics (total amount, avg amount, activity count, lobbyists, categories)
4. ✅ Sortable activity list (by date and amount)
5. ✅ Category badges with color coding
6. ✅ Breadcrumb navigation
7. ✅ Responsive design (mobile, tablet, desktop)
8. ✅ Loading and error states
9. ✅ Print-optimized styles
10. ✅ Performance optimizations

### Files Created
- `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/OrganizationProfile.js`

### Files Modified
- `/Users/michaelingram/Documents/GitHub/CA_lobby/src/App.js`
- `/Users/michaelingram/Documents/GitHub/CA_lobby/src/App.css`
- `/Users/michaelingram/Documents/GitHub/CA_lobby/src/components/Search.js`

### Success Criteria Met
- [ ] Organization names in search results are clickable
- [ ] Profile pages load with organization details
- [ ] Basic statistics display correctly
- [ ] Navigation between search and profile seamless
- [ ] No regressions in existing search functionality

---

## 🔄 Next Steps

After completing Phase 1:
1. **Review and Test**: Complete Task 1.20 thoroughly
2. **Commit Changes**: Use micro-save points strategy
3. **Document Issues**: Note any deviations or problems
4. **Proceed to Phase 2**: Enhanced data visualization and state management

---

**Last Updated:** September 30, 2025
**Status:** Ready to Start
**Next Review:** After Phase 1 completion