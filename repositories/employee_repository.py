from typing import Any
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class EmployeeRepository:
    def __init__(self, db):
        self.db = db

    def handle_employee_search(self, params: dict):
        """Handle employee search with validated parameters from controller.

        Assumes params are already validated and normalized by the controller:
        - q: sanitized string
        - company_ids, department_ids, position_ids: list of positive ints
        - locations, statuses: list of strings
        - limit: int (1-100)
        - page: positive int
        """
        # Extract parameters (already validated by controller)
        search_query = params.get("q", "")
        company_ids = params.get("company_ids", [])
        department_ids = params.get("department_ids", [])
        position_ids = params.get("position_ids", [])
        locations = params.get("locations", [])
        statuses = params.get("statuses", [])
        limit = params.get("limit", 50)
        page = params.get("page", 1)
        offset = (page - 1) * limit

        # Build and execute search query
        try:
            employees, total_count = self._search_employees(
                company_ids,
                search_query,
                department_ids,
                position_ids,
                locations,
                statuses,
                limit,
                offset,
            )

            response = {
                "employees": employees,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_count,
                },
            }

            return response
        except Exception as e:
            logger.error(f"Database error during employee search: {e}", exc_info=True)
            raise RuntimeError(f"Failed to execute employee search: {str(e)}") from e

    def _search_employees(
        self,
        company_ids: list[int],
        search_query: str,
        department_ids: list[int],
        position_ids: list[int],
        locations: list[str],
        statuses: list[str],
        limit: int,
        offset: int,
    ) -> tuple:
        """Search employees with filters"""
        with self.db as conn:
            cursor = conn.cursor()

            # Get column configuration
            columns = self._get_column_configuration()
            column_names: list[str] = [col["column_name"] for col in columns]
            # build select clause based on visible columns
            select_clause = ", ".join(
                [
                    f"e.{col}"
                    for col in column_names
                    if col
                    in [
                        "first_name",
                        "last_name",
                        "email",
                        "location",
                        "phone",
                        "status",
                        "company_id",
                    ]
                ]
            )
            join_clause = ""
            # build join clauses if department or position is visible
            if "department" in column_names:
                select_clause += ", d.name as department"
                join_clause += " LEFT JOIN departments d ON e.department_id = d.id"

            if "position" in column_names:
                select_clause += ", p.title as position"
                join_clause += " LEFT JOIN positions p ON e.position_id = p.id"

            # Build base query with joins
            query = f"""
                SELECT e.id, {select_clause}
                FROM employees e
                {join_clause}
            """
            params = []
            where = "WHERE 1=1"

            # Add search conditions
            if search_query:
                # 1. Escape any existing double quotes in the user input to prevent injection
                safe_query = search_query.replace('"', '""')

                # 2. Wrap the query in double quotes for FTS5 literal matching
                # Example: "john@techcorp.com" instead of john@techcorp.com
                safe_query = f'"{safe_query}"'
                where += " AND e.id IN (SELECT rowid FROM employees_fts WHERE employees_fts MATCH ?)"
                search_param = f"{safe_query}*"
                params.append(search_param)

            if company_ids:
                placeholders = ",".join("?" * len(company_ids))
                where += f" AND e.company_id IN ({placeholders})"
                params.extend(company_ids)

            if department_ids:
                placeholders = ",".join("?" * len(department_ids))
                where += f" AND e.department_id IN ({placeholders})"
                params.extend(department_ids)

            if position_ids:
                placeholders = ",".join("?" * len(position_ids))
                where += f" AND e.position_id IN ({placeholders})"
                params.extend(position_ids)

            if locations:
                location_conditions = " OR ".join(
                    ["e.location LIKE ?"] * len(locations)
                )
                where += f" AND ({location_conditions})"
                location_params = [f"%{loc}%" for loc in locations]
                params.extend(location_params)

            if statuses:
                status_placeholders = ",".join("?" * len(statuses))
                where += f" AND e.status IN ({status_placeholders})"
                params.extend(statuses)

            # Get total count
            count_query = "SELECT COUNT(*) FROM employees e " + where
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]

            # Add pagination and ordering
            query += " " + where
            query += " ORDER BY e.last_name, e.first_name LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            employees = [dict(row) for row in cursor.fetchall()]

            return employees, total_count

    @lru_cache(maxsize=1)
    def _get_column_configuration(self) -> list[dict[str, Any]]:
        """Get column configuration for dynamic columns"""
        with self.db as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT column_name, is_visible, display_order FROM column_configurations WHERE is_visible = 1 ORDER BY display_order"
            )
            columns = [
                {
                    "column_name": row[0],
                    "is_visible": bool(row[1]),
                    "display_order": row[2],
                }
                for row in cursor.fetchall()
            ]
            return columns
