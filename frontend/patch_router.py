import os

filepath = 'd:/myprojects/AMAS FARM/AMAS-FARM-Management-System/backend/app/api/v1/reports/router/financial.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Query(..., description=...) with Query(None, description=...)
content = content.replace(
    'account_id: int = Query(..., description=\"ID of the cash account\"),',
    'account_id: Optional[int] = Query(None, description=\"ID of the cash account\"),'
)
content = content.replace(
    'account_id: int = Query(..., description=\"ID of the bank account\"),',
    'account_id: Optional[int] = Query(None, description=\"ID of the bank account\"),'
)
content = content.replace(
    'account_id: int = Query(..., description=\"ID of the mobile money account\"),',
    'account_id: Optional[int] = Query(None, description=\"ID of the mobile money account\"),'
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Router updated")
