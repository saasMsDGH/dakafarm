import asyncio
from app.core.database import sessionlocal
from app.api.v1.finance.repository.BookRepo import BookRepo
from app.shared.pagination import PaginationParams

async def main():
    async with sessionlocal() as db:
        try:
            params = PaginationParams(page=2, limit=2)
            await BookRepo.list_transactions(db, account_id=1, params=params)
            print("OK")
        except Exception as e:
            print("ERROR:", e)

asyncio.run(main())
