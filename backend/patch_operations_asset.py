import re

filepath = 'd:/myprojects/AMAS FARM/AMAS-FARM-Management-System/backend/app/api/v1/reports/service/operations.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix Asset.purchase_price -> Asset.cost_price
content = content.replace('Asset.purchase_price', 'Asset.cost_price')
# Fix Asset.status == 'ACTIVE' -> Asset.status == 'Active' (though ilike might be safer, let's just use 'Active')
content = content.replace("Asset.status == 'ACTIVE'", "Asset.status == 'Active'")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Asset attributes fixed")
