# Backend-Frontend Connection Plan

**Project:** CA Lobby - California Lobbying Database & Web Application
**Document Version:** 1.0
**Date Created:** October 29, 2025
**Author:** Production Deployment Guide
**Purpose:** Step-by-step plan to connect BigQuery backend to React frontend
**Audience:** First-time production deployment

---

## 📋 Executive Summary

This document provides a complete, beginner-friendly implementation plan to connect the CA Lobby React frontend (deployed on Vercel) to the BigQuery backend database. This is the missing piece to transform the application from demo mode to production mode with real California lobbying data.

**Current State:**
- ✅ BigQuery database populated with CA lobbying data (13 tables, 73 views)
- ✅ React frontend deployed on Vercel using demo/sample data
- ✅ Data pipeline operational (`backend/pipeline/`)
- ❌ **No API connection between frontend and backend**

**Target State:**
- ✅ Vercel serverless functions querying BigQuery
- ✅ React frontend consuming real-time BigQuery data
- ✅ Fully operational production application

**Total Implementation Time:** 8-12 hours
**Skill Level Required:** Beginner-friendly with detailed instructions

---

## 📐 Architecture Overview

### Current Architecture (Demo Mode)

```
┌─────────────────────────────────────────────────────────────┐
│                     BigQuery Database                        │
│  - 13 Tables (CVR_LOBBY_DISCLOSURE_CD, LPAY_CD, etc.)      │
│  - 73 Views (4 layers: base, integration, analytical)       │
│  - Full California Lobbying Data                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ Manual CSV Export (Alameda only)
                           ▼
                  ┌────────────────────┐
                  │  Sample JSON Files │
                  │  (frontend/src/    │
                  │   data/)           │
                  └────────┬───────────┘
                           │
                           │ Static Import
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              React Frontend (Vercel)                         │
│  - Uses hardcoded demo data                                 │
│  - ~11 Alameda County organizations only                    │
│  - No search/filter capabilities                            │
└─────────────────────────────────────────────────────────────┘
```

**Limitations:**
- ❌ Static data only
- ❌ Limited to Alameda County
- ❌ No real-time updates
- ❌ No search functionality

### Target Architecture (Production Mode)

```
┌─────────────────────────────────────────────────────────────┐
│                  Google BigQuery                             │
│  - 13 Tables + 73 Views                                     │
│  - Complete California Dataset                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ SQL Queries (Parameterized)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Vercel Serverless Functions                     │
│  /api/health.py      - Health check endpoint               │
│  /api/search.py      - Search & filter lobbying data       │
│  /api/analytics.py   - Analytics aggregations              │
│                                                              │
│  Features:                                                   │
│  - BigQuery client connection                               │
│  - Parameterized queries (SQL injection protection)        │
│  - Response caching (5-minute TTL)                          │
│  - Error handling & logging                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ JSON API Responses
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              React Frontend (Vercel)                         │
│  - Fetches data from /api/* endpoints                       │
│  - Real-time search & filtering                             │
│  - Complete California dataset                              │
│  - Dynamic updates                                           │
└─────────────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ Real-time data access
- ✅ Statewide coverage (10,000+ organizations)
- ✅ Search and filter capabilities
- ✅ Always current data

---

## 🎯 Implementation Plan

### Phase 1: Prerequisites & Verification (30 minutes)

**Objective:** Verify access to BigQuery and gather required credentials.

#### 1.1 Verify BigQuery Access

**Steps:**

1. **Access Google Cloud Console**
   - Navigate to: https://console.cloud.google.com
   - Sign in with your Google account
   - Verify you can access the project

2. **Locate Project ID**
   - At the top of the Google Cloud Console, note your Project ID
   - Example: `ca-lobby-project-123456`
   - **Document it here:** `ca-lobby`

3. **Verify BigQuery Dataset**
   - Navigate to: https://console.cloud.google.com/bigquery
   - In the Explorer panel (left side), expand your project
   - Confirm you see the `ca_lobby` dataset
   - Click on it to view tables

4. **Check Data Availability**
   - Click "Compose new query"
   - Run this test query (replace `ca-lobby`):

   ```sql
   SELECT COUNT(*) as total_records
   FROM `YOUR_PROJECT_ID.ca_lobby.CVR_LOBBY_DISCLOSURE_CD`
   LIMIT 1;
   ```
   UserNote- Actual Query
  ```
  SELECT COUNT(*) as total_records
  FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd`
  LIMIT 1;
  ```

   - **Expected Result:** A number > 0 (confirms data exists)
   - **Document count:** `4266899`

#### 1.2 Obtain Service Account Credentials

**What is a Service Account?**
A service account is a special Google account that your application uses to access BigQuery programmatically.

**Steps:**

1. **Create Service Account** (if you don't have one)
   - Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
   - Click "Create Service Account"
   - Name: `ca-lobby-api`
   - Description: `API access to BigQuery for CA Lobby application`
   - Click "Create and Continue"

2. **Grant BigQuery Permissions**
   - Select role: `BigQuery Data Viewer`
   - Select role: `BigQuery Job User`
   - Click "Continue" → "Done"

3. **Create JSON Key**
   - Find your new service account in the list
   - Click the three dots (⋮) → "Manage Keys"
   - Click "Add Key" → "Create new key"
   - Choose "JSON" format
   - Click "Create"
   - **A JSON file will download automatically**

4. **Secure the Credentials File**
   - Move the JSON file to a secure location
   - **NEVER commit this file to git**
   - Example location: `~/credentials/ca-lobby-service-account.json`
   - **Document path:** `/Users/michaelingram/Documents/CA_lobby/ca-lobby-e1e196c41bdf.json`

**✅ Phase 1 Complete When:**
- [ ] You have your Google Cloud Project ID
- [ ] BigQuery dataset `ca_lobby` is accessible
- [ ] Test query returns data
- [ ] Service account JSON key downloaded and secured

---

### Phase 2: Create Backend API Structure (4-5 hours)

**Objective:** Build Vercel serverless functions to query BigQuery.

#### 2.1 Create API Directory Structure

**Location:** Project root (`ca-lobby_mono/`)

**Create these directories and files:**

```
ca-lobby_mono/
├── api/                              # NEW - Serverless functions
│   ├── _utils/                       # Shared utilities
│   │   ├── __init__.py              # Empty file (makes it a Python package)
│   │   ├── bigquery_client.py       # BigQuery connection wrapper
│   │   └── response.py              # JSON response helper
│   ├── health.py                     # Health check endpoint
│   ├── search.py                     # Search endpoint
│   └── analytics.py                  # Analytics endpoint
└── requirements.txt                  # Python dependencies (update)
```

**Commands to create structure:**

```bash
# Navigate to project root
cd /Users/michaelingram/Documents/GitHub/ca-lobby_mono

# Create directories
mkdir -p api/_utils

# Create empty __init__.py
touch api/_utils/__init__.py

# Create placeholder files (we'll populate them next)
touch api/_utils/bigquery_client.py
touch api/_utils/response.py
touch api/health.py
touch api/search.py
touch api/analytics.py
```

#### 2.2 Implement BigQuery Client Wrapper

**File:** `api/_utils/bigquery_client.py`

**Purpose:** Manages BigQuery connection and query execution.

**Code Implementation:**

```python
"""
BigQuery Client Wrapper for Vercel Serverless Functions
Handles connection, query execution, and error management
"""

import os
import json
from google.cloud import bigquery
from google.oauth2 import service_account

class BigQueryClient:
    """Singleton BigQuery client for serverless functions"""

    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BigQueryClient, cls).__new__(cls)
            cls._instance._initialize_client()
        return cls._instance

    def _initialize_client(self):
        """Initialize BigQuery client with service account credentials"""
        try:
            # Get credentials from environment variable (Vercel sets this)
            credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')

            if not credentials_json:
                raise ValueError("GOOGLE_APPLICATION_CREDENTIALS_JSON not set")

            # Parse JSON credentials
            credentials_info = json.loads(credentials_json)

            # Create credentials object
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info
            )

            # Get project ID
            project_id = os.environ.get('BIGQUERY_PROJECT_ID') or credentials_info['project_id']

            # Initialize BigQuery client
            self._client = bigquery.Client(
                credentials=credentials,
                project=project_id
            )

            print(f"✅ BigQuery client initialized for project: {project_id}")

        except Exception as e:
            print(f"❌ Failed to initialize BigQuery client: {e}")
            raise

    def execute_query(self, query, parameters=None):
        """
        Execute a BigQuery query with optional parameters

        Args:
            query (str): SQL query to execute
            parameters (list): List of bigquery.ScalarQueryParameter objects

        Returns:
            list: Query results as list of dictionaries
        """
        try:
            # Configure query job
            job_config = bigquery.QueryJobConfig()

            # Add parameters if provided (prevents SQL injection)
            if parameters:
                job_config.query_parameters = parameters

            # Execute query
            query_job = self._client.query(query, job_config=job_config)

            # Get results
            results = query_job.result()

            # Convert to list of dictionaries
            rows = []
            for row in results:
                rows.append(dict(row))

            return rows

        except Exception as e:
            print(f"❌ Query execution failed: {e}")
            raise

    def test_connection(self):
        """Test BigQuery connection"""
        try:
            query = "SELECT 1 as test"
            result = self.execute_query(query)
            return result[0]['test'] == 1
        except:
            return False

# Create singleton instance
def get_bigquery_client():
    """Get or create BigQuery client instance"""
    return BigQueryClient()
```

**Key Features:**
- ✅ Singleton pattern (reuses connection across requests)
- ✅ Reads credentials from environment variables
- ✅ Supports parameterized queries (SQL injection protection)
- ✅ Error handling and logging
- ✅ Connection testing

#### 2.3 Implement Response Helper

**File:** `api/_utils/response.py`

**Purpose:** Standardizes JSON responses across all endpoints.

**Code Implementation:**

```python
"""
Response Utilities for API Endpoints
Provides consistent JSON response formatting
"""

import json
from datetime import datetime

def success_response(data, status_code=200, metadata=None):
    """
    Create a successful JSON response

    Args:
        data: Response data (dict, list, or primitive)
        status_code: HTTP status code (default: 200)
        metadata: Optional metadata dictionary

    Returns:
        tuple: (response_body, status_code, headers)
    """
    response = {
        "success": True,
        "data": data,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    # Add metadata if provided
    if metadata:
        response["metadata"] = metadata

    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",  # CORS support
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }

    return (
        json.dumps(response, default=str),  # default=str handles dates
        status_code,
        headers
    )

def error_response(message, status_code=500, error_type="ServerError"):
    """
    Create an error JSON response

    Args:
        message: Error message
        status_code: HTTP status code (default: 500)
        error_type: Type of error (e.g., "ValidationError", "NotFoundError")

    Returns:
        tuple: (response_body, status_code, headers)
    """
    response = {
        "success": False,
        "error": {
            "type": error_type,
            "message": message
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }

    return (
        json.dumps(response),
        status_code,
        headers
    )

def paginated_response(data, page, limit, total_count):
    """
    Create a paginated response with metadata

    Args:
        data: List of items for current page
        page: Current page number
        limit: Items per page
        total_count: Total number of items available

    Returns:
        tuple: (response_body, status_code, headers)
    """
    total_pages = (total_count + limit - 1) // limit  # Ceiling division

    metadata = {
        "pagination": {
            "page": page,
            "limit": limit,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }

    return success_response(data, metadata=metadata)
```

**Key Features:**
- ✅ Consistent response format across all endpoints
- ✅ CORS headers for frontend access
- ✅ Pagination support
- ✅ Error standardization

#### 2.4 Implement Health Check Endpoint

**File:** `api/health.py`

**Purpose:** Simple endpoint to verify API and BigQuery connection are working.

**Code Implementation:**

```python
"""
Health Check Endpoint
Verifies API is running and BigQuery connection is working
"""

from http.server import BaseHTTPRequestHandler
from _utils.bigquery_client import get_bigquery_client
from _utils.response import success_response, error_response

class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler"""

    def do_GET(self):
        """Handle GET request for health check"""
        try:
            # Test BigQuery connection
            client = get_bigquery_client()
            db_connected = client.test_connection()

            # Prepare response data
            health_data = {
                "status": "healthy" if db_connected else "degraded",
                "api": "online",
                "database": "connected" if db_connected else "disconnected",
                "service": "ca-lobby-api",
                "version": "1.0.0"
            }

            # Return success response
            body, status, headers = success_response(health_data)

            self.send_response(status)
            for key, value in headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body.encode())

        except Exception as e:
            # Return error response
            body, status, headers = error_response(
                message=f"Health check failed: {str(e)}",
                status_code=500
            )

            self.send_response(status)
            for key, value in headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body.encode())

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
```

**Testing:**
- Endpoint: `GET /api/health`
- Expected Response:
  ```json
  {
    "success": true,
    "data": {
      "status": "healthy",
      "api": "online",
      "database": "connected",
      "service": "ca-lobby-api",
      "version": "1.0.0"
    },
    "timestamp": "2025-10-29T12:00:00Z"
  }
  ```

#### 2.5 Implement Search Endpoint

**File:** `api/search.py`

**Purpose:** Main search endpoint for lobbying activities with filtering.

**Code Implementation:**

```python
"""
Search Endpoint
Searches California lobbying data with filters
"""

from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from google.cloud import bigquery
from _utils.bigquery_client import get_bigquery_client
from _utils.response import success_response, error_response, paginated_response

class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler for search"""

    def do_GET(self):
        """Handle GET request for search"""
        try:
            # Parse query parameters
            parsed_url = urlparse(self.path)
            params = parse_qs(parsed_url.query)

            # Extract search parameters
            query_text = params.get('q', [''])[0]
            organization = params.get('organization', [''])[0]
            lobbyist = params.get('lobbyist', [''])[0]
            page = int(params.get('page', ['1'])[0])
            limit = min(int(params.get('limit', ['25'])[0]), 100)  # Max 100

            # Build SQL query
            sql_query = self._build_search_query()

            # Build query parameters (prevents SQL injection)
            query_params = []

            # Add search term parameter
            if query_text:
                query_params.append(
                    bigquery.ScalarQueryParameter('search_term', 'STRING', f'%{query_text}%')
                )

            # Add pagination parameters
            offset = (page - 1) * limit
            query_params.append(bigquery.ScalarQueryParameter('limit', 'INT64', limit))
            query_params.append(bigquery.ScalarQueryParameter('offset', 'INT64', offset))

            # Execute query
            client = get_bigquery_client()
            results = client.execute_query(sql_query, query_params)

            # Get total count (for pagination)
            count_query = self._build_count_query()
            count_result = client.execute_query(count_query, query_params[:1])  # Only search param
            total_count = count_result[0]['total'] if count_result else 0

            # Return paginated response
            body, status, headers = paginated_response(
                data=results,
                page=page,
                limit=limit,
                total_count=total_count
            )

            self.send_response(status)
            for key, value in headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body.encode())

        except Exception as e:
            # Return error response
            body, status, headers = error_response(
                message=f"Search failed: {str(e)}",
                status_code=500,
                error_type="SearchError"
            )

            self.send_response(status)
            for key, value in headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body.encode())

    def _build_search_query(self):
        """Build the main search SQL query"""
        # Note: Replace YOUR_PROJECT_ID with actual project ID
        # This will be dynamic based on environment variable

        return """
        SELECT
            filer_id,
            filer_naml as organization_name,
            filing_id,
            filing_date,
            rpt_year as year,
            rpt_period as period
        FROM `ca_lobby.CVR_LOBBY_DISCLOSURE_CD`
        WHERE
            (@search_term IS NULL OR filer_naml LIKE @search_term)
        ORDER BY filing_date DESC
        LIMIT @limit
        OFFSET @offset
        """

    def _build_count_query(self):
        """Build count query for pagination"""
        return """
        SELECT COUNT(*) as total
        FROM `ca_lobby.CVR_LOBBY_DISCLOSURE_CD`
        WHERE
            (@search_term IS NULL OR filer_naml LIKE @search_term)
        """

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
```

**Testing:**
- Endpoint: `GET /api/search?q=hospital&limit=5`
- Expected Response:
  ```json
  {
    "success": true,
    "data": [
      {
        "filer_id": "12345",
        "organization_name": "Children's Hospital Oakland",
        "filing_id": "67890",
        "filing_date": "2025-01-15",
        "year": 2025,
        "period": 1
      },
      ...
    ],
    "metadata": {
      "pagination": {
        "page": 1,
        "limit": 5,
        "total_count": 127,
        "total_pages": 26,
        "has_next": true,
        "has_prev": false
      }
    },
    "timestamp": "2025-10-29T12:00:00Z"
  }
  ```

#### 2.6 Implement Analytics Endpoint

**File:** `api/analytics.py`

**Purpose:** Provide aggregated data for charts and visualizations.

**Code Implementation:**

```python
"""
Analytics Endpoint
Provides aggregated data for visualizations
"""

from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from _utils.bigquery_client import get_bigquery_client
from _utils.response import success_response, error_response

class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler for analytics"""

    def do_GET(self):
        """Handle GET request for analytics"""
        try:
            # Parse query parameters
            parsed_url = urlparse(self.path)
            params = parse_qs(parsed_url.query)

            # Extract analytics type
            analytics_type = params.get('type', ['summary'])[0]

            # Route to appropriate analytics function
            if analytics_type == 'summary':
                data = self._get_summary_analytics()
            elif analytics_type == 'trends':
                data = self._get_trends_analytics()
            elif analytics_type == 'top_organizations':
                data = self._get_top_organizations()
            else:
                raise ValueError(f"Unknown analytics type: {analytics_type}")

            # Return success response
            body, status, headers = success_response(data)

            self.send_response(status)
            for key, value in headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body.encode())

        except Exception as e:
            # Return error response
            body, status, headers = error_response(
                message=f"Analytics failed: {str(e)}",
                status_code=500,
                error_type="AnalyticsError"
            )

            self.send_response(status)
            for key, value in headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body.encode())

    def _get_summary_analytics(self):
        """Get summary statistics"""
        query = """
        SELECT
            COUNT(DISTINCT filer_id) as total_organizations,
            COUNT(*) as total_filings,
            MAX(filing_date) as latest_filing
        FROM `ca_lobby.CVR_LOBBY_DISCLOSURE_CD`
        """

        client = get_bigquery_client()
        result = client.execute_query(query)
        return result[0] if result else {}

    def _get_trends_analytics(self):
        """Get filing trends over time"""
        query = """
        SELECT
            rpt_year as year,
            rpt_period as period,
            COUNT(*) as filing_count
        FROM `ca_lobby.CVR_LOBBY_DISCLOSURE_CD`
        WHERE rpt_year >= 2020
        GROUP BY year, period
        ORDER BY year DESC, period DESC
        LIMIT 12
        """

        client = get_bigquery_client()
        return client.execute_query(query)

    def _get_top_organizations(self):
        """Get top organizations by filing count"""
        query = """
        SELECT
            filer_id,
            filer_naml as organization_name,
            COUNT(*) as filing_count
        FROM `ca_lobby.CVR_LOBBY_DISCLOSURE_CD`
        GROUP BY filer_id, organization_name
        ORDER BY filing_count DESC
        LIMIT 10
        """

        client = get_bigquery_client()
        return client.execute_query(query)

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
```

**Testing:**
- Endpoint: `GET /api/analytics?type=summary`
- Expected Response:
  ```json
  {
    "success": true,
    "data": {
      "total_organizations": 1247,
      "total_filings": 15632,
      "latest_filing": "2025-10-15"
    },
    "timestamp": "2025-10-29T12:00:00Z"
  }
  ```

#### 2.7 Update Python Dependencies

**File:** `requirements.txt` (in project root)

Add these dependencies:

```txt
google-cloud-bigquery==3.38.0
google-auth==2.41.1
google-api-core==2.27.0
```

**✅ Phase 2 Complete When:**
- [ ] All API files created in `api/` directory
- [ ] BigQuery client wrapper implemented
- [ ] Health, Search, and Analytics endpoints created
- [ ] requirements.txt updated with BigQuery dependencies

---

### Phase 3: Configure Vercel Deployment (1 hour)

**Objective:** Configure Vercel to deploy both frontend and serverless functions.

#### 3.1 Update vercel.json Configuration

**File:** `frontend/vercel.json` → **Move to project root:** `vercel.json`

**Current Configuration:**
```json
{
  "version": 2,
  "framework": "create-react-app",
  "git": {
    "deploymentEnabled": {
      "working_branch": true
    }
  }
}
```

**New Configuration:**

```json
{
  "version": 2,
  "name": "ca-lobby-app",
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    },
    {
      "src": "api/**/*.py",
      "use": "@vercel/python",
      "config": {
        "maxDuration": 30
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ],
  "git": {
    "deploymentEnabled": {
      "working_branch": true
    }
  }
}
```

**Key Changes:**
- ✅ Added Python build configuration for `api/` directory
- ✅ Configured routing: `/api/*` → serverless functions
- ✅ Set max function duration to 30 seconds
- ✅ Static build for frontend

#### 3.2 Create .vercelignore File

**File:** `.vercelignore` (in project root)

**Purpose:** Tell Vercel what NOT to deploy.

```
# Backend pipeline (not needed in deployment)
backend/pipeline/
backend/docs/
backend/*.sql

# Python virtual environments
venv/
.venv/
env/
*.pyc
__pycache__/

# Credentials (NEVER deploy these)
*.json
!vercel.json
!package.json
!package-lock.json

# Development files
.env
.env.local
.DS_Store
```

#### 3.3 Update Frontend Build Configuration

**File:** `frontend/package.json`

Ensure these scripts exist:

```json
{
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "vercel-build": "react-scripts build"
  }
}
```

**The `vercel-build` script is what Vercel runs during deployment.**

**✅ Phase 3 Complete When:**
- [ ] vercel.json moved to project root and updated
- [ ] .vercelignore created with proper exclusions
- [ ] Frontend package.json has vercel-build script

---

### Phase 4: Configure Environment Variables (30 minutes)

**Objective:** Securely provide credentials to Vercel serverless functions.

#### 4.1 Install Vercel CLI

**Run these commands:**

```bash
# Install Vercel CLI globally
npm install -g vercel

# Verify installation
vercel --version
```

**Expected Output:** `Vercel CLI 33.0.0` (or similar)

#### 4.2 Login to Vercel

```bash
# Login to your Vercel account
vercel login
```

**This will:**
1. Open your browser
2. Ask you to confirm login
3. Link the CLI to your account

#### 4.3 Link Project to Vercel

```bash
# Navigate to project root
cd /Users/michaelingram/Documents/GitHub/ca-lobby_mono

# Link to Vercel project (or create new one)
vercel link
```

**You'll be asked:**
- Link to existing project? → **Yes** (if you already deployed frontend)
- Or create new project? → **Yes** (if first time)

#### 4.4 Add Environment Variables

**You need to add these environment variables to Vercel:**

1. **GOOGLE_APPLICATION_CREDENTIALS_JSON**

   ```bash
   vercel env add GOOGLE_APPLICATION_CREDENTIALS_JSON
   ```

   **When prompted:**
   - What's the value? → **Open your service account JSON file and copy the ENTIRE contents**
   - Expose to: → **Production, Preview, Development** (select all)

   **Example:**
   ```json
   {
     "type": "service_account",
     "project_id": "ca-lobby-project-123456",
     "private_key_id": "abc123...",
     "private_key": "-----BEGIN PRIVATE KEY-----\n...",
     "client_email": "ca-lobby-api@ca-lobby-project.iam.gserviceaccount.com",
     ...
   }
   ```

2. **BIGQUERY_PROJECT_ID**

   ```bash
   vercel env add BIGQUERY_PROJECT_ID
   ```

   **When prompted:**
   - What's the value? → **Your Google Cloud Project ID** (e.g., `ca-lobby-project-123456`)
   - Expose to: → **Production, Preview, Development** (select all)

3. **REACT_APP_USE_BACKEND_API**

   ```bash
   vercel env add REACT_APP_USE_BACKEND_API
   ```

   **When prompted:**
   - What's the value? → `true`
   - Expose to: → **Production, Preview, Development** (select all)

4. **REACT_APP_API_URL**

   ```bash
   vercel env add REACT_APP_API_URL
   ```

   **When prompted:**
   - What's the value? → `/api`
   - Expose to: → **Production, Preview, Development** (select all)

#### 4.5 Verify Environment Variables

```bash
# List all environment variables
vercel env ls
```

**Expected Output:**
```
Environment Variables
─────────────────────────────────────────────
Name                                 Value
GOOGLE_APPLICATION_CREDENTIALS_JSON  {...}
BIGQUERY_PROJECT_ID                  ca-lobby-project-123456
REACT_APP_USE_BACKEND_API            true
REACT_APP_API_URL                    /api
```

**✅ Phase 4 Complete When:**
- [ ] Vercel CLI installed and logged in
- [ ] Project linked to Vercel
- [ ] All 4 environment variables added
- [ ] Environment variables verified with `vercel env ls`

---

### Phase 5: Local Testing (1-2 hours)

**Objective:** Test everything works locally before deploying to Vercel.

#### 5.1 Test BigQuery Connection Locally

**Steps:**

1. **Set up local environment variables**

   Create a file: `.env.local` (in project root)

   ```bash
   # .env.local (DO NOT COMMIT THIS FILE)
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account.json
   BIGQUERY_PROJECT_ID=ca-lobby-project-123456
   REACT_APP_USE_BACKEND_API=true
   REACT_APP_API_URL=http://localhost:3000/api
   ```

2. **Test Python BigQuery connection**

   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r ../requirements.txt

   # Test connection
   python pipeline/Bigquery_connection.py
   ```

   **Expected Output:**
   ```
   ✅ Successfully connected to BigQuery project: ca-lobby-project-123456
   Available datasets: ['ca_lobby']
   ```

#### 5.2 Test Vercel Dev Server Locally

**Steps:**

```bash
# Navigate to project root
cd /Users/michaelingram/Documents/GitHub/ca-lobby_mono

# Start Vercel dev server
vercel dev
```

**Expected Output:**
```
Vercel CLI 33.0.0
> Ready! Available at http://localhost:3000
```

**This starts:**
- Frontend at: http://localhost:3000
- API functions at: http://localhost:3000/api/*

#### 5.3 Test Health Endpoint

**Open in browser or use curl:**

```bash
curl http://localhost:3000/api/health
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "api": "online",
    "database": "connected",
    "service": "ca-lobby-api",
    "version": "1.0.0"
  },
  "timestamp": "2025-10-29T15:30:00Z"
}
```

**✅ If you see `"database": "connected"` → BigQuery connection works!**

#### 5.4 Test Search Endpoint

```bash
curl "http://localhost:3000/api/search?q=hospital&limit=3"
```

**Expected Response:**
```json
{
  "success": true,
  "data": [
    {
      "filer_id": "12345",
      "organization_name": "Children's Hospital Oakland",
      "filing_id": "67890",
      "filing_date": "2025-01-15",
      "year": 2025,
      "period": 1
    },
    ...
  ],
  "metadata": {
    "pagination": {
      "page": 1,
      "limit": 3,
      "total_count": 127,
      "total_pages": 43,
      "has_next": true,
      "has_prev": false
    }
  },
  "timestamp": "2025-10-29T15:30:00Z"
}
```

**✅ If you see real organization names → BigQuery queries work!**

#### 5.5 Test Analytics Endpoint

```bash
curl "http://localhost:3000/api/analytics?type=summary"
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "total_organizations": 1247,
    "total_filings": 15632,
    "latest_filing": "2025-10-15"
  },
  "timestamp": "2025-10-29T15:30:00Z"
}
```

#### 5.6 Test Frontend Integration

**Steps:**

1. **Open browser:** http://localhost:3000
2. **Navigate to Search page**
3. **Type a search query:** "hospital"
4. **Verify:**
   - Results load from BigQuery (not demo data)
   - Real organization names appear
   - Clicking an organization shows real details

**✅ Phase 5 Complete When:**
- [ ] Health endpoint returns "connected"
- [ ] Search endpoint returns real BigQuery data
- [ ] Analytics endpoint returns summary statistics
- [ ] Frontend displays real data (not demo data)
- [ ] No console errors in browser

---

### Phase 6: Deploy to Vercel (1 hour)

**Objective:** Deploy to production and verify everything works.

#### 6.1 Commit Your Changes

**Steps:**

```bash
# Navigate to project root
cd /Users/michaelingram/Documents/GitHub/ca-lobby_mono

# Check status
git status

# Add all new files
git add api/
git add vercel.json
git add .vercelignore
git add requirements.txt

# Commit
git commit -m "feat: add backend API with BigQuery integration

- Create serverless functions in api/ directory
- Implement health, search, and analytics endpoints
- Add BigQuery client wrapper with connection pooling
- Configure Vercel deployment with serverless functions
- Update vercel.json with API routing
- Add environment variable support for credentials

Backend-frontend connection now complete.
API endpoints ready for production deployment."

# Push to GitHub
git push origin master
```

#### 6.2 Deploy to Vercel Preview

**Steps:**

```bash
# Deploy to preview environment
vercel deploy
```

**Expected Output:**
```
Deploying ~/Documents/GitHub/ca-lobby_mono
Inspect: https://vercel.com/...
Preview: https://ca-lobby-abc123-preview.vercel.app
```

**✅ You'll get a preview URL - save this!**

#### 6.3 Test Preview Deployment

**Test these URLs in your browser** (replace with your preview URL):

1. **Health Check:**
   ```
   https://ca-lobby-abc123-preview.vercel.app/api/health
   ```

   **Expected:** `{"success": true, "data": {"database": "connected", ...}}`

2. **Search:**
   ```
   https://ca-lobby-abc123-preview.vercel.app/api/search?q=hospital&limit=5
   ```

   **Expected:** JSON array with search results

3. **Analytics:**
   ```
   https://ca-lobby-abc123-preview.vercel.app/api/analytics?type=summary
   ```

   **Expected:** Summary statistics

4. **Frontend:**
   ```
   https://ca-lobby-abc123-preview.vercel.app
   ```

   **Expected:** Your React app loads and shows REAL data!

#### 6.4 Deploy to Production

**If preview tests pass:**

```bash
# Deploy to production
vercel --prod
```

**Expected Output:**
```
Production: https://ca-lobby.vercel.app
```

**🎉 Your app is now LIVE in production!**

#### 6.5 Final Verification

**Test production URLs:**

1. **Production Health:**
   ```
   https://ca-lobby.vercel.app/api/health
   ```

2. **Production Search:**
   ```
   https://ca-lobby.vercel.app/api/search?q=hospital
   ```

3. **Production Frontend:**
   ```
   https://ca-lobby.vercel.app
   ```

**✅ Phase 6 Complete When:**
- [ ] Code committed and pushed to GitHub
- [ ] Preview deployment successful
- [ ] All API endpoints tested in preview
- [ ] Frontend shows real data in preview
- [ ] Production deployment successful
- [ ] All endpoints working in production

---

## ✅ Verification Checklist

Use this checklist to verify your deployment is successful:

### API Endpoints

- [ ] `GET /api/health` returns 200 OK
- [ ] Health check shows `"database": "connected"`
- [ ] `GET /api/search?q=test` returns search results
- [ ] Search results contain real BigQuery data (not demo data)
- [ ] `GET /api/analytics?type=summary` returns statistics
- [ ] All endpoints return proper JSON format
- [ ] CORS headers allow frontend access

### Frontend Integration

- [ ] Frontend loads without errors
- [ ] Search page displays real organization names
- [ ] Clicking an organization shows real details
- [ ] Search filters work correctly
- [ ] Pagination works
- [ ] No console errors in browser DevTools
- [ ] Mobile responsive design works

### Performance

- [ ] Health check responds in < 1 second
- [ ] Search responds in < 3 seconds
- [ ] Analytics responds in < 5 seconds
- [ ] Frontend loads in < 3 seconds
- [ ] No timeout errors

### Security

- [ ] Service account credentials NOT in git repository
- [ ] `.gitignore` excludes `*.json` credential files
- [ ] Environment variables properly set in Vercel
- [ ] CORS configured (but not overly permissive)

---

## 🆘 Troubleshooting Guide

### Error: "Module not found: _utils"

**Problem:** Python can't find the utilities module.

**Solution:**
1. Verify `api/_utils/__init__.py` exists
2. Check file structure matches exactly
3. Ensure all files are committed and deployed

### Error: "GOOGLE_APPLICATION_CREDENTIALS_JSON not set"

**Problem:** Environment variable not configured in Vercel.

**Solution:**
```bash
# Verify environment variables
vercel env ls

# If missing, add it
vercel env add GOOGLE_APPLICATION_CREDENTIALS_JSON
```

### Error: "Table not found: ca_lobby.CVR_LOBBY_DISCLOSURE_CD"

**Problem:** BigQuery dataset or table doesn't exist, or wrong project ID.

**Solution:**
1. Check BigQuery console: https://console.cloud.google.com/bigquery
2. Verify dataset name is exactly `ca_lobby`
3. Check Project ID matches environment variable
4. Update SQL queries to use correct project ID

### Error: "Function timeout"

**Problem:** Query taking too long to execute.

**Solution:**
1. Add `LIMIT` clauses to SQL queries
2. Increase `maxDuration` in vercel.json:
   ```json
   "config": {
     "maxDuration": 60
   }
   ```
3. Optimize queries with WHERE clauses

### Error: "403 Forbidden" from BigQuery

**Problem:** Service account doesn't have permissions.

**Solution:**
1. Go to https://console.cloud.google.com/iam-admin/iam
2. Find your service account
3. Add roles:
   - BigQuery Data Viewer
   - BigQuery Job User

### Frontend shows demo data instead of real data

**Problem:** Frontend not using backend API.

**Solution:**
1. Check environment variable:
   ```bash
   vercel env ls | grep REACT_APP_USE_BACKEND_API
   ```
2. Should be: `true`
3. Redeploy after adding environment variable

### CORS errors in browser console

**Problem:** CORS headers not configured correctly.

**Solution:**
1. Verify response headers include:
   ```
   Access-Control-Allow-Origin: *
   Access-Control-Allow-Methods: GET, POST, OPTIONS
   ```
2. Check OPTIONS handler is implemented in each endpoint

---

## 📊 Success Metrics

Your deployment is successful when you achieve:

### Functional Metrics

- ✅ All API endpoints return 200 OK status
- ✅ Search returns real California lobbying data
- ✅ Frontend displays data from BigQuery (not demo files)
- ✅ Users can search and filter lobbying activities
- ✅ Organization profiles show complete details

### Performance Metrics

- ✅ Health check: < 1 second response time
- ✅ Search queries: < 3 seconds response time
- ✅ Analytics: < 5 seconds response time
- ✅ Frontend load: < 3 seconds initial load
- ✅ No timeout errors under normal load

### User Experience

- ✅ Search works on desktop and mobile
- ✅ Results are accurate and relevant
- ✅ Navigation is smooth
- ✅ No broken links or 404 errors
- ✅ Data is current (within last data refresh)

---

## 📝 Post-Deployment Tasks

After successful deployment:

### 1. Document Your Deployment

Create a file: `docs/DEPLOYMENT_SUCCESS_REPORT.md`

```markdown
# Deployment Success Report

**Date:** October 29, 2025
**Deployed By:** [Your Name]

## Deployment Details

- Production URL: https://ca-lobby.vercel.app
- API URL: https://ca-lobby.vercel.app/api
- BigQuery Project: [Your Project ID]
- Deployment Method: Vercel CLI

## Verification Results

- [x] Health check passed
- [x] Search endpoint working
- [x] Analytics endpoint working
- [x] Frontend showing real data

## Performance Metrics

- Health check response: XXms
- Search response: XXms
- Frontend load time: XXs

## Notes

[Any observations, issues encountered, or special configurations]
```

### 2. Monitor Your Application

**Set up monitoring:**

1. **Vercel Analytics**
   - Go to: https://vercel.com/dashboard
   - Enable Analytics for your project
   - Monitor real user metrics

2. **BigQuery Monitoring**
   - Check query costs: https://console.cloud.google.com/bigquery
   - Set up billing alerts if costs exceed expectations

3. **Error Tracking**
   - Monitor Vercel function logs
   - Check for 500 errors or timeouts

### 3. Optimize Performance

**After initial deployment:**

1. **Add Query Caching**
   - Implement Redis or in-memory caching
   - Cache frequently accessed queries for 5-10 minutes

2. **Optimize BigQuery Queries**
   - Use partitioned tables (by date)
   - Add clustering (by filer_id)
   - Review query costs in BigQuery console

3. **Frontend Optimization**
   - Implement lazy loading for routes
   - Add loading skeletons
   - Use React Query for client-side caching

### 4. Data Refresh Strategy

**Set up automated data refresh:**

1. **Create GitHub Action** (weekly refresh)

   File: `.github/workflows/refresh-data.yml`

   ```yaml
   name: Refresh BigQuery Data
   on:
     schedule:
       - cron: '0 0 * * 0'  # Every Sunday at midnight

   jobs:
     refresh:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Set up Python
           uses: actions/setup-python@v2
           with:
             python-version: '3.9'
         - name: Install dependencies
           run: |
             cd backend
             pip install -r requirements.txt
         - name: Download latest data
           env:
             GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.GCP_CREDENTIALS }}
           run: python backend/run_download.py
         - name: Upload to BigQuery
           env:
             GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.GCP_CREDENTIALS }}
           run: python backend/run_upload_pipeline.py
   ```

2. **Monitor refresh success**
   - Check GitHub Actions logs
   - Verify data freshness in BigQuery

---

## 🎓 Learning Resources

### Google BigQuery

- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices)
- [BigQuery Pricing](https://cloud.google.com/bigquery/pricing)

### Vercel

- [Vercel Serverless Functions](https://vercel.com/docs/serverless-functions/introduction)
- [Vercel Environment Variables](https://vercel.com/docs/environment-variables)
- [Vercel Python Runtime](https://vercel.com/docs/runtimes#official-runtimes/python)

### React

- [React Documentation](https://react.dev)
- [React Query (Data Fetching)](https://tanstack.com/query/latest)

---

## 📞 Support and Next Steps

### If You Get Stuck

1. **Review this document** - Most issues are covered in Troubleshooting
2. **Check Vercel logs** - https://vercel.com/dashboard → Your Project → Functions
3. **Review BigQuery logs** - https://console.cloud.google.com/logs
4. **Check environment variables** - `vercel env ls`

### Next Features to Implement

After successful backend-frontend connection:

1. **Advanced Search Filters**
   - Date range filtering
   - Amount range filtering
   - Multiple organization selection

2. **User Accounts**
   - Saved searches
   - Email alerts for new filings
   - Favorite organizations

3. **Data Visualizations**
   - Spending trends over time
   - Network graphs of lobbyist relationships
   - Geographic heat maps

4. **Export Functionality**
   - Export search results to CSV
   - Generate PDF reports
   - Excel downloads

---

## ✅ Document Completion

**This plan is complete when:**

- [x] All phases documented with step-by-step instructions
- [x] Code examples provided for all serverless functions
- [x] Troubleshooting guide covers common issues
- [x] Verification checklist ensures deployment success
- [x] Post-deployment tasks defined

**Document Status:** ✅ **READY FOR IMPLEMENTATION**

**Estimated Total Time:** 8-12 hours (including testing and troubleshooting)

**Prerequisites:**
- [ ] Google Cloud account with BigQuery access
- [ ] Service account credentials (JSON file)
- [ ] Vercel account
- [ ] Node.js and Python 3.9+ installed

**Next Steps:**
1. Read through entire document
2. Gather prerequisites (credentials, project ID)
3. Start with Phase 1: Prerequisites & Verification
4. Follow each phase sequentially
5. Test thoroughly at each step
6. Document your success!

---

**Good luck with your first production deployment! 🚀**

**Remember:** Take your time, test at each step, and don't skip the verification steps. You've got this!
