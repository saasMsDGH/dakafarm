with open("frontend/src/pages/pos/Expenses.jsx", "r", encoding="utf-8") as f:
    code = f.read()

import re

table_rows = """<td><span className="fw-bold">{c.expense_number}</span></td>
                      <td><span className="fw-normal">{c.expense_date}</span></td>
                      <td><span className="fw-normal">{c.category}</span></td>
                      <td><span className="fw-normal">{c.description}</span></td>
                      <td><span className="fw-bold text-danger">{parseFloat(c.amount).toLocaleString()}</span></td>
                      <td><span className="fw-normal">{c.payment_method}</span></td>"""

code = re.sub(
    r'<td>\s*<span className="fw-normal d-block">\{c\.expense_code\}</span>\s*</td>\s*<td><span className="fw-normal">\{c\.name\}</span></td>\s*<td><span className="fw-normal">\{c\.business_type\}</span></td>\s*<td><span className="fw-normal">\{c\.phone\}</span></td>\s*<td><span className="fw-normal">\{c\.address\}</span></td>\s*<td><span className="fw-bold">\{parseFloat\(c\.credit_limit\)\.toLocaleString\(\)\}</span></td>',
    table_rows,
    code
)

with open("frontend/src/pages/pos/Expenses.jsx", "w", encoding="utf-8") as f:
    f.write(code)
