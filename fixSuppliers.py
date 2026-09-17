with open("frontend/src/pages/pos/Suppliers.jsx", "r", encoding="utf-8") as f:
    code = f.read()

import re
form_fields = """            <Form.Group className="mb-3">
              <Form.Label>{t('name')} *</Form.Label>
              <Form.Control type="text" name="name" value={currentSupplier.name} onChange={handleChange} required />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>{t('contact_person')}</Form.Label>
              <Form.Control type="text" name="contact_person" value={currentSupplier.contact_person || ''} onChange={handleChange} />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>{t('phone')}</Form.Label>
              <Form.Control type="text" name="phone" value={currentSupplier.phone || ''} onChange={handleChange} />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>{t('email')}</Form.Label>
              <Form.Control type="email" name="email" value={currentSupplier.email || ''} onChange={handleChange} />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>{t('address')}</Form.Label>
              <Form.Control type="text" name="address" value={currentSupplier.address || ''} onChange={handleChange} />
            </Form.Group>"""

code = re.sub(
    r'<Modal\.Body>[\s\S]*?</Modal\.Body>',
    '<Modal.Body>\n' + form_fields + '\n          </Modal.Body>',
    code
)

with open("frontend/src/pages/pos/Suppliers.jsx", "w", encoding="utf-8") as f:
    f.write(code)
