with open("frontend/src/pages/inventory/Products.jsx", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    """              <Col md={6}>
                                <Col md={6}>
                <Form.Group id="current_stock" className="mb-3">""",
    """              </Col>
              <Col md={6}>
                <Form.Group id="current_stock" className="mb-3">"""
)

with open("frontend/src/pages/inventory/Products.jsx", "w", encoding="utf-8") as f:
    f.write(code)
