import os

path = 'frontend/src/pages/pos/Expenses.jsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add amount_paid to currentExpense state
content = content.replace(
    '''  const [currentExpense, setCurrentExpense] = useState({
    category: '',
    description: '',
    amount: '0.00',
    expense_date: new Date().toISOString().split('T')[0],
    payment_method: 'Cash',
    account_id: ''
  });''',
    '''  const [currentExpense, setCurrentExpense] = useState({
    category: '',
    description: '',
    amount: '0.00',
    amount_paid: '0.00',
    expense_date: new Date().toISOString().split('T')[0],
    payment_method: 'Cash',
    account_id: ''
  });'''
)

# Fix handleShowModal for edit to populate amount_paid
content = content.replace(
    '''      setCurrentExpense({
        ...expense,
        expense_date: expense.expense_date ? expense.expense_date.split('T')[0] : ''
      });''',
    '''      setCurrentExpense({
        ...expense,
        amount_paid: expense.amount_paid || '0.00',
        expense_date: expense.expense_date ? expense.expense_date.split('T')[0] : ''
      });'''
)

# Add amount_paid input to the form
amount_input_jsx = """              <Form.Group className="mb-3">
                <Form.Label>{t('amount')}</Form.Label>
                <Form.Control type="number" step="0.01" name="amount" value={currentExpense.amount} onChange={handleChange} required />
              </Form.Group>"""

amount_paid_jsx = """              <Form.Group className="mb-3">
                <Form.Label>{t('amount')}</Form.Label>
                <Form.Control type="number" step="0.01" name="amount" value={currentExpense.amount} onChange={handleChange} required />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>{t('amount_paid', 'Amount Paid')}</Form.Label>
                <Form.Control type="number" step="0.01" name="amount_paid" value={currentExpense.amount_paid} onChange={handleChange} />
              </Form.Group>"""

content = content.replace(amount_input_jsx, amount_paid_jsx)

# Modify handleSubmit to use the explicitly provided amount_paid
old_submit = """      const payload = {
        ...currentExpense,
        amount: parseFloat(currentExpense.amount)
      };

      if (currentExpense.account_id) {
        payload.account_id = parseInt(currentExpense.account_id);
      } else {
        delete payload.account_id;
        delete payload.payment_method;
      }

      if (isEdit) {
        await api.put(`/api/v1/pos/expenses/${currentExpense.id}`, payload);
        Swal.fire('Success', 'Expense updated successfully', 'success');
      } else {
        if (payload.account_id) {
          payload.amount_paid = parseFloat(currentExpense.amount);
        } else {
          payload.amount_paid = 0.0;
        }
        await api.post(`/api/v1/pos/expenses/`, payload);
        Swal.fire('Success', 'Expense added successfully', 'success');
      }"""

new_submit = """      const payload = {
        ...currentExpense,
        amount: parseFloat(currentExpense.amount),
        amount_paid: parseFloat(currentExpense.amount_paid) || 0.0
      };

      if (payload.amount_paid > 0) {
        if (!currentExpense.account_id) {
          Swal.fire('Error', 'Please select a Payment Account for the amount paid.', 'error');
          return;
        }
        payload.account_id = parseInt(currentExpense.account_id);
      } else {
        delete payload.account_id;
        delete payload.payment_method;
      }

      if (isEdit) {
        await api.put(`/api/v1/pos/expenses/${currentExpense.id}`, payload);
        Swal.fire('Success', 'Expense updated successfully', 'success');
      } else {
        await api.post(`/api/v1/pos/expenses/`, payload);
        Swal.fire('Success', 'Expense added successfully', 'success');
      }"""

content = content.replace(old_submit, new_submit)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
