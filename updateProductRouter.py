with open("backend/app/api/v1/inventory/Router/product_router.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    'return await ProductService.update(db, product_id, request)',
    'return await ProductService.update(db, product_id, request, current_user.id)'
)

with open("backend/app/api/v1/inventory/Router/product_router.py", "w", encoding="utf-8") as f:
    f.write(code)
