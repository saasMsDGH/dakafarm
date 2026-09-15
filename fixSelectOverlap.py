with open("frontend/src/pages/pos/Sales.jsx", "r", encoding="utf-8") as f:
    code = f.read()

old_select = """<Form.Group className="mb-3">
                        <Form.Label className="fw-bold">Customer</Form.Label>
                        <Select
                          options={customerOptions}
                          placeholder={t('search_customers')}
                          isClearable
                          onChange={(selected) => setNewSale({...newSale, customer_id: selected ? selected.value : ''})}
                          value={customerOptions.find(o => o.value === newSale.customer_id) || null}
                        />
                      </Form.Group>"""

new_select = """<Form.Group className="mb-4" style={{ position: 'relative', zIndex: 50 }}>
                        <Form.Label className="fw-bold">Customer</Form.Label>
                        <Select
                          options={customerOptions}
                          placeholder={t('search_customers')}
                          isClearable
                          menuPortalTarget={document.body}
                          styles={{ menuPortal: base => ({ ...base, zIndex: 9999 }) }}
                          onChange={(selected) => setNewSale({...newSale, customer_id: selected ? selected.value : ''})}
                          value={customerOptions.find(o => o.value === newSale.customer_id) || null}
                        />
                      </Form.Group>"""

code = code.replace(old_select, new_select)

with open("frontend/src/pages/pos/Sales.jsx", "w", encoding="utf-8") as f:
    f.write(code)
