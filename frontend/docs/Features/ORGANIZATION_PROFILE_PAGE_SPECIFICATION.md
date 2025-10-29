# Organization Profile Page Feature Specification

**Feature Name:** Organization Profile Pages with Clickable Search Results
**Date:** September 29, 2025
**Status:** 📋 SPECIFICATION - READY FOR REVIEW
**Priority:** High - Enhanced User Experience
**Estimated Implementation:** 2-3 days

---

## 🎯 **FEATURE OVERVIEW**

Transform static organization names in search results into clickable links that navigate users to comprehensive organization profile pages. Each profile provides deep insights into a lobbying organization's activities, spending patterns, and influence areas.

### **User Story**
*"As a researcher investigating lobbying activities, I want to click on an organization name in search results to see a comprehensive profile of that organization's lobbying history, so I can understand their full scope of influence and activities."*

---

## 📊 **CURRENT STATE ANALYSIS**

### **Existing Search Results Display**
```javascript
// Current implementation in Search.js (lines 362-369)
<div key={index} className="result-item">
  <h4>{result.organization || result.lobbyist || 'Lobby Entry'}</h4>
  <p>{result.description || result.activity_description || 'No description available'}</p>
  <span className="result-meta">
    Amount: {result.amount ? `$${result.amount.toLocaleString()}` : 'N/A'} |
    Date: {result.date || result.filing_date || 'N/A'}
  </span>
</div>
```

### **Current Data Structure (Demo Data)**
```javascript
{
  organization: 'California Medical Association',
  lobbyist: 'John Smith',
  description: 'Healthcare legislation advocacy and medical professional representation',
  amount: 125000,
  date: '2024-09-15',
  filing_date: '2024-09-15',
  category: 'healthcare',
  activity_description: 'Lobbying activities related to healthcare reform and medical licensing'
}
```

### **Current Limitations**
- Organization names are static text with no interaction
- No way to explore organization's complete lobbying history
- Limited context about organization's total influence
- No aggregated insights across multiple lobbying activities

---

## 🎨 **ORGANIZATION PROFILE PAGE DESIGN**

### **Page Layout Structure**

```
┌─────────────────────────────────────────────────────────────────┐
│ 🏛️ CA Lobby Search                                    [User] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ← Back to Search Results                                        │
│                                                                 │
│ 🏢 California Medical Association                               │
│                                                                 │
│ ┌─ ORGANIZATION OVERVIEW ──────────────────────────────────┐   │
│ │                                                          │   │
│ │ Industry: Healthcare                                     │   │
│ │ Total Spending (All Time): $2,450,000                   │   │
│ │ Active Since: 2018                                       │   │
│ │ Last Activity: September 15, 2024                        │   │
│ │ Number of Lobbyists: 8                                   │   │
│ │                                                          │   │
│ └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─ ACTIVITY SUMMARY ────────────────┐ ┌─ TOP FOCUS AREAS ───┐  │
│ │ 📊 Spending Over Time             │ │ 🎯 Policy Categories │  │
│ │                                   │ │                     │  │
│ │ [Interactive Chart]               │ │ ■■■■■■■■ Healthcare │  │
│ │                                   │ │ ■■■■■    Insurance  │  │
│ │ Last 12 Months: $450,000          │ │ ■■■      Licensing  │  │
│ │ vs Previous: +15%                 │ │ ■        Safety     │  │
│ │                                   │ │                     │  │
│ └───────────────────────────────────┘ └─────────────────────┘  │
│                                                                 │
│ ┌─ RECENT LOBBYING ACTIVITIES ─────────────────────────────┐   │
│ │                                                          │   │
│ │ Sep 15, 2024 - Healthcare Reform Bill AB-123            │   │
│ │ Lobbyist: John Smith | Amount: $125,000                 │   │
│ │ Description: Medical professional licensing reform       │   │
│ │                                                          │   │
│ │ Aug 22, 2024 - Insurance Coverage Expansion SB-456      │   │
│ │ Lobbyist: Sarah Johnson | Amount: $89,000               │   │
│ │ Description: Coverage mandate adjustments               │   │
│ │                                                          │   │
│ │ [Load More Activities...]                                │   │
│ │                                                          │   │
│ └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─ LOBBYIST NETWORK ─────────────┐ ┌─ RELATED ORGANIZATIONS ─┐ │
│ │                                │ │                         │ │
│ │ Primary Lobbyists:             │ │ Similar Organizations:  │ │
│ │ • John Smith (8 activities)    │ │ • CA Hospital Assoc.   │ │
│ │ • Sarah Johnson (5 activities) │ │ • Medical Board CA     │ │
│ │ • Dr. Michael Chen (3 acts)    │ │ • Nurses Union CA      │ │
│ │                                │ │                         │ │
│ └────────────────────────────────┘ └─────────────────────────┘ │
│                                                                 │
│ ┌─ EXPORT & ACTIONS ─────────────────────────────────────────┐ │
│ │                                                            │ │
│ │ [📊 Export Profile Data] [🔔 Set Alert] [💾 Bookmark]    │ │
│ │                                                            │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 **CORE INFORMATION SECTIONS**

### **1. Organization Overview Header**
**Essential Information:**
- Organization full name and any aliases
- Primary industry/category classification
- Total spending across all time periods
- Date of first lobbying activity in system
- Date of most recent activity
- Current active status

**Data Fields Required:**
```javascript
{
  organizationId: string,
  name: string,
  aliases: string[],
  primaryCategory: string,
  totalSpending: number,
  firstActivityDate: string,
  lastActivityDate: string,
  isActive: boolean,
  numberOfLobbyists: number
}
```

### **2. Activity Summary Dashboard**
**Visual Analytics:** 
- Spending over time (line chart showing quarterly/yearly trends)
- Spending comparison with previous periods
- Activity frequency patterns
- Peak activity periods

**Calculated Metrics:**
- Average spending per activity
- Spending trend (increasing/decreasing)
- Activity regularity patterns
- Seasonal lobbying patterns

### **3. Recent Lobbying Activities**
**Activity List (Paginated):**
- Date of activity
- Bill numbers or policy areas
- Assigned lobbyist(s)
- Spending amount
- Activity description
- Links to full activity details

**Sorting Options:**
- Most recent first (default)
- Highest spending first
- By lobbyist
- By policy category

---

## 🔍 **ADDITIONAL BENEFICIAL INFORMATION**

### **A. Policy Impact Analysis**
**Why Beneficial:** Helps users understand the organization's influence scope
- **Bills Influenced:** List of specific legislation the organization lobbied for/against
- **Success Rate:** Percentage of lobbied bills that passed
- **Opposition Analysis:** Bills they opposed and outcomes
- **Committee Focus:** Which legislative committees they focus on most

**Implementation Complexity:** Medium (requires bill tracking data)

### **B. Network Analysis**
**Why Beneficial:** Reveals lobbying ecosystem and relationships
- **Lobbyist Network:** All lobbyists who have worked for this organization
- **Shared Lobbyists:** Organizations that use the same lobbyists
- **Industry Peers:** Organizations in similar categories with spending comparisons
- **Coalition Partners:** Organizations that lobbied on the same bills

**Implementation Complexity:** High (requires relationship mapping)

### **C. Geographic Analysis** Version 2.0
**Why Beneficial:** Shows regional influence and focus areas
- **District Focus:** Which legislative districts are most targeted
- **Regional Spending:** Breakdown by Northern/Southern California focus
- **Local vs State:** Balance between local and state-level lobbying
- **Event Locations:** Where lobbying meetings/events typically occur

**Implementation Complexity:** Medium (requires geographic data)

### **D. Financial Deep Dive** Version 2.0
**Why Beneficial:** Provides transparency into spending patterns
- **Spending Categories:** Breakdown by type (direct lobbying, events, travel)
- **Quarterly Patterns:** Spending seasonality and budget cycles
- **Cost per Lobbyist:** Efficiency metrics
- **Expense Ratios:** Percentage spent on different lobbying activities

**Implementation Complexity:** Low (uses existing financial data)

### **E. Temporal Analysis** Version 2.0
**Why Beneficial:** Shows how organizations evolve their lobbying strategies
- **Strategy Evolution:** How focus areas have changed over time
- **Response Patterns:** How quickly they respond to new legislation
- **Election Cycles:** How spending correlates with election periods
- **Legislative Calendar:** Activity patterns around legislative sessions

**Implementation Complexity:** Medium (requires time-series analysis)

### **F. Competitive Intelligence**
**Why Beneficial:** Benchmarking against similar organizations
- **Industry Rankings:** Where organization ranks in spending within industry
- **Market Share:** Percentage of total industry lobbying spend
- **Competitor Analysis:** Direct comparison with similar organizations
- **Influence Score:** Calculated metric based on spending and success

**Implementation Complexity:** High (requires competitive analysis algorithms)

### **G. Regulatory Compliance**
**Why Beneficial:** Transparency and accountability tracking
- **Filing Timeliness:** How promptly organization files required reports
- **Disclosure Completeness:** Quality of information provided
- **Compliance History:** Any violations or issues
- **Report Quality Score:** Metric for transparency and completeness

**Implementation Complexity:** Medium (requires compliance data tracking)

---

## 🛠️ **TECHNICAL IMPLEMENTATION APPROACH**

### **Frontend Components**

#### **1. Enhanced Search Results** (`src/components/Search.js`)
```javascript
// Replace static organization name with clickable link
<h4>
  <Link to={`/organization/${encodeURIComponent(result.organization)}`} className="organization-link">
    {result.organization || result.lobbyist || 'Lobby Entry'}
  </Link>
</h4>
```

#### **2. New Organization Profile Component** (`src/components/OrganizationProfile.js`)
```javascript
import React, { useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useOrganizationStore } from '../stores';

function OrganizationProfile() {
  const { organizationName } = useParams();
  const {
    currentOrganization,
    loading,
    error,
    fetchOrganizationProfile
  } = useOrganizationStore();

  useEffect(() => {
    fetchOrganizationProfile(organizationName);
  }, [organizationName]);

  // Component implementation
}
```

#### **3. Router Integration** (`src/App.js`)
```javascript
// Add new route
<Route path="/organization/:organizationName" element={<OrganizationProfile />} />
```

### **State Management Extension**

#### **New Organization Store** (`src/stores/organizationStore.js`)
```javascript
import { create } from 'zustand';

const useOrganizationStore = create((set, get) => ({
  // Organization profile state
  currentOrganization: null,
  organizationActivities: [],
  organizationAnalytics: null,
  loading: false,
  error: null,

  // Actions
  fetchOrganizationProfile: async (organizationName) => {
    set({ loading: true, error: null });
    try {
      const profile = await apiCall(`/api/organizations/${organizationName}`);
      const activities = await apiCall(`/api/organizations/${organizationName}/activities`);
      const analytics = await apiCall(`/api/organizations/${organizationName}/analytics`);

      set({
        currentOrganization: profile.data,
        organizationActivities: activities.data,
        organizationAnalytics: analytics.data,
        loading: false
      });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  // Additional actions for pagination, filtering, etc.
}));
```

### **Backend API Requirements**

#### **New API Endpoints**
```javascript
// Organization profile endpoint
GET /api/organizations/:organizationName
Response: {
  organizationId: string,
  name: string,
  aliases: string[],
  primaryCategory: string,
  totalSpending: number,
  firstActivityDate: string,
  lastActivityDate: string,
  isActive: boolean,
  numberOfLobbyists: number,
  summary: string
}

// Organization activities endpoint
GET /api/organizations/:organizationName/activities?page=1&limit=10&sort=date
Response: {
  activities: [...],
  pagination: { total, pages, current }
}

// Organization analytics endpoint
GET /api/organizations/:organizationName/analytics
Response: {
  spendingOverTime: [...],
  categoryBreakdown: {...},
  lobbyistNetwork: [...],
  trendAnalysis: {...}
}

// Related organizations endpoint
GET /api/organizations/:organizationName/related
Response: {
  similarOrganizations: [...],
  sharedLobbyists: [...],
  industryPeers: [...]
}
```

---

## 🎯 **USER EXPERIENCE FLOW**

### **Navigation Path**
1. **Search Results** → User sees organization name as clickable link
2. **Click Organization** → Navigate to `/organization/[name]`
3. **Profile Page** → Comprehensive organization information
4. **Back Navigation** → Return to search results with state preserved

### **Breadcrumb Navigation**
```
Home > Search Results > California Medical Association Profile
```

### **Deep Linking Support**
- Direct URLs: `/organization/California%20Medical%20Association`
- Shareable links for specific organizations
- SEO-friendly URLs with organization names

### **State Persistence**
- Search results remain available when returning from profile
- Organization profile data cached for quick re-access
- User's scroll position preserved in search results

---

## 📊 **DATA REQUIREMENTS & SOURCES**

### **Primary Data Sources**
1. **Existing BigQuery Database:** Organization names, activities, spending
2. **Calculated Aggregations:** Total spending, activity counts, date ranges
3. **Derived Analytics:** Trends, patterns, comparative metrics

### **Data Processing Requirements**
```sql
-- Example query for organization profile data
SELECT
  organization,
  COUNT(*) as total_activities,
  SUM(amount) as total_spending,
  MIN(date) as first_activity,
  MAX(date) as last_activity,
  COUNT(DISTINCT lobbyist) as unique_lobbyists,
  category,
  AVG(amount) as avg_spending_per_activity
FROM lobby_activities
WHERE organization = ?
GROUP BY organization, category
```

### **Caching Strategy**
- **Organization Profiles:** Cache for 24 hours (daily data updates)
- **Activity Lists:** Cache with pagination metadata
- **Analytics Data:** Cache computed metrics for 1 hour
- **Related Organizations:** Cache for 1 week (relatively static)

---

## 🚀 **IMPLEMENTATION PHASES**

### **Phase 1: Basic Profile Page** (Day 1)
- Create OrganizationProfile component
- Add routing and navigation
- Implement basic organization overview section
- Make organization names clickable in search results

**Deliverables:**
- Clickable organization names in search results
- Basic organization profile page with overview information
- Navigation back to search results

### **Phase 2: Enhanced Data & Analytics** (Day 2)
- Add organization store with API integration
- Implement activity list with pagination
- Add spending analytics and visualizations
- Create lobbyist network section

**Deliverables:**
- Complete organization profile with all core sections
- Interactive charts and data visualizations
- Paginated activity history

### **Phase 3: Advanced Features** (Day 3)
- Implement related organizations
- Add export functionality
- Create bookmark and alert features
- Add mobile-responsive design optimizations

**Deliverables:**
- Fully featured organization profile pages
- Export and user action capabilities
- Mobile-optimized experience

---

## 🎨 **UI/UX DESIGN CONSIDERATIONS**

### **Visual Design**
- **Consistent Styling:** Use existing CSS design system and variables
- **Professional Appearance:** Government-appropriate color scheme and typography
- **Clear Hierarchy:** Proper heading structure and information organization
- **Responsive Design:** Mobile-first approach matching existing components

### **Accessibility**
- **Screen Reader Support:** Proper ARIA labels and semantic HTML
- **Keyboard Navigation:** Full keyboard accessibility for all interactive elements
- **Color Contrast:** Meet WCAG guidelines for text and background contrast
- **Focus Management:** Clear focus indicators and logical tab order

### **Performance Considerations**
- **Lazy Loading:** Load profile data on demand
- **Progressive Enhancement:** Show basic info first, load analytics progressively
- **Caching Strategy:** Cache organization data to prevent repeated API calls
- **Image Optimization:** Any charts or visualizations optimized for web

---

## ✅ **SUCCESS METRICS**

### **User Engagement**
- **Click-through Rate:** Percentage of users who click organization names
- **Time on Profile:** Average time spent on organization profile pages
- **Return Visits:** Users who visit multiple organization profiles
- **Export Usage:** Number of profile data exports

### **Technical Performance**
- **Page Load Time:** Profile pages load in <2 seconds
- **API Response Time:** Organization data queries complete in <1 second
- **Cache Hit Rate:** >80% of requests served from cache
- **Error Rate:** <1% of profile page requests fail

### **Data Quality**
- **Profile Completeness:** Percentage of organizations with complete profiles
- **Data Accuracy:** Accuracy of calculated metrics and aggregations
- **Update Frequency:** How quickly new activities appear in profiles

---

## 🔒 **SECURITY & PRIVACY CONSIDERATIONS**

### **Data Protection**
- **Public Data Only:** Display only publicly available lobbying information
- **No Personal Information:** Exclude private contact details or sensitive data
- **Rate Limiting:** Prevent automated scraping of organization profiles
- **Input Validation:** Sanitize organization names in URLs

### **Access Control**
- **Authentication Required:** Maintain existing Clerk authentication requirements
- **User Permissions:** Same access levels as search functionality
- **Audit Logging:** Track organization profile access for transparency

---

## 📝 **TESTING STRATEGY**

### **Unit Testing**
- Organization store actions and state management
- Profile component rendering with mock data
- URL parameter handling and routing

### **Integration Testing**
- End-to-end navigation from search to profile
- API integration with backend endpoints
- State persistence across navigation

### **User Testing**
- Usability testing with researchers and journalists
- Accessibility testing with screen readers
- Mobile device testing across various screen sizes

---

## 🎯 **RECOMMENDED IMPLEMENTATION PRIORITY**

### **High Priority (Must Have)**
1. **Clickable Organization Names** - Core feature requirement
2. **Basic Organization Overview** - Essential information display
3. **Recent Activities List** - Primary value proposition
4. **Back Navigation** - User experience requirement

### **Medium Priority (Should Have)**
5. **Spending Analytics Charts** - Enhanced data visualization
6. **Lobbyist Network** - Additional context and insights
7. **Related Organizations** - Discovery and exploration
8. **Export Functionality** - User utility feature

### **Low Priority (Nice to Have)**
9. **Bookmark and Alerts** - Advanced user features
10. **Competitive Analysis** - Advanced analytics
11. **Geographic Analysis** - Specialized insights
12. **Regulatory Compliance** - Specialized transparency metrics

---

## 📋 **NEXT STEPS FOR REVIEW**

### **Questions for Stakeholder Review**
1. **Scope Priority:** Which additional information sections are most valuable?
2. **Implementation Timeline:** Should this be implemented in phases or all at once?
3. **Data Requirements:** Are there specific metrics or analytics most important?
4. **User Experience:** Any specific navigation or interaction preferences?

### **Technical Decisions Needed**
1. **URL Structure:** `/organization/[name]` vs `/org/[id]` vs other format?
2. **Caching Strategy:** How long should organization data be cached?
3. **Pagination:** How many activities to show per page?
4. **Chart Library:** Continue with Recharts or consider alternatives for new charts?

### **Design Review Required**
1. **Visual Mockups:** Review proposed layout and information hierarchy
2. **Mobile Experience:** Confirm mobile-responsive design approach
3. **Integration Points:** Ensure consistent styling with existing components

---

**Document Status:** ✅ **READY FOR STAKEHOLDER REVIEW**
**Implementation Ready:** Pending stakeholder approval and prioritization decisions
**Estimated Completion:** 2-3 days after approval
**Dependencies:** Backend API implementation for enhanced features

---

*Document Created: September 29, 2025*
*Last Updated: September 29, 2025*
*Next Review: After stakeholder feedback*