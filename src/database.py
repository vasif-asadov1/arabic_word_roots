import sqlite3
import os


# Get the absolute path of the directory containing this script (src/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Build the path to the data folder dynamically
DB_NAME = os.path.join(BASE_DIR, "..", "data", "roots.sqlite3")

def init_db():
    # Connect to the database (this creates the file if it doesn't exist)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create the roots table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            root_arabic TEXT NOT NULL,
            meaning_english TEXT,
            meaning_turkish TEXT
        )
    ''')

    # Sample data for initial testing
    sample_roots = [
        ("ك ت ب", "writing, to write", "yazmak"),
        ("ق ر أ", "reading, to read", "okumak"),
        ("س م ع", "hearing, to listen", "işitmek, duymak"),
        ("ع ل م", "knowing, knowledge", "bilmek, ilim"),
        ("ر ح م", "mercy, compassion", "merhamet etmek, acımak")
    ]

    # Check if table is empty before inserting to avoid duplicates on multiple runs
    cursor.execute("SELECT COUNT(*) FROM roots")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO roots (root_arabic, meaning_english, meaning_turkish)
            VALUES (?, ?, ?)
        ''', sample_roots)
        print("Database created and sample roots inserted successfully.")
    else:
        print("Database already exists and contains data.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()