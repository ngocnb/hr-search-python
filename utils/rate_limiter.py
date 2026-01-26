import threading
import time
from typing import Dict


class RateLimiter:
    """Simple in-memory rate limiter using token bucket algorithm"""

    def __init__(self, requests_per_second: int = 10):
        self.requests_per_second = requests_per_second
        self.clients: Dict[str, Dict] = {}
        self.lock = threading.Lock()

    def is_allowed(self, client_ip: str) -> bool:
        """Check if client is allowed to make a request"""
        now = time.time()
        with self.lock:
            if client_ip not in self.clients:
                self.clients[client_ip] = {
                    "tokens": self.requests_per_second,
                    "last_refill": now,
                }

            client = self.clients[client_ip]

            # Refill tokens based on time elapsed
            time_elapsed = now - client["last_refill"]
            tokens_to_add = time_elapsed * self.requests_per_second
            client["tokens"] = min(
                self.requests_per_second, client["tokens"] + tokens_to_add
            )
            client["last_refill"] = now

            # Check if request can be processed
            if client["tokens"] >= 1:
                client["tokens"] -= 1
                return True

            return False
