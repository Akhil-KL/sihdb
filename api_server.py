from fastapi import FastAPI
import chromadb
import json   # ✅ ADDED (for loading reviews.json)
import os     # ✅ ADDED (to check if file exists)

app = FastAPI()

# ✅ CHANGED: path is now relative (works in Railway container, not Windows D:/ drive)
CHROMA_PATH = "./chroma_store"
REVIEWS_FILE = "./reviews.json"

# ✅ Connect to ChromaDB
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection("corporate_bills_reviews")

# -----------------------------
# 🔥 NEW FUNCTION: Auto-load data from reviews.json at startup
# -----------------------------
def load_reviews_into_db():
    if not os.path.exists(REVIEWS_FILE):
        print("⚠️ reviews.json not found in container!")
        return

    with open(REVIEWS_FILE, "r", encoding="utf-8") as f:
        reviews = json.load(f)

    # ✅ Clear old data before reloading
    # Clear existing records safely
    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    # ✅ Insert fresh data into ChromaDB
    for i, r in enumerate(reviews):
        bill_name = r.get("bill") or r.get("Bill") or r.get("bill_name")
        if not bill_name:
            continue
        collection.add(
            ids=[str(i)],
            documents=[r.get("review", "")],
            metadatas=[{
                "bill": bill_name,
                "sentiment": r.get("sentiment"),
                "time": r.get("time")
            }]
        )
    print(f"✅ Loaded {len(reviews)} reviews into ChromaDB")

# ✅ CALL FUNCTION at startup (this is new)
load_reviews_into_db()

# -----------------------------
# API Endpoints (unchanged except comments)!!!!
# -----------------------------
@app.get("/")
def root():
    return {"message": "✅ API is live! Use /bill endpoint."}

@app.get("/bill")
def get_reviews_by_bill():
    bill_name = "Taxation Amendment Bill 2023"   # 👈 still hardcoded for now

    # (same as before) - fetch everything from DB
    all_data = collection.get()
    available_bills = {meta.get("bill") for meta in all_data["metadatas"]}
    print("📌 Bills inside DB:", available_bills)

    reviews = []
    for doc, meta in zip(all_data["documents"], all_data["metadatas"]):
        if meta.get("bill") == bill_name:
            reviews.append({
                "bill": meta["bill"],
                "review": doc,
                "sentiment": meta["sentiment"],
                "time": meta["time"]
            })

    if not reviews:
        return {
            "message": f"No reviews found for bill: {bill_name}",
            "debug_available_bills": list(available_bills)
        }

    reviews.sort(key=lambda r: r["time"], reverse=True)

    return {
        "bill": bill_name,
        "total_reviews": len(reviews),
        "reviews": reviews
    }
