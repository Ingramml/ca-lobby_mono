# BigQuery Integration on Vercel Deployment Plan

**Project:** California Lobby Search System
**Phase:** Backend Integration Enablement
**Date Created:** October 2, 2025
**Status:** Planning Phase
**Dependencies:** Phase 1.1 (BigQuery Infrastructure), Phase 1.3 (Backend API)

---

## 📋 Executive Summary

This plan outlines the steps to enable BigQuery database integration for the CA Lobby application on Vercel deployments. The BigQuery infrastructure and backend API code already exist (completed in Phase 1.1 and 1.3), but are currently running in **demo data mode**. This plan covers configuration, deployment, testing, and monitoring for production BigQuery integration.

---

## 🎯 Current State Analysis

### ✅ What Already Exists

1. **BigQuery Infrastructure** (Phase 1.1 - Completed)
   - Complete data pipeline with 15+ Python scripts
   - Automated data ingestion from Big Local News (BLN) API
   - BigQuery dataset: `ca_lobby`
   - Production-ready SQL queries
   - Daily data synchronization

2. **Backend API** (Phase 1.3 - Completed)
   - Flask API with BigQuery integration code
   - Files: `database.py`, `data_service.py`, `app.py`
   - Authentication with Clerk
   - Search endpoints ready
   - Health check monitoring
   - **Currently in mock data mode**

3. **Frontend** (Phase 2 - Completed)
   - React app with search functionality
   - Organization profile pages
   - Environment variable support for backend toggle
   - Automatic fallback to demo data

### ⚠️ Current Configuration

**Demo Data Mode Active:**
- `USE_MOCK_DATA=true` (backend default)
- `REACT_APP_USE_BACKEND_API` not set (frontend uses demo data)
- No BigQuery credentials configured on Vercel
- Flask backend not deployed

---

## 🏗️ Architecture Overview

### Current Architecture (Demo Mode)
```
React Frontend (Vercel)
    ↓
Demo Data (sampleData.js)
    ↓
No backend calls
```

### Target Architecture (BigQuery Enabled)
```
React Frontend (Vercel)
    ↓
Flask Backend API (Vercel Serverless Functions)
    ↓
BigQuery Database (Google Cloud)
    ↓
CA Lobby Dataset
```

---

## 📊 Implementation Plan

### Phase 1: Prerequisites & Preparation

#### 1.1: Verify BigQuery Dataset Status
**Duration:** 1-2 hours

**Tasks:**
- [ ] Verify BigQuery dataset `ca_lobby` exists and is current
- [ ] Check data freshness (last update timestamp)
- [ ] Validate table schemas match API expectations
- [ ] Test Phase 1.1 data pipeline is still operational
- [ ] Document current record counts per table

**Validation Queries:**
```sql
-- Check dataset exists
SELECT schema_name
FROM `PROJECT_ID.INFORMATION_SCHEMA.SCHEMATA`
WHERE schema_name = 'ca_lobby';

-- Check table record counts
SELECT table_name, row_count
FROM `ca_lobby.__TABLES__`;

-- Verify recent data
SELECT MAX(filing_date) as latest_filing
FROM `ca_lobby.lobby_activities`;
```

**Deliverables:**
- Dataset health report
- Table inventory with record counts
- Data freshness verification

---

#### 1.2: Service Account & Credentials Setup
**Duration:** 2-3 hours

**Tasks:**
- [ ] Create dedicated service account for Vercel deployment
- [ ] Assign minimum required permissions (BigQuery Data Viewer, BigQuery Job User)
- [ ] Generate JSON key file
- [ ] Test credentials locally with backend API
- [ ] Document credential rotation policy

**Service Account Permissions:**
```
roles/bigquery.dataViewer     # Read access to ca_lobby dataset
roles/bigquery.jobUser        # Execute queries
```

**Testing:**
```bash
# Test credentials locally
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
cd webapp/backend
python -c "from database import db; print(db.health_check())"
```

**Security Considerations:**
- Use service account with minimal permissions
- Never commit credentials to git
- Rotate credentials every 90 days
- Monitor access logs in Google Cloud Console

**Deliverables:**
- Service account created
- JSON credentials file (stored securely)
- Local connection test passed
- Security documentation

---

### Phase 2: Backend Deployment Configuration

#### 2.1: Convert Flask Backend to Vercel Serverless Functions
**Duration:** 4-6 hours

**Current State:**
- Flask app in `webapp/backend/`
- Designed for traditional server deployment
- Needs adaptation for Vercel serverless

**Vercel Serverless Approach:**

**Option A: Vercel Python Runtime** (Recommended)
- Create `api/` directory in project root
- Convert Flask routes to Vercel serverless functions
- Each endpoint becomes a separate file

**Directory Structure:**
```
CA_lobby/
├── api/                          # Vercel serverless functions
│   ├── search.py                 # /api/search endpoint
│   ├── organization.py           # /api/organization endpoint
│   ├── health.py                 # /api/health endpoint
│   └── _database.py              # Shared database module
├── webapp/backend/               # Original Flask app (reference)
├── src/                          # React frontend
└── vercel.json                   # Updated configuration
```

**Updated `vercel.json`:**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    },
    {
      "src": "api/**/*.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ],
  "env": {
    "BIGQUERY_DATASET": "@bigquery_dataset",
    "USE_MOCK_DATA": "@use_mock_data"
  }
}
```

**Sample Serverless Function** (`api/search.py`):
```python
from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'webapp', 'backend'))

from data_service import DataService
from _database import get_database

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse query parameters
        query = self.parse_query_params()

        # Execute search
        db = get_database()
        service = DataService(db)
        results = service.search_lobby_activities(query)

        # Return JSON response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        self.wfile.write(json.dumps(results).encode())
        return
```

**Tasks:**
- [ ] Create `api/` directory structure
- [ ] Convert Flask routes to serverless handlers
- [ ] Adapt database connection for serverless (connection pooling)
- [ ] Update imports and module paths
- [ ] Test locally with `vercel dev`
- [ ] Handle cold start optimization

**Option B: Separate Backend Deployment** (Alternative)
- Deploy Flask backend separately on Vercel or other platform
- Frontend calls external API endpoint
- Simpler adaptation but increased latency

**Deliverables:**
- Serverless function implementations
- Updated `vercel.json`
- Local testing passed with `vercel dev`
- Cold start performance benchmarks

---

#### 2.2: Environment Variables Configuration
**Duration:** 1 hour

**Vercel Environment Variables Setup:**

1. **Navigate to Vercel Dashboard:**
   - Project: CA Lobby
   - Settings → Environment Variables

2. **Add Required Variables:**

| Variable Name | Value | Environment | Type |
|---------------|-------|-------------|------|
| `USE_MOCK_DATA` | `false` | Production, Preview | Plain Text |
| `BIGQUERY_DATASET` | `ca_lobby` | Production, Preview | Plain Text |
| `GOOGLE_APPLICATION_CREDENTIALS` | `[JSON content]` | Production | Secret |
| `REACT_APP_USE_BACKEND_API` | `true` | Production, Preview | Plain Text |

**Google Credentials Handling:**

**Option A: Environment Variable** (Recommended for Vercel)
```bash
# Store entire JSON key as environment variable
GOOGLE_APPLICATION_CREDENTIALS='{"type":"service_account","project_id":"...","private_key":"..."}'
```

**Option B: Vercel Secrets**
```bash
# Use Vercel CLI to add secret
vercel secrets add google-credentials-json '{"type":"service_account",...}'

# Reference in vercel.json
"env": {
  "GOOGLE_APPLICATION_CREDENTIALS": "@google-credentials-json"
}
```

**Backend Code Update** (`api/_database.py`):
```python
import json
import os
from google.cloud import bigquery
from google.oauth2 import service_account

def get_credentials():
    """Load credentials from environment variable."""
    creds_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

    if creds_json:
        # Parse JSON from environment variable
        creds_dict = json.loads(creds_json)
        credentials = service_account.Credentials.from_service_account_info(creds_dict)
        return credentials

    # Fallback for local development with file path
    creds_path = os.getenv('CREDENTIALS_LOCATION')
    if creds_path and os.path.exists(creds_path):
        credentials = service_account.Credentials.from_service_account_file(creds_path)
        return credentials

    raise ValueError("No BigQuery credentials found")
```

**Tasks:**
- [ ] Add all environment variables to Vercel dashboard
- [ ] Configure for Production and Preview environments
- [ ] Update backend code to read credentials from JSON string
- [ ] Test with `vercel env pull` locally
- [ ] Document variable purposes

**Deliverables:**
- All variables configured on Vercel
- Backend code updated for env-based credentials
- Local testing with pulled environment
- Environment variable documentation

---

### Phase 3: Frontend Configuration

#### 3.1: Update Frontend to Use Backend API
**Duration:** 2-3 hours

**Current State:**
- Frontend uses demo data by default
- Backend toggle via `REACT_APP_USE_BACKEND_API`

**Changes Needed:**

**File: `src/components/Search.js`**
```javascript
// Current (lines 200-210)
const useBackend = process.env.REACT_APP_USE_BACKEND_API === 'true';

// Update API endpoint for Vercel deployment
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

// Fetch from backend
const response = await fetch(`${API_BASE_URL}/search?${queryParams}`, {
  headers: {
    'Authorization': `Bearer ${await clerk.session.getToken()}`
  }
});
```

**Environment Variables for Frontend:**
```bash
# Production (.env.production)
REACT_APP_USE_BACKEND_API=true
REACT_APP_API_URL=/api

# Development (.env.development)
REACT_APP_USE_BACKEND_API=false  # Keep demo data for dev
```

**Error Handling & Fallback:**
```javascript
try {
  if (useBackend) {
    const response = await fetch(API_URL);
    const data = await response.json();

    if (data.error) {
      console.warn('Backend error, falling back to demo data:', data.error);
      return generateDemoSearchResults(query, filters);
    }

    return data;
  }
} catch (error) {
  console.error('Backend call failed, using demo data:', error);
  return generateDemoSearchResults(query, filters);
}
```

**Tasks:**
- [ ] Update API endpoints to use environment variable
- [ ] Add authentication headers (Clerk JWT)
- [ ] Implement graceful fallback to demo data
- [ ] Update error messages for production
- [ ] Test backend connectivity
- [ ] Add loading states for API calls

**Deliverables:**
- Updated Search component
- Environment-based API configuration
- Fallback mechanisms tested
- Loading states implemented

---

#### 3.2: Update Organization Profile Component
**Duration:** 1-2 hours

**File: `src/components/OrganizationProfile.js`**

**Backend Integration:**
```javascript
useEffect(() => {
  const fetchOrganizationData = async () => {
    const useBackend = process.env.REACT_APP_USE_BACKEND_API === 'true';

    if (useBackend) {
      try {
        const response = await fetch(
          `/api/organization?name=${encodeURIComponent(organizationName)}`,
          {
            headers: {
              'Authorization': `Bearer ${await clerk.session.getToken()}`
            }
          }
        );

        const data = await response.json();
        setOrganizationData(data);
      } catch (error) {
        console.error('Failed to fetch organization:', error);
        // Fallback to demo data
        setOrganizationData(getDemoOrganization(organizationName));
      }
    } else {
      setOrganizationData(getDemoOrganization(organizationName));
    }
  };

  fetchOrganizationData();
}, [organizationName]);
```

**Tasks:**
- [ ] Add backend API call for organization data
- [ ] Maintain demo data fallback
- [ ] Update related organizations endpoint
- [ ] Test with real BigQuery data
- [ ] Verify all profile sections work

**Deliverables:**
- Backend-integrated organization profile
- Fallback mechanisms
- All features tested with real data

---

### Phase 4: Deployment & Testing

#### 4.1: Staged Deployment Strategy
**Duration:** 1 day

**Deployment Stages:**

**Stage 1: Preview Deployment**
```bash
# Deploy to preview environment first
git checkout -b feature/bigquery-integration
# Make changes
git add .
git commit -m "Feature: Enable BigQuery backend integration"
git push origin feature/bigquery-integration
# Vercel automatically creates preview deployment
```

**Stage 2: Test Preview Environment**
- Verify environment variables loaded
- Test search functionality with real data
- Test organization profiles
- Check error handling and fallbacks
- Monitor BigQuery queries in Google Cloud Console
- Verify authentication works
- Test pagination with large datasets

**Stage 3: Production Deployment**
```bash
# After preview testing passes
git checkout main
git merge feature/bigquery-integration
git push origin main
# Vercel deploys to production
```

**Rollback Plan:**
```bash
# If issues arise
git revert <commit-hash>
git push origin main

# Or set environment variable
vercel env add USE_MOCK_DATA
# Value: true
# Environment: Production
```

**Tasks:**
- [ ] Deploy to preview environment
- [ ] Complete preview testing checklist
- [ ] Monitor for errors
- [ ] Merge to production
- [ ] Monitor production deployment
- [ ] Document rollback procedures

**Deliverables:**
- Preview deployment successful
- All tests passed
- Production deployment completed
- Monitoring in place

---

#### 4.2: Integration Testing Checklist
**Duration:** 4-6 hours

**Test Cases:**

**1. Search Functionality**
- [ ] Empty search returns results
- [ ] Search by organization name
- [ ] Search by lobbyist name
- [ ] Filter by date range
- [ ] Filter by amount range
- [ ] Pagination works (100+ results)
- [ ] Sort by different fields
- [ ] Export to CSV
- [ ] Export to JSON

**2. Organization Profiles**
- [ ] Click organization from search results
- [ ] Profile loads with real data
- [ ] All 6 metric cards show correct values
- [ ] Activity list displays
- [ ] Pagination in activity list works
- [ ] Related organizations populate
- [ ] Lobbyist network displays
- [ ] Export functions work

**3. Performance**
- [ ] Search completes in < 3 seconds
- [ ] Large dataset queries (10,000+ records) work
- [ ] Caching reduces query time on repeat searches
- [ ] Cold start latency acceptable (< 5 seconds)
- [ ] Page load time < 2 seconds

**4. Error Handling**
- [ ] Invalid query handled gracefully
- [ ] BigQuery timeout handled
- [ ] Network error falls back to demo data
- [ ] Authentication failure shows appropriate message
- [ ] Invalid organization name handled

**5. Security**
- [ ] Clerk authentication required
- [ ] JWT tokens validated
- [ ] SQL injection protection verified
- [ ] Credentials not exposed in responses
- [ ] CORS configured correctly

**6. Monitoring**
- [ ] Health check endpoint returns status
- [ ] Logs visible in Vercel dashboard
- [ ] BigQuery job logs in Google Cloud Console
- [ ] Error tracking configured
- [ ] Performance metrics collected

**Testing Tools:**
```bash
# Local testing
vercel dev

# Preview deployment
vercel --prod=false

# Test API directly
curl https://preview-url.vercel.app/api/search?q=medical

# Check health
curl https://preview-url.vercel.app/api/health
```

**Deliverables:**
- All test cases passed
- Issues documented and resolved
- Performance benchmarks met
- Security verified

---

### Phase 5: Monitoring & Optimization

#### 5.1: Monitoring Setup
**Duration:** 2-3 hours

**Metrics to Track:**

**1. Backend Performance**
- API response times
- BigQuery query execution times
- Cache hit rates
- Error rates
- Serverless function cold start times

**2. Database Metrics**
- Queries per day
- Data scanned per query
- Concurrent queries
- Failed queries
- Cost per 1000 queries

**3. Application Health**
- Uptime percentage
- Error rate
- User authentication success rate
- Search success rate
- Fallback activation rate (demo data usage)

**Monitoring Tools:**

**Vercel Analytics:**
```javascript
// Add to src/index.js
import { Analytics } from '@vercel/analytics/react';

function App() {
  return (
    <>
      <YourApp />
      <Analytics />
    </>
  );
}
```

**Google Cloud Monitoring:**
- Enable BigQuery query logging
- Set up query cost alerts
- Monitor data scanned per query
- Track query failures

**Custom Logging:**
```python
# api/_database.py
import logging
import time

def execute_query_with_metrics(query):
    start = time.time()

    try:
        result = client.query(query).result()
        duration = time.time() - start

        logging.info({
            'event': 'query_success',
            'duration_ms': duration * 1000,
            'rows_returned': result.total_rows,
            'bytes_scanned': result.total_bytes_processed
        })

        return result
    except Exception as e:
        logging.error({
            'event': 'query_failure',
            'error': str(e),
            'query': query[:100]  # Log first 100 chars
        })
        raise
```

**Alerts Configuration:**

| Alert | Condition | Action |
|-------|-----------|--------|
| High Error Rate | > 5% errors in 5 min | Email notification |
| Query Cost Spike | > $10/day | Email notification |
| API Latency | > 5s average | Slack notification |
| BigQuery Quota | > 80% quota used | Email notification |

**Tasks:**
- [ ] Enable Vercel Analytics
- [ ] Configure Google Cloud logging
- [ ] Set up custom metrics logging
- [ ] Create alert policies
- [ ] Test alert notifications
- [ ] Create monitoring dashboard

**Deliverables:**
- Monitoring dashboards configured
- Alerts tested and active
- Logging centralized
- Documentation for monitoring

---

#### 5.2: Performance Optimization
**Duration:** 3-4 hours

**Optimization Strategies:**

**1. Query Optimization**
```sql
-- Add indexes to frequently queried columns
CREATE INDEX idx_organization_name
ON `ca_lobby.lobby_activities` (organization_name);

CREATE INDEX idx_filing_date
ON `ca_lobby.lobby_activities` (filing_date DESC);

-- Use partitioned tables for large datasets
CREATE TABLE `ca_lobby.lobby_activities_partitioned`
PARTITION BY DATE(filing_date)
AS SELECT * FROM `ca_lobby.lobby_activities`;
```

**2. Backend Caching**
```python
# api/_database.py
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def execute_cached_query(query_hash):
    """Cache frequently run queries."""
    return execute_query(query_hash)

def search_with_cache(query_params):
    # Generate cache key
    cache_key = hashlib.md5(str(query_params).encode()).hexdigest()

    # Check cache
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result

    # Execute query
    result = execute_query(build_query(query_params))

    # Store in cache (5 minute TTL)
    cache.set(cache_key, result, ttl=300)

    return result
```

**3. Frontend Optimization**
```javascript
// Implement request debouncing
import { debounce } from 'lodash';

const debouncedSearch = debounce(async (query) => {
  await performSearch(query);
}, 500);  // Wait 500ms after user stops typing
```

**4. Connection Pooling**
```python
# For serverless, use connection singleton
class BigQueryConnectionPool:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_client(self):
        if self._client is None:
            self._client = bigquery.Client(credentials=get_credentials())
        return self._client
```

**5. Data Transfer Optimization**
```sql
-- Limit columns selected
SELECT
  organization_name,
  lobbyist_name,
  amount,
  filing_date
FROM `ca_lobby.lobby_activities`
WHERE filing_date > DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR)
LIMIT 100;

-- vs. SELECT * (slower and more expensive)
```

**Performance Targets:**

| Metric | Target | Measurement |
|--------|--------|-------------|
| Search Response Time | < 2s | P95 latency |
| Cold Start Time | < 5s | Serverless function init |
| Cache Hit Rate | > 60% | Cache hits / total queries |
| BigQuery Cost | < $20/month | Monthly billing |
| Data Scanned | < 100MB/query | Average per query |

**Tasks:**
- [ ] Implement query caching
- [ ] Add database indexes
- [ ] Optimize SQL queries
- [ ] Test connection pooling
- [ ] Implement frontend debouncing
- [ ] Measure performance improvements
- [ ] Document optimization techniques

**Deliverables:**
- Performance benchmarks before/after
- Optimized queries documented
- Cache hit rates improved
- Cost reduction achieved

---

### Phase 6: Documentation & Handoff

#### 6.1: Technical Documentation
**Duration:** 2-3 hours

**Documents to Create:**

**1. Deployment Guide** (`Documentation/Deployment/BIGQUERY_DEPLOYMENT_GUIDE.md`)
- Step-by-step deployment process
- Environment variable reference
- Troubleshooting common issues
- Rollback procedures

**2. Operations Manual** (`Documentation/Deployment/BIGQUERY_OPERATIONS.md`)
- Daily monitoring checklist
- Alert response procedures
- Query optimization guide
- Cost management strategies

**3. API Reference** (`Documentation/Deployment/API_REFERENCE.md`)
- Endpoint documentation
- Request/response formats
- Authentication requirements
- Error codes

**4. Completion Report** (`Documentation/Deployment/BIGQUERY_INTEGRATION_COMPLETION_REPORT.md`)
- Summary of implementation
- Issues encountered and resolved
- Performance metrics achieved
- Lessons learned

**Tasks:**
- [ ] Create deployment guide
- [ ] Document API endpoints
- [ ] Write operations manual
- [ ] Complete completion report
- [ ] Update MASTER_PROJECT_PLAN.md
- [ ] Update CLAUDE.md with new configuration

**Deliverables:**
- Complete documentation set
- Master plan updated
- Completion report filed

---

#### 6.2: Knowledge Transfer
**Duration:** 1-2 hours

**Training Materials:**

**1. Video Walkthrough** (Optional)
- Deployment process demonstration
- Monitoring dashboard tour
- Troubleshooting common issues

**2. Quick Reference Cards**
- Environment variables
- Common commands
- Troubleshooting flowchart

**3. Runbook**
```markdown
# BigQuery Backend Emergency Runbook

## Problem: High Error Rate
1. Check Vercel logs: vercel.com/dashboard/logs
2. Check BigQuery status: console.cloud.google.com/bigquery
3. If BigQuery down: Set USE_MOCK_DATA=true
4. Notify team

## Problem: High Costs
1. Check query patterns in Cloud Console
2. Identify expensive queries
3. Add caching or optimize
4. Set query cost limits

## Problem: Slow Queries
1. Check query execution times in logs
2. Verify cache is working
3. Check for missing indexes
4. Consider query optimization
```

**Tasks:**
- [ ] Create quick reference materials
- [ ] Write emergency runbook
- [ ] Test rollback procedures
- [ ] Document lessons learned

**Deliverables:**
- Training materials complete
- Runbook tested
- Team briefed on new system

---

## 🔧 Technical Requirements

### Google Cloud Prerequisites
- BigQuery API enabled
- Service account created
- Dataset `ca_lobby` exists and populated
- Billing account configured
- Query quota limits set

### Vercel Prerequisites
- Pro or Team plan (for environment variables)
- Python runtime support enabled
- Domain configured (if using custom domain)
- Build settings optimized

### Development Tools
- Vercel CLI installed (`npm i -g vercel`)
- Google Cloud SDK installed
- Python 3.9+ for backend testing
- Node 18+ for frontend

---

## 💰 Cost Estimates

### BigQuery Costs
**Query Pricing:** $5 per TB scanned

**Estimated Monthly Usage:**
- 1,000 searches/day × 100MB/query = 100GB/day
- 100GB × 30 days = 3TB/month
- 3TB × $5 = **$15/month**

**With Optimization (caching, indexes):**
- 60% cache hit rate reduces scanned data by 60%
- 3TB × 0.4 = 1.2TB/month
- 1.2TB × $5 = **$6/month**

### Vercel Costs
**Hobby Plan:** Free (personal use)
**Pro Plan:** $20/month (includes serverless functions)

**Total Estimated Cost:** $6-26/month (depending on plan and optimization)

---

## ⚠️ Risk Assessment

### High-Priority Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| BigQuery quota exceeded | Medium | High | Set query limits, implement caching |
| High query costs | Medium | Medium | Monitor spending, optimize queries |
| Cold start latency | High | Medium | Connection pooling, warm-up functions |
| Credential exposure | Low | Critical | Use environment variables, rotate keys |
| Service account deleted | Low | Critical | Backup credentials, document recovery |

### Contingency Plans

**Plan A: Rollback to Demo Data**
- Set `USE_MOCK_DATA=true` on Vercel
- Redeploy frontend without backend
- No data loss, immediate recovery

**Plan B: Separate Backend Deployment**
- Deploy Flask backend on alternative platform (e.g., Cloud Run)
- Update frontend to call external API
- More control over backend infrastructure

**Plan C: Gradual Rollout**
- Enable for 10% of users initially
- Monitor performance and costs
- Gradually increase to 100%

---

## 📅 Timeline Summary

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| 1. Prerequisites | 3-5 hours | BigQuery access, service account |
| 2. Backend Config | 5-7 hours | Phase 1 |
| 3. Frontend Config | 3-5 hours | Phase 2 |
| 4. Deployment | 1 day | Phases 1-3 |
| 5. Monitoring | 5-7 hours | Phase 4 |
| 6. Documentation | 3-5 hours | Phase 5 |
| **Total** | **2-3 days** | All phases sequential |

---

## ✅ Success Criteria

**Functional Requirements:**
- [ ] Search returns real BigQuery data
- [ ] Organization profiles show accurate information
- [ ] All filters and pagination work correctly
- [ ] Export functionality works with real data
- [ ] Authentication integrated

**Performance Requirements:**
- [ ] Search latency < 3 seconds (P95)
- [ ] Cache hit rate > 60%
- [ ] Uptime > 99.5%
- [ ] Error rate < 1%

**Cost Requirements:**
- [ ] Monthly BigQuery cost < $20
- [ ] No unexpected quota overages
- [ ] Cost monitoring alerts configured

**Operational Requirements:**
- [ ] Monitoring dashboard active
- [ ] Alerts configured and tested
- [ ] Documentation complete
- [ ] Rollback tested

---

## 📞 Support & Escalation

### Issue Severity Levels

**P0 - Critical:**
- Production down or unusable
- Data corruption
- Security breach
- Response: Immediate, rollback if needed

**P1 - High:**
- Major feature broken
- High error rates (> 10%)
- Performance degradation
- Response: Within 4 hours

**P2 - Medium:**
- Minor feature issues
- Occasional errors
- Non-critical performance issues
- Response: Within 1 day

**P3 - Low:**
- Cosmetic issues
- Enhancement requests
- Documentation updates
- Response: Next sprint

### Contact Points
- **Vercel Support:** support@vercel.com
- **Google Cloud Support:** Cloud Console → Support
- **Internal:** [Team Slack/Email]

---

## 🎯 Next Steps

**To Execute This Plan:**

1. **Review and Approve**
   - Technical lead review
   - Stakeholder approval
   - Budget confirmation

2. **Prepare Environment**
   - Verify BigQuery dataset
   - Create service account
   - Test credentials locally

3. **Schedule Implementation**
   - Block 2-3 days for focused work
   - Notify stakeholders of deployment window
   - Prepare rollback plan

4. **Execute Phases Sequentially**
   - Follow plan step-by-step
   - Test thoroughly at each phase
   - Document any deviations

5. **Post-Implementation Review**
   - Verify success criteria met
   - Complete documentation
   - Conduct team retrospective

---

**Last Updated:** October 2, 2025
**Plan Author:** CA Lobby Development Team
**Review Status:** Draft - Awaiting Approval

---

## 📚 References

- [Phase 1.1 Completion Report](../Phase1/Reports/PHASE_1_1_COMPLETION_REPORT.md) - Original BigQuery implementation
- [Phase 1.3 Completion Report](../Phase1/Reports/PHASE_1_3_COMPLETION_REPORT_FOR_CLAUDE.md) - Backend API development
- [Demo Data Configuration](../General/DEMO_DATA_CONFIGURATION.md) - Current configuration
- [Vercel Serverless Functions Guide](https://vercel.com/docs/serverless-functions/introduction)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices-performance-overview)
