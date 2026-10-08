"""LandShield backend entry point. Run with: uvicorn app.main:app --reload"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  (importing registers all tables)
from app.database import Base, engine
from app.routes import events as events_routes
from app.routes import properties as properties_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once at startup: create any tables that don't exist yet.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    lifespan=lifespan,
    title="LandShield Backend",
    description="AI Property Change Intelligence - backend API (hackathon demo, synthetic data).",
    version="0.1.0",
)

# Allow the React frontend (any local port) to call this API during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(properties_routes.router)
app.include_router(events_routes.router)


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "service": "landshield-backend"}