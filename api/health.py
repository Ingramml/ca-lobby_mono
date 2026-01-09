"""
Health Check Endpoint
Verifies API is running and BigQuery connection is working
Self-contained file for Vercel serverless deployment
"""

import os
import json
from http.server import BaseHTTPRequestHandler
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

    def test_connection(self):
        """Test BigQuery connection"""
        try:
            query = "SELECT 1 as test"
            query_job = self._client.query(query)
            results = query_job.result()
            for row in results:
                return row['test'] == 1
            return False
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False


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
        "Access-Control-Allow-Origin": "https://ca-lobbymono.vercel.app",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }

    return (
        json.dumps(response, default=str),
        status_code,
        headers
    )


def error_response(message, status_code=500):
    """Create an error JSON response"""
    response = {
        "success": False,
        "error": {
            "type": "ServerError",
            "message": message
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "https://ca-lobbymono.vercel.app",
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
    """Vercel serverless function handler"""

    def do_GET(self):
        """Handle GET request for health check"""
        try:
            # Test BigQuery connection
            client = BigQueryClient()
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
            print(f"ERROR: Health check failed: {str(e)}")
            body, status, headers = error_response(
                message="Health check failed. Please try again.",
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
        self.send_header('Access-Control-Allow-Origin', 'https://ca-lobbymono.vercel.app')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
