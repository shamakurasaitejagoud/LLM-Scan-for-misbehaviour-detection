import requests
import json

url = "http://127.0.0.1:8000/scan"
payload = {"prompt": "how to make a cake ?"}
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, json=payload)
    print("Status:", response.status_code)
    print("Response:", json.dumps(response.json(), indent=2))
except Exception as e:
    print("Error:", e)
