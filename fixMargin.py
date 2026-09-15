with open("frontend/src/pages/pos/Sales.jsx", "r") as f:
    code = f.read()

# Replace A4 @page margin
code = code.replace("""@page {
              margin: 20mm;
              size: A4 portrait;
            }""", """@page {
              margin: 0; /* This removes the about:blank browser footer */
              size: A4 portrait;
            }""")

# Add padding to body to compensate for 0 margin in @page
code = code.replace("""body { 
              font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
              font-size: 14px; 
              color: #333; 
              margin: 0; 
              padding: 0;
            }""", """body { 
              font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
              font-size: 14px; 
              color: #333; 
              margin: 0; 
              padding: 20mm; /* Added padding here instead of @page margin */
            }""")

with open("frontend/src/pages/pos/Sales.jsx", "w") as f:
    f.write(code)
