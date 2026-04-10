from sentence_transformers import SentenceTransformer
import chromadb
from dotenv import load_dotenv
import os
load_dotenv()

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')
model.max_seq_length = 512  # Ensure the model can handle longer texts if needed
os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Disable parallelism to avoid warnings
# Connect to SAME ChromaDB as Step 5
client = chromadb.PersistentClient(
    settings=chromadb.Settings(
        persist_directory=os.getenv("chroma_dir")
    )
)

collection = client.get_collection(name="case_chunks")

def retrieve(query_id, query, top_k=5):
    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    #Return chunk ids + texts+ case_ids together
    chunk_ids = [int(id) for id in results["ids"][0]]
    chunk_texts = results["documents"][0]
    case_ids = [metadata["case_id"] for metadata in results["metadatas"][0]]


    return {"chunk_ids": chunk_ids, "chunk_texts": chunk_texts, "case_ids": case_ids}
