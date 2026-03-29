"""Pydantic models defining request/response shapes for the Archon API."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# 1. EPISODE MODELS
# ---------------------------------------------------------------------------


class EpisodeSummary(BaseModel):
    """Brief episode info for list views."""

    id: int
    episode_num: int
    topic_id: str
    topic_name: str
    depth: str
    phase: int
    category: str
    generated_at: str  # ISO datetime string
    pdf_path: Optional[str] = None
    markdown_path: Optional[str] = None
    has_assessment: bool = False
    assessment_score: Optional[float] = None  # 0.0 to 1.0 if taken


class EpisodeDetail(EpisodeSummary):
    """Full episode info including content."""

    markdown_content: Optional[str] = None
    show_notes: Optional[str] = None
    sources_used: List[str] = []


class EpisodeGenerateRequest(BaseModel):
    """Request to generate a new episode."""

    topic_id: Optional[str] = None  # None = auto-select
    depth: Optional[str] = None  # None = auto-select
    skip_pdf: bool = False
    skip_assessment: bool = False
    skip_sources: bool = False
    skip_push: bool = False
    use_paper: bool = False


class EpisodeGenerateResponse(BaseModel):
    """Response after generating an episode."""

    success: bool
    episode_num: int
    topic_name: str
    word_count: int
    pdf_path: Optional[str] = None
    assessment_questions: int = 0
    errors: List[str] = []
    cost_estimate: float = 0.0  # Estimated API cost for this episode


# ---------------------------------------------------------------------------
# 2. ASSESSMENT MODELS
# ---------------------------------------------------------------------------


class AssessmentQuestion(BaseModel):
    """A single quiz question."""

    id: int
    question_text: str
    question_type: str  # "multiple_choice", "short_answer", "code_challenge"
    options: Optional[List[str]] = None  # For multiple choice
    difficulty: str  # "easy", "medium", "hard"
    topic_tags: List[str] = []


class AssessmentQuestionWithAnswer(AssessmentQuestion):
    """Question with correct answer (for grading view)."""

    correct_answer: str
    explanation: str
    user_answer: Optional[str] = None
    is_correct: Optional[bool] = None


class AssessmentSubmission(BaseModel):
    """Submit an answer to a question."""

    assessment_id: int
    user_answer: str


class AssessmentResult(BaseModel):
    """Result after submitting an answer."""

    assessment_id: int
    is_correct: bool
    correct_answer: str
    explanation: str


class AssessmentSummary(BaseModel):
    """Summary of assessment for an episode."""

    episode_num: int
    topic_name: str
    total_questions: int
    answered: int
    correct: int
    score: Optional[float] = None  # 0.0 to 1.0
    questions: List[AssessmentQuestionWithAnswer] = []


# ---------------------------------------------------------------------------
# 3. SOURCE MODELS
# ---------------------------------------------------------------------------


class Source(BaseModel):
    """A content source in the registry."""

    id: str
    name: str
    url: str
    type: str  # "api" or "web"
    fetcher: str  # "generic", "arxiv_fetcher", etc.
    categories: List[str]
    quality: str  # "high", "medium", "mixed"
    enabled: bool


class SourceAddRequest(BaseModel):
    """Request to add a new source."""

    id: str
    name: str
    url: str
    categories: List[str] = ["all"]
    quality: str = "medium"
    # type and fetcher are auto-detected


class SourceToggleRequest(BaseModel):
    """Enable or disable a source."""

    enabled: bool


class SourceTestResult(BaseModel):
    """Result of testing a source."""

    source_id: str
    success: bool
    title: Optional[str] = None
    content_preview: Optional[str] = None  # First 200 chars
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# 4. ANALYTICS MODELS
# ---------------------------------------------------------------------------


class DailySnapshot(BaseModel):
    """Daily analytics snapshot."""

    date: str
    episodes_completed: int
    total_episodes: int  # 165
    completion_percentage: float
    streak_days: int
    avg_score_today: Optional[float] = None
    avg_score_overall: Optional[float] = None
    knowledge_coverage: float  # 0.0 to 1.0
    category_scores: dict  # { "linear_algebra": 0.85, ... }
    phase_progress: dict  # { "1": 0.33, "2": 0.0, ... }
    total_study_hours: float


class ProgressOverview(BaseModel):
    """High-level progress for dashboard."""

    episodes_completed: int
    total_episodes: int
    current_streak: int
    overall_score: Optional[float] = None
    current_phase: int
    current_topic: Optional[str] = None
    next_topic: Optional[str] = None
    knowledge_coverage: float
    categories: dict  # { category: { total, mastered, in_progress, avg_confidence } }


class PublicDashboardData(BaseModel):
    """Data for the public recruiter-facing dashboard."""

    last_updated: str
    episodes_completed: int
    total_episodes: int
    completion_percentage: float
    streak_days: int
    category_breakdown: dict
    score_trend: List[dict]  # [{ episode: 1, score: 0.85 }, ...]
    phase_progress: dict
    total_study_hours: float


# ---------------------------------------------------------------------------
# 5. PROFILE MODELS
# ---------------------------------------------------------------------------


class TopicNode(BaseModel):
    """A single topic in the knowledge graph."""

    id: str
    name: str
    confidence: float
    prerequisites: List[str]
    category: str
    phase: int
    episodes: List[int]
    has_code: bool = True
    has_math: bool = True


class KnowledgeGraphSummary(BaseModel):
    """Summary of the knowledge graph."""

    total_topics: int
    mastered: int  # confidence >= 0.9
    in_progress: int  # 0 < confidence < 0.9
    not_started: int  # confidence == 0.0
    unlocked: int  # prerequisites met
    locked: int  # prerequisites not met
    topics: List[TopicNode] = []


# ---------------------------------------------------------------------------
# 6. PIPELINE MODELS
# ---------------------------------------------------------------------------


class PipelineStatus(BaseModel):
    """Current status of the pipeline."""

    is_running: bool
    last_run: Optional[str] = None
    last_episode: Optional[int] = None
    next_scheduled: Optional[str] = None
    errors: List[str] = []


class PipelineRunRequest(BaseModel):
    """Request to trigger a pipeline run."""

    topic_id: Optional[str] = None
    skip_pdf: bool = False
    skip_assessment: bool = False
    skip_sources: bool = False
    skip_push: bool = False
