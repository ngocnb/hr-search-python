"""
Unit tests for RateLimiter functionality
"""

import unittest
import time
from utils.rate_limiter import RateLimiter


class TestRateLimiter(unittest.TestCase):
    """Test rate limiter functionality"""

    rps = 5  # Requests per second

    def setUp(self):
        """Set up test fixtures"""
        self.limiter = RateLimiter(requests_per_second=self.rps)

    def test_rate_limiter_allows_initial_requests(self):
        """Test that initial requests are allowed"""
        client_ip = "192.168.1.1"
        for i in range(self.rps):
            self.assertTrue(
                self.limiter.is_allowed(client_ip), f"Request {i + 1} should be allowed"
            )

    def test_rate_limiter_blocks_excessive_requests(self):
        """Test that rate limiter blocks excessive requests"""
        client_ip = "192.168.1.2"
        # Use up all tokens
        for i in range(self.rps):
            self.limiter.is_allowed(client_ip)

        # Next request should be blocked
        self.assertFalse(
            self.limiter.is_allowed(client_ip),
            "Request should be blocked after limit exceeded",
        )

    def test_rate_limiter_different_clients(self):
        """Test that rate limiter tracks different clients separately"""
        client1 = "192.168.1.1"
        client2 = "192.168.1.2"

        # Use up tokens for client1
        for i in range(self.rps):
            self.limiter.is_allowed(client1)

        # Client1 should be blocked
        self.assertFalse(self.limiter.is_allowed(client1))

        # Client2 should still have tokens
        self.assertTrue(self.limiter.is_allowed(client2))

    def test_rate_limiter_token_refill(self):
        """Test that tokens refill over time"""
        client_ip = "192.168.1.3"

        # Use up all tokens
        for i in range(self.rps):
            self.limiter.is_allowed(client_ip)

        # Should be blocked
        self.assertFalse(self.limiter.is_allowed(client_ip))

        # Wait for token refill
        time.sleep(1.1)

        # Should now be allowed
        self.assertTrue(self.limiter.is_allowed(client_ip))


if __name__ == "__main__":
    unittest.main()
