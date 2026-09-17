import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faEdit, faTrash, faSearch, faEye } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, Button, Modal, Form, InputGroup, Pagination, Badge, Nav } from '@themesberg/react-bootstrap';
import { useTranslation } from 'react-i18next';
import { api } from "../../api/axios";
import Swal from 'sweetalert2';

export default () => {
  const { t } = useTranslation();
  
  const [payrolls, setPayrolls] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  
  const [showModal, setShowModal] = useState(false);
  const [showPayslipModal, setShowPayslipModal] = useState(false);
  const [isEdit, setIsEdit] = useState(false);
  
  const [currentPayroll, setCurrentPayroll] = useState({
    employee_id: '',
    pay_period: '',
    basic_salary: '0.00',
    allowances: '0.00',
    deductions: '0.00',
    payment_status: 'Pending',
    payment_date: ''
  });

  const fetchPayrolls = async (currentPage = page, search = searchTerm) => {
    setLoading(true);
    try {
      const response = await api.get(`/api/v1/hr/payrolls/?page=${currentPage}&limit=10&search=${search}`);
      setPayrolls(response.data.items);
      setTotalPages(response.data.pages);
      setPage(response.data.page);
    } catch (error) {
      console.error("Failed to fetch payrolls", error);
      Swal.fire('Error', 'Failed to load payroll records', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchEmployees = async () => {
    try {
      // Fetch all employees for dropdown (using large limit or search if many)
      const response = await api.get(`/api/v1/hr/employees/?page=1&limit=1000`);
      setEmployees(response.data.items);
    } catch (error) {
      console.error("Failed to fetch employees", error);
    }
  };

  useEffect(() => {
    fetchPayrolls();
    fetchEmployees();
  }, []);

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
    fetchPayrolls(1, e.target.value);
  };

  const handlePageChange = (newPage) => {
    fetchPayrolls(newPage, searchTerm);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setCurrentPayroll({
      employee_id: '',
      pay_period: '',
      basic_salary: '0.00',
      allowances: '0.00',
      deductions: '0.00',
      payment_status: 'Pending',
      payment_date: ''
    });
    setIsEdit(false);
  };

  const handleShowAddModal = () => {
    setIsEdit(false);
    setShowModal(true);
  };

  const handleShowEditModal = (payroll) => {
    setCurrentPayroll({ ...payroll });
    setIsEdit(true);
    setShowModal(true);
  };

  const handleShowPayslip = (payroll) => {
    setCurrentPayroll(payroll);
    setShowPayslipModal(true);
  };

  const formatCurrency = (amount) => {
    return Number(amount).toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 2 });
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
        await api.delete(`/api/v1/hr/payrolls/${id}`);
        Swal.fire('Deleted!', 'Payroll record has been deleted.', 'success');
        fetchPayrolls();
      } catch (error) {
        Swal.fire('Error!', error.response?.data?.detail || 'Deletion failed', 'error');
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...currentPayroll,
        basic_salary: parseFloat(currentPayroll.basic_salary) || 0,
        allowances: parseFloat(currentPayroll.allowances) || 0,
        deductions: parseFloat(currentPayroll.deductions) || 0,
      };

      payload.payment_date = payload.payment_date || null;

      if (isEdit) {
        await api.put(`/api/v1/hr/payrolls/${currentPayroll.id}`, payload);
        Swal.fire('Success', 'Payroll updated successfully', 'success');
      } else {
        await api.post('/api/v1/hr/payrolls/', payload);
        Swal.fire('Success', 'Payroll added successfully', 'success');
      }
      handleCloseModal();
      fetchPayrolls();
    } catch (error) {
      Swal.fire('Error', error.response?.data?.detail || 'Submission failed', 'error');
    }
  };

  return (
    <>
      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <div className="d-block mb-4 mb-md-0">
          <h4>{t('payroll', 'Payroll')}</h4>
          <p className="mb-0">{t('manage_payroll', 'Manage employee salaries and payments.')}</p>
        </div>
        <div className="btn-toolbar mb-2 mb-md-0">
          <Button variant="primary" size="sm" onClick={handleShowAddModal}>
            <FontAwesomeIcon icon={faPlus} className="me-2" /> Add Payroll
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
                <th className="border-bottom">{t('pay_period', 'Pay Period')}</th>
                <th className="border-bottom">{t('employee', 'Employee')}</th>
                <th className="border-bottom">{t('basic_salary', 'Basic Salary')}</th>
                <th className="border-bottom">{t('net_salary', 'Net Salary')}</th>
                <th className="border-bottom">{t('payment_status', 'Status')}</th>
                <th className="border-bottom">{t('actions', 'Actions')}</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="6" className="text-center">Loading...</td></tr>
              ) : payrolls.length === 0 ? (
                <tr><td colSpan="6" className="text-center">No payroll records found.</td></tr>
              ) : (
                payrolls.map(pay => (
                  <tr key={pay.id}>
                    <td><span className="fw-normal">{pay.pay_period}</span></td>
                    <td>
                      <span className="fw-normal">
                        {pay.employee ? `${pay.employee.first_name} ${pay.employee.last_name}` : 'Unknown'}
                      </span>
                    </td>
                    <td><span className="fw-normal">{formatCurrency(pay.basic_salary)}</span></td>
                    <td><span className="fw-bold">{formatCurrency(pay.net_salary)}</span></td>
                    <td>
                      <Badge bg={pay.payment_status === 'Paid' ? 'success' : 'warning'}>{pay.payment_status}</Badge>
                    </td>
                    <td>
                      <Button variant="success" size="sm" className="me-2" onClick={() => handleShowPayslip(pay)}>
                        <FontAwesomeIcon icon={faEye} />
                      </Button>
                      <Button variant="info" size="sm" className="me-2" onClick={() => handleShowEditModal(pay)}>
                        <FontAwesomeIcon icon={faEdit} />
                      </Button>
                      <Button variant="danger" size="sm" onClick={() => handleDelete(pay.id)}>
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

      {/* Payslip Modal (A4 / Invoice Format) */}
      <Modal as={Modal} show={showPayslipModal} onHide={() => setShowPayslipModal(false)} size="lg">
        <Modal.Header className="d-print-none">
          <Modal.Title className="h6">Pay Slip</Modal.Title>
          <Button variant="close" aria-label="Close" onClick={() => setShowPayslipModal(false)} />
        </Modal.Header>
        <Modal.Body className="p-0">
          <div id="payslip-print-area" className="bg-white p-5" style={{ minHeight: '800px', color: '#333', fontFamily: 'Helvetica, Arial, sans-serif' }}>
            {currentPayroll.employee && (
              <>
                <div className="d-flex justify-content-between align-items-end border-bottom pb-3 mb-4">
                  <div>
                    <h2 className="mb-0 fw-bolder text-uppercase" style={{ color: '#2c3e50', letterSpacing: '2px' }}>AMAS FARM</h2>
                    <p className="mb-0 text-muted mt-1">Official Employee Pay Slip</p>
                  </div>
                  <div className="text-end">
                    <h1 className="text-uppercase mb-0" style={{ color: '#000', fontSize: '28px', fontWeight: '900' }}>INVOICE</h1>
                    <p className="mb-0 text-muted"><strong>Date:</strong> {new Date().toLocaleDateString()}</p>
                    <p className="mb-0 text-muted"><strong>Receipt #:</strong> PR-{currentPayroll.id.toString().padStart(5, '0')}</p>
                  </div>
                </div>

                <Row className="mb-5">
                  <Col sm={6}>
                    <h6 className="text-uppercase text-muted mb-2">Employee Details</h6>
                    <h5 className="mb-1 fw-bold">{currentPayroll.employee.first_name} {currentPayroll.employee.last_name}</h5>
                    <p className="mb-0"><strong>Position:</strong> {currentPayroll.employee.position}</p>
                  </Col>
                  <Col sm={6} className="text-end">
                    <h6 className="text-uppercase text-muted mb-2">Payment Details</h6>
                    <p className="mb-1"><strong>Pay Period:</strong> {currentPayroll.pay_period}</p>
                    <p className="mb-0"><strong>Status:</strong> <span className={currentPayroll.payment_status === 'Paid' ? 'text-success fw-bold' : 'text-warning fw-bold'}>{currentPayroll.payment_status}</span></p>
                    {currentPayroll.payment_date && <p className="mb-0"><strong>Paid On:</strong> {currentPayroll.payment_date}</p>}
                  </Col>
                </Row>

                <Table bordered className="mb-5">
                  <thead className="bg-light">
                    <tr>
                      <th className="text-uppercase text-muted py-3">Description</th>
                      <th className="text-uppercase text-muted py-3 text-end">Amount (TZS)</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="py-3">Basic Salary</td>
                      <td className="py-3 text-end">{formatCurrency(currentPayroll.basic_salary)}</td>
                    </tr>
                    <tr>
                      <td className="py-3">Allowances</td>
                      <td className="py-3 text-end">{formatCurrency(currentPayroll.allowances)}</td>
                    </tr>
                    <tr>
                      <td className="py-3 text-danger">Deductions</td>
                      <td className="py-3 text-end text-danger">-{formatCurrency(currentPayroll.deductions)}</td>
                    </tr>
                    <tr className="bg-light border-top border-dark border-2">
                      <td className="py-3 fw-bolder fs-5 text-end">NET SALARY</td>
                      <td className="py-3 fw-bolder fs-5 text-end">{formatCurrency(currentPayroll.net_salary)}</td>
                    </tr>
                  </tbody>
                </Table>

                <Row className="mt-5 pt-5">
                  <Col sm={6} className="text-center">
                    <div style={{ borderTop: '1px solid #333', width: '80%', margin: '0 auto', paddingTop: '10px' }}>
                      <p className="fw-bold mb-0">Authorized By</p>
                      <p className="text-muted small">
                        {currentPayroll.user ? `${currentPayroll.user.first_name} ${currentPayroll.user.last_name}` : 'AMAS Farm Admin'}
                      </p>
                    </div>
                  </Col>
                  <Col sm={6} className="text-center">
                    <div style={{ borderTop: '1px solid #333', width: '80%', margin: '0 auto', paddingTop: '10px' }}>
                      <p className="fw-bold mb-0">Employee Signature</p>
                      <p className="text-muted small">Received in good condition</p>
                    </div>
                  </Col>
                </Row>

                <div className="text-center mt-5 text-muted small">
                  <hr />
                  <p>Thank you for your hard work and dedication to AMAS FARM!</p>
                </div>
              </>
            )}
          </div>
        </Modal.Body>
        <Modal.Footer className="d-print-none">
          <Button variant="secondary" onClick={() => setShowPayslipModal(false)}>Close</Button>
          <Button variant="primary" onClick={() => {
            const printWindow = window.open('', '', 'width=900,height=800');
            printWindow.document.write('<html><head><title>AMAS FARM Payslip</title>');
            printWindow.document.write('<style>@media print { @page { margin: 0; } body { padding: 1.5cm; } }</style>');
            printWindow.document.write('<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">');
            printWindow.document.write('</head><body>');
            printWindow.document.write(document.getElementById('payslip-print-area').innerHTML);
            printWindow.document.write('</body></html>');
            printWindow.document.close();
            setTimeout(() => {
                printWindow.print();
                printWindow.close();
            }, 500);
          }}>Print Pay Slip</Button>
        </Modal.Footer>
      </Modal>

      {/* Edit/Add Modal */}
      <Modal as={Modal} show={showModal} onHide={handleCloseModal}>
        <Form onSubmit={handleSubmit}>
          <Modal.Header>
            <Modal.Title className="h6">{isEdit ? 'Edit Payroll' : 'Add Payroll'}</Modal.Title>
            <Button variant="close" aria-label="Close" onClick={handleCloseModal} />
          </Modal.Header>
          <Modal.Body>
            <Row>
              <Col md={12} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('employee', 'Employee')}</Form.Label>
                  <Form.Select required value={currentPayroll.employee_id} onChange={(e) => setCurrentPayroll({...currentPayroll, employee_id: e.target.value})} disabled={isEdit}>
                    <option value="">Select Employee</option>
                    {employees.map(emp => (
                      <option key={emp.id} value={emp.id}>{emp.first_name} {emp.last_name} - {emp.position}</option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={6} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('pay_period', 'Pay Period')}</Form.Label>
                  <Form.Control required type="text" placeholder="e.g. September 2026" value={currentPayroll.pay_period} onChange={(e) => setCurrentPayroll({...currentPayroll, pay_period: e.target.value})} />
                </Form.Group>
              </Col>
              <Col md={6} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('payment_status', 'Status')}</Form.Label>
                  <Form.Select required value={currentPayroll.payment_status} onChange={(e) => setCurrentPayroll({...currentPayroll, payment_status: e.target.value})}>
                    <option value="Pending">Pending</option>
                    <option value="Paid">Paid</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={4} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('basic_salary', 'Basic Salary')}</Form.Label>
                  <Form.Control required type="number" step="0.01" value={currentPayroll.basic_salary} onChange={(e) => setCurrentPayroll({...currentPayroll, basic_salary: e.target.value})} />
                </Form.Group>
              </Col>
              <Col md={4} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('allowances', 'Allowances')}</Form.Label>
                  <Form.Control type="number" step="0.01" value={currentPayroll.allowances} onChange={(e) => setCurrentPayroll({...currentPayroll, allowances: e.target.value})} />
                </Form.Group>
              </Col>
              <Col md={4} className="mb-3">
                <Form.Group>
                  <Form.Label>{t('deductions', 'Deductions')}</Form.Label>
                  <Form.Control type="number" step="0.01" value={currentPayroll.deductions} onChange={(e) => setCurrentPayroll({...currentPayroll, deductions: e.target.value})} />
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
