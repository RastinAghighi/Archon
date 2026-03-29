"""FastAPI router for episode-related endpoints."""

from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.schemas.models import (
    EpisodeDetail,
    EpisodeGenerateRequest,
    EpisodeGenerateResponse,
    EpisodeSummary,
)
from backend.services.episode_service import episode_service
from src.curriculum_planner import plan_next_episode

router = APIRouter(prefix="/api/episodes", tags=["Episodes"])


@router.get("/next")
def get_next_episode():
    """Return what the next episode would be without generating it."""
    plan = plan_next_episode()
    if plan is None:
        raise HTTPException(status_code=404, detail="Curriculum complete — no topics remaining")
    return plan


@router.get("/", response_model=List[EpisodeSummary])
def list_episodes():
    """Return all episodes sorted by episode_num descending (newest first)."""
    episodes = episode_service.get_all_episodes()
    episodes.sort(key=lambda e: e["episode_num"], reverse=True)
    return episodes


@router.get("/{episode_num}", response_model=EpisodeDetail)
def get_episode(episode_num: int):
    """Return full details for a specific episode."""
    episode = episode_service.get_episode(episode_num)
    if episode is None:
        raise HTTPException(status_code=404, detail=f"Episode {episode_num} not found")
    return episode


@router.get("/{episode_num}/pdf")
def get_episode_pdf(episode_num: int):
    """Download the PDF file for an episode."""
    pdf_path = episode_service.get_episode_pdf_path(episode_num)
    if pdf_path is None:
        raise HTTPException(status_code=404, detail=f"PDF not found for episode {episode_num}")
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"episode_{episode_num:03d}.pdf",
    )


@router.get("/{episode_num}/markdown")
def get_episode_markdown(episode_num: int):
    """Return raw markdown content as plain text."""
    episode = episode_service.get_episode(episode_num)
    if episode is None or episode.get("markdown_content") is None:
        raise HTTPException(status_code=404, detail=f"Markdown not found for episode {episode_num}")
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(content=episode["markdown_content"])


@router.post("/generate", response_model=EpisodeGenerateResponse)
def generate_episode(request: EpisodeGenerateRequest):
    """Trigger generation of a new episode (synchronous, 1-3 minutes)."""
    result = episode_service.generate_episode(
        topic_id=request.topic_id,
        skip_pdf=request.skip_pdf,
        skip_assessment=request.skip_assessment,
        skip_sources=request.skip_sources,
        skip_push=request.skip_push,
        use_paper=request.use_paper,
    )
    return result
