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
    
    # We want to make sure fetchReport(1) is called on mount
    content = content.replace(
        '''  useEffect(() => {
    fetchAccounts();
  }, []);''',
        '''  useEffect(() => {
    fetchReport(1);
    fetchAccounts();
  }, []);'''
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Frontend useEffect updated")
