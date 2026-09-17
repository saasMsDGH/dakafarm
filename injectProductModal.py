with open("frontend/src/pages/pos/Purchases.jsx", "r", encoding="utf-8") as f:
    code = f.read()

import re

# 1. State for New Product Modal
state_inject = """  const [page, setPage] = useState(1);
  const [showProductModal, setShowProductModal] = useState(false);
  const [categories, setCategories] = useState([]);
  const [newProduct, setNewProduct] = useState({
    name: '',
    category_id: '',
    unit_of_measure: '',
    unit_price: 0,
    selling_price: 0,
    current_stock: 0,
    is_active: true
  });

  const handleCreateProduct = async () => {
    if (!newProduct.name || !newProduct.category_id || !newProduct.unit_of_measure) {
      Swal.fire('Error', 'Please fill all required fields', 'error');
      return;
    }
    try {
      const payload = {
        ...newProduct,
        category_id: parseInt(newProduct.category_id),
        unit_price: parseFloat(newProduct.unit_price) || 0,
        selling_price: parseFloat(newProduct.selling_price) || 0,
      };
      const response = await api.post('/api/v1/inventory/products/', payload);
      setProducts([response.data, ...products]);
      setShowProductModal(false);
      setNewProduct({ name: '', category_id: '', unit_of_measure: '', unit_price: 0, selling_price: 0, current_stock: 0, is_active: true });
      Swal.fire('Success', 'Product created successfully', 'success');
    } catch (error) {
      Swal.fire('Error', error.response?.data?.detail || 'Failed to create product', 'error');
    }
  };"""

code = code.replace("  const [page, setPage] = useState(1);", state_inject)

# 2. Fetch categories in initial load
fetch_inject = """  const fetchData = async () => {
    setLoading(true);
    try {
      const [suppRes, prodRes, catRes] = await Promise.all([
        api.get('/api/v1/pos/suppliers/', { params: { limit: 100 } }),
        api.get('/api/v1/inventory/products/', { params: { limit: 1000 } }),
        api.get('/api/v1/inventory/product-categories/', { params: { limit: 100 } })
      ]);
      setSuppliers(suppRes.data.items || []);
      setProducts(prodRes.data.items || []);
      setCategories(catRes.data.items || []);
    } catch (error) {"""

code = re.sub(
    r'const fetchData = async \(\) => \{\s*setLoading\(true\);\s*try \{\s*const \[suppRes, prodRes\] = await Promise\.all\(\[\s*api\.get\(\'/api/v1/pos/suppliers/\', \{ params: \{ limit: 100 \} \}\),\s*api\.get\(\'/api/v1/inventory/products/\', \{ params: \{ limit: 1000 \} \}\)\s*\]\);\s*setSuppliers\(suppRes\.data\.items \|\| \[\]\);\s*setProducts\(prodRes\.data\.items \|\| \[\]\);\s*\} catch \(error\) \{',
    fetch_inject,
    code
)


# 3. Add button next to Search
search_inject = """                    <div className="d-flex mb-3 gap-2">
                      <InputGroup>
                        <InputGroup.Text><FontAwesomeIcon icon={faSearch} /></InputGroup.Text>
                        <Form.Control 
                          type="text" 
                          placeholder="Search products..." 
                          value={productSearch}
                          onChange={(e) => setProductSearch(e.target.value)}
                        />
                      </InputGroup>
                      <Button variant="outline-primary" style={{ whiteSpace: 'nowrap' }} onClick={() => setShowProductModal(true)}>
                        <FontAwesomeIcon icon={faPlus} className="me-2" /> New Product
                      </Button>
                    </div>"""

code = re.sub(
    r'<InputGroup className="mb-3">[\s\S]*?</InputGroup>',
    search_inject,
    code,
    count=1
)

# 4. Add the Modal JSX at the end before returning
modal_inject = """      <Modal show={showProductModal} onHide={() => setShowProductModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Create New Product</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Product Name *</Form.Label>
              <Form.Control type="text" value={newProduct.name} onChange={e => setNewProduct({...newProduct, name: e.target.value})} required />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Category *</Form.Label>
              <Form.Select value={newProduct.category_id} onChange={e => setNewProduct({...newProduct, category_id: e.target.value})} required>
                <option value="">-- Select Category --</option>
                {categories.map(c => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Unit of Measure *</Form.Label>
              <Form.Control type="text" placeholder="e.g. kg, trays" value={newProduct.unit_of_measure} onChange={e => setNewProduct({...newProduct, unit_of_measure: e.target.value})} required />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowProductModal(false)}>Cancel</Button>
          <Button variant="primary" onClick={handleCreateProduct}>Create Product</Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};"""

code = code.replace(
    """    </>
  );
};""",
    modal_inject
)

with open("frontend/src/pages/pos/Purchases.jsx", "w", encoding="utf-8") as f:
    f.write(code)
