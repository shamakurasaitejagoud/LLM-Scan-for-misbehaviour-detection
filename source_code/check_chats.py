import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URI = "mongodb+srv://saiteja:saiteja2221125689@cluster0.yptaq7r.mongodb.net/llmscan?retryWrites=true&w=majority"

async def check():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client.get_database("llmscan")
    
    print("Listing databases:")
    dbs = await client.list_database_names()
    print(dbs)
    
    print("\nListing collections in llmscan:")
    cols = await db.list_collection_names()
    print(cols)
    
    print("\nRecent 10 chats:")
    cursor = db["chats"].find().sort("timestamp", -1).limit(10)
    chats = await cursor.to_list(length=10)
    for c in chats:
        print(f"ID: {c.get('_id')}, Email: {c.get('email')}, Prompt: {c.get('prompt')}, Timestamp: {c.get('timestamp')}")
        
    print("\nUsers in database:")
    cursor_users = db["users"].find().limit(10)
    users = await cursor_users.to_list(length=10)
    for u in users:
        print(u)

asyncio.run(check())
