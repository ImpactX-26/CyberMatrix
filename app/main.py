
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.database import Base, engine
from app.routes import events as events_routes
from app.routes import properties as properties_routes
from app.routes import documents as documents_routes
from app.routes import reminders as reminders_routes
from app.services.reminder_worker import send_due_reminders_once


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create any missing database tables at startup.
    await asyncio.to_thread(Base.metadata.create_all, bind=engine)
    stop_event = asyncio.Event()

    async def reminder_loop():
        while not stop_event.is_set():
            try:
                await asyncio.to_thread(send_due_reminders_once)
            except Exception:
                logging.getLogger("cybermatrix.reminders").exception(
                    "Reminder worker failed"
                )

            try:
                await asyncio.wait_for(stop_event.wait(), timeout=30)
            except asyncio.TimeoutError:
                pass

    worker = asyncio.create_task(reminder_loop())

    try:
        yield
    finally:
        stop_event.set()
        worker.cancel()
        try:
            await worker
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="CyberMatrix Backend",
    description="CyberMatrix property intelligence backend API.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(properties_routes.router)
app.include_router(events_routes.router)
app.include_router(documents_routes.router)
app.include_router(reminders_routes.router)


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "service": "cybermatrix-backend"}
