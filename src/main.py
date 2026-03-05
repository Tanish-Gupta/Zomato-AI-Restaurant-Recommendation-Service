"""FastAPI application entry point."""

import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import APP_HOST, APP_PORT, LOG_LEVEL
from src.phase3_api.routes import router

logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Warm the restaurant repository on startup so first request has data."""
    try:
        from src.phase1_data.repository import RestaurantRepository
        repo = RestaurantRepository()
        repo.initialize(force_reload=False)
        logger.info("Restaurant repository warmed: %s restaurants", len(repo.data))
    except Exception as e:
        logger.warning("Could not warm repository on startup: %s. First request may be slow or fail.", e)
    yield


app = FastAPI(
    title="AI Restaurant Recommendation Service",
    description="Get personalized restaurant recommendations using preferences and Groq LLM.",
    version="1.0.0",
    lifespan=lifespan,
)
# Allow common dev origins (Vite often uses 5173, 5174, etc.)
_CORS_ORIGINS = [
    "http://localhost:5173", "http://127.0.0.1:5173",
    "http://localhost:5174", "http://127.0.0.1:5174",
    "http://localhost:5175", "http://127.0.0.1:5175",
    "http://localhost:3000", "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/")
def root():
    return {"message": "AI Restaurant Recommendation API", "docs": "/docs"}


def run():
    import uvicorn
    uvicorn.run(app, host=APP_HOST, port=APP_PORT)


if __name__ == "__main__":
    run()
