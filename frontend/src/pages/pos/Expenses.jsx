import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faEdit, faTrash, faSearch } from '@fortawesome/free-solid-svg-icons';
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
  const [currentExpense, setCurrentExpense] = useState({
        category: '',
    description: '',
    amount: '0.00',
    expense_date: new Date().toISOString().split('T')[0],
    payment_method: 'CASH'
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
    payment_method: 'CASH'
    });
    setIsEdit(false);
  };

  const handleShowAddModal = () => {
    setIsEdit(false);
    setShowModal(true);
  };

  const handleShowEditModal = (expense) => {
    setCurrentExpense({
      ...expense
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
        credit_limit: parseFloat(currentExpense.credit_limit) || 0
      };

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
                <th className="border-bottom">ID / Code</th>
                <th className="border-bottom">Name</th>
                <th className="border-bottom">{t('business_type')}</th>
                <th className="border-bottom">Phone</th>
                <th className="border-bottom">Address</th>
                <th className="border-bottom">{t('credit_limit')}</th>
                <th className="border-bottom">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="7" className="text-center">Loading...</td></tr>
              ) : expenses.length === 0 ? (
                <tr><td colSpan="7" className="text-center">No expenses found.</td></tr>
              ) : (
                expenses.map(c => (
                  <tr key={c.id}>
                    <td><span className="fw-bold">{c.expense_number}</span></td>
                      <td><span className="fw-normal">{c.expense_date}</span></td>
                      <td><span className="fw-normal">{c.category}</span></td>
                      <td><span className="fw-normal">{c.description}</span></td>
                      <td><span className="fw-bold text-danger">{parseFloat(c.amount).toLocaleString()}</span></td>
                      <td><span className="fw-normal">{c.payment_method}</span></td>
                    <td>
                      <Button variant="info" size="sm" className="me-2" onClick={() => handleShowEditModal(c)}>
                        <FontAwesomeIcon icon={faEdit} />
                      </Button>
                      <Button variant="danger" size="sm" onClick={() => handleDelete(c.id)}>
                        <FontAwesomeIcon icon={faTrash} />
                      </Button>
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
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleCloseModal}>Cancel</Button>
            <Button variant="primary" type="submit">Save</Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </>
  );
};
