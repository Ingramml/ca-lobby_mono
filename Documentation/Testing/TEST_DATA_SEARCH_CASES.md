# CA Lobby Search System - Comprehensive Test Data & Cases

**Document Purpose:** Comprehensive test cases for validating all CA Lobby search functionality
**Created:** September 29, 2025
**Last Updated:** September 29, 2025
**Test Environment:** Demo Mode (Production Environment)

---

## 🎯 **SEARCH FUNCTIONALITY TEST CASES**

### **Available Demo Data (Current)**
The system contains 5 demo lobby records with the following structure:
- **Organizations**: California Medical Association, Tech Innovation Coalition, Environmental Defense Alliance, Education Reform Society, Small Business Coalition
- **Lobbyists**: John Smith, Sarah Johnson, Michael Chen, Emily Rodriguez, David Wilson
- **Date Range**: August 20, 2024 - September 15, 2024
- **Amount Range**: $43,200 - $125,000

---

## 📋 **TEST CASE CATEGORIES**

### **1. BASIC SEARCH FUNCTIONALITY**

#### **Test Case 1A: Organization Search**
**Function**: Search by organization name
**Test Data Points:**
1. **"California Medical"** → Should return: California Medical Association ($125,000)
2. **"Tech Innovation"** → Should return: Tech Innovation Coalition ($89,000)
3. **"Environmental"** → Should return: Environmental Defense Alliance ($67,500)
4. **"Education"** → Should return: Education Reform Society ($52,000)
5. **"Small Business"** → Should return: Small Business Coalition ($43,200)

**Expected Results**: Each search should return exactly 1 matching record
**Validation**: Verify organization name appears in results with correct amount

#### **Test Case 1B: Lobbyist Name Search**
**Function**: Search by lobbyist name
**Test Data Points:**
1. **"John Smith"** → Should return: California Medical Association record
2. **"Sarah Johnson"** → Should return: Tech Innovation Coalition record
3. **"Michael Chen"** → Should return: Environmental Defense Alliance record
4. **"Emily Rodriguez"** → Should return: Education Reform Society record
5. **"David Wilson"** → Should return: Small Business Coalition record

**Expected Results**: Each search should return exactly 1 matching record
**Validation**: Verify lobbyist name matches search term exactly

#### **Test Case 1C: Description/Activity Search**
**Function**: Search by keywords in description or activity
**Test Data Points:**
1. **"healthcare"** → Should return: California Medical Association (healthcare reform)
2. **"technology"** → Should return: Tech Innovation Coalition (technology policy)
3. **"climate"** → Should return: Environmental Defense Alliance (climate change)
4. **"education"** → Should return: Education Reform Society (educational funding)
5. **"regulatory"** → Should return: Small Business Coalition (regulatory relief)

**Expected Results**: Each search should return at least 1 matching record
**Validation**: Verify search terms appear in description or activity_description

---

### **2. ADVANCED FILTER FUNCTIONALITY**

#### **Test Case 2A: Organization Filter (Advanced Filters Section)**
**Function**: Filter results using organization filter field
**Test Data Points:**
1. **Filter: "Medical"** → Should return: California Medical Association only
2. **Filter: "Tech"** → Should return: Tech Innovation Coalition only
3. **Filter: "Environmental"** → Should return: Environmental Defense Alliance only
4. **Filter: "Education"** → Should return: Education Reform Society only
5. **Filter: "Business"** → Should return: Small Business Coalition only

**Expected Results**: Each filter should isolate specific organization
**Validation**: Only matching organization appears in filtered results

#### **Test Case 2B: Lobbyist Filter (Advanced Filters Section)**
**Function**: Filter results using lobbyist filter field
**Test Data Points:**
1. **Filter: "John"** → Should return: John Smith (California Medical Association)
2. **Filter: "Sarah"** → Should return: Sarah Johnson (Tech Innovation Coalition)
3. **Filter: "Michael"** → Should return: Michael Chen (Environmental Defense Alliance)
4. **Filter: "Emily"** → Should return: Emily Rodriguez (Education Reform Society)
5. **Filter: "David"** → Should return: David Wilson (Small Business Coalition)

**Expected Results**: Each filter should isolate specific lobbyist
**Validation**: Only matching lobbyist appears in filtered results

#### **Test Case 2C: Date Range Filter**
**Function**: Filter results by date range selection
**Test Data Points:**
1. **"Last Month"** → Should return: All 5 records (all within last month)
2. **"Last Quarter"** → Should return: All 5 records (all within last quarter)
3. **"Last Year"** → Should return: All 5 records (all within last year)
4. **"All Time"** → Should return: All 5 records (default setting)
5. **"Custom Range"** → Should show: Custom date picker option

**Expected Results**: Filter should include/exclude based on date ranges
**Validation**: Verify date filtering logic matches selected range

#### **Test Case 2D: Category Filter**
**Function**: Filter results by category selection
**Test Data Points:**
1. **"Healthcare"** → Should return: California Medical Association (if categorized)
2. **"Technology"** → Should return: Tech Innovation Coalition (if categorized)
3. **"Environment"** → Should return: Environmental Defense Alliance (if categorized)
4. **"Education"** → Should return: Education Reform Society (if categorized)
5. **"Finance"** → Should return: No results (no financial organizations in demo)

**Expected Results**: Category filtering should match organization types
**Validation**: Verify categorization logic is consistent

---

### **3. COMBINED SEARCH & FILTER FUNCTIONALITY**

#### **Test Case 3A: Search + Organization Filter**
**Function**: Combine search query with organization filter
**Test Data Points:**
1. **Search: "healthcare" + Org Filter: "Medical"** → Should return: California Medical Association
2. **Search: "policy" + Org Filter: "Tech"** → Should return: Tech Innovation Coalition
3. **Search: "climate" + Org Filter: "Environmental"** → Should return: Environmental Defense Alliance
4. **Search: "funding" + Org Filter: "Education"** → Should return: Education Reform Society
5. **Search: "business" + Org Filter: "Coalition"** → Should return: Small Business Coalition

**Expected Results**: Results should match both search term AND organization filter
**Validation**: Verify AND logic between search and filters

#### **Test Case 3B: Search + Lobbyist Filter**
**Function**: Combine search query with lobbyist filter
**Test Data Points:**
1. **Search: "medical" + Lobbyist Filter: "John"** → Should return: John Smith record
2. **Search: "innovation" + Lobbyist Filter: "Sarah"** → Should return: Sarah Johnson record
3. **Search: "environmental" + Lobbyist Filter: "Michael"** → Should return: Michael Chen record
4. **Search: "reform" + Lobbyist Filter: "Emily"** → Should return: Emily Rodriguez record
5. **Search: "regulatory" + Lobbyist Filter: "David"** → Should return: David Wilson record

**Expected Results**: Results should match both search term AND lobbyist filter
**Validation**: Verify filtering accuracy with multiple criteria

---

### **4. EDGE CASE & ERROR HANDLING**

#### **Test Case 4A: No Results Scenarios**
**Function**: Validate behavior when no matches found
**Test Data Points:**
1. **"Pharmaceutical"** → Should return: No results (organization not in demo)
2. **"Banking"** → Should return: No results (industry not in demo)
3. **"Robert Jones"** → Should return: No results (lobbyist not in demo)
4. **"Transportation"** → Should return: No results (topic not in demo)
5. **"Agriculture"** → Should return: No results (sector not in demo)

**Expected Results**: Display "No results found" message appropriately
**Validation**: Verify graceful handling of empty result sets

#### **Test Case 4B: Partial Match Testing**
**Function**: Validate partial string matching
**Test Data Points:**
1. **"Med"** → Should return: California Medical Association (partial org name)
2. **"Tech"** → Should return: Tech Innovation Coalition (partial org name)
3. **"Smith"** → Should return: John Smith record (partial lobbyist name)
4. **"Johnson"** → Should return: Sarah Johnson record (partial lobbyist name)
5. **"health"** → Should return: California Medical Association (partial description)

**Expected Results**: Partial matches should work correctly
**Validation**: Verify case-insensitive partial matching

#### **Test Case 4C: Case Sensitivity Testing**
**Function**: Validate case-insensitive search
**Test Data Points:**
1. **"CALIFORNIA MEDICAL"** → Should return: California Medical Association
2. **"tech innovation"** → Should return: Tech Innovation Coalition
3. **"JOHN SMITH"** → Should return: John Smith record
4. **"sarah johnson"** → Should return: Sarah Johnson record
5. **"HEALTHCARE"** → Should return: California Medical Association

**Expected Results**: Case should not affect search results
**Validation**: Verify consistent case-insensitive matching

---

### **5. USER INTERFACE & EXPERIENCE TESTING**

#### **Test Case 5A: Mobile Responsiveness**
**Function**: Validate mobile search experience
**Test Data Points:**
1. **Mobile Search Input**: Touch-friendly, no zoom on iOS (16px font)
2. **Mobile Filter Toggles**: Easy thumb navigation, proper spacing
3. **Mobile Results Display**: Readable cards, proper spacing
4. **Mobile Navigation**: Smooth scrolling, touch targets ≥44px
5. **Mobile Performance**: Fast search response, smooth animations

**Expected Results**: Seamless mobile experience across devices
**Validation**: Test on actual mobile devices or browser dev tools

#### **Test Case 5B: Search History & Persistence**
**Function**: Validate search history and saved searches
**Test Data Points:**
1. **Search History**: Recent searches appear in dashboard
2. **Filter Persistence**: Last used filters remembered between sessions
3. **Saved Searches**: Ability to save frequent searches (if implemented)
4. **Clear History**: Option to clear search history (if implemented)
5. **Session State**: Search state maintained during navigation

**Expected Results**: User preferences and history properly maintained
**Validation**: Verify Zustand store persistence functionality

---

## 🛠️ **TESTING PROTOCOL**

### **Step-by-Step Testing Process**
1. **Navigate to Search Page**: http://localhost:3000/search
2. **Execute Test Case**: Enter test data point
3. **Verify Results**: Confirm expected outcome
4. **Document Results**: Record pass/fail status
5. **Test Next Case**: Continue through all test points

### **Success Criteria**
- ✅ All basic search functions return expected results
- ✅ Advanced filters work correctly in isolation
- ✅ Combined search + filter logic functions properly
- ✅ Edge cases handled gracefully
- ✅ Mobile experience is smooth and functional

### **Failure Investigation**
If any test case fails:
1. **Check Console**: Look for JavaScript errors
2. **Verify Data**: Confirm test data exists in demo set
3. **Test Isolation**: Try simpler version of failed test
4. **Document Issue**: Record specific failure details
5. **Report Bug**: Create detailed bug report with reproduction steps

---

## 📊 **EXPECTED RESULTS SUMMARY**

### **Demo Data Coverage**
- **5 Organizations**: Complete coverage of organization search
- **5 Lobbyists**: Complete coverage of lobbyist search
- **5 Date Ranges**: All within recent 2024 timeframe
- **5 Amount Levels**: Range from $43K to $125K
- **Multiple Industries**: Healthcare, Tech, Environment, Education, Business

### **Search Function Coverage**
- **Basic Text Search**: ✅ Organization, Lobbyist, Description
- **Advanced Filters**: ✅ Organization, Lobbyist, Date Range, Category
- **Combined Search**: ✅ Search + Multiple Filters
- **Edge Cases**: ✅ No Results, Partial Matches, Case Insensitive
- **User Experience**: ✅ Mobile Responsive, State Persistence

---

**Total Test Cases**: 25 individual test points across 5 major functional areas
**Test Coverage**: 100% of implemented search functionality
**Test Environment**: Demo mode with 5 representative lobby records
**Validation Method**: Manual testing with documented expected results

---

*This document serves as the comprehensive testing guide for validating all CA Lobby search functionality using the available demo data set.*