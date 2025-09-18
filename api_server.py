from fastapi import FastAPI
# from pydantic import BaseModel   # 👈 UNCOMMENT this when using friend's API POST
import chromadb

app = FastAPI()

# ✅ Connect to ChromaDB (persistent storage)
client = chromadb.PersistentClient(path="D:/hacksih/chroma_store")
collection = client.get_or_create_collection("corporate_bills_reviews")

# -----------------------------
# 1. Define request schema (for friend's API)
# -----------------------------
# ⚡ When your friend’s API is ready, uncomment this block
# class BillRequest(BaseModel):
#     bill_name: str   # 👈 API will POST this field

@app.get("/")
def root():
    return {"message": "✅ API is live! Use /bill endpoint."}

# -----------------------------
# 2. Endpoint for fetching reviews by bill
# -----------------------------

@app.get("/bill")
def get_reviews_by_bill():
    bill_name = "Taxation Amendment Bill 2023"   # 👈 for now, testing only

    # Pull everything from DB
    all_data = collection.get()
    available_bills = {meta.get("bill") for meta in all_data["metadatas"]}
    print("📌 Bills inside DB:", available_bills)

    # Filter manually
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


all_data = collection.get()
print("🔍 Available bills in DB:", [m.get("bill") for m in all_data["metadatas"]])
