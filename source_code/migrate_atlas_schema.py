import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

ATLAS_URI = "mongodb+srv://saiteja:saiteja2221125689@cluster0.yptaq7r.mongodb.net/llmscan?retryWrites=true&w=majority"

async def migrate_schema():
    print("Connecting to MongoDB Atlas...")
    client = AsyncIOMotorClient(ATLAS_URI)
    db = client.get_database("llmscan")
    
    chats_col = db["chats"]
    cursor = chats_col.find()
    chats = await cursor.to_list(length=1000)
    print(f"Found {len(chats)} total chat documents.")
    
    updated_count = 0
    for chat in chats:
        doc_id = chat["_id"]
        
        # Check if it has legacy top-level fields
        has_legacy_fields = "prompt" in chat or "response" in chat or "analysis" in chat
        
        if has_legacy_fields:
            # We construct a messages list
            messages = chat.get("messages", [])
            
            # If the legacy message is not already the first element in messages, prepend it
            legacy_prompt = chat.get("prompt")
            legacy_response = chat.get("response")
            legacy_analysis = chat.get("analysis")
            legacy_timestamp = chat.get("timestamp")
            
            # Check if we should insert the legacy message at the start
            legacy_already_present = False
            if messages:
                # Compare the first message prompt
                if messages[0].get("prompt") == legacy_prompt:
                    legacy_already_present = True
                    
            if not legacy_already_present and legacy_prompt:
                messages.insert(0, {
                    "prompt": legacy_prompt,
                    "response": legacy_response,
                    "analysis": legacy_analysis,
                    "timestamp": legacy_timestamp
                })
                
            # Set the title to the legacy prompt or first message prompt
            title = chat.get("title") or legacy_prompt or (messages[0].get("prompt") if messages else "Chat Session")
            
            # Update the document to the new schema and remove legacy fields
            update_doc = {
                "$set": {
                    "messages": messages,
                    "title": title
                },
                "$unset": {
                    "prompt": "",
                    "response": "",
                    "analysis": ""
                }
            }
            
            await chats_col.update_one({"_id": doc_id}, update_doc)
            updated_count += 1
            print(f"Migrated document {doc_id} with title: '{title}'")
            
    print(f"Migration finished. Updated {updated_count} legacy documents to multi-turn format.")

if __name__ == "__main__":
    asyncio.run(migrate_schema())
