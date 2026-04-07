import csv
import os
import sys
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "entrepreneurial_cases.csv")

def main():
    print("🔌 Connecting to database...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print("✅ Connected!\n")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)

    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM entrepreneurial_cases;")
    count = cur.fetchone()[0]
    if count > 0:
        print(f"⚠️  Table already has {count} rows.")
        answer = input("Reload? (y/n): ")
        if answer.lower() != "y":
            print("👍 Already loaded!")
            cur.close()
            conn.close()
            return
        cur.execute("DELETE FROM entrepreneurial_cases;")

    print(f"📄 Reading CSV...")
    if not os.path.exists(CSV_PATH):
        print(f"❌ CSV not found at: {CSV_PATH}")
        print("   Make sure entrepreneurial_cases.csv is inside your /data folder.")
        sys.exit(1)

    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append((
                row["title"].strip(),
                row["source"].strip(),
                row["industry"].strip(),
                int(row["year"]) if row.get("year", "").strip() else None,
                row["case_text"].strip(),
            ))

    print(f"📄 Found {len(rows)} cases. Inserting...")

    execute_values(
        cur,
        "INSERT INTO entrepreneurial_cases (title, source, industry, year, case_text) VALUES %s",
        rows
    )
    conn.commit()
    print(f"✅ Inserted {len(rows)} cases!")

    cur.execute("SELECT case_id, title FROM entrepreneurial_cases LIMIT 3;")
    for r in cur.fetchall():
        print(f"  [{r[0]}] {r[1][:60]}")

    cur.close()
    conn.close()
    print("\n🎉 Done! Dataset loaded.\n")

if __name__ == "__main__":
    main()