import requests
import json

BASE_URL = "http://localhost:8000"

r = requests.post(BASE_URL + "/login", data={"username": "admin_tb_e22851@amas.com", "password": "Admin@1234"}, headers={"Content-Type": "application/x-www-form-urlencoded"})
token = r.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}
r = requests.get(BASE_URL + "/api/v1/finance/transactions/?limit=1000", headers=headers)
txs = r.json()["items"]

for tx in txs:
    amount = float(tx["amount"])
    if amount > 100000:
        print(tx["transaction_type"], tx["direction"], amount)
