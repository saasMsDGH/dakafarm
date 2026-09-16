with open("backend/app/api/v1/inventory/schemas/ProductSchema.py", "r", encoding="utf-8") as f:
    code = f.read()

import re

# Add current_stock to ProductCreate
code = re.sub(
    r'(selling_price: Optional\[Decimal\] = Field\(Decimal\(\'0\.00\'\), description="Default selling price"\))',
    r'\1\n    current_stock: Optional[Decimal] = Field(Decimal(\'0.000\'), description="Initial stock level")',
    code
)

# Add current_stock to ProductUpdate
code = re.sub(
    r'(selling_price: Optional\[Decimal\] = None)',
    r'\1\n    current_stock: Optional[Decimal] = None',
    code
)

with open("backend/app/api/v1/inventory/schemas/ProductSchema.py", "w", encoding="utf-8") as f:
    f.write(code)
