import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.get_database("llmscan")
    
    print("Listing local databases:")
    dbs = await client.list_database_names()
    print(dbs)
    
    print("\nListing collections in local llmscan:")
    cols = await db.list_collection_names()
    print(cols)
    
    print("\nLocal 10 chats:")
    cursor = db["chats"].find().sort("timestamp", -1).limit(10)
    chats = await cursor.to_list(length=10)
    for c in chats:
        print(f"ID: {c.get('_id')}, Email: {c.get('email')}, Prompt: {c.get('prompt')}, Timestamp: {c.get('timestamp')}")

asyncio.run(check())
