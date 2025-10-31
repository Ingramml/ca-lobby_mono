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

            print(f" BigQuery client initialized for project: {project_id}")

        except Exception as e:
            print(f"L Failed to initialize BigQuery client: {e}")
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
            print(f"L Query execution failed: {e}")
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
