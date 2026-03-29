"""FastAPI router for source management endpoints."""

from typing import List

from fastapi import APIRouter, HTTPException

from backend.schemas.models import (
    Source,
    SourceAddRequest,
    SourceTestResult,
    SourceToggleRequest,
)
from backend.services.episode_service import episode_service

router = APIRouter(prefix="/api/sources", tags=["Sources"])


@router.get("/", response_model=List[Source])
def list_sources():
    """Return all sources from the registry."""
    return episode_service.get_sources()


@router.post("/", response_model=Source)
def add_source(request: SourceAddRequest):
    """Add a new source with auto-detected type and fetcher."""
    # Check for duplicate
    existing = episode_service.source_registry.get_source(request.id)
    if existing is not None:
        raise HTTPException(status_code=409, detail=f"Source '{request.id}' already exists")

    source_dict = {
        "id": request.id,
        "name": request.name,
        "url": request.url,
        "categories": request.categories,
        "quality": request.quality,
    }

    success = episode_service.add_source(source_dict)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add source")

    # Return the newly created source
    created = episode_service.source_registry.get_source(request.id)
    return created


@router.put("/{source_id}/toggle", response_model=Source)
def toggle_source(source_id: str, request: SourceToggleRequest):
    """Enable or disable a source."""
    success = episode_service.toggle_source(source_id, request.enabled)
    if not success:
        raise HTTPException(status_code=404, detail=f"Source '{source_id}' not found")

    updated = episode_service.source_registry.get_source(source_id)
    return updated


@router.post("/{source_id}/test", response_model=SourceTestResult)
def test_source(source_id: str):
    """Test a source by fetching one piece of content. May take a few seconds."""
    result = episode_service.test_source(source_id)
    return result


@router.delete("/{source_id}")
def delete_source(source_id: str):
    """Remove a source from the registry."""
    source = episode_service.source_registry.get_source(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail=f"Source '{source_id}' not found")

    episode_service.source_registry.remove_source(source_id)
    return {"deleted": True, "source_id": source_id}
