import os

path = 'frontend/src/pages/inventory/Products.jsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add Tabs to import
content = content.replace("Pagination } from", "Pagination, Tabs, Tab } from")

# Add activeTab state
content = content.replace('const [searchTerm, setSearchTerm] = useState("");', 'const [searchTerm, setSearchTerm] = useState("");\n  const [activeTab, setActiveTab] = useState("all");')

# Update fetchProducts to use activeTab
fetch_old = """  const fetchProducts = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/inventory/products/', {
        params: { page, limit: 10, search: searchTerm }
      });"""

fetch_new = """  const fetchProducts = async () => {
    setLoading(true);
    try {
      const params = { page, limit: 10, search: searchTerm };
      if (activeTab === 'low_stock') params.status_filter = 'Low Stock';
      if (activeTab === 'out_of_stock') params.status_filter = 'Out of Stock';
      
      const response = await api.get('/api/v1/inventory/products/', { params });"""

content = content.replace(fetch_old, fetch_new)

# Add activeTab to useEffect dependencies
content = content.replace('}, [page, searchTerm]);', '}, [page, searchTerm, activeTab]);')

# Add Tabs above the Table
tabs_jsx = """
      <Tabs activeKey={activeTab} onSelect={(k) => { setActiveTab(k); setPage(1); }} className="mb-3">
        <Tab eventKey="all" title={t('all_products', 'All Products')} />
        <Tab eventKey="low_stock" title={<span className="text-warning">{t('low_stock', 'Low Stock')}</span>} />
        <Tab eventKey="out_of_stock" title={<span className="text-danger">{t('out_of_stock', 'Out of Stock')}</span>} />
      </Tabs>

      <Card border="light" className="table-wrapper table-responsive shadow-sm">"""

content = content.replace('<Card border="light" className="table-wrapper table-responsive shadow-sm">', tabs_jsx)

# Also let's translate the table and modals while we're at it
content = content.replace('<th>Category</th>', '<th>{t("category", "Category")}</th>')
content = content.replace('<th>Product Name</th>', '<th>{t("product_name", "Product Name")}</th>')
content = content.replace('<th>Unit</th>', '<th>{t("unit", "Unit")}</th>')
content = content.replace('<th>Buying Price</th>', '<th>{t("buying_price", "Buying Price")}</th>')
content = content.replace('<th>Selling Price</th>', '<th>{t("selling_price", "Selling Price")}</th>')
content = content.replace('<th>Current Stock</th>', '<th>{t("current_stock", "Current Stock")}</th>')
content = content.replace('<th>Reorder Level</th>', '<th>{t("reorder_level", "Reorder Level")}</th>')
content = content.replace('<th>Status</th>', '<th>{t("status", "Status")}</th>')
content = content.replace('<th>Actions</th>', '<th>{t("actions", "Actions")}</th>')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Products.jsx updated with tabs!")
