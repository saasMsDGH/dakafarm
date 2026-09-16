with open("backend/app/api/v1/pos/router.py", "r", encoding="utf-8") as f:
    code = f.read()

code += """
from app.api.v1.pos.Router import supplier_router
router.include_router(supplier_router.router)
from app.api.v1.pos.Router import purchase_router
router.include_router(purchase_router.router)
from app.api.v1.pos.Router import expense_router
router.include_router(expense_router.router)
"""

with open("backend/app/api/v1/pos/router.py", "w", encoding="utf-8") as f:
    f.write(code)
