# CA Lobby Sample Data Size Strategy

**Document Type:** Technical Specification
**Phase:** Phase 2 - Data Integration Planning
**Created:** October 24, 2025
**Status:** Active
**Owner:** CA Lobby Project Team

---

## 📋 Executive Summary

This document defines the optimal data size strategy for the CA Lobby web application when transitioning from demo data to real California lobby data. It provides specific recommendations for data volumes, file structures, loading strategies, and performance benchmarks to ensure fast, responsive user experience across all devices and network conditions.

---

## 🎯 Objectives

1. **Performance First** - Maintain <3 second page loads on 3G networks
2. **Scalability** - Support growth from hundreds to thousands of organizations
3. **User Experience** - Provide instant search and smooth interactions
4. **Data Accuracy** - Use real CA lobby data while maintaining performance
5. **Flexibility** - Support both demo mode and production backend

---

## 📊 Current State Analysis

### Existing Demo Data Structure

**Location:** `src/utils/sampleData.js`

**Current Implementation:**
- **Function-based generation:** `generateSampleLobbyData(count = 100)`
- **15 pre-defined organizations** (CA Chamber, PG&E, CMA, etc.)
- **10 lobby categories** (Healthcare, Technology, Energy, etc.)
- **Date range:** 2023-01-01 to 2025-09-28
- **Spending range:** $0 - $500,000 per activity
- **Default count:** 100 records

**Data Processing Functions:**
- `processLobbyTrends()` - Aggregate by quarter/month/year
- `processOrganizationData()` - Top organizations by spending
- `processCategoryData()` - Category breakdowns
- `aggregateOrganizationMetrics()` - Summary statistics
- `extractLobbyistNetwork()` - Lobbyist relationships
- `calculateSpendingTrends()` - Time-series analysis
- `findRelatedOrganizations()` - Similarity matching

**File Size Estimate:**
- Source code: ~8 KB (286 lines)
- Generated 100 records: ~15-20 KB JSON
- Generated 1,000 records: ~150-200 KB JSON
- Generated 5,000 records: ~750 KB - 1 MB JSON

### Current Architecture

**State Management:** Zustand (Phase 2b.2 completed)
- `searchStore` - Search state and results
- `userStore` - User preferences and history
- `appStore` - Application state

**Backend:** Flask API with BigQuery (Phase 1.1 completed)
- API endpoints available but not required
- Demo mode active by default
- `REACT_APP_USE_BACKEND_API` flag controls mode

**Deployment:** Vercel (Phase 1.2 completed)
- Build time target: <10 seconds
- Bundle size current: ~300 KB (before real data)
- Target bundle size: <1 MB total

---

## 🎯 Recommended Data Strategy

### Three-Tier Approach ⭐ **RECOMMENDED**

#### **Tier 1: Initial Summary Data** (Client-Side)
**Purpose:** Fast initial load, searchable list, instant filtering

**Size:** 200-300 KB
**Records:** 500-1,000 organizations (summary only)
**Load Time:** <1 second on WiFi, 2-3s on 3G

**Data Structure:**
```javascript
// src/data/organizations-summary.json
{
  "metadata": {
    "totalOrganizations": 1000,
    "lastUpdated": "2025-10-24",
    "dataVersion": "1.0"
  },
  "organizations": [
    {
      "id": "org_001",
      "name": "California Medical Association",
      "totalSpending": 5000000,
      "activityCount": 150,
      "topCategory": "Healthcare",
      "lastActivity": "2025-09-28",
      "lobbyistCount": 12
    }
    // ... 500-1000 organizations
  ]
}
```

**Fields Per Organization:** 7-10 fields (summary only)
**Estimated Size:** ~200-400 bytes per org
**Total Size:** 200-400 KB for 1,000 orgs

#### **Tier 2: Detailed Profiles** (Lazy Loaded)
**Purpose:** Full organization details loaded on-demand

**Size:** 5-15 KB per profile
**Records:** 50-100 activities per org initially
**Load Time:** <500ms per profile

**Data Structure:**
```javascript
// src/data/profiles/california-medical-association.json
{
  "id": "org_001",
  "name": "California Medical Association",
  "summary": {
    "totalSpending": 5000000,
    "activityCount": 150,
    "averageSpending": 33333,
    "firstActivity": "2020-01-15",
    "lastActivity": "2025-09-28"
  },
  "activities": [
    {
      "id": "act_001",
      "date": "2025-09-28",
      "amount": 45000,
      "category": "Healthcare",
      "lobbyist": "John Smith",
      "description": "Healthcare reform advocacy"
    }
    // ... first 50-100 activities (paginated)
  ],
  "lobbyists": [
    {
      "name": "John Smith",
      "activityCount": 25,
      "totalAmount": 500000,
      "categories": ["Healthcare"]
    }
    // ... 10-20 lobbyists
  ],
  "relatedOrganizations": [
    {
      "name": "California Hospital Association",
      "similarityScore": 0.85,
      "sharedCategories": ["Healthcare"]
    }
    // ... 5-10 related orgs
  ]
}
```

**Storage:** Separate JSON files per organization
**Caching:** Store in Zustand + sessionStorage
**Total Storage:** 500-1,500 KB (if user views 100 profiles)

#### **Tier 3: Backend API** (On-Demand)
**Purpose:** Unlimited data access, advanced queries, real-time updates

**When to Use:**
- Dataset exceeds 2,000 organizations
- User requests >100 activities for an org
- Advanced filtering/sorting beyond client capabilities
- Real-time data requirements
- Export large datasets

**Backend Endpoints:**
```
GET /api/organizations?page=1&limit=50
GET /api/organizations/{id}/activities?page=1&limit=100
GET /api/search?q=healthcare&filters[category]=Healthcare
GET /api/organizations/{id}/full-profile
POST /api/export/csv
```

---

## 📏 Data Volume Recommendations

### By Dataset Size

#### **Small Dataset: <500 Organizations**
```
Strategy: Full Client-Side (Single Tier)
File: organizations-full.json (300-500 KB)
Approach: Load all data at startup
Search: Client-side filtering
Performance: Excellent (<1s load)
Backend: Optional
```

**Implementation:**
- Single JSON file with all data
- Client-side search and filtering
- No lazy loading needed
- Simple architecture

#### **Medium Dataset: 500-2,000 Organizations** ⭐ **MOST LIKELY**
```
Strategy: Hybrid Tiered Approach
Tier 1: organizations-summary.json (200-500 KB)
Tier 2: profiles/{org-name}.json (5-15 KB each)
Tier 3: Backend API for heavy queries
Performance: Good (<2s initial, <500ms details)
Backend: Recommended for advanced features
```

**Implementation:**
- Summary data loaded at startup
- Profile details loaded on-demand
- Backend for exports and advanced queries
- Optimal balance of speed and scalability

#### **Large Dataset: 2,000-10,000 Organizations**
```
Strategy: Backend-First with Client Caching
Tier 1: Minimal summary (top 100 orgs, 50 KB)
Tier 2: All data from backend API
Tier 3: Client caching for recent queries
Performance: Good with caching (<2s searches)
Backend: Required
```

**Implementation:**
- Minimal client-side data
- Backend API handles all queries
- Aggressive client-side caching
- Pagination and virtualization required

#### **Very Large Dataset: >10,000 Organizations**
```
Strategy: Full Backend Architecture
Client: Search interface only (<100 KB)
Backend: All data queries and processing
Caching: Redis/Memcached server-side
Performance: <3s with proper indexing
Backend: Required with optimization
```

**Implementation:**
- No static data files
- All queries server-side
- Advanced caching strategies
- Database query optimization critical

---

## 🎯 Performance Benchmarks

### Load Time Targets

| Data Tier | WiFi | 4G | 3G | Target |
|-----------|------|----|----|--------|
| Tier 1 (Summary) | <0.5s | <1s | <2s | **<2s on 3G** |
| Tier 2 (Profile) | <0.3s | <0.5s | <1s | **<1s on 3G** |
| Tier 3 (API Query) | <0.5s | <1s | <2s | **<2s on 3G** |

### Bundle Size Targets

| Component | Current | With Data | Target |
|-----------|---------|-----------|--------|
| Base App | ~300 KB | ~300 KB | <500 KB |
| Summary Data | 0 KB | 200-300 KB | <400 KB |
| Cached Profiles | 0 KB | 100-500 KB | <500 KB |
| **Total Initial** | **300 KB** | **500-600 KB** | **<1 MB** |

### Rendering Performance

| Operation | Records | Target | Approach |
|-----------|---------|--------|----------|
| Initial Render | 1,000 | <500ms | Virtual scrolling |
| Search Filter | 1,000 | <200ms | Debounced input |
| Pagination | 25/page | <100ms | Pre-calculated pages |
| Profile Load | 1 org | <300ms | Lazy loading |

---

## 🏗️ Implementation Plan

### Phase 1: Prepare Summary Data (Current Priority)

**Tasks:**
1. Determine actual CA lobby data size
2. Create data extraction script
3. Generate organizations-summary.json
4. Test load performance
5. Implement in Search component

**Timeline:** 1-2 days

**Deliverables:**
- `src/data/organizations-summary.json` (200-400 KB)
- Data generation script
- Performance metrics

### Phase 2: Implement Lazy Loading

**Tasks:**
1. Create profiles directory structure
2. Generate individual profile JSONs
3. Implement on-demand loading in OrganizationProfile
4. Add caching in Zustand stores
5. Test with 50-100 profiles

**Timeline:** 2-3 days

**Deliverables:**
- `src/data/profiles/` directory with individual JSONs
- Profile loading service
- Caching implementation

### Phase 3: Backend Integration (If Needed)

**Tasks:**
1. Enable `REACT_APP_USE_BACKEND_API` flag
2. Connect to Flask BigQuery endpoints
3. Implement pagination for large queries
4. Add loading states and error handling
5. Performance testing with real backend

**Timeline:** 3-5 days

**Deliverables:**
- Backend API integration
- Pagination implementation
- Error handling and loading states

---

## 📋 Data File Structure

### Recommended Directory Layout

```
src/data/
├── organizations-summary.json    # Tier 1: 200-400 KB
├── metadata.json                 # Dataset info, version
├── profiles/                     # Tier 2: Lazy loaded
│   ├── california-medical-association.json
│   ├── pge-corporation.json
│   ├── california-teachers-association.json
│   └── ... (500-1000 files)
├── categories.json               # Category definitions
└── lobbyists-index.json          # Optional: Lobbyist directory
```

### Alternative: Chunked Approach

```
src/data/
├── orgs-chunk-001.json          # Orgs 1-100
├── orgs-chunk-002.json          # Orgs 101-200
├── orgs-chunk-003.json          # Orgs 201-300
└── ... (10-20 chunks of 100 orgs each)
```

**Benefits:**
- Smaller initial download
- Progressive loading
- Better caching granularity

**Drawbacks:**
- More HTTP requests
- Complex loading logic
- Cache management overhead

---

## 🚀 Migration Strategy

### From Current Demo to Real Data

#### Step 1: Analyze Real Data
```bash
# Determine actual CA lobby dataset size
# Count organizations, activities, date ranges
# Calculate estimated JSON sizes
```

#### Step 2: Choose Strategy
- **<500 orgs:** Use single JSON file
- **500-2000 orgs:** Use Tier 1 + Tier 2 approach ⭐
- **>2000 orgs:** Use backend API

#### Step 3: Generate Data Files
```bash
# Create organizations-summary.json
# Generate profile JSONs (if using Tier 2)
# Validate JSON structure
# Test file sizes
```

#### Step 4: Update Components
```javascript
// Replace generateSampleLobbyData() calls
// Use imported JSON files
// Add lazy loading for profiles
// Maintain demo mode fallback
```

#### Step 5: Performance Testing
- Test load times on 3G/4G/WiFi
- Measure bundle size impact
- Verify search performance
- Test pagination

#### Step 6: Deploy
- Deploy to Vercel staging
- Monitor build size
- Test production performance
- Enable for users

---

## 🎯 Specific Recommendations

### For CA Lobby Project

**Expected Dataset Size:** ~500-2,000 organizations (estimate pending confirmation)

**Recommended Approach:** **Hybrid Tiered (Tier 1 + Tier 2)**

**Implementation:**
1. **Tier 1:** `organizations-summary.json` with 500-1,000 orgs (250-400 KB)
2. **Tier 2:** Individual profile JSONs loaded on-demand (5-15 KB each)
3. **Tier 3:** Backend API for exports and advanced queries (already available)

**Performance Targets:**
- Initial load: <2 seconds on 3G
- Profile view: <1 second
- Search: <200ms (client-side)
- Total bundle: <900 KB

**Fallback:**
- Keep current demo data generator
- Use `REACT_APP_USE_DEMO_DATA` flag
- Switch between demo/real data easily

---

## 📊 Monitoring and Optimization

### Metrics to Track

1. **Bundle Size**
   - Initial bundle size
   - Total transferred size
   - Compression ratio

2. **Load Times**
   - Time to First Byte (TTFB)
   - First Contentful Paint (FCP)
   - Time to Interactive (TTI)

3. **Runtime Performance**
   - Search response time
   - Filter/sort time
   - Profile load time

4. **User Experience**
   - Bounce rate
   - Average session duration
   - Pages per session

### Optimization Techniques

**If bundle too large:**
- Split data into more chunks
- Use gzip compression
- Lazy load more aggressively
- Move to backend API

**If searches too slow:**
- Add client-side indexing
- Pre-calculate common queries
- Use Web Workers for filtering
- Implement debouncing

**If profile loads too slow:**
- Reduce initial activity count
- Paginate activities earlier
- Cache profiles more aggressively
- Preload top organizations

---

## 🔄 Maintenance and Updates

### Data Refresh Strategy

**Demo Data:**
- Update quarterly or as needed
- Regenerate with new date ranges
- Keep realistic spending amounts

**Real Data:**
- Daily backend updates (automated)
- Weekly client JSON updates (manual or scripted)
- Monthly full data refresh

### Version Control

**JSON Data Files:**
- Track in Git (if <500 KB)
- Use Git LFS for larger files
- Document data version in metadata.json

**Backup Strategy:**
- Keep previous version for rollback
- Test new data before deployment
- Validate JSON structure before commit

---

## ✅ Success Criteria

### Phase 1 Complete When:
- [ ] organizations-summary.json created (<400 KB)
- [ ] Load time <2s on 3G network
- [ ] Search works with real data
- [ ] Bundle size <900 KB total
- [ ] Demo mode still functional

### Phase 2 Complete When:
- [ ] Profile JSONs generated for top 100 orgs
- [ ] Lazy loading implemented
- [ ] Profile load time <1s
- [ ] Caching working in Zustand
- [ ] 50+ profiles tested

### Phase 3 Complete When:
- [ ] Backend API integrated
- [ ] Pagination working for all queries
- [ ] Export functionality operational
- [ ] Performance acceptable (<=3s queries)
- [ ] Error handling comprehensive

---

## 📚 References

### Project Documentation
- [MASTER_PROJECT_PLAN.md](../General/MASTER_PROJECT_PLAN.md)
- [DEMO_DATA_CONFIGURATION.md](../General/DEMO_DATA_CONFIGURATION.md)
- Phase 2b.2 State Management Completion Report

### Technical Resources
- React Performance: https://react.dev/learn/render-and-commit
- Web Performance: https://web.dev/performance/
- Vercel Bundle Analysis: https://vercel.com/docs/concepts/deployments/bundle-size

### Related Files
- `src/utils/sampleData.js` - Current demo data generator
- `src/stores/searchStore.js` - Search state management
- `src/components/Search.js` - Main search component
- `src/components/OrganizationProfile.js` - Profile page

---

## 🎯 Next Steps

1. **Immediate:** Analyze real CA lobby data to determine actual dataset size
2. **Week 1:** Implement Tier 1 summary data approach
3. **Week 2:** Add Tier 2 lazy loading if needed
4. **Week 3:** Performance testing and optimization
5. **Week 4:** Production deployment with real data

---

**Document Owner:** CA Lobby Project Team
**Last Reviewed:** October 24, 2025
**Next Review:** After real data analysis complete

**Status:** ✅ Strategy Defined - Awaiting Real Data Analysis
