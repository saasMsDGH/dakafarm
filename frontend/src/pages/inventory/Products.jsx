import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faEdit, faTrash, faSearch } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, Button, Modal, Form, InputGroup, Pagination } from '@themesberg/react-bootstrap';
import { useTranslation } from 'react-i18next';
import { api } from "../../api/axios";
import Swal from 'sweetalert2';

export default () => {
  const { t } = useTranslation();
  
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  
  const [showModal, setShowModal] = useState(false);
  const [isEdit, setIsEdit] = useState(false);
  const [currentProduct, setCurrentProduct] = useState({
    category_id: '',
    name: '',
    unit_of_measure: '',
    unit_price: '0.00',
    selling_price: '0.00',
    reorder_level: '0.000',
    description: '',
    is_active: true
  });

  const fetchCategories = async () => {
    try {
      const response = await api.get('/api/v1/inventory/product-categories/', { params: { limit: 100 } });
      setCategories(response.data.items);
    } catch (error) {
      console.error("Failed to fetch categories:", error);
    }
  };

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/inventory/products/', {
        params: { page, limit: 10, search: searchTerm }
      });
      setProducts(response.data.items);
      setTotalPages(response.data.pages || 1);
    } catch (error) {
      console.error("Failed to fetch products:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  useEffect(() => {
    fetchProducts();
  }, [page, searchTerm]);

  const handleShowModal = (product = null) => {
    if (product) {
      setCurrentProduct({
        ...product,
        unit_price: product.unit_price || '0.00',
        selling_price: product.selling_price || '0.00',
        reorder_level: product.reorder_level || '0.000',
      });
      setIsEdit(true);
    } else {
      setCurrentProduct({
        category_id: '',
        name: '',
        unit_of_measure: '',
        unit_price: '0.00',
        selling_price: '0.00',
        reorder_level: '0.000',
        description: '',
        is_active: true
      });
      setIsEdit(false);
    }
    setShowModal(true);
  };

  const handleCloseModal = () => setShowModal(false);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setCurrentProduct({ 
      ...currentProduct, 
      [name]: type === 'checkbox' ? checked : value 
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...currentProduct,
        category_id: parseInt(currentProduct.category_id),
        unit_price: parseFloat(currentProduct.unit_price),
        selling_price: parseFloat(currentProduct.selling_price),
        reorder_level: parseFloat(currentProduct.reorder_level)
      };

      if (isEdit) {
        await api.put(`/api/v1/inventory/products/${currentProduct.id}`, payload);
        Swal.fire('Updated!', 'The product has been updated.', 'success');
      } else {
        await api.post('/api/v1/inventory/products/', payload);
        Swal.fire('Saved!', 'The product has been added.', 'success');
      }
      handleCloseModal();
      fetchProducts();
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'An error occurred while saving.';
      Swal.fire('Error', errorMsg, 'error');
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
        await api.delete(`/api/v1/inventory/products/${id}`);
        Swal.fire('Deleted!', 'The product has been deleted.', 'success');
        fetchProducts();
      } catch (error) {
        const errorMsg = error.response?.data?.detail || 'Failed to delete.';
        Swal.fire('Error', errorMsg, 'error');
      }
    }
  };

  const getCategoryDisplay = (catId) => {
    const cat = categories.find(c => c.id === catId);
    return cat ? cat.name : catId;
  };

  return (
    <>
      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <div className="d-block mb-4 mb-md-0">
          <h4>{t('products', 'Products')}</h4>
        </div>
        <div className="btn-toolbar mb-2 mb-md-0">
          <Button variant="primary" size="sm" onClick={() => handleShowModal()}>
            <FontAwesomeIcon icon={faPlus} className="me-2" /> {t('add_product', 'Add Product')}
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
                <th className="border-bottom">{t('name', 'Name')}</th>
                <th className="border-bottom">{t('category', 'Category')}</th>
                <th className="border-bottom">{t('unit', 'Unit')}</th>
                <th className="border-bottom">{t('unit_price', 'Cost')}</th>
                <th className="border-bottom">{t('selling_price', 'Price')}</th>
                <th className="border-bottom">{t('status', 'Status')}</th>
                <th className="border-bottom">{t('actions', 'Actions')}</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="7" className="text-center">Loading...</td></tr>
              ) : products.length === 0 ? (
                <tr><td colSpan="7" className="text-center">No products found</td></tr>
              ) : (
                products.map(prod => (
                  <tr key={prod.id}>
                    <td><span className="fw-normal">{prod.name}</span></td>
                    <td><span className="fw-normal">{getCategoryDisplay(prod.category_id)}</span></td>
                    <td><span className="fw-normal">{prod.unit_of_measure}</span></td>
                    <td><span className="fw-normal">{prod.unit_price}</span></td>
                    <td><span className="fw-normal">{prod.selling_price}</span></td>
                    <td>
                      <span className={`fw-bold text-${prod.is_active ? 'success' : 'danger'}`}>
                        {prod.is_active ? t('active', 'Active') : t('inactive', 'Inactive')}
                      </span>
                    </td>
                    <td>
                      <Button variant="info" size="sm" className="me-2" onClick={() => handleShowModal(prod)}>
                        <FontAwesomeIcon icon={faEdit} />
                      </Button>
                      <Button variant="danger" size="sm" onClick={() => handleDelete(prod.id)}>
                        <FontAwesomeIcon icon={faTrash} />
                      </Button>
                    </td>
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
            <Modal.Title>{isEdit ? t('edit', 'Edit') : t('add_product', 'Add Product')}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Form.Group id="category_id" className="mb-3">
              <Form.Label>{t('select_category', 'Select Category')}</Form.Label>
              <Form.Select 
                required 
                name="category_id"
                value={currentProduct.category_id} 
                onChange={handleInputChange}
              >
                <option value="">-- {t('select_category', 'Select Category')} --</option>
                {categories.map(c => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </Form.Select>
            </Form.Group>

            <Form.Group id="name" className="mb-3">
              <Form.Label>{t('name', 'Name')}</Form.Label>
              <Form.Control 
                required 
                type="text" 
                name="name"
                value={currentProduct.name} 
                onChange={handleInputChange} 
              />
            </Form.Group>

            <Row>
              <Col md={6}>
                <Form.Group id="unit_of_measure" className="mb-3">
                  <Form.Label>{t('unit_of_measure', 'Unit of Measure')}</Form.Label>
                  <Form.Control 
                    required 
                    type="text" 
                    placeholder="e.g. kg, bags"
                    name="unit_of_measure"
                    value={currentProduct.unit_of_measure} 
                    onChange={handleInputChange} 
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group id="reorder_level" className="mb-3">
                  <Form.Label>{t('reorder_level', 'Reorder Level')}</Form.Label>
                  <Form.Control 
                    type="number"
                    step="0.001" 
                    name="reorder_level"
                    value={currentProduct.reorder_level} 
                    onChange={handleInputChange} 
                  />
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group id="unit_price" className="mb-3">
                  <Form.Label>{t('unit_price', 'Cost Price')}</Form.Label>
                  <Form.Control 
                    type="number"
                    step="0.01" 
                    name="unit_price"
                    value={currentProduct.unit_price} 
                    onChange={handleInputChange} 
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group id="selling_price" className="mb-3">
                  <Form.Label>{t('selling_price', 'Selling Price')}</Form.Label>
                  <Form.Control 
                    type="number"
                    step="0.01" 
                    name="selling_price"
                    value={currentProduct.selling_price} 
                    onChange={handleInputChange} 
                  />
                </Form.Group>
              </Col>
            </Row>
            
            <Form.Group id="description" className="mb-3">
              <Form.Label>{t('description', 'Description')}</Form.Label>
              <Form.Control 
                as="textarea" 
                rows={2}
                name="description"
                value={currentProduct.description} 
                onChange={handleInputChange} 
              />
            </Form.Group>

            <Form.Group id="is_active" className="mb-3">
              <Form.Check 
                type="checkbox"
                label={t('is_active', 'Active')}
                name="is_active"
                checked={currentProduct.is_active}
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
