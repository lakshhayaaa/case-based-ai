from sentence_transformers import SentenceTransformer
from database.db_connection import get_connection

# Load MiniLM model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Connect to DB
conn = get_connection()
cur = conn.cursor()

# Fetch all chunks
cur.execute("SELECT chunk_id, chunk_text FROM case_chunks;")
chunks = cur.fetchall()

print(f"Found {len(chunks)} chunks")

# Generate embeddings and store
for chunk_id, chunk_text in chunks:
    embedding = model.encode(chunk_text)

    embedding_str = ",".join(map(str, embedding.tolist()))

    cur.execute(
        """
        UPDATE case_chunks
        SET embedding_vector = %s
        WHERE chunk_id = %s;
        """,
        (embedding_str, chunk_id)
    )

conn.commit()

print(" Embeddings generated and stored!")

cur.close()
conn.close()