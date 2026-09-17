import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faEdit, faTrash, faSearch } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, Button, Modal, Form, InputGroup, Pagination } from '@themesberg/react-bootstrap';
import { useTranslation } from 'react-i18next';
import { api } from "../../api/axios";
import Swal from 'sweetalert2';

export default () => {
  const { t } = useTranslation();
  
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  
  const [showModal, setShowModal] = useState(false);
  const [isEdit, setIsEdit] = useState(false);
  const [currentCategory, setCurrentCategory] = useState({
    name: '',
    description: ''
  });

  const fetchCategories = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/inventory/product-categories/', {
        params: { page, limit: 10, search: searchTerm }
      });
      setCategories(response.data.items);
      setTotalPages(response.data.pages || 1);
    } catch (error) {
      console.error("Failed to fetch categories:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCategories();
  }, [page, searchTerm]);

  const handleShowModal = (category = null) => {
    if (category) {
      setCurrentCategory({ ...category });
      setIsEdit(true);
    } else {
      setCurrentCategory({ name: '', description: '' });
      setIsEdit(false);
    }
    setShowModal(true);
  };

  const handleCloseModal = () => setShowModal(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setCurrentCategory({ ...currentCategory, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (isEdit) {
        await api.put(`/api/v1/inventory/product-categories/${currentCategory.id}`, currentCategory);
        Swal.fire('Updated!', 'The category has been updated.', 'success');
      } else {
        await api.post('/api/v1/inventory/product-categories/', currentCategory);
        Swal.fire('Saved!', 'The category has been added.', 'success');
      }
      handleCloseModal();
      fetchCategories();
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
        await api.delete(`/api/v1/inventory/product-categories/${id}`);
        Swal.fire('Deleted!', 'The category has been deleted.', 'success');
        fetchCategories();
      } catch (error) {
        const errorMsg = error.response?.data?.detail || 'Failed to delete.';
        Swal.fire('Error', errorMsg, 'error');
      }
    }
  };

  return (
    <>
      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <div className="d-block mb-4 mb-md-0">
          <h4>{t('product_categories', 'Product Categories')}</h4>
        </div>
        <div className="btn-toolbar mb-2 mb-md-0">
          <Button variant="primary" size="sm" onClick={() => handleShowModal()}>
            <FontAwesomeIcon icon={faPlus} className="me-2" /> {t('add_category', 'Add Category')}
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
                <th className="border-bottom">ID</th>
                <th className="border-bottom">{t('name', 'Name')}</th>
                <th className="border-bottom">{t('description', 'Description')}</th>
                <th className="border-bottom">{t('actions', 'Actions')}</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="4" className="text-center">Loading...</td></tr>
              ) : categories.length === 0 ? (
                <tr><td colSpan="4" className="text-center">No categories found</td></tr>
              ) : (
                categories.map(cat => (
                  <tr key={cat.id}>
                    <td><span className="fw-normal">{cat.id}</span></td>
                    <td><span className="fw-normal">{cat.name}</span></td>
                    <td><span className="fw-normal">{cat.description || '-'}</span></td>
                    <td>
                      <Button variant="info" size="sm" className="me-2" onClick={() => handleShowModal(cat)}>
                        <FontAwesomeIcon icon={faEdit} />
                      </Button>
                      <Button variant="danger" size="sm" onClick={() => handleDelete(cat.id)}>
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
            <Modal.Title>{isEdit ? t('edit', 'Edit') : t('add_category', 'Add Category')}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Form.Group id="name" className="mb-3">
              <Form.Label>{t('name', 'Name')}</Form.Label>
              <Form.Control 
                required 
                type="text" 
                name="name"
                value={currentCategory.name} 
                onChange={handleInputChange} 
              />
            </Form.Group>
            
            <Form.Group id="description" className="mb-3">
              <Form.Label>{t('description', 'Description')} (Optional)</Form.Label>
              <Form.Control 
                as="textarea" 
                rows={3}
                name="description"
                value={currentCategory.description} 
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
