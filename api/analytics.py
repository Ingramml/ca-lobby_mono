"""
Analytics Endpoint
Provides aggregated data for visualizations
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


# ============================================================================
# VERCEL SERVERLESS FUNCTION HANDLER
# ============================================================================

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
            elif analytics_type == 'spending':
                data = self._get_spending_trends()
            elif analytics_type == 'spending_breakdown':
                data = self._get_spending_breakdown()
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
            COUNT(DISTINCT FILER_ID) as total_organizations,
            COUNT(*) as total_filings,
            MAX(RPT_DATE_DATE) as latest_filing
        FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd`
        WHERE RPT_DATE_DATE IS NOT NULL
          AND RPT_DATE_DATE <= CURRENT_DATE()
          AND EXTRACT(YEAR FROM RPT_DATE_DATE) >= 2000
        """

        client = BigQueryClient()
        result = client.execute_query(query)
        return result[0] if result else {}

    def _get_trends_analytics(self):
        """Get filing trends over time"""
        query = """
        SELECT
            EXTRACT(YEAR FROM RPT_DATE_DATE) as year,
            RPT_DATE as period,
            COUNT(*) as filing_count
        FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd`
        WHERE RPT_DATE_DATE IS NOT NULL
          AND RPT_DATE_DATE <= CURRENT_DATE()
          AND EXTRACT(YEAR FROM RPT_DATE_DATE) >= 2020
        GROUP BY year, period
        ORDER BY year DESC, period DESC
        LIMIT 12
        """

        client = BigQueryClient()
        return client.execute_query(query)

    def _get_top_organizations(self):
        """Get top organizations by spending - uses v_organization_summary view

        Migrated from raw cvr_lobby_disclosure_cd to v_organization_summary view.
        Benefits: Queries 37K pre-aggregated rows instead of 4.3M rows with GROUP BY (instant)

        Note: View has many NULL values for organization_filer_id and total_filings,
        but total_spending and organization_name are populated. Sort by spending instead.
        """
        query = """
        SELECT
            CAST(organization_filer_id AS STRING) as filer_id,
            organization_name,
            CAST(ROUND(total_spending) AS INT64) as filing_count
        FROM `ca-lobby.ca_lobby.v_organization_summary`
        WHERE organization_name IS NOT NULL
          AND total_spending IS NOT NULL
          AND total_spending > 0
        ORDER BY total_spending DESC
        LIMIT 10
        """

        client = BigQueryClient()
        return client.execute_query(query)

    def _get_spending_trends(self):
        """Get yearly spending trends by government type"""
        query = """
        WITH yearly_spending AS (
            SELECT
                EXTRACT(YEAR FROM p.RPT_DATE_DATE) as year,
                p.FILER_ID as filer_id,
                CAST(pay.PER_TOTAL AS FLOAT64) as amount,
                CASE
                    WHEN UPPER(p.FIRM_NAME) LIKE '%CITY OF%' THEN 'city'
                    WHEN UPPER(p.FIRM_NAME) LIKE '%COUNTY%' THEN 'county'
                    ELSE 'other'
                END as govt_type
            FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` p
            LEFT JOIN `ca-lobby.ca_lobby.lpay_cd` pay ON p.FILING_ID = pay.FILING_ID
            WHERE p.RPT_DATE_DATE IS NOT NULL
              AND p.RPT_DATE_DATE <= CURRENT_DATE()
              AND EXTRACT(YEAR FROM p.RPT_DATE_DATE) >= 2015
              AND EXTRACT(YEAR FROM p.RPT_DATE_DATE) <= EXTRACT(YEAR FROM CURRENT_DATE())
              AND pay.PER_TOTAL IS NOT NULL
              AND CAST(pay.PER_TOTAL AS FLOAT64) > 0
        )
        SELECT
            year,
            SUM(amount) as total_spending,
            SUM(CASE WHEN govt_type = 'city' THEN amount ELSE 0 END) as city_spending,
            SUM(CASE WHEN govt_type = 'county' THEN amount ELSE 0 END) as county_spending,
            COUNT(DISTINCT CASE WHEN govt_type = 'city' THEN filer_id END) as city_count,
            COUNT(DISTINCT CASE WHEN govt_type = 'county' THEN filer_id END) as county_count
        FROM yearly_spending
        GROUP BY year
        ORDER BY year ASC
        """

        client = BigQueryClient()
        return client.execute_query(query)

    def _get_spending_breakdown(self):
        """Get spending breakdown by government type and category - uses v_organization_summary view

        Migrated from raw lpay_cd + cvr_lobby_disclosure_cd JOIN to v_organization_summary view.
        Benefits: Queries 37K pre-aggregated rows instead of 5.6M + 4.3M JOIN (150x faster)
        Expected performance: 5-8s → 100ms
        """
        query = """
        SELECT
            CASE
                WHEN UPPER(organization_name) LIKE '%LEAGUE%CITIES%'
                     OR UPPER(organization_name) LIKE '%CITY OF%'
                THEN 'city'
                WHEN UPPER(organization_name) LIKE '%COUNTY%'
                     OR UPPER(organization_name) LIKE '%CSAC%'
                     OR UPPER(organization_name) LIKE '%ASSOCIATION OF COUNTIES%'
                THEN 'county'
                ELSE 'other'
            END as govt_type,
            CASE
                WHEN UPPER(organization_name) LIKE '%LEAGUE%'
                     OR UPPER(organization_name) LIKE '%ASSOCIATION%'
                     OR UPPER(organization_name) LIKE '%COALITION%'
                THEN 'membership'
                ELSE 'other_lobbying'
            END as spending_category,
            SUM(total_spending) as total_amount,
            COUNT(DISTINCT organization_name) as filer_count
        FROM `ca-lobby.ca_lobby.v_organization_summary`
        WHERE (
            UPPER(organization_name) LIKE '%CITY%'
            OR UPPER(organization_name) LIKE '%COUNTY%'
            OR UPPER(organization_name) LIKE '%LEAGUE%'
            OR UPPER(organization_name) LIKE '%ASSOCIATION%'
            OR UPPER(organization_name) LIKE '%CSAC%'
        )
        AND total_spending > 0
        GROUP BY govt_type, spending_category
        HAVING total_amount > 0
        ORDER BY govt_type, spending_category
        """

        try:
            client = BigQueryClient()
            result = client.execute_query(query)

            # Return empty array if no results
            if not result:
                return [
                    {'govt_type': 'city', 'spending_category': 'membership', 'total_amount': 0, 'filer_count': 0},
                    {'govt_type': 'city', 'spending_category': 'other_lobbying', 'total_amount': 0, 'filer_count': 0},
                    {'govt_type': 'county', 'spending_category': 'membership', 'total_amount': 0, 'filer_count': 0},
                    {'govt_type': 'county', 'spending_category': 'other_lobbying', 'total_amount': 0, 'filer_count': 0}
                ]
            return result
        except Exception as e:
            import traceback
            traceback.print_exc()
            # Return default structure on error
            return [
                {'govt_type': 'city', 'spending_category': 'membership', 'total_amount': 0, 'filer_count': 0},
                {'govt_type': 'city', 'spending_category': 'other_lobbying', 'total_amount': 0, 'filer_count': 0},
                {'govt_type': 'county', 'spending_category': 'membership', 'total_amount': 0, 'filer_count': 0},
                {'govt_type': 'county', 'spending_category': 'other_lobbying', 'total_amount': 0, 'filer_count': 0}
            ]

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
