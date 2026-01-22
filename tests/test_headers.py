"""
Unit tests for HTTP headers and response formatting
"""

import unittest
from http.server import HTTPServer
from urllib.request import urlopen
from urllib.error import HTTPError
import threading
import time
from main import RequestHandler


class TestHeaders(unittest.TestCase):
    """Test HTTP headers and response formatting"""

    @classmethod
    def setUpClass(cls):
        """Set up API server for testing"""
        cls.host = "localhost"
        cls.port = 9998
        cls.server_address = (cls.host, cls.port)

        # Create and start the server
        cls.httpd = HTTPServer(cls.server_address, RequestHandler)
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()

        # Give server time to start
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        """Shut down API server"""
        cls.httpd.shutdown()

    def test_cors_headers(self):
        """Test that CORS headers are present"""
        try:
            response = urlopen(f"http://{self.host}:{self.port}/")
            headers = response.headers

            self.assertIn("Access-Control-Allow-Origin", headers)
            self.assertEqual(headers["Access-Control-Allow-Origin"], "*")
        except HTTPError as e:
            self.fail(f"Unexpected HTTP error: {e}")

    def test_cors_methods_header(self):
        """Test that CORS methods header is present"""
        try:
            response = urlopen(f"http://{self.host}:{self.port}/")
            headers = response.headers

            self.assertIn("Access-Control-Allow-Methods", headers)
            self.assertIn("GET", headers["Access-Control-Allow-Methods"])
        except HTTPError as e:
            self.fail(f"Unexpected HTTP error: {e}")

    def test_cors_headers_allowed(self):
        """Test that CORS headers allowed is present"""
        try:
            response = urlopen(f"http://{self.host}:{self.port}/")
            headers = response.headers

            self.assertIn("Access-Control-Allow-Headers", headers)
        except HTTPError as e:
            self.fail(f"Unexpected HTTP error: {e}")

    def test_content_type_json(self):
        """Test that JSON endpoints return correct content type"""
        try:
            response = urlopen(f"http://{self.host}:{self.port}/openapi.json")
            headers = response.headers

            self.assertIn("Content-type", headers)
            self.assertIn("application/json", headers["Content-type"])
        except HTTPError as e:
            self.fail(f"Unexpected HTTP error: {e}")

    def test_content_type_html(self):
        """Test that docs endpoint returns HTML content type"""
        try:
            response = urlopen(f"http://{self.host}:{self.port}/")
            headers = response.headers

            self.assertIn("Content-type", headers)
            self.assertIn("text/html", headers["Content-type"])
        except HTTPError as e:
            self.fail(f"Unexpected HTTP error: {e}")

    def test_content_type_error_response(self):
        """Test that error responses have correct content type"""
        try:
            urlopen(f"http://{self.host}:{self.port}/invalid/endpoint")
        except HTTPError as e:
            headers = e.headers

            self.assertIn("Content-type", headers)
            self.assertIn("application/json", headers["Content-type"])


if __name__ == "__main__":
    unittest.main()
