import requests
from jose import jwt
import os

NEXTAUTH_SECRET = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

# Create a payload similar to NextAuth JWT
payload = {
    "name": "xyz",
    "email": "xyz@gmail.com",
    "picture": None,
    "sub": "6a217eb49d7ac651fcb5384b" # from user document _id
}

# Sign the token
token = jwt.encode(payload, NEXTAUTH_SECRET, algorithm=ALGORITHM)

# Call /recent-chats
url = "http://127.0.0.1:8000/recent-chats"
headers = {
    "Authorization": f"Bearer {token}"
}

print("Testing GET /recent-chats...")
try:
    response = requests.get(url, headers=headers)
    print("Status:", response.status_code)
    print("Response JSON:")
    print(response.json())
except Exception as e:
    print("Error:", e)
