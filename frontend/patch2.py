import os

files = [
    ('CashBookReport.jsx', 'CASH', 'Cash Book', 'faPiggyBank'),
    ('BankBookReport.jsx', 'BANK', 'Bank Book', 'faUniversity'),
    ('MobileMoneyReport.jsx', 'MOBILE_MONEY', 'Mobile Money Book', 'faMobileAlt')
]

base_path = 'd:/myprojects/AMAS FARM/AMAS-FARM-Management-System/frontend/src/pages/reports/financial/'

for filename, acc_type, title, icon in files:
    filepath = os.path.join(base_path, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We will replace the filter logic and the error message to match correctly.
    # We already have a patch in place, we can just replace the account type strings.
    if filename == 'CashBookReport.jsx':
        content = content.replace(\"a.account_type === 'Cash'\", \"a.account_type === 'CASH'\")
        content = content.replace(\"No Cash accounts found\", \"No CASH accounts found\")
    elif filename == 'BankBookReport.jsx':
        content = content.replace(\"a.account_type === 'Bank'\", \"a.account_type === 'BANK'\")
        content = content.replace(\"No Bank accounts found\", \"No BANK accounts found\")
    elif filename == 'MobileMoneyReport.jsx':
        content = content.replace(\"a.account_type === 'Mobile Money'\", \"a.account_type === 'MOBILE_MONEY'\")
        content = content.replace(\"No Mobile Money accounts found\", \"No MOBILE_MONEY accounts found\")
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Fixed uppercase enum matching")
