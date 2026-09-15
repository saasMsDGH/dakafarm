import requests
token = requests.post("http://localhost:8000/login", data={"username": "admin_pos@amas.com", "password": "Admin@1234"}).json().get("access_token")
r = requests.get("http://localhost:8000/api/v1/user/me", headers={"Authorization": f"Bearer {token}"})
print(r.text)
