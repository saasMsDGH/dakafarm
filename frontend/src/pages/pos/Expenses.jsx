import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faEdit, faTrash, faSearch, faEye, faMoneyBillWave } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, Button, Modal, Form, InputGroup, Pagination } from '@themesberg/react-bootstrap';
import { useTranslation } from 'react-i18next';
import { api } from "../../api/axios";
import Swal from 'sweetalert2';

export default () => {
  const { t } = useTranslation();
  
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  
  const [showModal, setShowModal] = useState(false);
  const [isEdit, setIsEdit] = useState(false);
  const [accounts, setAccounts] = useState([]);
  const [currentExpense, setCurrentExpense] = useState({
    category: '',
    description: '',
    amount: '',
    amount_paid: '',
    expense_date: new Date().toISOString().split('T')[0],
    payment_method: 'Cash',
    account_id: ''
  });

  const [showViewModal, setShowViewModal] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [expenseDetails, setExpenseDetails] = useState(null);
  const [paymentInput, setPaymentInput] = useState({
    amount: 0,
    payment_method: 'Cash',
    account_id: ''
  });

  const fetchExpenses = async (currentPage = page, search = searchTerm) => {
    setLoading(true);
    try {
      const response = await api.get(`/api/v1/pos/expenses/?page=${currentPage}&limit=10&search=${search}`);
      setExpenses(response.data.items);
      setTotalPages(response.data.pages);
      setPage(response.data.page);
    } catch (error) {
      console.error("Failed to fetch expenses", error);
      Swal.fire('Error', 'Failed to load expenses', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExpenses();
    const fetchAccounts = async () => {
      try {
        const accRes = await api.get('/api/v1/finance/accounts/?limit=1000');
        setAccounts(accRes.data.items || accRes.data);
      } catch (error) {
        console.error("Failed to load accounts", error);
      }
    };
    fetchAccounts();
  }, []);

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
    fetchExpenses(1, e.target.value);
  };

  const handlePageChange = (newPage) => {
    fetchExpenses(newPage, searchTerm);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setCurrentExpense({
            category: '',
    description: '',
    amount: '0.00',
    expense_date: new Date().toISOString().split('T')[0],
    payment_method: 'CASH',
    account_id: ''
    });
    setIsEdit(false);
  };

  const handleShowAddModal = () => {
    setIsEdit(false);
    setShowModal(true);
  };

  const handleShowEditModal = (expense) => {
    setCurrentExpense({
      ...expense,
      account_id: expense.account_id || ''
    });
    setIsEdit(true);
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    const result = await Swal.fire({
      title: 'Are you sure?',
      text: "You won't be able to revert this!",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Yes, delete it!'
    });

    if (result.isConfirmed) {
      try {
        await api.delete(`/api/v1/pos/expenses/${id}`);
        Swal.fire('Deleted!', 'Expense has been deleted.', 'success');
        fetchExpenses();
      } catch (error) {
        Swal.fire('Error', 'Failed to delete expense. They might be linked to sales.', 'error');
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
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
      }
      handleCloseModal();
      fetchExpenses();
    } catch (error) {
      console.error(error);
      Swal.fire('Error', error.response?.data?.detail || 'Failed to save expense', 'error');
    }
  };

  const handleChange = (e) => {
    setCurrentExpense({ ...currentExpense, [e.target.name]: e.target.value });
  };

  const handleViewExpense = async (id) => {
    try {
      const res = await api.get(`/api/v1/pos/expenses/${id}`);
      const payRes = await api.get(`/api/v1/pos/expenses/${id}/payments/`);
      setExpenseDetails({ ...res.data, payments: payRes.data || [] });
      setShowViewModal(true);
    } catch (error) {
      Swal.fire('Error', 'Failed to fetch expense details', 'error');
    }
  };

  const handleShowPaymentModal = (expense) => {
    setExpenseDetails(expense); // Just keeping context of which expense we are paying
    setPaymentInput({
      amount: parseFloat(expense.amount) - parseFloat(expense.amount_paid),
      payment_method: 'Cash',
      account_id: ''
    });
    setShowPaymentModal(true);
  };

  const submitPayment = async (e) => {
    e.preventDefault();
    if (!paymentInput.account_id) {
      Swal.fire('Error', 'Please select a Payment Account.', 'error');
      return;
    }
    try {
      const payload = {
        expense_id: expenseDetails.id,
        amount: parseFloat(paymentInput.amount),
        payment_method: paymentInput.payment_method,
        account_id: paymentInput.account_id ? parseInt(paymentInput.account_id) : null,
        payment_date: new Date().toISOString()
      };
      await api.post(`/api/v1/pos/expenses/${expenseDetails.id}/payments`, payload);
      Swal.fire('Success', 'Payment recorded successfully', 'success');
      setShowPaymentModal(false);
      fetchExpenses();
      if (showViewModal) {
          handleViewExpense(expenseDetails.id);
      }
    } catch (error) {
      Swal.fire('Error', error.response?.data?.detail || 'Failed to add payment', 'error');
    }
  };

  return (
    <>
      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <div className="d-block mb-4 mb-md-0">
          <h4>{t('expenses', 'Expenses')}</h4>
          <p className="mb-0">{t('manage_expenses', 'Manage your expenses and credit limits.')}</p>
        </div>
        <div className="btn-toolbar mb-2 mb-md-0">
          <Button variant="primary" size="sm" onClick={handleShowAddModal}>
            <FontAwesomeIcon icon={faPlus} className="me-2" /> {t('add_expense')}
          </Button>
        </div>
      </div>

      <div className="table-settings mb-4">
        <Row className="justify-content-between align-items-center">
          <Col xs={12} md={6} lg={4}>
            <InputGroup>
              <InputGroup.Text><FontAwesomeIcon icon={faSearch} /></InputGroup.Text>
              <Form.Control
                type="text"
                placeholder={t('search', 'Search...')}
                value={searchTerm}
                onChange={handleSearch}
              />
            </InputGroup>
          </Col>
        </Row>
      </div>

      <Card border="light" className="table-wrapper table-responsive shadow-sm">
        <Card.Body className="pt-0">
          <Table hover className="user-table align-items-center">
            <thead>
              <tr>
                <th className="border-bottom">Expense #</th>
                <th className="border-bottom">Date</th>
                <th className="border-bottom">Category</th>
                <th className="border-bottom">Description</th>
                <th className="border-bottom">Total Amount</th>
                <th className="border-bottom">Amount Paid</th>
                <th className="border-bottom">Status</th>
                <th className="border-bottom">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="8" className="text-center">Loading...</td></tr>
              ) : expenses.length === 0 ? (
                <tr><td colSpan="8" className="text-center">No expenses found.</td></tr>
              ) : (
                expenses.map(c => (
                  <tr key={c.id}>
                    <td><span className="fw-bold">{c.expense_number}</span></td>
                    <td><span className="fw-normal">{new Date(c.expense_date).toLocaleDateString()}</span></td>
                    <td><span className="fw-normal">{c.category}</span></td>
                    <td><span className="fw-normal">{c.description || '-'}</span></td>
                    <td><span className="fw-bold text-danger">{parseFloat(c.amount).toLocaleString()}</span></td>
                    <td><span className="fw-bold text-success">{parseFloat(c.amount_paid).toLocaleString()}</span></td>
                    <td>
                      <span className={`badge ${c.payment_status === 'PAID' ? 'bg-success' : c.payment_status === 'PARTIAL' ? 'bg-warning' : 'bg-danger'}`}>
                        {c.payment_status}
                      </span>
                    </td>
                    <td>
                      <Button variant="primary" size="sm" className="me-2" onClick={() => handleViewExpense(c.id)}>
                        <FontAwesomeIcon icon={faEye} />
                      </Button>
                      {c.payment_status !== 'PAID' && (
                        <Button variant="success" size="sm" className="me-2" onClick={() => handleShowPaymentModal(c)}>
                          <FontAwesomeIcon icon={faMoneyBillWave} />
                        </Button>
                      )}
                        {c.payment_status === 'UNPAID' && (
                          <Button variant="danger" size="sm" onClick={() => handleDelete(c.id)}>
                            <FontAwesomeIcon icon={faTrash} />
                          </Button>
                        )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </Table>
          
          <Card.Footer className="px-3 border-0 d-lg-flex align-items-center justify-content-between">
            <Pagination className="mb-2 mb-lg-0">
              <Pagination.Prev onClick={() => handlePageChange(page - 1)} disabled={page === 1} />
              {[...Array(totalPages)].map((_, i) => (
                <Pagination.Item key={i + 1} active={i + 1 === page} onClick={() => handlePageChange(i + 1)}>
                  {i + 1}
                </Pagination.Item>
              ))}
              <Pagination.Next onClick={() => handlePageChange(page + 1)} disabled={page === totalPages || totalPages === 0} />
            </Pagination>
          </Card.Footer>
        </Card.Body>
      </Card>

      <Modal as={Modal.Dialog} centered show={showModal} onHide={handleCloseModal}>
        <Form onSubmit={handleSubmit}>
          <Modal.Header closeButton>
            <Modal.Title>{isEdit ? 'Edit Expense' : t('add_expense')}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>{t('category')}</Form.Label>
              <Form.Control type="text" name="category" value={currentExpense.category} onChange={handleChange} required />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>{t('amount')}</Form.Label>
              <Form.Control type="number" step="0.01" name="amount" value={currentExpense.amount} onChange={handleChange} required />
            </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>{t('amount_paid', 'Amount Paid')}</Form.Label>
                <Form.Control type="number" step="0.01" name="amount_paid" value={currentExpense.amount_paid} onChange={handleChange} />
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
              <Form.Label>Payment Account *</Form.Label>
              <Form.Select name="account_id" value={currentExpense.account_id} onChange={handleChange}>
                <option value="">-- Select Account --</option>
                <option value="">{t("pay_later", "Pay Later (Unpaid)")}</option>
                  {accounts.map(acc => (
                  <option key={acc.id} value={acc.id}>{acc.name} ({acc.account_type})</option>
                ))}
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>{t('description')}</Form.Label>
              <Form.Control as="textarea" rows={3} name="description" value={currentExpense.description || ''} onChange={handleChange} />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleCloseModal}>Cancel</Button>
            <Button variant="primary" type="submit">Save</Button>
          </Modal.Footer>
        </Form>
      </Modal>
      <Modal as={Modal.Dialog} centered show={showViewModal} onHide={() => setShowViewModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Expense Details</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {expenseDetails && (
            <div>
              <div className="mb-4">
                <Row>
                  <Col md={6}>
                    <p><strong>Expense #:</strong> {expenseDetails.expense_number}</p>
                    <p><strong>Date:</strong> {new Date(expenseDetails.expense_date).toLocaleDateString()}</p>
                    <p><strong>Category:</strong> {expenseDetails.category}</p>
                  </Col>
                  <Col md={6}>
                    <p><strong>Total Amount:</strong> {parseFloat(expenseDetails.amount).toLocaleString()}</p>
                    <p><strong>Amount Paid:</strong> {parseFloat(expenseDetails.amount_paid).toLocaleString()}</p>
                    <p><strong>Status:</strong> <span className={`badge ${expenseDetails.payment_status === 'PAID' ? 'bg-success' : expenseDetails.payment_status === 'PARTIAL' ? 'bg-warning' : 'bg-danger'}`}>{expenseDetails.payment_status}</span></p>
                  </Col>
                </Row>
                <p><strong>Description:</strong> {expenseDetails.description}</p>
              </div>
              
              <h5 className="mt-4 border-bottom pb-2">Payment History</h5>
              {expenseDetails.payments && expenseDetails.payments.length > 0 ? (
                <Table size="sm" bordered hover>
                  <thead className="bg-light">
                    <tr>
                      <th>Date</th>
                      <th>Method</th>
                      <th>Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {expenseDetails.payments.map((pay, i) => (
                      <tr key={i}>
                        <td>{new Date(pay.payment_date).toLocaleDateString()}</td>
                        <td>{pay.payment_method}</td>
                        <td className="text-success fw-bold">{parseFloat(pay.amount).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <p className="text-muted">No payments recorded yet.</p>
              )}
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowViewModal(false)}>Close</Button>
          {expenseDetails && expenseDetails.payment_status !== 'PAID' && (
            <Button variant="success" onClick={() => { setShowViewModal(false); handleShowPaymentModal(expenseDetails); }}>
              Add Payment
            </Button>
          )}
        </Modal.Footer>
      </Modal>

      <Modal as={Modal.Dialog} centered show={showPaymentModal} onHide={() => setShowPaymentModal(false)}>
        <Form onSubmit={submitPayment}>
          <Modal.Header closeButton>
            <Modal.Title>Add Payment</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            {expenseDetails && (
              <div className="mb-3 text-muted">
                Expense: <strong>{expenseDetails.expense_number}</strong><br/>
                Total Due: <strong>{parseFloat(expenseDetails.amount).toLocaleString()}</strong><br/>
                Remaining Balance: <strong className="text-danger">
                  {(parseFloat(expenseDetails.amount) - parseFloat(expenseDetails.amount_paid)).toLocaleString()}
                </strong>
              </div>
            )}
            <Form.Group className="mb-3">
              <Form.Label>Payment Amount *</Form.Label>
              <Form.Control type="number" step="0.01" value={paymentInput.amount} onChange={(e) => setPaymentInput({...paymentInput, amount: e.target.value})} required />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Payment Method *</Form.Label>
              <Form.Select value={paymentInput.payment_method} onChange={(e) => setPaymentInput({...paymentInput, payment_method: e.target.value})} required>
                <option value="Cash">Cash</option>
                <option value="Mobile Money">Mobile Money</option>
                <option value="Bank Transfer">Bank</option>
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Payment Account *</Form.Label>
              <Form.Select value={paymentInput.account_id} onChange={(e) => setPaymentInput({...paymentInput, account_id: e.target.value})} required>
                <option value="">-- Select Account --</option>
                <option value="">{t("pay_later", "Pay Later (Unpaid)")}</option>
                  {accounts.map(acc => (
                  <option key={acc.id} value={acc.id}>{acc.name} ({acc.account_type})</option>
                ))}
              </Form.Select>
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowPaymentModal(false)}>Cancel</Button>
            <Button variant="success" type="submit">Submit Payment</Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </>
  );
};
