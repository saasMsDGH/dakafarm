import requests

s, b = requests.post("http://localhost:8000/login", data={"username": "admin_pos@amas.com", "password": "Admin@1234"}).json()
token = requests.post("http://localhost:8000/login", data={"username": "admin_pos@amas.com", "password": "Admin@1234"}).json().get("access_token")

r = requests.get("http://localhost:8000/api/v1/pos/customers/?limit=1000", headers={"Authorization": f"Bearer {token}"})
print(r.status_code)
print(r.text)
