import sys
import os

# Adds the parent directory to the search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import Database


def create_fts_index(db = None):
    if db is None:
        db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()

    # FTS5 virtual table for fast text search on names/emails
    print("Creating FTS index...")
    cursor.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS employees_fts USING fts5(
            first_name, last_name, email,
            content='employees',
            content_rowid='id',
            tokenize='trigram'
        )
        """
    )

    # Triggers to keep FTS index in sync
    print("Creating triggers for FTS index...")
    cursor.execute(
        """
        CREATE TRIGGER IF NOT EXISTS employees_ai AFTER INSERT ON employees BEGIN
            INSERT INTO employees_fts(rowid, first_name, last_name, email)
            VALUES (new.id, new.first_name, new.last_name, new.email);
        END;
        """
    )
    cursor.execute(
        """
        CREATE TRIGGER IF NOT EXISTS employees_ad AFTER DELETE ON employees BEGIN
            INSERT INTO employees_fts(employees_fts, rowid, first_name, last_name, email)
            VALUES('delete', old.id, old.first_name, old.last_name, old.email);
        END;
        """
    )
    cursor.execute(
        """
        CREATE TRIGGER IF NOT EXISTS employees_au AFTER UPDATE ON employees BEGIN
            INSERT INTO employees_fts(employees_fts, rowid, first_name, last_name, email)
            VALUES('delete', old.id, old.first_name, old.last_name, old.email);
            INSERT INTO employees_fts(rowid, first_name, last_name, email)
            VALUES (new.id, new.first_name, new.last_name, new.email);
        END;
        """
    )

    # Backfill FTS index for existing rows
    print("Backfilling FTS index...")
    cursor.execute(
        """
        INSERT INTO employees_fts(rowid, first_name, last_name, email)
        SELECT id, first_name, last_name, email FROM employees;
        """
    )

    conn.commit()
    conn.close()
    print("FTS index and triggers created.")


def drop_fts_index():
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()

    print("Dropping FTS index and triggers...")
    cursor.execute("DROP TRIGGER IF EXISTS employees_ai;")
    cursor.execute("DROP TRIGGER IF EXISTS employees_ad;")
    cursor.execute("DROP TRIGGER IF EXISTS employees_au;")
    cursor.execute("DROP TABLE IF EXISTS employees_fts;")

    conn.commit()
    conn.close()
    print("FTS index and triggers dropped.")


if __name__ == "__main__":
    # create or drop the FTS index from command line
    if len(sys.argv) != 2:
        print("Usage: python database_fts.py [create|drop]")
        sys.exit(1)

    if sys.argv[1] == "create":
        create_fts_index()
    elif sys.argv[1] == "drop":
        drop_fts_index()
    else:
        print("Usage: python database_fts.py [create|drop]")
        sys.exit(1)
