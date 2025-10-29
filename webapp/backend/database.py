"""
Database Connection Module for CA Lobby API

Leverages existing Phase 1.1 BigQuery connection patterns and infrastructure.
Provides connection pooling, error handling, and query optimization for API layer.

Based on:
- Bigquery_connection.py patterns from Phase 1.1
- Existing credential management from .env
- Phase 1.1 error handling and logging patterns
"""

from google.cloud import bigquery
from google.oauth2 import service_account
from google.api_core.exceptions import GoogleAPICallError, NotFound, Forbidden
from dotenv import load_dotenv
import os
import logging
from functools import lru_cache
from datetime import datetime
import time

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """
    Database connection manager using Phase 1.1 established patterns.
    Provides connection pooling, retry logic, and error handling.
    """

    def __init__(self):
        self.client = None
        self.project_id = None
        self.dataset_id = os.getenv('BIGQUERY_DATASET', 'ca_lobby')
        self.use_mock_data = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'

    def initialize_connection(self):
        """
        Initialize BigQuery connection using Phase 1.1 patterns.
        Returns client instance or None if connection fails.
        """
        if self.use_mock_data:
            logger.info("🔧 Using mock data mode - database connection skipped")
            return None

        try:
            # Get credentials path from environment (Phase 1.1 pattern)
            credentials_path = os.getenv('CREDENTIALS_LOCATION')
            if not credentials_path:
                logger.error("❌ CREDENTIALS_LOCATION not set in environment")
                return None

            if not os.path.exists(credentials_path):
                logger.error(f"❌ Credentials file not found: {credentials_path}")
                return None

            # Load credentials using Phase 1.1 pattern
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            self.project_id = credentials.project_id

            # Initialize BigQuery client
            self.client = bigquery.Client(credentials=credentials, project=self.project_id)

            # Test connection by listing datasets (Phase 1.1 validation pattern)
            datasets = list(self.client.list_datasets())
            logger.info(f"✅ Connected to BigQuery project: {self.project_id}")
            logger.info(f"Available datasets: {[dataset.dataset_id for dataset in datasets]}")

            return self.client

        except FileNotFoundError as e:
            logger.error(f"❌ Credentials file not found: {e}")
            return None
        except Forbidden as e:
            logger.error(f"❌ Access forbidden - check credentials permissions: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return None

    def get_client(self):
        """
        Get or create database client with connection retry logic.
        Follows Phase 1.1 error recovery patterns.
        """
        if self.use_mock_data:
            return None

        if self.client is None:
            self.initialize_connection()

        return self.client

    @lru_cache(maxsize=100)
    def execute_query_cached(self, query_string, cache_key=None):
        """
        Execute query with caching for common queries.
        Uses LRU cache to optimize performance for repeated queries.
        """
        return self.execute_query(query_string)

    def execute_query(self, query_string, retry_count=3):
        """
        Execute BigQuery with retry logic and error handling.
        Applies Phase 1.1 error recovery patterns.

        Args:
            query_string (str): SQL query to execute
            retry_count (int): Number of retry attempts

        Returns:
            query results or None if failed
        """
        if self.use_mock_data:
            logger.info("🔧 Mock data mode - returning sample data")
            return self._get_mock_data(query_string)

        client = self.get_client()
        if client is None:
            logger.error("❌ No database client available")
            return None

        for attempt in range(retry_count):
            try:
                # Configure query job with optimization settings
                job_config = bigquery.QueryJobConfig()
                job_config.use_query_cache = True
                job_config.use_legacy_sql = False

                logger.info(f"🔍 Executing query (attempt {attempt + 1}/{retry_count})")
                logger.debug(f"Query: {query_string[:200]}...")

                start_time = time.time()
                query_job = client.query(query_string, job_config=job_config)
                results = query_job.result()
                execution_time = time.time() - start_time

                logger.info(f"✅ Query executed successfully in {execution_time:.2f}s")
                return results

            except GoogleAPICallError as e:
                logger.warning(f"⚠️ BigQuery API error (attempt {attempt + 1}): {e}")
                if attempt == retry_count - 1:
                    logger.error(f"❌ Query failed after {retry_count} attempts: {e}")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff

            except Exception as e:
                logger.error(f"❌ Query execution error: {e}")
                return None

        return None

    def _get_mock_data(self, query_string):
        """
        Provide mock data for testing when USE_MOCK_DATA=true.
        Simulates database responses for development/testing.
        """
        # Analyze query to determine appropriate mock response
        query_lower = query_string.lower()

        if 'lobby' in query_lower and 'search' in query_lower:
            return self._mock_lobby_search_data()
        elif 'health' in query_lower or 'status' in query_lower:
            return self._mock_health_data()
        else:
            return self._mock_generic_data()

    def _mock_lobby_search_data(self):
        """Mock lobby search data for testing."""
        from collections import namedtuple
        Row = namedtuple('Row', ['name', 'amount', 'date', 'client'])

        return [
            Row('Sample Lobbyist 1', 50000, '2024-01-15', 'Tech Company A'),
            Row('Sample Lobbyist 2', 75000, '2024-01-20', 'Healthcare Corp'),
            Row('Sample Lobbyist 3', 30000, '2024-01-25', 'Energy Firm'),
        ]

    def _mock_health_data(self):
        """Mock health/status data for testing."""
        from collections import namedtuple
        Row = namedtuple('Row', ['status', 'timestamp', 'records_count'])

        return [Row('healthy', datetime.utcnow().isoformat(), 12543)]

    def _mock_generic_data(self):
        """Mock generic data for unrecognized queries."""
        from collections import namedtuple
        Row = namedtuple('Row', ['result'])

        return [Row('Mock data response')]

    def health_check(self):
        """
        Perform database health check.
        Returns status information for monitoring purposes.
        """
        if self.use_mock_data:
            return {
                'status': 'mock_mode',
                'connection': 'simulated',
                'timestamp': datetime.utcnow().isoformat()
            }

        try:
            client = self.get_client()
            if client is None:
                return {
                    'status': 'unhealthy',
                    'error': 'No client connection available',
                    'timestamp': datetime.utcnow().isoformat()
                }

            # Simple query to test connection
            query = f"SELECT COUNT(*) as record_count FROM `{self.project_id}.{self.dataset_id}.INFORMATION_SCHEMA.TABLES`"
            result = self.execute_query(query)

            if result:
                return {
                    'status': 'healthy',
                    'connection': 'active',
                    'project_id': self.project_id,
                    'dataset': self.dataset_id,
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': 'Query execution failed',
                    'timestamp': datetime.utcnow().isoformat()
                }

        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

# Global database instance following Phase 1.1 patterns
db = DatabaseConnection()

def get_database():
    """Get the global database instance."""
    return db