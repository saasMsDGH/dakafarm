import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faEdit, faTrash, faSearch, faShareAlt, faEye, faMoneyBillWave } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, Button, Modal, Form, InputGroup, Pagination, Badge, Nav } from '@themesberg/react-bootstrap';
import { useTranslation } from 'react-i18next';
import { api } from "../../api/axios";
import Swal from 'sweetalert2';

export default () => {
  const { t } = useTranslation();
  
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [accounts, setAccounts] = useState([]);
  
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  
  const [showModal, setShowModal] = useState(false);
  const [isEdit, setIsEdit] = useState(false);
  
  const [showDistModal, setShowDistModal] = useState(false);
  const [distAsset, setDistAsset] = useState(null);
  const [distForm, setDistForm] = useState({ location: '', quantity: 1, notes: '' });

  const [currentAsset, setCurrentAsset] = useState({
    name: '',
    description: '',
    purchase_date: new Date().toISOString().split('T')[0],
    cost_price: '0.00',
    quantity: 1,
    condition: 'Good',
    depreciation_rate: '0.00',
    status: 'Active',
    amount_paid: '0.00',
    payment_method: 'Cash',
    account_id: ''
  });

  // Payment Modal State
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentAsset, setPaymentAsset] = useState(null);
  const [paymentForm, setPaymentForm] = useState({
    amount: '',
    payment_method: 'Cash',
    account_id: ''
  });

  // View Details Modal State
  const [showViewModal, setShowViewModal] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [assetPayments, setAssetPayments] = useState([]);
  const [loadingPayments, setLoadingPayments] = useState(false);

  const fetchAssets = async (currentPage = page, search = searchTerm) => {
    setLoading(true);
    try {
      const response = await api.get(`/api/v1/assets/list/?page=${currentPage}&limit=10&search=${search}`);
      setAssets(response.data.items);
      setTotalPages(response.data.pages);
      setPage(response.data.page);
    } catch (error) {
      console.error("Failed to fetch assets", error);
      Swal.fire('Error', 'Failed to load assets', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchAccounts = async () => {
    try {
      const response = await api.get('/api/v1/finance/accounts/?limit=1000');
      setAccounts(response.data.items || response.data || []);
    } catch (error) {
      console.error("Failed to load accounts", error);
    }
  };

  useEffect(() => {
    fetchAssets();
    fetchAccounts();
  }, []);

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
    fetchAssets(1, e.target.value);
  };

  const handlePageChange = (newPage) => {
    fetchAssets(newPage, searchTerm);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setCurrentAsset({
      name: '',
      description: '',
      purchase_date: new Date().toISOString().split('T')[0],
      cost_price: '0.00',
      quantity: 1,
      condition: 'Good',
      depreciation_rate: '0.00',
      status: 'Active',
      amount_paid: '0.00',
      payment_method: 'Cash',
      account_id: ''
    });
    setIsEdit(false);
  };

  const handleShowAddModal = () => {
    setIsEdit(false);
    setCurrentAsset({
      name: '',
      description: '',
      purchase_date: new Date().toISOString().split('T')[0],
      cost_price: '0.00',
      quantity: 1,
      condition: 'Good',
      depreciation_rate: '0.00',
      status: 'Active',
      amount_paid: '0.00',
      payment_method: 'Cash',
      account_id: ''
    });
    setShowModal(true);
  };

  const handleShowEditModal = (asset) => {
    setCurrentAsset({
      ...asset,
      purchase_date: asset.purchase_date ? asset.purchase_date.split('T')[0] : '',
      amount_paid: asset.amount_paid || '0.00',
      payment_method: 'Cash',
      account_id: ''
    });
    setIsEdit(true);
    setShowModal(true);
  };

  const handleShowDistModal = (asset) => {
    setDistAsset(asset);
    setDistForm({ location: '', quantity: 1, notes: '' });
    setShowDistModal(true);
  };

  const handleDistSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/api/v1/assets/list/${distAsset.id}/distributions`, {
        ...distForm,
        quantity: parseInt(distForm.quantity, 10),
        notes: distForm.notes || null
      });
      Swal.fire('Success', 'Asset distributed successfully', 'success');
      setShowDistModal(false);
      fetchAssets();
    } catch (error) {
      const detail = error.response?.data?.detail;
      const errorMessage = Array.isArray(detail) ? detail.map(d => `${d.loc.join('.')}: ${d.msg}`).join(', ') : (detail || 'Distribution failed');
      Swal.fire('Error', errorMessage, 'error');
    }
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
        await api.delete(`/api/v1/assets/list/${id}`);
        Swal.fire('Deleted!', 'Asset has been deleted.', 'success');
        fetchAssets();
      } catch (error) {
        Swal.fire('Error!', error.response?.data?.detail || 'Deletion failed', 'error');
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const quantity = parseInt(currentAsset.quantity, 10) || 1;
      const costPrice = parseFloat(currentAsset.cost_price) || 0;
      const totalCost = quantity * costPrice;
      const amountPaid = parseFloat(currentAsset.amount_paid) || 0;

      if (!isEdit && amountPaid > totalCost) {
        Swal.fire('Error', `Amount paid (${amountPaid.toLocaleString()}) cannot exceed total cost (${totalCost.toLocaleString()}).`, 'error');
        return;
      }

      if (!isEdit && amountPaid > 0 && !currentAsset.account_id) {
        Swal.fire('Error', 'Please select a Financial Account for the upfront payment.', 'error');
        return;
      }

      const payload = {
        name: currentAsset.name,
        description: currentAsset.description || null,
        purchase_date: currentAsset.purchase_date || null,
        cost_price: costPrice,
        quantity: quantity,
        condition: currentAsset.condition,
        depreciation_rate: parseFloat(currentAsset.depreciation_rate) || 0,
        status: currentAsset.status
      };

      if (!isEdit) {
        payload.amount_paid = amountPaid;
        if (amountPaid > 0) {
          payload.payment_method = currentAsset.payment_method;
          payload.account_id = parseInt(currentAsset.account_id, 10);
        }
      }

      if (isEdit) {
        await api.put(`/api/v1/assets/list/${currentAsset.id}`, payload);
        Swal.fire('Success', 'Asset updated successfully', 'success');
      } else {
        await api.post('/api/v1/assets/list/', payload);
        Swal.fire('Success', 'Asset added successfully and payment recorded in finance', 'success');
      }
      handleCloseModal();
      fetchAssets();
    } catch (error) {
      const detail = error.response?.data?.detail;
      const errorMessage = Array.isArray(detail) ? detail.map(d => `${d.loc.join('.')}: ${d.msg}`).join(', ') : (detail || 'Submission failed');
      Swal.fire('Error', errorMessage, 'error');
    }
  };

  // Payment Handler
  const handleShowPaymentModal = (asset) => {
    const totalCost = (asset.quantity || 1) * parseFloat(asset.cost_price || 0);
    const amountPaid = parseFloat(asset.amount_paid || 0);
    const remaining = Math.max(0, totalCost - amountPaid);

    setPaymentAsset(asset);
    setPaymentForm({
      amount: remaining > 0 ? remaining : '',
      payment_method: 'Cash',
      account_id: ''
    });
    setShowPaymentModal(true);
  };

  const handlePaymentSubmit = async (e) => {
    e.preventDefault();
    if (!paymentAsset) return;

    const totalCost = (paymentAsset.quantity || 1) * parseFloat(paymentAsset.cost_price || 0);
    const amountPaid = parseFloat(paymentAsset.amount_paid || 0);
    const remaining = Math.max(0, totalCost - amountPaid);
    const payAmount = parseFloat(paymentForm.amount) || 0;

    if (payAmount <= 0) {
      Swal.fire('Error', 'Payment amount must be greater than zero.', 'error');
      return;
    }

    if (payAmount > remaining) {
      Swal.fire('Error', `Payment amount (${payAmount.toLocaleString()}) cannot exceed remaining balance of ${remaining.toLocaleString()}.`, 'error');
      return;
    }

    if (!paymentForm.account_id) {
      Swal.fire('Error', 'Please select a Financial Account for this payment.', 'error');
      return;
    }

    try {
      await api.post(`/api/v1/assets/list/${paymentAsset.id}/payments/`, {
        amount: payAmount,
        payment_method: paymentForm.payment_method,
        account_id: parseInt(paymentForm.account_id, 10)
      });

      Swal.fire('Success', 'Asset payment successfully recorded and tracked in finance!', 'success');
      setShowPaymentModal(false);
      fetchAssets();
      
      // If view modal is open for this asset, refresh its payment history
      if (showViewModal && selectedAsset && selectedAsset.id === paymentAsset.id) {
        handleViewAsset(paymentAsset.id);
      }
    } catch (error) {
      const detail = error.response?.data?.detail;
      const errorMessage = Array.isArray(detail) ? detail.map(d => `${d.loc.join('.')}: ${d.msg}`).join(', ') : (detail || 'Payment failed');
      Swal.fire('Error', errorMessage, 'error');
    }
  };

  // View Details & Payment History Handler
  const handleViewAsset = async (assetId) => {
    try {
      const res = await api.get(`/api/v1/assets/list/${assetId}`);
      setSelectedAsset(res.data);
      setShowViewModal(true);
      setLoadingPayments(true);
      
      const payRes = await api.get(`/api/v1/assets/list/${assetId}/payments/`);
      setAssetPayments(payRes.data || []);
    } catch (error) {
      console.error("Failed to load asset details", error);
      Swal.fire('Error', 'Failed to fetch asset details', 'error');
    } finally {
      setLoadingPayments(false);
    }
  };

  const formatCurrency = (amount) => {
    return Number(amount || 0).toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 2 });
  };

  const getAccountName = (accId) => {
    const acc = accounts.find(a => a.id === accId);
    return acc ? `${acc.name} (${acc.account_type})` : `Account #${accId}`;
  };

  return (
    <>
      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <div className="d-block mb-4 mb-md-0">
          <h4>{t('assets', 'Assets')}</h4>
          <p className="mb-0">{t('manage_assets', 'Manage farm assets, equipment, and financial tracking.')}</p>
        </div>
        <div className="btn-toolbar mb-2 mb-md-0">
          <Button variant="primary" size="sm" onClick={handleShowAddModal}>
            <FontAwesomeIcon icon={faPlus} className="me-2" /> Add Asset
          </Button>
        </div>
      </div>

      <div className="table-settings mb-4">
        <Row className="justify-content-between align-items-center">
          <Col xs={8} md={6} lg={3} xl={4}>
            <InputGroup>
              <InputGroup.Text><FontAwesomeIcon icon={faSearch} /></InputGroup.Text>
              <Form.Control type="text" placeholder={t('search', 'Search')} value={searchTerm} onChange={handleSearch} />
            </InputGroup>
          </Col>
        </Row>
      </div>

      <Card border="light" className="table-wrapper table-responsive shadow-sm">
        <Card.Body className="pt-0">
          <Table hover className="user-table align-items-center">
            <thead>
              <tr>
                <th className="border-bottom">{t('asset_code', 'Code')}</th>
                <th className="border-bottom">{t('name', 'Name')}</th>
                <th className="border-bottom">{t('quantity', 'Qty')}</th>
                <th className="border-bottom">{t('cost_price', 'Unit Cost')}</th>
                <th className="border-bottom">{t('total_cost', 'Total Cost')}</th>
                <th className="border-bottom">{t('amount_paid', 'Paid')}</th>
                <th className="border-bottom">{t('balance', 'Balance')}</th>
                <th className="border-bottom">{t('payment_status', 'Payment')}</th>
                <th className="border-bottom">{t('status', 'Status')}</th>
                <th className="border-bottom text-center">{t('actions', 'Actions')}</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="10" className="text-center py-4">Loading assets...</td></tr>
              ) : assets.length === 0 ? (
                <tr><td colSpan="10" className="text-center py-4">No assets found.</td></tr>
              ) : (
                assets.map(asset => {
                  const totalCost = (asset.quantity || 1) * parseFloat(asset.cost_price || 0);
                  const amountPaid = parseFloat(asset.amount_paid || 0);
                  const balance = Math.max(0, totalCost - amountPaid);
                  const paymentStatus = asset.payment_status || (balance === 0 ? 'PAID' : amountPaid > 0 ? 'PARTIAL' : 'UNPAID');

                  return (
                    <tr key={asset.id}>
                      <td><span className="fw-bold text-primary">{asset.asset_code}</span></td>
                      <td>
                        <span className="fw-bold text-dark">{asset.name}</span>
                        {asset.description && <div className="small text-muted text-truncate" style={{ maxWidth: '180px' }}>{asset.description}</div>}
                      </td>
                      <td>
                        <span className="fw-bold">{asset.quantity}</span>
                        {asset.distributions && asset.distributions.length > 0 && (
                          <div className="small text-muted">{asset.distributions.length} loc</div>
                        )}
                      </td>
                      <td><span className="fw-normal">{formatCurrency(asset.cost_price)}</span></td>
                      <td><span className="fw-bold">{formatCurrency(totalCost)}</span></td>
                      <td><span className="fw-normal text-success">{formatCurrency(amountPaid)}</span></td>
                      <td>
                        <span className={`fw-bold ${balance > 0 ? 'text-danger' : 'text-muted'}`}>
                          {formatCurrency(balance)}
                        </span>
                      </td>
                      <td>
                        <Badge bg={paymentStatus === 'PAID' ? 'success' : paymentStatus === 'PARTIAL' ? 'warning' : 'danger'}>
                          {paymentStatus}
                        </Badge>
                      </td>
                      <td>
                        <Badge bg={asset.status === 'Active' ? 'success' : asset.status === 'Maintenance' ? 'warning' : 'secondary'}>
                          {asset.status}
                        </Badge>
                      </td>
                      <td className="text-center">
                        <Button variant="secondary" size="sm" className="me-1" onClick={() => handleViewAsset(asset.id)} title="View Details & Payments">
                          <FontAwesomeIcon icon={faEye} />
                        </Button>
                        {paymentStatus !== 'PAID' && (
                          <Button variant="success" size="sm" className="me-1" onClick={() => handleShowPaymentModal(asset)} title="Add Payment">
                            <FontAwesomeIcon icon={faMoneyBillWave} />
                          </Button>
                        )}
                        <Button variant="primary" size="sm" className="me-1" onClick={() => handleShowDistModal(asset)} title="Distribute Asset">
                          <FontAwesomeIcon icon={faShareAlt} />
                        </Button>
                        <Button variant="info" size="sm" className="me-1" onClick={() => handleShowEditModal(asset)} title="Edit Asset">
                          <FontAwesomeIcon icon={faEdit} />
                        </Button>
                        <Button variant="danger" size="sm" onClick={() => handleDelete(asset.id)} title="Delete Asset">
                          <FontAwesomeIcon icon={faTrash} />
                        </Button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </Table>
          <Card.Footer className="px-3 border-0 d-lg-flex align-items-center justify-content-between">
            <Nav>
              <Pagination className="mb-2 mb-lg-0">
                <Pagination.Prev disabled={page === 1} onClick={() => handlePageChange(page - 1)}>Previous</Pagination.Prev>
                <Pagination.Item active>{page}</Pagination.Item>
                <Pagination.Next disabled={page === totalPages || totalPages === 0} onClick={() => handlePageChange(page + 1)}>Next</Pagination.Next>
              </Pagination>
            </Nav>
            <small className="fw-bold">
              Showing page <b>{page}</b> out of <b>{totalPages}</b>
            </small>
          </Card.Footer>
        </Card.Body>
      </Card>

      {/* ADD / EDIT ASSET MODAL */}
      <Modal as={Modal} show={showModal} onHide={handleCloseModal} size="lg">
        <Form onSubmit={handleSubmit}>
          <Modal.Header>
            <Modal.Title className="h6">{isEdit ? 'Edit Asset' : 'Add New Farm Asset'}</Modal.Title>
            <Button variant="close" aria-label="Close" onClick={handleCloseModal} />
          </Modal.Header>
          <Modal.Body>
            <Row>
              <Col md={8} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('name', 'Asset Name')} *</Form.Label>
                  <Form.Control required type="text" placeholder="e.g. Electric Generator 15kVA" value={currentAsset.name} onChange={(e) => setCurrentAsset({...currentAsset, name: e.target.value})} />
                </Form.Group>
              </Col>
              <Col md={4} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('purchase_date', 'Purchase Date')}</Form.Label>
                  <Form.Control type="date" value={currentAsset.purchase_date || ''} onChange={(e) => setCurrentAsset({...currentAsset, purchase_date: e.target.value})} />
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={12} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('description', 'Description')}</Form.Label>
                  <Form.Control as="textarea" rows={2} placeholder="Optional asset details, serial number, or vendor info..." value={currentAsset.description || ''} onChange={(e) => setCurrentAsset({...currentAsset, description: e.target.value})} />
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={4} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('quantity', 'Total Quantity')} *</Form.Label>
                  <Form.Control required type="number" min="1" value={currentAsset.quantity} onChange={(e) => setCurrentAsset({...currentAsset, quantity: e.target.value})} />
                </Form.Group>
              </Col>
              <Col md={4} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('cost_price', 'Unit Cost (FCFA)')} *</Form.Label>
                  <Form.Control required type="number" step="0.01" min="0" value={currentAsset.cost_price} onChange={(e) => setCurrentAsset({...currentAsset, cost_price: e.target.value})} />
                </Form.Group>
              </Col>
              <Col md={4} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('total_cost', 'Total Asset Cost')}</Form.Label>
                  <Form.Control 
                    disabled 
                    type="text" 
                    className="fw-bold bg-light"
                    value={formatCurrency((parseInt(currentAsset.quantity, 10) || 1) * (parseFloat(currentAsset.cost_price) || 0))} 
                  />
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={4} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('condition', 'Condition')}</Form.Label>
                  <Form.Select required value={currentAsset.condition} onChange={(e) => setCurrentAsset({...currentAsset, condition: e.target.value})}>
                    <option value="New">New</option>
                    <option value="Good">Good</option>
                    <option value="Fair">Fair</option>
                    <option value="Poor">Poor</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={4} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('depreciation_rate', 'Depreciation Rate (%/yr)')}</Form.Label>
                  <Form.Control type="number" step="0.01" min="0" value={currentAsset.depreciation_rate} onChange={(e) => setCurrentAsset({...currentAsset, depreciation_rate: e.target.value})} />
                </Form.Group>
              </Col>
              <Col md={4} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('status', 'Operational Status')}</Form.Label>
                  <Form.Select required value={currentAsset.status} onChange={(e) => setCurrentAsset({...currentAsset, status: e.target.value})}>
                    <option value="Active">Active</option>
                    <option value="Maintenance">Maintenance</option>
                    <option value="Disposed">Disposed</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>

            {/* Financial Payment Section (Only upon Creation) */}
            {!isEdit && (
              <div className="border rounded p-3 bg-light mt-2 mb-2">
                <h6 className="text-primary mb-3">Finance & Payment Settlement</h6>
                <Row>
                  <Col md={4} className="mb-3">
                    <Form.Group>
                      <Form.Label>Amount Paid (FCFA)</Form.Label>
                      <Form.Control 
                        type="number" 
                        step="0.01" 
                        min="0"
                        placeholder="0.00"
                        value={currentAsset.amount_paid} 
                        onChange={(e) => setCurrentAsset({...currentAsset, amount_paid: e.target.value})} 
                      />
                      <Form.Text className="text-muted">
                        Leave 0 if purchased on credit (Unpaid).
                      </Form.Text>
                    </Form.Group>
                  </Col>
                  
                  {parseFloat(currentAsset.amount_paid) > 0 && (
                    <>
                      <Col md={4} className="mb-3">
                        <Form.Group>
                          <Form.Label>Payment Method *</Form.Label>
                          <Form.Select 
                            required 
                            value={currentAsset.payment_method} 
                            onChange={(e) => setCurrentAsset({...currentAsset, payment_method: e.target.value})}
                          >
                            <option value="Cash">Cash</option>
                            <option value="Bank Transfer">Bank Transfer</option>
                            <option value="Mobile Money">Mobile Money</option>
                          </Form.Select>
                        </Form.Group>
                      </Col>

                      <Col md={4} className="mb-3">
                        <Form.Group>
                          <Form.Label>Payment Account *</Form.Label>
                          <Form.Select 
                            required 
                            value={currentAsset.account_id} 
                            onChange={(e) => setCurrentAsset({...currentAsset, account_id: e.target.value})}
                          >
                            <option value="">-- Select Financial Account --</option>
                            {accounts.map(acc => (
                              <option key={acc.id} value={acc.id}>
                                {acc.name} ({acc.account_type})
                              </option>
                            ))}
                          </Form.Select>
                          <Form.Text className="text-muted">Account money is paid from.</Form.Text>
                        </Form.Group>
                      </Col>
                    </>
                  )}
                </Row>
              </div>
            )}
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleCloseModal}>Cancel</Button>
            <Button variant="primary" type="submit">{isEdit ? 'Update Asset' : 'Save Asset & Record Payment'}</Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* ADD PAYMENT MODAL */}
      <Modal as={Modal} show={showPaymentModal} onHide={() => setShowPaymentModal(false)} centered>
        <Form onSubmit={handlePaymentSubmit}>
          <Modal.Header closeButton>
            <Modal.Title className="h6">Record Asset Payment</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            {paymentAsset && (
              <div className="border rounded p-3 mb-3 bg-light">
                <div className="d-flex justify-content-between mb-1">
                  <span className="text-muted">Asset Code:</span>
                  <span className="fw-bold">{paymentAsset.asset_code}</span>
                </div>
                <div className="d-flex justify-content-between mb-1">
                  <span className="text-muted">Asset Name:</span>
                  <span className="fw-bold">{paymentAsset.name}</span>
                </div>
                <div className="d-flex justify-content-between mb-1">
                  <span className="text-muted">Total Cost:</span>
                  <span className="fw-bold">
                    {formatCurrency((paymentAsset.quantity || 1) * parseFloat(paymentAsset.cost_price || 0))} FCFA
                  </span>
                </div>
                <div className="d-flex justify-content-between mb-1">
                  <span className="text-muted">Total Paid:</span>
                  <span className="fw-bold text-success">{formatCurrency(paymentAsset.amount_paid)} FCFA</span>
                </div>
                <div className="d-flex justify-content-between pt-2 border-top mt-2">
                  <span className="fw-bold text-dark">Remaining Balance:</span>
                  <span className="fw-bold text-danger">
                    {formatCurrency(Math.max(0, ((paymentAsset.quantity || 1) * parseFloat(paymentAsset.cost_price || 0)) - parseFloat(paymentAsset.amount_paid || 0)))} FCFA
                  </span>
                </div>
              </div>
            )}

            <Form.Group className="mb-3">
              <Form.Label>Payment Amount (FCFA) *</Form.Label>
              <Form.Control 
                required 
                type="number" 
                step="0.01" 
                min="0.01" 
                value={paymentForm.amount} 
                onChange={(e) => setPaymentForm({...paymentForm, amount: e.target.value})} 
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Payment Method *</Form.Label>
              <Form.Select 
                required 
                value={paymentForm.payment_method} 
                onChange={(e) => setPaymentForm({...paymentForm, payment_method: e.target.value})}
              >
                <option value="Cash">Cash</option>
                <option value="Bank Transfer">Bank Transfer</option>
                <option value="Mobile Money">Mobile Money</option>
              </Form.Select>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Financial Account *</Form.Label>
              <Form.Select 
                required 
                value={paymentForm.account_id} 
                onChange={(e) => setPaymentForm({...paymentForm, account_id: e.target.value})}
              >
                <option value="">-- Select Financial Account --</option>
                {accounts.map(acc => (
                  <option key={acc.id} value={acc.id}>
                    {acc.name} ({acc.account_type})
                  </option>
                ))}
              </Form.Select>
              <Form.Text className="text-muted">
                The account from which funds will be deducted.
              </Form.Text>
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowPaymentModal(false)}>Cancel</Button>
            <Button variant="success" type="submit">Confirm & Post Payment</Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* VIEW DETAILS & PAYMENT HISTORY MODAL */}
      <Modal as={Modal} show={showViewModal} onHide={() => setShowViewModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title className="h6">Asset Details & Financial History</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedAsset && (
            <div>
              {/* Asset Information Card */}
              <div className="border rounded p-3 mb-4 bg-light">
                <Row>
                  <Col md={6}>
                    <p className="mb-1"><strong>Asset Code:</strong> <span className="text-primary fw-bold">{selectedAsset.asset_code}</span></p>
                    <p className="mb-1"><strong>Name:</strong> {selectedAsset.name}</p>
                    <p className="mb-1"><strong>Condition:</strong> {selectedAsset.condition}</p>
                    <p className="mb-1"><strong>Status:</strong> <Badge bg={selectedAsset.status === 'Active' ? 'success' : selectedAsset.status === 'Maintenance' ? 'warning' : 'secondary'}>{selectedAsset.status}</Badge></p>
                    {selectedAsset.description && <p className="mb-1"><strong>Description:</strong> {selectedAsset.description}</p>}
                  </Col>
                  <Col md={6}>
                    <p className="mb-1"><strong>Purchase Date:</strong> {selectedAsset.purchase_date ? new Date(selectedAsset.purchase_date).toLocaleDateString() : 'N/A'}</p>
                    <p className="mb-1"><strong>Quantity:</strong> {selectedAsset.quantity}</p>
                    <p className="mb-1"><strong>Unit Cost:</strong> {formatCurrency(selectedAsset.cost_price)} FCFA</p>
                    <p className="mb-1"><strong>Total Cost:</strong> <span className="fw-bold">{formatCurrency((selectedAsset.quantity || 1) * parseFloat(selectedAsset.cost_price || 0))} FCFA</span></p>
                    <p className="mb-1"><strong>Amount Paid:</strong> <span className="text-success fw-bold">{formatCurrency(selectedAsset.amount_paid)} FCFA</span></p>
                    <p className="mb-1">
                      <strong>Remaining Balance:</strong>{' '}
                      <span className={`fw-bold ${((selectedAsset.quantity || 1) * parseFloat(selectedAsset.cost_price || 0)) - parseFloat(selectedAsset.amount_paid || 0) > 0 ? 'text-danger' : 'text-success'}`}>
                        {formatCurrency(Math.max(0, ((selectedAsset.quantity || 1) * parseFloat(selectedAsset.cost_price || 0)) - parseFloat(selectedAsset.amount_paid || 0)))} FCFA
                      </span>
                    </p>
                    <p className="mb-1">
                      <strong>Payment Status:</strong>{' '}
                      <Badge bg={selectedAsset.payment_status === 'PAID' ? 'success' : selectedAsset.payment_status === 'PARTIAL' ? 'warning' : 'danger'}>
                        {selectedAsset.payment_status}
                      </Badge>
                    </p>
                  </Col>
                </Row>
              </div>

              {/* Payment History Section */}
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h6 className="mb-0 text-dark">Payment History (Ledger Settlements)</h6>
                {selectedAsset.payment_status !== 'PAID' && (
                  <Button variant="success" size="sm" onClick={() => { setShowViewModal(false); handleShowPaymentModal(selectedAsset); }}>
                    <FontAwesomeIcon icon={faMoneyBillWave} className="me-1" /> Add Payment
                  </Button>
                )}
              </div>

              {loadingPayments ? (
                <p className="text-center text-muted py-3">Loading payments...</p>
              ) : assetPayments.length === 0 ? (
                <div className="text-center py-4 border rounded text-muted">
                  No payment records found for this asset.
                </div>
              ) : (
                <Table size="sm" bordered hover className="mb-3">
                  <thead className="bg-light">
                    <tr>
                      <th>Ref Number</th>
                      <th>Date</th>
                      <th>Method</th>
                      <th>Account</th>
                      <th className="text-end">Amount (FCFA)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {assetPayments.map(p => (
                      <tr key={p.id}>
                        <td className="fw-bold">{p.payment_reference}</td>
                        <td>{new Date(p.payment_date).toLocaleDateString()}</td>
                        <td>{p.payment_method}</td>
                        <td>{getAccountName(p.account_id)}</td>
                        <td className="text-end fw-bold text-success">{formatCurrency(p.amount)}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}

              {/* Distributions Section */}
              {selectedAsset.distributions && selectedAsset.distributions.length > 0 && (
                <div className="mt-4">
                  <h6 className="mb-2 text-dark">Asset Allocations / Distributions</h6>
                  <Table size="sm" bordered hover>
                    <thead className="bg-light">
                      <tr>
                        <th>Location</th>
                        <th>Quantity</th>
                        <th>Notes</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedAsset.distributions.map(d => (
                        <tr key={d.id}>
                          <td>{d.location}</td>
                          <td>{d.quantity}</td>
                          <td>{d.notes || '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </div>
              )}
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowViewModal(false)}>Close</Button>
        </Modal.Footer>
      </Modal>

      {/* ASSET DISTRIBUTION MODAL */}
      <Modal as={Modal} show={showDistModal} onHide={() => setShowDistModal(false)} size="lg">
        <Form onSubmit={handleDistSubmit}>
          <Modal.Header>
            <Modal.Title className="h6">Distribute Asset: {distAsset?.name}</Modal.Title>
            <Button variant="close" aria-label="Close" onClick={() => setShowDistModal(false)} />
          </Modal.Header>
          <Modal.Body>
            <div className="mb-4">
              <strong>Total Quantity Available:</strong> {distAsset?.quantity}
              <br />
              <strong>Already Distributed:</strong> {distAsset?.distributions?.reduce((sum, d) => sum + d.quantity, 0) || 0}
            </div>

            {distAsset?.distributions && distAsset.distributions.length > 0 && (
              <Table size="sm" bordered hover className="mb-4">
                <thead className="bg-light">
                  <tr>
                    <th>Location</th>
                    <th>Quantity</th>
                    <th>Notes</th>
                  </tr>
                </thead>
                <tbody>
                  {distAsset.distributions.map(d => (
                    <tr key={d.id}>
                      <td>{d.location}</td>
                      <td>{d.quantity}</td>
                      <td>{d.notes || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            )}

            <h6 className="border-bottom pb-2 mb-3">New Distribution</h6>
            <Row>
              <Col md={6} className="mb-3">
                <Form.Group>
                  <Form.Label>Target Location / House</Form.Label>
                  <Form.Control required type="text" placeholder="e.g. House A" value={distForm.location} onChange={e => setDistForm({...distForm, location: e.target.value})} />
                </Form.Group>
              </Col>
              <Col md={6} className="mb-3">
                <Form.Group>
                  <Form.Label>Quantity to Allocate</Form.Label>
                  <Form.Control required type="number" min="1" max={distAsset ? distAsset.quantity - (distAsset.distributions?.reduce((sum, d) => sum + d.quantity, 0) || 0) : 1} value={distForm.quantity} onChange={e => setDistForm({...distForm, quantity: e.target.value})} />
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={12} className="mb-3">
                <Form.Group>
                  <Form.Label>Notes</Form.Label>
                  <Form.Control as="textarea" rows={2} value={distForm.notes} onChange={e => setDistForm({...distForm, notes: e.target.value})} />
                </Form.Group>
              </Col>
            </Row>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowDistModal(false)}>Cancel</Button>
            <Button variant="primary" type="submit">Allocate</Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </>
  );
};
