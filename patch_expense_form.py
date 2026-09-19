import os

path = 'frontend/src/pages/pos/Expenses.jsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix state manually
content = content.replace(
    "amount: '0.00',\n      expense_date: new Date()",
    "amount: '0.00',\n      amount_paid: '0.00',\n      expense_date: new Date()"
)

# Fix edit
content = content.replace(
    "...expense,\n        expense_date: expense.expense_date",
    "...expense,\n        amount_paid: expense.amount_paid || '0.00',\n        expense_date: expense.expense_date"
)

# Fix form
form_old = """              <Form.Group className="mb-3">
                <Form.Label>{t('amount')}</Form.Label>
                <Form.Control type="number" step="0.01" name="amount" value={currentExpense.amount} onChange={handleChange} required />
              </Form.Group>"""

form_new = """              <Form.Group className="mb-3">
                <Form.Label>{t('amount')}</Form.Label>
                <Form.Control type="number" step="0.01" name="amount" value={currentExpense.amount} onChange={handleChange} required />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>{t('amount_paid', 'Amount Paid')}</Form.Label>
                <Form.Control type="number" step="0.01" name="amount_paid" value={currentExpense.amount_paid || '0.00'} onChange={handleChange} />
              </Form.Group>"""

content = content.replace(form_old, form_new)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("amount_paid form and state applied.")
