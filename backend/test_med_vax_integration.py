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

print("[Setup] Creating user...")
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

# Create Meds Product
s, b = req("POST", "/api/v1/inventory/products/", {
    "name": f"Meds {UNIQUE_SUFFIX}",
    "category_id": category_id,
    "unit_of_measure": "liters",
    "reorder_level": 5.0
}, token=admin_token)
meds_product_id = b.get("id")
req("POST", "/api/v1/inventory/movements/", {
    "product_id": meds_product_id, "movement_type": "IN", "quantity": 100.0
}, token=admin_token)

# Create Vax Product
s, b = req("POST", "/api/v1/inventory/products/", {
    "name": f"Vax {UNIQUE_SUFFIX}",
    "category_id": category_id,
    "unit_of_measure": "vials",
    "reorder_level": 5.0
}, token=admin_token)
vax_product_id = b.get("id")
req("POST", "/api/v1/inventory/movements/", {
    "product_id": vax_product_id, "movement_type": "IN", "quantity": 100.0
}, token=admin_token)

print(f"\n--- Testing MedicationRecords ---")
s, b = req("POST", "/api/v1/farm/medication-records/", {
    "flock_id": flock_id,
    "product_id": meds_product_id,
    "record_date": "2023-01-02",
    "disease_suspected": "Coccidiosis",
    "quantity_used": 10.0,
    "cost_per_unit": 5.0,
    "withdrawal_period_days": 14
}, token=admin_token)
med_id = b.get("id")
if s == 201: print("-> PASS: Med Record created")
else: print(f"-> FAIL: {s} - {b}")

s, p = req("GET", f"/api/v1/inventory/products/{meds_product_id}", token=admin_token)
if p.get("current_stock") == "90.000": print("-> PASS: Med stock correctly dropped to 90")
else: print(f"-> FAIL: Expected 90 stock, got {p.get('current_stock')}")

s, b = req("PUT", f"/api/v1/farm/medication-records/{med_id}", {"quantity_used": 20.0}, token=admin_token)
s, p = req("GET", f"/api/v1/inventory/products/{meds_product_id}", token=admin_token)
if p.get("current_stock") == "80.000": print("-> PASS: Med stock accurately deducted to 80")

s, b = req("DELETE", f"/api/v1/farm/medication-records/{med_id}", token=admin_token)
s, p = req("GET", f"/api/v1/inventory/products/{meds_product_id}", token=admin_token)
if p.get("current_stock") == "100.000": print("-> PASS: Med stock fully restored to 100")

print(f"\n--- Testing VaccinationRecords ---")
s, b = req("POST", "/api/v1/farm/vaccination-records/", {
    "flock_id": flock_id,
    "product_id": vax_product_id,
    "record_date": "2023-01-02",
    "disease_targeted": "Newcastle",
    "administration_method": "Water",
    "quantity_used": 15.0,
    "cost_per_unit": 10.0,
    "next_due_date": "2023-02-02"
}, token=admin_token)
vax_id = b.get("id")
if s == 201: print("-> PASS: Vax Record created")
else: print(f"-> FAIL: {s} - {b}")

s, p = req("GET", f"/api/v1/inventory/products/{vax_product_id}", token=admin_token)
if p.get("current_stock") == "85.000": print("-> PASS: Vax stock correctly dropped to 85")
else: print(f"-> FAIL: Expected 85 stock, got {p.get('current_stock')}")

s, b = req("PUT", f"/api/v1/farm/vaccination-records/{vax_id}", {"quantity_used": 20.0}, token=admin_token)
s, p = req("GET", f"/api/v1/inventory/products/{vax_product_id}", token=admin_token)
if p.get("current_stock") == "80.000": print("-> PASS: Vax stock accurately deducted to 80")

s, b = req("DELETE", f"/api/v1/farm/vaccination-records/{vax_id}", token=admin_token)
s, p = req("GET", f"/api/v1/inventory/products/{vax_product_id}", token=admin_token)
if p.get("current_stock") == "100.000": print("-> PASS: Vax stock fully restored to 100")

print("\nAll integration tests complete.")
