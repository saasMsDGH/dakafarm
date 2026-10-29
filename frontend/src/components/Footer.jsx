import React from "react";
import moment from "moment-timezone";
import { Row, Col, Card } from '@themesberg/react-bootstrap';

export default () => {
  const currentYear = moment().get("year");

  return (
    <footer className="footer section py-3 d-print-none bg-white border-top mt-auto">
      <Row className="align-items-center justify-content-between px-3">
        
        {/* Copyright */}
        <Col xs={12} lg={4} className="mb-2 mb-lg-0 text-center text-lg-start">
          <p className="mb-0 text-muted fw-normal">
            &copy; {currentYear}{" "}
            <Card.Link href="https://github.com/saasMsDGH/dakafarm" target="_blank" className="text-primary fw-bold text-decoration-none">
              DAKAFARM
            </Card.Link>
          </p>
        </Col>

        {/* Creator */}
        <Col xs={12} lg={4} className="mb-2 mb-lg-0 text-center">
          <p className="mb-0 text-muted fw-normal">
            Créé par{" "}
            <Card.Link href="https://github.com/tajirdev" target="_blank" className="text-primary fw-bold text-decoration-none">
              tajirdev
            </Card.Link>
          </p>
        </Col>

        {/* Version */}
        <Col xs={12} lg={4} className="text-center text-lg-end">
          <p className="mb-0 text-muted fw-normal">
            Version 1.0.0
          </p>
        </Col>
        
      </Row>
    </footer>
  );
};
