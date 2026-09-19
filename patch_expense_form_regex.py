import os
import re

path = 'frontend/src/pages/pos/Expenses.jsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Insert amount_paid
new_content = re.sub(
    r'(<Form\.Group className="mb-3">\s*<Form\.Label>\{t\(\'amount\'\)\}</Form\.Label>\s*<Form\.Control type="number" step="0\.01" name="amount" value=\{currentExpense\.amount\} onChange=\{handleChange\} required />\s*</Form\.Group>)',
    r'\1\n              <Form.Group className="mb-3">\n                <Form.Label>{t(\'amount_paid\', \'Amount Paid\')}</Form.Label>\n                <Form.Control type="number" step="0.01" name="amount_paid" value={currentExpense.amount_paid || \'0.00\'} onChange={handleChange} />\n              </Form.Group>',
    content
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)
