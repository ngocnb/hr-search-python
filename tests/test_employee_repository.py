import os
import sys
import tempfile
import unittest
from typing import List
from database import Database
from repositories.employee_repository import EmployeeRepository

# Ensure helpers module is importable despite its package path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UTILS_DIR = os.path.join(ROOT_DIR, "utils")
if UTILS_DIR not in sys.path:
    sys.path.insert(0, UTILS_DIR)


def _get_id(db: Database, table: str, column: str, value: str) -> int:
    """Helper to fetch an id from a table by column value."""
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM {table} WHERE {column} = ?", (value,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


class TestEmployeeRepository(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create isolated temp database file
        cls.temp_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        cls.db = Database(db_path=cls.temp_db_file.name)
        cls.db.create_sample_data()

        cls.repo = EmployeeRepository(cls.db)
        # Inject database instance
        cls.repo.db = cls.db

        # Cache commonly used IDs
        cls.tech_corp_id = _get_id(cls.db, "companies", "name", "Tech Corp")
        cls.finance_ltd_id = _get_id(cls.db, "companies", "name", "Finance Ltd")
        cls.hr_dept_id = _get_id(cls.db, "departments", "name", "HR")
        cls.finance_dept_id = _get_id(cls.db, "departments", "name", "Finance")
        cls.head_nurse_position_id = _get_id(cls.db, "positions", "title", "Head Nurse")

    @classmethod
    def tearDownClass(cls):
        # Clean up temp database file
        try:
            os.unlink(cls.temp_db_file.name)
        except OSError:
            pass

    def test_search_by_company_and_status(self):
        employees, total = self.repo._search_employees(
            company_ids=[self.tech_corp_id],
            search_query="",
            department_ids=[],
            position_ids=[],
            locations=[],
            statuses=["Active"],
            limit=10,
            offset=0,
        )

        self.assertEqual(total, 3)
        self.assertTrue(all(emp["status"] == "Active" for emp in employees))

    def test_text_search_matches_multiple_fields(self):
        employees, total = self.repo._search_employees(
            company_ids=[self.tech_corp_id],
            search_query="john",
            department_ids=[],
            position_ids=[],
            locations=[],
            statuses=[],
            limit=10,
            offset=0,
        )

        self.assertEqual(total, 2)  # John (first name) + Mike Johnson (last name)
        last_names = {emp["last_name"].lower() for emp in employees}
        self.assertIn("doe", last_names)
        self.assertIn("johnson", last_names)

    def test_filter_by_department(self):
        employees, total = self.repo._search_employees(
            company_ids=[self.tech_corp_id],
            search_query="",
            department_ids=[self.hr_dept_id],
            position_ids=[],
            locations=[],
            statuses=[],
            limit=10,
            offset=0,
        )

        print("Employees Found:", employees)

        self.assertEqual(total, 1)
        self.assertEqual(employees[0]["department"], "HR")

    def test_filter_by_location(self):
        employees, total = self.repo._search_employees(
            company_ids=[self.finance_ltd_id],
            search_query="",
            department_ids=[],
            position_ids=[],
            locations=["Chicago"],
            statuses=[],
            limit=10,
            offset=0,
        )

        self.assertEqual(total, 2)
        self.assertTrue(all("Chicago" in emp["location"] for emp in employees))

    def test_filter_by_position_and_status(self):
        employees, total = self.repo._search_employees(
            company_ids=[],
            search_query="",
            department_ids=[],
            position_ids=[self.head_nurse_position_id],
            locations=[],
            statuses=["Not started"],
            limit=10,
            offset=0,
        )

        self.assertEqual(total, 1)
        self.assertEqual(employees[0]["status"], "Not started")
        self.assertEqual(employees[0]["position"], "Head Nurse")

    def test_pagination_limit_and_offset(self):
        employees_page1, total1 = self.repo._search_employees(
            company_ids=[self.tech_corp_id],
            search_query="",
            department_ids=[],
            position_ids=[],
            locations=[],
            statuses=[],
            limit=1,
            offset=0,
        )

        employees_page2, total2 = self.repo._search_employees(
            company_ids=[self.tech_corp_id],
            search_query="",
            department_ids=[],
            position_ids=[],
            locations=[],
            statuses=[],
            limit=1,
            offset=1,
        )

        self.assertEqual(total1, 3)
        self.assertEqual(total2, 3)
        self.assertEqual(len(employees_page1), 1)
        self.assertEqual(len(employees_page2), 1)
        self.assertNotEqual(
            employees_page1[0]["id"],
            employees_page2[0]["id"],
            "Pagination should return different records",
        )

    def test_column_configuration_returns_visible_columns(self):
        columns = self.repo._get_column_configuration()
        column_names: List[str] = [col["column_name"] for col in columns]

        expected_columns = [
            "first_name",
            "last_name",
            "email",
            "department",
            "position",
            "location",
            "phone",
            "status",
        ]

        self.assertEqual(column_names, expected_columns)
        self.assertTrue(all(col["is_visible"] for col in columns))
        # Ensure sorted by display_order asc
        display_orders = [col["display_order"] for col in columns]
        self.assertEqual(display_orders, sorted(display_orders))


if __name__ == "__main__":
    unittest.main()
