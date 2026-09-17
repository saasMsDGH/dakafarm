import json
import urllib.error
import urllib.request
import time

BASE = "http://localhost:8000"

def req(method, path, body=None, token=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=10) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        return e.code, (json.loads(raw) if raw else {})

def form_req(path, body_str):
    data = body_str.encode()
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    request = urllib.request.Request(BASE + path, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=10) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

UNIQUE_SUFFIX = int(time.time())
ADMIN_EMAIL = f"farm_inv_{UNIQUE_SUFFIX}@amasfarm.com"

req("POST", "/api/v1/user/", {
    "first_name": "Farm", "last_name": "Test",
    "email": ADMIN_EMAIL, "phone": "0700000000",
    "password_hash": "Admin@1234", "role": "admin"
})
s, b = form_req("/login", f"username={ADMIN_EMAIL}&password=Admin@1234")
admin_token = b.get("access_token")

s, b = req("POST", "/api/v1/farm/houses/", {"name": f"House {UNIQUE_SUFFIX}", "capacity": 1000}, token=admin_token)
house_id = b.get("id")

s, b = req("POST", "/api/v1/farm/flocks/", {
    "house_id": house_id,
    "batch_number": f"BATCH-{UNIQUE_SUFFIX}",
    "bird_type": "Layers",
    "strain": "Isa Brown",
    "source": "Hatchery",
    "initial_quantity": 500,
    "current_quantity": 500,
    "arrival_date": "2023-01-01"
}, token=admin_token)
flock_id = b.get("id")

s, b = req("POST", "/api/v1/inventory/product-categories/", {"name": f"Cat {UNIQUE_SUFFIX}", "description": "Desc"}, token=admin_token)
category_id = b.get("id")

# Create a Product WITH A UNIT PRICE of $15
s, b = req("POST", "/api/v1/inventory/products/", {
    "name": f"Layer Mash {UNIQUE_SUFFIX}",
    "category_id": category_id,
    "unit_of_measure": "bags",
    "unit_price": 15.00,
    "reorder_level": 5.0
}, token=admin_token)
product_id = b.get("id")

req("POST", "/api/v1/inventory/movements/", {
    "product_id": product_id, "movement_type": "IN", "quantity": 100.0
}, token=admin_token)

# OMIT cost_per_unit in the FeedRecord request!
s, b = req("POST", "/api/v1/farm/feed-records/", {
    "flock_id": flock_id,
    "product_id": product_id,
    "record_date": "2023-01-02",
    "quantity_used": 10.0
}, token=admin_token)
print(f"Feed Record created: {s}")

if float(b.get("cost_per_unit")) == 15.0 and float(b.get("total_cost")) == 150.0:
    print("-> PASS: System automatically fetched the product's unit price!")
else:
    print(f"-> FAIL: Did not fetch unit price. Got: {b.get('cost_per_unit')} / Total: {b.get('total_cost')}")
