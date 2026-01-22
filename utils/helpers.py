import json
from typing import Any, Dict


class Helpers:
    @staticmethod
    def parse_string_list(self, value: str) -> list[str]:
        """Parse a comma-separated string into a list of strings"""
        if not value:
            return []
        return [item.strip() for item in value.split(",") if item.strip()]

    @staticmethod
    def parse_int_list(self, value: str) -> list[int]:
        """Parse a comma-separated string into a list of integers"""
        if not value:
            return []
        try:
            return [int(item.strip()) for item in value.split(",") if item.strip()]
        except ValueError:
            return []

    @staticmethod
    def get_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """Send JSON response"""
        self._set_headers(status_code)
        response = json.dumps(data, indent=2)
        self.wfile.write(response.encode("utf-8"))

    @staticmethod
    def get_error_response(self, message: str, status_code: int = 400):
        """Send error response"""
        self._get_json_response({"error": message}, status_code)
