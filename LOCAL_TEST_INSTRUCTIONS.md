# Local Testing Instructions

## Production Build Deployed Locally

**Status:** ✅ Production build is serving at **http://localhost:50361**

## What Has Been Fixed

### 1. Dashboard Charts (✅ Fixed)
- Replaced old demo organizations (California Medical Association, Google, Meta, etc.)
- Now shows only 6 real Alameda County organizations
- Uses `organizations-summary.json` data

### 2. Search Function Loading State (✅ Fixed)
- Added `finally` block with `setLoading(false)`
- Search now completes instead of hanging

### 3. Debug Logging Added (✅ Active)
- Logs when search button is clicked
- Logs query and filters
- Logs number of results generated
- Logs when results are set in store

## How to Test

### Test 1: Dashboard Charts
1. Navigate to http://localhost:50361
2. Sign in with Clerk authentication
3. Go to Dashboard
4. **Expected:** Chart should show only these 6 organizations:
   - ALAMEDA COUNTY
   - ALAMEDA, CITY OF
   - ALAMEDA COUNTY WASTE MANAGEMENT AUTHORITY
   - ALAMEDA UNIFIED SCHOOL DISTRICT
   - ALAMEDA ALLIANCE FOR HEALTH
   - ALAMEDA CORRIDOR-EAST CONSTRUCTION AUTHORITY
5. **Should NOT see:** California Medical Association, Google, Meta, Tesla, etc.

### Test 2: Search Functionality
1. Go to Search page (http://localhost:50361/search)
2. Open browser console (F12 → Console tab)
3. Type "alameda" in the search box
4. Click the "🔍 Search" button
5. **Expected console output:**
   ```
   Search button clicked - handleSearch triggered
   Query: alameda Has filters: false
   Generating search results...
   Search results generated: 6 results
   Results set in store
   Search completed successfully
   ```
6. **Expected UI:** Should see 6 results displayed below the search form

### Test 3: Empty Search
1. Clear the search box (leave it empty)
2. Click Search button
3. **Expected:** Error message "Please enter a search term or select at least one filter."

### Test 4: Organization Profile Links
1. Perform a search for "alameda"
2. Click on any organization name in the results
3. **Expected:** Navigate to organization profile page (e.g., `/organization/ALAMEDA%20COUNTY`)
4. **Expected:** Profile should show organization details, activities, charts

## Data Verification

### Organizations Data
- **Total Organizations:** 6
- **All from:** Alameda County
- **Data File:** `src/data/organizations-summary.json`
- **Profile Files:** `src/data/profiles/*.json` (6 files)

### Search Pattern Tests
| Query | Expected Matches |
|-------|-----------------|
| "alameda" | 6 matches (all organizations) |
| "county" | 2 matches (ALAMEDA COUNTY, ALAMEDA COUNTY WASTE MANAGEMENT AUTHORITY) |
| "city" | 1 match (ALAMEDA, CITY OF) |
| "" (empty) | Error message |

## Known Issues

### Issue: Search Button Does Nothing
**If you experience this:**
1. Open browser console (F12)
2. Check for JavaScript errors
3. Look for the debug logs listed in Test 2 above
4. **Copy all console output** and share it

**Possible causes:**
- Console logs not appearing → JavaScript not loading
- Logs appear but no results → `generateSearchResults()` function issue
- Results generated but not displayed → React rendering issue
- Error messages → Filter or query validation issue

## Build Information

- **Build File:** `build/static/js/main.bee2ca4e.js`
- **Bundle Size:** 195.27 KB (gzipped)
- **Build Date:** 2025-10-24
- **Latest Commit:** 9d1c34c7f
- **Debug Logging:** ✅ Enabled

## Vercel Deployment

The same build has also been deployed to Vercel. You can test there as well at your Vercel URL.

## Next Steps

1. Test all 4 scenarios above
2. Copy any console output showing errors or unexpected behavior
3. Report what you see vs what is expected
4. I can then fix any remaining issues based on your feedback

## Stop Local Server

When done testing:
```bash
lsof -ti:50361 | xargs kill -9
```
