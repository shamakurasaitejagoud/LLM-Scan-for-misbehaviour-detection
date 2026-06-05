import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

ATLAS_URI = "mongodb+srv://saiteja:saiteja2221125689@cluster0.yptaq7r.mongodb.net/llmscan?retryWrites=true&w=majority"

async def check():
    client = AsyncIOMotorClient(ATLAS_URI)
    db = client.get_database("llmscan")
    
    print("Chats in MongoDB Atlas:")
    cursor = db["chats"].find().sort("timestamp", -1)
    chats = await cursor.to_list(length=100)
    for c in chats:
        print(f"ID: {c.get('_id')}, Email: {c.get('email')}, Prompt: {c.get('prompt')}, Timestamp: {c.get('timestamp')}")

asyncio.run(check())
