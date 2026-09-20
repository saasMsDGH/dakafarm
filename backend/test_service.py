import asyncio
from app.api.v1.reports.service.operations import OperationsReportService
from app.core.database import sessionlocal

async def test_service():
    async with sessionlocal() as db:
        res = await OperationsReportService.get_master_summary(db)
        print(res.model_dump_json(indent=2))

asyncio.run(test_service())
