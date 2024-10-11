"""Setups up FastAPI Server."""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root() -> dict:
    """Root endpoint that returns a greeting message."""
    return {"message": "Hello World"}
