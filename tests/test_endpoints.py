"""
Unit tests for API endpoints
"""

import unittest
import json
import threading
import time
from http.server import HTTPServer
from urllib.request import urlopen
from urllib.error import HTTPError
from main import RequestHandler


class TestAPIEndpoints(unittest.TestCase):
    """Test API endpoints"""

    @classmethod
    def setUpClass(cls):
        """Set up API server for testing"""
        cls.host = "localhost"
        cls.port = 9999
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

    def test_openapi_docs_endpoint(self):
        """Test that OpenAPI docs endpoint returns HTML"""
        try:
            response = urlopen(f"http://{self.host}:{self.port}/")
            content = response.read().decode("utf-8")
            status_code = response.getcode()

            self.assertEqual(status_code, 200)
            self.assertIn("HR Employee Search API", content)
            self.assertIn("<!DOCTYPE html>", content)
        except HTTPError as e:
            self.fail(f"Unexpected HTTP error: {e}")

    def test_openapi_spec_endpoint(self):
        """Test that OpenAPI spec endpoint returns valid JSON"""
        try:
            response = urlopen(f"http://{self.host}:{self.port}/openapi.json")
            content = response.read().decode("utf-8")
            status_code = response.getcode()

            self.assertEqual(status_code, 200)

            spec = json.loads(content)
            self.assertEqual(spec["openapi"], "3.0.0")
            self.assertEqual(spec["info"]["title"], "HR Employee Search API")
            self.assertIn("/api/v1/employees/search", spec["paths"])
        except HTTPError as e:
            self.fail(f"Unexpected HTTP error: {e}")

    def test_employee_search_endpoint(self):
        """Test employee search endpoint"""
        try:
            import urllib.request

            req = urllib.request.Request(
                f"http://{self.host}:{self.port}/api/v1/employees/search",
                data=json.dumps({"company_ids": "1"}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            response = urllib.request.urlopen(req)
            content = response.read().decode("utf-8")
            status_code = response.getcode()

            self.assertEqual(status_code, 200)

            data = json.loads(content)
            # Employee search endpoint should return employee data
            self.assertIsNotNone(data)
        except HTTPError as e:
            self.fail(f"Unexpected HTTP error: {e}")

    def test_404_not_found(self):
        """Test that invalid endpoint returns 404"""
        try:
            urlopen(f"http://{self.host}:{self.port}/invalid/endpoint")
            self.fail("Should have raised HTTPError for 404")
        except HTTPError as e:
            self.assertEqual(e.code, 404)
            content = e.read().decode("utf-8")
            data = json.loads(content)
            self.assertIn("error", data)

    def test_options_request(self):
        """Test that OPTIONS requests return 200"""
        import urllib.request

        req = urllib.request.Request(
            f"http://{self.host}:{self.port}/api/v1/employees/search"
        )
        req.get_method = lambda: "OPTIONS"

        try:
            response = urllib.request.urlopen(req)
            self.assertEqual(response.getcode(), 200)
        except HTTPError as e:
            self.fail(f"Unexpected HTTP error: {e}")


if __name__ == "__main__":
    unittest.main()
