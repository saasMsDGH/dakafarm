with open("frontend/src/pages/pos/Purchases.jsx", "r", encoding="utf-8") as f:
    code = f.read()

import re

fetch_inject = """    const fetchDependencies = async () => {
      try {
        const custRes = await api.get(`/api/v1/pos/suppliers/?limit=1000`);
        setSuppliers(custRes.data.items);
        const prodRes = await api.get(`/api/v1/inventory/products/?limit=1000`);
        setProducts(prodRes.data.items);
        const catRes = await api.get(`/api/v1/inventory/product-categories/?limit=100`);
        setCategories(catRes.data.items);
      } catch (error) {"""

code = re.sub(
    r'const fetchDependencies = async \(\) => \{\s*try \{\s*const custRes = await api\.get\(`/api/v1/pos/suppliers/\?limit=1000`\);\s*setSuppliers\(custRes\.data\.items\);\s*const prodRes = await api\.get\(`/api/v1/inventory/products/\?limit=1000`\);\s*setProducts\(prodRes\.data\.items\);\s*\} catch \(error\) \{',
    fetch_inject,
    code
)

with open("frontend/src/pages/pos/Purchases.jsx", "w", encoding="utf-8") as f:
    f.write(code)
