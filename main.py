"""
HR Employee Search Microservice
A FastAPI-like web service built with Python standard library only
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import time
import threading
from typing import Dict, List, Any
import os
import sys
import argparse
import glob
from database import Database


class RateLimiter:
    """Simple in-memory rate limiter using token bucket algorithm"""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.clients: Dict[str, Dict] = {}
        self.lock = threading.Lock()

    def is_allowed(self, client_ip: str) -> bool:
        """Check if client is allowed to make a request"""
        with self.lock:
            now = time.time()

            if client_ip not in self.clients:
                self.clients[client_ip] = {
                    "tokens": self.requests_per_minute,
                    "last_refill": now,
                }

            client = self.clients[client_ip]

            # Refill tokens based on time elapsed
            time_elapsed = now - client["last_refill"]
            tokens_to_add = time_elapsed * (self.requests_per_minute / 60)
            client["tokens"] = min(
                self.requests_per_minute, client["tokens"] + tokens_to_add
            )
            client["last_refill"] = now

            # Check if request can be processed
            if client["tokens"] >= 1:
                client["tokens"] -= 1
                return True

            return False


class RequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for employee search API"""

    # Initialize database and rate limiter as class variables
    db = Database()
    rate_limiter = RateLimiter(requests_per_minute=60)

    def _set_headers(
        self, status_code: int = 200, content_type: str = "application/json"
    ):
        """Set HTTP response headers"""
        self.send_response(status_code)
        self.send_header("Content-type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _get_client_ip(self) -> str:
        """Get client IP address"""
        return self.client_address[0]

    def _parse_query_params(self, path: str) -> Dict[str, List[str]]:
        """Parse query parameters from URL"""
        parsed = urlparse(path)
        return parse_qs(parsed.query)

    def _get_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """Send JSON response"""
        self._set_headers(status_code)
        response = json.dumps(data, indent=2)
        self.wfile.write(response.encode("utf-8"))

    def _get_error_response(self, message: str, status_code: int = 400):
        """Send error response"""
        self._get_json_response({"error": message}, status_code)

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self._set_headers(200)

    def do_GET(self):
        """Handle GET requests"""
        client_ip = self._get_client_ip()

        # Rate limiting
        if not self.rate_limiter.is_allowed(client_ip):
            self._get_error_response("Rate limit exceeded", 429)
            return

        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == "/":
            self._serve_openapi_docs()
        elif path == "/api/v1/employees/search":
            # TODO: Implement employee search handling
            self._get_json_response({"message": "Employee search endpoint"})
        elif path == "/openapi.json":
            self._serve_openapi_spec()
        else:
            self._get_error_response("Endpoint not found", 404)

    def _serve_openapi_docs(self):
        """Serve simple OpenAPI documentation page"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>HR Employee Search API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .method { color: #fff; padding: 3px 8px; border-radius: 3px; font-weight: bold; }
                .get { background: #61affe; }
                .param { margin: 5px 0; }
                code { background: #f0f0f0; padding: 2px 4px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>HR Employee Search API</h1>
            <p>API documentation for the HR Employee Search Microservice</p>
            
            <div class="endpoint">
                <span class="method get">GET</span> <code>/api/v1/employees/search</code>
                <h3>Search Employees</h3>
                <div class="param"><strong>company_ids</strong> (optional): Comma-separated company IDs</div>
                <div class="param"><strong>q</strong> (optional): Search query (first name, last name, email)</div>
                <div class="param"><strong>department_ids</strong> (optional): Comma-separated department IDs</div>
                <div class="param"><strong>position_ids</strong> (optional): Comma-separated position IDs</div>
                <div class="param"><strong>locations</strong> (optional): Comma-separated locations</div>
                <div class="param"><strong>statuses</strong> (optional): Comma-separated statuses (Active, Not started, Terminated)</div>
                <div class="param"><strong>limit</strong> (optional): Results per page (default: 50, max: 100)</div>
                <div class="param"><strong>page</strong> (optional): Page number for pagination (default: 1)</div>
            </div>
            
            <p><a href="/openapi.json">Download OpenAPI Spec</a></p>
        </body>
        </html>
        """
        self._set_headers(200, "text/html")
        self.wfile.write(html.encode("utf-8"))

    def _serve_openapi_spec(self):
        """Serve OpenAPI specification"""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "HR Employee Search API",
                "version": "1.0.0",
                "description": "API for searching employees in HR directory",
            },
            "paths": {
                "/api/v1/employees/search": {
                    "get": {
                        "summary": "Search employees",
                        "parameters": [
                            {
                                "name": "company_ids",
                                "in": "query",
                                "required": True,
                                "schema": {"type": "string"},
                            },
                            {
                                "name": "q",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "string"},
                            },
                            {
                                "name": "department_ids",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "string"},
                            },
                            {
                                "name": "position_ids",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "string"},
                            },
                            {
                                "name": "locations",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "string"},
                            },
                            {
                                "name": "statuses",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "string"},
                            },
                            {
                                "name": "limit",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "integer", "default": 50},
                            },
                            {
                                "name": "offset",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "integer", "default": 0},
                            },
                        ],
                        "responses": {
                            "200": {"description": "Successful response"},
                            "400": {"description": "Bad request"},
                            "429": {"description": "Rate limit exceeded"},
                        },
                    }
                }
            },
        }
        self._get_json_response(spec)


def run_server(host: str = "localhost", port: int = 8000, debug: bool = False):
    """Run the HTTP server"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"HR Employee Search API running on http://{host}:{port}")
    print("API Documentation: http://localhost:8000")
    print("OpenAPI Spec: http://localhost:8000/openapi.json")

    if debug:
        print("Debug mode is ON - Hot reload is enabled.")
        # Start file watcher thread for hot reload
        watcher_thread = threading.Thread(
            target=_watch_files_for_reload, args=(httpd,), daemon=True
        )
        watcher_thread.start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()


def _watch_files_for_reload(httpd: HTTPServer):
    """Watch Python files for changes and restart server"""
    watched_files = {}
    check_interval = 1  # Check every 1 second

    # Get all Python files in project
    def get_project_files():
        py_files = glob.glob("**/*.py", recursive=True)
        # Exclude __pycache__
        return [f for f in py_files if "__pycache__" not in f]

    # Initial scan
    for file_path in get_project_files():
        try:
            watched_files[file_path] = os.path.getmtime(file_path)
        except OSError:
            pass

    print(f"Watching {len(watched_files)} Python files for changes...")

    while True:
        time.sleep(check_interval)
        current_files = get_project_files()

        # Check for modified files
        for file_path in current_files:
            try:
                current_mtime = os.path.getmtime(file_path)

                if file_path not in watched_files:
                    # New file detected
                    print(f"[HOT RELOAD] New file detected: {file_path}")
                    print("[HOT RELOAD] Restarting server...")
                    os.execv(sys.executable, [sys.executable] + sys.argv)
                    break
                elif watched_files[file_path] != current_mtime:
                    # File modified
                    print(f"[HOT RELOAD] File modified: {file_path}")
                    print("[HOT RELOAD] Restarting server...")
                    os.execv(sys.executable, [sys.executable] + sys.argv)
                    break
            except OSError:
                pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HR Employee Search API")
    parser.add_argument(
        "--debug",
        type=lambda x: x.lower() == "true",
        default=False,
        help="Enable debug mode with hot reload (default: False)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host to bind to (default: localhost)",
    )

    args = parser.parse_args()
    run_server(host=args.host, port=args.port, debug=args.debug)
