import os
import requests
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

BASE_URL = os.getenv("CONFLUENCE_BASE_URL")
PAT = os.getenv("CONFLUENCE_PAT")

if not BASE_URL:
    raise RuntimeError("CONFLUENCE_BASE_URL is not set in .env")

if not PAT:
    raise RuntimeError("CONFLUENCE_PAT is not set in .env")


url = f"{BASE_URL}/rest/api/content"

params = {
    "spaceKey": "AI",
    "limit": 5,
    "expand": "body.storage",
}

headers = {
    "Authorization": f"Bearer {PAT}",
    "Accept": "application/json",
}

response = requests.get(
    url,
    params=params,
    headers=headers,
    verify=False,  # فقط برای تست فعلی
    timeout=15,
)

print("Status:", response.status_code)
print()
print(response.text[:5000])