import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faSave,
  faUserShield,
  faLanguage,
  faUser,
  faLock,
  faEye,
  faEyeSlash,
  faEnvelope,
  faPhone,
  faKey,
  faCheck,
  faShieldAlt,
  faCalendarAlt,
  faCheckCircle,
  faGlobe,
  faExclamationTriangle,
  faChevronRight,
  faInfoCircle,
  faWarehouse,
  faDove,
  faEgg,
  faSeedling,
  faSyringe,
  faHeartbeat
} from "@fortawesome/free-solid-svg-icons";
import {
  Col,
  Row,
  Card,
  Form,
  Button,
  InputGroup,
  Badge,
  Alert,
  Spinner
} from "@themesberg/react-bootstrap";
import { useTranslation } from "react-i18next";
import { useAuth } from "../context/AuthContext";
import { api } from "../api/axios";
import moment from "moment";
import Swal from "sweetalert2";

export default () => {
  const { t, i18n } = useTranslation();
  const { user, fetchUser } = useAuth();

  // Active navigation tab
  const [activeTab, setActiveTab] = useState("personal");

  // Profile Info State
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
  });
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [profileFeedback, setProfileFeedback] = useState(null);

  // Sync user object into formData whenever user updates
  useEffect(() => {
    if (user) {
      setFormData({
        first_name: user.first_name || "",
        last_name: user.last_name || "",
        email: user.email || "",
        phone: user.phone || "",
      });
    }
  }, [user]);

  // Password State
  const [passwordData, setPasswordData] = useState({
    old_password: "",
    new_password: "",
    confirm_password: ""
  });
  const [showOldPass, setShowOldPass] = useState(false);
  const [showNewPass, setShowNewPass] = useState(false);
  const [showConfirmPass, setShowConfirmPass] = useState(false);
  const [isChangingPass, setIsChangingPass] = useState(false);
  const [passFeedback, setPassFeedback] = useState(null);

  const handleInfoChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handlePassChange = (e) => {
    setPasswordData({ ...passwordData, [e.target.name]: e.target.value });
  };

  const handleLanguageChange = (lang) => {
    i18n.changeLanguage(lang);
    Swal.fire({
      toast: true,
      position: 'top-end',
      icon: 'success',
      title: lang === 'sw' ? 'Lugha imebadilishwa kuwa Kiswahili' : 'Language switched to English',
      showConfirmButton: false,
      timer: 2000,
      timerProgressBar: true
    });
  };

  const updateProfile = async (e) => {
    e.preventDefault();
    setIsSavingProfile(true);
    setProfileFeedback(null);

    try {
      await api.put(`/api/v1/user/${user.id}`, {
        first_name: formData.first_name,
        last_name: formData.last_name,
        email: formData.email,
        phone: formData.phone
      });
      await fetchUser(); // refresh auth context
      setProfileFeedback({ type: "success", text: t("profile_updated") });
      Swal.fire({
        icon: "success",
        title: t("profile_updated"),
        timer: 2200,
        showConfirmButton: false
      });
    } catch (error) {
      const errText = error.response?.data?.detail || t("failed_update_profile");
      setProfileFeedback({ type: "danger", text: errText });
      Swal.fire({
        icon: "error",
        title: t("failed_update_profile"),
        text: errText
      });
    } finally {
      setIsSavingProfile(false);
    }
  };

  const updatePassword = async (e) => {
    e.preventDefault();
    setPassFeedback(null);

    if (passwordData.new_password.length < 6) {
      setPassFeedback({ type: "danger", text: t("password_rules") });
      return;
    }

    if (passwordData.new_password !== passwordData.confirm_password) {
      setPassFeedback({ type: "danger", text: t("passwords_mismatch") });
      return;
    }

    setIsChangingPass(true);
    try {
      await api.put(`/api/v1/user/${user.id}/password`, {
        old_password: passwordData.old_password,
        new_password: passwordData.new_password
      });
      setPassFeedback({ type: "success", text: t("password_changed") });
      setPasswordData({ old_password: "", new_password: "", confirm_password: "" });
      Swal.fire({
        icon: "success",
        title: t("password_changed"),
        timer: 2200,
        showConfirmButton: false
      });
    } catch (error) {
      const errText = error.response?.data?.detail || t("failed_change_password");
      setPassFeedback({ type: "danger", text: errText });
      Swal.fire({
        icon: "error",
        title: t("failed_change_password"),
        text: errText
      });
    } finally {
      setIsChangingPass(false);
    }
  };

  // Compute initials for the avatar badge
  const getAvatarInitials = () => {
    const f = (formData.first_name || user?.first_name || "").trim();
    const l = (formData.last_name || user?.last_name || "").trim();
    if (f && l) return `${f[0]}${l[0]}`.toUpperCase();
    if (f) return f.slice(0, 2).toUpperCase();
    return "AF";
  };

  // Nav menu items
  const navItems = [
    {
      id: "personal",
      title: t("profile_info_tab", "Personal Details"),
      desc: t("profile_info_sub", "Name, contact phone & email"),
      icon: faUser,
    },
    {
      id: "security",
      title: t("security_tab", "Security & Password"),
      desc: t("security_sub", "Manage your password & access"),
      icon: faLock,
    },
    {
      id: "preferences",
      title: t("preferences_tab", "Language & Display"),
      desc: t("preferences_sub", "Choose system language"),
      icon: faGlobe,
    },
    {
      id: "permissions",
      title: t("permissions_tab", "Roles & Access"),
      desc: t("permissions_sub", "View assigned responsibilities"),
      icon: faUserShield,
    },
  ];

  const currentRole = user?.role_name || t("role_worker");
  const isAdmin = currentRole.toLowerCase().includes("admin");

  return (
    <>
      {/* Header section */}
      <div className="py-4">
        <div className="d-flex justify-content-between align-items-center flex-wrap">
          <div>
            <h2 className="h4 fw-bold text-dark mb-1">
              {t("account_settings", "Account Settings")}
            </h2>
            <p className="text-muted small mb-0">
              {t("profile_subtitle", "Manage your personal information, security credentials, and system preferences.")}
            </p>
          </div>
        </div>
      </div>

      <Row>
        {/* Left Column: Profile Card & Vertical Navigation */}
        <Col xs={12} lg={4} className="mb-4">
          {/* Identity Card */}
          <Card border="light" className="bg-white shadow-sm rounded-3 overflow-hidden mb-4 border-0">
            {/* AMAS Gradient Banner */}
            <div
              style={{
                height: "110px",
                background: "linear-gradient(135deg, #0d3b2e 0%, #157347 50%, #198754 100%)",
                position: "relative",
                padding: "12px 16px",
              }}
            >
              <div className="d-flex justify-content-between align-items-center">
                <span
                  className="badge bg-white text-success fw-bold px-2 py-1 shadow-sm"
                  style={{ fontSize: "0.72rem", letterSpacing: "0.5px" }}
                >
                  DAKAFARM
                </span>
                <span
                  className={`badge ${user?.is_active !== false ? "bg-success" : "bg-secondary"} text-white shadow-sm px-2 py-1`}
                  style={{ fontSize: "0.72rem" }}
                >
                  <FontAwesomeIcon icon={faCheckCircle} className="me-1" />
                  {user?.is_active !== false ? t("active_status", "Active") : t("inactive", "Inactive")}
                </span>
              </div>
            </div>

            {/* Profile Avatar & Info */}
            <div className="px-4 pb-4 pt-0 text-center">
              <div
                className="rounded-circle mx-auto d-flex align-items-center justify-content-center text-white fw-bold shadow"
                style={{
                  width: "82px",
                  height: "82px",
                  marginTop: "-41px",
                  background: "linear-gradient(135deg, #1f2937 0%, #374151 100%)",
                  border: "4px solid #ffffff",
                  fontSize: "1.65rem",
                  letterSpacing: "1px",
                  position: "relative",
                  zIndex: 2,
                }}
              >
                {getAvatarInitials()}
              </div>

              <h5 className="mt-3 mb-1 fw-bold text-dark">
                {formData.first_name || user?.first_name} {formData.last_name || user?.last_name}
              </h5>

              <div className="mb-3">
                <Badge bg="light" className="text-primary border border-primary px-3 py-2 fw-semibold">
                  <FontAwesomeIcon icon={faShieldAlt} className="me-2" />
                  {currentRole}
                </Badge>
              </div>

              {/* Quick Contacts & Details */}
              <div className="text-start bg-light rounded-3 p-3 mt-3">
                <div className="d-flex align-items-center text-secondary mb-2 small">
                  <div
                    className="rounded-circle bg-white shadow-xs d-flex align-items-center justify-content-center me-2 text-primary"
                    style={{ width: "24px", height: "24px" }}
                  >
                    <FontAwesomeIcon icon={faEnvelope} style={{ fontSize: "0.75rem" }} />
                  </div>
                  <span className="text-truncate fw-medium">{user?.email || "—"}</span>
                </div>

                <div className="d-flex align-items-center text-secondary mb-2 small">
                  <div
                    className="rounded-circle bg-white shadow-xs d-flex align-items-center justify-content-center me-2 text-success"
                    style={{ width: "24px", height: "24px" }}
                  >
                    <FontAwesomeIcon icon={faPhone} style={{ fontSize: "0.75rem" }} />
                  </div>
                  <span className="fw-medium">{user?.phone || "—"}</span>
                </div>

                <div className="d-flex align-items-center text-secondary small">
                  <div
                    className="rounded-circle bg-white shadow-xs d-flex align-items-center justify-content-center me-2 text-warning"
                    style={{ width: "24px", height: "24px" }}
                  >
                    <FontAwesomeIcon icon={faCalendarAlt} style={{ fontSize: "0.75rem" }} />
                  </div>
                  <span className="fw-medium">
                    {t("member_since")}: {user?.created_at ? moment(user.created_at).format("MMM YYYY") : "—"}
                  </span>
                </div>
              </div>
            </div>
          </Card>

          {/* Navigation Pill Menu Card */}
          <Card border="light" className="bg-white shadow-sm rounded-3 border-0">
            <Card.Body className="p-2">
              <div className="d-flex flex-column gap-2">
                {navItems.map((item) => {
                  const isActive = activeTab === item.id;
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => setActiveTab(item.id)}
                      className={`w-100 text-start border-0 rounded-3 p-3 d-flex align-items-center justify-content-between transition-all ${
                        isActive
                          ? "bg-primary text-white shadow-sm"
                          : "bg-white text-secondary hover-bg-light"
                      }`}
                      style={{
                        cursor: "pointer",
                        transition: "all 0.2s ease",
                      }}
                    >
                      <div className="d-flex align-items-center">
                        <div
                          className={`rounded-circle d-flex align-items-center justify-content-center me-3 ${
                            isActive ? "bg-white text-primary" : "bg-light text-primary"
                          }`}
                          style={{ width: "36px", height: "36px", minWidth: "36px" }}
                        >
                          <FontAwesomeIcon icon={item.icon} />
                        </div>
                        <div>
                          <div className={`fw-bold small ${isActive ? "text-white" : "text-dark"}`}>
                            {item.title}
                          </div>
                          <div
                            className={`small ${isActive ? "text-white-50" : "text-muted"}`}
                            style={{ fontSize: "0.76rem" }}
                          >
                            {item.desc}
                          </div>
                        </div>
                      </div>
                      <FontAwesomeIcon
                        icon={faChevronRight}
                        className={`ms-2 small ${isActive ? "text-white" : "text-muted"}`}
                        style={{ opacity: isActive ? 1 : 0.4 }}
                      />
                    </button>
                  );
                })}
              </div>
            </Card.Body>
          </Card>
        </Col>

        {/* Right Column: Tab Panels */}
        <Col xs={12} lg={8}>
          {/* TAB 1: PERSONAL INFORMATION */}
          {activeTab === "personal" && (
            <Card border="light" className="bg-white shadow-sm rounded-3 border-0 mb-4">
              <Card.Header className="bg-transparent border-bottom p-4">
                <div className="d-flex align-items-center">
                  <div
                    className="rounded-circle bg-primary bg-opacity-10 text-primary d-flex align-items-center justify-content-center me-3"
                    style={{ width: "42px", height: "42px" }}
                  >
                    <FontAwesomeIcon icon={faUser} />
                  </div>
                  <div>
                    <h5 className="mb-0 fw-bold text-dark">{t("personal_info", "Personal Information")}</h5>
                    <p className="text-muted small mb-0">
                      {t("profile_info_sub", "Update your personal profile details and contact information.")}
                    </p>
                  </div>
                </div>
              </Card.Header>

              <Card.Body className="p-4">
                {profileFeedback && (
                  <Alert
                    variant={profileFeedback.type}
                    onClose={() => setProfileFeedback(null)}
                    dismissible
                    className="mb-4 py-2"
                  >
                    <FontAwesomeIcon
                      icon={profileFeedback.type === "success" ? faCheckCircle : faExclamationTriangle}
                      className="me-2"
                    />
                    {profileFeedback.text}
                  </Alert>
                )}

                <Form onSubmit={updateProfile}>
                  <Row className="mb-3">
                    <Col md={6} className="mb-3 mb-md-0">
                      <Form.Group id="first_name">
                        <Form.Label className="small fw-bold text-secondary">
                          {t("first_name", "First Name")} <span className="text-danger">*</span>
                        </Form.Label>
                        <InputGroup>
                          <InputGroup.Text className="bg-light border-end-0">
                            <FontAwesomeIcon icon={faUser} className="text-muted" />
                          </InputGroup.Text>
                          <Form.Control
                            required
                            type="text"
                            name="first_name"
                            className="border-start-0 ps-0"
                            placeholder="John"
                            value={formData.first_name}
                            onChange={handleInfoChange}
                          />
                        </InputGroup>
                      </Form.Group>
                    </Col>

                    <Col md={6}>
                      <Form.Group id="last_name">
                        <Form.Label className="small fw-bold text-secondary">
                          {t("last_name", "Last Name")} <span className="text-danger">*</span>
                        </Form.Label>
                        <InputGroup>
                          <InputGroup.Text className="bg-light border-end-0">
                            <FontAwesomeIcon icon={faUser} className="text-muted" />
                          </InputGroup.Text>
                          <Form.Control
                            required
                            type="text"
                            name="last_name"
                            className="border-start-0 ps-0"
                            placeholder="Doe"
                            value={formData.last_name}
                            onChange={handleInfoChange}
                          />
                        </InputGroup>
                      </Form.Group>
                    </Col>
                  </Row>

                  <Row className="mb-4">
                    <Col md={6} className="mb-3 mb-md-0">
                      <Form.Group id="email">
                        <Form.Label className="small fw-bold text-secondary">
                          {t("email", "Email Address")} <span className="text-danger">*</span>
                        </Form.Label>
                        <InputGroup>
                          <InputGroup.Text className="bg-light border-end-0">
                            <FontAwesomeIcon icon={faEnvelope} className="text-muted" />
                          </InputGroup.Text>
                          <Form.Control
                            required
                            type="email"
                            name="email"
                            className="border-start-0 ps-0"
                            placeholder="john@example.com"
                            value={formData.email}
                            onChange={handleInfoChange}
                          />
                        </InputGroup>
                      </Form.Group>
                    </Col>

                    <Col md={6}>
                      <Form.Group id="phone">
                        <Form.Label className="small fw-bold text-secondary">
                          {t("phone", "Phone Number")} <span className="text-danger">*</span>
                        </Form.Label>
                        <InputGroup>
                          <InputGroup.Text className="bg-light border-end-0">
                            <FontAwesomeIcon icon={faPhone} className="text-muted" />
                          </InputGroup.Text>
                          <Form.Control
                            required
                            type="text"
                            name="phone"
                            className="border-start-0 ps-0"
                            placeholder="+255 7XX XXX XXX"
                            value={formData.phone}
                            onChange={handleInfoChange}
                          />
                        </InputGroup>
                      </Form.Group>
                    </Col>
                  </Row>

                  {/* Read-only System Role Box */}
                  <div className="bg-light rounded-3 p-3 mb-4 border">
                    <div className="d-flex align-items-center justify-content-between flex-wrap gap-2">
                      <div>
                        <div className="small fw-bold text-dark">{t("assigned_role", "Assigned Role")}</div>
                        <div className="text-muted small">
                          <FontAwesomeIcon icon={faInfoCircle} className="me-1 text-primary" />
                          {t("role_notice", "Role is assigned and managed by system administrator")}
                        </div>
                      </div>
                      <Badge bg="secondary" className="px-3 py-2 text-white">
                        <FontAwesomeIcon icon={faShieldAlt} className="me-1" />
                        {currentRole}
                      </Badge>
                    </div>
                  </div>

                  <div className="d-flex justify-content-end">
                    <Button
                      variant="primary"
                      type="submit"
                      disabled={isSavingProfile}
                      className="px-4 py-2 fw-semibold"
                    >
                      {isSavingProfile ? (
                        <>
                          <Spinner animation="border" size="sm" className="me-2" />
                          {t("saving_changes", "Saving changes...")}
                        </>
                      ) : (
                        <>
                          <FontAwesomeIcon icon={faSave} className="me-2" />
                          {t("save_changes", "Save Changes")}
                        </>
                      )}
                    </Button>
                  </div>
                </Form>
              </Card.Body>
            </Card>
          )}

          {/* TAB 2: SECURITY & PASSWORD */}
          {activeTab === "security" && (
            <Card border="light" className="bg-white shadow-sm rounded-3 border-0 mb-4">
              <Card.Header className="bg-transparent border-bottom p-4">
                <div className="d-flex align-items-center">
                  <div
                    className="rounded-circle bg-primary bg-opacity-10 text-primary d-flex align-items-center justify-content-center me-3"
                    style={{ width: "42px", height: "42px" }}
                  >
                    <FontAwesomeIcon icon={faLock} />
                  </div>
                  <div>
                    <h5 className="mb-0 fw-bold text-dark">{t("security_password", "Security & Password")}</h5>
                    <p className="text-muted small mb-0">
                      {t("security_sub", "Manage your account password and security credentials.")}
                    </p>
                  </div>
                </div>
              </Card.Header>

              <Card.Body className="p-4">
                {passFeedback && (
                  <Alert
                    variant={passFeedback.type}
                    onClose={() => setPassFeedback(null)}
                    dismissible
                    className="mb-4 py-2"
                  >
                    <FontAwesomeIcon
                      icon={passFeedback.type === "success" ? faCheckCircle : faExclamationTriangle}
                      className="me-2"
                    />
                    {passFeedback.text}
                  </Alert>
                )}

                <Form onSubmit={updatePassword}>
                  <div className="mb-4">
                    <Form.Group id="oldPassword">
                      <Form.Label className="small fw-bold text-secondary">
                        {t("current_password_label", "Current Password")} <span className="text-danger">*</span>
                      </Form.Label>
                      <InputGroup>
                        <InputGroup.Text className="bg-light border-end-0">
                          <FontAwesomeIcon icon={faLock} className="text-muted" />
                        </InputGroup.Text>
                        <Form.Control
                          required
                          type={showOldPass ? "text" : "password"}
                          name="old_password"
                          className="border-start-0 border-end-0 ps-0"
                          placeholder="••••••••"
                          value={passwordData.old_password}
                          onChange={handlePassChange}
                        />
                        <Button
                          variant="outline-light"
                          className="border border-start-0 text-muted"
                          type="button"
                          onClick={() => setShowOldPass(!showOldPass)}
                          title={showOldPass ? "Hide" : "Show"}
                        >
                          <FontAwesomeIcon icon={showOldPass ? faEyeSlash : faEye} />
                        </Button>
                      </InputGroup>
                    </Form.Group>
                  </div>

                  <Row className="mb-4">
                    <Col md={6} className="mb-3 mb-md-0">
                      <Form.Group id="newPassword">
                        <Form.Label className="small fw-bold text-secondary">
                          {t("new_password_label", "New Password")} <span className="text-danger">*</span>
                        </Form.Label>
                        <InputGroup>
                          <InputGroup.Text className="bg-light border-end-0">
                            <FontAwesomeIcon icon={faKey} className="text-muted" />
                          </InputGroup.Text>
                          <Form.Control
                            required
                            type={showNewPass ? "text" : "password"}
                            name="new_password"
                            className="border-start-0 border-end-0 ps-0"
                            placeholder="••••••••"
                            value={passwordData.new_password}
                            onChange={handlePassChange}
                          />
                          <Button
                            variant="outline-light"
                            className="border border-start-0 text-muted"
                            type="button"
                            onClick={() => setShowNewPass(!showNewPass)}
                            title={showNewPass ? "Hide" : "Show"}
                          >
                            <FontAwesomeIcon icon={showNewPass ? faEyeSlash : faEye} />
                          </Button>
                        </InputGroup>
                        <div className="small mt-1 d-flex align-items-center">
                          {passwordData.new_password.length >= 6 ? (
                            <span className="text-success">
                              <FontAwesomeIcon icon={faCheckCircle} className="me-1" />
                              {t("password_rules", "Password must be at least 6 characters long.")}
                            </span>
                          ) : (
                            <span className="text-muted">
                              <FontAwesomeIcon icon={faInfoCircle} className="me-1" />
                              {t("password_rules", "Password must be at least 6 characters long.")}
                            </span>
                          )}
                        </div>
                      </Form.Group>
                    </Col>

                    <Col md={6}>
                      <Form.Group id="confirmPassword">
                        <Form.Label className="small fw-bold text-secondary">
                          {t("confirm_password_label", "Confirm New Password")} <span className="text-danger">*</span>
                        </Form.Label>
                        <InputGroup>
                          <InputGroup.Text className="bg-light border-end-0">
                            <FontAwesomeIcon icon={faKey} className="text-muted" />
                          </InputGroup.Text>
                          <Form.Control
                            required
                            type={showConfirmPass ? "text" : "password"}
                            name="confirm_password"
                            className="border-start-0 border-end-0 ps-0"
                            placeholder="••••••••"
                            value={passwordData.confirm_password}
                            onChange={handlePassChange}
                          />
                          <Button
                            variant="outline-light"
                            className="border border-start-0 text-muted"
                            type="button"
                            onClick={() => setShowConfirmPass(!showConfirmPass)}
                            title={showConfirmPass ? "Hide" : "Show"}
                          >
                            <FontAwesomeIcon icon={showConfirmPass ? faEyeSlash : faEye} />
                          </Button>
                        </InputGroup>
                        {passwordData.confirm_password.length > 0 && (
                          <div className="small mt-1 d-flex align-items-center">
                            {passwordData.new_password === passwordData.confirm_password ? (
                              <span className="text-success">
                                <FontAwesomeIcon icon={faCheckCircle} className="me-1" />
                                {t("passwords_match_indicator", "Passwords match")}
                              </span>
                            ) : (
                              <span className="text-danger">
                                <FontAwesomeIcon icon={faExclamationTriangle} className="me-1" />
                                {t("passwords_mismatch_indicator", "Passwords do not match")}
                              </span>
                            )}
                          </div>
                        )}
                      </Form.Group>
                    </Col>
                  </Row>

                  <div className="d-flex justify-content-end">
                    <Button
                      variant="primary"
                      type="submit"
                      disabled={isChangingPass}
                      className="px-4 py-2 fw-semibold"
                    >
                      {isChangingPass ? (
                        <>
                          <Spinner animation="border" size="sm" className="me-2" />
                          {t("updating_pass", "Updating password...")}
                        </>
                      ) : (
                        <>
                          <FontAwesomeIcon icon={faLock} className="me-2" />
                          {t("update_password", "Update Password")}
                        </>
                      )}
                    </Button>
                  </div>
                </Form>
              </Card.Body>
            </Card>
          )}

          {/* TAB 3: LANGUAGE & PREFERENCES */}
          {activeTab === "preferences" && (
            <Card border="light" className="bg-white shadow-sm rounded-3 border-0 mb-4">
              <Card.Header className="bg-transparent border-bottom p-4">
                <div className="d-flex align-items-center">
                  <div
                    className="rounded-circle bg-primary bg-opacity-10 text-primary d-flex align-items-center justify-content-center me-3"
                    style={{ width: "42px", height: "42px" }}
                  >
                    <FontAwesomeIcon icon={faGlobe} />
                  </div>
                  <div>
                    <h5 className="mb-0 fw-bold text-dark">{t("preferences_tab", "Language & Display")}</h5>
                    <p className="text-muted small mb-0">
                      {t("preferences_sub", "Choose your preferred system language.")}
                    </p>
                  </div>
                </div>
              </Card.Header>

              <Card.Body className="p-4">
                <Row className="g-3 mb-4">
                  {/* French Card */}
                  <Col md={6}>
                    <div
                      onClick={() => handleLanguageChange("fr")}
                      className={`p-4 rounded-3 border transition-all h-100 position-relative ${
                        i18n.language === "fr"
                          ? "border-primary bg-primary bg-opacity-10 shadow-sm"
                          : "border-light bg-light hover-shadow"
                      }`}
                      style={{ cursor: "pointer", transition: "all 0.2s ease" }}
                    >
                      <div className="d-flex align-items-start justify-content-between mb-3">
                        <div
                          className="rounded-circle bg-primary bg-opacity-10 text-primary d-flex align-items-center justify-content-center shadow-xs"
                          style={{ width: "46px", height: "46px" }}
                        >
                          <FontAwesomeIcon icon={faGlobe} size="lg" />
                        </div>
                        {i18n.language === "fr" ? (
                          <Badge bg="primary" className="px-2 py-1 text-white">
                            <FontAwesomeIcon icon={faCheck} className="me-1" />
                            {t("active_language", "Active Language")}
                          </Badge>
                        ) : (
                          <Badge bg="light" className="text-secondary border">
                            {t("select_this_language", "Select this language")}
                          </Badge>
                        )}
                      </div>
                      <h6 className="fw-bold text-dark mb-1">{t("french_language", "Français")}</h6>
                      <p className="text-muted small mb-0">
                        {t("french_display_desc", "Interface affichée en français")}
                      </p>
                    </div>
                  </Col>

                  {/* English Card */}
                  <Col md={6}>
                    <div
                      onClick={() => handleLanguageChange("en")}
                      className={`p-4 rounded-3 border transition-all h-100 position-relative ${
                        i18n.language === "en"
                          ? "border-primary bg-primary bg-opacity-10 shadow-sm"
                          : "border-light bg-light hover-shadow"
                      }`}
                      style={{ cursor: "pointer", transition: "all 0.2s ease" }}
                    >
                      <div className="d-flex align-items-start justify-content-between mb-3">
                        <div
                          className="rounded-circle bg-primary bg-opacity-10 text-primary d-flex align-items-center justify-content-center shadow-xs"
                          style={{ width: "46px", height: "46px" }}
                        >
                          <FontAwesomeIcon icon={faGlobe} size="lg" />
                        </div>
                        {i18n.language === "en" ? (
                          <Badge bg="primary" className="px-2 py-1 text-white">
                            <FontAwesomeIcon icon={faCheck} className="me-1" />
                            {t("active_language", "Active Language")}
                          </Badge>
                        ) : (
                          <Badge bg="light" className="text-secondary border">
                            {t("select_this_language", "Select this language")}
                          </Badge>
                        )}
                      </div>
                      <h6 className="fw-bold text-dark mb-1">{t("english_language", "English")}</h6>
                      <p className="text-muted small mb-0">
                        {t("english_display_desc", "System interface displayed in English")}
                      </p>
                    </div>
                  </Col>

                  {/* Kiswahili Card */}
                  <Col md={6}>
                    <div
                      onClick={() => handleLanguageChange("sw")}
                      className={`p-4 rounded-3 border transition-all h-100 position-relative ${
                        i18n.language === "sw"
                          ? "border-primary bg-primary bg-opacity-10 shadow-sm"
                          : "border-light bg-light hover-shadow"
                      }`}
                      style={{ cursor: "pointer", transition: "all 0.2s ease" }}
                    >
                      <div className="d-flex align-items-start justify-content-between mb-3">
                        <div
                          className="rounded-circle bg-success bg-opacity-10 text-success d-flex align-items-center justify-content-center shadow-xs"
                          style={{ width: "46px", height: "46px" }}
                        >
                          <FontAwesomeIcon icon={faLanguage} size="lg" />
                        </div>
                        {i18n.language === "sw" ? (
                          <Badge bg="primary" className="px-2 py-1 text-white">
                            <FontAwesomeIcon icon={faCheck} className="me-1" />
                            {t("active_language", "Active Language")}
                          </Badge>
                        ) : (
                          <Badge bg="light" className="text-secondary border">
                            {t("select_this_language", "Select this language")}
                          </Badge>
                        )}
                      </div>
                      <h6 className="fw-bold text-dark mb-1">{t("swahili_language", "Kiswahili")}</h6>
                      <p className="text-muted small mb-0">
                        {t("swahili_display_desc", "Mfumo mzima unaonekana kwa Kiswahili")}
                      </p>
                    </div>
                  </Col>
                </Row>

                <div className="bg-light rounded-3 p-3 border">
                  <div className="d-flex align-items-start">
                    <FontAwesomeIcon icon={faInfoCircle} className="text-primary me-2 mt-1" />
                    <p className="small text-muted mb-0">
                      {i18n.language === "fr" ? "La langue choisie s’applique aux menus, formulaires et tableaux." : i18n.language === "sw"
                        ? "Mabadiliko ya lugha hutumika mara moja kwenye menyu zote, fomu, ripoti za uendeshaji na jumbe za taarifa za mfumo mzima."
                        : "Language preferences apply immediately across all navigation panels, tables, forms, and alerts throughout the system."}
                    </p>
                  </div>
                </div>
              </Card.Body>
            </Card>
          )}

          {/* TAB 4: ROLES & ACCESS PERMISSIONS */}
          {activeTab === "permissions" && (
            <Card border="light" className="bg-white shadow-sm rounded-3 border-0 mb-4">
              <Card.Header className="bg-transparent border-bottom p-4">
                <div className="d-flex align-items-center">
                  <div
                    className="rounded-circle bg-primary bg-opacity-10 text-primary d-flex align-items-center justify-content-center me-3"
                    style={{ width: "42px", height: "42px" }}
                  >
                    <FontAwesomeIcon icon={faUserShield} />
                  </div>
                  <div>
                    <h5 className="mb-0 fw-bold text-dark">{t("permissions_tab", "Roles & Access")}</h5>
                    <p className="text-muted small mb-0">
                      {t("permissions_sub", "View assigned responsibilities and module access.")}
                    </p>
                  </div>
                </div>
              </Card.Header>

              <Card.Body className="p-4">
                {/* Role hero banner */}
                <div className="bg-light rounded-3 p-4 border mb-4">
                  <div className="d-flex align-items-center justify-content-between flex-wrap gap-2 mb-2">
                    <h6 className="fw-bold text-dark mb-0">{t("assigned_role", "Assigned Role")}</h6>
                    <Badge bg="primary" className="px-3 py-2 text-white fs-6">
                      <FontAwesomeIcon icon={faShieldAlt} className="me-2" />
                      {currentRole}
                    </Badge>
                  </div>
                  <p className="text-muted small mb-0">
                    {isAdmin
                      ? t("administrator_role_desc", "Full Administrative Access: Complete management of farm operations, finance, inventory, HR, and user accounts.")
                      : t("worker_role_desc", "Farm Operations Access: Routine recording of flocks, productions, feeds, and health records.")}
                  </p>
                </div>

                {/* Module Access Cards */}
                <h6 className="fw-bold text-dark mb-3">
                  {t("module_access", "Module Access & Responsibilities")}
                </h6>
                <Row className="g-3 mb-4">
                  {[
                    { title: t("houses", "Houses"), desc: "Banda layout, capacity & structure", icon: faWarehouse, color: "text-primary" },
                    { title: t("flocks", "Flocks"), desc: "Flock batches, arrivals & ages", icon: faDove, color: "text-info" },
                    { title: t("productions", "Productions"), desc: "Daily egg collection & yields", icon: faEgg, color: "text-warning" },
                    { title: t("feeds", "Feeds"), desc: "Feed distribution & warehouse stock", icon: faSeedling, color: "text-success" },
                    { title: t("vaccinations", "Vaccinations"), desc: "Schedules & health protocols", icon: faSyringe, color: "text-danger" },
                    { title: t("mortalities", "Mortalities"), desc: "Loss records & health alerts", icon: faHeartbeat, color: "text-secondary" },
                  ].map((mod, i) => (
                    <Col md={6} key={i}>
                      <div className="d-flex align-items-center p-3 rounded-3 border bg-white h-100">
                        <div
                          className={`rounded-circle bg-light ${mod.color} d-flex align-items-center justify-content-center me-3 flex-shrink-0 shadow-xs`}
                          style={{ width: "42px", height: "42px", fontSize: "1.1rem" }}
                        >
                          <FontAwesomeIcon icon={mod.icon} />
                        </div>
                        <div className="flex-grow-1">
                          <div className="fw-bold small text-dark">{mod.title}</div>
                          <div className="text-muted small" style={{ fontSize: "0.78rem" }}>
                            {mod.desc}
                          </div>
                        </div>
                        <span className="badge bg-success bg-opacity-10 text-success rounded-circle p-2 ms-2">
                          <FontAwesomeIcon icon={faCheck} />
                        </span>
                      </div>
                    </Col>
                  ))}
                </Row>

                {/* Notice Box */}
                <div className="bg-light rounded-3 p-3 border">
                  <div className="d-flex align-items-center text-muted small">
                    <FontAwesomeIcon icon={faInfoCircle} className="text-primary me-2 flex-shrink-0" />
                    <span>
                      {t("role_contact_help", "To request permission updates or transfer role responsibilities, please contact the farm administrator.")}
                    </span>
                  </div>
                </div>
              </Card.Body>
            </Card>
          )}
        </Col>
      </Row>
    </>
  );
};
