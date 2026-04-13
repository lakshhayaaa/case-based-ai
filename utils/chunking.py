import psycopg2
import os
from dotenv import load_dotenv
from database.db_connection import get_connection
import re
# Load environment variables from .env file
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

import re

def chunk_text(text, chunk_size=100, overlap=20):
    # Split into sentences
    sentences = re.split(r'(?<=[.!?]) +', text)

    chunks = []
    current_chunk = []
    current_length = 0
    chunk_id = 0

    for sentence in sentences:
        words = sentence.split()
        sentence_length = len(words)

        # If adding this sentence stays within limit
        if current_length + sentence_length <= chunk_size:
            current_chunk.append(sentence)
            current_length += sentence_length
        else:
            # Save current chunk
            chunks.append((" ".join(current_chunk), chunk_id))
            chunk_id += 1

            # Keep overlap (last 2 sentences)
            overlap_sentences = current_chunk[-2:] if len(current_chunk) >= 2 else current_chunk
            current_chunk = overlap_sentences.copy()
            current_length = sum(len(s.split()) for s in current_chunk)

            # Add new sentence
            current_chunk.append(sentence)
            current_length += sentence_length

    # Add last chunk
    if current_chunk:
        chunks.append((" ".join(current_chunk), chunk_id))

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