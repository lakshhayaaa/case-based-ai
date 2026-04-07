import psycopg2
import os
from dotenv import load_dotenv
from database.db_connection import get_connection
# Load environment variables from .env file
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

def chunk_text(text, chunk_size=200, overlap=50):
    words = text.split()
    chunks = []
    start=0
    chunk_id=0
    while start<len(words):
        end=start+chunk_size
        chunk=words[start:end]
        chunks.append(( " ".join(chunk), chunk_id ))
        start+=chunk_size-overlap
        chunk_id+=1
    return chunks

conn=get_connection()
cur=conn.cursor()
# Fetch all cases
cur.execute("SELECT case_id, case_text FROM entrepreneurial_cases;")
cases = cur.fetchall()

print(f"Found {len(cases)} cases")

total_chunks = 0

# Loop through each case
for case_id, case_text in cases:
    chunks = chunk_text(case_text)

    # Insert each chunk
    for chunk_text_value, chunk_order in chunks:
        cur.execute(
            """
            INSERT INTO case_chunks (case_id, chunk_text, chunk_order)
            VALUES (%s, %s, %s);
            """,
            (case_id, chunk_text_value, chunk_order)
        )

    total_chunks += len(chunks)

# Save changes
conn.commit()

print(f"Inserted {total_chunks} chunks!")

# Close connection
cur.close()
conn.close()