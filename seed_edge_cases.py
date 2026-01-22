"""
Seed script for security and edge case testing
Inserts abnormal data to test application robustness, input validation, and security
Usage: python3 seed_edge_cases.py [--delete-first]
"""

import argparse
from database import Database


# Edge case and security test data
EDGE_CASES = [
    # SQL Injection attempts
    {
        "company_id": 1,
        "first_name": "Robert'; DROP TABLE employees; --",
        "last_name": "Smith",
        "email": "robert.smith@test.com",
        "department_id": 1,
        "position_id": 1,
        "location": "New York",
        "phone": "555-0001",
        "status": "Active",
        "description": "SQL Injection in first_name",
    },
    {
        "company_id": 1,
        "first_name": "John",
        "last_name": "O'Brien' OR '1'='1",
        "email": "john.obrien@test.com",
        "department_id": 1,
        "position_id": 1,
        "location": "New York",
        "phone": "555-0002",
        "status": "Active",
        "description": "SQL Injection in last_name",
    },
    {
        "company_id": 1,
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "test@example.com' OR '1'='1",
        "department_id": 1,
        "position_id": 1,
        "location": "New York",
        "phone": "555-0003",
        "status": "Active",
        "description": "SQL Injection in email",
    },
    # XSS attempts
    {
        "company_id": 1,
        "first_name": "<script>alert('XSS')</script>",
        "last_name": "Smith",
        "email": "xss.test@test.com",
        "department_id": 1,
        "position_id": 1,
        "location": "New York",
        "phone": "555-0004",
        "status": "Active",
        "description": "XSS in first_name",
    },
    {
        "company_id": 1,
        "first_name": "John",
        "last_name": "<img src=x onerror=alert('XSS')>",
        "email": "xss.test2@test.com",
        "department_id": 1,
        "position_id": 1,
        "location": "New York",
        "phone": "555-0005",
        "status": "Active",
        "description": "XSS in last_name",
    },
    {
        "company_id": 1,
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "<iframe src='javascript:alert(1)'></iframe>",
        "department_id": 1,
        "position_id": 1,
        "location": "New York",
        "phone": "555-0006",
        "status": "Active",
        "description": "XSS in email",
    },
    # Very long strings
    {
        "company_id": 1,
        "first_name": "A" * 255,
        "last_name": "Smith",
        "email": "longname@test.com",
        "department_id": 1,
        "position_id": 1,
        "location": "New York",
        "phone": "555-0007",
        "status": "Active",
        "description": "Very long first_name (255 chars)",
    },
    {
        "company_id": 1,
        "first_name": "John",
        "last_name": "B" * 255,
        "email": "longlast@test.com",
        "department_id": 1,
        "position_id": 1,
        "location": "New York",
        "phone": "555-0008",
        "status": "Active",
        "description": "Very long last_name (255 chars)",
    },
    {
        "company_id": 1,
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "C" * 200 + "@test.com",
        "department_id": 1,
        "position_id": 1,
        "location": "New York",
        "phone": "555-0009",
        "status": "Active",
        "description": "Very long email (200+ chars)",
    },
    # Special characters
    {
        "company_id": 1,
        "first_name": "José",
        "last_name": "García",
        "email": "jose.garcia@test.com",
        "department_id": 1,
        "position_id": 1,
        "location": "Madrid",
        "phone": "555-0010",
        "status": "Active",
        "description": "Accented characters (Spanish)",
    },
    {
        "company_id": 1,
        "first_name": "李",
        "last_name": "明",
        "email": "li.ming@test.com",
        "department_id": 1,
        "position_id": 1,
        "location": "Beijing",
        "phone": "555-0011",
        "status": "Active",
        "description": "Chinese characters",
    },
    {
        "company_id": 1,
        "first_name": "محمد",
        "last_name": "أحمد",
        "email": "muhammad@test.com",
        "department_id": 1,
        "position_id": 1,
        "location": "Dubai",
        "phone": "555-0012",
        "status": "Active",
        "description": "Arabic characters",
    },
    {
        "company_id": 1,
        "first_name": "Владимир",
        "last_name": "Путин",
        "email": "vladimir@test.com",
        "department_id": 1,
        "position_id": 1,
        "location": "Moscow",
        "phone": "555-0013",
        "status": "Active",
        "description": "Cyrillic characters",
    },
    # Special symbols and operators
    {
        "company_id": 1,
        "first_name": "Test!@#$%",
        "last_name": "^&*()_+-=[]{}",
        "email": "symbols@test.com",
        "department_id": 1,
        "position_id": 1,
        "location": "New York",
        "phone": "555-0014",
        "status": "Active",
        "description": "Special symbols in names",
    },
    {
        "company_id": 1,
        "first_name": "Test",
        "last_name": "Name",
        "email": "test+tag@test.com",
        "department_id": 1,
        "position_id": 1,
        "location": "New York",
        "phone": "555-0015",
        "status": "Active",
        "description": "Plus sign in email (valid but edge case)",
    },
    # Invalid/unusual email formats
    {
        "company_id": 1,
        "first_name": "NoEmail",
        "last_name": "User",
        "email": "invalid.email",
        "department_id": 1,
        "position_id": 1,
        "location": "New York",
        "phone": "555-0016",
        "status": "Active",
        "description": "Email without domain",
    },
    {
        "company_id": 1,
        "first_name": "DoubleAt",
        "last_name": "User",
        "email": "test@@example.com",
        "department_id": 1,
        "position_id": 1,
        "location": "New York",
        "phone": "555-0017",
        "status": "Active",
        "description": "Double @ in email",
    },
    # Empty and whitespace strings
    {
        "company_id": 1,
        "first_name": " ",
        "last_name": "Smith",
        "email": "whitespace@test.com",
        "department_id": 1,
        "position_id": 1,
        "location": "New York",
        "phone": "555-0018",
        "status": "Active",
        "description": "Whitespace in first_name",
    },
    {
        "company_id": 1,
        "first_name": "John",
        "last_name": "   \t\n   ",
        "email": "whitespace2@test.com",
        "department_id": 1,
        "position_id": 1,
        "location": "New York",
        "phone": "555-0019",
        "status": "Active",
        "description": "Tabs and newlines in last_name",
    },
    # Null-like strings
    {
        "company_id": 1,
        "first_name": "null",
        "last_name": "User",
        "email": "null@test.com",
        "department_id": 1,
        "position_id": 1,
        "location": "New York",
        "phone": "555-0020",
        "status": "Active",
        "description": "String 'null' in first_name",
    },
    {
        "company_id": 1,
        "first_name": "John",
        "last_name": "NULL",
        "email": "nulltest@test.com",
        "department_id": 1,
        "position_id": 1,
        "location": "New York",
        "phone": "555-0021",
        "status": "Active",
        "description": "String 'NULL' in last_name",
    },
    # Boundary values and duplicates
    {
        "company_id": 1,
        "first_name": "John",
        "last_name": "Smith",
        "email": "john.smith@test.com",
        "department_id": 1,
        "position_id": 1,
        "location": "New York",
        "phone": "555-0022",
        "status": "Active",
        "description": "First duplicate record",
    },
    {
        "company_id": 1,
        "first_name": "John",
        "last_name": "Smith",
        "email": "john.smith@test.com",
        "department_id": 1,
        "position_id": 1,
        "location": "New York",
        "phone": "555-0022",
        "status": "Active",
        "description": "Exact duplicate record",
    },
    # Command injection attempts
    {
        "company_id": 1,
        "first_name": "Command",
        "last_name": "$(whoami)",
        "email": "command@test.com",
        "department_id": 1,
        "position_id": 1,
        "location": "New York",
        "phone": "555-0023",
        "status": "Active",
        "description": "Command substitution attempt",
    },
    {
        "company_id": 1,
        "first_name": "Injection",
        "last_name": "`cat /etc/passwd`",
        "email": "injection@test.com",
        "department_id": 1,
        "position_id": 1,
        "location": "New York",
        "phone": "555-0024",
        "status": "Active",
        "description": "Backtick command execution",
    },
    # Boundary status values
    {
        "company_id": 1,
        "first_name": "UnknownStatus",
        "last_name": "User",
        "email": "unknown@test.com",
        "department_id": 1,
        "position_id": 1,
        "location": "New York",
        "phone": "555-0025",
        "status": "UnknownStatus",
        "description": "Unknown status value",
    },
    {
        "company_id": 1,
        "first_name": "EmptyStatus",
        "last_name": "User",
        "email": "emptystatus@test.com",
        "department_id": 1,
        "position_id": 1,
        "location": "New York",
        "phone": "555-0026",
        "status": "",
        "description": "Empty status value",
    },
    # Unicode normalization edge cases
    {
        "company_id": 1,
        "first_name": "Café",  # NFC normalization
        "last_name": "Naïve",
        "email": "unicode@test.com",
        "department_id": 1,
        "position_id": 1,
        "location": "New York",
        "phone": "555-0027",
        "status": "Active",
        "description": "Unicode composed characters",
    },
]


def seed_edge_cases(delete_first: bool = False, db: Database | None = None):
    """Insert edge case and security test data

    Args:
        delete_first: When True, remove existing TestCorp employees before inserting
        db: Optional Database instance (useful for tests with temp DB). If not
            provided, defaults to hr_search.db.

    Returns:
        dict: Summary with inserted, skipped, company_id, department_id, position_id
    """
    db = db or Database(db_path="hr_search.db")

    conn = db.get_connection()
    cursor = conn.cursor()

    # Get or create base company for testing
    cursor.execute("INSERT OR IGNORE INTO companies (name) VALUES (?)", ("TestCorp",))
    cursor.execute("SELECT id FROM companies WHERE name = ?", ("TestCorp",))
    company_id = cursor.fetchone()[0]

    # Get or create test department and position
    cursor.execute(
        "INSERT OR IGNORE INTO departments (company_id, name) VALUES (?, ?)",
        (company_id, "Testing"),
    )
    cursor.execute(
        "SELECT id FROM departments WHERE company_id = ? AND name = ?",
        (company_id, "Testing"),
    )
    dept_id = cursor.fetchone()[0]

    cursor.execute(
        "INSERT OR IGNORE INTO positions (company_id, title) VALUES (?, ?)",
        (company_id, "QA Tester"),
    )
    cursor.execute(
        "SELECT id FROM positions WHERE company_id = ? AND title = ?",
        (company_id, "QA Tester"),
    )
    pos_id = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    # Delete existing edge case records if requested
    if delete_first:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM employees WHERE company_id = (SELECT id FROM companies WHERE name = 'TestCorp')"
        )
        conn.commit()
        conn.close()
        print("Deleted existing edge case records.\n")

    # Insert edge case records
    conn = db.get_connection()
    cursor = conn.cursor()

    print(f"Inserting {len(EDGE_CASES)} edge case and security test records...\n")

    inserted = 0
    skipped = 0

    for i, case in enumerate(EDGE_CASES, 1):
        try:
            cursor.execute(
                """
                INSERT INTO employees 
                (company_id, first_name, last_name, email, department_id, position_id, location, phone, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    company_id,
                    case["first_name"],
                    case["last_name"],
                    case["email"],
                    dept_id,
                    pos_id,
                    case["location"],
                    case["phone"],
                    case["status"],
                ),
            )
            inserted += 1
            print(f"✓ [{i:2d}] {case['description']}")
        except Exception as e:
            skipped += 1
            print(f"✗ [{i:2d}] {case['description']} - Error: {str(e)[:50]}")

    conn.commit()
    conn.close()

    print(f"\n{'=' * 70}")
    print(f"Edge Case Data Seeding Complete")
    print(f"{'=' * 70}")
    print(f"✓ Successfully inserted: {inserted} records")
    print(f"✗ Skipped/Failed: {skipped} records")
    print(f"\nThese edge cases test:")
    print(f"  • SQL Injection attempts")
    print(f"  • XSS payload handling")
    print(f"  • Long string boundaries")
    print(f"  • Unicode and special characters")
    print(f"  • Invalid email formats")
    print(f"  • Empty and whitespace values")
    print(f"  • Duplicate records")
    print(f"  • Command injection attempts")
    print(f"  • Null-like string handling")
    print(f"  • Unicode normalization")

    return {
        "inserted": inserted,
        "skipped": skipped,
        "company_id": company_id,
        "department_id": dept_id,
        "position_id": pos_id,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Seed database with edge case and security test data"
    )
    parser.add_argument(
        "--delete-first",
        action="store_true",
        help="Delete existing edge case records before inserting new ones",
    )

    args = parser.parse_args()
    seed_edge_cases(delete_first=args.delete_first)
