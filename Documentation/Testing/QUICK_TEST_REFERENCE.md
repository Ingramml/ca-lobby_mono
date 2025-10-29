# CA Lobby Search - Quick Test Reference

**URL**: http://localhost:3000/search
**Date**: September 29, 2025

## 🔍 **IMMEDIATE TEST SEARCHES** (5 guaranteed results)

### **Basic Organization Searches**
1. **"California Medical"** → Returns: California Medical Association ($125,000)
2. **"Tech Innovation"** → Returns: Tech Innovation Coalition ($89,000)
3. **"Environmental"** → Returns: Environmental Defense Alliance ($67,500)
4. **"Education"** → Returns: Education Reform Society ($52,000)
5. **"Small Business"** → Returns: Small Business Coalition ($43,200)

### **Lobbyist Name Searches**
1. **"John Smith"** → Returns: California Medical Association record
2. **"Sarah Johnson"** → Returns: Tech Innovation Coalition record
3. **"Michael Chen"** → Returns: Environmental Defense Alliance record
4. **"Emily Rodriguez"** → Returns: Education Reform Society record
5. **"David Wilson"** → Returns: Small Business Coalition record

### **Keyword Searches**
1. **"healthcare"** → Returns: California Medical Association (healthcare reform)
2. **"technology"** → Returns: Tech Innovation Coalition (technology policy)
3. **"climate"** → Returns: Environmental Defense Alliance (climate change)
4. **"education"** → Returns: Education Reform Society (educational funding)
5. **"regulatory"** → Returns: Small Business Coalition (regulatory relief)

### **Filter Testing (Advanced Filters Section)**
1. **Organization Filter: "Medical"** → Isolates: California Medical Association
2. **Organization Filter: "Tech"** → Isolates: Tech Innovation Coalition
3. **Lobbyist Filter: "John"** → Isolates: John Smith records
4. **Lobbyist Filter: "Sarah"** → Isolates: Sarah Johnson records
5. **Date Range: "All Time"** → Shows: All 5 records

### **No Results Tests** (should show "No results found")
1. **"Pharmaceutical"** → No results (not in demo data)
2. **"Banking"** → No results (not in demo data)
3. **"Robert Jones"** → No results (lobbyist not in demo)
4. **"Transportation"** → No results (topic not in demo)
5. **"XYZ Corporation"** → No results (organization not in demo)

---

## 📱 **MOBILE TESTING CHECKLIST**

### **Touch Targets** (should all be ≥44px)
- [ ] Search input field
- [ ] Search button
- [ ] Filter dropdown menus
- [ ] Navigation links
- [ ] Any action buttons

### **Mobile Layout** (test at different widths)
- [ ] 320px width (small phone)
- [ ] 768px width (tablet)
- [ ] Search form stacks vertically on mobile
- [ ] No horizontal scrolling at any width
- [ ] Navigation transforms to mobile menu

### **iOS Specific**
- [ ] Search input doesn't zoom (16px font size)
- [ ] Touch feedback feels responsive
- [ ] No blue highlight on tap (webkit-tap-highlight)

---

## ✅ **EXPECTED FUNCTIONALITY**

### **Working Features**
- ✅ Basic text search across organization, lobbyist, and description
- ✅ Organization filter in Advanced Filters section
- ✅ Lobbyist filter in Advanced Filters section
- ✅ Date range filter dropdown
- ✅ Search results display with proper formatting
- ✅ "No results found" for non-matching searches
- ✅ Case-insensitive search
- ✅ Partial string matching

### **Demo Mode Behavior**
- ✅ All searches use sample data (5 records total)
- ✅ Demo banner shows explaining this is demonstration data
- ✅ Search functionality works without backend connection
- ✅ Results display consistently

---

## 🐛 **WHAT TO WATCH FOR**

### **Potential Issues**
- Search not returning expected results
- Filters not working in combination
- Mobile layout breaking at certain widths
- Console errors in browser developer tools
- Blank screens or loading states that don't resolve

### **If Something Breaks**
1. Check browser console for errors
2. Verify you're using exact test terms from this guide
3. Try refreshing the page
4. Test on different screen sizes
5. Clear browser cache if needed

---

## 📊 **SUCCESS CRITERIA**

**Phase 2d Complete When:**
- ✅ All 25 test searches work as expected
- ✅ Mobile layout responsive at all breakpoints
- ✅ Touch interactions feel smooth and responsive
- ✅ No JavaScript errors in console
- ✅ Search results display properly formatted
- ✅ Advanced filters work correctly

---

**Test Server**: http://localhost:3000 (should be running)
**Navigation**: Click "🔍 Search" in the top navigation
**Authentication**: Sign in required to access search functionality