"""
Seed script to insert 1 million employee records for performance testing
Usage: python3 utils/seed_large_dataset.py [--records=1000000]
"""

import argparse
import time
import random
import sys
import os
import json

# Adds the parent directory to the search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import Database


# Load data from JSON files
def load_json_data(filename):
    """Load data from JSON file in utils directory"""
    file_path = os.path.join(os.path.dirname(__file__), filename)
    with open(file_path, "r") as f:
        return json.load(f)


# Sample data pools loaded from JSON files
FIRST_NAMES = load_json_data("first-names.json")
LAST_NAMES = load_json_data("last-names.json")
LOCATIONS = load_json_data("locations.json")

DEPARTMENTS = [
    "Engineering",
    "HR",
    "Medical",
    "Nursing",
    "Accounting",
    "Finance",
    "Sales",
    "Marketing",
    "Operations",
    "IT",
    "Support",
    "Legal",
    "Research",
    "Development",
    "Quality",
    "Production",
    "Logistics",
]

POSITIONS = [
    "Senior Developer",
    "DevOps Engineer",
    "HR Manager",
    "Doctor",
    "Head Nurse",
    "Senior Accountant",
    "Financial Analyst",
    "Sales Manager",
    "Marketing Manager",
    "Operations Manager",
    "IT Manager",
    "Support Lead",
    "Junior Developer",
    "Nurse",
    "Accountant",
    "Analyst",
    "Coordinator",
]

STATUSES = ["Active", "Not started", "Terminated"]


def generate_email(first_name: str, last_name: str, company_name: str) -> str:
    """Generate a unique email address"""
    domain = company_name.lower().replace(" ", "").replace("'", "")
    return f"{first_name.lower()}.{last_name.lower()}@{domain}.com"


def seed_large_dataset(num_records: int = 1000000):
    """Insert large dataset of employee records"""
    print(f"Starting to seed {num_records:,} employee records...")
    print("This may take several minutes...\n")

    db = Database(db_path="hr_search.db")

    conn = db.get_connection()
    cursor = conn.cursor()

    # Get or create companies
    companies = ["Tech Corp", "Health Inc", "Finance Ltd", "RetailCo", "TravelPlus"]
    cursor.executemany(
        "INSERT OR IGNORE INTO companies (name) VALUES (?)", [(c,) for c in companies]
    )

    cursor.execute("SELECT id, name FROM companies")
    company_dict = {row[1]: row[0] for row in cursor.fetchall()}
    company_ids = list(company_dict.values())

    # Create departments for each company
    for company_id in company_ids:
        for dept in DEPARTMENTS:
            cursor.execute(
                "INSERT OR IGNORE INTO departments (company_id, name) VALUES (?, ?)",
                (company_id, dept),
            )

    # Create positions for each company
    for company_id in company_ids:
        for pos in POSITIONS:
            cursor.execute(
                "INSERT OR IGNORE INTO positions (company_id, title) VALUES (?, ?)",
                (company_id, pos),
            )

    # Get department and position IDs
    cursor.execute("SELECT id, company_id FROM departments")
    dept_list = [(row[0], row[1]) for row in cursor.fetchall()]

    cursor.execute("SELECT id, company_id FROM positions")
    pos_list = [(row[0], row[1]) for row in cursor.fetchall()]

    conn.commit()
    conn.close()

    # Generate and insert employee records in batches
    batch_size = 10000
    total_inserted = 0
    start_time = time.time()

    print("Generating and inserting employee records in batches...\n")

    for batch_num in range(0, num_records, batch_size):
        batch = []
        batch_end = min(batch_num + batch_size, num_records)

        for i in range(batch_num, batch_end):
            company_id = random.choice(company_ids)
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)

            # Find departments and positions for this company
            company_depts = [d[0] for d in dept_list if d[1] == company_id]
            company_pos = [p[0] for p in pos_list if p[1] == company_id]

            department_id = random.choice(company_depts) if company_depts else None
            position_id = random.choice(company_pos) if company_pos else None

            email = generate_email(
                first_name,
                last_name,
                [k for k, v in company_dict.items() if v == company_id][0],
            )
            location = random.choice(LOCATIONS)
            phone = f"555-{random.randint(1000, 9999)}"
            status = random.choice(STATUSES)

            batch.append(
                (
                    company_id,
                    first_name,
                    last_name,
                    email,
                    department_id,
                    position_id,
                    location,
                    phone,
                    status,
                )
            )

        # Insert batch
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.executemany(
            """
            INSERT INTO employees 
            (company_id, first_name, last_name, email, department_id, position_id, location, phone, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            batch,
        )
        conn.commit()
        conn.close()

        total_inserted = batch_end
        elapsed = time.time() - start_time
        rate = total_inserted / elapsed if elapsed > 0 else 0

        progress_pct = (total_inserted / num_records) * 100
        print(
            f"Progress: {progress_pct:.1f}% ({total_inserted:,}/{num_records:,} records) - "
            f"Rate: {rate:.0f} records/sec - Elapsed: {elapsed:.1f}s"
        )

    total_time = time.time() - start_time
    print(
        f"\n✓ Successfully inserted {total_inserted:,} employee records in {total_time:.1f} seconds"
    )
    print(f"  Average rate: {total_inserted / total_time:.0f} records/sec\n")

    # Print statistics
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM employees")
    total_employees = cursor.fetchone()[0]
    print(f"Database Statistics:")
    print(f"  Total employees: {total_employees:,}")
    print(f"  Total companies: {len(company_ids)}")
    print(f"  Database file: hr_search.db")
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Seed the database with large dataset of employee records"
    )
    parser.add_argument(
        "--records",
        type=int,
        default=1000000,
        help="Number of employee records to insert (default: 1,000,000)",
    )

    args = parser.parse_args()
    seed_large_dataset(args.records)
