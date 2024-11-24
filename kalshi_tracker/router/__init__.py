from fastapi import APIRouter

from .markets import router as markets_router

router = APIRouter()

router.include_router(markets_router)
