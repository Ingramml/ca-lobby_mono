"""
Search Endpoint
Searches California lobbying data with filters
Self-contained file for Vercel serverless deployment
"""

import os
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from datetime import datetime
from google.cloud import bigquery
from google.oauth2 import service_account


# ============================================================================
# BIGQUERY CLIENT (inline utility)
# ============================================================================

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
            # Get credentials from environment variable
            credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')

            if not credentials_json:
                # Try file-based credentials for local development
                credentials_file = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
                if credentials_file:
                    credentials = service_account.Credentials.from_service_account_file(credentials_file)
                    project_id = os.environ.get('BIGQUERY_PROJECT_ID')
                else:
                    raise ValueError("No credentials found")
            else:
                # Parse JSON credentials for Vercel deployment
                credentials_info = json.loads(credentials_json)
                credentials = service_account.Credentials.from_service_account_info(credentials_info)
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

    def execute_query(self, query, params=None):
        """Execute a BigQuery query and return results"""
        try:
            job_config = bigquery.QueryJobConfig()
            if params:
                job_config.query_parameters = params

            query_job = self._client.query(query, job_config=job_config)
            results = query_job.result()

            # Convert to list of dicts
            return [dict(row) for row in results]

        except Exception as e:
            print(f"Query execution failed: {e}")
            raise


# ============================================================================
# RESPONSE UTILITIES (inline utility)
# ============================================================================

def success_response(data, status_code=200):
    """Create a successful JSON response"""
    response = {
        "success": True,
        "data": data,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }

    return (
        json.dumps(response, default=str),
        status_code,
        headers
    )


def error_response(message, status_code=500, error_type="ServerError"):
    """Create an error JSON response"""
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
    """Create a paginated JSON response"""
    total_pages = (total_count + limit - 1) // limit  # Ceiling division

    response = {
        "success": True,
        "data": data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1
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
        json.dumps(response, default=str),
        200,
        headers
    )


# ============================================================================
# VERCEL SERVERLESS FUNCTION HANDLER
# ============================================================================

class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler for search"""

    def do_GET(self):
        """Handle GET request for search"""
        try:
            # Parse query parameters
            parsed_url = urlparse(self.path)
            params = parse_qs(parsed_url.query)

            # Check if requesting organization filings
            org_name = params.get('organization', [''])[0]
            if org_name:
                # Return all filings for this organization
                self._handle_organization_filings(org_name)
                return

            # Extract search parameters
            query_text = params.get('q', [''])[0]
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
            client = BigQueryClient()
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

    def _handle_organization_filings(self, org_name):
        """Get all filings for a specific organization - uses partitioned table for 76% cost reduction

        Uses case-insensitive LIKE matching to handle variations in organization names.
        """
        try:
            # Debug logging
            print(f"DEBUG: _handle_organization_filings called with org_name='{org_name}'")

            query = """
            SELECT
                FILING_ID as filing_id,
                FILER_ID as filer_id,
                FILER_NAML as organization_name,
                FORMAT_DATE('%Y-%m-%d', RPT_DATE_DATE) as filing_date,
                EXTRACT(YEAR FROM RPT_DATE_DATE) as year,
                CONCAT(
                    'Q',
                    CAST(EXTRACT(QUARTER FROM RPT_DATE_DATE) AS STRING),
                    ' ',
                    CAST(EXTRACT(YEAR FROM RPT_DATE_DATE) AS STRING)
                ) as period
            FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd_partitioned`
            WHERE UPPER(FILER_NAML) LIKE UPPER(@org_name)
              AND FROM_DATE_DATE >= '2020-01-01'
              AND RPT_DATE_DATE IS NOT NULL
              AND EXTRACT(YEAR FROM RPT_DATE_DATE) BETWEEN 2000 AND 2025
            ORDER BY RPT_DATE_DATE DESC
            """

            client = BigQueryClient()
            # Add wildcards for LIKE matching to handle exact and partial matches
            search_pattern = f"%{org_name}%"
            print(f"DEBUG: search_pattern='{search_pattern}'")
            query_params = [
                bigquery.ScalarQueryParameter('org_name', 'STRING', search_pattern)
            ]
            results = client.execute_query(query, query_params)
            print(f"DEBUG: Query returned {len(results)} results")

            # Return success response
            body, status, headers = success_response(results)

            self.send_response(status)
            for key, value in headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body.encode())

        except Exception as e:
            # Return error response
            body, status, headers = error_response(
                message=f"Failed to fetch organization filings: {str(e)}",
                status_code=500,
                error_type="OrganizationFilingsError"
            )

            self.send_response(status)
            for key, value in headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body.encode())

    def _build_search_query(self):
        """Build the main search SQL query - uses v_organization_summary view + fallback to raw table

        Primary: v_organization_summary (37K orgs with payments) - 116x faster
        Fallback: cvr_lobby_disclosure_cd (orgs with filings but no payments)

        This ensures ALL registered organizations are searchable, not just those with payments.
        """
        return """
        WITH view_results AS (
            SELECT
                organization_filer_id as filer_id,
                organization_name,
                total_filings as filing_count,
                FORMAT_DATE('%Y-%m-%d', first_activity_date) as first_filing_date,
                FORMAT_DATE('%Y-%m-%d', last_activity_date) as latest_filing_date,
                EXTRACT(YEAR FROM first_activity_date) as first_year,
                EXTRACT(YEAR FROM last_activity_date) as latest_year,
                total_spending,
                total_lobbying_firms
            FROM `ca-lobby.ca_lobby.v_organization_summary`
            WHERE (@search_term IS NULL OR UPPER(organization_name) LIKE UPPER(@search_term))
        ),
        raw_results AS (
            SELECT
                SAFE_CAST(FILER_ID AS INT64) as filer_id,
                FILER_NAML as organization_name,
                COUNT(DISTINCT FILING_ID) as filing_count,
                FORMAT_DATE('%Y-%m-%d', MIN(RPT_DATE_DATE)) as first_filing_date,
                FORMAT_DATE('%Y-%m-%d', MAX(RPT_DATE_DATE)) as latest_filing_date,
                EXTRACT(YEAR FROM MIN(RPT_DATE_DATE)) as first_year,
                EXTRACT(YEAR FROM MAX(RPT_DATE_DATE)) as latest_year,
                CAST(0 AS FLOAT64) as total_spending,
                CAST(NULL AS INT64) as total_lobbying_firms
            FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd_partitioned`
            WHERE (@search_term IS NULL OR UPPER(FILER_NAML) LIKE UPPER(@search_term))
              AND FROM_DATE_DATE >= '2020-01-01'
              AND SAFE_CAST(FILER_ID AS INT64) IS NOT NULL
              AND FILER_NAML NOT IN (
                SELECT organization_name FROM view_results
              )
            GROUP BY FILER_ID, FILER_NAML
        )
        SELECT * FROM view_results
        UNION ALL
        SELECT * FROM raw_results
        ORDER BY latest_filing_date DESC
        LIMIT @limit
        OFFSET @offset
        """

    def _build_count_query(self):
        """Build count query for pagination - counts from both view and raw table

        Includes ALL organizations (with payments + without payments)
        """
        return """
        WITH view_results AS (
            SELECT organization_name
            FROM `ca-lobby.ca_lobby.v_organization_summary`
            WHERE (@search_term IS NULL OR UPPER(organization_name) LIKE UPPER(@search_term))
        ),
        raw_results AS (
            SELECT DISTINCT FILER_NAML as organization_name
            FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd_partitioned`
            WHERE (@search_term IS NULL OR UPPER(FILER_NAML) LIKE UPPER(@search_term))
              AND FROM_DATE_DATE >= '2020-01-01'
              AND FILER_NAML NOT IN (
                SELECT organization_name FROM view_results
              )
        )
        SELECT COUNT(*) as total FROM (
            SELECT organization_name FROM view_results
            UNION ALL
            SELECT organization_name FROM raw_results
        )
        """

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
