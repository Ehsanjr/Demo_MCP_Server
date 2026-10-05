import requests

BASE_URL = "https://192.168.237.35"

session = requests.Session()

session.cookies.set(
    "JSESSIONID",
    "16C1DB758C004521C3499BD7B8954479",
    domain="192.168.237.35",
    path="/",
)

url = f"{BASE_URL}/rest/api/content"

params = {
    "spaceKey": "AI",
    "limit": 5,
    "expand": "body.storage",
}

response = session.get(
    url,
    params=params,
    verify=False,
    timeout=15,
)

print("Status:", response.status_code)
print()
print(response.text[:3000])




