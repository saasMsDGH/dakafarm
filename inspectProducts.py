with open("frontend/src/pages/inventory/Products.jsx", "r", encoding="utf-8") as f:
    code = f.read()

import re

# Match from selling_price Form.Group to reorder_level Form.Group
pattern = r'<Form\.Group\s+id="selling_price"[\s\S]*?</Form\.Group>\s*</Col>\s*</Col>\s*</Col>\s*<Col md=\{6\}>\s*<Form\.Group id="current_stock"[\s\S]*?</Form\.Group>\s*</Col>\s*<Col md=\{6\}>\s*<Form\.Group id="reorder_level"'
# Wait, I don't know exactly what is there. I'll just print out the block to see what it is.
