import React, { useState } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSave, faUserShield, faLanguage } from '@fortawesome/free-solid-svg-icons';
import { Col, Row, Card, Form, Button } from '@themesberg/react-bootstrap';
import { useTranslation } from 'react-i18next';
import { useAuth } from "../context/AuthContext";
import { api } from "../api/axios";

export default () => {
  const { t, i18n } = useTranslation();
  const { user, fetchUser } = useAuth();
  
  // Profile Info State
  const [formData, setFormData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    phone: user?.phone || '',
  });
  const [infoMessage, setInfoMessage] = useState(null);

  // Password State
  const [passwordData, setPasswordData] = useState({
    old_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [passMessage, setPassMessage] = useState(null);

  const handleInfoChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handlePassChange = (e) => {
    setPasswordData({ ...passwordData, [e.target.name]: e.target.value });
  };

  const changeLanguage = (e) => {
    i18n.changeLanguage(e.target.value);
  };

  const updateProfile = async (e) => {
    e.preventDefault();
    setInfoMessage({ type: 'info', text: t('updating_profile') });
    try {
      await api.put(`/api/v1/user/${user.id}`, {
        first_name: formData.first_name,
        last_name: formData.last_name,
        email: formData.email,
        phone: formData.phone
      });
      await fetchUser(); // refresh auth context
      setInfoMessage({ type: 'success', text: t('profile_updated') });
    } catch (error) {
      setInfoMessage({ 
        type: 'danger', 
        text: error.response?.data?.detail || t('failed_update_profile') 
      });
    }
  };

  const updatePassword = async (e) => {
    e.preventDefault();
    if (passwordData.new_password !== passwordData.confirm_password) {
      setPassMessage({ type: 'danger', text: t('passwords_mismatch') });
      return;
    }
    
    setPassMessage({ type: 'info', text: t('updating_password') });
    try {
      await api.put(`/api/v1/user/${user.id}/password`, {
        old_password: passwordData.old_password,
        new_password: passwordData.new_password
      });
      setPassMessage({ type: 'success', text: t('password_changed') });
      setPasswordData({ old_password: '', new_password: '', confirm_password: '' });
    } catch (error) {
      setPassMessage({ 
        type: 'danger', 
        text: error.response?.data?.detail || t('failed_change_password') 
      });
    }
  };

  return (
    <>
      <div className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center py-4">
        <h2>{t('settings_title')}</h2>
      </div>

      <Row>
        <Col xs={12} xl={8}>
          <Card border="light" className="bg-white shadow-sm mb-4">
            <Card.Body>
              <h5 className="mb-4">{t('general_info')}</h5>
              {infoMessage && (
                <div className={`alert alert-${infoMessage.type}`} role="alert">
                  {infoMessage.text}
                </div>
              )}
              <Form onSubmit={updateProfile}>
                <Row>
                  <Col md={6} className="mb-3">
                    <Form.Group id="firstName">
                      <Form.Label>{t('first_name')}</Form.Label>
                      <Form.Control required type="text" name="first_name" value={formData.first_name} onChange={handleInfoChange} />
                    </Form.Group>
                  </Col>
                  <Col md={6} className="mb-3">
                    <Form.Group id="lastName">
                      <Form.Label>{t('last_name')}</Form.Label>
                      <Form.Control required type="text" name="last_name" value={formData.last_name} onChange={handleInfoChange} />
                    </Form.Group>
                  </Col>
                </Row>
                <Row>
                  <Col md={6} className="mb-3">
                    <Form.Group id="email">
                      <Form.Label>{t('email')}</Form.Label>
                      <Form.Control required type="email" name="email" value={formData.email} onChange={handleInfoChange} />
                    </Form.Group>
                  </Col>
                  <Col md={6} className="mb-3">
                    <Form.Group id="phone">
                      <Form.Label>{t('phone')}</Form.Label>
                      <Form.Control required type="text" name="phone" value={formData.phone} onChange={handleInfoChange} />
                    </Form.Group>
                  </Col>
                </Row>
                <div className="mt-3">
                  <Button variant="primary" type="submit">
                    <FontAwesomeIcon icon={faSave} className="me-2" /> {t('save_all')}
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>

          <Card border="light" className="bg-white shadow-sm mb-4">
            <Card.Body>
              <h5 className="mb-4">{t('change_password')}</h5>
              {passMessage && (
                <div className={`alert alert-${passMessage.type}`} role="alert">
                  {passMessage.text}
                </div>
              )}
              <Form onSubmit={updatePassword}>
                <Row>
                  <Col md={12} className="mb-3">
                    <Form.Group id="oldPassword">
                      <Form.Label>{t('current_password')}</Form.Label>
                      <Form.Control required type="password" name="old_password" value={passwordData.old_password} onChange={handlePassChange} />
                    </Form.Group>
                  </Col>
                </Row>
                <Row>
                  <Col md={6} className="mb-3">
                    <Form.Group id="newPassword">
                      <Form.Label>{t('new_password')}</Form.Label>
                      <Form.Control required type="password" name="new_password" value={passwordData.new_password} onChange={handlePassChange} />
                    </Form.Group>
                  </Col>
                  <Col md={6} className="mb-3">
                    <Form.Group id="confirmPassword">
                      <Form.Label>{t('confirm_password')}</Form.Label>
                      <Form.Control required type="password" name="confirm_password" value={passwordData.confirm_password} onChange={handlePassChange} />
                    </Form.Group>
                  </Col>
                </Row>
                <div className="mt-3">
                  <Button variant="secondary" type="submit">
                    <FontAwesomeIcon icon={faSave} className="me-2" /> {t('update_password')}
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>
        </Col>

        <Col xs={12} xl={4}>
          <Card border="light" className="text-center p-0 mb-4">
            <div className="profile-cover rounded-top" data-background="../assets/img/profile-cover.jpg"></div>
            <Card.Body className="pb-5">
              <Card.Title>{user?.first_name} {user?.last_name}</Card.Title>
              <Card.Subtitle className="fw-normal"><FontAwesomeIcon icon={faUserShield} className="me-2" />{user?.role_name || t('role_worker')}</Card.Subtitle>
              <Card.Text className="text-gray mb-4 mt-2">
                {t('profile_description')}
              </Card.Text>
            </Card.Body>
          </Card>

          <Card border="light" className="shadow-sm mb-4">
            <Card.Body>
              <h5 className="mb-4">
                <FontAwesomeIcon icon={faLanguage} className="me-2" /> 
                {t('language_settings')}
              </h5>
              <Form.Group id="languageSelect">
                <Form.Label>{t('select_language')}</Form.Label>
                <Form.Select value={i18n.language} onChange={changeLanguage}>
                  <option value="en">English</option>
                  <option value="sw">Swahili</option>
                </Form.Select>
              </Form.Group>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </>
  );
};
