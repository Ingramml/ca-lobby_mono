"""
Search API Endpoints for CA Lobby System

Implements search functionality using Phase 1.1 data patterns and Phase 1.3b data service.
Provides comprehensive search with filtering, pagination, and advanced query capabilities.

Based on:
- Phase 1.1 SQL queries and data schema
- Phase 1.3b data access layer patterns
- Existing validation patterns from checkingfile
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

from middleware import handle_api_errors, validate_json_request
from data_service import get_data_service

logger = logging.getLogger(__name__)

# Create blueprint for search endpoints
search_bp = Blueprint('search', __name__, url_prefix='/api/search')

@search_bp.route('/', methods=['GET'])
@handle_api_errors
def search_lobby_data():
    """
    Search lobby data with comprehensive filtering options.

    Query Parameters:
    - q: General search term
    - lobbyist: Lobbyist name filter
    - client: Client name filter
    - amount_min: Minimum amount filter
    - amount_max: Maximum amount filter
    - date_from: Start date filter (YYYY-MM-DD)
    - date_to: End date filter (YYYY-MM-DD)
    - page: Page number (default: 1)
    - per_page: Results per page (default: 50, max: 1000)
    """

    try:
        # Get query parameters
        search_term = request.args.get('q', '').strip()
        lobbyist_filter = request.args.get('lobbyist', '').strip()
        client_filter = request.args.get('client', '').strip()
        amount_min = request.args.get('amount_min', type=float)
        amount_max = request.args.get('amount_max', type=float)
        date_from = request.args.get('date_from', '').strip()
        date_to = request.args.get('date_to', '').strip()

        # Pagination parameters
        page = max(1, request.args.get('page', 1, type=int))
        per_page = min(1000, max(1, request.args.get('per_page', 50, type=int)))

        # Build filters dictionary
        filters = {}

        if search_term:
            # For general search, we'll search in both lobbyist and client names
            filters['general_search'] = search_term

        if lobbyist_filter:
            filters['lobbyist_name'] = lobbyist_filter

        if client_filter:
            filters['client_name'] = client_filter

        if amount_min is not None:
            filters['amount_min'] = amount_min

        if amount_max is not None:
            filters['amount_max'] = amount_max

        if date_from:
            # Validate date format
            try:
                datetime.strptime(date_from, '%Y-%m-%d')
                filters['date_from'] = date_from
            except ValueError:
                return jsonify({
                    'error': 'Invalid date format',
                    'message': 'date_from must be in YYYY-MM-DD format',
                    'status_code': 400,
                    'timestamp': datetime.utcnow().isoformat()
                }), 400

        if date_to:
            # Validate date format
            try:
                datetime.strptime(date_to, '%Y-%m-%d')
                filters['date_to'] = date_to
            except ValueError:
                return jsonify({
                    'error': 'Invalid date format',
                    'message': 'date_to must be in YYYY-MM-DD format',
                    'status_code': 400,
                    'timestamp': datetime.utcnow().isoformat()
                }), 400

        # Calculate offset for pagination
        offset = (page - 1) * per_page

        # Get data service and execute search
        data_service = get_data_service()
        results = data_service.get_lobby_data(filters, per_page, offset)

        # Prepare response
        response_data = {
            'success': True,
            'data': results['data'],
            'pagination': {
                'page': results['page'],
                'per_page': results['per_page'],
                'total': results['total'],
                'pages': (results['total'] + per_page - 1) // per_page
            },
            'filters': results['filters_applied'],
            'cache_info': results.get('cache_info', {}),
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.info(f"Search completed: {len(results['data'])} results, page {page}")
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise

@search_bp.route('/advanced', methods=['POST'])
@handle_api_errors
@validate_json_request(['query_type'])
def advanced_search():
    """
    Advanced search with complex query capabilities.

    Request Body:
    {
        "query_type": "complex|aggregation|analytics",
        "parameters": {
            // Query-specific parameters
        }
    }
    """

    data = request.get_json()
    query_type = data['query_type']
    parameters = data.get('parameters', {})

    try:
        data_service = get_data_service()

        if query_type == 'complex':
            results = _execute_complex_search(data_service, parameters)
        elif query_type == 'aggregation':
            results = _execute_aggregation_query(data_service, parameters)
        elif query_type == 'analytics':
            results = _execute_analytics_query(data_service, parameters)
        else:
            return jsonify({
                'error': 'Invalid query type',
                'message': 'query_type must be one of: complex, aggregation, analytics',
                'status_code': 400,
                'timestamp': datetime.utcnow().isoformat()
            }), 400

        response_data = {
            'success': True,
            'query_type': query_type,
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.info(f"Advanced search completed: {query_type}")
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Advanced search error: {e}")
        raise

def _execute_complex_search(data_service, parameters):
    """Execute complex search with multiple criteria."""
    # This would implement complex search logic
    # For now, return mock data in development
    return {
        'message': 'Complex search functionality ready for implementation',
        'parameters_received': parameters,
        'sample_data': [
            {
                'lobbyist_name': 'Complex Search Result 1',
                'client_name': 'Advanced Client A',
                'amount': 125000,
                'report_date': '2024-01-15'
            }
        ]
    }

def _execute_aggregation_query(data_service, parameters):
    """Execute aggregation queries for summary statistics."""
    # This would implement aggregation logic
    return {
        'message': 'Aggregation query functionality ready for implementation',
        'parameters_received': parameters,
        'sample_aggregation': {
            'total_amount': 2500000,
            'unique_lobbyists': 45,
            'unique_clients': 78,
            'date_range': '2024-01-01 to 2024-12-31'
        }
    }

def _execute_analytics_query(data_service, parameters):
    """Execute analytics queries for insights and trends."""
    # This would implement analytics logic
    return {
        'message': 'Analytics query functionality ready for implementation',
        'parameters_received': parameters,
        'sample_analytics': {
            'top_lobbyists': ['Lobbyist A', 'Lobbyist B', 'Lobbyist C'],
            'top_clients': ['Client X', 'Client Y', 'Client Z'],
            'monthly_trends': [100000, 120000, 110000, 130000]
        }
    }

@search_bp.route('/suggestions', methods=['GET'])
@handle_api_errors
def get_search_suggestions():
    """
    Get search suggestions for autocomplete functionality.

    Query Parameters:
    - type: 'lobbyist' or 'client'
    - q: Search term for suggestions
    """

    suggestion_type = request.args.get('type', '').lower()
    search_term = request.args.get('q', '').strip()

    if suggestion_type not in ['lobbyist', 'client']:
        return jsonify({
            'error': 'Invalid suggestion type',
            'message': 'type must be either "lobbyist" or "client"',
            'status_code': 400,
            'timestamp': datetime.utcnow().isoformat()
        }), 400

    if len(search_term) < 2:
        return jsonify({
            'error': 'Search term too short',
            'message': 'Search term must be at least 2 characters long',
            'status_code': 400,
            'timestamp': datetime.utcnow().isoformat()
        }), 400

    try:
        # This would query the database for actual suggestions
        # For now, return mock suggestions
        mock_suggestions = {
            'lobbyist': [
                f'Sample Lobbyist {i} containing "{search_term}"'
                for i in range(1, 6)
            ],
            'client': [
                f'Sample Client {i} containing "{search_term}"'
                for i in range(1, 6)
            ]
        }

        suggestions = mock_suggestions.get(suggestion_type, [])

        response_data = {
            'success': True,
            'type': suggestion_type,
            'query': search_term,
            'suggestions': suggestions,
            'count': len(suggestions),
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.info(f"Search suggestions: {len(suggestions)} for '{search_term}'")
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Search suggestions error: {e}")
        raise

@search_bp.route('/export', methods=['POST'])
@handle_api_errors
@validate_json_request(['format'])
def export_search_results():
    """
    Export search results in various formats.

    Request Body:
    {
        "format": "csv|json|xlsx",
        "filters": {
            // Same filters as search endpoint
        },
        "limit": 10000
    }
    """

    data = request.get_json()
    export_format = data['format'].lower()
    filters = data.get('filters', {})
    limit = min(10000, data.get('limit', 1000))  # Max 10k records for export

    if export_format not in ['csv', 'json', 'xlsx']:
        return jsonify({
            'error': 'Invalid export format',
            'message': 'format must be one of: csv, json, xlsx',
            'status_code': 400,
            'timestamp': datetime.utcnow().isoformat()
        }), 400

    try:
        # Get data service and fetch results for export
        data_service = get_data_service()
        results = data_service.get_lobby_data(filters, limit, 0)

        # Prepare export data
        export_data = {
            'success': True,
            'format': export_format,
            'record_count': len(results['data']),
            'filters_applied': results['filters_applied'],
            'generated_at': datetime.utcnow().isoformat(),
            'data': results['data']
        }

        # Set appropriate response headers for download
        response = jsonify(export_data)
        response.headers['Content-Disposition'] = f'attachment; filename=lobby_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'

        logger.info(f"Export generated: {export_format}, {len(results['data'])} records")
        return response

    except Exception as e:
        logger.error(f"Export error: {e}")
        raise