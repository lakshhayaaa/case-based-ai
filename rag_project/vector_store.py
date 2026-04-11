import chromadb
import dotenv
from database.db_connection import get_connection
from dotenv import load_dotenv
import os

load_dotenv()

client=chromadb.PersistentClient(
    settings=chromadb.Settings(persist_directory=os.getenv("chroma_dir"))
)
collection = client.get_or_create_collection(name="case_chunks")

#connect to the database and fetch all the case chunks
conn=get_connection()
curr=conn.cursor()
curr.execute('''
             SELECT chunk_id,case_id,chunk_text,embedding_vector
             FROM case_chunks
             ''')
case_chunks=curr.fetchall()
print(f"Fetched {len(case_chunks)} case chunks from the database.")

#insert the case chunks into chromadb
for chunk_id,case_id,chunk_text,embedding_str in case_chunks:
    embedding_vector=list(map(float,embedding_str.split(',')))
    #upsert adds the document if it doesn't exist and updates it if it does, using the chunk_id as the unique identifier
    client.get_collection(name="case_chunks").upsert(
        documents=[chunk_text],
        metadatas=[{"case_id": case_id}],
        ids=[str(chunk_id)],
        embeddings=[embedding_vector]
    )
print("Inserted case chunks into chromadb.")
print("Collections after storing:", client.list_collections())