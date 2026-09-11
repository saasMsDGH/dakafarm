import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faEdit, faTrash, faSearch } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, Button, Modal, Form, InputGroup, Pagination, Badge } from '@themesberg/react-bootstrap';
import { useTranslation } from 'react-i18next';
import { api } from "../../api/axios";
import Swal from 'sweetalert2';
import moment from 'moment';

export default () => {
  const { t } = useTranslation();
  
  const [flocks, setFlocks] = useState([]);
  const [houses, setHouses] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Pagination and Search
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  
  // Modal State
  const [showModal, setShowModal] = useState(false);
  const [isEdit, setIsEdit] = useState(false);
  const [currentFlock, setCurrentFlock] = useState({
    house_id: '',
    breed: '',
    initial_quantity: '',
    arrival_date: moment().format('YYYY-MM-DD'),
  });

  const PREDEFINED_STATUSES = ['Active', 'Sold', 'Depleted'];
  const [statusSelection, setStatusSelection] = useState('Active');
  const [customStatus, setCustomStatus] = useState('');

  const fetchHouses = async () => {
    try {
      const response = await api.get('/api/v1/farm/houses/', { params: { limit: 100 } });
      setHouses(response.data.items);
    } catch (error) {
      console.error("Failed to fetch houses:", error);
    }
  };

  const fetchFlocks = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/farm/flocks/', {
        params: { page, limit: 10, search: searchTerm }
      });
      setFlocks(response.data.items);
      setTotalPages(response.data.pages || 1);
    } catch (error) {
      console.error("Failed to fetch flocks:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHouses();
  }, []);

  useEffect(() => {
    fetchFlocks();
  }, [page, searchTerm]);

  const handleShowModal = (flock = null) => {
    if (flock) {
      setCurrentFlock({
        ...flock,
        arrival_date: flock.arrival_date || moment().format('YYYY-MM-DD')
      });
      
      if (PREDEFINED_STATUSES.includes(flock.status)) {
        setStatusSelection(flock.status);
        setCustomStatus('');
      } else {
        setStatusSelection('Other');
        setCustomStatus(flock.status || '');
      }
      setIsEdit(true);
    } else {
      setCurrentFlock({
        house_id: houses.length > 0 ? houses[0].id : '',
        breed: '',
        initial_quantity: '',
        arrival_date: moment().format('YYYY-MM-DD'),
      });
      setStatusSelection('Active');
      setCustomStatus('');
      setIsEdit(false);
    }
    setShowModal(true);
  };

  const handleCloseModal = () => setShowModal(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setCurrentFlock({
      ...currentFlock,
      [name]: value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const finalStatus = statusSelection === 'Other' ? customStatus : statusSelection;
    
    if (statusSelection === 'Other' && !finalStatus.trim()) {
      Swal.fire('Error', 'Please provide a custom status', 'error');
      return;
    }

    try {
      const payload = {
        house_id: parseInt(currentFlock.house_id),
        breed: currentFlock.breed || null,
        initial_quantity: parseInt(currentFlock.initial_quantity),
        arrival_date: currentFlock.arrival_date,
        status: finalStatus
      };

      if (isEdit) {
        await api.put(`/api/v1/farm/flocks/${currentFlock.id}`, payload);
        Swal.fire('Success', t('profile_updated') || 'Updated successfully', 'success');
      } else {
        await api.post('/api/v1/farm/flocks/', payload);
        Swal.fire('Success', 'Added successfully', 'success');
      }
      handleCloseModal();
      fetchFlocks();
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
        await api.delete(`/api/v1/farm/flocks/${id}`);
        Swal.fire('Deleted!', 'The flock has been deleted.', 'success');
        fetchFlocks();
      } catch (error) {
        let errorMsg = error.response?.data?.detail || 'Failed to delete the flock.';
        if (error.response?.status === 403) {
           errorMsg = t('admin_only_delete', 'This action is for admins only.');
        }
        Swal.fire('Error', errorMsg, 'error');
      }
    }
  };

  // Helper to map status to a translated badge and color
  const getStatusDisplay = (status) => {
    if (status === 'Active') return { label: t('active'), bg: 'success' };
    if (status === 'Sold') return { label: t('sold'), bg: 'info' };
    if (status === 'Depleted') return { label: t('depleted'), bg: 'warning' };
    return { label: status, bg: 'secondary' }; // Custom status
  };

  // Helper to find house name
  const getHouseName = (houseId) => {
    const house = houses.find(h => h.id === houseId);
    return house ? house.name : houseId;
  };

  return (
    <>
      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <div className="d-block mb-4 mb-md-0">
          <h4>{t('flocks_title')}</h4>
        </div>
        <div className="btn-toolbar mb-2 mb-md-0">
          <Button variant="primary" size="sm" onClick={() => handleShowModal()}>
            <FontAwesomeIcon icon={faPlus} className="me-2" /> {t('add_flock')}
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
                <th className="border-bottom">{t('flock_code')}</th>
                <th className="border-bottom">{t('house_name')}</th>
                <th className="border-bottom">{t('breed')}</th>
                <th className="border-bottom">{t('arrival_date')}</th>
                <th className="border-bottom">{t('initial_quantity')}</th>
                <th className="border-bottom">{t('current_quantity')}</th>
                <th className="border-bottom">{t('is_active')}</th>
                <th className="border-bottom">{t('actions')}</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="8" className="text-center">Loading...</td></tr>
              ) : flocks.length === 0 ? (
                <tr><td colSpan="8" className="text-center">No records found</td></tr>
              ) : (
                flocks.map(flock => {
                  const statusDisplay = getStatusDisplay(flock.status);
                  return (
                    <tr key={flock.id}>
                      <td><span className="fw-bold">{flock.flock_code}</span></td>
                      <td><span className="fw-normal">{getHouseName(flock.house_id)}</span></td>
                      <td><span className="fw-normal">{flock.breed || '-'}</span></td>
                      <td><span className="fw-normal">{flock.arrival_date}</span></td>
                      <td><span className="fw-normal">{flock.initial_quantity}</span></td>
                      <td><span className="fw-bold">{flock.current_quantity}</span></td>
                      <td>
                        <Badge bg={statusDisplay.bg} className="badge-lg">
                          {statusDisplay.label}
                        </Badge>
                      </td>
                      <td>
                        <Button variant="info" size="sm" className="me-2" onClick={() => handleShowModal(flock)}>
                          <FontAwesomeIcon icon={faEdit} />
                        </Button>
                        <Button variant="danger" size="sm" onClick={() => handleDelete(flock.id)}>
                          <FontAwesomeIcon icon={faTrash} />
                        </Button>
                      </td>
                    </tr>
                  )
                })
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
            <Modal.Title>{isEdit ? t('edit') : t('add_flock')}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Form.Group id="house_id" className="mb-3">
              <Form.Label>{t('select_house')}</Form.Label>
              <Form.Select 
                required 
                name="house_id"
                value={currentFlock.house_id} 
                onChange={handleInputChange}
              >
                <option value="">-- {t('select_house')} --</option>
                {houses.map(h => (
                  <option key={h.id} value={h.id}>{h.name} {h.capacity ? `(Cap: ${h.capacity})` : ''}</option>
                ))}
              </Form.Select>
            </Form.Group>
            
            <Form.Group id="breed" className="mb-3">
              <Form.Label>{t('breed')}</Form.Label>
              <Form.Control 
                type="text" 
                name="breed"
                value={currentFlock.breed || ''} 
                onChange={handleInputChange} 
              />
            </Form.Group>
            
            <Form.Group id="initial_quantity" className="mb-3">
              <Form.Label>{t('initial_quantity')}</Form.Label>
              <Form.Control 
                required 
                type="number" 
                min="1"
                name="initial_quantity"
                value={currentFlock.initial_quantity} 
                onChange={handleInputChange} 
              />
            </Form.Group>
            
            <Form.Group id="arrival_date" className="mb-3">
              <Form.Label>{t('arrival_date')}</Form.Label>
              <Form.Control 
                required 
                type="date" 
                name="arrival_date"
                value={currentFlock.arrival_date} 
                onChange={handleInputChange} 
              />
            </Form.Group>
            
            <Form.Group id="status_selection" className="mb-3">
              <Form.Label>{t('is_active', 'Status')}</Form.Label>
              <Form.Select 
                value={statusSelection} 
                onChange={(e) => setStatusSelection(e.target.value)}
              >
                <option value="Active">{t('active')}</option>
                <option value="Sold">{t('sold')}</option>
                <option value="Depleted">{t('depleted')}</option>
                <option value="Other">{t('other')}</option>
              </Form.Select>
            </Form.Group>

            {statusSelection === 'Other' && (
              <Form.Group id="custom_status" className="mb-3">
                <Form.Label>{t('custom_status')}</Form.Label>
                <Form.Control 
                  required
                  type="text" 
                  value={customStatus} 
                  onChange={(e) => setCustomStatus(e.target.value)} 
                />
              </Form.Group>
            )}

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
