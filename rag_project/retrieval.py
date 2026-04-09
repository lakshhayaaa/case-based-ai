from sentence_transformers import SentenceTransformer
import chromadb

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Connect to SAME ChromaDB as Step 5
client = chromadb.PersistentClient(
    settings=chromadb.Settings(
        persist_directory="/Users/akshayav/Desktop/case-based-ai/chroma_db"
    )
)

collection = client.get_collection(name="case_chunks")

def retrieve(query, top_k=5):
    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results

# Test
if __name__ == "__main__":
    query = "How did ITC grow?"
    results = retrieve(query)

    print("\nTop results:\n")
    for i, doc in enumerate(results["documents"][0]):
        print(f"{i+1}. {doc}\n")