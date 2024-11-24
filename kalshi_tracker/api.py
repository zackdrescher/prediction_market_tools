"""Setups up FastAPI Server."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, FastAPI

from kalshi_tracker.config import Settings
from kalshi_tracker.router import router

app = FastAPI()

app.include_router(router)


@lru_cache
def get_settings() -> Settings:
    """Get settings from the environment.

    This function is cached to prevent multiple calls to the environment.
    """
    return Settings()


@app.get("/")
async def root(settings: Annotated[Settings, Depends(get_settings)]) -> dict:
    """Root endpoint that returns a greeting message."""
    return settings.model_dump()
