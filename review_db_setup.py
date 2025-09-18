# review_db_setup.py
import json
import chromadb
from sentence_transformers import SentenceTransformer

# -----------------------------
# 1. Load reviews dataset from JSON
# -----------------------------
with open("D:/hacksih/reviews.json", "r", encoding="utf-8") as f:
    reviews = json.load(f)

print(f"📂 Loaded {len(reviews)} reviews from JSON")

# -----------------------------
# 2. Create a persistent ChromaDB client
# -----------------------------
client = chromadb.PersistentClient(path="D:/hacksih/chroma_store")

# -----------------------------
# 3. Create or get the collection
# -----------------------------
collection = client.get_or_create_collection("corporate_bills_reviews")

# ⚠️ COMMENT THIS OUT (don’t wipe data each run unless you want a reset)
# collection.delete(where={})

# -----------------------------
# 4. Load embedding model
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# 5. Store reviews in the collection
# -----------------------------
for i, r in enumerate(reviews):
    print(f"Row {i}: keys = {list(r.keys())}")

    bill_name = r.get("bill") or r.get("bill") or ""  # handle missing key

    if not bill_name.strip():
        print(f"⚠️ Skipping row {i} — no bill field found")
        continue

    emb = model.encode(r["review"]).tolist()

    collection.add(
        documents=[r["review"]],
        embeddings=[emb],
        ids=[str(i)],
        metadatas=[{
            "bill": bill_name.strip(),
            "sentiment": r.get("sentiment", ""),
            "time": r.get("time", "")
        }]
    )


# -----------------------------
# 6. Verify stored data
# -----------------------------
all_data = collection.get()
print("🔍 Bills stored in DB:", [m.get("bill") for m in all_data["metadatas"]])
