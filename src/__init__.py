"""Setups up FastAPI Server."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, FastAPI

from .config import Settings

app = FastAPI()


@lru_cache
def get_settings() -> Settings:
    return Settings()


@app.get("/")
async def root(settings: Annotated[Settings, Depends(get_settings)]) -> dict:
    """Root endpoint that returns a greeting message."""
    return settings.model_dump()
