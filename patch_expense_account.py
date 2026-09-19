import os

path = 'frontend/src/pages/pos/Expenses.jsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure there is an empty option
if 'Pay Later' not in content:
    # First, try to remove required
    content = content.replace(
        '<Form.Select name="account_id" value={currentExpense.account_id} onChange={handleChange} required>',
        '<Form.Select name="account_id" value={currentExpense.account_id} onChange={handleChange}>'
    )
    
    # Then insert the empty option
    content = content.replace(
        '{accounts.map(acc => (',
        '<option value="">{t("pay_later", "Pay Later (Unpaid)")}</option>\n                  {accounts.map(acc => ('
    )

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
