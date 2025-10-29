"""
Authentication Integration for CA Lobby API

Implements Clerk authentication integration using Phase 1.1 established patterns.
Provides JWT token validation, role-based access control, and session management.

Based on:
- Phase 1.1 Clerk documentation patterns and lessons learned
- Existing web integration guidance from Phase 1.1
- Authentication best practices from Phase 1.1 infrastructure
"""

import os
import jwt
import requests
import logging
from functools import wraps
from flask import request, jsonify, current_app, g
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class ClerkAuth:
    """
    Clerk authentication integration following Phase 1.1 patterns.
    Handles JWT validation, user management, and role-based access control.
    """

    def __init__(self):
        self.clerk_secret_key = os.getenv('CLERK_SECRET_KEY')
        self.clerk_publishable_key = os.getenv('CLERK_PUBLISHABLE_KEY')
        self.clerk_jwt_key = os.getenv('CLERK_JWT_KEY')

        if not self.clerk_secret_key:
            logger.warning("CLERK_SECRET_KEY not configured - authentication will be in mock mode")
            self.mock_mode = True
        else:
            self.mock_mode = False
            logger.info("✅ Clerk authentication configured")

    def verify_token(self, token: str) -> dict:
        """
        Verify JWT token from Clerk.
        Returns user information if valid, raises exception if invalid.
        """
        if self.mock_mode:
            return self._mock_user_verification(token)

        try:
            # Get Clerk's public key for JWT verification
            clerk_jwks_url = "https://api.clerk.dev/v1/jwks"
            response = requests.get(clerk_jwks_url, timeout=5)
            response.raise_for_status()
            jwks = response.json()

            # Decode the JWT token
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get('kid')

            # Find the right key
            rsa_key = None
            for key in jwks['keys']:
                if key['kid'] == kid:
                    rsa_key = {
                        'kty': key['kty'],
                        'kid': key['kid'],
                        'use': key['use'],
                        'n': key['n'],
                        'e': key['e']
                    }
                    break

            if not rsa_key:
                raise ValueError("Unable to find appropriate key")

            # Verify the token
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=['RS256'],
                audience=self.clerk_publishable_key,
                options={"verify_signature": True}
            )

            return {
                'user_id': payload.get('sub'),
                'email': payload.get('email'),
                'username': payload.get('username'),
                'first_name': payload.get('given_name'),
                'last_name': payload.get('family_name'),
                'roles': payload.get('roles', []),
                'permissions': payload.get('permissions', []),
                'session_id': payload.get('sid'),
                'exp': payload.get('exp'),
                'iat': payload.get('iat')
            }

        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {str(e)}")
        except requests.RequestException as e:
            logger.error(f"Error fetching Clerk JWKS: {e}")
            raise ValueError("Authentication service unavailable")
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise ValueError("Token verification failed")

    def _mock_user_verification(self, token: str) -> dict:
        """
        Mock user verification for development/testing.
        Follows Phase 1.1 testing patterns.
        """
        # Simple mock token validation
        if token.startswith('mock_'):
            user_type = token.split('_')[1] if len(token.split('_')) > 1 else 'user'

            mock_users = {
                'admin': {
                    'user_id': 'mock_admin_001',
                    'email': 'admin@example.com',
                    'username': 'admin',
                    'first_name': 'Admin',
                    'last_name': 'User',
                    'roles': ['admin', 'user'],
                    'permissions': ['read', 'write', 'delete', 'admin']
                },
                'user': {
                    'user_id': 'mock_user_001',
                    'email': 'user@example.com',
                    'username': 'testuser',
                    'first_name': 'Test',
                    'last_name': 'User',
                    'roles': ['user'],
                    'permissions': ['read']
                }
            }

            user_data = mock_users.get(user_type, mock_users['user'])
            user_data.update({
                'session_id': f'mock_session_{int(time.time())}',
                'exp': int(time.time()) + 3600,  # 1 hour from now
                'iat': int(time.time())
            })

            logger.info(f"🔧 Mock authentication: {user_type} user")
            return user_data

        raise ValueError("Invalid mock token format")

    def get_user_by_id(self, user_id: str) -> dict:
        """
        Get user information by ID from Clerk.
        """
        if self.mock_mode:
            return {
                'id': user_id,
                'email': 'mock@example.com',
                'username': 'mockuser',
                'first_name': 'Mock',
                'last_name': 'User',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }

        try:
            headers = {
                'Authorization': f'Bearer {self.clerk_secret_key}',
                'Content-Type': 'application/json'
            }

            response = requests.get(
                f'https://api.clerk.dev/v1/users/{user_id}',
                headers=headers,
                timeout=5
            )
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"Error fetching user {user_id}: {e}")
            raise ValueError("Failed to fetch user information")

# Global auth instance
clerk_auth = ClerkAuth()

def require_auth(required_permissions=None):
    """
    Decorator to require authentication for endpoints.

    Args:
        required_permissions: List of required permissions (optional)

    Usage:
        @require_auth()
        def protected_endpoint():
            # Access user via g.current_user

        @require_auth(['read', 'write'])
        def admin_endpoint():
            # Access user via g.current_user
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Get token from Authorization header
                auth_header = request.headers.get('Authorization', '')

                if not auth_header:
                    return jsonify({
                        'error': 'Missing Authorization Header',
                        'message': 'Authorization header is required',
                        'status_code': 401,
                        'timestamp': datetime.utcnow().isoformat()
                    }), 401

                # Extract token (format: "Bearer <token>")
                try:
                    token = auth_header.split(' ')[1]
                except IndexError:
                    return jsonify({
                        'error': 'Invalid Authorization Header',
                        'message': 'Authorization header must be in format: Bearer <token>',
                        'status_code': 401,
                        'timestamp': datetime.utcnow().isoformat()
                    }), 401

                # Verify token
                user_data = clerk_auth.verify_token(token)

                # Check if token is expired
                if user_data.get('exp', 0) < time.time():
                    return jsonify({
                        'error': 'Token Expired',
                        'message': 'Authentication token has expired',
                        'status_code': 401,
                        'timestamp': datetime.utcnow().isoformat()
                    }), 401

                # Check required permissions
                if required_permissions:
                    user_permissions = user_data.get('permissions', [])
                    user_roles = user_data.get('roles', [])

                    # Admin role bypasses permission checks
                    if 'admin' not in user_roles:
                        missing_permissions = [
                            perm for perm in required_permissions
                            if perm not in user_permissions
                        ]

                        if missing_permissions:
                            return jsonify({
                                'error': 'Insufficient Permissions',
                                'message': f'Required permissions: {missing_permissions}',
                                'status_code': 403,
                                'timestamp': datetime.utcnow().isoformat()
                            }), 403

                # Store user data in g for access in the endpoint
                g.current_user = user_data
                g.user_id = user_data.get('user_id')
                g.user_roles = user_data.get('roles', [])
                g.user_permissions = user_data.get('permissions', [])

                logger.info(f"Authenticated user: {user_data.get('email', 'unknown')} (ID: {user_data.get('user_id')})")

                return f(*args, **kwargs)

            except ValueError as e:
                logger.warning(f"Authentication failed: {str(e)}")
                return jsonify({
                    'error': 'Authentication Failed',
                    'message': str(e),
                    'status_code': 401,
                    'timestamp': datetime.utcnow().isoformat()
                }), 401

            except Exception as e:
                logger.error(f"Authentication error: {str(e)}")
                return jsonify({
                    'error': 'Authentication Error',
                    'message': 'An error occurred during authentication',
                    'status_code': 500,
                    'timestamp': datetime.utcnow().isoformat()
                }), 500

        return decorated_function
    return decorator

def require_role(*required_roles):
    """
    Decorator to require specific roles for endpoints.

    Usage:
        @require_role('admin')
        def admin_only_endpoint():
            pass

        @require_role('admin', 'moderator')
        def admin_or_moderator_endpoint():
            pass
    """
    def decorator(f):
        @wraps(f)
        @require_auth()
        def decorated_function(*args, **kwargs):
            user_roles = g.get('user_roles', [])

            # Check if user has any of the required roles
            if not any(role in user_roles for role in required_roles):
                return jsonify({
                    'error': 'Insufficient Role',
                    'message': f'Required roles: {list(required_roles)}',
                    'status_code': 403,
                    'timestamp': datetime.utcnow().isoformat()
                }), 403

            return f(*args, **kwargs)

        return decorated_function
    return decorator

def get_current_user():
    """
    Get current authenticated user from request context.
    Returns user data if authenticated, None otherwise.
    """
    return g.get('current_user')

def is_authenticated():
    """
    Check if current request is authenticated.
    Returns True if authenticated, False otherwise.
    """
    return g.get('current_user') is not None

def has_permission(permission):
    """
    Check if current user has specific permission.
    Returns True if user has permission, False otherwise.
    """
    user_permissions = g.get('user_permissions', [])
    user_roles = g.get('user_roles', [])

    # Admin role has all permissions
    if 'admin' in user_roles:
        return True

    return permission in user_permissions

def has_role(role):
    """
    Check if current user has specific role.
    Returns True if user has role, False otherwise.
    """
    user_roles = g.get('user_roles', [])
    return role in user_roles