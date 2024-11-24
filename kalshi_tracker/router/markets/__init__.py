from fastapi import APIRouter

from .get_markets import router as get_markets_router

router = APIRouter(prefix="/markets", tags=["markets"])

router.include_router(get_markets_router)
