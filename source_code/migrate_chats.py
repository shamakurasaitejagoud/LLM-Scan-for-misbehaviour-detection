import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

LOCAL_URI = "mongodb://localhost:27017"
ATLAS_URI = "mongodb+srv://saiteja:saiteja2221125689@cluster0.yptaq7r.mongodb.net/llmscan?retryWrites=true&w=majority"

async def migrate():
    print("Connecting to databases...")
    local_client = AsyncIOMotorClient(LOCAL_URI)
    atlas_client = AsyncIOMotorClient(ATLAS_URI)
    
    local_db = local_client.get_database("llmscan")
    atlas_db = atlas_client.get_database("llmscan")
    
    print("Fetching local chats...")
    local_chats = await local_db["chats"].find().to_list(length=100)
    print(f"Found {len(local_chats)} local chats.")
    
    if not local_chats:
        print("No chats to migrate.")
        return
        
    print("Migrating to MongoDB Atlas...")
    inserted_count = 0
    for chat in local_chats:
        # Check if chat already exists in Atlas by _id
        exists = await atlas_db["chats"].find_one({"_id": chat["_id"]})
        if not exists:
            await atlas_db["chats"].insert_one(chat)
            inserted_count += 1
            print(f"Migrated chat: {chat.get('prompt')}")
            
    print(f"Migration completed! Migrated {inserted_count} chats successfully.")

asyncio.run(migrate())
