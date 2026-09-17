with open("frontend/src/pages/pos/Customers.jsx", "r", encoding="utf-8") as f:
    code = f.read()

# Replace customer specific terms with expense
code = code.replace("Customer", "Expense")
code = code.replace("customer", "expense")
code = code.replace("CUSTOMERS", "EXPENSES")

# Initial state for Expense
new_state = """    category: '',
    description: '',
    amount: '0.00',
    expense_date: new Date().toISOString().split('T')[0],
    payment_method: 'CASH'"""
import re
code = re.sub(
    r"name: '',\s+business_type: '',\s+phone: '',\s+email: '',\s+address: '',\s+credit_limit: '0.00'",
    new_state,
    code
)

# Table headers
headers = """<th className="border-bottom">{t('expense_number')}</th>
                  <th className="border-bottom">{t('expense_date')}</th>
                  <th className="border-bottom">{t('category')}</th>
                  <th className="border-bottom">{t('description')}</th>
                  <th className="border-bottom">{t('amount')}</th>
                  <th className="border-bottom">{t('payment_method')}</th>"""
code = re.sub(
    r'<th className="border-bottom">\{t\(\'name\'\)\}</th>[\s\S]*?<th className="border-bottom">\{t\(\'credit_limit\'\)\}</th>',
    headers,
    code
)

# Table rows
rows = """<td><span className="fw-bold">{expense.expense_number}</span></td>
                    <td><span className="fw-normal">{expense.expense_date}</span></td>
                    <td><span className="fw-normal">{expense.category}</span></td>
                    <td><span className="fw-normal">{expense.description}</span></td>
                    <td><span className="fw-bold text-danger">{expense.amount}</span></td>
                    <td><span className="fw-normal">{expense.payment_method}</span></td>"""
code = re.sub(
    r'<td><span className="fw-bold">\{expense\.name\}</span></td>[\s\S]*?<td><span className="fw-bold text-primary">\{expense\.credit_limit\}</span></td>',
    rows,
    code
)

# Form fields
form_fields = """<Row>
              <Col md={6}>
                <Form.Group id="category" className="mb-3">
                  <Form.Label>{t('category')}</Form.Label>
                  <Form.Control 
                    type="text" 
                    name="category"
                    value={currentExpense.category} 
                    onChange={handleInputChange} 
                    required
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group id="amount" className="mb-3">
                  <Form.Label>{t('amount')}</Form.Label>
                  <Form.Control 
                    type="number"
                    step="0.01" 
                    name="amount"
                    value={currentExpense.amount} 
                    onChange={handleInputChange} 
                    required
                  />
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={6}>
                <Form.Group id="expense_date" className="mb-3">
                  <Form.Label>{t('expense_date')}</Form.Label>
                  <Form.Control 
                    type="date" 
                    name="expense_date"
                    value={currentExpense.expense_date} 
                    onChange={handleInputChange} 
                    required
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group id="payment_method" className="mb-3">
                  <Form.Label>{t('payment_method')}</Form.Label>
                  <Form.Select 
                    name="payment_method"
                    value={currentExpense.payment_method} 
                    onChange={handleInputChange}
                  >
                    <option value="CASH">{t('cash')}</option>
                    <option value="BANK">{t('bank')}</option>
                    <option value="MOBILE">{t('mobile_money')}</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={12}>
                <Form.Group id="description" className="mb-3">
                  <Form.Label>{t('description')}</Form.Label>
                  <Form.Control 
                    as="textarea"
                    rows={3}
                    name="description"
                    value={currentExpense.description} 
                    onChange={handleInputChange} 
                  />
                </Form.Group>
              </Col>
            </Row>"""
code = re.sub(
    r'<Row>\s+<Col md=\{12\}>\s+<Form\.Group id="name"[\s\S]*?</Form\.Group>\s+</Col>\s+</Row>',
    form_fields,
    code
)

with open("frontend/src/pages/pos/Expenses.jsx", "w", encoding="utf-8") as f:
    f.write(code)
