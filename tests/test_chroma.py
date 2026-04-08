import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

client = chromadb.PersistentClient(
    settings=chromadb.Settings(persist_directory="/Users/lakshayaa/Desktop/case-based-ai/chroma_db")
)
print("Collections in test:", client.list_collections())
collection = client.get_collection(name="case_chunks")

query = "how did the startup increase revenue?"

query_embedding = model.encode(query)

results = collection.query(
    query_embeddings=[query_embedding.tolist()],
    n_results=3
)

print("\n🔍 Query:", query)
print("\n📄 Top results:\n")

for doc in results["documents"][0]:
    print("-", doc[:200], "\n")
