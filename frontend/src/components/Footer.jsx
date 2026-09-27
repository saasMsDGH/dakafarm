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
            <Card.Link href="https://amasfarm.com" target="_blank" className="text-primary fw-bold text-decoration-none">
              AMAS FARM
            </Card.Link>
          </p>
        </Col>

        {/* Creator */}
        <Col xs={12} lg={4} className="mb-2 mb-lg-0 text-center">
          <p className="mb-0 text-muted fw-normal">
            Created by{" "}
            <Card.Link href="" target="_blank" className="text-primary fw-bold text-decoration-none">
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
