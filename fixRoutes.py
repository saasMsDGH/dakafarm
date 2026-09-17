with open("frontend/src/routes.js", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "Sales: { path: \"/pos/sales\" },",
    "Sales: { path: \"/pos/sales\" },\n    Suppliers: { path: \"/pos/suppliers\" },\n    Purchases: { path: \"/pos/purchases\" },\n    Expenses: { path: \"/pos/expenses\" },"
)

with open("frontend/src/routes.js", "w", encoding="utf-8") as f:
    f.write(code)
