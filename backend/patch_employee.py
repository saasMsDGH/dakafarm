import re

filepath = 'd:/myprojects/AMAS FARM/AMAS-FARM-Management-System/backend/app/api/v1/reports/service/operations.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix Employee.is_active -> Employee.status
content = content.replace('Employee.is_active', 'Employee.status')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Employee attributes fixed")
