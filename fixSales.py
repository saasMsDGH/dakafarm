import re

with open("frontend/src/pages/pos/Sales.jsx", "r") as f:
    code = f.read()

correct_function = """  const handlePrintReceipt = () => {
    if (!currentSale) return;
    
    const printWindow = window.open('', '_blank', 'width=400,height=600');
    
    const itemsHtml = currentSale.items.map(item => `
      <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
        <div style="flex: 2; text-align: left; padding-right: 5px;">
          <div>${getProductName(item.product_id)}</div>
          <div style="color: #555; font-size: 12px;">@ TSh ${parseFloat(item.unit_price).toLocaleString()}</div>
        </div>
        <div style="flex: 1; text-align: center;">${item.quantity}</div>
        <div style="flex: 1; text-align: right;">${parseFloat(item.total_amount).toLocaleString()}</div>
      </div>
    `).join('');

    const paymentMethod = currentSale.payments && currentSale.payments.length > 0 
      ? currentSale.payments[0].payment_method 
      : (currentSale.payment_status === 'PAID' ? 'Cash' : 'Credit');

    const html = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>Receipt - ${currentSale.invoice_number}</title>
          <style>
            @page {
              margin: 0;
              size: 80mm 297mm;
            }
            body { 
              font-family: Arial, sans-serif;
              font-size: 14px; 
              color: #000; 
              margin: 0; 
              padding: 0;
              display: flex;
              justify-content: center;
            }
            .receipt-container {
              width: 300px;
              padding: 10px;
              box-sizing: border-box;
            }
            .text-center { text-align: center; }
            .text-right { text-align: right; }
            .fw-bold { font-weight: bold; }
            .divider { text-align: center; margin: 5px 0; font-family: monospace; letter-spacing: -1px; overflow: hidden; white-space: nowrap; }
            
            h1 { font-size: 28px; font-weight: 900; margin: 5px 0; }
            p { margin: 2px 0; font-size: 14px; }
            .header-text { font-size: 12px; font-weight: bold; margin-bottom: 10px; }
            
            .flex-between { display: flex; justify-content: space-between; margin: 2px 0; }
          </style>
        </head>
        <body>
          <div class="receipt-container">
            <div class="text-center header-text" style="margin-top: 10px;">
              *** START OF SALES RECEIPT ***
            </div>
            
            <div class="text-center">
              <h1>AMAS FARM</h1>
              <p>Dar es Salaam</p>
              <p>Tel: 0712 345 678</p>
              <p>info@amasfarm.com</p>
            </div>
            
            <div class="divider">----------------------------------------------------</div>
            
            <div>
              <p>Receipt:<br/>${currentSale.invoice_number}</p>
              <p>Date: ${new Date(currentSale.sale_date).toLocaleString()}</p>
              <p>Cashier: Admin</p>
              <p>Customer: ${getCustomerName(currentSale.customer_id)}</p>
              <p>Payment: ${paymentMethod}</p>
            </div>
            
            <div class="divider">----------------------------------------------------</div>
            
            <div style="display: flex; justify-content: space-between; font-weight: bold; margin-bottom: 5px;">
              <div style="flex: 2; text-align: left;">ITEM</div>
              <div style="flex: 1; text-align: center;">QTY</div>
              <div style="flex: 1; text-align: right;">AMOUNT</div>
            </div>
            
            ${itemsHtml}
            
            <div class="divider">----------------------------------------------------</div>
            
            <div class="flex-between">
              <span>SUBTOTAL</span>
              <span>TSh ${parseFloat(currentSale.subtotal).toLocaleString()}</span>
            </div>
            <div class="flex-between">
              <span>DISCOUNT</span>
              <span>TSh ${parseFloat(currentSale.discount).toLocaleString()}</span>
            </div>
            <div class="flex-between" style="font-size: 16px; font-weight: 900; margin: 5px 0;">
              <span>TOTAL</span>
              <span>TSh ${parseFloat(currentSale.total_amount).toLocaleString()}</span>
            </div>
            <div class="flex-between">
              <span>CASH / PAID</span>
              <span>TSh ${parseFloat(currentSale.amount_paid).toLocaleString()}</span>
            </div>
            <div class="flex-between">
              <span>BALANCE</span>
              <span>TSh ${(parseFloat(currentSale.total_amount) - parseFloat(currentSale.amount_paid)).toLocaleString()}</span>
            </div>
            
            <br/>
            <div class="text-center">
              <p style="font-weight: bold;">RECEIPT VERIFICATION CODE</p>
              <p style="word-break: break-all;">${currentSale.invoice_number}</p>
            </div>
            
            <br/>
            
            <div class="text-center">
              <h2 style="margin: 0; font-size: 20px; font-weight: 900;">THANK YOU!</h2>
              <p>Glad to see you again!</p>
            </div>
            
            <div class="text-center header-text" style="margin-top: 15px;">
              *** END OF SALES RECEIPT ***
            </div>
          </div>
          
          <script>
            window.onload = function() { 
              setTimeout(function() {
                window.print(); 
                window.close(); 
              }, 300);
            }
          </script>
        </body>
      </html>
    `;
    
    printWindow.document.write(html);
    printWindow.document.close();
  };

  const getStatusBadge ="""

broken_pattern = re.compile(r'  const handlePrintReceipt = \(\) => \{.*?printWindow\.document\.close\(\);\n  \};\n\n  const getStatusBadge =', re.DOTALL)
code = broken_pattern.sub(correct_function, code)

with open("frontend/src/pages/pos/Sales.jsx", "w") as f:
    f.write(code)
