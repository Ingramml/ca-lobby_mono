# CA LOBBY APPLICATION - COMPREHENSIVE MANUAL TESTING CHECKLIST
## Real Alameda County Data Deployment Verification

**Application URL:** https://ca-lobby-webapp.vercel.app (verify latest deployment)
**Test Date:** _____________
**Tester Name:** _____________
**Browser/Device:** _____________

---

## 📋 PRE-TESTING SETUP

### Prerequisites
- [ ] **Browser**: Chrome, Firefox, Safari, or Edge (latest version)
- [ ] **Network**: Stable internet connection
- [ ] **Auth Account**: Valid Clerk authentication account
- [ ] **Screen Size**: Test on desktop (1920x1080 recommended) first
- [ ] **Downloads**: Ensure browser can download files (check ~/Downloads/)

### Expected Data Overview
- **Total Organizations**: 6 real Alameda County organizations
- **Total Activities**: 2,823 lobby activities (2000-2025)
- **Data Source**: Real California lobby data from Alameda County

---

## 🔐 SECTION 1: AUTHENTICATION & INITIAL LOAD

### Test 1.1: Application Access
- [ ] **Navigate** to https://ca-lobby-webapp.vercel.app
- [ ] **Verify**: Page loads without errors (should see Clerk auth screen)
- [ ] **Expected**: Clean UI, no console errors (press F12 to check)
- [ ] **Load Time**: Initial page load < 3 seconds

### Test 1.2: Clerk Authentication
- [ ] **Click**: Sign In button
- [ ] **Enter**: Valid email/password OR use OAuth (Google, etc.)
- [ ] **Verify**: Successfully authenticated and redirected to Dashboard
- [ ] **Expected**: Welcome message shows your first name
- [ ] **Check**: User profile icon/button visible in header

### Test 1.3: Dashboard Initial State
- [ ] **Verify**: Dashboard page loads with all sections visible
- [ ] **Check**: "CA Lobby Data Insights" section present
- [ ] **Check**: Three charts visible (Lobby Trends, Organization, Category)
- [ ] **Check**: "System Status" section with 4-5 status cards
- [ ] **Check**: "Recent Search Activity" shows "No recent searches" initially

---

## 🔍 SECTION 2: SEARCH FUNCTIONALITY

### Test 2.1: Empty Search (Show All Organizations)
- [ ] **Navigate**: Click "Search" in navigation menu
- [ ] **Leave**: Search box empty
- [ ] **Click**: "🔍 Search" button
- [ ] **Expected**: 6 results displayed (all Alameda County organizations)
- [ ] **Verify Organizations Listed**:
  - [ ] ALAMEDA COUNTY (875 activities badge)
  - [ ] ALAMEDA, CITY OF (406 activities badge)
  - [ ] ALAMEDA COUNTY WASTE MANAGEMENT AUTHORITY (611 activities)
  - [ ] ALAMEDA UNIFIED SCHOOL DISTRICT (77 activities)
  - [ ] ALAMEDA ALLIANCE FOR HEALTH (266 activities)
  - [ ] ALAMEDA CORRIDOR-EAST CONSTRUCTION AUTHORITY (588 activities)
- [ ] **Check**: Each result shows organization name in blue (clickable)
- [ ] **Check**: Activity count badge visible next to each name
- [ ] **Check**: Description text under each organization
- [ ] **Check**: "Search Results (6 found)" header visible

### Test 2.2: Search by Keyword
- [ ] **Test 2.2a - Search "county"**: 2 results expected
- [ ] **Test 2.2b - Search "school"**: 1 result expected
- [ ] **Test 2.2c - Search "health"**: 1 result expected
- [ ] **Test 2.2d - Case insensitive**: All variations work

### Test 2.3: Search Edge Cases
- [ ] **No results search**: "xyzabc123" shows 0 results
- [ ] **Special characters**: "CORRIDOR-EAST" finds organization
- [ ] **Search history**: Recent searches appear in Dashboard

---

## 🏢 SECTION 3: ORGANIZATION PROFILES

### Test 3.1: Navigation to Profile
- [ ] **Click**: "ALAMEDA COUNTY" from search results
- [ ] **Expected**: Navigate to profile page
- [ ] **Load Time**: < 2 seconds

### Test 3.2: Profile Header & Breadcrumbs
- [ ] **Verify Breadcrumbs**: "Home / Search / ALAMEDA COUNTY"
- [ ] **Test**: Click each breadcrumb link
- [ ] **Check**: "← Back to Search" button works
- [ ] **Verify**: Export buttons visible (CSV & JSON)

### Test 3.3: Activity Summary Metrics
- [ ] **Verify 6 Metric Cards**:
  - [ ] Total Activities: 875
  - [ ] Date Range displayed
  - [ ] Total Spending shown
  - [ ] Active Lobbyists count
  - [ ] Registrations: 56
  - [ ] Organization Type: PURCHASER

### Test 3.4: Spending Trends Chart
- [ ] **Verify**: Chart loads and displays data
- [ ] **Test**: Hover shows tooltips
- [ ] **Check**: No console errors

### Test 3.5: Activity List & Pagination
- [ ] **Verify**: First 10 activities displayed
- [ ] **Test**: "Next Page" button works
- [ ] **Check**: Page numbers accurate (e.g., "Page 1 of 88")
- [ ] **Export**: Activities download as CSV

### Test 3.6: Export Functionality
- [ ] **CSV Export**: Downloads summary file
- [ ] **JSON Export**: Downloads complete profile
- [ ] **Verify**: Files contain correct data

### Test 3.7: Keyboard Navigation
- [ ] **ESC key**: Returns to search page
- [ ] **Tab navigation**: Focus moves through elements
- [ ] **Enter on breadcrumb**: Navigates correctly

---

## 🔄 SECTION 4: TEST ALL 6 ORGANIZATIONS

**Repeat key tests for each organization:**

### 4.1: ALAMEDA, CITY OF (406 activities)
- [ ] Profile loads correctly
- [ ] Exports work

### 4.2: ALAMEDA COUNTY WASTE MANAGEMENT AUTHORITY (611 activities)
- [ ] Profile loads correctly
- [ ] Pagination works (62 pages)

### 4.3: ALAMEDA UNIFIED SCHOOL DISTRICT (77 activities)
- [ ] Profile loads correctly
- [ ] 8 pages of activities

### 4.4: ALAMEDA ALLIANCE FOR HEALTH (266 activities)
- [ ] Profile loads correctly
- [ ] 27 pages of activities

### 4.5: ALAMEDA CORRIDOR-EAST CONSTRUCTION AUTHORITY (588 activities)
- [ ] Profile loads correctly
- [ ] 59 pages of activities

---

## ⚡ SECTION 5: PERFORMANCE TESTING

### Test 5.1: Load Times
- [ ] **Initial load**: < 5 seconds
- [ ] **Search results**: < 2 seconds
- [ ] **Profile load**: < 2 seconds
- [ ] **Chart rendering**: < 2 seconds

### Test 5.2: Bundle Size
- [ ] **Open DevTools** → Network
- [ ] **Check**: Main bundle < 200 KB (gzipped)
- [ ] **Verify**: Total transfer < 500 KB

### Test 5.3: Console Errors
- [ ] **No critical errors** (red in console)
- [ ] **Warnings acceptable** (yellow - document any)

---

## 📱 SECTION 6: RESPONSIVE DESIGN

### Test 6.1: Mobile (< 768px)
- [ ] **Resize to 375px** width
- [ ] **Verify**: Cards stack vertically
- [ ] **Check**: Navigation becomes mobile menu
- [ ] **Test**: All features accessible

### Test 6.2: Tablet (768px - 1024px)
- [ ] **Resize to 768px**
- [ ] **Verify**: 2-column layout
- [ ] **Test**: Charts resize properly

### Test 6.3: Desktop (> 1024px)
- [ ] **Full width** (1920px)
- [ ] **Verify**: 3-column grid
- [ ] **Check**: Proper spacing

---

## 🐛 SECTION 7: ERROR HANDLING

### Test 7.1: Invalid URLs
- [ ] **Try**: `/organization/FAKE_ORG`
- [ ] **Expected**: Error page with "Return to Search"

### Test 7.2: Network Issues
- [ ] **Set DevTools** to Offline
- [ ] **Expected**: Graceful error message

### Test 7.3: Data Integrity
- [ ] **Verify**: Activity counts match across search/profile
- [ ] **Check**: Date ranges consistent
- [ ] **Math**: Total activities = 2,823

---

## ✅ FINAL VERIFICATION

### Core Functionality
- [ ] ✅ Authentication works
- [ ] ✅ Search returns 6 organizations
- [ ] ✅ All profiles accessible
- [ ] ✅ Exports work
- [ ] ✅ Navigation smooth

### Performance
- [ ] ✅ Load times acceptable
- [ ] ✅ No memory leaks
- [ ] ✅ No console errors

### Data Accuracy
- [ ] ✅ 2,823 total activities
- [ ] ✅ Correct activity counts per org
- [ ] ✅ Date ranges accurate (2000-2025)

---

## 🐞 ISSUES FOUND

| Issue # | Section | Description | Severity | Status |
|---------|---------|-------------|----------|--------|
| 1 | | | High/Med/Low | Open/Fixed |
| 2 | | | | |

---

## 📊 TESTING SUMMARY

**Tests Passed**: _____ / _____
**Tests Failed**: _____
**Critical Issues**: _____

**Overall Status**: ✅ PASS / ❌ FAIL / ⚠️ PASS WITH ISSUES

---

## ✅ SIGN-OFF

**Tester**: _________________________
**Date**: _________________________
**Recommendation**: Ready for Production / Needs Fixes / Do Not Deploy

---

## 📚 QUICK REFERENCE

### Expected Organization Counts
1. ALAMEDA COUNTY: 875 activities
2. ALAMEDA, CITY OF: 406 activities
3. WASTE MANAGEMENT AUTHORITY: 611 activities
4. UNIFIED SCHOOL DISTRICT: 77 activities
5. ALLIANCE FOR HEALTH: 266 activities
6. CORRIDOR-EAST CONSTRUCTION: 588 activities

**Total**: 2,823 activities

### URLs to Test
- Dashboard: `/`
- Search: `/search`
- Example Profile: `/organization/ALAMEDA%20COUNTY`

### Performance Targets
- Initial load: < 5s
- Search: < 2s
- Profile: < 2s
- Bundle: < 200 KB (gzipped)

---

**END OF CHECKLIST**
