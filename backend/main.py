"""Archon API — Main FastAPI application."""

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from backend.routes import analytics, assessments, episodes, pipeline, sources

app = FastAPI(
    title="Archon API",
    description="Personalized AI Learning Platform — Backend API",
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(episodes.router)
app.include_router(assessments.router)
app.include_router(sources.router)
app.include_router(analytics.router)
app.include_router(pipeline.router)

# ---------------------------------------------------------------------------
# Static file serving
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

pdfs_dir = PROJECT_ROOT / "output" / "pdfs"
markdown_dir = PROJECT_ROOT / "output" / "markdown"

if pdfs_dir.exists():
    app.mount("/files/pdfs", StaticFiles(directory=str(pdfs_dir)), name="pdfs")
if markdown_dir.exists():
    app.mount("/files/markdown", StaticFiles(directory=str(markdown_dir)), name="markdown")

# ---------------------------------------------------------------------------
# Root & health
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    return {
        "name": "Archon API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/api/health")
async def health():
    episodes_dir = PROJECT_ROOT / "output" / "pdfs"
    count = len([f for f in episodes_dir.glob("*.pdf")]) if episodes_dir.exists() else 0
    return {
        "status": "healthy",
        "episodes_generated": count,
        "pipeline_running": False,
    }


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup():
    print("🚀 Archon API running at http://localhost:8000")
    print("📚 API docs at http://localhost:8000/docs")


# ---------------------------------------------------------------------------
# Dev entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
