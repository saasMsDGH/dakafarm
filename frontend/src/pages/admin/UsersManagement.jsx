import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faEdit, faSearch, faUserShield, faKey, faUserSlash, faUserCheck, faCheck, faTimes } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Table, Button, Modal, Form, InputGroup, Pagination, Badge } from '@themesberg/react-bootstrap';
import { api } from "../../api/axios";
import Swal from 'sweetalert2';
import { useTranslation } from 'react-i18next';

export default () => {
  const { t } = useTranslation();
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);

  // Pagination & Filtering
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Modals
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showPasswordModal, setShowPasswordModal] = useState(false);

  // States
  const [currentUser, setCurrentUser] = useState(null);
  
  const initialUserState = {
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    password_hash: '',
    role: 'Farm Worker',
  };
  const [newUser, setNewUser] = useState(initialUserState);
  const [editUser, setEditUser] = useState({});
  const [newPassword, setNewPassword] = useState('');

  const fetchRoles = async () => {
    try {
      const res = await api.get('/api/v1/user/roles');
      setRoles(res.data || []);
    } catch (error) {
      console.error("Failed to load roles", error);
    }
  };

  const fetchUsers = async (searchOverride = searchTerm, pageOverride = page) => {
    setLoading(true);
    try {
      let query = `/api/v1/user/?page=${pageOverride}&limit=10`;
      if (searchOverride) query += `&search=${searchOverride}`;
      const res = await api.get(query);
      setUsers(res.data.items || res.data);
      setTotalPages(res.data.pages || 1);
    } catch (error) {
      Swal.fire('Error', 'Failed to fetch users', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRoles();
  }, []);

  useEffect(() => {
    fetchUsers(searchTerm, page);
  }, [page]);

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  const applySearch = () => {
    setPage(1);
    fetchUsers(searchTerm, 1);
  };

  const handleRoleFilter = (e) => {
    // If we wanted server-side role filtering, we would pass it to the API.
    // For now, if the search term changes, just trigger a search.
    // We will just use the search input.
  };

  const filteredUsers = users.filter(u => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      u.first_name.toLowerCase().includes(term) ||
      u.last_name.toLowerCase().includes(term) ||
      u.email.toLowerCase().includes(term) ||
      (u.role_name && u.role_name.toLowerCase().includes(term))
    );
  });

  const handleAddUser = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/v1/user/', newUser);
      Swal.fire('Success', 'User created successfully', 'success');
      setShowAddModal(false);
      setNewUser(initialUserState);
      fetchUsers();
    } catch (error) {
      Swal.fire('Error', error.response?.data?.detail || 'Failed to create user', 'error');
    }
  };

  const handleEditUser = async (e) => {
    e.preventDefault();
    try {
      await api.put(`/api/v1/user/${editUser.id}`, {
        first_name: editUser.first_name,
        last_name: editUser.last_name,
        email: editUser.email,
        phone: editUser.phone,
        role: editUser.role_name,
        is_active: editUser.is_active
      });
      Swal.fire('Success', 'User updated successfully', 'success');
      setShowEditModal(false);
      fetchUsers();
    } catch (error) {
      Swal.fire('Error', error.response?.data?.detail || 'Failed to update user', 'error');
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    if (newPassword.length < 6) {
      Swal.fire('Warning', 'Password must be at least 6 characters long.', 'warning');
      return;
    }
    try {
      await api.put(`/api/v1/user/${currentUser.id}/password`, {
        new_password: newPassword
      });
      Swal.fire('Success', 'Password changed successfully', 'success');
      setShowPasswordModal(false);
      setNewPassword('');
    } catch (error) {
      Swal.fire('Error', error.response?.data?.detail || 'Failed to change password', 'error');
    }
  };

  const toggleUserStatus = async (user) => {
    const action = user.is_active ? 'Deactivate' : 'Activate';
    const result = await Swal.fire({
      title: `${action} User?`,
      text: `Are you sure you want to ${action.toLowerCase()} ${user.first_name} ${user.last_name}?`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: `Yes, ${action}`,
    });

    if (result.isConfirmed) {
      try {
        await api.put(`/api/v1/user/${user.id}`, {
          is_active: !user.is_active
        });
        Swal.fire('Success', `User ${action.toLowerCase()}d successfully.`, 'success');
        fetchUsers();
      } catch (error) {
        Swal.fire('Error', error.response?.data?.detail || 'Failed to update user status', 'error');
      }
    }
  };

  return (
    <>
      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <div className="d-block mb-4 mb-md-0">
          <h4>{t("user_management", "Users Management")}</h4>
          <p className="mb-0">Manage system users, roles, and access.</p>
        </div>
        <div className="btn-toolbar mb-2 mb-md-0">
          <Button variant="primary" size="sm" onClick={() => setShowAddModal(true)}>
            <FontAwesomeIcon icon={faPlus} className="me-2" /> Add User
          </Button>
        </div>
      </div>

      <div className="table-settings mb-4">
        <Row className="justify-content-between align-items-center">
          <Col xs={12} lg={6} className="d-flex">
            <InputGroup className="me-3">
              <InputGroup.Text><FontAwesomeIcon icon={faSearch} /></InputGroup.Text>
              <Form.Control type="text" placeholder="Search name, email, or role..." value={searchTerm} onChange={handleSearch} />
              <Button variant="primary" onClick={applySearch}>Search</Button>
            </InputGroup>
            <Form.Select style={{ maxWidth: '200px' }} onChange={(e) => { 
              setSearchTerm(e.target.value); 
              setPage(1);
              fetchUsers(e.target.value, 1); 
            }}>
              <option value="">All Roles</option>
              {roles.map(r => <option key={r.id} value={r.name}>{r.name}</option>)}
            </Form.Select>
          </Col>
        </Row>
      </div>

      <Card border="light" className="table-wrapper table-responsive shadow-sm">
        <Card.Body className="pt-0">
          <Table hover className="user-table align-items-center">
            <thead>
              <tr>
                <th className="border-bottom">{t("name", "Name")}</th>
                <th className="border-bottom">{t("email", "Email")}</th>
                <th className="border-bottom">{t("phone", "Phone")}</th>
                <th className="border-bottom">{t("role", "Role")}</th>
                <th className="border-bottom">{t("status", "Status")}</th>
                <th className="border-bottom">{t("actions", "Actions")}</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="6" className="text-center">Loading...</td></tr>
              ) : filteredUsers.length === 0 ? (
                <tr><td colSpan="6" className="text-center">No users found</td></tr>
              ) : (
                filteredUsers.map(u => (
                  <tr key={u.id}>
                    <td><span className="fw-bold">{u.first_name} {u.last_name}</span></td>
                    <td>{u.email}</td>
                    <td>{u.phone || '-'}</td>
                    <td>
                      <Badge bg={u.role_name === 'admin' ? 'danger' : 'info'} className="badge-lg">
                        {u.role_name}
                      </Badge>
                    </td>
                    <td>
                      {u.is_active ? (
                        <Badge bg="success" className="badge-lg"><FontAwesomeIcon icon={faCheck} className="me-1"/> Active</Badge>
                      ) : (
                        <Badge bg="secondary" className="badge-lg"><FontAwesomeIcon icon={faTimes} className="me-1"/> Inactive</Badge>
                      )}
                    </td>
                    <td>
                      <Button variant="info" size="sm" className="me-2" onClick={() => { setEditUser(u); setShowEditModal(true); }}>
                        <FontAwesomeIcon icon={faEdit} />
                      </Button>
                      <Button variant="warning" size="sm" className="me-2" title="Change Password" onClick={() => { setCurrentUser(u); setShowPasswordModal(true); }}>
                        <FontAwesomeIcon icon={faKey} />
                      </Button>
                      <Button variant={u.is_active ? 'danger' : 'success'} size="sm" title={u.is_active ? 'Deactivate' : 'Activate'} onClick={() => toggleUserStatus(u)}>
                        <FontAwesomeIcon icon={u.is_active ? faUserSlash : faUserCheck} />
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </Table>
          {totalPages > 0 && (
            <Card.Footer className="px-3 border-0 d-flex flex-column flex-lg-row align-items-center justify-content-between">
              <div className="fw-normal small mt-2 mt-lg-0 mb-2 mb-lg-0">
                Showing page <b>{page}</b> out of <b>{totalPages}</b>
              </div>
              <Pagination className="mb-0">
                <Pagination.Prev onClick={() => setPage(page - 1)} disabled={page === 1} />
                {[...Array(totalPages)].map((_, i) => (
                  <Pagination.Item key={i + 1} active={page === i + 1} onClick={() => setPage(i + 1)}>
                    {i + 1}
                  </Pagination.Item>
                ))}
                <Pagination.Next onClick={() => setPage(page + 1)} disabled={page === totalPages} />
              </Pagination>
            </Card.Footer>
          )}
        </Card.Body>
      </Card>

      {/* Add User Modal */}
      <Modal as={Modal.Dialog} centered show={showAddModal} onHide={() => setShowAddModal(false)}>
        <Form onSubmit={handleAddUser}>
          <Modal.Header closeButton>
            <Modal.Title>{t("add_new_user", "Add New User")}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>{t("first_name", "First Name")}</Form.Label>
                  <Form.Control required type="text" value={newUser.first_name} onChange={(e) => setNewUser({...newUser, first_name: e.target.value})} />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>{t("last_name", "Last Name")}</Form.Label>
                  <Form.Control required type="text" value={newUser.last_name} onChange={(e) => setNewUser({...newUser, last_name: e.target.value})} />
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>{t("email", "Email")}</Form.Label>
              <Form.Control required type="email" value={newUser.email} onChange={(e) => setNewUser({...newUser, email: e.target.value})} />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>{t("phone_number", "Phone Number")}</Form.Label>
              <Form.Control type="text" value={newUser.phone} onChange={(e) => setNewUser({...newUser, phone: e.target.value})} />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>{t("role", "Role")}</Form.Label>
              <Form.Select required value={newUser.role} onChange={(e) => setNewUser({...newUser, role: e.target.value})}>
                {roles.map(r => <option key={r.id} value={r.name}>{r.name}</option>)}
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>{t("initial_password", "Initial Password")}</Form.Label>
              <Form.Control required type="password" value={newUser.password_hash} onChange={(e) => setNewUser({...newUser, password_hash: e.target.value})} />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowAddModal(false)}>{t("cancel", "Cancel")}</Button>
            <Button variant="primary" type="submit">Create User</Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Edit User Modal */}
      <Modal as={Modal.Dialog} centered show={showEditModal} onHide={() => setShowEditModal(false)}>
        <Form onSubmit={handleEditUser}>
          <Modal.Header closeButton>
            <Modal.Title>{t("edit_user_profile", "Edit User Profile")}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>{t("first_name", "First Name")}</Form.Label>
                  <Form.Control required type="text" value={editUser.first_name || ''} onChange={(e) => setEditUser({...editUser, first_name: e.target.value})} />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>{t("last_name", "Last Name")}</Form.Label>
                  <Form.Control required type="text" value={editUser.last_name || ''} onChange={(e) => setEditUser({...editUser, last_name: e.target.value})} />
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>{t("email", "Email")}</Form.Label>
              <Form.Control required type="email" value={editUser.email || ''} onChange={(e) => setEditUser({...editUser, email: e.target.value})} />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>{t("phone_number", "Phone Number")}</Form.Label>
              <Form.Control type="text" value={editUser.phone || ''} onChange={(e) => setEditUser({...editUser, phone: e.target.value})} />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>{t("role", "Role")}</Form.Label>
              <Form.Select required value={editUser.role_name || ''} onChange={(e) => setEditUser({...editUser, role_name: e.target.value})}>
                {roles.map(r => <option key={r.id} value={r.name}>{r.name}</option>)}
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Check type="switch" id="is-active-switch" label="Active Status" checked={editUser.is_active || false} onChange={(e) => setEditUser({...editUser, is_active: e.target.checked})} />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowEditModal(false)}>{t("cancel", "Cancel")}</Button>
            <Button variant="primary" type="submit">{t("save_all", "Save Changes")}</Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Change Password Modal */}
      <Modal as={Modal.Dialog} centered show={showPasswordModal} onHide={() => setShowPasswordModal(false)}>
        <Form onSubmit={handlePasswordChange}>
          <Modal.Header closeButton>
            <Modal.Title>{t("change_password", "Change Password")}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <p className="text-muted">Setting new password for <strong>{currentUser?.first_name} {currentUser?.last_name}</strong>.</p>
            <Form.Group className="mb-3">
              <Form.Label>{t("new_password", "New Password")}</Form.Label>
              <Form.Control required type="password" placeholder="Min 6 characters" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowPasswordModal(false)}>{t("cancel", "Cancel")}</Button>
            <Button variant="warning" type="submit">Update Password</Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </>
  );
};
