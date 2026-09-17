with open("frontend/src/pages/inventory/Products.jsx", "r", encoding="utf-8") as f:
    code = f.read()

import re

# Fix the nested Col issue
code = re.sub(
    r'<\s*Col\s+md=\{6\}\s*>\s*<\s*Col\s+md=\{6\}\s*>\s*<\s*Form.Group\s+id="current_stock"',
    r'</Col>\n              <Col md={6}>\n                <Form.Group id="current_stock"',
    code
)

with open("frontend/src/pages/inventory/Products.jsx", "w", encoding="utf-8") as f:
    f.write(code)
