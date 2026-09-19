import requests
import uuid

BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = f"admin_finance_{uuid.uuid4().hex[:6]}@amas.com"

def req(method, path, json=None, token=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    r = requests.request(method, BASE_URL + path, json=json, headers=headers)
    try:
        return r.status_code, r.json()
    except:
        return r.status_code, r.text

def form_req(path, data):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(BASE_URL + path, data=data, headers=headers)
    return r.status_code, r.json()

def check(name, status, body, expected):
    if status == expected:
        print("PASS: " + name)
    else:
        print("FAIL: " + name + " Status: " + str(status) + " Expected: " + str(expected))

print("--- FINANCE ACCOUNTS TESTS ---")

req("POST", "/api/v1/user/", {
    "first_name": "Admin", "last_name": "Finance", "email": ADMIN_EMAIL,
    "phone": "0700111222", "password_hash": "Admin@1234", "role": "admin"
})
s, b = form_req("/login", f"username={ADMIN_EMAIL}&password=Admin@1234")
token = b.get("access_token")

s, b = req("POST", "/api/v1/finance/accounts/", {
    "name": "Main Cash Vault",
    "account_type": "CASH",
    "opening_balance": 150000.50
}, token=token)
check("Create CASH Account", s, b, 201)
account_id_1 = b.get("id")

s, b = req("POST", "/api/v1/finance/accounts/", {
    "name": "CRDB Primary",
    "account_type": "BANK",
    "bank_name": "CRDB",
    "account_number": "1234567890",
    "opening_balance": 5000000.00
}, token=token)
check("Create BANK Account", s, b, 201)
account_id_2 = b.get("id")

s, b = req("POST", "/api/v1/finance/accounts/", {
    "name": "Main Cash Vault",
    "account_type": "CASH"
}, token=token)
check("Duplicate Account Name", s, b, 409)

s, b = req("POST", "/api/v1/finance/accounts/", {
    "name": "Weird Account",
    "account_type": "CRYPTO"
}, token=token)
check("Invalid Account Type", s, b, 422)

s, b = req("POST", "/api/v1/finance/accounts/", {
    "account_type": "CASH"
}, token=token)
check("Missing Name Field", s, b, 422)

s, b = req("GET", f"/api/v1/finance/accounts/{account_id_1}", token=token)
check("Get Account", s, b, 200)

s, b = req("GET", f"/api/v1/finance/accounts/9999", token=token)
check("Get Nonexistent Account", s, b, 404)

s, b = req("GET", "/api/v1/finance/accounts/?search=CRDB", token=token)
check("List Accounts with search", s, b, 200)

s, b = req("PUT", f"/api/v1/finance/accounts/{account_id_2}", {
    "name": "CRDB Main Branch"
}, token=token)
check("Update Account", s, b, 200)

s, b = req("PUT", f"/api/v1/finance/accounts/{account_id_1}", {
    "is_active": False
}, token=token)
check("Deactivate Account", s, b, 200)

s, b = req("GET", f"/api/v1/finance/accounts/")
check("Unauthorized Access", s, b, 401)

print("--- TESTS COMPLETED ---")
