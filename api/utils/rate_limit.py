"""
Rate Limiting Utility for API Endpoints
Simple in-memory rate limiter (resets on cold start)
"""

from datetime import datetime, timedelta
from collections import defaultdict

# In-memory storage for request counts
# Note: This resets on serverless cold start, which is acceptable for basic protection
request_counts = defaultdict(list)

# Rate limit configuration
RATE_LIMIT = 60  # requests per minute per IP
WINDOW = 60  # seconds


def check_rate_limit(ip: str) -> bool:
    """
    Check if a request should be allowed based on rate limiting.

    Args:
        ip: The client IP address

    Returns:
        True if request should be allowed, False if rate limited
    """
    now = datetime.now()
    cutoff = now - timedelta(seconds=WINDOW)

    # Clean old requests outside the window
    request_counts[ip] = [t for t in request_counts[ip] if t > cutoff]

    # Check if over limit
    if len(request_counts[ip]) >= RATE_LIMIT:
        return False

    # Record this request
    request_counts[ip].append(now)
    return True


def get_rate_limit_headers(ip: str) -> dict:
    """
    Get rate limit headers for response.

    Args:
        ip: The client IP address

    Returns:
        Dictionary of rate limit headers
    """
    now = datetime.now()
    cutoff = now - timedelta(seconds=WINDOW)
    current_count = len([t for t in request_counts.get(ip, []) if t > cutoff])

    return {
        "X-RateLimit-Limit": str(RATE_LIMIT),
        "X-RateLimit-Remaining": str(max(0, RATE_LIMIT - current_count)),
        "X-RateLimit-Reset": str(int((cutoff + timedelta(seconds=WINDOW)).timestamp()))
    }
