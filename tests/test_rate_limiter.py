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

    def test_rate_limiter_cleanup_inactive_clients(self):
        """Test that inactive clients are cleaned up to prevent memory leak"""
        # Create a limiter with short cleanup interval for testing (2 seconds)
        limiter = RateLimiter(requests_per_second=5, cleanup_interval=2)

        # Add some clients
        client1 = "192.168.1.10"
        client2 = "192.168.1.11"
        client3 = "192.168.1.12"

        limiter.is_allowed(client1)
        limiter.is_allowed(client2)
        limiter.is_allowed(client3)

        # Should have 3 clients
        self.assertEqual(len(limiter.clients), 3)

        # Wait for cleanup interval + some buffer
        time.sleep(2.5)

        # Add a new client - this should trigger cleanup
        client4 = "192.168.1.13"
        limiter.is_allowed(client4)

        # Old clients should be cleaned up, only client4 should remain
        self.assertEqual(len(limiter.clients), 1)
        self.assertIn(client4, limiter.clients)
        self.assertNotIn(client1, limiter.clients)
        self.assertNotIn(client2, limiter.clients)
        self.assertNotIn(client3, limiter.clients)

    def test_rate_limiter_cleanup_keeps_active_clients(self):
        """Test that active clients are not cleaned up"""
        # Create a limiter with short cleanup interval for testing (2 seconds)
        limiter = RateLimiter(requests_per_second=5, cleanup_interval=2)

        # Add a client
        client1 = "192.168.1.20"
        limiter.is_allowed(client1)

        # Wait less than cleanup interval
        time.sleep(1)

        # Make another request from the same client (keeps it active)
        limiter.is_allowed(client1)

        # Wait a bit more (total > cleanup_interval, but last activity < cleanup_interval)
        time.sleep(1.5)

        # Trigger cleanup with a new client
        client2 = "192.168.1.21"
        limiter.is_allowed(client2)

        # client1 should still be there because it was active recently
        self.assertIn(client1, limiter.clients)
        self.assertIn(client2, limiter.clients)


if __name__ == "__main__":
    unittest.main()
