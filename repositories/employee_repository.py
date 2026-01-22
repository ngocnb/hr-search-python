from typing import Any, Dict, List
from urllib.parse import parse_qs
from utils.helpers import Helpers


class EmployeeRepository:
    def __init__(self, db):
        self.db = db

    def handle_employee_search(self, params: dict):
        print("Search Parameters:", params)
        # Parse optional parameters
        search_query = params.get("q", [""])[0].strip()
        company_ids = params.get("company_ids", [])
        department_ids = params.get("department_ids", [])
        position_ids = params.get("position_ids", [])
        locations = params.get("locations", [])
        statuses = params.get("statuses", [])
        limit = min(int(params.get("limit", [50])[0]), 100)
        offset = (int(params.get("page", [1])[0]) - 1) * limit

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

            # Get column configuration
            columns = self._get_column_configuration()

            # Format response with dynamic columns
            formatted_employees = []
            for employee in employees:
                formatted_employee = {}
                for column in columns:
                    if column["column_name"] in employee:
                        formatted_employee[column["column_name"]] = employee[
                            column["column_name"]
                        ]
                formatted_employees.append(formatted_employee)

            response = {
                "employees": formatted_employees,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_count,
                },
            }

            return response
        except Exception as e:
            print("Error during employee search:", e)
            raise

    def _search_employees(
        self,
        company_ids: List[int],
        search_query: str,
        department_ids: List[int],
        position_ids: List[int],
        locations: List[str],
        statuses: List[str],
        limit: int,
        offset: int,
    ) -> tuple:
        """Search employees with filters"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Build base query with joins
        query = """
            SELECT e.id, e.first_name, e.last_name, e.email, e.location, e.phone, e.status, e.company_id,
                   d.name as department, e.department_id as department_id, p.title as position, e.position_id as position_id
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.id
            LEFT JOIN positions p ON e.position_id = p.id
        """
        params = []
        where = "WHERE 1=1"

        # Add search conditions
        if search_query:
            where += (
                " AND (e.first_name LIKE ? OR e.last_name LIKE ? OR e.email LIKE ?)"
            )
            search_param = f"%{search_query}%"
            params.extend([search_param, search_param, search_param])

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
            location_conditions = " OR ".join(["e.location LIKE ?"] * len(locations))
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

        print("Final Query:", query)
        print("With Parameters:", params)
        cursor.execute(query, params)
        employees = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return employees, total_count

    def _get_column_configuration(self) -> List[Dict[str, Any]]:
        """Get column configuration for dynamic columns"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT column_name, is_visible, display_order FROM column_configurations WHERE is_visible = 1 ORDER BY display_order"
        )
        columns = [
            {"column_name": row[0], "is_visible": bool(row[1]), "display_order": row[2]}
            for row in cursor.fetchall()
        ]
        conn.close()
        return columns
