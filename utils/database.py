"""
Database schema and setup for HR Employee Search Microservice
"""

import sqlite3


class Database:
    def __init__(self, db_path: str = "hr_search.db"):
        self.db_path = db_path
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with proper settings"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def __enter__(self) -> sqlite3.Connection:
        """Context manager entry - returns a connection"""
        self._conn = self.get_connection()
        return self._conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures connection is closed"""
        if hasattr(self, "_conn"):
            if exc_type is None:
                # No exception, commit the transaction
                self._conn.commit()
            else:
                # Exception occurred, rollback
                self._conn.rollback()
            self._conn.close()
            delattr(self, "_conn")
        return False  # Don't suppress exceptions

    def init_database(self):
        """Initialize database tables and indexes"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Companies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Departments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                company_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies (id)
            )
        """)

        # Positions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                company_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies (id)
            )
        """)

        # Employees table with indexes for performance
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT,
                department_id INTEGER,
                position_id INTEGER,
                location TEXT,
                phone TEXT,
                status TEXT DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies (id),
                FOREIGN KEY (department_id) REFERENCES departments (id),
                FOREIGN KEY (position_id) REFERENCES positions (id)
            )
        """)

        # Column configurations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS column_configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                column_name TEXT NOT NULL,
                is_visible BOOLEAN DEFAULT 1,
                display_order INTEGER DEFAULT 0,
                UNIQUE(column_name)
            )
        """)

        # Performance indexes for millions of records
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_employees_company_id ON employees(company_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_employees_name ON employees(first_name, last_name, email)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_employees_department ON employees(company_id, department_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_employees_position ON employees(company_id, position_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_employees_location ON employees(company_id, location)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_employees_search ON employees(company_id, first_name, last_name, email)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_employees_status ON employees(company_id, status)"
        )
        # Additional per-column indexes with NOCASE to optimize case-insensitive prefix searches
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_employees_first_name_nc ON employees(first_name COLLATE NOCASE)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_employees_last_name_nc ON employees(last_name COLLATE NOCASE)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_employees_email_nc ON employees(email COLLATE NOCASE)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_employees_location_nc ON employees(location COLLATE NOCASE)"
        )

        conn.commit()
        conn.close()

    def create_sample_data(self):
        """Create sample companies, departments, positions and employees for testing"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create sample companies
        companies = [("Tech Corp",), ("Health Inc",), ("Finance Ltd",)]
        cursor.executemany(
            "INSERT OR IGNORE INTO companies (name) VALUES (?)", companies
        )

        # Get company IDs
        cursor.execute("SELECT id, name FROM companies")
        companies_dict = {row[1]: row[0] for row in cursor.fetchall()}

        # Create departments for each company
        departments = [
            (companies_dict["Tech Corp"], "Engineering"),
            (companies_dict["Tech Corp"], "HR"),
            (companies_dict["Health Inc"], "Medical"),
            (companies_dict["Health Inc"], "Nursing"),
            (companies_dict["Finance Ltd"], "Accounting"),
            (companies_dict["Finance Ltd"], "Finance"),
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO departments (company_id, name) VALUES (?, ?)",
            departments,
        )

        # Create positions for each company
        positions = [
            (companies_dict["Tech Corp"], "Senior Developer"),
            (companies_dict["Tech Corp"], "DevOps Engineer"),
            (companies_dict["Tech Corp"], "HR Manager"),
            (companies_dict["Health Inc"], "Doctor"),
            (companies_dict["Health Inc"], "Head Nurse"),
            (companies_dict["Finance Ltd"], "Senior Accountant"),
            (companies_dict["Finance Ltd"], "Financial Analyst"),
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO positions (company_id, title) VALUES (?, ?)",
            positions,
        )

        # Get department and position IDs
        cursor.execute("SELECT id, name, company_id FROM departments")
        dept_dict = {(row[2], row[1]): row[0] for row in cursor.fetchall()}

        cursor.execute("SELECT id, title, company_id FROM positions")
        pos_dict = {(row[2], row[1]): row[0] for row in cursor.fetchall()}

        # Sample employees
        employees = [
            (
                companies_dict["Tech Corp"],
                "John",
                "Doe",
                "john@techcorp.com",
                dept_dict[(companies_dict["Tech Corp"], "Engineering")],
                pos_dict[(companies_dict["Tech Corp"], "Senior Developer")],
                "New York",
                "555-0101",
                "Active",
            ),
            (
                companies_dict["Tech Corp"],
                "Jane",
                "Smith",
                "jane@techcorp.com",
                dept_dict[(companies_dict["Tech Corp"], "Engineering")],
                pos_dict[(companies_dict["Tech Corp"], "DevOps Engineer")],
                "San Francisco",
                "555-0102",
                "Active",
            ),
            (
                companies_dict["Tech Corp"],
                "Mike",
                "Johnson",
                "mike@techcorp.com",
                dept_dict[(companies_dict["Tech Corp"], "HR")],
                pos_dict[(companies_dict["Tech Corp"], "HR Manager")],
                "New York",
                "555-0103",
                "Active",
            ),
            (
                companies_dict["Health Inc"],
                "Sarah",
                "Williams",
                "sarah@healthinc.com",
                dept_dict[(companies_dict["Health Inc"], "Medical")],
                pos_dict[(companies_dict["Health Inc"], "Doctor")],
                "Boston",
                "555-0201",
                "Active",
            ),
            (
                companies_dict["Health Inc"],
                "Robert",
                "Brown",
                "robert@healthinc.com",
                dept_dict[(companies_dict["Health Inc"], "Nursing")],
                pos_dict[(companies_dict["Health Inc"], "Head Nurse")],
                "Boston",
                "555-0202",
                "Not started",
            ),
            (
                companies_dict["Finance Ltd"],
                "Emily",
                "Davis",
                "emily@financeltd.com",
                dept_dict[(companies_dict["Finance Ltd"], "Accounting")],
                pos_dict[(companies_dict["Finance Ltd"], "Senior Accountant")],
                "Chicago",
                "555-0301",
                "Active",
            ),
            (
                companies_dict["Finance Ltd"],
                "David",
                "Miller",
                "david@financeltd.com",
                dept_dict[(companies_dict["Finance Ltd"], "Finance")],
                pos_dict[(companies_dict["Finance Ltd"], "Financial Analyst")],
                "Chicago",
                "555-0302",
                "Terminated",
            ),
        ]

        cursor.executemany(
            """
            INSERT OR IGNORE INTO employees 
            (company_id, first_name, last_name, email, department_id, position_id, location, phone, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            employees,
        )

        # Default column configurations
        all_columns = [
            "first_name",
            "last_name",
            "email",
            "department",
            "position",
            "location",
            "phone",
            "status",
        ]

        for i, column in enumerate(all_columns):
            cursor.execute(
                """
                INSERT OR IGNORE INTO column_configurations 
                (column_name, is_visible, display_order)
                VALUES (?, ?, ?)
            """,
                (column, True, i),
            )

        conn.commit()
        conn.close()
        print("Sample data created successfully!")


# Database instance
db = Database()

if __name__ == "__main__":
    # Create sample data for testing
    db.create_sample_data()
