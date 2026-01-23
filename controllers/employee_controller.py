from repositories.employee_repository import EmployeeRepository
from typing import Any
from utils.validations import Validations


class EmployeeController:
    def __init__(self, employee_repository: EmployeeRepository):
        self.employee_repository = employee_repository

    def search_employees(self, params: dict):
        validated_params = self._validate_and_normalize_params(params or {})
        return self.employee_repository.handle_employee_search(validated_params)

    def _validate_and_normalize_params(self, params: dict[str, Any]) -> dict[str, Any]:
        """Validate incoming search params and normalize types.

        - Ensures limit/page are positive and caps limit at 100
        - Coerces ids to positive ints (company/department/position)
        - Sanitizes search query for LIKE usage
        - Ensures list-type fields are lists of the right primitive type
        """

        # Core primitives
        raw_limit = params.get("limit", 50)
        raw_page = params.get("page", 1)

        limit = Validations.coerce_int_strict(raw_limit, "limit")
        if limit <= 0 or limit > 100:
            raise ValueError("limit must be between 1 and 100")

        page = Validations.coerce_int_strict(raw_page, "page")
        if page <= 0:
            raise ValueError("page must be a positive integer")

        search_query = params.get("q", "")
        if not isinstance(search_query, str):
            raise ValueError("q must be a string")
        search_query = Validations.sanitize_like_term(search_query.strip())

        company_ids = Validations.ensure_positive_int_list_strict(
            params.get("company_ids"), "company_ids"
        )
        department_ids = Validations.ensure_positive_int_list_strict(
            params.get("department_ids"), "department_ids"
        )
        position_ids = Validations.ensure_positive_int_list_strict(
            params.get("position_ids"), "position_ids"
        )
        locations = Validations.ensure_str_list_strict(
            params.get("locations"), "locations"
        )
        statuses = Validations.ensure_str_list_strict(
            params.get("statuses"), "statuses"
        )

        return {
            "q": search_query,
            "company_ids": company_ids,
            "department_ids": department_ids,
            "position_ids": position_ids,
            "locations": locations,
            "statuses": statuses,
            "limit": limit,
            "page": page,
        }
