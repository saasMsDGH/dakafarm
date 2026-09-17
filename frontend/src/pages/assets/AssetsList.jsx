import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faEdit, faTrash, faSearch, faShareAlt } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, Button, Modal, Form, InputGroup, Pagination, Badge, Nav } from '@themesberg/react-bootstrap';
import { useTranslation } from 'react-i18next';
import { api } from "../../api/axios";
import Swal from 'sweetalert2';

export default () => {
  const { t } = useTranslation();
  
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  
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
    purchase_date: '',
    cost_price: '0.00',
    quantity: 1,
    condition: 'Good',
    depreciation_rate: '0.00',
    status: 'Active'
  });

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

  useEffect(() => {
    fetchAssets();
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
      purchase_date: '',
      cost_price: '0.00',
    quantity: 1,
      condition: 'Good',
      depreciation_rate: '0.00',
      status: 'Active'
    });
    setIsEdit(false);
  };

  const handleShowAddModal = () => {
    setIsEdit(false);
    setShowModal(true);
  };

  const handleShowEditModal = (asset) => {
    setCurrentAsset({ ...asset });
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
      const payload = {
        ...currentAsset,
        quantity: parseInt(currentAsset.quantity, 10) || 1,
        cost_price: parseFloat(currentAsset.cost_price) || 0,
        depreciation_rate: parseFloat(currentAsset.depreciation_rate) || 0
      };

      if (!payload.purchase_date) payload.purchase_date = null;
      if (!payload.description) payload.description = null;

      if (isEdit) {
        await api.put(`/api/v1/assets/list/${currentAsset.id}`, payload);
        Swal.fire('Success', 'Asset updated successfully', 'success');
      } else {
        await api.post('/api/v1/assets/list/', payload);
        Swal.fire('Success', 'Asset added successfully', 'success');
      }
      handleCloseModal();
      fetchAssets();
    } catch (error) {
      const detail = error.response?.data?.detail;
      const errorMessage = Array.isArray(detail) ? detail.map(d => `${d.loc.join('.')}: ${d.msg}`).join(', ') : (detail || 'Submission failed');
      Swal.fire('Error', errorMessage, 'error');
    }
  };

  const formatCurrency = (amount) => {
    return Number(amount).toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 2 });
  };

  return (
    <>
      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <div className="d-block mb-4 mb-md-0">
          <h4>{t('assets', 'Assets')}</h4>
          <p className="mb-0">{t('manage_assets', 'Manage farm assets and equipment.')}</p>
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
                <th className="border-bottom">{t('quantity', 'Quantity')}</th>
                <th className="border-bottom">{t('condition', 'Condition')}</th>
                <th className="border-bottom">{t('cost_price', 'Cost')}</th>
                <th className="border-bottom">{t('status', 'Status')}</th>
                <th className="border-bottom">{t('actions', 'Actions')}</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="7" className="text-center">Loading...</td></tr>
              ) : assets.length === 0 ? (
                <tr><td colSpan="7" className="text-center">No assets found.</td></tr>
              ) : (
                assets.map(asset => (
                  <tr key={asset.id}>
                    <td><span className="fw-bold text-primary">{asset.asset_code}</span></td>
                    <td>
                      <span className="fw-normal">{asset.name}</span>
                      </td>
                    <td>
                      <span className="fw-bold">{asset.quantity}</span>
                      {asset.distributions && asset.distributions.length > 0 && (
                        <div className="small text-muted">{asset.distributions.length} allocations</div>
                      )}
                    </td>
                    <td><span className="fw-normal">{asset.condition}</span></td>
                    <td><span className="fw-bold">{formatCurrency(asset.cost_price)}</span></td>
                    <td>
                      <Badge bg={asset.status === 'Active' ? 'success' : asset.status === 'Maintenance' ? 'warning' : 'danger'}>
                        {asset.status}
                      </Badge>
                    </td>
                    <td>
                      
                      <Button variant="success" size="sm" className="me-2" onClick={() => handleShowDistModal(asset)} title="Distribute Asset">
                        <FontAwesomeIcon icon={faShareAlt} />
                      </Button>
                      <Button variant="info" size="sm" className="me-2" onClick={() => handleShowEditModal(asset)}>
                        <FontAwesomeIcon icon={faEdit} />
                      </Button>
                      <Button variant="danger" size="sm" onClick={() => handleDelete(asset.id)}>
                        <FontAwesomeIcon icon={faTrash} />
                      </Button>
                    </td>
                  </tr>
                ))
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

      <Modal as={Modal} show={showModal} onHide={handleCloseModal} size="lg">
        <Form onSubmit={handleSubmit}>
          <Modal.Header>
            <Modal.Title className="h6">{isEdit ? 'Edit Asset' : 'Add Asset'}</Modal.Title>
            <Button variant="close" aria-label="Close" onClick={handleCloseModal} />
          </Modal.Header>
          <Modal.Body>
            <Row>
              <Col md={12} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('name', 'Asset Name')}</Form.Label>
                  <Form.Control required type="text" value={currentAsset.name} onChange={(e) => setCurrentAsset({...currentAsset, name: e.target.value})} />
                </Form.Group>
              </Col>
              </Row>
            <Row>
              <Col md={12} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('description', 'Description')}</Form.Label>
                  <Form.Control as="textarea" rows={2} value={currentAsset.description || ''} onChange={(e) => setCurrentAsset({...currentAsset, description: e.target.value})} />
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={12} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('purchase_date', 'Purchase Date')}</Form.Label>
                  <Form.Control type="date" value={currentAsset.purchase_date || ''} onChange={(e) => setCurrentAsset({...currentAsset, purchase_date: e.target.value})} />
                </Form.Group>
              </Col>
            </Row>
            <Row>
              
              <Col md={4} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('quantity', 'Total Quantity')}</Form.Label>
                  <Form.Control type="number" min="1" value={currentAsset.quantity} onChange={(e) => setCurrentAsset({...currentAsset, quantity: e.target.value})} />
                </Form.Group>
              </Col>
              <Col md={4} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('cost_price', 'Cost Price')}</Form.Label>
                  <Form.Control type="number" step="0.01" value={currentAsset.cost_price} onChange={(e) => setCurrentAsset({...currentAsset, cost_price: e.target.value})} />
                </Form.Group>
              </Col>
              <Col md={4} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('depreciation_rate', 'Depreciation Rate (%)')}</Form.Label>
                  <Form.Control type="number" step="0.01" value={currentAsset.depreciation_rate} onChange={(e) => setCurrentAsset({...currentAsset, depreciation_rate: e.target.value})} />
                </Form.Group>
              </Col>
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
            </Row>
            <Row>
              <Col md={12} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('status', 'Status')}</Form.Label>
                  <Form.Select required value={currentAsset.status} onChange={(e) => setCurrentAsset({...currentAsset, status: e.target.value})}>
                    <option value="Active">Active</option>
                    <option value="Maintenance">Maintenance</option>
                    <option value="Disposed">Disposed</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleCloseModal}>Cancel</Button>
            <Button variant="primary" type="submit">Save Asset</Button>
          </Modal.Footer>
        </Form>
      </Modal>

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
