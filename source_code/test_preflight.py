import requests

url_scan = "http://127.0.0.1:8000/scan"
url_recent = "http://127.0.0.1:8000/recent-chats"

headers_preflight = {
    "Origin": "http://localhost:3000",
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "authorization,content-type"
}

print("=== Preflight for /scan ===")
r_scan = requests.options(url_scan, headers=headers_preflight)
print("Status:", r_scan.status_code)
for k, v in r_scan.headers.items():
    print(f"{k}: {v}")

headers_preflight_recent = {
    "Origin": "http://localhost:3000",
    "Access-Control-Request-Method": "GET",
    "Access-Control-Request-Headers": "authorization"
}

print("\n=== Preflight for /recent-chats ===")
r_recent = requests.options(url_recent, headers=headers_preflight_recent)
print("Status:", r_recent.status_code)
for k, v in r_recent.headers.items():
    print(f"{k}: {v}")
