import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faEdit, faTrash, faSearch } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, Button, Modal, Form, InputGroup, Pagination, Badge } from '@themesberg/react-bootstrap';
import { useTranslation } from 'react-i18next';
import { api } from "../../api/axios";
import Swal from 'sweetalert2';

export default () => {
  const { t } = useTranslation();
  
  const [houses, setHouses] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Pagination and Search
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  
  // Modal State
  const [showModal, setShowModal] = useState(false);
  const [isEdit, setIsEdit] = useState(false);
  const [currentHouse, setCurrentHouse] = useState({ name: '', location: '', capacity: '', description: '', status: true });

  const fetchHouses = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/farm/houses/', {
        params: { page, limit: 10, search: searchTerm }
      });
      setHouses(response.data.items);
      setTotalPages(response.data.pages || 1);
    } catch (error) {
      console.error("Failed to fetch houses:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHouses();
  }, [page, searchTerm]);

  const handleShowModal = (house = null) => {
    if (house) {
      setCurrentHouse(house);
      setIsEdit(true);
    } else {
      setCurrentHouse({ name: '', location: '', capacity: '', description: '', status: true });
      setIsEdit(false);
    }
    setShowModal(true);
  };

  const handleCloseModal = () => setShowModal(false);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setCurrentHouse({
      ...currentHouse,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (isEdit) {
        await api.put(`/api/v1/farm/houses/${currentHouse.id}`, {
          name: currentHouse.name,
          location: currentHouse.location || null,
          capacity: currentHouse.capacity ? parseInt(currentHouse.capacity) : null,
          description: currentHouse.description || null,
          status: currentHouse.status
        });
        Swal.fire('Success', t('profile_updated') || 'Updated successfully', 'success');
      } else {
        await api.post('/api/v1/farm/houses/', {
          name: currentHouse.name,
          location: currentHouse.location || null,
          capacity: currentHouse.capacity ? parseInt(currentHouse.capacity) : null,
          description: currentHouse.description || null,
          status: currentHouse.status
        });
        Swal.fire('Success', 'Added successfully', 'success');
      }
      handleCloseModal();
      fetchHouses();
    } catch (error) {
      Swal.fire('Error', error.response?.data?.detail || 'Failed to save', 'error');
    }
  };

  const handleDelete = async (id) => {
    const result = await Swal.fire({
      title: 'Are you sure?',
      text: "You won't be able to revert this!",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes, delete it!'
    });

    if (result.isConfirmed) {
      try {
        await api.delete(`/api/v1/farm/houses/${id}`);
        Swal.fire('Deleted!', 'The house has been deleted.', 'success');
        fetchHouses();
      } catch (error) {
        let errorMsg = error.response?.data?.detail || 'Failed to delete the house.';
        if (error.response?.status === 403) {
           errorMsg = t('admin_only_delete', 'This action is for admins only.');
        }
        Swal.fire('Error', errorMsg, 'error');
      }
    }
  };

  return (
    <>
      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <div className="d-block mb-4 mb-md-0">
          <h4>{t('houses_title')}</h4>
        </div>
        <div className="btn-toolbar mb-2 mb-md-0">
          <Button variant="primary" size="sm" onClick={() => handleShowModal()}>
            <FontAwesomeIcon icon={faPlus} className="me-2" /> {t('add_house')}
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
                placeholder="Search..." 
                value={searchTerm}
                onChange={(e) => { setSearchTerm(e.target.value); setPage(1); }}
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
                <th className="border-bottom">{t('house_name')}</th>
                <th className="border-bottom">{t('location', 'Location')}</th>
                <th className="border-bottom">{t('capacity')}</th>
                <th className="border-bottom">{t('is_active')}</th>
                <th className="border-bottom">{t('actions')}</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="5" className="text-center">Loading...</td></tr>
              ) : houses.length === 0 ? (
                <tr><td colSpan="5" className="text-center">No records found</td></tr>
              ) : (
                houses.map(house => (
                  <tr key={house.id}>
                    <td>
                      <span className="fw-normal">{house.name}</span>
                    </td>
                    <td>
                      <span className="fw-normal">{house.location || '-'}</span>
                    </td>
                    <td>
                      <span className="fw-normal">{house.capacity || '-'}</span>
                    </td>
                    <td>
                      {house.status ? (
                        <Badge bg="success" className="badge-lg">{t('active')}</Badge>
                      ) : (
                        <Badge bg="danger" className="badge-lg">{t('inactive')}</Badge>
                      )}
                    </td>
                    <td>
                      <Button variant="info" size="sm" className="me-2" onClick={() => handleShowModal(house)}>
                        <FontAwesomeIcon icon={faEdit} />
                      </Button>
                      <Button variant="danger" size="sm" onClick={() => handleDelete(house.id)}>
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
                Previous
              </Pagination.Prev>
              <Pagination.Item active>{page}</Pagination.Item>
              <Pagination.Next disabled={page === totalPages || totalPages === 0} onClick={() => setPage(page + 1)}>
                Next
              </Pagination.Next>
            </Pagination>
          </Card.Footer>
        </Card.Body>
      </Card>

      {/* Add/Edit Modal */}
      <Modal as={Modal.Dialog} centered show={showModal} onHide={handleCloseModal}>
        <Form onSubmit={handleSubmit}>
          <Modal.Header closeButton>
            <Modal.Title>{isEdit ? t('edit') : t('add_house')}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Form.Group id="name" className="mb-3">
              <Form.Label>{t('house_name')}</Form.Label>
              <Form.Control 
                required 
                type="text" 
                name="name"
                value={currentHouse.name} 
                onChange={handleInputChange} 
              />
            </Form.Group>
            <Form.Group id="location" className="mb-3">
              <Form.Label>{t('location', 'Location')}</Form.Label>
              <Form.Control 
                type="text" 
                name="location"
                value={currentHouse.location || ''} 
                onChange={handleInputChange} 
              />
            </Form.Group>
            <Form.Group id="capacity" className="mb-3">
              <Form.Label>{t('capacity')}</Form.Label>
              <Form.Control 
                type="number" 
                name="capacity"
                value={currentHouse.capacity || ''} 
                onChange={handleInputChange} 
              />
            </Form.Group>
            <Form.Group id="description" className="mb-3">
              <Form.Label>{t('description', 'Description')}</Form.Label>
              <Form.Control 
                as="textarea"
                rows="3"
                name="description"
                value={currentHouse.description || ''} 
                onChange={handleInputChange} 
              />
            </Form.Group>
            <Form.Check 
              type="switch" 
              id="status" 
              name="status"
              label={t('is_active')}
              checked={currentHouse.status}
              onChange={handleInputChange}
            />
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" type="button" onClick={handleCloseModal}>
              {t('cancel')}
            </Button>
            <Button variant="primary" type="submit">
              {t('save')}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </>
  );
};
