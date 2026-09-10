import React from "react";
import moment from "moment-timezone";
import { Row, Col, Card } from '@themesberg/react-bootstrap';

export default () => {
  const currentYear = moment().get("year");

  return (
    <div>
      <footer className="footer section py-5">
        <Row>
          <Col xs={12} className="mb-4 mb-lg-0">
            <p className="mb-0 text-center text-xl-center">
              Copyright ©{`${currentYear} `}
              <Card.Link href="https://amasfarm.com" target="_blank" className="text-blue text-decoration-none fw-normal">
                AMAS FARM
              </Card.Link>
            </p>
          </Col>
        </Row>
      </footer>
    </div>
  );
};
