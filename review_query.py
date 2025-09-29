import chromadb
from sentence_transformers import SentenceTransformer

# -----------------------------
# 1. Connect to the same persistent ChromaDB folder
# -----------------------------
client = chromadb.PersistentClient(path="D:/hacksih/chroma_store")

# -----------------------------
# 2. Get the collection
# -----------------------------
collection = client.get_or_create_collection("corporate_bills_reviews")

# -----------------------------
# 3. Load embedding model (must be the same as in setup)
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# 4. Example query
# -----------------------------
query = "impact on small businesses"
query_emb = model.encode(query).tolist()

# -----------------------------
# 5. Query the DB
# -----------------------------
results = collection.query(query_embeddings=[query_emb], n_results=3)

# -----------------------------
# 6. Print results
# -----------------------------
print("\nQuery:", query)
for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
    print(f"- {doc} (Bill: {meta['bill']}, Sentiment: {meta['sentiment']}, Time: {meta['time']})")
