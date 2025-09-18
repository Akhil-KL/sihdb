# review_query.py

import chromadb
from sentence_transformers import SentenceTransformer

# -----------------------------
# 1. Connect to the same persistent ChromaDB folder
#    - This ensures we are working with the same data created in setup
# -----------------------------
client = chromadb.PersistentClient(path="D:/hacksih/chroma_store")

# -----------------------------
# 2. Get or create the collection
#    - If it exists, it will load
#    - If not, it will create a new one (empty)
# -----------------------------
collection = client.get_or_create_collection("corporate_bills_reviews")

# -----------------------------
# 3. Load embedding model (must be same model as in setup)
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# 4. Example user query
#    - Instead of exact word match, we will search by meaning
# -----------------------------
query = "impact on small businesses"
query_emb = model.encode(query).tolist()

# -----------------------------
# 5. Query the DB
#    - Returns top N most similar reviews
# -----------------------------
results = collection.query(query_embeddings=[query_emb], n_results=2)

# -----------------------------
# 6. Print results
#    - Shows review text + metadata (topic, sentiment)
# -----------------------------
print("\nQuery:", query)
for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
    print(f"- {doc} (Topic: {meta['topic']}, Sentiment: {meta['sentiment']})")
