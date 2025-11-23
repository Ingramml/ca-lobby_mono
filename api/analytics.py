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
            elif analytics_type == 'org_spending_by_govt':
                data = self._get_org_spending_by_govt()
            elif analytics_type == 'top_city_recipients':
                data = self._get_top_city_recipients()
            elif analytics_type == 'top_county_recipients':
                data = self._get_top_county_recipients()
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
        """Get summary statistics

        FIXED: Now filters to latest amendments only to avoid counting amendments
        as separate filings. Uses ROW_NUMBER() window function for deduplication.
        """
        query = """
        WITH latest_filings AS (
            SELECT
                FILER_ID,
                FILING_ID,
                RPT_DATE_DATE,
                ROW_NUMBER() OVER (PARTITION BY FILING_ID ORDER BY AMEND_ID DESC) as rn
            FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd`
            WHERE RPT_DATE_DATE IS NOT NULL
              AND RPT_DATE_DATE <= CURRENT_DATE()
              AND EXTRACT(YEAR FROM RPT_DATE_DATE) >= 2000
        )
        SELECT
            COUNT(DISTINCT FILER_ID) as total_organizations,
            COUNT(*) as total_filings,
            MAX(RPT_DATE_DATE) as latest_filing
        FROM latest_filings
        WHERE rn = 1
        """

        client = BigQueryClient()
        result = client.execute_query(query)
        return result[0] if result else {}

    def _get_trends_analytics(self):
        """Get filing trends over time

        FIXED: Now filters to latest amendments only to avoid counting amendments
        as separate filings. Uses ROW_NUMBER() window function for deduplication.
        """
        query = """
        WITH latest_filings AS (
            SELECT
                RPT_DATE_DATE,
                RPT_DATE,
                ROW_NUMBER() OVER (PARTITION BY FILING_ID ORDER BY AMEND_ID DESC) as rn
            FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd`
            WHERE RPT_DATE_DATE IS NOT NULL
              AND RPT_DATE_DATE <= CURRENT_DATE()
              AND EXTRACT(YEAR FROM RPT_DATE_DATE) >= 2020
        )
        SELECT
            EXTRACT(YEAR FROM RPT_DATE_DATE) as year,
            RPT_DATE as period,
            COUNT(*) as filing_count
        FROM latest_filings
        WHERE rn = 1
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

        FIXED: Renamed field from misleading 'filing_count' to accurate 'total_spending'

        Note: View has many NULL values for organization_filer_id and total_filings,
        but total_spending and organization_name are populated. Sort by spending instead.
        """
        query = """
        SELECT
            CAST(organization_filer_id AS STRING) as filer_id,
            organization_name,
            CAST(ROUND(total_spending) AS INT64) as total_spending
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
        """Get yearly spending trends by government type

        FIXED: Now correctly uses EMPLR_NAML (who paid) instead of FIRM_NAME (lobbying firm)
        and filters to latest amendments only to avoid double-counting.
        """
        query = """
        WITH yearly_spending AS (
            SELECT
                EXTRACT(YEAR FROM p.RPT_DATE_DATE) as year,
                pay.EMPLR_ID as filer_id,
                CAST(pay.PER_TOTAL AS FLOAT64) as amount,
                CASE
                    WHEN UPPER(pay.EMPLR_NAML) LIKE '%CITY OF%'
                         OR UPPER(pay.EMPLR_NAML) LIKE '%LEAGUE%CITIES%'
                    THEN 'city'
                    WHEN UPPER(pay.EMPLR_NAML) LIKE '%COUNTY%'
                         OR UPPER(pay.EMPLR_NAML) LIKE '%CSAC%'
                         OR UPPER(pay.EMPLR_NAML) LIKE '%ASSOCIATION OF COUNTIES%'
                    THEN 'county'
                    ELSE 'other'
                END as govt_type
            FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` p
            INNER JOIN `ca-lobby.ca_lobby.lpay_cd` pay
                ON p.FILING_ID = pay.FILING_ID
                AND p.AMEND_ID = pay.AMEND_ID
            WHERE p.RPT_DATE_DATE IS NOT NULL
              AND p.RPT_DATE_DATE <= CURRENT_DATE()
              AND EXTRACT(YEAR FROM p.RPT_DATE_DATE) >= 2015
              AND EXTRACT(YEAR FROM p.RPT_DATE_DATE) <= EXTRACT(YEAR FROM CURRENT_DATE())
              AND pay.PER_TOTAL IS NOT NULL
              AND CAST(pay.PER_TOTAL AS FLOAT64) > 0
              AND (p.FILING_ID, p.AMEND_ID) IN (
                  SELECT FILING_ID, MAX(AMEND_ID)
                  FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd`
                  GROUP BY FILING_ID
              )
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
        """Get spending breakdown by government type and category for 2025 only

        FIXED: Now correctly uses EMPLR_NAML (who paid) instead of FIRM_NAME (lobbying firm)
        and filters to latest amendments only to avoid double-counting.
        """
        query = """
        WITH spending_2025 AS (
            SELECT
                pay.EMPLR_NAML as employer_name,
                pay.EMPLR_ID as filer_id,
                CAST(pay.PER_TOTAL AS FLOAT64) as amount
            FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` p
            INNER JOIN `ca-lobby.ca_lobby.lpay_cd` pay
                ON p.FILING_ID = pay.FILING_ID
                AND p.AMEND_ID = pay.AMEND_ID
            WHERE p.RPT_DATE_DATE IS NOT NULL
              AND EXTRACT(YEAR FROM p.RPT_DATE_DATE) = 2025
              AND pay.PER_TOTAL IS NOT NULL
              AND CAST(pay.PER_TOTAL AS FLOAT64) > 0
              AND (p.FILING_ID, p.AMEND_ID) IN (
                  SELECT FILING_ID, MAX(AMEND_ID)
                  FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd`
                  GROUP BY FILING_ID
              )
              AND (
                UPPER(pay.EMPLR_NAML) LIKE '%CITY%'
                OR UPPER(pay.EMPLR_NAML) LIKE '%COUNTY%'
                OR UPPER(pay.EMPLR_NAML) LIKE '%LEAGUE%'
                OR UPPER(pay.EMPLR_NAML) LIKE '%ASSOCIATION%'
                OR UPPER(pay.EMPLR_NAML) LIKE '%CSAC%'
              )
        )
        SELECT
            CASE
                WHEN UPPER(employer_name) LIKE '%LEAGUE%CITIES%'
                     OR UPPER(employer_name) LIKE '%CITY OF%'
                THEN 'city'
                WHEN UPPER(employer_name) LIKE '%COUNTY%'
                     OR UPPER(employer_name) LIKE '%CSAC%'
                     OR UPPER(employer_name) LIKE '%ASSOCIATION OF COUNTIES%'
                THEN 'county'
                ELSE 'other'
            END as govt_type,
            CASE
                WHEN UPPER(employer_name) LIKE '%LEAGUE%'
                     OR UPPER(employer_name) LIKE '%ASSOCIATION%'
                     OR UPPER(employer_name) LIKE '%COALITION%'
                THEN 'membership'
                ELSE 'other_lobbying'
            END as spending_category,
            SUM(amount) as total_amount,
            COUNT(DISTINCT filer_id) as filer_count
        FROM spending_2025
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

    def _get_org_spending_by_govt(self):
        """Get top 10 lobbying firms by payments from city vs county entities

        FIXED: Now correctly shows lobbying firms (PAYEE_NAML) and classifies by
        employer type (EMPLR_NAML). Filters to latest amendments only.

        Returns lobbying firms that received payments from city or county entities,
        with separate amounts for city and county spending per firm.
        Used for stacked bar chart visualization.
        """
        query = """
        WITH org_spending AS (
            SELECT
                pay.PAYEE_NAML as organization_name,
                CASE
                    WHEN UPPER(pay.EMPLR_NAML) LIKE '%CITY OF%'
                         OR UPPER(pay.EMPLR_NAML) LIKE '%LEAGUE%CITIES%'
                    THEN 'city'
                    WHEN UPPER(pay.EMPLR_NAML) LIKE '%COUNTY%'
                         OR UPPER(pay.EMPLR_NAML) LIKE '%CSAC%'
                         OR UPPER(pay.EMPLR_NAML) LIKE '%ASSOCIATION OF COUNTIES%'
                    THEN 'county'
                    ELSE 'other'
                END as govt_type,
                CAST(pay.PER_TOTAL AS FLOAT64) as amount
            FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` p
            INNER JOIN `ca-lobby.ca_lobby.lpay_cd` pay
                ON p.FILING_ID = pay.FILING_ID
                AND p.AMEND_ID = pay.AMEND_ID
            WHERE p.RPT_DATE_DATE IS NOT NULL
              AND EXTRACT(YEAR FROM p.RPT_DATE_DATE) = 2025
              AND pay.PER_TOTAL IS NOT NULL
              AND CAST(pay.PER_TOTAL AS FLOAT64) > 0
              AND (p.FILING_ID, p.AMEND_ID) IN (
                  SELECT FILING_ID, MAX(AMEND_ID)
                  FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd`
                  GROUP BY FILING_ID
              )
              AND (
                UPPER(pay.EMPLR_NAML) LIKE '%CITY%'
                OR UPPER(pay.EMPLR_NAML) LIKE '%COUNTY%'
                OR UPPER(pay.EMPLR_NAML) LIKE '%LEAGUE%'
                OR UPPER(pay.EMPLR_NAML) LIKE '%ASSOCIATION%'
                OR UPPER(pay.EMPLR_NAML) LIKE '%CSAC%'
              )
        ),
        aggregated AS (
            SELECT
                organization_name,
                SUM(CASE WHEN govt_type = 'city' THEN amount ELSE 0 END) as city_spending,
                SUM(CASE WHEN govt_type = 'county' THEN amount ELSE 0 END) as county_spending,
                SUM(amount) as total_spending
            FROM org_spending
            WHERE govt_type IN ('city', 'county')
            GROUP BY organization_name
            HAVING total_spending > 0
        )
        SELECT
            organization_name,
            CAST(ROUND(city_spending) AS INT64) as city_spending,
            CAST(ROUND(county_spending) AS INT64) as county_spending,
            CAST(ROUND(total_spending) AS INT64) as total_spending
        FROM aggregated
        ORDER BY total_spending DESC
        LIMIT 10
        """

        try:
            client = BigQueryClient()
            result = client.execute_query(query)
            return result if result else []
        except Exception as e:
            import traceback
            traceback.print_exc()
            return []

    def _get_top_city_recipients(self):
        """Get top 10 individuals/firms paid by cities for lobbying activities

        Uses LPAY_CD table where:
        - EMPLR_NAML = The city/county (employer/client)
        - PAYEE_NAML = The lobbying firm who received payment
        - PER_TOTAL = Payment amount

        This correctly tracks WHO got paid BY cities for lobbying services.
        Uses most recent 3 years of data to ensure results.
        """
        query = """
        WITH city_payments AS (
            SELECT
                d.FILING_ID,
                d.RPT_DATE_DATE,
                pay.PAYEE_NAML as recipient_name,
                CAST(pay.PER_TOTAL AS FLOAT64) as amount
            FROM `ca-lobby.ca_lobby.lpay_cd` pay
            JOIN `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` d
                ON pay.FILING_ID = d.FILING_ID
                AND pay.AMEND_ID = d.AMEND_ID
            WHERE pay.PAYEE_NAML IS NOT NULL
              AND pay.PAYEE_NAML != ''
              AND pay.PER_TOTAL IS NOT NULL
              AND CAST(pay.PER_TOTAL AS FLOAT64) > 0
              AND d.RPT_DATE_DATE IS NOT NULL
              AND EXTRACT(YEAR FROM d.RPT_DATE_DATE) >= EXTRACT(YEAR FROM CURRENT_DATE()) - 2
              AND (
                UPPER(pay.EMPLR_NAML) LIKE '%CITY OF%'
                OR UPPER(pay.EMPLR_NAML) LIKE '%LEAGUE%CITIES%'
              )
        )
        SELECT
            recipient_name,
            CAST(ROUND(SUM(amount)) AS INT64) as total_amount
        FROM city_payments
        GROUP BY recipient_name
        HAVING total_amount > 0
        ORDER BY total_amount DESC
        LIMIT 10
        """

        try:
            client = BigQueryClient()
            result = client.execute_query(query)
            return result if result else []
        except Exception as e:
            import traceback
            traceback.print_exc()
            return []

    def _get_top_county_recipients(self):
        """Get top 10 individuals/firms paid by counties for lobbying activities

        Uses LPAY_CD table where:
        - EMPLR_NAML = The county (employer/client)
        - PAYEE_NAML = The lobbying firm who received payment
        - PER_TOTAL = Payment amount

        This correctly tracks WHO got paid BY counties for lobbying services.
        Uses most recent 3 years of data to ensure results.
        """
        query = """
        WITH county_payments AS (
            SELECT
                d.FILING_ID,
                d.RPT_DATE_DATE,
                pay.PAYEE_NAML as recipient_name,
                CAST(pay.PER_TOTAL AS FLOAT64) as amount
            FROM `ca-lobby.ca_lobby.lpay_cd` pay
            JOIN `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` d
                ON pay.FILING_ID = d.FILING_ID
                AND pay.AMEND_ID = d.AMEND_ID
            WHERE pay.PAYEE_NAML IS NOT NULL
              AND pay.PAYEE_NAML != ''
              AND pay.PER_TOTAL IS NOT NULL
              AND CAST(pay.PER_TOTAL AS FLOAT64) > 0
              AND d.RPT_DATE_DATE IS NOT NULL
              AND EXTRACT(YEAR FROM d.RPT_DATE_DATE) >= EXTRACT(YEAR FROM CURRENT_DATE()) - 2
              AND (
                UPPER(pay.EMPLR_NAML) LIKE '%COUNTY%'
                OR UPPER(pay.EMPLR_NAML) LIKE '%CSAC%'
                OR UPPER(pay.EMPLR_NAML) LIKE '%ASSOCIATION OF COUNTIES%'
              )
        )
        SELECT
            recipient_name,
            CAST(ROUND(SUM(amount)) AS INT64) as total_amount
        FROM county_payments
        GROUP BY recipient_name
        HAVING total_amount > 0
        ORDER BY total_amount DESC
        LIMIT 10
        """

        try:
            client = BigQueryClient()
            result = client.execute_query(query)
            return result if result else []
        except Exception as e:
            import traceback
            traceback.print_exc()
            return []

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
