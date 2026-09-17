import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faEdit, faTrash, faSearch } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, Button, Modal, Form, InputGroup, Pagination } from '@themesberg/react-bootstrap';
import { useTranslation } from 'react-i18next';
import { api } from "../../api/axios";
import Swal from 'sweetalert2';

export default () => {
  const { t } = useTranslation();
  
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  
  const [showModal, setShowModal] = useState(false);
  const [isEdit, setIsEdit] = useState(false);
  const [currentSupplier, setCurrentSupplier] = useState({
    name: '',
    contact_person: '',
    phone: '',
    email: '',
    address: '',
    
  });

  const fetchSuppliers = async (currentPage = page, search = searchTerm) => {
    setLoading(true);
    try {
      const response = await api.get(`/api/v1/pos/suppliers/?page=${currentPage}&limit=10&search=${search}`);
      setSuppliers(response.data.items);
      setTotalPages(response.data.pages);
      setPage(response.data.page);
    } catch (error) {
      console.error("Failed to fetch suppliers", error);
      Swal.fire('Error', 'Failed to load suppliers', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSuppliers();
  }, []);

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
    fetchSuppliers(1, e.target.value);
  };

  const handlePageChange = (newPage) => {
    fetchSuppliers(newPage, searchTerm);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setCurrentSupplier({
        name: '',
        contact_person: '',
        phone: '',
        email: '',
        address: '',
        
    });
    setIsEdit(false);
  };

  const handleShowAddModal = () => {
    setIsEdit(false);
    setShowModal(true);
  };

  const handleShowEditModal = (supplier) => {
    setCurrentSupplier({
      ...supplier
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
        await api.delete(`/api/v1/pos/suppliers/${id}`);
        Swal.fire('Deleted!', 'Supplier has been deleted.', 'success');
        fetchSuppliers();
      } catch (error) {
        Swal.fire('Error', 'Failed to delete supplier. They might be linked to sales.', 'error');
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...currentSupplier,
        credit_limit: parseFloat(currentSupplier.credit_limit) || 0
      };

      if (isEdit) {
        await api.put(`/api/v1/pos/suppliers/${currentSupplier.id}`, payload);
        Swal.fire('Success', 'Supplier updated successfully', 'success');
      } else {
        await api.post(`/api/v1/pos/suppliers/`, payload);
        Swal.fire('Success', 'Supplier added successfully', 'success');
      }
      handleCloseModal();
      fetchSuppliers();
    } catch (error) {
      console.error(error);
      Swal.fire('Error', error.response?.data?.detail || 'Failed to save supplier', 'error');
    }
  };

  const handleChange = (e) => {
    setCurrentSupplier({ ...currentSupplier, [e.target.name]: e.target.value });
  };

  return (
    <>
      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <div className="d-block mb-4 mb-md-0">
          <h4>{t('suppliers', 'Suppliers')}</h4>
          <p className="mb-0">{t('manage_suppliers', 'Manage your suppliers and credit limits.')}</p>
        </div>
        <div className="btn-toolbar mb-2 mb-md-0">
          <Button variant="primary" size="sm" onClick={handleShowAddModal}>
            <FontAwesomeIcon icon={faPlus} className="me-2" /> {t('add_supplier')}
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
                <th className="border-bottom">{t('contact_person')}</th>
                <th className="border-bottom">Phone</th>
                <th className="border-bottom">Address</th>
                
                <th className="border-bottom">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="7" className="text-center">Loading...</td></tr>
              ) : suppliers.length === 0 ? (
                <tr><td colSpan="7" className="text-center">No suppliers found.</td></tr>
              ) : (
                suppliers.map(c => (
                  <tr key={c.id}>
                    <td>
                      <span className="fw-normal d-block">{c.supplier_code}</span>
                    </td>
                    <td><span className="fw-normal">{c.name}</span></td>
                    <td><span className="fw-normal">{c.contact_person}</span></td>
                    <td><span className="fw-normal">{c.phone}</span></td>
                    <td><span className="fw-normal">{c.address}</span></td>
                    
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
            <Modal.Title>{isEdit ? 'Edit Supplier' : t('add_supplier')}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>{t('name')} *</Form.Label>
              <Form.Control type="text" name="name" value={currentSupplier.name} onChange={handleChange} required />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>{t('contact_person')}</Form.Label>
              <Form.Control type="text" name="contact_person" value={currentSupplier.contact_person || ''} onChange={handleChange} />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>{t('phone')}</Form.Label>
              <Form.Control type="text" name="phone" value={currentSupplier.phone || ''} onChange={handleChange} />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>{t('email')}</Form.Label>
              <Form.Control type="email" name="email" value={currentSupplier.email || ''} onChange={handleChange} />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>{t('address')}</Form.Label>
              <Form.Control type="text" name="address" value={currentSupplier.address || ''} onChange={handleChange} />
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
