with open("frontend/src/pages/pos/Suppliers.jsx", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("<td><span className=\"fw-normal\">{c.business_type}</span></td>", "<td><span className=\"fw-normal\">{c.contact_person}</span></td>")
code = code.replace("<td><span className=\"fw-bold\">{parseFloat(c.credit_limit).toLocaleString()}</span></td>", "")

with open("frontend/src/pages/pos/Suppliers.jsx", "w", encoding="utf-8") as f:
    f.write(code)
