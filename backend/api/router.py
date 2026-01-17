from fastapi import APIRouter
from backend.api.health import router as health_router
from backend.api.trading import router as trading_router
from backend.api.market_data import router as market_data_router
from backend.api.indicators import router as indicators_router

router = APIRouter()

router.include_router(health_router)
router.include_router(trading_router)
router.include_router(market_data_router)
router.include_router(indicators_router)
