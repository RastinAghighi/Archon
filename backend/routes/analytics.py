"""FastAPI router for analytics and dashboard endpoints."""

import json
import os
from typing import List

from fastapi import APIRouter, HTTPException

from backend.schemas.models import (
    DailySnapshot,
    KnowledgeGraphSummary,
    ProgressOverview,
    PublicDashboardData,
)
from backend.services.episode_service import episode_service

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

# Project root for reading snapshot files
PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
ANALYTICS_DIR = os.path.join(PROJECT_ROOT, "output", "analytics")


@router.get("/overview", response_model=ProgressOverview)
def get_progress_overview():
    """Return high-level progress overview."""
    try:
        return episode_service.get_progress_overview()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute overview: {e}")


@router.get("/snapshot", response_model=DailySnapshot)
def get_latest_snapshot():
    """Return the latest daily analytics snapshot."""
    # Try to read the latest snapshot file first
    snapshot_path = os.path.join(ANALYTICS_DIR, "latest_snapshot.json")
    if os.path.exists(snapshot_path):
        try:
            with open(snapshot_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, KeyError):
            pass

    # Fall back to computing a fresh snapshot
    try:
        snapshot = episode_service.analytics.compute_daily_snapshot()
        return snapshot
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute snapshot: {e}")


@router.get("/history", response_model=List[DailySnapshot])
def get_snapshot_history():
    """Return all historical snapshots for charting."""
    try:
        cursor = episode_service.db.conn.cursor()
        cursor.execute(
            "SELECT snapshot_data FROM analytics_snapshots ORDER BY date ASC"
        )
        rows = cursor.fetchall()
        snapshots = []
        for row in rows:
            try:
                data = json.loads(row["snapshot_data"]) if isinstance(row["snapshot_data"], str) else row["snapshot_data"]
                snapshots.append(data)
            except (json.JSONDecodeError, TypeError):
                continue
        return snapshots
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {e}")


@router.get("/knowledge-graph", response_model=KnowledgeGraphSummary)
def get_knowledge_graph():
    """Return the full knowledge graph with all topics and their status."""
    try:
        return episode_service.get_knowledge_graph()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load knowledge graph: {e}")


@router.get("/score-history")
def get_score_history():
    """Return assessment scores over time for charting."""
    try:
        return episode_service.analytics.get_score_history()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve score history: {e}")


@router.get("/public", response_model=PublicDashboardData)
def get_public_dashboard():
    """Return the public recruiter-facing dashboard data. No authentication required."""
    # Try cached file first for fast response
    dashboard_path = os.path.join(ANALYTICS_DIR, "public_dashboard.json")
    if os.path.exists(dashboard_path):
        try:
            with open(dashboard_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, KeyError):
            pass

    # Fall back to computing fresh data
    try:
        return episode_service.get_public_dashboard_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate public dashboard: {e}")
