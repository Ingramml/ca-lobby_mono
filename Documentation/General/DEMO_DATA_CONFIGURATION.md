# Demo Data Configuration

**Project:** California Lobby Search System
**Last Updated:** September 30, 2025
**Status:** ACTIVE - Demo Data Mode

---

## 📋 Overview

The CA Lobby application is currently configured to use **demo/fake data** for all search operations. This allows frontend development and testing without requiring the Flask backend API or BigQuery database to be running.

---

## 🎯 Current Configuration

### Default Behavior
- **All deployments use demo data** until explicitly configured otherwise
- No backend API calls are made by default
- No Flask server required for local development
- No BigQuery integration needed for testing

### Demo Data Mode
**Status:** ✅ **ACTIVE** (Default)
- File: `src/components/Search.js`
- Mode: Demo data only
- Backend API: Disabled by default

---

## 🔧 How It Works

### Search.js Configuration

The Search component checks for an environment variable to determine data source:

```javascript
// Line 201 in Search.js
const useBackend = process.env.REACT_APP_USE_BACKEND_API === 'true';

if (!useBackend) {
  // Use demo data (default behavior)
  const demoResults = generateDemoSearchResults(query, filters);
  // ... rest of demo data logic
}
```

**Default:** `useBackend = false` (no environment variable set)
- Always uses demo data
- Never calls Flask API
- No connection errors

---

## 📊 Demo Data Contents

### Organizations (10 Total Activities)

1. **California Medical Association** (3 activities)
   - Category: Healthcare
   - Lobbyists: John Smith, Dr. Maria Garcia, Robert Thompson
   - Total Amount: $277,500
   - Dates: Sept 15, Aug 20, July 10 (2024)

2. **Tech Innovation Coalition** (2 activities)
   - Category: Technology
   - Lobbyists: Sarah Johnson, Kevin Zhang
   - Total Amount: $184,000
   - Dates: Sept 10, Aug 15 (2024)

3. **Environmental Defense Alliance** (2 activities)
   - Category: Environment
   - Lobbyists: Michael Chen, Jennifer Martinez
   - Total Amount: $139,500
   - Dates: Sept 5, Aug 1 (2024)

4. **Education Reform Society** (1 activity)
   - Category: Education
   - Lobbyist: Emily Rodriguez
   - Amount: $52,000
   - Date: Aug 28 (2024)

5. **Small Business Coalition** (1 activity)
   - Category: Finance
   - Lobbyist: David Wilson
   - Amount: $43,200
   - Date: Aug 20 (2024)

### Data Fields
Each activity includes:
- `organization` - Organization name
- `lobbyist` - Lobbyist name
- `description` - Activity description
- `amount` - Dollar amount (integer)
- `date` - Activity date (YYYY-MM-DD)
- `filing_date` - Same as date
- `category` - Category slug (healthcare, technology, environment, education, finance)
- `activity_description` - Detailed description

---

## 🚀 Enabling Backend API (Future)

### When Backend Integration Is Ready

To enable backend API calls:

1. **Create `.env` file** in project root:
   ```bash
   REACT_APP_USE_BACKEND_API=true
   ```

2. **Start Flask backend** (in separate terminal):
   ```bash
   cd webapp/backend
   python run.py
   # Backend runs on http://localhost:5001
   ```

3. **Restart React dev server**:
   ```bash
   npm start
   ```

### Backend Requirements
- Flask server running on port 5001
- BigQuery credentials configured
- API endpoints available at `/api/search`

---

## ⚠️ Important Notes

### For Developers
1. **No Backend Required** - You can develop and test without Flask/BigQuery
2. **Console Messages** - Will show "Demo search completed" when using fake data
3. **Automatic Fallback** - Even if `REACT_APP_USE_BACKEND_API=true`, errors fallback to demo data
4. **No API Errors** - You won't see "Failed to fetch" or connection refused errors

### For Deployment
1. **Vercel/Production** - Currently uses demo data
2. **No Backend Configured** - No Flask backend deployed yet
3. **Full Functionality** - All features work with demo data
4. **Organization Profiles** - Work perfectly with demo organizations

---

## 🧪 Testing Demo Data

### Local Testing
1. Navigate to http://localhost:3000
2. Sign in with Clerk
3. Go to Search page
4. Click "Search" (leave query empty to see all data)
5. Click organization names to see profiles

### Demo Organizations to Test
- **California Medical Association** - Multiple activities, rich data
- **Tech Innovation Coalition** - 2 activities, technology category
- **Environmental Defense Alliance** - 2 activities, green category
- **Education Reform Society** - Single activity
- **Small Business Coalition** - Single activity, finance category

---

## 📁 Related Files

### Source Files
- **Search Component**: `src/components/Search.js` (lines 6-150 for demo data)
- **Organization Profile**: `src/components/OrganizationProfile.js`
- **API Config**: `src/config/api.js` (not used in demo mode)

### Documentation
- **Phase 1 Completion**: `Documentation/Phase2/Reports/ORGANIZATION_PROFILE_PHASE1_COMPLETION_REPORT.md`
- **Master Plan**: `Documentation/General/MASTER_PROJECT_PLAN.md`
- **CLAUDE.md**: Project reference guide

---

## 🔄 Future Backend Integration

### Planned Timeline
**Not scheduled yet** - Backend integration will be a separate phase

### What Will Change
1. Environment variable will enable backend
2. Flask API endpoints will be called
3. BigQuery data will be queried
4. Demo data will become fallback only

### What Won't Change
1. Organization Profile feature remains the same
2. UI/UX stays identical
3. Demo data available as fallback
4. Component structure unchanged

---

## 📞 Quick Reference

### Check Current Mode
Look at console logs in browser DevTools:
- **Demo Mode**: "Demo search completed: X results"
- **Backend Mode**: "Backend search completed: {...}"
- **Fallback**: "Fallback to demo data: X results"

### Environment Variables
```bash
# Demo data only (default - no .env needed)
# No environment variable set

# Backend API mode (future)
REACT_APP_USE_BACKEND_API=true
```

### Restart After Changes
```bash
# Kill existing servers
pkill -f "react-scripts"

# Start fresh
npm start
```

---

## ✅ Current Status Summary

**Data Source:** Demo/Fake Data ✅
**Backend Required:** No ❌
**BigQuery Required:** No ❌
**Flask API:** Not running ❌
**Organization Profiles:** Fully functional ✅
**Search Feature:** Fully functional ✅
**Local Development:** Working ✅

---

**Last Verified:** September 30, 2025
**Next Review:** When backend integration phase begins

---