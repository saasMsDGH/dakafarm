with open("backend/app/api/v1/pos/schemas/PurchaseSchema.py", "r", encoding="utf-8") as f:
    code = f.read()

import re
code = re.sub(
    r'(quantity: Decimal = Field\(\.\.\., gt=0\)\s*\n\s*unit_cost: Decimal = Field\(\.\.\., ge=0\))',
    r'\1\n    new_selling_price: Optional[Decimal] = Field(None, ge=0, description="Optionally update the product selling price")',
    code
)

with open("backend/app/api/v1/pos/schemas/PurchaseSchema.py", "w", encoding="utf-8") as f:
    f.write(code)
