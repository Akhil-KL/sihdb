from fastapi import FastAPI
import chromadb
import json
import os

app = FastAPI()

CHROMA_PATH = "./chroma_store"
REVIEWS_FILE = "./reviews.json"

# ✅ Connect to ChromaDB
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection("corporate_bills_reviews")


# -----------------------------
# Load reviews into DB
# -----------------------------
def load_reviews_into_db():
    if not os.path.exists(REVIEWS_FILE):
        print("⚠️ reviews.json not found in container!")
        return

    with open(REVIEWS_FILE, "r", encoding="utf-8") as f:
        reviews = json.load(f)

    # Clear existing records
    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    # Insert fresh data
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


# Load data at startup
load_reviews_into_db()


# -----------------------------
# API Endpoints
# -----------------------------
@app.get("/")
def root():
    return {"message": "✅ API is live! Use /bill?name=<bill_name> endpoint."}


@app.get("/bill")
def get_reviews_by_bill():
    # -----------------------------
    # 2. Fetch current bill name from external API
    # -----------------------------
    try:
        resp = requests.get("https://affectionate-intuition-production-5f8d.up.railway.app/bill")
        resp.raise_for_status()
        bill_name = resp.json().get("bill", "").strip()
    except Exception as e:
        return {"error": f"Failed to fetch bill from external API: {e}"}

    if not bill_name:
        return {"message": "No bill name returned from external API"}

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
