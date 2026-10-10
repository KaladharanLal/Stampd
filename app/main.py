import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from app.db import init_db
from app.routers import destinations, visits, users, lists, pages

BASE_DIR = Path(__file__).resolve().parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure static and templates dirs exist
    os.makedirs(BASE_DIR / "static" / "css", exist_ok=True)
    os.makedirs(BASE_DIR / "static" / "js", exist_ok=True)
    os.makedirs(BASE_DIR / "static" / "vendor", exist_ok=True)
    os.makedirs(BASE_DIR / "templates", exist_ok=True)
    init_db()
    yield

app = FastAPI(
    title="Stampd — Letterboxd for Travelers",
    description="Social destination logging, passport stamps, and travel DNA API for LAYOVER 2026",
    version="1.0.0",
    lifespan=lifespan
)

# Static files & Templates
static_dir = BASE_DIR / "static"
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

templates_dir = BASE_DIR / "templates"
os.makedirs(templates_dir, exist_ok=True)
templates = Jinja2Templates(directory=str(templates_dir))

# Include API Routers
app.include_router(destinations.router)
app.include_router(visits.router)
app.include_router(users.router)
app.include_router(lists.router)
app.include_router(pages.router)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": "Stampd",
        "theme": "LAYOVER 2026",
        "version": "1.0.0"
    }

