import asyncio
import os
import requests
from jose import jwt

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

prompts = [
    "Hello",
    "What is 2 + 2?",
    "Tell me a joke",
    "What is the capital of France?",
    "how to bake a cake"
]

def test():
    for p in prompts:
        print(f"\nScanning prompt: '{p}'...")
        res = requests.post("http://127.0.0.1:8000/scan", headers=headers, json={"prompt": p})
        if res.status_code == 200:
            data = res.json()
            ta = data.get("threat_assessment", {})
            is_safe = data.get("is_safe")
            summary = data.get("safety_summary")
            print(f"Safety: {'SAFE' if is_safe else 'UNSAFE'}")
            print(f"Summary: {summary}")
            print("Threat Assessment:")
            for cat, prob in ta.items():
                print(f"  {cat}: {prob:.4f}")
        else:
            print("Error:", res.status_code, res.text)

if __name__ == "__main__":
    test()
