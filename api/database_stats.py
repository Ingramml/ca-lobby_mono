"""
Database Statistics Endpoint
Provides comprehensive database statistics for admin dashboard
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
    """Vercel serverless function handler for database statistics"""

    def do_GET(self):
        """Handle GET request for database statistics"""
        try:
            # Get comprehensive database statistics
            stats = self._get_database_statistics()

            # Return success response
            body, status, headers = success_response(stats)

            self.send_response(status)
            for key, value in headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body.encode())

        except Exception as e:
            # Return error response
            body, status, headers = error_response(
                message=f"Database statistics failed: {str(e)}",
                status_code=500,
                error_type="DatabaseStatsError"
            )

            self.send_response(status)
            for key, value in headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body.encode())

    def _get_database_statistics(self):
        """Get comprehensive database statistics"""
        client = BigQueryClient()

        # Get overall summary
        summary_query = """
        SELECT
            COUNT(DISTINCT FILER_ID) as total_organizations,
            COUNT(*) as total_filings,
            MIN(RPT_DATE_DATE) as earliest_filing,
            MAX(RPT_DATE_DATE) as latest_filing,
            COUNT(DISTINCT EXTRACT(YEAR FROM RPT_DATE_DATE)) as years_covered
        FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd`
        WHERE RPT_DATE_DATE IS NOT NULL
          AND RPT_DATE_DATE <= CURRENT_DATE()
          AND EXTRACT(YEAR FROM RPT_DATE_DATE) >= 2000
        """

        # Get payment statistics
        payment_query = """
        SELECT
            COUNT(*) as total_payments,
            SUM(CAST(PER_TOTAL AS FLOAT64)) as total_amount,
            AVG(CAST(PER_TOTAL AS FLOAT64)) as avg_payment
        FROM `ca-lobby.ca_lobby.lpay_cd`
        WHERE PER_TOTAL IS NOT NULL
          AND CAST(PER_TOTAL AS FLOAT64) > 0
        """

        # Get organization view statistics
        org_view_query = """
        SELECT
            COUNT(*) as total_orgs_in_view,
            COUNT(CASE WHEN total_spending > 0 THEN 1 END) as orgs_with_spending,
            SUM(total_spending) as total_spending_all,
            AVG(total_spending) as avg_spending_per_org,
            MAX(total_spending) as max_org_spending,
            SUM(total_payment_line_items) as total_payment_items
        FROM `ca-lobby.ca_lobby.v_organization_summary`
        WHERE organization_name IS NOT NULL
        """

        # Get yearly breakdown
        yearly_query = """
        SELECT
            EXTRACT(YEAR FROM RPT_DATE_DATE) as year,
            COUNT(DISTINCT FILER_ID) as orgs_count,
            COUNT(*) as filings_count
        FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd`
        WHERE RPT_DATE_DATE IS NOT NULL
          AND EXTRACT(YEAR FROM RPT_DATE_DATE) >= 2015
          AND EXTRACT(YEAR FROM RPT_DATE_DATE) <= EXTRACT(YEAR FROM CURRENT_DATE())
        GROUP BY year
        ORDER BY year DESC
        LIMIT 10
        """

        # Get government type breakdown
        govt_type_query = """
        SELECT
            CASE
                WHEN UPPER(organization_name) LIKE '%CITY%'
                     OR UPPER(organization_name) LIKE '%LEAGUE%CITIES%'
                THEN 'city'
                WHEN UPPER(organization_name) LIKE '%COUNTY%'
                     OR UPPER(organization_name) LIKE '%CSAC%'
                THEN 'county'
                ELSE 'other'
            END as govt_type,
            COUNT(*) as org_count,
            SUM(total_spending) as total_spending
        FROM `ca-lobby.ca_lobby.v_organization_summary`
        WHERE organization_name IS NOT NULL
          AND total_spending > 0
        GROUP BY govt_type
        """

        # Get top spending organizations
        top_orgs_query = """
        SELECT
            organization_name,
            CAST(ROUND(total_spending) AS INT64) as total_spending,
            total_payment_line_items,
            EXTRACT(YEAR FROM last_activity_date) as last_active_year
        FROM `ca-lobby.ca_lobby.v_organization_summary`
        WHERE total_spending IS NOT NULL
          AND total_spending > 0
          AND organization_name IS NOT NULL
        ORDER BY total_spending DESC
        LIMIT 10
        """

        # Execute all queries
        summary = client.execute_query(summary_query)[0] if client.execute_query(summary_query) else {}
        payments = client.execute_query(payment_query)[0] if client.execute_query(payment_query) else {}
        org_view = client.execute_query(org_view_query)[0] if client.execute_query(org_view_query) else {}
        yearly = client.execute_query(yearly_query)
        govt_types = client.execute_query(govt_type_query)
        top_orgs = client.execute_query(top_orgs_query)

        # Compile comprehensive statistics
        return {
            "summary": {
                "total_organizations": summary.get('total_organizations', 0),
                "total_filings": summary.get('total_filings', 0),
                "earliest_filing": summary.get('earliest_filing'),
                "latest_filing": summary.get('latest_filing'),
                "years_covered": summary.get('years_covered', 0)
            },
            "payments": {
                "total_payments": payments.get('total_payments', 0),
                "total_amount": payments.get('total_amount', 0),
                "avg_payment": payments.get('avg_payment', 0)
            },
            "organization_view": {
                "total_orgs_in_view": org_view.get('total_orgs_in_view', 0),
                "orgs_with_spending": org_view.get('orgs_with_spending', 0),
                "total_spending_all": org_view.get('total_spending_all', 0),
                "avg_spending_per_org": org_view.get('avg_spending_per_org', 0),
                "max_org_spending": org_view.get('max_org_spending', 0),
                "total_payment_items": org_view.get('total_payment_items', 0)
            },
            "yearly_breakdown": yearly,
            "government_types": govt_types,
            "top_organizations": top_orgs,
            "tables": {
                "cvr_lobby_disclosure_cd": {
                    "description": "Lobbying disclosure filings",
                    "row_count": "~4.3M rows"
                },
                "lpay_cd": {
                    "description": "Payment transactions",
                    "row_count": "~5.6M rows"
                },
                "v_organization_summary": {
                    "description": "Optimized organization summary view",
                    "row_count": f"~{org_view.get('total_orgs_in_view', 0):,} rows",
                    "optimization": "116x faster than raw table queries"
                }
            }
        }

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
