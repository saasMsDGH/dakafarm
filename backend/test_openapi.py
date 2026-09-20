from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
response = client.get("/openapi.json")

if response.status_code == 200:
    data = response.json()
    paths = data.get("paths", {})
    print(f"Total Routes in OpenAPI: {len(paths)}")
    for p in list(paths.keys())[:10]:
        print(" -", p)
    if len(paths) > 10:
        print(" ... (truncated)")
else:
    print(f"FAILED to fetch openapi.json. Status: {response.status_code}")
