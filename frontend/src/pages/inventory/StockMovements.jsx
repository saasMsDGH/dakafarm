import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faSearch } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, Button, Modal, Form, InputGroup, Pagination } from '@themesberg/react-bootstrap';
import { useTranslation } from 'react-i18next';
import { api } from "../../api/axios";
import Swal from 'sweetalert2';

export default () => {
  const { t } = useTranslation();
  
  const [movements, setMovements] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  
  const [showModal, setShowModal] = useState(false);
  const [currentMovement, setCurrentMovement] = useState({
    product_id: '',
    movement_type: 'IN',
    quantity: '',
    reference_type: '',
    reference_id: ''
  });

  const fetchProducts = async () => {
    try {
      const response = await api.get('/api/v1/inventory/products/', { params: { limit: 100 } });
      setProducts(response.data.items);
    } catch (error) {
      console.error("Failed to fetch products:", error);
    }
  };

  const fetchMovements = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/inventory/movements/', {
        params: { page, limit: 10, search: searchTerm }
      });
      setMovements(response.data.items);
      setTotalPages(response.data.pages || 1);
    } catch (error) {
      console.error("Failed to fetch movements:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  useEffect(() => {
    fetchMovements();
  }, [page, searchTerm]);

  const handleShowModal = () => {
    setCurrentMovement({
      product_id: '',
      movement_type: 'IN',
      quantity: '',
      reference_type: '',
      reference_id: ''
    });
    setShowModal(true);
  };

  const handleCloseModal = () => setShowModal(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setCurrentMovement({ ...currentMovement, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...currentMovement,
        product_id: parseInt(currentMovement.product_id),
        quantity: parseFloat(currentMovement.quantity)
      };
      
      if (payload.reference_id) {
          payload.reference_id = parseInt(payload.reference_id);
      } else {
          payload.reference_id = null;
      }
      
      if (!payload.reference_type) {
          payload.reference_type = null;
      }

      await api.post('/api/v1/inventory/movements/', payload);
      Swal.fire('Saved!', 'The stock movement has been recorded.', 'success');
      
      handleCloseModal();
      fetchMovements();
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'An error occurred while saving.';
      Swal.fire('Error', errorMsg, 'error');
    }
  };

  const getProductDisplay = (prodId) => {
    const prod = products.find(p => p.id === prodId);
    return prod ? prod.name : prodId;
  };

  return (
    <>
      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <div className="d-block mb-4 mb-md-0">
          <h4>{t('stock_movements', 'Stock Movements')}</h4>
        </div>
        <div className="btn-toolbar mb-2 mb-md-0">
          <Button variant="primary" size="sm" onClick={() => handleShowModal()}>
            <FontAwesomeIcon icon={faPlus} className="me-2" /> {t('add_movement', 'Add Movement')}
          </Button>
        </div>
      </div>

      <div className="table-settings mb-4">
        <Row className="justify-content-between align-items-center">
          <Col xs={8} md={6} lg={3} xl={4}>
            <InputGroup>
              <InputGroup.Text><FontAwesomeIcon icon={faSearch} /></InputGroup.Text>
              <Form.Control 
                type="text" 
                placeholder={t('search', 'Search...')} 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
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
                <th className="border-bottom">{t('date', 'Date')}</th>
                <th className="border-bottom">{t('product', 'Product')}</th>
                <th className="border-bottom">{t('type', 'Type')}</th>
                <th className="border-bottom">{t('quantity', 'Quantity')}</th>
                <th className="border-bottom">{t('reference', 'Reference Type')}</th>
                <th className="border-bottom">Reference ID</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="6" className="text-center">Loading...</td></tr>
              ) : movements.length === 0 ? (
                <tr><td colSpan="6" className="text-center">No movements found</td></tr>
              ) : (
                movements.map(mov => (
                  <tr key={mov.id}>
                    <td><span className="fw-normal">{new Date(mov.created_at).toLocaleString()}</span></td>
                    <td><span className="fw-normal">{getProductDisplay(mov.product_id)}</span></td>
                    <td>
                      <span className={`fw-bold text-${mov.movement_type === 'IN' ? 'success' : mov.movement_type === 'OUT' ? 'danger' : 'warning'}`}>
                        {mov.movement_type}
                      </span>
                    </td>
                    <td><span className="fw-normal">{mov.quantity}</span></td>
                    <td><span className="fw-normal">{mov.reference_type || '-'}</span></td>
                    <td><span className="fw-normal">{mov.reference_id || '-'}</span></td>
                  </tr>
                ))
              )}
            </tbody>
          </Table>
          
          <Card.Footer className="px-3 border-0 d-flex flex-column flex-lg-row align-items-center justify-content-between">
            <Pagination className="mb-2 mb-lg-0">
              <Pagination.Prev disabled={page === 1} onClick={() => setPage(page - 1)}>
                {t('previous', 'Previous')}
              </Pagination.Prev>
              <Pagination.Item active>{page}</Pagination.Item>
              <Pagination.Next disabled={page === totalPages || totalPages === 0} onClick={() => setPage(page + 1)}>
                {t('next', 'Next')}
              </Pagination.Next>
            </Pagination>
          </Card.Footer>
        </Card.Body>
      </Card>

      <Modal as={Modal.Dialog} centered show={showModal} onHide={handleCloseModal}>
        <Form onSubmit={handleSubmit}>
          <Modal.Header closeButton>
            <Modal.Title>{t('add_movement', 'Add Movement')}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Form.Group id="product_id" className="mb-3">
              <Form.Label>{t('select_product', 'Select Product')}</Form.Label>
              <Form.Select 
                required 
                name="product_id"
                value={currentMovement.product_id} 
                onChange={handleInputChange}
              >
                <option value="">-- {t('select_product', 'Select Product')} --</option>
                {products.map(p => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </Form.Select>
            </Form.Group>

            <Row>
              <Col md={6}>
                <Form.Group id="movement_type" className="mb-3">
                  <Form.Label>{t('movement_type', 'Movement Type')}</Form.Label>
                  <Form.Select 
                    required 
                    name="movement_type"
                    value={currentMovement.movement_type} 
                    onChange={handleInputChange} 
                  >
                    <option value="IN">IN (Receive Stock)</option>
                    <option value="OUT">OUT (Use/Sell Stock)</option>
                    <option value="ADJUSTMENT">ADJUSTMENT</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group id="quantity" className="mb-3">
                  <Form.Label>{t('quantity', 'Quantity')}</Form.Label>
                  <Form.Control 
                    required 
                    type="number"
                    step="0.001" 
                    name="quantity"
                    value={currentMovement.quantity} 
                    onChange={handleInputChange} 
                  />
                </Form.Group>
              </Col>
            </Row>

            <Form.Group id="reference_type" className="mb-3">
              <Form.Label>Reference Type (Optional)</Form.Label>
              <Form.Control 
                type="text" 
                name="reference_type"
                placeholder="e.g. Manual, Purchase"
                value={currentMovement.reference_type} 
                onChange={handleInputChange} 
              />
            </Form.Group>
            
            <Form.Group id="reference_id" className="mb-3">
              <Form.Label>Reference ID (Optional)</Form.Label>
              <Form.Control 
                type="number" 
                name="reference_id"
                value={currentMovement.reference_id} 
                onChange={handleInputChange} 
              />
            </Form.Group>

          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" type="button" onClick={handleCloseModal}>
              {t('cancel', 'Cancel')}
            </Button>
            <Button variant="primary" type="submit">
              {t('save', 'Save')}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </>
  );
};
