with open("frontend/src/pages/pos/Expenses.jsx", "r", encoding="utf-8") as f:
    code = f.read()

import re

# Form fields replace
form_fields = """            <Form.Group className="mb-3">
              <Form.Label>{t('category')}</Form.Label>
              <Form.Control type="text" name="category" value={currentExpense.category} onChange={handleChange} required />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>{t('amount')}</Form.Label>
              <Form.Control type="number" step="0.01" name="amount" value={currentExpense.amount} onChange={handleChange} required />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>{t('expense_date')}</Form.Label>
              <Form.Control type="date" name="expense_date" value={currentExpense.expense_date} onChange={handleChange} required />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>{t('payment_method')}</Form.Label>
              <Form.Select name="payment_method" value={currentExpense.payment_method} onChange={handleChange}>
                <option value="CASH">{t('cash')}</option>
                <option value="BANK">{t('bank')}</option>
                <option value="MOBILE">{t('mobile_money')}</option>
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>{t('description')}</Form.Label>
              <Form.Control as="textarea" rows={3} name="description" value={currentExpense.description || ''} onChange={handleChange} />
            </Form.Group>"""

code = re.sub(
    r'<Modal\.Body>[\s\S]*?</Modal\.Body>',
    '<Modal.Body>\n' + form_fields + '\n          </Modal.Body>',
    code
)

with open("frontend/src/pages/pos/Expenses.jsx", "w", encoding="utf-8") as f:
    f.write(code)
