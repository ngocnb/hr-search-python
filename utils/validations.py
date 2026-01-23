class Validations:
    @staticmethod
    def coerce_int_strict(value: object, field: str) -> int:
        if isinstance(value, bool):
            raise ValueError(f"{field} must be an integer")
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.strip().lstrip("-+").isdigit():
            return int(value)
        raise ValueError(f"{field} must be an integer")

    @staticmethod
    def ensure_positive_int_list_strict(values: object, field: str) -> list[int]:
        result: list[int] = []
        if values is None:
            return result
        if isinstance(values, (str, int)):
            values = [values]
        if isinstance(values, list):
            for item in values:
                num = Validations.coerce_int_strict(item, field)
                if num <= 0:
                    raise ValueError(f"{field} values must be positive integers")
                result.append(num)
            return result
        raise ValueError(
            f"{field} must be a list of positive integers or a single integer"
        )

    @staticmethod
    def ensure_str_list_strict(values: object, field: str) -> list[str]:
        if values is None:
            return []
        if isinstance(values, str):
            return [values.strip()] if values.strip() else []
        if isinstance(values, list):
            cleaned = [str(v).strip() for v in values if str(v).strip()]
            if len(cleaned) != len(values):
                # Some entries were empty/whitespace; still acceptable but trimmed.
                return cleaned
            return cleaned
        raise ValueError(f"{field} must be a string or list of strings")

    @staticmethod
    def sanitize_like_term(term: str) -> str:
        # Strip LIKE wildcard characters to avoid user-controlled patterns
        return term.replace("%", "").replace("_", "")
