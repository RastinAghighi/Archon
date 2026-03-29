"""FastAPI router for pipeline control endpoints."""

import os

import yaml
from fastapi import APIRouter, HTTPException

from backend.schemas.models import (
    EpisodeGenerateResponse,
    PipelineRunRequest,
    PipelineStatus,
)
from backend.services.episode_service import episode_service

router = APIRouter(prefix="/api/pipeline", tags=["Pipeline"])

# Project root for reading config
PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))


@router.get("/status", response_model=PipelineStatus)
def get_pipeline_status():
    """Return current pipeline status."""
    return episode_service.get_pipeline_status()


@router.post("/run", response_model=EpisodeGenerateResponse)
def run_pipeline(request: PipelineRunRequest):
    """Trigger a full pipeline run (synchronous, may take 1-3 minutes)."""
    if episode_service._pipeline_running:
        raise HTTPException(status_code=409, detail="Pipeline is already running")

    try:
        result = episode_service.generate_episode(
            topic_id=request.topic_id,
            skip_pdf=request.skip_pdf,
            skip_assessment=request.skip_assessment,
            skip_sources=request.skip_sources,
            skip_push=request.skip_push,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {e}")


@router.get("/config")
def get_pipeline_config():
    """Return current pipeline configuration from settings.yaml."""
    config_path = os.path.join(PROJECT_ROOT, "config", "settings.yaml")
    if not os.path.exists(config_path):
        raise HTTPException(status_code=404, detail="Configuration file not found")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # Strip sensitive keys before returning
        config.pop("api", None)

        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read config: {e}")
