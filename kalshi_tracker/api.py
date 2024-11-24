"""Setups up FastAPI Server."""

from fastapi import FastAPI

from kalshi_tracker.router import router

app = FastAPI()

app.include_router(router)
