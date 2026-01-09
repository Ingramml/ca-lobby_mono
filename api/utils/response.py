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
        "Access-Control-Allow-Origin": "https://ca-lobbymono.vercel.app",
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
        "Access-Control-Allow-Origin": "https://ca-lobbymono.vercel.app",
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
