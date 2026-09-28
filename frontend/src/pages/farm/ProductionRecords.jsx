import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faEdit, faTrash, faSearch } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, Button, Modal, Form, InputGroup, Pagination } from '@themesberg/react-bootstrap';
import { useTranslation } from 'react-i18next';
import { api } from "../../api/axios";
import Swal from 'sweetalert2';
import moment from 'moment';

export default () => {
  const { t } = useTranslation();
  
  const [records, setRecords] = useState([]);
  const [flocks, setFlocks] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Pagination and Search
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  
  // Modal State
  const [showModal, setShowModal] = useState(false);
  const [isEdit, setIsEdit] = useState(false);
  const [currentRecord, setCurrentRecord] = useState({
    flock_id: '',
    record_date: moment().format('YYYY-MM-DD'),
    total_eggs: '',
    damaged_eggs: '0'
  });

  const fetchFlocks = async () => {
    try {
      const response = await api.get('/api/v1/farm/flocks/', { params: { limit: 100 } });
      setFlocks(response.data.items);
    } catch (error) {
      console.error("Failed to fetch flocks:", error);
    }
  };

  const fetchRecords = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/farm/production-records/', {
        params: { page, limit: 10, search: searchTerm }
      });
      setRecords(response.data.items);
      setTotalPages(response.data.pages || 1);
    } catch (error) {
      console.error("Failed to fetch production records:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFlocks();
  }, []);

  useEffect(() => {
    fetchRecords();
  }, [page, searchTerm]);

  const handleShowModal = (record = null) => {
    if (record) {
      setCurrentRecord({
        ...record,
        record_date: record.record_date || moment().format('YYYY-MM-DD')
      });
      setIsEdit(true);
    } else {
      setCurrentRecord({
        flock_id: flocks.length > 0 ? flocks[0].id : '',
        record_date: moment().format('YYYY-MM-DD'),
        total_eggs: '',
        damaged_eggs: '0'
      });
      setIsEdit(false);
    }
    setShowModal(true);
  };

  const handleCloseModal = () => setShowModal(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setCurrentRecord({
      ...currentRecord,
      [name]: value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        flock_id: parseInt(currentRecord.flock_id),
        record_date: currentRecord.record_date,
        total_eggs: parseInt(currentRecord.total_eggs),
        damaged_eggs: parseInt(currentRecord.damaged_eggs) || 0
      };

      if (isEdit) {
        await api.put(`/api/v1/farm/production-records/${currentRecord.id}`, payload);
        Swal.fire('Success', t('profile_updated') || 'Updated successfully', 'success');
      } else {
        await api.post('/api/v1/farm/production-records/', payload);
        Swal.fire('Success', 'Added successfully', 'success');
      }
      handleCloseModal();
      fetchRecords();
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
        await api.delete(`/api/v1/farm/production-records/${id}`);
        Swal.fire('Deleted!', 'The record has been deleted.', 'success');
        fetchRecords();
      } catch (error) {
        let errorMsg = error.response?.data?.detail || 'Failed to delete the record.';
        if (error.response?.status === 403) {
           errorMsg = t('admin_only_delete', 'This action is for admins only.');
        }
        Swal.fire('Error', errorMsg, 'error');
      }
    }
  };

  const getFlockDisplay = (flockId) => {
    const flock = flocks.find(f => f.id === flockId);
    return flock ? `${flock.flock_code} (${flock.breed || 'N/A'})` : flockId;
  };

  return (
    <>
      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <div className="d-block mb-4 mb-md-0">
          <h4>{t('production_records_title')}</h4>
        </div>
        <div className="btn-toolbar mb-2 mb-md-0">
          <Button variant="primary" size="sm" onClick={() => handleShowModal()}>
            <FontAwesomeIcon icon={faPlus} className="me-2" /> {t('add_production')}
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
                <th className="border-bottom">{t('record_date')}</th>
                <th className="border-bottom">{t('flock')}</th>
                <th className="border-bottom">{t('total_birds')}</th>
                <th className="border-bottom">{t('total_eggs')}</th>
                <th className="border-bottom text-danger">{t('damaged_eggs')}</th>
                <th className="border-bottom text-success">{t('good_eggs')}</th>
                <th className="border-bottom text-info">{t('laying_percentage')}</th>
                <th className="border-bottom">{t('actions', 'Actions')}</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="8" className="text-center">Loading...</td></tr>
              ) : records.length === 0 ? (
                <tr><td colSpan="8" className="text-center">No records found</td></tr>
              ) : (
                records.map(record => (
                  <tr key={record.id}>
                    <td><span className="fw-normal">{record.record_date}</span></td>
                    <td><span className="fw-normal">{getFlockDisplay(record.flock_id)}</span></td>
                    <td><span className="fw-normal">{record.total_birds}</span></td>
                    <td><span className="fw-bold">{record.total_eggs}</span></td>
                    <td><span className="fw-bold text-danger">{record.damaged_eggs}</span></td>
                    <td><span className="fw-bold text-success">{record.good_eggs}</span></td>
                    <td><span className="fw-bold text-info">{record.laying_percentage}%</span></td>
                    <td>
                      <Button variant="info" size="sm" className="me-2" onClick={() => handleShowModal(record)}>
                        <FontAwesomeIcon icon={faEdit} />
                      </Button>
                      <Button variant="danger" size="sm" onClick={() => handleDelete(record.id)}>
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
            <Modal.Title>{isEdit ? t('edit', 'Edit') : t('add_production')}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Form.Group id="flock_id" className="mb-3">
              <Form.Label>{t('select_flock')}</Form.Label>
              <Form.Select 
                required 
                name="flock_id"
                value={currentRecord.flock_id} 
                onChange={handleInputChange}
              >
                <option value="">-- {t('select_flock')} --</option>
                {flocks.map(f => (
                  <option key={f.id} value={f.id}>{f.flock_code} ({f.breed || 'N/A'})</option>
                ))}
              </Form.Select>
            </Form.Group>
            
            <Form.Group id="record_date" className="mb-3">
              <Form.Label>{t('record_date')}</Form.Label>
              <Form.Control 
                required 
                type="date" 
                name="record_date"
                value={currentRecord.record_date} 
                onChange={handleInputChange} 
              />
            </Form.Group>
            
            <Row>
              <Col md={6}>
                <Form.Group id="total_eggs" className="mb-3">
                  <Form.Label>{t('total_eggs')}</Form.Label>
                  <Form.Control 
                    required 
                    type="number" 
                    min="0"
                    name="total_eggs"
                    value={currentRecord.total_eggs} 
                    onChange={handleInputChange} 
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group id="damaged_eggs" className="mb-3">
                  <Form.Label>{t('damaged_eggs')}</Form.Label>
                  <Form.Control 
                    type="number" 
                    min="0"
                    name="damaged_eggs"
                    value={currentRecord.damaged_eggs} 
                    onChange={handleInputChange} 
                  />
                </Form.Group>
              </Col>
            </Row>

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
