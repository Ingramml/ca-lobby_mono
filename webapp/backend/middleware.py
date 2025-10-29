"""
Middleware for CA Lobby API

Provides error handling, request logging, and security middleware
following Phase 1.1 established patterns for error management.

Based on:
- Phase 1.1 error handling patterns from data processing scripts
- Existing logging patterns and error recovery strategies
- Security practices from Phase 1.1 infrastructure
"""

from flask import jsonify, request, g
from functools import wraps
import logging
import time
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """
    Register global error handlers following Phase 1.1 error patterns.
    Provides consistent error responses across all API endpoints.
    """

    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle bad request errors with proper logging."""
        logger.warning(f"Bad request: {error} from {request.remote_addr}")
        return jsonify({
            'error': 'Bad Request',
            'message': 'The request could not be understood by the server',
            'status_code': 400,
            'timestamp': datetime.utcnow().isoformat()
        }), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        """Handle authentication errors."""
        logger.warning(f"Unauthorized access attempt from {request.remote_addr}")
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required to access this resource',
            'status_code': 401,
            'timestamp': datetime.utcnow().isoformat()
        }), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle authorization errors."""
        logger.warning(f"Forbidden access attempt from {request.remote_addr}")
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource',
            'status_code': 403,
            'timestamp': datetime.utcnow().isoformat()
        }), 403

    @app.errorhandler(404)
    def not_found_error(error):
        """Handle not found errors."""
        logger.info(f"404 error: {request.url} from {request.remote_addr}")
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource could not be found',
            'status_code': 404,
            'timestamp': datetime.utcnow().isoformat()
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        """
        Handle internal server errors with detailed logging.
        Follows Phase 1.1 error logging patterns.
        """
        error_id = f"error_{int(time.time())}"
        logger.error(f"Internal server error [{error_id}]: {error}")
        logger.error(f"Traceback: {traceback.format_exc()}")

        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'error_id': error_id,
            'status_code': 500,
            'timestamp': datetime.utcnow().isoformat()
        }), 500

    logger.info("✅ Error handlers registered")

def register_request_middleware(app):
    """
    Register request middleware for logging and monitoring.
    Follows Phase 1.1 logging patterns for request tracking.
    """

    @app.before_request
    def log_request():
        """Log incoming requests with timing information."""
        g.start_time = time.time()
        g.request_id = f"req_{int(time.time() * 1000)}"

        logger.info(f"[{g.request_id}] {request.method} {request.url} from {request.remote_addr}")

        # Log request headers in debug mode
        if app.config.get('DEBUG'):
            logger.debug(f"[{g.request_id}] Headers: {dict(request.headers)}")

    @app.after_request
    def log_response(response):
        """Log response information and timing."""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            logger.info(f"[{g.request_id}] Response: {response.status_code} ({duration:.3f}s)")

        # Add request ID to response headers for debugging
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id

        return response

    logger.info("✅ Request middleware registered")

def handle_api_errors(f):
    """
    Decorator for API endpoint error handling.
    Provides consistent error responses following Phase 1.1 patterns.

    Usage:
        @handle_api_errors
        def my_endpoint():
            # endpoint code
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)

        except ValueError as e:
            logger.warning(f"Validation error in {f.__name__}: {e}")
            return jsonify({
                'error': 'Validation Error',
                'message': str(e),
                'status_code': 400,
                'timestamp': datetime.utcnow().isoformat()
            }), 400

        except KeyError as e:
            logger.warning(f"Missing required field in {f.__name__}: {e}")
            return jsonify({
                'error': 'Missing Required Field',
                'message': f'Required field {e} is missing',
                'status_code': 400,
                'timestamp': datetime.utcnow().isoformat()
            }), 400

        except Exception as e:
            error_id = f"error_{int(time.time())}"
            logger.error(f"Unexpected error in {f.__name__} [{error_id}]: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")

            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred',
                'error_id': error_id,
                'status_code': 500,
                'timestamp': datetime.utcnow().isoformat()
            }), 500

    return decorated_function

def validate_json_request(required_fields=None):
    """
    Decorator for validating JSON request data.
    Follows Phase 1.1 validation patterns.

    Args:
        required_fields (list): List of required field names

    Usage:
        @validate_json_request(['name', 'email'])
        def create_user():
            # endpoint code
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                logger.warning(f"Non-JSON request to {f.__name__}")
                return jsonify({
                    'error': 'Invalid Content Type',
                    'message': 'Content-Type must be application/json',
                    'status_code': 400,
                    'timestamp': datetime.utcnow().isoformat()
                }), 400

            data = request.get_json()
            if not data:
                logger.warning(f"Empty JSON request to {f.__name__}")
                return jsonify({
                    'error': 'Invalid JSON',
                    'message': 'Request body must contain valid JSON',
                    'status_code': 400,
                    'timestamp': datetime.utcnow().isoformat()
                }), 400

            # Check required fields
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    logger.warning(f"Missing fields in {f.__name__}: {missing_fields}")
                    return jsonify({
                        'error': 'Missing Required Fields',
                        'message': f'Required fields are missing: {", ".join(missing_fields)}',
                        'missing_fields': missing_fields,
                        'status_code': 400,
                        'timestamp': datetime.utcnow().isoformat()
                    }), 400

            return f(*args, **kwargs)

        return decorated_function
    return decorator

def setup_middleware(app):
    """
    Set up all middleware for the Flask application.
    Consolidates middleware registration following Phase 1.1 patterns.
    """
    logger.info("🔧 Setting up API middleware...")

    # Register error handlers
    register_error_handlers(app)

    # Register request middleware
    register_request_middleware(app)

    logger.info("✅ All middleware configured successfully")

    return app