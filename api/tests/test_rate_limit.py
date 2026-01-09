"""
Tests for rate limiting utility
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.rate_limit import check_rate_limit, request_counts, RATE_LIMIT


class TestRateLimit:
    """Test cases for rate limiting functionality"""

    def setup_method(self):
        """Clear rate limit state before each test"""
        request_counts.clear()

    def test_allows_requests_under_limit(self):
        """Test that requests under the limit are allowed"""
        ip = '192.168.1.1'

        # First request should be allowed
        assert check_rate_limit(ip) == True

        # Multiple requests under limit should be allowed
        for _ in range(10):
            assert check_rate_limit(ip) == True

    def test_blocks_requests_over_limit(self):
        """Test that requests over the limit are blocked"""
        ip = '192.168.1.2'

        # Make RATE_LIMIT requests (all should pass)
        for _ in range(RATE_LIMIT):
            assert check_rate_limit(ip) == True

        # Next request should be blocked
        assert check_rate_limit(ip) == False

    def test_separate_limits_per_ip(self):
        """Test that each IP has its own rate limit"""
        ip1 = '192.168.1.3'
        ip2 = '192.168.1.4'

        # Exhaust limit for ip1
        for _ in range(RATE_LIMIT):
            check_rate_limit(ip1)

        # ip1 should be blocked
        assert check_rate_limit(ip1) == False

        # ip2 should still be allowed
        assert check_rate_limit(ip2) == True

    def test_handles_unknown_ip(self):
        """Test handling of unknown IP"""
        assert check_rate_limit('unknown') == True

    def test_handles_empty_ip(self):
        """Test handling of empty IP string"""
        assert check_rate_limit('') == True


class TestRateLimitHeaders:
    """Test cases for rate limit headers"""

    def setup_method(self):
        """Clear rate limit state before each test"""
        request_counts.clear()

    def test_get_rate_limit_headers(self):
        """Test that rate limit headers are returned correctly"""
        from utils.rate_limit import get_rate_limit_headers

        ip = '192.168.1.5'

        # Make some requests
        for _ in range(5):
            check_rate_limit(ip)

        headers = get_rate_limit_headers(ip)

        assert 'X-RateLimit-Limit' in headers
        assert 'X-RateLimit-Remaining' in headers
        assert 'X-RateLimit-Reset' in headers

        assert headers['X-RateLimit-Limit'] == str(RATE_LIMIT)
        assert int(headers['X-RateLimit-Remaining']) == RATE_LIMIT - 5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
