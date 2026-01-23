class Helpers:
    @staticmethod
    def parse_string_list(value: str) -> list[str]:
        """Parse a comma-separated string into a list of strings"""
        if not value:
            return []
        return [item.strip() for item in value.split(",") if item.strip()]

    @staticmethod
    def parse_int_list(value: str) -> list[int]:
        """Parse a comma-separated string into a list of integers"""
        if not value:
            return []
        try:
            return [int(item.strip()) for item in value.split(",") if item.strip()]
        except ValueError:
            return []
