import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import json

ATLAS_URI = "mongodb+srv://saiteja:saiteja2221125689@cluster0.yptaq7r.mongodb.net/llmscan?retryWrites=true&w=majority"

async def inspect():
    client = AsyncIOMotorClient(ATLAS_URI)
    db = client.get_database("llmscan")
    
    doc = await db["chats"].find_one({"_id": ObjectId("6a2272ce5eb29cccc4ec7a84")})
    if not doc:
        print("Document not found!")
        return
        
    print("Email:", doc.get("email"))
    print("Title:", doc.get("title"))
    print("Messages count:", len(doc.get("messages", [])))
    
    if doc.get("messages"):
        first_msg = doc["messages"][0]
        print("Prompt:", first_msg.get("prompt"))
        print("Response:", first_msg.get("response"))
        print("Threat Assessment:")
        print(json.dumps(first_msg.get("analysis", {}).get("threat_assessment"), indent=2))
        print("Layer AIE (first 5 values):", first_msg.get("analysis", {}).get("layer_aie", [])[:5])
        print("Layer AIE (length):", len(first_msg.get("analysis", {}).get("layer_aie", [])))

if __name__ == "__main__":
    asyncio.run(inspect())
