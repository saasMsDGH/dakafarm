with open("backend/app/api/v1/inventory/schemas/ProductSchema.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip_next = False
for i, line in enumerate(lines):
    if skip_next:
        skip_next = False
        continue
    new_lines.append(line)
    if "current_stock: Optional[Decimal] = None" in line and "class ProductResponse" in "".join(lines[:i]):
        if i + 1 < len(lines) and "current_stock: Optional[Decimal] = None" in lines[i+1]:
            skip_next = True

with open("backend/app/api/v1/inventory/schemas/ProductSchema.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)
