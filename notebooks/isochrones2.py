print("debut du script")

import requests
import os
from pathlib import Path
from dotenv import load_dotenv

print("imports OK")

load_dotenv(Path("C:/Users/Admin/Desktop/zonecore/.env"))
ORS_API_KEY = os.getenv("ORS_API_KEY")

print(f"cle : {ORS_API_KEY[:10]}")

url = "https://api.openrouteservice.org/v2/isochrones/driving-car"
headers = {
    "Authorization": ORS_API_KEY,
    "Content-Type": "application/json"
}
body = {
    "locations": [[3.0573, 50.6292]],
    "range": [600],
    "range_type": "time"
}

print("appel API...")
r = requests.post(url, headers=headers, json=body, timeout=30)
print(f"status : {r.status_code}")
print(f"reponse : {r.text[:300]}")