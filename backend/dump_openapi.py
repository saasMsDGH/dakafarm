import json
import sys
import os

# Insert backend directory to path
sys.path.insert(0, os.path.abspath('d:/myprojects/AMAS FARM/AMAS-FARM-Management-System/backend'))

from app.main import app

openapi = app.openapi()
with open('openapi.json', 'w', encoding='utf-8') as f:
    json.dump(openapi, f, indent=2)
print("Dumped OpenAPI to openapi.json")
