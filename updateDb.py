with open("backend/app/db/__init__.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_imports = [
    "from app.api.v1.pos.models.supplier import Supplier\n",
    "from app.api.v1.pos.models.purchase import Purchase, PurchaseItem\n",
    "from app.api.v1.pos.models.purchase_payment import PurchasePayment\n",
    "from app.api.v1.pos.models.expense import Expense\n",
]

# Insert imports before __all__
all_idx = next(i for i, line in enumerate(lines) if line.startswith("__all__ ="))
lines = lines[:all_idx] + new_imports + lines[all_idx:]

# Update __all__ list
all_line = lines[-1]
import re
match = re.search(r'__all__ = \[(.*)\]', all_line)
if match:
    existing_items = match.group(1)
    new_items = ', "Supplier", "Purchase", "PurchaseItem", "PurchasePayment", "Expense"'
    lines[-1] = f'__all__ = [{existing_items}{new_items}]\n'

with open("backend/app/db/__init__.py", "w", encoding="utf-8") as f:
    f.writelines(lines)
