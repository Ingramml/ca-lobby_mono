# Google Analytics Integration Plan

**Project:** CA Lobby Search System
**Phase:** 2g - Analytics Integration
**Created:** October 24, 2025
**Status:** Planning

## Executive Summary

Integrate Google Analytics 4 (GA4) into the CA Lobby application to track user behavior, page views, search patterns, and user engagement metrics. This will replace the removed custom Analytics page with professional analytics capabilities.

## Objectives

1. ✅ Track page views and user navigation patterns
2. ✅ Monitor search queries and filter usage
3. ✅ Track organization profile views
4. ✅ Measure user engagement and session duration
5. ✅ Track export functionality usage (CSV/JSON downloads)
6. ✅ Monitor error rates and user experience issues

## Prerequisites

- ✅ Google Analytics 4 account created
- ✅ GA4 Measurement ID obtained (format: G-XXXXXXXXXX)
- ✅ Analytics page removed from application
- ✅ React application deployed and accessible

## Implementation Approach

### Option 1: Direct Script Injection (Recommended for MVP)
**Pros:**
- Simple implementation
- No additional dependencies
- Works immediately on deployment
- Standard Google implementation

**Cons:**
- Less programmatic control
- Manual event tracking requires additional code

### Option 2: React GA4 Package (Recommended for Production)
**Pros:**
- React-specific integration
- Programmatic event tracking
- TypeScript support
- Better SPA handling

**Cons:**
- Additional dependency (~50KB)
- Requires more configuration

**Decision:** Use **Option 2 (React GA4)** for better React integration and event tracking capabilities.

## Technical Implementation

### Step 1: Install Dependencies

```bash
npm install react-ga4
```

**Impact:**
- Bundle size increase: ~50KB (gzipped)
- Current bundle: 194.87 KB → Projected: ~245 KB (still under 400KB target)

### Step 2: Create Analytics Utility

**File:** `src/utils/analytics.js`

```javascript
import ReactGA from 'react-ga4';

const MEASUREMENT_ID = process.env.REACT_APP_GA_MEASUREMENT_ID;

// Initialize Google Analytics
export const initGA = () => {
  if (MEASUREMENT_ID && process.env.NODE_ENV === 'production') {
    ReactGA.initialize(MEASUREMENT_ID, {
      gaOptions: {
        anonymizeIp: true, // GDPR compliance
        cookieFlags: 'SameSite=None;Secure'
      }
    });
  }
};

// Track page views
export const trackPageView = (path) => {
  if (MEASUREMENT_ID && process.env.NODE_ENV === 'production') {
    ReactGA.send({ hitType: 'pageview', page: path });
  }
};

// Track custom events
export const trackEvent = (category, action, label, value) => {
  if (MEASUREMENT_ID && process.env.NODE_ENV === 'production') {
    ReactGA.event({
      category,
      action,
      label,
      value
    });
  }
};

// Track search queries
export const trackSearch = (query, filters, resultCount) => {
  trackEvent('Search', 'search_executed', query, resultCount);

  // Track active filters
  if (filters.organization) {
    trackEvent('Search', 'filter_organization', filters.organization);
  }
  if (filters.category && filters.category !== 'all') {
    trackEvent('Search', 'filter_category', filters.category);
  }
  if (filters.dateRange && filters.dateRange !== 'all') {
    trackEvent('Search', 'filter_date_range', filters.dateRange);
  }
};

// Track organization profile views
export const trackOrganizationView = (organizationName) => {
  trackEvent('Organization', 'profile_view', organizationName);
};

// Track export actions
export const trackExport = (exportType, organizationName) => {
  trackEvent('Export', exportType, organizationName);
};

// Track errors
export const trackError = (errorMessage, errorLocation) => {
  trackEvent('Error', errorLocation, errorMessage);
};
```

### Step 3: Update App.js for Route Tracking

**File:** `src/App.js`

```javascript
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { initGA, trackPageView } from './utils/analytics';

function AppContent() {
  const location = useLocation();

  // Initialize GA on mount
  useEffect(() => {
    initGA();
  }, []);

  // Track page views on route change
  useEffect(() => {
    trackPageView(location.pathname + location.search);
  }, [location]);

  // ... rest of component
}
```

### Step 4: Update Search Component

**File:** `src/components/Search.js`

```javascript
import { trackSearch } from '../utils/analytics';

const handleSearch = async (e) => {
  e.preventDefault();
  // ... existing search logic

  try {
    const searchResults = generateSearchResults(query, filters);
    setResults(searchResults);

    // Track search with GA
    trackSearch(query, filters, searchResults.length);

    addToHistory({
      query,
      filters,
      resultCount: searchResults.length,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    // ... error handling
  }
};
```

### Step 5: Update OrganizationProfile Component

**File:** `src/components/OrganizationProfile.js`

```javascript
import { trackOrganizationView, trackExport } from '../utils/analytics';

useEffect(() => {
  if (decodedOrgName) {
    trackOrganizationView(decodedOrgName);
  }
}, [decodedOrgName]);

const handleExportCSV = () => {
  trackExport('csv', organizationData.name);
  // ... existing export logic
};

const handleExportJSON = () => {
  trackExport('json', organizationData.name);
  // ... existing export logic
};
```

### Step 6: Environment Configuration

**File:** `.env` (local development)
```bash
REACT_APP_GA_MEASUREMENT_ID=G-XXXXXXXXXX
```

**File:** `.env.production` (or Vercel environment variables)
```bash
REACT_APP_GA_MEASUREMENT_ID=G-XXXXXXXXXX
```

**Vercel Setup:**
1. Go to Vercel Dashboard → Project Settings → Environment Variables
2. Add: `REACT_APP_GA_MEASUREMENT_ID` = `G-XXXXXXXXXX`
3. Scope: Production, Preview, Development (as needed)
4. Redeploy for changes to take effect

## Events to Track

### Page Views (Automatic)
- `/` - Dashboard
- `/search` - Search page
- `/reports` - Reports page
- `/settings` - Settings page
- `/organization/:name` - Organization profiles

### Custom Events

| Category | Action | Label | Value | Description |
|----------|--------|-------|-------|-------------|
| Search | search_executed | Query text | Result count | User performed search |
| Search | filter_organization | Organization name | - | Organization filter used |
| Search | filter_category | Category name | - | Category filter applied |
| Search | filter_date_range | Date range value | - | Date filter applied |
| Organization | profile_view | Organization name | - | Profile page viewed |
| Organization | activity_pagination | Page number | - | User paginated activities |
| Export | csv | Organization name | - | CSV export downloaded |
| Export | json | Organization name | - | JSON export downloaded |
| Export | activities_csv | Organization name | Row count | Activities exported |
| Navigation | breadcrumb_click | Target page | - | Breadcrumb navigation |
| Error | search_error | Error message | - | Search failed |
| Error | profile_load_error | Organization name | - | Profile failed to load |

## Testing Plan

### Development Testing
1. Set test GA4 property (separate from production)
2. Use GA Measurement ID: `G-XXXXXXXXXX-DEV`
3. Test all event tracking in localhost
4. Verify events in GA4 DebugView

### Production Testing
1. Deploy to Vercel with production GA4 ID
2. Test page views in real-time GA4 reports
3. Verify custom events fire correctly
4. Check event parameters are captured

### GA4 Real-Time Verification
1. Open GA4 → Reports → Real-time
2. Perform actions in application
3. Verify events appear within 5 seconds
4. Check event parameters are correct

## Privacy & Compliance

### GDPR Compliance
- ✅ IP anonymization enabled (`anonymizeIp: true`)
- ✅ No PII (Personally Identifiable Information) tracked
- ✅ Organization names are public data (not PII)
- ✅ Search queries do not contain user information
- ⚠️ Consider adding cookie consent banner (future enhancement)

### Data Retention
- Default: 14 months (GA4 standard)
- Can be configured in GA4 settings
- Event data automatically expires per retention policy

## Performance Impact

### Bundle Size
- **Current:** 194.87 KB (gzipped)
- **react-ga4:** ~50 KB (gzipped)
- **Projected Total:** ~245 KB (gzipped)
- **Target:** < 400 KB ✅ WITHIN TARGET

### Runtime Performance
- GA4 loads asynchronously (non-blocking)
- Event tracking uses navigator.sendBeacon (optimal)
- Minimal impact on page load time (<50ms)

## Rollout Strategy

### Phase 1: Core Tracking (Day 1)
- ✅ Install react-ga4
- ✅ Create analytics utility
- ✅ Initialize GA4 in App.js
- ✅ Track page views automatically
- ✅ Deploy and verify basic tracking

### Phase 2: Search Tracking (Day 2)
- ✅ Track search queries
- ✅ Track filter usage
- ✅ Track result counts
- ✅ Track search errors

### Phase 3: Organization Tracking (Day 3)
- ✅ Track profile views
- ✅ Track export actions
- ✅ Track pagination events

### Phase 4: Advanced Events (Day 4)
- ✅ Track navigation patterns
- ✅ Track user engagement time
- ✅ Track dashboard chart interactions
- ✅ Custom dimensions for data analysis

## Success Metrics

### Implementation Success
- ✅ GA4 receiving page views within 1 hour of deployment
- ✅ All custom events firing correctly
- ✅ Real-time reports showing activity
- ✅ No console errors from GA4 code
- ✅ Bundle size under 250 KB

### Analytics Usage Success (30 days post-launch)
- Track top 10 most searched organizations
- Identify most used filters
- Measure average search result count
- Track organization profile views distribution
- Monitor export feature usage

## GA4 Dashboard Setup

### Custom Reports to Create
1. **Search Analysis**
   - Top search queries
   - Average results per search
   - Most used filters
   - Search-to-profile-view conversion

2. **Organization Popularity**
   - Most viewed organizations
   - Profile view duration
   - Export rates by organization

3. **User Journey**
   - Entry pages
   - Navigation flow
   - Exit pages
   - Session duration

4. **Feature Usage**
   - Export feature adoption
   - Filter usage distribution
   - Mobile vs desktop usage

## Documentation Updates Required

After implementation:
- ✅ Update README.md with GA4 setup instructions
- ✅ Document environment variable requirements
- ✅ Add privacy policy section
- ✅ Create GA4 event tracking reference doc

## Known Limitations

1. **Ad Blockers:** ~30% of users may block GA4
2. **Cookie Restrictions:** Safari ITP may limit tracking
3. **Real-time Delay:** Events may take 5-10 seconds to appear
4. **Event Sampling:** GA4 may sample high-traffic properties

## Alternatives Considered

### Alternative 1: Plausible Analytics
- **Pros:** Privacy-focused, lightweight, EU-hosted
- **Cons:** Paid service, less features than GA4
- **Decision:** Not chosen (GA4 is free and more powerful)

### Alternative 2: Matomo
- **Pros:** Self-hosted, full data ownership
- **Cons:** Requires infrastructure, maintenance overhead
- **Decision:** Not chosen (too complex for current needs)

### Alternative 3: No Analytics
- **Pros:** No privacy concerns, no bundle size increase
- **Cons:** No insights into user behavior
- **Decision:** Rejected (analytics needed for product decisions)

## Next Steps

1. ✅ Get approval for this plan
2. ✅ Obtain GA4 Measurement ID from project owner
3. ✅ Create implementation tasks in todo list
4. ✅ Begin Phase 1 implementation
5. ✅ Test in development environment
6. ✅ Deploy to production
7. ✅ Monitor for 24 hours
8. ✅ Create GA4 custom reports

## Sign-Off

**Plan Status:** ⏳ AWAITING APPROVAL
**Estimated Duration:** 2 days
**Dependencies:** GA4 Measurement ID required
**Risk Level:** Low (non-breaking addition)

---

**Last Updated:** October 24, 2025
**Author:** CA Lobby Development Team
**Next Review:** After Phase 1 implementation
