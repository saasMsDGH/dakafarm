from fastapi import APIRouter
from app.api.v1.assets.Router import asset_router

router = APIRouter(prefix="/assets")
router.include_router(asset_router.router)
