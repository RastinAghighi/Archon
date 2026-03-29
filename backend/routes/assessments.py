"""FastAPI router for assessment-related endpoints."""

from typing import List

from fastapi import APIRouter, HTTPException

from backend.schemas.models import (
    AssessmentQuestion,
    AssessmentResult,
    AssessmentSubmission,
    AssessmentSummary,
)
from backend.services.episode_service import episode_service

router = APIRouter(prefix="/api/assessments", tags=["Assessments"])


@router.get("/history")
def get_assessment_history():
    """Return assessment history across all episodes, sorted by episode_num descending."""
    episodes = episode_service.get_all_episodes()
    history = []
    for ep in episodes:
        if ep["has_assessment"]:
            history.append({
                "episode_num": ep["episode_num"],
                "topic_name": ep["topic_name"],
                "score": ep["assessment_score"],
                "date_taken": ep["generated_at"],
            })
    history.sort(key=lambda h: h["episode_num"], reverse=True)
    return history


@router.get("/{episode_num}", response_model=AssessmentSummary)
def get_assessment(episode_num: int):
    """Return assessment questions for an episode (without answers for quiz mode)."""
    assessment = episode_service.get_assessment(episode_num)
    if assessment is None:
        raise HTTPException(status_code=404, detail=f"No assessment found for episode {episode_num}")

    # Strip answers for quiz mode — return questions without correct_answer
    quiz_questions = []
    for q in assessment["questions"]:
        quiz_questions.append({
            "id": q["id"],
            "question_text": q["question_text"],
            "question_type": q["question_type"],
            "options": q["options"],
            "difficulty": q["difficulty"],
            "topic_tags": q["topic_tags"],
        })

    return {
        "episode_num": assessment["episode_num"],
        "topic_name": assessment["topic_name"],
        "total_questions": assessment["total_questions"],
        "answered": assessment["answered"],
        "correct": assessment["correct"],
        "score": assessment["score"],
        "questions": quiz_questions,
    }


@router.get("/{episode_num}/results", response_model=AssessmentSummary)
def get_assessment_results(episode_num: int):
    """Return assessment with answers, scores, and explanations (review mode)."""
    assessment = episode_service.get_assessment(episode_num)
    if assessment is None:
        raise HTTPException(status_code=404, detail=f"No assessment found for episode {episode_num}")
    return assessment


@router.post("/{episode_num}/submit", response_model=AssessmentResult)
def submit_assessment_answer(episode_num: int, submission: AssessmentSubmission):
    """Submit an answer to a question, grade it, and update profile confidence."""
    result = episode_service.submit_assessment_answer(
        assessment_id=submission.assessment_id,
        user_answer=submission.user_answer,
    )
    if result is None:
        raise HTTPException(status_code=404, detail=f"Assessment question {submission.assessment_id} not found")
    return result
