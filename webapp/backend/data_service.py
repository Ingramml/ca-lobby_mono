"""
Data Access Service Layer for CA Lobby API

Implements data access patterns using Phase 1.1 established infrastructure.
Provides caching, large dataset handling, and query optimization.

Based on:
- Phase 1.1 file selection and processing patterns (fileselector.py)
- Existing data formatting patterns (Column_rename.py)
- Large dataset processing patterns from Phase 1.1
- Error handling and recovery from existing scripts
"""

import logging
import time
from functools import lru_cache
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional, Any
import json

from database import get_database

logger = logging.getLogger(__name__)

class DataAccessService:
    """
    Data access service layer implementing Phase 1.1 patterns.
    Handles query optimization, caching, and large dataset processing.
    """

    def __init__(self):
        self.db = get_database()
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes default TTL

    def _get_cache_key(self, query: str, params: Dict = None) -> str:
        """Generate cache key from query and parameters."""
        cache_data = {
            'query': query,
            'params': params or {}
        }
        return f"query_cache_{hash(json.dumps(cache_data, sort_keys=True))}"

    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is still valid."""
        if 'timestamp' not in cache_entry:
            return False

        cache_time = cache_entry['timestamp']
        expiry_time = cache_time + timedelta(seconds=self.cache_ttl)
        return datetime.utcnow() < expiry_time

    def _cache_result(self, cache_key: str, data: Any) -> None:
        """Cache query result with timestamp."""
        self.cache[cache_key] = {
            'data': data,
            'timestamp': datetime.utcnow(),
            'hits': 0
        }
        logger.debug(f"Cached result for key: {cache_key[:50]}...")

    def _get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Retrieve cached result if valid."""
        if cache_key not in self.cache:
            return None

        cache_entry = self.cache[cache_key]
        if not self._is_cache_valid(cache_entry):
            del self.cache[cache_key]
            logger.debug(f"Cache expired for key: {cache_key[:50]}...")
            return None

        # Update hit counter
        cache_entry['hits'] += 1
        logger.debug(f"Cache hit for key: {cache_key[:50]}... (hits: {cache_entry['hits']})")
        return cache_entry['data']

    def execute_cached_query(self, query: str, params: Dict = None) -> Optional[List[Dict]]:
        """
        Execute query with caching support.
        Applies Phase 1.1 query optimization patterns.
        """
        cache_key = self._get_cache_key(query, params)

        # Try to get from cache first
        cached_result = self._get_cached_result(cache_key)
        if cached_result is not None:
            logger.info(f"Query served from cache: {len(cached_result)} records")
            return cached_result

        # Execute query if not cached
        start_time = time.time()
        results = self.db.execute_query(query)
        execution_time = time.time() - start_time

        if results is None:
            logger.warning(f"Query returned no results: {query[:100]}...")
            return None

        # Convert results to list of dictionaries for easier handling
        processed_results = self._process_query_results(results)

        # Cache the results
        self._cache_result(cache_key, processed_results)

        logger.info(f"Query executed and cached: {len(processed_results)} records in {execution_time:.3f}s")
        return processed_results

    def _process_query_results(self, results) -> List[Dict]:
        """
        Process query results into standardized format.
        Applies Phase 1.1 data formatting patterns.
        """
        processed_data = []

        for row in results:
            # Handle different row types (BigQuery Row objects vs mock data)
            if hasattr(row, 'items') and callable(row.items):
                # BigQuery Row object
                row_dict = {}
                for key, value in row.items():
                    formatted_key = self._standardize_column_name(key)
                    formatted_value = self._standardize_value(value)
                    row_dict[formatted_key] = formatted_value
            elif hasattr(row, '_fields'):
                # Named tuple (mock data)
                row_dict = {}
                for field in row._fields:
                    value = getattr(row, field)
                    formatted_key = self._standardize_column_name(field)
                    formatted_value = self._standardize_value(value)
                    row_dict[formatted_key] = formatted_value
            else:
                # Dictionary or other formats
                row_dict = dict(row) if not isinstance(row, dict) else row

            processed_data.append(row_dict)

        return processed_data

    def _standardize_column_name(self, column_name: str) -> str:
        """
        Standardize column names following Phase 1.1 patterns.
        Based on Column_rename.py standardization approach.
        """
        # Convert to lowercase and replace spaces/special chars with underscores
        standardized = column_name.lower().replace(' ', '_').replace('-', '_')

        # Remove special characters
        import re
        standardized = re.sub(r'[^\w]', '_', standardized)

        # Remove multiple underscores
        standardized = re.sub(r'_+', '_', standardized).strip('_')

        return standardized

    def _standardize_value(self, value: Any) -> Any:
        """
        Standardize values following Phase 1.1 data processing patterns.
        """
        if value is None:
            return None

        # Handle datetime objects
        if hasattr(value, 'isoformat'):
            return value.isoformat()

        # Handle numeric values
        if isinstance(value, (int, float)):
            return value

        # Handle strings
        if isinstance(value, str):
            return value.strip()

        # Convert other types to string
        return str(value)

    def get_lobby_data(self, filters: Dict = None, limit: int = 1000, offset: int = 0) -> Dict:
        """
        Get lobby data with filtering and pagination.
        Implements Phase 1.1 file selection patterns for efficient querying.
        """
        try:
            # Build query with filters (Phase 1.1 selection pattern)
            query = self._build_lobby_query(filters, limit, offset)

            # Execute cached query
            results = self.execute_cached_query(query, {
                'filters': filters,
                'limit': limit,
                'offset': offset
            })

            if results is None:
                return {
                    'data': [],
                    'total': 0,
                    'page': offset // limit + 1,
                    'per_page': limit,
                    'filters_applied': filters or {}
                }

            # Get total count for pagination
            count_query = self._build_lobby_count_query(filters)
            count_result = self.execute_cached_query(count_query, {'filters': filters})
            total_count = count_result[0]['total'] if count_result else len(results)

            return {
                'data': results,
                'total': total_count,
                'page': offset // limit + 1,
                'per_page': limit,
                'filters_applied': filters or {},
                'cache_info': self._get_cache_stats()
            }

        except Exception as e:
            logger.error(f"Error getting lobby data: {e}")
            raise

    def _build_lobby_query(self, filters: Dict = None, limit: int = 1000, offset: int = 0) -> str:
        """
        Build lobby data query with filters.
        Applies Phase 1.1 data selection patterns.
        """
        # Base query (mock data mode will return sample data)
        base_query = """
        SELECT
            lobbyist_name,
            client_name,
            amount,
            report_date,
            activity_description,
            payment_type
        FROM `{project}.{dataset}.lobby_data`
        """.strip()

        where_clauses = []

        if filters:
            # Apply filters following Phase 1.1 validation patterns
            if 'lobbyist_name' in filters:
                where_clauses.append(f"LOWER(lobbyist_name) LIKE '%{filters['lobbyist_name'].lower()}%'")

            if 'client_name' in filters:
                where_clauses.append(f"LOWER(client_name) LIKE '%{filters['client_name'].lower()}%'")

            if 'amount_min' in filters:
                where_clauses.append(f"amount >= {filters['amount_min']}")

            if 'amount_max' in filters:
                where_clauses.append(f"amount <= {filters['amount_max']}")

            if 'date_from' in filters:
                where_clauses.append(f"report_date >= '{filters['date_from']}'")

            if 'date_to' in filters:
                where_clauses.append(f"report_date <= '{filters['date_to']}'")

        # Add WHERE clause if filters exist
        if where_clauses:
            base_query += " WHERE " + " AND ".join(where_clauses)

        # Add ordering and pagination
        base_query += " ORDER BY report_date DESC, amount DESC"
        base_query += f" LIMIT {limit} OFFSET {offset}"

        return base_query

    def _build_lobby_count_query(self, filters: Dict = None) -> str:
        """Build count query for pagination."""
        base_query = "SELECT COUNT(*) as total FROM `{project}.{dataset}.lobby_data`"

        where_clauses = []
        if filters:
            if 'lobbyist_name' in filters:
                where_clauses.append(f"LOWER(lobbyist_name) LIKE '%{filters['lobbyist_name'].lower()}%'")
            if 'client_name' in filters:
                where_clauses.append(f"LOWER(client_name) LIKE '%{filters['client_name'].lower()}%'")
            if 'amount_min' in filters:
                where_clauses.append(f"amount >= {filters['amount_min']}")
            if 'amount_max' in filters:
                where_clauses.append(f"amount <= {filters['amount_max']}")
            if 'date_from' in filters:
                where_clauses.append(f"report_date >= '{filters['date_from']}'")
            if 'date_to' in filters:
                where_clauses.append(f"report_date <= '{filters['date_to']}'")

        if where_clauses:
            base_query += " WHERE " + " AND ".join(where_clauses)

        return base_query

    def get_cache_stats(self) -> Dict:
        """Get cache performance statistics."""
        return self._get_cache_stats()

    def _get_cache_stats(self) -> Dict:
        """Internal method to get cache statistics."""
        total_entries = len(self.cache)
        total_hits = sum(entry.get('hits', 0) for entry in self.cache.values())

        # Calculate cache effectiveness
        if total_entries > 0:
            avg_hits = total_hits / total_entries
            hit_rate = min(100, (total_hits / max(1, total_hits + total_entries)) * 100)
        else:
            avg_hits = 0
            hit_rate = 0

        return {
            'total_cached_queries': total_entries,
            'total_cache_hits': total_hits,
            'average_hits_per_query': round(avg_hits, 2),
            'cache_hit_rate_percent': round(hit_rate, 2),
            'cache_ttl_seconds': self.cache_ttl
        }

    def clear_cache(self, pattern: str = None) -> Dict:
        """Clear cache entries, optionally matching a pattern."""
        if pattern is None:
            entries_cleared = len(self.cache)
            self.cache.clear()
            logger.info(f"Cleared all cache entries: {entries_cleared}")
        else:
            entries_cleared = 0
            keys_to_remove = [key for key in self.cache.keys() if pattern in key]
            for key in keys_to_remove:
                del self.cache[key]
                entries_cleared += 1
            logger.info(f"Cleared {entries_cleared} cache entries matching pattern: {pattern}")

        return {
            'entries_cleared': entries_cleared,
            'remaining_entries': len(self.cache),
            'timestamp': datetime.utcnow().isoformat()
        }

# Global data service instance
data_service = DataAccessService()

def get_data_service() -> DataAccessService:
    """Get the global data service instance."""
    return data_service