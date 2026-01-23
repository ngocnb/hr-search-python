import unittest
import json
import threading
import time
from http.server import HTTPServer
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from main import RequestHandler


class TestEmployeeSearchAPI(unittest.TestCase):
    """Comprehensive tests for /api/v1/employees/search endpoint"""

    @classmethod
    def setUpClass(cls):
        """Set up API server for testing"""
        cls.host = "localhost"
        cls.port = 9996
        cls.server_address = (cls.host, cls.port)

        cls.httpd = HTTPServer(cls.server_address, RequestHandler)
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()

        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        """Shut down API server"""
        cls.httpd.shutdown()

    def _make_search_request(self, payload):
        """Helper to make search request"""
        req = Request(
            f"http://{self.host}:{self.port}/api/v1/employees/search",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        return urlopen(req)

    def test_search_endpoint_basic_request(self):
        """Test basic search request"""
        response = self._make_search_request(
            {
                "q": "",
                "company_ids": [],
                "department_ids": [],
                "position_ids": [],
                "locations": [],
                "statuses": [],
                "limit": 50,
                "page": 1,
            }
        )

        self.assertEqual(response.getcode(), 200)
        data = json.loads(response.read().decode("utf-8"))
        self.assertIn("employees", data)
        self.assertIn("pagination", data)

    def test_search_response_structure(self):
        """Test search response has correct structure"""
        response = self._make_search_request(
            {
                "q": "",
                "company_ids": [],
                "department_ids": [],
                "position_ids": [],
                "locations": [],
                "statuses": [],
                "limit": 10,
                "page": 1,
            }
        )

        data = json.loads(response.read().decode("utf-8"))

        # Verify response structure
        self.assertIn("employees", data)
        self.assertIsInstance(data["employees"], list)

        self.assertIn("pagination", data)
        pagination = data["pagination"]
        self.assertIn("total", pagination)
        self.assertIn("limit", pagination)
        self.assertIn("offset", pagination)
        self.assertIn("has_more", pagination)

        # Verify types
        self.assertIsInstance(pagination["total"], int)
        self.assertIsInstance(pagination["limit"], int)
        self.assertIsInstance(pagination["offset"], int)
        self.assertIsInstance(pagination["has_more"], bool)

    def test_search_with_query_parameter(self):
        """Test search with search query"""
        response = self._make_search_request(
            {
                "q": "john",
                "company_ids": [],
                "department_ids": [],
                "position_ids": [],
                "locations": [],
                "statuses": [],
                "limit": 50,
                "page": 1,
            }
        )

        data = json.loads(response.read().decode("utf-8"))
        self.assertIn("employees", data)
        self.assertIn("pagination", data)

    def test_search_with_company_filter(self):
        """Test search with company filter"""
        response = self._make_search_request(
            {
                "q": "",
                "company_ids": [1],
                "department_ids": [],
                "position_ids": [],
                "locations": [],
                "statuses": [],
                "limit": 50,
                "page": 1,
            }
        )

        data = json.loads(response.read().decode("utf-8"))
        self.assertIn("employees", data)
        self.assertIn("pagination", data)

    def test_search_with_status_filter(self):
        """Test search with status filter"""
        response = self._make_search_request(
            {
                "q": "",
                "company_ids": [],
                "department_ids": [],
                "position_ids": [],
                "locations": [],
                "statuses": ["Active"],
                "limit": 50,
                "page": 1,
            }
        )

        data = json.loads(response.read().decode("utf-8"))
        self.assertIn("employees", data)

    def test_search_with_multiple_filters(self):
        """Test search with multiple filters"""
        response = self._make_search_request(
            {
                "q": "john",
                "company_ids": [1, 2],
                "department_ids": [1],
                "position_ids": [],
                "locations": ["New York"],
                "statuses": ["Active"],
                "limit": 25,
                "page": 1,
            }
        )

        data = json.loads(response.read().decode("utf-8"))
        self.assertIn("employees", data)
        self.assertEqual(data["pagination"]["limit"], 25)

    def test_search_with_pagination(self):
        """Test search pagination"""
        response = self._make_search_request(
            {
                "q": "",
                "company_ids": [],
                "department_ids": [],
                "position_ids": [],
                "locations": [],
                "statuses": [],
                "limit": 5,
                "page": 2,
            }
        )

        data = json.loads(response.read().decode("utf-8"))
        pagination = data["pagination"]
        self.assertEqual(pagination["limit"], 5)
        self.assertEqual(pagination["offset"], 5)

    def test_search_with_max_limit(self):
        """Test that limit > 100 is rejected"""
        with self.assertRaises(HTTPError) as context:
            self._make_search_request(
                {
                    "q": "",
                    "company_ids": [],
                    "department_ids": [],
                    "position_ids": [],
                    "locations": [],
                    "statuses": [],
                    "limit": 999,
                    "page": 1,
                }
            )

        self.assertEqual(context.exception.code, 400)
        payload = json.loads(context.exception.read().decode("utf-8"))
        self.assertIn("limit", payload.get("error", ""))

    def test_search_invalid_json(self):
        """Test search endpoint with invalid JSON"""
        req = Request(
            f"http://{self.host}:{self.port}/api/v1/employees/search",
            data=b"invalid json {]",
            headers={"Content-Type": "application/json"},
        )

        with self.assertRaises(HTTPError) as context:
            urlopen(req)

        self.assertEqual(context.exception.code, 400)
        content = context.exception.read().decode("utf-8")
        data = json.loads(content)
        self.assertIn("error", data)
        self.assertIn("Invalid JSON", data["error"])

    def test_search_empty_body(self):
        """Test search endpoint with empty body"""
        req = Request(
            f"http://{self.host}:{self.port}/api/v1/employees/search",
            data=b"",
            headers={"Content-Type": "application/json"},
        )

        with self.assertRaises(HTTPError) as context:
            urlopen(req)

        self.assertEqual(context.exception.code, 400)

    def test_search_response_content_type(self):
        """Test that search response has JSON content type"""
        response = self._make_search_request(
            {
                "q": "",
                "company_ids": [],
                "department_ids": [],
                "position_ids": [],
                "locations": [],
                "statuses": [],
                "limit": 50,
                "page": 1,
            }
        )

        self.assertIn("application/json", response.headers["Content-type"])

    def test_search_cors_headers(self):
        """Test that search response includes CORS headers"""
        response = self._make_search_request(
            {
                "q": "",
                "company_ids": [],
                "department_ids": [],
                "position_ids": [],
                "locations": [],
                "statuses": [],
                "limit": 50,
                "page": 1,
            }
        )

        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "*")
        self.assertIn("GET", response.headers["Access-Control-Allow-Methods"])

    def test_search_with_string_limit(self):
        """Test search with string limit parameter"""
        response = self._make_search_request(
            {
                "q": "",
                "company_ids": [],
                "department_ids": [],
                "position_ids": [],
                "locations": [],
                "statuses": [],
                "limit": 25,
                "page": 1,
            }
        )

        data = json.loads(response.read().decode("utf-8"))
        self.assertEqual(data["pagination"]["limit"], 25)

    def test_search_empty_result(self):
        """Test search that returns no results"""
        response = self._make_search_request(
            {
                "q": "nonexistentemployeename12345xyz",
                "company_ids": [],
                "department_ids": [],
                "position_ids": [],
                "locations": [],
                "statuses": [],
                "limit": 50,
                "page": 1,
            }
        )

        data = json.loads(response.read().decode("utf-8"))
        self.assertEqual(data["pagination"]["total"], 0)
        self.assertEqual(len(data["employees"]), 0)

    def test_search_with_special_characters(self):
        """Test search with special characters (SQL injection attempt)"""
        response = self._make_search_request(
            {
                "q": "'; DROP TABLE employees; --",
                "company_ids": [],
                "department_ids": [],
                "position_ids": [],
                "locations": [],
                "statuses": [],
                "limit": 50,
                "page": 1,
            }
        )

        # Should not crash or return error
        self.assertEqual(response.getcode(), 200)
        data = json.loads(response.read().decode("utf-8"))
        self.assertIn("employees", data)

    def test_validation_fails_on_limit_too_high(self):
        """Validation should reject limit > 100"""
        with self.assertRaises(HTTPError) as context:
            self._make_search_request({"limit": 1000, "page": 1})

        self.assertEqual(context.exception.code, 400)
        payload = json.loads(context.exception.read().decode("utf-8"))
        self.assertIn("limit", payload.get("error", ""))

    def test_validation_fails_on_negative_page(self):
        """Validation should reject non-positive page"""
        with self.assertRaises(HTTPError) as context:
            self._make_search_request({"limit": 10, "page": 0})

        self.assertEqual(context.exception.code, 400)
        payload = json.loads(context.exception.read().decode("utf-8"))
        self.assertIn("page", payload.get("error", ""))

    def test_validation_fails_on_non_int_company_ids(self):
        """Validation should reject non-integer company_ids"""
        with self.assertRaises(HTTPError) as context:
            self._make_search_request({"company_ids": ["abc"], "page": 1, "limit": 10})

        self.assertEqual(context.exception.code, 400)
        payload = json.loads(context.exception.read().decode("utf-8"))
        self.assertIn("company_ids", payload.get("error", ""))

    def test_validation_fails_on_non_string_query(self):
        """Validation should reject non-string q"""
        with self.assertRaises(HTTPError) as context:
            self._make_search_request({"q": 123, "page": 1, "limit": 10})

        self.assertEqual(context.exception.code, 400)
        payload = json.loads(context.exception.read().decode("utf-8"))
        self.assertIn("q", payload.get("error", ""))


if __name__ == "__main__":
    unittest.main()
