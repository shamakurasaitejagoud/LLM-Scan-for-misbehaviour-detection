import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

ATLAS_URI = "mongodb+srv://saiteja:saiteja2221125689@cluster0.yptaq7r.mongodb.net/llmscan?retryWrites=true&w=majority"

async def inspect():
    client = AsyncIOMotorClient(ATLAS_URI)
    db = client.get_database("llmscan")
    
    doc = await db["chats"].find_one({"_id": ObjectId("6a2272ce5eb29cccc4ec7a84")})
    if not doc:
        print("Document not found!")
        return
        
    analysis = doc["messages"][0]["analysis"]
    layer_aie = analysis["layer_aie"]
    threat_assessment = analysis["threat_assessment"]
    
    print("Full layer_aie (31 values):")
    print(layer_aie)
    print("\nSlice [10:31] (21 values):")
    print(layer_aie[10:31])
    print("\nThreat Assessment:")
    print(threat_assessment)

if __name__ == "__main__":
    asyncio.run(inspect())
