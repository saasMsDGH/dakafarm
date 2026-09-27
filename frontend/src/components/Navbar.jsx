import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSignOutAlt, faLanguage } from "@fortawesome/free-solid-svg-icons";
import { faUserCircle } from "@fortawesome/free-regular-svg-icons";
import { Nav, Navbar, Dropdown, Container } from '@themesberg/react-bootstrap';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import { useAuth } from "../context/AuthContext";
import { Routes } from "../routes";

export default (props) => {
  const { t, i18n } = useTranslation();
  const { user, logout } = useAuth();

  const UserAvatar = ({ name }) => {
    const initial = name ? name.charAt(0).toUpperCase() : 'U';
    return (
      <div 
        className="user-avatar md-avatar rounded-circle d-flex align-items-center justify-content-center bg-secondary text-white fw-bold"
        style={{ fontSize: '1.2rem' }}
      >
        {initial}
      </div>
    );
  };

  const isSwahili = i18n.language?.startsWith('sw');

  return (
    <Navbar variant="dark" expanded className="ps-0 pe-2 pb-0 d-print-none">
      <Container fluid className="px-0">
        <div className="d-flex justify-content-end w-100">
          <Nav className="align-items-center">
            {/* Language Switcher */}
            <Dropdown as={Nav.Item} className="me-3">
              <Dropdown.Toggle as={Nav.Link} className="pt-1 px-2 d-flex align-items-center text-dark">
                <FontAwesomeIcon icon={faLanguage} className="me-1 text-primary" style={{ fontSize: '1.2rem' }} />
                <span className="fw-bold small text-uppercase">
                  {isSwahili ? 'SW' : 'EN'}
                </span>
              </Dropdown.Toggle>
              <Dropdown.Menu className="user-dropdown dropdown-menu-right mt-2">
                <Dropdown.Item 
                  onClick={() => i18n.changeLanguage('en')} 
                  className={`fw-bold ${!isSwahili ? 'text-primary' : ''}`}
                >
                  🇺🇸 English (EN)
                </Dropdown.Item>
                <Dropdown.Item 
                  onClick={() => i18n.changeLanguage('sw')} 
                  className={`fw-bold ${isSwahili ? 'text-primary' : ''}`}
                >
                  🇹🇿 Kiswahili (SW)
                </Dropdown.Item>
              </Dropdown.Menu>
            </Dropdown>

            <Dropdown as={Nav.Item}>
              <Dropdown.Toggle as={Nav.Link} className="pt-1 px-0">
                <div className="media d-flex align-items-center">
                  <UserAvatar name={user?.first_name} />
                  <div className="media-body ms-2 text-dark align-items-center d-none d-lg-block">
                    <span className="mb-0 font-small fw-bold">{user?.first_name} {user?.last_name}</span>
                  </div>
                </div>
              </Dropdown.Toggle>
              <Dropdown.Menu className="user-dropdown dropdown-menu-right mt-2">
                <Dropdown.Item as={Link} to={Routes.Settings.path} className="fw-bold">
                  <FontAwesomeIcon icon={faUserCircle} className="me-2" /> {t('my_profile')}
                </Dropdown.Item>

                <Dropdown.Divider />

                <Dropdown.Item onClick={logout} className="fw-bold">
                  <FontAwesomeIcon icon={faSignOutAlt} className="text-danger me-2" /> {t('logout', 'Logout')}
                </Dropdown.Item>
              </Dropdown.Menu>
            </Dropdown>
          </Nav>
        </div>
      </Container>
    </Navbar>
  );
};
