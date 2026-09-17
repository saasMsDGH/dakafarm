import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faEdit, faTrash, faSearch } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, Button, Modal, Form, InputGroup, Pagination, Badge, Nav } from '@themesberg/react-bootstrap';
import { useTranslation } from 'react-i18next';
import { api } from "../../api/axios";
import Swal from 'sweetalert2';

export default () => {
  const { t } = useTranslation();
  
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  
  const [showModal, setShowModal] = useState(false);
  const [isEdit, setIsEdit] = useState(false);
  const [currentEmployee, setCurrentEmployee] = useState({
    first_name: '',
    last_name: '',
    position: '',
    phone: '',
    employment_date: '',
    status: 'Active'
  });

  const fetchEmployees = async (currentPage = page, search = searchTerm) => {
    setLoading(true);
    try {
      const response = await api.get(`/api/v1/hr/employees/?page=${currentPage}&limit=10&search=${search}`);
      setEmployees(response.data.items);
      setTotalPages(response.data.pages);
      setPage(response.data.page);
    } catch (error) {
      console.error("Failed to fetch employees", error);
      Swal.fire('Error', 'Failed to load employees', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmployees();
  }, []);

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
    fetchEmployees(1, e.target.value);
  };

  const handlePageChange = (newPage) => {
    fetchEmployees(newPage, searchTerm);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setCurrentEmployee({
      first_name: '',
      last_name: '',
      position: '',
      phone: '',
      employment_date: '',
      status: 'Active'
    });
    setIsEdit(false);
  };

  const handleShowAddModal = () => {
    setIsEdit(false);
    setShowModal(true);
  };

  const handleShowEditModal = (emp) => {
    setCurrentEmployee({ ...emp, status: emp.status ? 'Active' : 'Inactive' });
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
        await api.delete(`/api/v1/hr/employees/${id}`);
        Swal.fire('Deleted!', 'Employee has been deleted.', 'success');
        fetchEmployees();
      } catch (error) {
        Swal.fire('Error!', error.response?.data?.detail || 'Deletion failed', 'error');
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...currentEmployee,
        status: currentEmployee.status === 'Active' ? true : false
      };
      payload.employment_date = payload.employment_date || null;
      payload.phone = payload.phone || null;

      if (isEdit) {
        await api.put(`/api/v1/hr/employees/${currentEmployee.id}`, payload);
        Swal.fire('Success', 'Employee updated successfully', 'success');
      } else {
        await api.post('/api/v1/hr/employees/', payload);
        Swal.fire('Success', 'Employee added successfully', 'success');
      }
      handleCloseModal();
      fetchEmployees();
    } catch (error) {
      Swal.fire('Error', error.response?.data?.detail || 'Submission failed', 'error');
    }
  };

  return (
    <>
      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <div className="d-block mb-4 mb-md-0">
          <h4>{t('employees', 'Employees')}</h4>
          <p className="mb-0">{t('manage_employees', 'Manage farm employees and staff.')}</p>
        </div>
        <div className="btn-toolbar mb-2 mb-md-0">
          <Button variant="primary" size="sm" onClick={handleShowAddModal}>
            <FontAwesomeIcon icon={faPlus} className="me-2" /> Add Employee
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
                <th className="border-bottom">{t('employee_code', 'Code')}</th>
                <th className="border-bottom">{t('first_name', 'First Name')}</th>
                <th className="border-bottom">{t('last_name', 'Last Name')}</th>
                <th className="border-bottom">{t('position', 'Position')}</th>
                <th className="border-bottom">{t('phone', 'Phone')}</th>
                <th className="border-bottom">{t('status', 'Status')}</th>
                <th className="border-bottom">{t('actions', 'Actions')}</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="7" className="text-center">Loading...</td></tr>
              ) : employees.length === 0 ? (
                <tr><td colSpan="7" className="text-center">No employees found.</td></tr>
              ) : (
                employees.map(emp => (
                  <tr key={emp.id}>
                    <td><span className="fw-normal">{emp.employee_code}</span></td>
                    <td><span className="fw-normal">{emp.first_name}</span></td>
                    <td><span className="fw-normal">{emp.last_name}</span></td>
                    <td><span className="fw-normal">{emp.position}</span></td>
                    <td><span className="fw-normal">{emp.phone}</span></td>
                    <td>
                      <Badge bg={emp.status ? 'success' : 'danger'}>{emp.status ? 'Active' : 'Inactive'}</Badge>
                    </td>
                    <td>
                      <Button variant="info" size="sm" className="me-2" onClick={() => handleShowEditModal(emp)}>
                        <FontAwesomeIcon icon={faEdit} />
                      </Button>
                      <Button variant="danger" size="sm" onClick={() => handleDelete(emp.id)}>
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

      <Modal as={Modal} show={showModal} onHide={handleCloseModal}>
        <Form onSubmit={handleSubmit}>
          <Modal.Header>
            <Modal.Title className="h6">{isEdit ? 'Edit Employee' : 'Add Employee'}</Modal.Title>
            <Button variant="close" aria-label="Close" onClick={handleCloseModal} />
          </Modal.Header>
          <Modal.Body>
            <Row>
              <Col md={6} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('first_name', 'First Name')}</Form.Label>
                  <Form.Control required type="text" value={currentEmployee.first_name} onChange={(e) => setCurrentEmployee({...currentEmployee, first_name: e.target.value})} />
                </Form.Group>
              </Col>
              <Col md={6} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('last_name', 'Last Name')}</Form.Label>
                  <Form.Control required type="text" value={currentEmployee.last_name} onChange={(e) => setCurrentEmployee({...currentEmployee, last_name: e.target.value})} />
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={6} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('position', 'Position')}</Form.Label>
                  <Form.Control required type="text" value={currentEmployee.position} onChange={(e) => setCurrentEmployee({...currentEmployee, position: e.target.value})} />
                </Form.Group>
              </Col>
              <Col md={6} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('phone', 'Phone')}</Form.Label>
                  <Form.Control type="text" value={currentEmployee.phone || ''} onChange={(e) => setCurrentEmployee({...currentEmployee, phone: e.target.value})} />
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={6} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('employment_date', 'Employment Date')}</Form.Label>
                  <Form.Control type="date" value={currentEmployee.employment_date || ''} onChange={(e) => setCurrentEmployee({...currentEmployee, employment_date: e.target.value})} />
                </Form.Group>
              </Col>
              <Col md={6} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('status', 'Status')}</Form.Label>
                  <Form.Select required value={currentEmployee.status} onChange={(e) => setCurrentEmployee({...currentEmployee, status: e.target.value})}>
                    <option value="Active">Active</option>
                    <option value="Inactive">Inactive</option>
                    <option value="Terminated">Terminated</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
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
