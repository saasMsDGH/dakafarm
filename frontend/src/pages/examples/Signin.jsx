import React, { useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEnvelope, faUnlockAlt } from "@fortawesome/free-solid-svg-icons";
import { Col, Row, Form, Card, Button, Container, InputGroup, Alert, ButtonGroup } from '@themesberg/react-bootstrap';
import { useHistory } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import { useAuth } from "../../context/AuthContext";
import { Routes } from "../../routes";

// You can create/use a customized background if you want
import BgImage from "../../assets/img/illustrations/farm-signin.svg";

export default () => {
  const { t, i18n } = useTranslation();
  const { login } = useAuth();
  const history = useHistory();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await login(username, password);
      history.push(Routes.CampaignData.path);
    } catch (err) {
      setError(err.response?.data?.detail || t('login_failed', 'Network error. Please try again.'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main>
      <section 
        className="d-flex align-items-center my-5 mt-lg-6 mb-lg-5 vh-100" 
        style={{ 
          backgroundImage: `url(${BgImage})`, 
          backgroundSize: 'cover', 
          backgroundPosition: 'center', 
          backgroundRepeat: 'no-repeat',
          marginTop: '0 !important',
          marginBottom: '0 !important'
        }}
      >
        <Container>
          <Row className="justify-content-center">
            <Col xs={12} className="d-flex align-items-center justify-content-center">
              <div className="bg-white shadow-soft border rounded border-light p-4 p-lg-5 w-100 fmxw-500" style={{ opacity: 0.95 }}>
                <div className="d-flex justify-content-end mb-3">
                  <ButtonGroup size="sm">
                    <Button variant={i18n.language?.startsWith('fr') ? 'primary' : 'outline-primary'} size="sm" onClick={() => i18n.changeLanguage('fr')}>FR</Button>
                    <Button 
                      variant={i18n.language?.startsWith('en') ? 'primary' : 'outline-primary'}
                      size="sm" 
                      onClick={() => i18n.changeLanguage('en')}
                      className="py-1 px-2 font-xs fw-bold"
                    >
                      EN
                    </Button>
                    <Button 
                      variant={i18n.language?.startsWith('sw') ? 'primary' : 'outline-primary'} 
                      size="sm" 
                      onClick={() => i18n.changeLanguage('sw')}
                      className="py-1 px-2 font-xs fw-bold"
                    >
                      SW
                    </Button>
                  </ButtonGroup>
                </div>

                <div className="text-center text-md-center mb-4 mt-md-0">
                  <h3 className="mb-0 text-primary">DAKAFARM</h3>
                  <p className="mt-2 text-gray">{t('welcome')}</p>
                </div>
                
                {error && <Alert variant="danger">{error}</Alert>}

                <Form className="mt-4" onSubmit={handleLogin}>
                  <Form.Group id="username" className="mb-4">
                    <Form.Label>{t('email_or_username', 'Email or Username')}</Form.Label>
                    <InputGroup>
                      <InputGroup.Text>
                        <FontAwesomeIcon icon={faEnvelope} />
                      </InputGroup.Text>
                      <Form.Control 
                        autoFocus 
                        required 
                        type="text" 
                        placeholder="adresse@exemple.fr"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                      />
                    </InputGroup>
                  </Form.Group>
                  <Form.Group id="password" className="mb-4">
                    <Form.Label>{t('password', 'Password')}</Form.Label>
                    <InputGroup>
                      <InputGroup.Text>
                        <FontAwesomeIcon icon={faUnlockAlt} />
                      </InputGroup.Text>
                      <Form.Control 
                        required 
                        type="password" 
                        placeholder="********" 
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                      />
                    </InputGroup>
                  </Form.Group>
                  
                  <Button variant="primary" type="submit" className="w-100" disabled={isLoading}>
                    {isLoading ? t('signing_in', 'Signing in...') : t('login')}
                  </Button>
                </Form>
              </div>
            </Col>
          </Row>
        </Container>
      </section>
    </main>
  );
};
