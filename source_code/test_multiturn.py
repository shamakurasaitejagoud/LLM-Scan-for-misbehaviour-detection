import requests
from jose import jwt
import json

NEXTAUTH_SECRET = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

payload = {
    "name": "xyz",
    "email": "xyz@gmail.com",
    "picture": None,
    "sub": "6a217eb49d7ac651fcb5384b"
}

token = jwt.encode(payload, NEXTAUTH_SECRET, algorithm=ALGORITHM)
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

def test():
    # 1. Send first prompt
    print("Sending prompt 1...")
    res1 = requests.post("http://127.0.0.1:8000/scan", headers=headers, json={
        "prompt": "Hello, this is prompt 1"
    })
    print("Status:", res1.status_code)
    data1 = res1.json()
    chat_id = data1.get("chat_id")
    print("Received chat_id:", chat_id)
    
    if not chat_id:
        print("Error: No chat_id received!")
        return

    # 2. Send second prompt with chat_id
    print("\nSending prompt 2 with chat_id...")
    res2 = requests.post("http://127.0.0.1:8000/scan", headers=headers, json={
        "prompt": "This is prompt 2 in the same chat",
        "chat_id": chat_id
    })
    print("Status:", res2.status_code)
    data2 = res2.json()
    print("Received chat_id:", data2.get("chat_id"))
    
    # 3. Call recent-chats
    print("\nCalling /recent-chats...")
    res3 = requests.get("http://127.0.0.1:8000/recent-chats", headers=headers)
    recent = res3.json()
    print("Recent chats list (first item):")
    if recent:
        item = recent[0]
        print(f"ID: {item.get('id')}")
        print(f"Title: {item.get('prompt')}")
        print(f"Messages count: {len(item.get('messages', []))}")
        for idx, m in enumerate(item.get('messages', [])):
            print(f"  Msg {idx+1}: {m.get('prompt')} -> {m.get('response')[:30]}...")
            
test()
