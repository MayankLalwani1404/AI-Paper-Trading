from fastapi import APIRouter
from backend.api.health import router as health_router
from backend.api.trading import router as trading_router

router = APIRouter()

router.include_router(health_router)
router.include_router(trading_router)
