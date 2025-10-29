# BigQuery Integration - Complete Step-by-Step Implementation Guide

**Project:** California Lobby Search System
**Phase:** Backend Integration Enablement
**Date Created:** October 2, 2025
**Status:** Ready for Implementation
**Dependencies:** Phase 1.1 (BigQuery Infrastructure), Phase 1.3 (Backend API)

---

## 📋 Table of Contents

- [Executive Summary](#-executive-summary)
- [Phase 1: Prerequisites & Preparation](#phase-1-prerequisites--preparation)
  - [1.1: Verify BigQuery Dataset Status](#11-verify-bigquery-dataset-status)
  - [1.2: Service Account & Credentials Setup](#12-service-account--credentials-setup)
- [Phase 2: Backend Deployment Configuration](#phase-2-backend-deployment-configuration)
  - [2.1: Convert Flask Backend to Vercel Serverless Functions](#21-convert-flask-backend-to-vercel-serverless-functions)
  - [2.2: Environment Variables Configuration](#22-environment-variables-configuration)
- [Phase 3: Frontend Configuration](#phase-3-frontend-configuration)
  - [3.1: Update Frontend to Use Backend API](#31-update-frontend-to-use-backend-api)
  - [3.2: Update Organization Profile Component](#32-update-organization-profile-component)
- [Phase 4: Deployment & Testing](#phase-4-deployment--testing)
  - [4.1: Staged Deployment Strategy](#41-staged-deployment-strategy)
  - [4.2: Integration Testing Checklist](#42-integration-testing-checklist)
- [Phase 5: Monitoring & Optimization](#phase-5-monitoring--optimization)
  - [5.1: Monitoring Setup](#51-monitoring-setup)
  - [5.2: Performance Optimization](#52-performance-optimization)
- [Phase 6: Documentation & Handoff](#phase-6-documentation--handoff)
  - [6.1: Technical Documentation](#61-technical-documentation)
  - [6.2: Knowledge Transfer](#62-knowledge-transfer)

---

## 📋 Executive Summary

This guide provides complete step-by-step instructions for enabling BigQuery database integration for the CA Lobby application on Vercel deployments. The BigQuery infrastructure and backend API code already exist (completed in Phase 1.1 and 1.3), but are currently running in **demo data mode**. This plan covers configuration, deployment, testing, and monitoring for production BigQuery integration.

**Total Estimated Duration:** 2-3 days

---

# Phase 1: Prerequisites & Preparation

**Total Duration:** 3-5 hours

---

## 1.1: Verify BigQuery Dataset Status

**Duration:** 1-2 hours

### Step 1: Access Google Cloud Console

1. Open browser and navigate to https://console.cloud.google.com
2. Sign in with your Google Cloud account
3. Select your project (the one containing the `ca_lobby` dataset)
4. Navigate to **BigQuery** from the left menu (or use search)

### Step 2: Verify Dataset Exists

1. In BigQuery console, look at the Explorer panel on the left
2. Expand your project ID
3. Look for the `ca_lobby` dataset
4. Click on the dataset to view its tables
5. You should see tables like `lobby_activities`, `lobbyists`, `organizations`, etc.

### Step 3: Check Data Freshness

1. Click the **Compose new query** button
2. Copy and paste this query (replace `YOUR_PROJECT_ID` with your actual project ID):

```sql
SELECT
  MAX(filing_date) as latest_filing,
  COUNT(*) as total_records
FROM `YOUR_PROJECT_ID.ca_lobby.lobby_activities`;
```

3. Click **Run**
4. Note the results:
   - **latest_filing:** _____________
   - **total_records:** _____________

### Step 4: Document Table Inventory

1. Run this query to get all table counts:

```sql
SELECT
  table_name,
  row_count,
  TIMESTAMP_MILLIS(creation_time) as created_at,
  TIMESTAMP_MILLIS(last_modified_time) as last_modified
FROM `ca_lobby.__TABLES__`
ORDER BY table_name;
```

2. Save these results to a document or spreadsheet
3. Create a file: `Documentation/Deployment/BIGQUERY_DATASET_STATUS.md`
4. Document all tables with their row counts and last modified dates

### Step 5: Validate Table Schemas

1. Click on the `lobby_activities` table
2. Click the **Schema** tab
3. Verify the schema includes expected fields:
   - `organization_name`
   - `lobbyist_name`
   - `filing_date`
   - `amount`
   - Other fields your API expects

4. Document any schema mismatches

### Step 6: Test Data Pipeline (Optional)

1. Switch to the `main` branch if data processing files are there:
```bash
git checkout main
```

2. Look for data pipeline scripts in the repository
3. If found, run a test sync to verify pipeline is operational
4. Switch back to your working branch

**✅ Phase 1.1 Deliverables:**
- [ ] Dataset confirmed to exist
- [ ] Latest filing date recorded: _____________
- [ ] Total record count: _____________
- [ ] All tables documented with row counts
- [ ] Schema validated against API expectations
- [ ] Dataset status document created

---

## 1.2: Service Account & Credentials Setup

**Duration:** 2-3 hours

### Step 1: Create Service Account

1. In Google Cloud Console, navigate to **IAM & Admin** → **Service Accounts**
   - Click hamburger menu (☰) → **IAM & Admin** → **Service Accounts**

2. Click **+ CREATE SERVICE ACCOUNT** at the top

3. Enter service account details:
   - **Service account name:** `vercel-ca-lobby-backend`
   - **Service account ID:** (auto-filled, e.g., `vercel-ca-lobby-backend`)
   - **Description:** `Service account for CA Lobby Vercel deployment with BigQuery access`

4. Click **CREATE AND CONTINUE**

### Step 2: Assign Permissions

1. In the "Grant this service account access to project" section:

2. Click **Select a role** dropdown

3. Add **First Role:**
   - Type: `BigQuery Data Viewer`
   - Click on `BigQuery Data Viewer` when it appears
   - Click **+ ADD ANOTHER ROLE**

4. Add **Second Role:**
   - Type: `BigQuery Job User`
   - Click on `BigQuery Job User` when it appears

5. Click **CONTINUE**

6. Skip "Grant users access to this service account" (optional)

7. Click **DONE**

### Step 3: Generate JSON Key File

1. You'll see your service accounts list
2. Find `vercel-ca-lobby-backend@YOUR_PROJECT_ID.iam.gserviceaccount.com`
3. Click the **Actions** menu (⋮ three vertical dots) on the right
4. Select **Manage keys**

5. Click **ADD KEY** → **Create new key**

6. Select **JSON** as the key type

7. Click **CREATE**

8. **⚠️ IMPORTANT:** The JSON key file will automatically download to your computer
   - File name: `YOUR_PROJECT_ID-xxxxx.json`
   - **IMMEDIATELY** move this file to a secure location
   - **NEVER** commit this file to git
   - Suggested location: `~/credentials/ca-lobby/` (outside git repo)

9. Create the secure directory and move the file:
```bash
mkdir -p ~/credentials/ca-lobby
mv ~/Downloads/YOUR_PROJECT_ID-*.json ~/credentials/ca-lobby/service-account-key.json
chmod 600 ~/credentials/ca-lobby/service-account-key.json
```

### Step 4: Test Credentials Locally

1. Open terminal and navigate to your project:
```bash
cd /Users/michaelingram/Documents/GitHub/CA_lobby
```

2. Set environment variable with the path to your key file:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=~/credentials/ca-lobby/service-account-key.json
```

3. Verify the environment variable is set:
```bash
echo $GOOGLE_APPLICATION_CREDENTIALS
```

4. Navigate to backend directory:
```bash
cd webapp/backend
```

5. Test the connection with Python:
```bash
python3 -c "from database import db; print(db.health_check())"
```

**Expected output:** You should see a success message or connection status

**If you get an error:**
- Check the file path is correct
- Ensure the environment variable is set
- Verify Python can import the database module
- Check that BigQuery API is enabled in your project

### Step 5: Document Credential Information

1. Create a secure document (stored locally, **NOT in git**):

Create file: `~/credentials/ca-lobby/CREDENTIALS_INFO.md`

```markdown
# CA Lobby BigQuery Credentials

**Service Account Email:** vercel-ca-lobby-backend@YOUR_PROJECT_ID.iam.gserviceaccount.com
**Created:** October 2, 2025
**Key File Location:** ~/credentials/ca-lobby/service-account-key.json
**Rotation Due:** January 2, 2026 (90 days)

## Permissions:
- BigQuery Data Viewer
- BigQuery Job User

## Usage:
- Vercel deployment for CA Lobby backend API
- Read-only access to ca_lobby dataset

## Security Notes:
- Never commit to git
- Rotate every 90 days
- Monitor usage in Google Cloud Console
```

2. Set a calendar reminder for 90 days to rotate credentials

### Step 6: Add to .gitignore

1. Ensure your `.gitignore` includes:
```bash
# Add to .gitignore if not already there
**/service-account*.json
**/credentials*.json
*.pem
*.key
```

**✅ Phase 1.2 Deliverables:**
- [ ] Service account created: `vercel-ca-lobby-backend`
- [ ] Permissions assigned (BigQuery Data Viewer, BigQuery Job User)
- [ ] JSON key file downloaded and secured at: ~/credentials/ca-lobby/service-account-key.json
- [ ] Local connection test passed
- [ ] Credential information documented
- [ ] Rotation reminder set (90 days)
- [ ] .gitignore updated

**🎉 Phase 1 Complete!** You now have verified BigQuery access and secure credentials.

---

# Phase 2: Backend Deployment Configuration

**Total Duration:** 5-7 hours

---

## 2.1: Convert Flask Backend to Vercel Serverless Functions

**Duration:** 4-6 hours

### Overview

Currently, your Flask backend is in `webapp/backend/` and designed for traditional server deployment. Vercel uses **serverless functions**, so we need to adapt the code.

### Step 1: Understand Current Backend Structure

1. Review existing backend files:
```bash
cd /Users/michaelingram/Documents/GitHub/CA_lobby
ls -la webapp/backend/
```

Expected files:
- `app.py` - Main Flask application
- `database.py` - BigQuery connection
- `data_service.py` - Data access layer
- `auth.py` - Authentication
- `requirements.txt` - Python dependencies

### Step 2: Create API Directory Structure

1. Create the `api/` directory in project root:
```bash
cd /Users/michaelingram/Documents/GitHub/CA_lobby
mkdir -p api
```

2. Create the serverless function files:
```bash
touch api/search.py
touch api/organization.py
touch api/health.py
touch api/_database.py
touch api/requirements.txt
```

### Step 3: Create Shared Database Module

1. Create `api/_database.py`:

```python
"""
Shared database connection module for Vercel serverless functions.
Optimized for serverless with connection pooling.
"""

import json
import os
from google.cloud import bigquery
from google.oauth2 import service_account

# Global connection pool (persists across warm starts)
_client = None

def get_credentials():
    """
    Load BigQuery credentials from environment variable.
    Supports both JSON string (Vercel) and file path (local dev).
    """
    # Try JSON string from environment (Vercel deployment)
    creds_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

    if creds_json and creds_json.startswith('{'):
        # Parse JSON from environment variable
        try:
            creds_dict = json.loads(creds_json)
            credentials = service_account.Credentials.from_service_account_info(creds_dict)
            return credentials
        except json.JSONDecodeError:
            pass

    # Fallback: File path for local development
    if creds_json and os.path.exists(creds_json):
        credentials = service_account.Credentials.from_service_account_file(creds_json)
        return credentials

    # No credentials found
    raise ValueError("No BigQuery credentials found. Set GOOGLE_APPLICATION_CREDENTIALS environment variable.")

def get_database_client():
    """
    Get or create BigQuery client with connection pooling.
    Reuses client across warm starts for better performance.
    """
    global _client

    if _client is None:
        credentials = get_credentials()
        project_id = os.getenv('BIGQUERY_PROJECT_ID')
        _client = bigquery.Client(
            credentials=credentials,
            project=project_id
        )

    return _client

def health_check():
    """Test database connection."""
    try:
        client = get_database_client()
        # Simple query to test connection
        query = "SELECT 1 as status"
        result = client.query(query).result()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

### Step 4: Create Health Check Endpoint

1. Create `api/health.py`:

```python
"""
Health check endpoint for monitoring.
GET /api/health
"""

from http.server import BaseHTTPRequestHandler
import json
from _database import health_check

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Return health status."""
        try:
            status = health_check()

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            self.wfile.write(json.dumps(status).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            error_response = {
                "status": "error",
                "message": str(e)
            }
            self.wfile.write(json.dumps(error_response).encode())

        return
```

### Step 5: Create Search Endpoint

1. Create `api/search.py`:

```python
"""
Search endpoint for lobby activities.
GET /api/search?q=query&organization=name&start_date=2024-01-01&end_date=2024-12-31
"""

from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import os
from _database import get_database_client

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle search requests."""
        try:
            # Check if mock data mode is enabled
            use_mock = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'

            if use_mock:
                # Return mock data
                mock_response = {
                    "results": [],
                    "total": 0,
                    "message": "Mock data mode enabled"
                }
                self.send_json_response(mock_response, 200)
                return

            # Parse query parameters
            parsed_url = urlparse(self.path)
            params = parse_qs(parsed_url.query)

            # Extract search parameters
            query = params.get('q', [''])[0]
            organization = params.get('organization', [''])[0]
            start_date = params.get('start_date', [''])[0]
            end_date = params.get('end_date', [''])[0]
            limit = int(params.get('limit', ['100'])[0])
            offset = int(params.get('offset', ['0'])[0])

            # Build SQL query
            dataset = os.getenv('BIGQUERY_DATASET', 'ca_lobby')
            sql_query = self.build_search_query(
                dataset, query, organization, start_date, end_date, limit, offset
            )

            # Execute query
            client = get_database_client()
            query_job = client.query(sql_query)
            results = query_job.result()

            # Format results
            formatted_results = [dict(row) for row in results]

            response = {
                "results": formatted_results,
                "total": len(formatted_results),
                "offset": offset,
                "limit": limit
            }

            self.send_json_response(response, 200)

        except Exception as e:
            error_response = {
                "error": str(e),
                "message": "Search failed"
            }
            self.send_json_response(error_response, 500)

    def build_search_query(self, dataset, query, organization, start_date, end_date, limit, offset):
        """Build BigQuery SQL for search."""
        sql = f"""
        SELECT
            organization_name,
            lobbyist_name,
            filing_date,
            amount,
            quarter,
            year
        FROM `{dataset}.lobby_activities`
        WHERE 1=1
        """

        if query:
            sql += f" AND (organization_name LIKE '%{query}%' OR lobbyist_name LIKE '%{query}%')"

        if organization:
            sql += f" AND organization_name = '{organization}'"

        if start_date:
            sql += f" AND filing_date >= '{start_date}'"

        if end_date:
            sql += f" AND filing_date <= '{end_date}'"

        sql += f" ORDER BY filing_date DESC LIMIT {limit} OFFSET {offset}"

        return sql

    def send_json_response(self, data, status_code):
        """Send JSON response with CORS headers."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
```

### Step 6: Create Organization Endpoint

1. Create `api/organization.py`:

```python
"""
Organization profile endpoint.
GET /api/organization?name=Organization+Name
"""

from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import os
from _database import get_database_client

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle organization profile requests."""
        try:
            # Check if mock data mode is enabled
            use_mock = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'

            if use_mock:
                mock_response = {
                    "organization": {},
                    "message": "Mock data mode enabled"
                }
                self.send_json_response(mock_response, 200)
                return

            # Parse query parameters
            parsed_url = urlparse(self.path)
            params = parse_qs(parsed_url.query)

            organization_name = params.get('name', [''])[0]

            if not organization_name:
                self.send_json_response({"error": "Organization name required"}, 400)
                return

            # Get organization data
            dataset = os.getenv('BIGQUERY_DATASET', 'ca_lobby')
            client = get_database_client()

            # Query for organization details
            sql_query = f"""
            SELECT
                organization_name,
                COUNT(*) as total_activities,
                SUM(amount) as total_spending,
                MIN(filing_date) as first_filing,
                MAX(filing_date) as last_filing,
                COUNT(DISTINCT lobbyist_name) as total_lobbyists
            FROM `{dataset}.lobby_activities`
            WHERE organization_name = '{organization_name}'
            GROUP BY organization_name
            """

            result = client.query(sql_query).result()
            rows = list(result)

            if not rows:
                self.send_json_response({"error": "Organization not found"}, 404)
                return

            org_data = dict(rows[0])

            response = {
                "organization": org_data
            }

            self.send_json_response(response, 200)

        except Exception as e:
            error_response = {
                "error": str(e),
                "message": "Failed to fetch organization"
            }
            self.send_json_response(error_response, 500)

    def send_json_response(self, data, status_code):
        """Send JSON response with CORS headers."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
```

### Step 7: Create Requirements File

1. Create `api/requirements.txt`:

```txt
google-cloud-bigquery==3.11.4
google-auth==2.23.0
```

### Step 8: Update vercel.json

1. Open `vercel.json` and update it:

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
  ]
}
```

### Step 9: Test Locally with Vercel Dev

1. Install Vercel CLI if not already installed:
```bash
npm install -g vercel
```

2. Start Vercel dev server:
```bash
cd /Users/michaelingram/Documents/GitHub/CA_lobby
vercel dev
```

3. Test the health endpoint:
```bash
curl http://localhost:3000/api/health
```

4. Test the search endpoint:
```bash
curl "http://localhost:3000/api/search?q=medical"
```

**✅ Phase 2.1 Deliverables:**
- [ ] `api/` directory created with all endpoint files
- [ ] `_database.py` connection module implemented
- [ ] `health.py` endpoint created
- [ ] `search.py` endpoint created
- [ ] `organization.py` endpoint created
- [ ] `requirements.txt` created
- [ ] `vercel.json` updated
- [ ] Local testing with `vercel dev` passed

---

## 2.2: Environment Variables Configuration

**Duration:** 1 hour

### Step 1: Prepare Credentials for Vercel

1. Read your service account JSON key:
```bash
cat ~/credentials/ca-lobby/service-account-key.json
```

2. Copy the ENTIRE JSON content (it's one long line)

3. The JSON should look like:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "vercel-ca-lobby-backend@...",
  ...
}
```

### Step 2: Access Vercel Dashboard

1. Go to https://vercel.com/dashboard
2. Sign in to your account
3. Find your **CA Lobby** project
4. Click on the project to open it

### Step 3: Add Environment Variables

1. Click **Settings** tab at the top
2. Click **Environment Variables** in the left sidebar
3. Add the following variables one by one:

#### Variable 1: USE_MOCK_DATA

- **Key:** `USE_MOCK_DATA`
- **Value:** `false`
- **Environments:** Check both **Production** and **Preview**
- Click **Add**

#### Variable 2: BIGQUERY_DATASET

- **Key:** `BIGQUERY_DATASET`
- **Value:** `ca_lobby`
- **Environments:** Check both **Production** and **Preview**
- Click **Add**

#### Variable 3: BIGQUERY_PROJECT_ID

- **Key:** `BIGQUERY_PROJECT_ID`
- **Value:** `your-actual-project-id` (get from service account JSON)
- **Environments:** Check both **Production** and **Preview**
- Click **Add**

#### Variable 4: GOOGLE_APPLICATION_CREDENTIALS

- **Key:** `GOOGLE_APPLICATION_CREDENTIALS`
- **Value:** Paste the ENTIRE JSON content from Step 1 (yes, the whole thing including curly braces)
- **Environments:** Check both **Production** and **Preview**
- **Type:** This is sensitive, Vercel will mark it as secret
- Click **Add**

#### Variable 5: REACT_APP_USE_BACKEND_API

- **Key:** `REACT_APP_USE_BACKEND_API`
- **Value:** `true`
- **Environments:** Check both **Production** and **Preview**
- Click **Add**

#### Variable 6: REACT_APP_API_URL

- **Key:** `REACT_APP_API_URL`
- **Value:** `/api`
- **Environments:** Check both **Production** and **Preview**
- Click **Add**

### Step 4: Verify Variables

1. You should now see 6 environment variables listed
2. Click **Decrypt** to verify values (except for the sensitive credentials)
3. Ensure Production and Preview are both checked for all variables

### Step 5: Update Local .env File

1. Create or update `.env` file in your project root:

```bash
cd /Users/michaelingram/Documents/GitHub/CA_lobby
nano .env
```

2. Add these variables for local development:

```bash
# Local Development Environment Variables

# BigQuery Configuration
USE_MOCK_DATA=false
BIGQUERY_DATASET=ca_lobby
BIGQUERY_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/Users/michaelingram/credentials/ca-lobby/service-account-key.json

# Frontend Configuration
REACT_APP_USE_BACKEND_API=true
REACT_APP_API_URL=http://localhost:3000/api

# Clerk (if needed)
REACT_APP_CLERK_PUBLISHABLE_KEY=your_clerk_key
```

3. Save the file (Ctrl+X, then Y, then Enter)

### Step 6: Test Environment Variables Locally

1. Pull environment variables from Vercel:
```bash
vercel env pull
```

2. This creates a `.env.local` file with your Vercel environment variables

3. Test that variables are loaded:
```bash
source .env
echo $USE_MOCK_DATA
echo $BIGQUERY_DATASET
```

**✅ Phase 2.2 Deliverables:**
- [ ] All 6 environment variables added to Vercel dashboard
- [ ] Variables configured for both Production and Preview
- [ ] Local `.env` file created and tested
- [ ] Environment variables pulled with `vercel env pull`
- [ ] Variables verified and working

**🎉 Phase 2 Complete!** Backend is configured for Vercel serverless deployment.

---

# Phase 3: Frontend Configuration

**Total Duration:** 3-5 hours

---

## 3.1: Update Frontend to Use Backend API

**Duration:** 2-3 hours

### Step 1: Update Search Component

1. Open `src/components/Search.js`:
```bash
cd /Users/michaelingram/Documents/GitHub/CA_lobby
code src/components/Search.js
```

2. Find the search function (around line 200-250)

3. Update the API endpoint configuration:

```javascript
// Add at the top of the component
const useBackend = process.env.REACT_APP_USE_BACKEND_API === 'true';
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';
```

4. Update the search handler function:

```javascript
const handleSearch = async () => {
  setLoading(true);
  setError(null);

  try {
    if (useBackend) {
      // Backend API call
      const queryParams = new URLSearchParams({
        q: searchQuery,
        organization: filters.organization || '',
        start_date: filters.startDate || '',
        end_date: filters.endDate || '',
        limit: '100',
        offset: '0'
      });

      const response = await fetch(`${API_BASE_URL}/search?${queryParams}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          // Add Clerk auth if needed
          // 'Authorization': `Bearer ${await clerk.session.getToken()}`
        }
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      if (data.error) {
        console.warn('Backend error, falling back to demo data:', data.error);
        setResults(generateDemoSearchResults(searchQuery, filters));
      } else {
        setResults(data.results);
      }
    } else {
      // Demo data fallback
      setResults(generateDemoSearchResults(searchQuery, filters));
    }
  } catch (error) {
    console.error('Backend call failed, using demo data:', error);
    setError('Failed to fetch data from server. Using demo data.');
    setResults(generateDemoSearchResults(searchQuery, filters));
  } finally {
    setLoading(false);
  }
};
```

### Step 2: Add Error Handling UI

1. Add error state display in the render section:

```javascript
return (
  <div className="search-container">
    {/* Search input */}
    <input
      value={searchQuery}
      onChange={(e) => setSearchQuery(e.target.value)}
      placeholder="Search organizations, lobbyists..."
    />

    {/* Error message display */}
    {error && (
      <div className="error-banner" style={{
        background: '#fff3cd',
        border: '1px solid #ffc107',
        padding: '12px',
        borderRadius: '4px',
        marginBottom: '16px'
      }}>
        <strong>⚠️ Warning:</strong> {error}
      </div>
    )}

    {/* Loading state */}
    {loading && (
      <div className="loading-spinner">
        Loading...
      </div>
    )}

    {/* Results */}
    <div className="results">
      {results.map(result => (
        // Your result rendering
      ))}
    </div>
  </div>
);
```

### Step 3: Add Backend Status Indicator

1. Add a status indicator to show if using backend or demo data:

```javascript
// At the top of component
const [backendStatus, setBackendStatus] = useState('unknown');

// Check backend health on component mount
useEffect(() => {
  const checkBackendHealth = async () => {
    if (useBackend) {
      try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        setBackendStatus(data.status === 'healthy' ? 'connected' : 'disconnected');
      } catch (error) {
        setBackendStatus('disconnected');
      }
    } else {
      setBackendStatus('demo-mode');
    }
  };

  checkBackendHealth();
}, []);

// In render, add status badge
{backendStatus === 'connected' && (
  <div className="backend-status" style={{
    background: '#d4edda',
    color: '#155724',
    padding: '8px 12px',
    borderRadius: '4px',
    marginBottom: '16px'
  }}>
    ✓ Connected to live database
  </div>
)}

{backendStatus === 'demo-mode' && (
  <div className="backend-status" style={{
    background: '#d1ecf1',
    color: '#0c5460',
    padding: '8px 12px',
    borderRadius: '4px',
    marginBottom: '16px'
  }}>
    ℹ Demo mode active
  </div>
)}
```

**✅ Phase 3.1 Deliverables:**
- [ ] Search component updated with backend API calls
- [ ] Error handling and fallback implemented
- [ ] Loading states added
- [ ] Backend status indicator added
- [ ] Code tested locally

---

## 3.2: Update Organization Profile Component

**Duration:** 1-2 hours

### Step 1: Update OrganizationProfile Component

1. Open `src/components/OrganizationProfile.js`:
```bash
code src/components/OrganizationProfile.js
```

2. Add backend configuration at the top:

```javascript
const useBackend = process.env.REACT_APP_USE_BACKEND_API === 'true';
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';
```

3. Update the data fetching logic:

```javascript
useEffect(() => {
  const fetchOrganizationData = async () => {
    setLoading(true);
    setError(null);

    try {
      if (useBackend) {
        // Fetch from backend API
        const response = await fetch(
          `${API_BASE_URL}/organization?name=${encodeURIComponent(organizationName)}`,
          {
            headers: {
              'Content-Type': 'application/json',
              // Add Clerk auth if needed
              // 'Authorization': `Bearer ${await clerk.session.getToken()}`
            }
          }
        );

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();

        if (data.error) {
          console.warn('Backend error, using demo data:', data.error);
          setOrganizationData(getDemoOrganization(organizationName));
        } else {
          setOrganizationData(data.organization);
        }
      } else {
        // Demo data fallback
        setOrganizationData(getDemoOrganization(organizationName));
      }
    } catch (error) {
      console.error('Failed to fetch organization:', error);
      setError('Failed to load organization data. Using demo data.');
      setOrganizationData(getDemoOrganization(organizationName));
    } finally {
      setLoading(false);
    }
  };

  if (organizationName) {
    fetchOrganizationData();
  }
}, [organizationName]);
```

### Step 2: Test Components Locally

1. Start the development server:
```bash
npm start
```

2. Test search functionality:
   - Navigate to search page
   - Enter a search query
   - Verify results load
   - Check console for any errors

3. Test organization profile:
   - Click on an organization from search results
   - Verify profile loads
   - Check all sections display correctly

**✅ Phase 3.2 Deliverables:**
- [ ] OrganizationProfile component updated
- [ ] Backend API integration added
- [ ] Error handling implemented
- [ ] Demo data fallback working
- [ ] Local testing passed

**🎉 Phase 3 Complete!** Frontend is configured to use the backend API.

---

# Phase 4: Deployment & Testing

**Total Duration:** 1 day

---

## 4.1: Staged Deployment Strategy

**Duration:** 4-6 hours

### Step 1: Create Feature Branch

1. Create a new branch for this work:
```bash
cd /Users/michaelingram/Documents/GitHub/CA_lobby
git checkout -b feature/bigquery-integration
```

2. Verify you're on the new branch:
```bash
git branch
```

### Step 2: Commit Backend Changes

1. Add all new API files:
```bash
git add api/
git add vercel.json
```

2. Commit backend changes:
```bash
git commit -m "Backend: Add Vercel serverless functions for BigQuery integration

- Create api/ directory with serverless functions
- Add health, search, and organization endpoints
- Implement connection pooling for serverless
- Update vercel.json for Python runtime support

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Step 3: Commit Frontend Changes

1. Add frontend changes:
```bash
git add src/components/Search.js
git add src/components/OrganizationProfile.js
git add .env
```

2. Commit frontend changes:
```bash
git commit -m "Frontend: Enable backend API integration

- Update Search component to call backend API
- Add error handling and fallback to demo data
- Update OrganizationProfile for backend integration
- Add backend health status indicator

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Step 4: Push to GitHub

1. Push the feature branch:
```bash
git push -u origin feature/bigquery-integration
```

2. Vercel will automatically create a **Preview Deployment**

3. Check your email or Vercel dashboard for the preview URL

### Step 5: Test Preview Deployment

1. Open the preview URL (e.g., `https://ca-lobby-git-feature-bigquery-integration-yourname.vercel.app`)

2. Open browser DevTools (F12) → Console tab

3. Test the health endpoint:
   - Open: `https://your-preview-url.vercel.app/api/health`
   - Should see: `{"status": "healthy", "database": "connected"}`

4. If health check fails:
   - Check Vercel deployment logs
   - Verify environment variables are set
   - Check service account permissions

### Step 6: Full Preview Testing

Run through this checklist:

**Search Functionality:**
- [ ] Navigate to search page
- [ ] Enter search query (e.g., "medical")
- [ ] Verify results load from BigQuery (not demo data)
- [ ] Check console for "Connected to live database" message
- [ ] Test filters (date range, organization)
- [ ] Test pagination
- [ ] Verify export to CSV works
- [ ] Verify export to JSON works

**Organization Profile:**
- [ ] Click organization from search results
- [ ] Profile loads with real BigQuery data
- [ ] All 6 metric cards show values
- [ ] Activity list displays
- [ ] Pagination works
- [ ] Related organizations show
- [ ] Lobbyist network displays
- [ ] Export functions work

**Performance:**
- [ ] Search completes in < 5 seconds
- [ ] Organization profile loads in < 5 seconds
- [ ] No console errors
- [ ] Network tab shows successful API calls

**Error Handling:**
- [ ] Invalid query handled gracefully
- [ ] Network issues fall back to demo data
- [ ] Error messages display appropriately

### Step 7: Monitor BigQuery Usage

1. Go to Google Cloud Console → BigQuery
2. Click **Query History** tab
3. Verify queries are being executed
4. Check data scanned per query
5. Monitor for any failed queries

### Step 8: Production Deployment

**Only proceed if ALL preview tests pass!**

1. Merge to main branch:
```bash
git checkout main
git merge feature/bigquery-integration
```

2. Push to production:
```bash
git push origin main
```

3. Vercel automatically deploys to production

4. Wait for deployment to complete (check Vercel dashboard)

### Step 9: Production Validation

1. Visit production URL: `https://ca-lobby-webapp.vercel.app`

2. Run through the same testing checklist as preview

3. Monitor for 30 minutes:
   - Check Vercel logs for errors
   - Monitor BigQuery query history
   - Watch for user reports

### Step 10: Rollback Plan (If Needed)

**If there are critical issues:**

Option A: Revert commit
```bash
git revert HEAD
git push origin main
```

Option B: Set environment variable to disable backend
```bash
# In Vercel dashboard:
# Set USE_MOCK_DATA=true
# Redeploy
```

Option C: Rollback to previous deployment
1. Go to Vercel dashboard
2. Find previous deployment
3. Click **Promote to Production**

**✅ Phase 4.1 Deliverables:**
- [ ] Feature branch created and pushed
- [ ] Preview deployment successful
- [ ] Preview testing checklist completed
- [ ] Production deployment successful
- [ ] Production validation completed
- [ ] Rollback procedures documented

---

## 4.2: Integration Testing Checklist

**Duration:** 2-3 hours

### Complete Testing Matrix

Print this checklist and mark off each item:

#### Search Functionality Tests

**Basic Search:**
- [ ] Empty search returns recent results
- [ ] Search by organization name works
- [ ] Search by lobbyist name works
- [ ] Search with special characters works
- [ ] Search with numbers works

**Advanced Filters:**
- [ ] Date range filter works
- [ ] Start date only filter works
- [ ] End date only filter works
- [ ] Amount range filter works
- [ ] Category filter works
- [ ] Multiple filters combined work

**Results Display:**
- [ ] Results show correct data
- [ ] Results match BigQuery data (spot check)
- [ ] Pagination works (next/previous)
- [ ] Page numbers display correctly
- [ ] Results per page setting works

**Export Functions:**
- [ ] Export to CSV downloads file
- [ ] CSV contains correct data
- [ ] CSV opens in Excel correctly
- [ ] Export to JSON downloads file
- [ ] JSON is valid and parseable

#### Organization Profile Tests

**Profile Loading:**
- [ ] Click org from search loads profile
- [ ] Direct URL navigation works
- [ ] Profile shows correct organization
- [ ] All data sections load

**Metrics Display:**
- [ ] Total spending shows correct value
- [ ] Total activities count is accurate
- [ ] Total lobbyists count is accurate
- [ ] Date range is correct
- [ ] Average spending calculates correctly
- [ ] Quarter breakdown is accurate

**Activity List:**
- [ ] Activities display in table
- [ ] Pagination works
- [ ] Activities are sorted by date
- [ ] All columns show data
- [ ] Activity details are accurate

**Related Data:**
- [ ] Lobbyist network displays
- [ ] Related organizations show
- [ ] Similarity scores make sense
- [ ] Click related org navigates correctly

**Profile Export:**
- [ ] Export CSV works
- [ ] Export JSON works
- [ ] Export Activities works
- [ ] Files contain correct data

#### Performance Tests

**Response Times:**
- [ ] Health check: < 1 second
- [ ] Search (simple): < 3 seconds
- [ ] Search (complex): < 5 seconds
- [ ] Organization profile: < 3 seconds
- [ ] Export generation: < 5 seconds

**Load Testing:**
- [ ] 10 consecutive searches work
- [ ] Multiple tabs work simultaneously
- [ ] No memory leaks in browser
- [ ] No connection timeout errors

**Cold Start:**
- [ ] First request after idle: < 10 seconds
- [ ] Subsequent requests: < 3 seconds

#### Error Handling Tests

**Network Errors:**
- [ ] Disconnect WiFi → graceful fallback
- [ ] Slow connection → loading indicator
- [ ] API timeout → error message
- [ ] Invalid URL → 404 page

**Invalid Inputs:**
- [ ] Empty organization name → handled
- [ ] Invalid date format → handled
- [ ] SQL injection attempt → blocked
- [ ] XSS attempt → sanitized

**Backend Errors:**
- [ ] BigQuery quota exceeded → fallback
- [ ] Invalid credentials → error message
- [ ] Database timeout → retry logic
- [ ] Malformed response → error handling

#### Security Tests

**Authentication:**
- [ ] Unauthenticated requests rejected (if auth enabled)
- [ ] Invalid tokens rejected
- [ ] Token expiration handled
- [ ] Session timeout works

**Data Security:**
- [ ] Credentials not exposed in responses
- [ ] No sensitive data in console logs
- [ ] No sensitive data in URLs
- [ ] CORS configured correctly

**SQL Injection:**
- [ ] `'; DROP TABLE--` in search → blocked
- [ ] `OR 1=1` in filters → blocked
- [ ] Special chars sanitized

#### Monitoring Tests

**Logging:**
- [ ] API calls logged in Vercel
- [ ] Errors logged with stack traces
- [ ] Query times logged
- [ ] Vercel dashboard shows metrics

**BigQuery Monitoring:**
- [ ] Queries visible in Cloud Console
- [ ] Query costs calculated
- [ ] Failed queries logged
- [ ] Data scanned metrics available

**Health Monitoring:**
- [ ] /api/health returns 200
- [ ] Health check shows database status
- [ ] Uptime monitoring works

#### Browser Compatibility

**Desktop Browsers:**
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

**Mobile Browsers:**
- [ ] iOS Safari
- [ ] Android Chrome
- [ ] Responsive design works

#### Accessibility Tests

**Keyboard Navigation:**
- [ ] Tab through search form
- [ ] Enter submits search
- [ ] Escape clears/cancels
- [ ] Arrow keys for pagination

**Screen Reader:**
- [ ] Form labels read correctly
- [ ] Error messages announced
- [ ] Loading states announced
- [ ] Results count announced

**✅ Phase 4.2 Deliverables:**
- [ ] All test cases executed
- [ ] Pass rate: _____% (target: >95%)
- [ ] Issues documented
- [ ] Critical issues resolved
- [ ] Known issues documented for future

**🎉 Phase 4 Complete!** Application is deployed and tested with BigQuery integration.

---

# Phase 5: Monitoring & Optimization

**Total Duration:** 5-7 hours

---

## 5.1: Monitoring Setup

**Duration:** 2-3 hours

### Step 1: Enable Vercel Analytics

1. Install Vercel Analytics:
```bash
cd /Users/michaelingram/Documents/GitHub/CA_lobby
npm install @vercel/analytics
```

2. Add to `src/index.js`:

```javascript
import { Analytics } from '@vercel/analytics/react';

// In your root component
function App() {
  return (
    <>
      {/* Your app components */}
      <Analytics />
    </>
  );
}
```

3. Deploy the change:
```bash
git add package.json package-lock.json src/index.js
git commit -m "Monitoring: Add Vercel Analytics"
git push origin main
```

4. View analytics:
   - Go to Vercel Dashboard → Your Project → Analytics

### Step 2: Configure BigQuery Logging

1. Go to Google Cloud Console → BigQuery

2. Enable query logging:
   - Click **Query Settings**
   - Enable **"Save query history"**
   - Set retention to 30 days

3. Create a saved query for monitoring:

```sql
-- Save as "Daily Query Cost Monitor"
SELECT
  DATE(creation_time) as query_date,
  user_email,
  COUNT(*) as total_queries,
  SUM(total_bytes_processed) / POW(10, 12) as tb_processed,
  SUM(total_bytes_processed) / POW(10, 12) * 5 as estimated_cost_usd
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE
  creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND job_type = 'QUERY'
  AND state = 'DONE'
GROUP BY query_date, user_email
ORDER BY query_date DESC;
```

### Step 3: Set Up Cost Alerts

1. In Google Cloud Console, go to **Billing** → **Budgets & Alerts**

2. Click **CREATE BUDGET**

3. Configure budget:
   - **Name:** CA Lobby BigQuery Monthly Budget
   - **Projects:** Select your project
   - **Services:** BigQuery
   - **Budget amount:** $20 per month
   - **Alerts:** 50%, 80%, 100%, 120%

4. Add email notification for your email address

5. Click **FINISH**

### Step 4: Create Monitoring Dashboard

1. Create a simple monitoring page:

Create `public/monitoring.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>CA Lobby - System Monitoring</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
    }
    .metric-card {
      border: 1px solid #ddd;
      border-radius: 8px;
      padding: 16px;
      margin: 16px 0;
    }
    .metric-value {
      font-size: 32px;
      font-weight: bold;
      color: #2563eb;
    }
    .status-ok { color: #10b981; }
    .status-warning { color: #f59e0b; }
    .status-error { color: #ef4444; }
  </style>
</head>
<body>
  <h1>CA Lobby System Monitoring</h1>

  <div class="metric-card">
    <h3>Backend Health</h3>
    <div id="backend-status" class="metric-value">Checking...</div>
    <p id="backend-message"></p>
  </div>

  <div class="metric-card">
    <h3>Last Update</h3>
    <div id="last-update" class="metric-value"></div>
  </div>

  <script>
    async function checkHealth() {
      try {
        const response = await fetch('/api/health');
        const data = await response.json();

        const statusEl = document.getElementById('backend-status');
        const messageEl = document.getElementById('backend-message');

        if (data.status === 'healthy') {
          statusEl.textContent = '✓ Healthy';
          statusEl.className = 'metric-value status-ok';
          messageEl.textContent = 'Database connection active';
        } else {
          statusEl.textContent = '✗ Unhealthy';
          statusEl.className = 'metric-value status-error';
          messageEl.textContent = data.error || 'Unknown error';
        }
      } catch (error) {
        document.getElementById('backend-status').textContent = '✗ Error';
        document.getElementById('backend-status').className = 'metric-value status-error';
        document.getElementById('backend-message').textContent = error.message;
      }

      document.getElementById('last-update').textContent = new Date().toLocaleString();
    }

    // Check on load and every 30 seconds
    checkHealth();
    setInterval(checkHealth, 30000);
  </script>
</body>
</html>
```

2. Access monitoring dashboard at: `https://your-app.vercel.app/monitoring.html`

### Step 5: Configure Error Tracking (Optional)

1. Consider adding Sentry for error tracking:

```bash
npm install @sentry/react
```

2. Initialize in `src/index.js`:

```javascript
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "your-sentry-dsn",
  environment: process.env.NODE_ENV,
  tracesSampleRate: 0.1,
});
```

**✅ Phase 5.1 Deliverables:**
- [ ] Vercel Analytics enabled
- [ ] BigQuery logging configured
- [ ] Cost alerts set up (Budget: $20/month)
- [ ] Monitoring dashboard created
- [ ] Error tracking configured (optional)

---

## 5.2: Performance Optimization

**Duration:** 3-4 hours

### Step 1: Implement Query Caching

1. Update `api/_database.py` to add caching:

```python
from functools import lru_cache
import hashlib
import time

# Simple in-memory cache (persists across warm starts)
_query_cache = {}
CACHE_TTL = 300  # 5 minutes

def get_cached_query(cache_key):
    """Get cached query result if not expired."""
    if cache_key in _query_cache:
        result, timestamp = _query_cache[cache_key]
        if time.time() - timestamp < CACHE_TTL:
            return result
        else:
            # Cache expired
            del _query_cache[cache_key]
    return None

def cache_query(cache_key, result):
    """Cache query result with timestamp."""
    _query_cache[cache_key] = (result, time.time())

def execute_query_with_cache(query):
    """Execute query with caching."""
    # Generate cache key from query
    cache_key = hashlib.md5(query.encode()).hexdigest()

    # Check cache
    cached_result = get_cached_query(cache_key)
    if cached_result:
        return cached_result

    # Execute query
    client = get_database_client()
    result = client.query(query).result()

    # Convert to list to cache
    result_list = [dict(row) for row in result]

    # Cache result
    cache_query(cache_key, result_list)

    return result_list
```

2. Update `api/search.py` to use caching:

```python
from _database import execute_query_with_cache

# In the handler:
results = execute_query_with_cache(sql_query)
```

### Step 2: Optimize SQL Queries

1. Update queries to select only needed columns:

**Before:**
```sql
SELECT * FROM `ca_lobby.lobby_activities`
```

**After:**
```sql
SELECT
  organization_name,
  lobbyist_name,
  filing_date,
  amount,
  quarter,
  year
FROM `ca_lobby.lobby_activities`
```

2. Add WHERE clauses to limit data scanned:

```sql
-- Always filter by date to reduce scan
WHERE filing_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 2 YEAR)
```

3. Use LIMIT to reduce results:

```sql
-- Always limit results
LIMIT 100
```

### Step 3: Add Frontend Request Debouncing

1. Install lodash if not already installed:
```bash
npm install lodash
```

2. Update `src/components/Search.js`:

```javascript
import { debounce } from 'lodash';

// Create debounced search function
const debouncedSearch = useCallback(
  debounce(async (query, filters) => {
    await performSearch(query, filters);
  }, 500), // Wait 500ms after user stops typing
  []
);

// In your input onChange:
const handleInputChange = (e) => {
  const value = e.target.value;
  setSearchQuery(value);

  // Trigger debounced search
  debouncedSearch(value, filters);
};
```

### Step 4: Implement Connection Pooling

Already implemented in `api/_database.py` with the global `_client` variable that persists across warm starts.

### Step 5: Measure Performance Improvements

1. Before optimizations, record baseline metrics:

```bash
# Run 10 searches and measure time
for i in {1..10}; do
  time curl "https://your-app.vercel.app/api/search?q=test"
done
```

2. After optimizations, record new metrics

3. Compare:
   - Average response time
   - Cache hit rate
   - BigQuery cost per query

### Step 6: Create BigQuery Partitioned Table (Advanced)

1. If you have large datasets, partition by date:

```sql
CREATE TABLE `ca_lobby.lobby_activities_partitioned`
PARTITION BY DATE(filing_date)
AS SELECT * FROM `ca_lobby.lobby_activities`;
```

2. Update queries to use partitioned table:

```python
dataset = os.getenv('BIGQUERY_DATASET', 'ca_lobby')
table = 'lobby_activities_partitioned'
```

**Performance Targets:**

| Metric | Baseline | Target | Achieved |
|--------|----------|--------|----------|
| Search Response | ___s | < 2s | ___s |
| Cache Hit Rate | 0% | > 60% | ___% |
| Cold Start | ___s | < 5s | ___s |
| BigQuery Cost/Query | $___ | < $0.01 | $___ |
| Data Scanned/Query | ___MB | < 100MB | ___MB |

**✅ Phase 5.2 Deliverables:**
- [ ] Query caching implemented
- [ ] SQL queries optimized
- [ ] Frontend debouncing added
- [ ] Performance benchmarks measured
- [ ] Targets met or improvement plan documented

**🎉 Phase 5 Complete!** System is monitored and optimized.

---

# Phase 6: Documentation & Handoff

**Total Duration:** 3-5 hours

---

## 6.1: Technical Documentation

**Duration:** 2-3 hours

### Step 1: Create Deployment Guide

Create `Documentation/Deployment/BIGQUERY_DEPLOYMENT_GUIDE.md`:

```markdown
# BigQuery Integration Deployment Guide

## Quick Start

### Prerequisites
- Google Cloud project with BigQuery dataset
- Service account with BigQuery permissions
- Vercel account with project configured

### Deployment Steps

1. **Add environment variables to Vercel:**
   - `USE_MOCK_DATA=false`
   - `BIGQUERY_DATASET=ca_lobby`
   - `BIGQUERY_PROJECT_ID=your-project-id`
   - `GOOGLE_APPLICATION_CREDENTIALS={json}`
   - `REACT_APP_USE_BACKEND_API=true`
   - `REACT_APP_API_URL=/api`

2. **Deploy to Vercel:**
   ```bash
   git push origin main
   ```

3. **Verify deployment:**
   ```bash
   curl https://your-app.vercel.app/api/health
   ```

## Troubleshooting

### Health Check Fails
- Verify environment variables are set
- Check service account permissions
- Review Vercel deployment logs

### High Query Costs
- Check cache hit rate
- Optimize SQL queries
- Add date range filters

[Include full troubleshooting guide...]
```

### Step 2: Create Operations Manual

Create `Documentation/Deployment/BIGQUERY_OPERATIONS.md`:

```markdown
# BigQuery Integration Operations Manual

## Daily Checklist

- [ ] Check Vercel deployment status
- [ ] Review error logs
- [ ] Monitor BigQuery costs
- [ ] Verify health endpoint

## Weekly Tasks

- [ ] Review query performance
- [ ] Check cache hit rates
- [ ] Analyze slow queries
- [ ] Review cost trends

## Monthly Tasks

- [ ] Rotate service account credentials
- [ ] Review and optimize queries
- [ ] Update documentation
- [ ] Security audit

[Include full operations procedures...]
```

### Step 3: Create API Reference

Create `Documentation/Deployment/API_REFERENCE.md`:

```markdown
# CA Lobby API Reference

## Endpoints

### GET /api/health
Returns backend health status.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### GET /api/search
Search lobby activities.

**Parameters:**
- `q` - Search query (optional)
- `organization` - Filter by organization (optional)
- `start_date` - Filter by start date (optional)
- `end_date` - Filter by end date (optional)
- `limit` - Results per page (default: 100)
- `offset` - Pagination offset (default: 0)

**Response:**
```json
{
  "results": [...],
  "total": 150,
  "offset": 0,
  "limit": 100
}
```

[Include full API documentation...]
```

### Step 4: Create Completion Report

Create `Documentation/Deployment/BIGQUERY_INTEGRATION_COMPLETION_REPORT.md`:

```markdown
# BigQuery Integration - Completion Report

**Date:** October [X], 2025
**Status:** ✅ COMPLETED

## Executive Summary

Successfully enabled BigQuery database integration for CA Lobby application on Vercel. System is now serving live data from BigQuery instead of demo data.

## Objectives Achieved

- [x] BigQuery dataset verified and operational
- [x] Service account created with proper permissions
- [x] Backend API converted to Vercel serverless functions
- [x] Frontend updated to use backend API
- [x] Deployed to production with zero downtime
- [x] Monitoring and optimization implemented
- [x] Documentation completed

## Implementation Details

### Phase 1: Prerequisites
- Dataset: ca_lobby with [X] records
- Service account: vercel-ca-lobby-backend
- Credentials: Secured and tested

### Phase 2: Backend
- Created 3 serverless functions (health, search, organization)
- Implemented connection pooling
- Added error handling and fallbacks

### Phase 3: Frontend
- Updated Search component
- Updated OrganizationProfile component
- Added error handling UI

### Phase 4: Deployment
- Preview deployment tested successfully
- Production deployment completed
- Zero downtime migration

### Phase 5: Monitoring
- Vercel Analytics enabled
- BigQuery cost alerts configured
- Monitoring dashboard created

## Performance Metrics

- Search response time: [X]s (target: <2s)
- Cache hit rate: [X]% (target: >60%)
- BigQuery cost: $[X]/month (target: <$20)
- Uptime: [X]% (target: >99%)

## Issues Encountered

[Document any issues and resolutions...]

## Next Steps

- Monitor performance for 1 week
- Gather user feedback
- Plan Phase 2.1 enhancements

## Sign-Off

Project Status: ✅ PRODUCTION READY
Deployment: ✅ SUCCESSFUL
Documentation: ✅ COMPLETE

Completed by: [Your Name]
Date: October [X], 2025
```

### Step 5: Update Master Plan

1. Open `Documentation/General/MASTER_PROJECT_PLAN.md`

2. Update with completion:

```markdown
#### BigQuery Integration ✅ COMPLETED
**Duration:** October 2-[X], 2025
**Status:** ✅ COMPLETED

**Deliverables Achieved:**
- ✅ Backend API deployed as serverless functions
- ✅ Frontend integrated with backend
- ✅ Production deployment successful
- ✅ Monitoring and optimization complete

**Reference Documents:**
- [Implementation Plan](../Deployment/BIGQUERY_VERCEL_INTEGRATION_PLAN.md)
- [Complete Guide](../Deployment/BIGQUERY_COMPLETE_IMPLEMENTATION_GUIDE.md)
- [Completion Report](../Deployment/BIGQUERY_INTEGRATION_COMPLETION_REPORT.md)
```

**✅ Phase 6.1 Deliverables:**
- [ ] Deployment guide created
- [ ] Operations manual created
- [ ] API reference documented
- [ ] Completion report filed
- [ ] Master plan updated

---

## 6.2: Knowledge Transfer

**Duration:** 1-2 hours

### Step 1: Create Quick Reference Card

Create `Documentation/Deployment/QUICK_REFERENCE.md`:

```markdown
# BigQuery Integration - Quick Reference

## Emergency Contacts
- Vercel Dashboard: https://vercel.com/dashboard
- Google Cloud Console: https://console.cloud.google.com
- Support: [your email]

## Common Commands

### Check Health
```bash
curl https://ca-lobby-webapp.vercel.app/api/health
```

### View Logs
```bash
vercel logs
```

### Rollback to Demo Data
Set environment variable in Vercel:
`USE_MOCK_DATA=true`

## Environment Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| USE_MOCK_DATA | false | Enable/disable backend |
| BIGQUERY_DATASET | ca_lobby | Dataset name |
| GOOGLE_APPLICATION_CREDENTIALS | {json} | Service account key |

## Monitoring URLs

- Vercel Analytics: [URL]
- BigQuery Console: [URL]
- Monitoring Dashboard: https://your-app.vercel.app/monitoring.html
```

### Step 2: Create Emergency Runbook

Create `Documentation/Deployment/EMERGENCY_RUNBOOK.md`:

```markdown
# Emergency Runbook

## Problem: Site Down

1. Check Vercel status: https://vercel.com/status
2. Check deployment logs in Vercel dashboard
3. If backend issue, set `USE_MOCK_DATA=true`
4. Redeploy: `vercel --prod`

## Problem: High Error Rate

1. Check Vercel logs for error patterns
2. Check BigQuery status in Cloud Console
3. Verify service account permissions
4. Rollback to previous deployment if needed

## Problem: High Costs

1. Check BigQuery job history
2. Identify expensive queries
3. Add caching or optimize queries
4. Set stricter query limits
5. Consider setting daily quota in BigQuery

## Problem: Slow Queries

1. Check query execution times in logs
2. Verify cache is working (check hit rate)
3. Check for missing indexes
4. Optimize SQL queries
5. Consider partitioned tables

## Rollback Procedures

### Option 1: Revert Code
```bash
git revert HEAD
git push origin main
```

### Option 2: Environment Variable
Vercel Dashboard → Settings → Environment Variables
Set `USE_MOCK_DATA=true`

### Option 3: Previous Deployment
Vercel Dashboard → Deployments → [Select previous] → Promote to Production
```

### Step 3: Test Rollback Procedures

1. Practice rolling back to demo data:
   - Set `USE_MOCK_DATA=true` in Vercel
   - Verify site switches to demo data
   - Set back to `false`
   - Verify backend connection restored

2. Document rollback time: _____minutes

**✅ Phase 6.2 Deliverables:**
- [ ] Quick reference created
- [ ] Emergency runbook created
- [ ] Rollback procedures tested
- [ ] Team briefed on new system

**🎉 Phase 6 Complete!** Full documentation and handoff materials ready.

---

# 📊 Final Completion Checklist

## All Phases Summary

### ✅ Phase 1: Prerequisites & Preparation
- [ ] BigQuery dataset verified
- [ ] Service account created and tested
- [ ] Credentials secured

### ✅ Phase 2: Backend Deployment Configuration
- [ ] Serverless functions created
- [ ] Environment variables configured
- [ ] Local testing passed

### ✅ Phase 3: Frontend Configuration
- [ ] Search component updated
- [ ] Organization profile updated
- [ ] Error handling implemented

### ✅ Phase 4: Deployment & Testing
- [ ] Preview deployment successful
- [ ] Production deployment successful
- [ ] All tests passed

### ✅ Phase 5: Monitoring & Optimization
- [ ] Monitoring configured
- [ ] Performance optimized
- [ ] Targets met

### ✅ Phase 6: Documentation & Handoff
- [ ] All documentation created
- [ ] Knowledge transfer complete
- [ ] Runbooks tested

## Success Criteria

**Functional:**
- [x] Search returns real BigQuery data
- [x] Organization profiles accurate
- [x] All features working
- [x] Authentication integrated

**Performance:**
- [ ] Search latency < 3s (P95)
- [ ] Cache hit rate > 60%
- [ ] Uptime > 99.5%
- [ ] Error rate < 1%

**Cost:**
- [ ] Monthly cost < $20
- [ ] No quota overages
- [ ] Alerts configured

**Operational:**
- [ ] Monitoring active
- [ ] Documentation complete
- [ ] Rollback tested

---

## 🎯 Next Steps After Completion

1. **Monitor for 1 week**
   - Daily health checks
   - Cost monitoring
   - Performance tracking

2. **Gather user feedback**
   - Survey users
   - Analyze usage patterns
   - Identify improvement areas

3. **Plan enhancements**
   - Advanced analytics
   - Additional data sources
   - Performance tuning

4. **Regular maintenance**
   - Rotate credentials (90 days)
   - Review and optimize queries
   - Update documentation

---

**Project:** CA Lobby BigQuery Integration
**Status:** Ready for Implementation
**Estimated Duration:** 2-3 days
**Last Updated:** October 2, 2025

---

## 📚 Document References

- [Original Plan](./BIGQUERY_VERCEL_INTEGRATION_PLAN.md)
- [Master Project Plan](../General/MASTER_PROJECT_PLAN.md)
- [Demo Data Configuration](../General/DEMO_DATA_CONFIGURATION.md)
- [Commit Strategy](../General/COMMIT_STRATEGY.md)

---

**Ready to begin? Start with Phase 1.1!** 🚀
