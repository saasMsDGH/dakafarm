import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faEdit, faTrash, faSearch, faCheckCircle, faTimesCircle } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, Button, Modal, Form, InputGroup, Pagination, Badge } from '@themesberg/react-bootstrap';
import { useTranslation } from 'react-i18next';
import { api } from "../../api/axios";
import Swal from 'sweetalert2';

export default () => {
  const { t } = useTranslation();
  
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  
  const [showModal, setShowModal] = useState(false);
  const [isEdit, setIsEdit] = useState(false);
  
  const [currentAccount, setCurrentAccount] = useState({
    name: '',
    account_type: 'CASH',
    bank_name: '',
    account_number: '',
    opening_balance: '0.00',
    is_active: true
  });

  const fetchAccounts = async (currentPage = page, search = searchTerm) => {
    try {
      setLoading(true);
      const response = await api.get(`/api/v1/finance/accounts/?page=${currentPage}&limit=10&search=${search}`);
      setAccounts(response.data.items);
      setTotalPages(response.data.pages);
      setPage(currentPage);
    } catch (error) {
      console.error("Failed to fetch accounts", error);
      Swal.fire('Error', 'Failed to load financial accounts', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAccounts();
  }, []);

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
    fetchAccounts(1, e.target.value);
  };

  const handlePageChange = (newPage) => {
    fetchAccounts(newPage, searchTerm);
  };

  const handleShowAddModal = () => {
    setIsEdit(false);
    setCurrentAccount({
      name: '',
      account_type: 'CASH',
      bank_name: '',
      account_number: '',
      opening_balance: '0.00',
      is_active: true
    });
    setShowModal(true);
  };

  const handleShowEditModal = (account) => {
    setIsEdit(true);
    setCurrentAccount({
      ...account,
      bank_name: account.bank_name || '',
      account_number: account.account_number || '',
    });
    setShowModal(true);
  };

  const handleSave = async () => {
    try {
      const payload = {
        name: currentAccount.name,
        account_type: currentAccount.account_type,
        bank_name: currentAccount.bank_name || null,
        account_number: currentAccount.account_number || null,
        is_active: currentAccount.is_active
      };

      if (!isEdit) {
        payload.opening_balance = parseFloat(currentAccount.opening_balance) || 0;
      }

      if (isEdit) {
        await api.put(`/api/v1/finance/accounts/${currentAccount.id}`, payload);
        Swal.fire('Success', 'Financial account updated successfully', 'success');
      } else {
        await api.post(`/api/v1/finance/accounts/`, payload);
        Swal.fire('Success', 'Financial account created successfully', 'success');
      }
      setShowModal(false);
      fetchAccounts();
    } catch (error) {
      console.error("Save error", error);
      let errMsg = 'Failed to save account';
      if (error.response && error.response.data && error.response.data.detail) {
        if (Array.isArray(error.response.data.detail)) {
            errMsg = error.response.data.detail.map(e => e.msg || e.type).join(", ");
        } else {
            errMsg = error.response.data.detail;
        }
      }
      Swal.fire('Error', errMsg, 'error');
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setCurrentAccount({ 
        ...currentAccount, 
        [name]: type === 'checkbox' ? checked : value 
    });
  };

  const toggleStatus = async (account) => {
    try {
      await api.put(`/api/v1/finance/accounts/${account.id}`, {
        is_active: !account.is_active
      });
      Swal.fire('Success', `Account marked as ${!account.is_active ? 'Active' : 'Inactive'}`, 'success');
      fetchAccounts();
    } catch (error) {
      Swal.fire('Error', 'Failed to change account status', 'error');
    }
  };

  return (
    <>
      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <div className="d-block mb-4 mb-md-0">
          <h4>{t('financial_accounts', 'Financial Accounts')}</h4>
          <p className="mb-0">{t('manage_financial_accounts', 'Manage Cash, Bank, and Mobile Money accounts.')}</p>
        </div>
        <div className="btn-toolbar mb-2 mb-md-0">
          <Button variant="primary" size="sm" onClick={handleShowAddModal}>
            <FontAwesomeIcon icon={faPlus} className="me-2" /> {t('add_account', 'Add Account')}
          </Button>
        </div>
      </div>

      <Card border="light" className="shadow-sm">
        <Card.Body>
          <div className="table-settings mb-4">
            <Row className="justify-content-between align-items-center">
              <Col xs={12} md={4}>
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

          <Table responsive className="align-items-center table-flush">
            <thead className="thead-light">
              <tr>
                <th scope="col">{t('name', 'Account Name')}</th>
                <th scope="col">{t('account_type', 'Type')}</th>
                <th scope="col">{t('bank_details', 'Details')}</th>
                <th scope="col">{t('opening_balance', 'Opening Balance')}</th>
                <th scope="col">{t('status', 'Status')}</th>
                <th scope="col">{t('actions', 'Actions')}</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="6" className="text-center">Loading...</td></tr>
              ) : accounts.length === 0 ? (
                <tr><td colSpan="6" className="text-center">No accounts found.</td></tr>
              ) : (
                accounts.map(acc => (
                  <tr key={acc.id}>
                    <td><span className="fw-bold">{acc.name}</span></td>
                    <td>
                        <Badge bg={acc.account_type === 'CASH' ? 'success' : acc.account_type === 'BANK' ? 'info' : 'warning'}>
                            {acc.account_type}
                        </Badge>
                    </td>
                    <td>
                      {acc.account_type !== 'CASH' && (
                          <div className="small">
                              <div><strong>Bank:</strong> {acc.bank_name || '-'}</div>
                              <div><strong>A/C:</strong> {acc.account_number || '-'}</div>
                          </div>
                      )}
                      {acc.account_type === 'CASH' && <span className="text-muted">-</span>}
                    </td>
                    <td><span className="fw-normal">{acc.opening_balance}</span></td>
                    <td>
                      <Badge bg={acc.is_active ? 'success' : 'danger'}>
                        {acc.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </td>
                    <td>
                      <Button variant="link" className="text-dark me-2 p-0" onClick={() => handleShowEditModal(acc)}>
                        <FontAwesomeIcon icon={faEdit} className="text-secondary" />
                      </Button>
                      <Button variant="link" className="text-dark p-0" onClick={() => toggleStatus(acc)}>
                        <FontAwesomeIcon icon={acc.is_active ? faTimesCircle : faCheckCircle} className={acc.is_active ? "text-danger" : "text-success"} title={acc.is_active ? "Deactivate" : "Activate"} />
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </Table>

          {totalPages > 1 && (
            <Card.Footer className="px-3 border-0 d-flex flex-column flex-lg-row align-items-center justify-content-between">
              <Pagination>
                <Pagination.Prev onClick={() => handlePageChange(page - 1)} disabled={page === 1} />
                {[...Array(totalPages)].map((_, i) => (
                  <Pagination.Item key={i + 1} active={i + 1 === page} onClick={() => handlePageChange(i + 1)}>
                    {i + 1}
                  </Pagination.Item>
                ))}
                <Pagination.Next onClick={() => handlePageChange(page + 1)} disabled={page === totalPages} />
              </Pagination>
            </Card.Footer>
          )}
        </Card.Body>
      </Card>

      <Modal as={Modal.Dialog} centered show={showModal} onHide={() => setShowModal(false)}>
        <Form>
          <Modal.Header closeButton>
            <Modal.Title>{isEdit ? 'Edit Financial Account' : 'Add Financial Account'}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Row>
              <Col md={12} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('account_name', 'Account Name')} <span className="text-danger">*</span></Form.Label>
                  <Form.Control type="text" name="name" value={currentAccount.name} onChange={handleChange} required />
                </Form.Group>
              </Col>
              <Col md={12} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('account_type', 'Account Type')} <span className="text-danger">*</span></Form.Label>
                  <Form.Select name="account_type" value={currentAccount.account_type} onChange={handleChange} required>
                    <option value="CASH">Cash</option>
                    <option value="BANK">Bank Account</option>
                    <option value="MOBILE_MONEY">Mobile Money</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              
              {currentAccount.account_type !== 'CASH' && (
                  <>
                    <Col md={12} className="mb-3">
                        <Form.Group>
                        <Form.Label>{t('bank_provider_name', 'Bank/Provider Name')}</Form.Label>
                        <Form.Control type="text" name="bank_name" value={currentAccount.bank_name} onChange={handleChange} placeholder="e.g. CRDB, M-Pesa" />
                        </Form.Group>
                    </Col>
                    <Col md={12} className="mb-3">
                        <Form.Group>
                        <Form.Label>{t('account_number', 'Account Number / Phone')}</Form.Label>
                        <Form.Control type="text" name="account_number" value={currentAccount.account_number} onChange={handleChange} />
                        </Form.Group>
                    </Col>
                  </>
              )}

              {!isEdit && (
                  <Col md={12} className="mb-3">
                    <Form.Group>
                    <Form.Label>{t('opening_balance', 'Opening Balance')}</Form.Label>
                    <Form.Control type="number" step="0.01" name="opening_balance" value={currentAccount.opening_balance} onChange={handleChange} />
                    <Form.Text className="text-muted">You cannot change this later. Ensure this is correct.</Form.Text>
                    </Form.Group>
                </Col>
              )}
            </Row>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowModal(false)}>
              {t('cancel', 'Cancel')}
            </Button>
            <Button variant="primary" onClick={handleSave}>
              {t('save', 'Save')}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </>
  );
};
