with open("frontend/src/pages/pos/Customers.jsx", "r", encoding="utf-8") as f:
    code = f.read()

# Replace customer specific terms with supplier
code = code.replace("Customer", "Supplier")
code = code.replace("customer", "supplier")
code = code.replace("CUSTOMERS", "SUPPLIERS")

# Remove business_type and credit_limit, add contact_person
code = code.replace("business_type: '',", "contact_person: '',")
code = code.replace("credit_limit: '0.00'", "")

code = code.replace("<th className=\"border-bottom\">{t('business_type')}</th>", "<th className=\"border-bottom\">{t('contact_person')}</th>")
code = code.replace("<td><span className=\"fw-normal\">{supplier.business_type}</span></td>", "<td><span className=\"fw-normal\">{supplier.contact_person}</span></td>")

code = code.replace("<th className=\"border-bottom\">{t('credit_limit')}</th>", "")
code = code.replace("<td><span className=\"fw-bold text-primary\">{supplier.credit_limit}</span></td>", "")

# Form replace
form_replace = """<Col md={6}>
                <Form.Group id="contact_person" className="mb-3">
                  <Form.Label>{t('contact_person')}</Form.Label>
                  <Form.Control 
                    type="text" 
                    name="contact_person"
                    value={currentSupplier.contact_person} 
                    onChange={handleInputChange} 
                  />
                </Form.Group>
              </Col>"""
code = code.replace("""<Col md={6}>
                <Form.Group id="business_type" className="mb-3">
                  <Form.Label>{t('business_type')}</Form.Label>
                  <Form.Control 
                    type="text" 
                    name="business_type"
                    value={currentSupplier.business_type} 
                    onChange={handleInputChange} 
                  />
                </Form.Group>
              </Col>""", form_replace)

code = code.replace("""<Col md={6}>
                <Form.Group id="credit_limit" className="mb-3">
                  <Form.Label>{t('credit_limit')}</Form.Label>
                  <Form.Control 
                    type="number"
                    step="0.01" 
                    name="credit_limit"
                    value={currentSupplier.credit_limit} 
                    onChange={handleInputChange} 
                  />
                </Form.Group>
              </Col>""", "")

with open("frontend/src/pages/pos/Suppliers.jsx", "w", encoding="utf-8") as f:
    f.write(code)
