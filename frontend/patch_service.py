import os

filepath = 'd:/myprojects/AMAS FARM/AMAS-FARM-Management-System/backend/app/api/v1/reports/service/financial.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

old_sig = '''    @staticmethod
    async def get_book_report(
        db: AsyncSession,
        account_id: int,
        params: PaginationParams,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        transaction_type: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> CashBookReport:
        # Fetch account info
        acc_result = await db.execute(select(FinancialAccount).where(FinancialAccount.id == account_id))
        account = acc_result.scalar_one_or_none()
        if not account:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Account not found")'''

new_sig = '''    @staticmethod
    async def get_book_report(
        db: AsyncSession,
        account_id: Optional[int],
        params: PaginationParams,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        transaction_type: Optional[str] = None,
        direction: Optional[str] = None,
        account_type: Optional[str] = None,
    ) -> CashBookReport:
        from fastapi import HTTPException
        # Fetch account info
        if account_id:
            acc_result = await db.execute(select(FinancialAccount).where(FinancialAccount.id == account_id))
            account = acc_result.scalar_one_or_none()
        elif account_type:
            acc_result = await db.execute(select(FinancialAccount).where(FinancialAccount.account_type == account_type).limit(1))
            account = acc_result.scalar_one_or_none()
        else:
            raise HTTPException(status_code=400, detail="Must provide account_id or account_type")

        if not account:
            raise HTTPException(status_code=404, detail=f"No {account_type or ''} account found")
            
        account_id = account.id'''

content = content.replace(old_sig, new_sig)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Service updated")
