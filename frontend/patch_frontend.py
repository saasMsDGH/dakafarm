import os

files = [
    'CashBookReport.jsx',
    'BankBookReport.jsx',
    'MobileMoneyReport.jsx'
]

base_path = 'd:/myprojects/AMAS FARM/AMAS-FARM-Management-System/frontend/src/pages/reports/financial/'

for filename in files:
    filepath = os.path.join(base_path, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove early return if no accId
    content = content.replace(
        'if (!accId) return; // Do not fetch if no account selected',
        ''
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Frontend fetch limit removed")
