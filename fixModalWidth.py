import re
with open("frontend/src/pages/pos/Sales.jsx", "r", encoding="utf-8") as f:
    code = f.read()

# Add dialogClassName
code = code.replace("size=\"xl\" centered show={showNewSaleModal}", "size=\"xl\" dialogClassName=\"modal-90w\" centered show={showNewSaleModal}")

# Inject <style> before return (
style_block = """
  return (
    <>
      <style>{`
        .modal-90w {
          max-width: 90% !important;
        }
      `}</style>
"""

code = code.replace("  return (\n    <>", style_block)

with open("frontend/src/pages/pos/Sales.jsx", "w", encoding="utf-8") as f:
    f.write(code)
