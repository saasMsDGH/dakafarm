import re
with open("backend/app/api/v1/pos/service/SaleService.py", "r") as f:
    code = f.read()

pattern = re.compile(r'        # 6\. Commit the entire transaction.*?return created_sale', re.DOTALL)

replacement = """        # 6. Commit the entire transaction
        try:
            db.expunge(created_sale) # Detach so it doesn't cause expiration conflicts
            await db.commit()
            # Fetch freshly
            final_sale = await SaleRepo.get_by_id(db, created_sale.id)
            return final_sale
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Commit failed: {str(e)}")"""

code = pattern.sub(replacement, code)
with open("backend/app/api/v1/pos/service/SaleService.py", "w") as f:
    f.write(code)
