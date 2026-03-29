"""
Service layer bridging FastAPI routes with existing Archon pipeline modules.

This module does NOT duplicate logic — it imports and calls existing modules,
wrapping them in a structured API-friendly interface.
"""

import glob
import json
import os
from datetime import datetime

from src.profile_manager import ProfileManager
from src.curriculum_planner import plan_next_episode, plan_specific_topic
from src.content_sourcer import build_source_bundle
from src.document_writer import generate_document
from src.pdf_renderer import render_pdf
from src.assessment_generator import generate_assessment
from src.analytics_engine import AnalyticsEngine
from src.show_notes_generator import generate_show_notes
from src.github_uploader import git_push_episode, get_streak_count
from src.utils.database import ArchonDB
from src.utils.source_fetchers import SourceRegistry
from src.paper_engine import PaperEngine

# Project root (two levels up from backend/services/)
PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))


class EpisodeService:
    """Central service for all episode-related operations."""

    def __init__(self):
        self.db = ArchonDB()
        self.profile_manager = ProfileManager()
        self.analytics = AnalyticsEngine()
        self.source_registry = SourceRegistry()
        self.paper_engine = PaperEngine()
        self._pipeline_running = False
        self._pipeline_errors = []
        self._last_run = None
        self._last_episode = None

    # ------------------------------------------------------------------
    # Episodes
    # ------------------------------------------------------------------

    def get_all_episodes(self) -> list:
        """Return summary dicts for every episode in the database."""
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM episodes ORDER BY id")
        episodes = []

        for row in cursor.fetchall():
            ep = dict(row)
            episode_id = ep["id"]

            # Check for assessment existence and completion
            cursor2 = self.db.conn.cursor()
            cursor2.execute(
                "SELECT COUNT(*) as total, "
                "SUM(CASE WHEN answered_at IS NOT NULL THEN 1 ELSE 0 END) as answered, "
                "SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct "
                "FROM assessments WHERE episode_id = ?",
                (episode_id,),
            )
            stats = dict(cursor2.fetchone())
            total = stats["total"] or 0
            answered = stats["answered"] or 0
            correct = stats["correct"] or 0

            has_assessment = total > 0
            score = round(correct / answered, 2) if answered > 0 else None

            # Derive category from the knowledge graph
            topic = self.profile_manager.get_topic(ep["topic_id"])
            category = topic["category"] if topic else "unknown"

            episodes.append({
                "id": episode_id,
                "episode_num": episode_id,
                "topic_id": ep["topic_id"],
                "topic_name": ep["topic_name"],
                "depth": ep["depth"],
                "phase": ep["phase"],
                "category": category,
                "generated_at": ep["generated_at"],
                "pdf_path": ep["pdf_path"] or None,
                "markdown_path": ep["markdown_path"] or None,
                "has_assessment": has_assessment,
                "assessment_score": score,
            })

        return episodes

    def get_episode(self, episode_num: int) -> dict:
        """Return full episode detail including markdown content and show notes."""
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM episodes WHERE id = ?", (episode_num,))
        row = cursor.fetchone()
        if row is None:
            return None

        ep = dict(row)
        topic = self.profile_manager.get_topic(ep["topic_id"])
        category = topic["category"] if topic else "unknown"

        # Read markdown content
        markdown_content = None
        md_path = ep.get("markdown_path")
        if md_path:
            full_md_path = os.path.join(PROJECT_ROOT, md_path) if not os.path.isabs(md_path) else md_path
            if os.path.exists(full_md_path):
                with open(full_md_path, "r", encoding="utf-8") as f:
                    markdown_content = f.read()

        # Read show notes
        show_notes = None
        sn_path = ep.get("show_notes_path")
        if sn_path:
            full_sn_path = os.path.join(PROJECT_ROOT, sn_path) if not os.path.isabs(sn_path) else sn_path
            if os.path.exists(full_sn_path):
                with open(full_sn_path, "r", encoding="utf-8") as f:
                    show_notes = f.read()
        else:
            # Try default location
            default_sn = os.path.join(PROJECT_ROOT, "output", "show_notes", f"episode_{episode_num:03d}_notes.md")
            if os.path.exists(default_sn):
                with open(default_sn, "r", encoding="utf-8") as f:
                    show_notes = f.read()

        return {
            "id": ep["id"],
            "episode_num": ep["id"],
            "topic_id": ep["topic_id"],
            "topic_name": ep["topic_name"],
            "depth": ep["depth"],
            "phase": ep["phase"],
            "category": category,
            "generated_at": ep["generated_at"],
            "pdf_path": ep["pdf_path"] or None,
            "markdown_path": ep["markdown_path"] or None,
            "markdown_content": markdown_content,
            "show_notes": show_notes,
            "sources_used": [],
        }

    def get_episode_pdf_path(self, episode_num: int) -> str:
        """Find and return the PDF file path for a given episode number."""
        pdf_dir = os.path.join(PROJECT_ROOT, "output", "pdfs")
        pattern = os.path.join(pdf_dir, f"episode_{episode_num:03d}*")
        matches = glob.glob(pattern)
        if matches:
            return matches[0]
        return None

    # ------------------------------------------------------------------
    # Pipeline / Generation
    # ------------------------------------------------------------------

    def generate_episode(
        self,
        topic_id=None,
        skip_pdf=False,
        skip_assessment=False,
        skip_sources=False,
        skip_push=False,
        use_paper=False,
    ) -> dict:
        """Run the full Archon pipeline, returning structured results."""
        self._pipeline_running = True
        self._pipeline_errors = []
        result = {
            "success": False,
            "episode_num": 0,
            "topic_name": "",
            "word_count": 0,
            "pdf_path": None,
            "assessment_questions": 0,
            "errors": [],
            "cost_estimate": 0.0,
        }

        # ── a. Profile ────────────────────────────────────────────────
        try:
            pm = ProfileManager()
            pm.apply_time_decay()
            pm.save()
        except Exception as e:
            self._pipeline_errors.append(f"Profile: {e}")
            self._pipeline_running = False
            result["errors"] = list(self._pipeline_errors)
            return result

        # ── b. Plan ───────────────────────────────────────────────────
        plan = None
        try:
            if topic_id:
                plan = plan_specific_topic(topic_id)
            else:
                plan = plan_next_episode()
        except Exception as e:
            self._pipeline_errors.append(f"Planning: {e}")

        if plan is None:
            self._pipeline_errors.append("Planning: no plan generated")
            self._pipeline_running = False
            result["errors"] = list(self._pipeline_errors)
            return result

        t_id = plan["topic_id"]
        topic_name = plan["topic_name"]
        depth = plan["depth"]
        subtopics = plan["subtopics"]
        category = plan["category"]
        phase = plan.get("phase", 1)
        episode_num = plan["episode_num"]

        result["episode_num"] = episode_num
        result["topic_name"] = topic_name

        # ── c. Sources ────────────────────────────────────────────────
        source_material = ""
        try:
            if skip_sources:
                source_material = (
                    f"Cover {topic_name} thoroughly for an AI/ML learner. "
                    f"Depth: {depth}. Subtopics: {', '.join(subtopics) if subtopics else topic_name}."
                )
            elif use_paper or depth == "paper_review":
                paper_result = self.paper_engine.process_paper(topic_name, learner_level="beginner")
                if paper_result and paper_result.get("analysis"):
                    source_material = paper_result["analysis"]
                    if paper_result.get("translated_explanation"):
                        source_material += "\n\n" + paper_result["translated_explanation"]
                    result["cost_estimate"] += 0.15  # Paper engine uses Opus
                else:
                    source_material = build_source_bundle(topic_name, t_id, depth, category, episode_num)
            else:
                source_material = build_source_bundle(topic_name, t_id, depth, category, episode_num)
        except Exception as e:
            self._pipeline_errors.append(f"Sources: {e}")
            source_material = f"Cover {topic_name} thoroughly for an AI/ML learner."

        # ── d. Document ───────────────────────────────────────────────
        markdown = None
        try:
            profile = pm.get_profile()
            graph = profile["knowledge_graph"]
            completed = [t for t in graph if t.get("episode_history")]
            yesterday_topic = completed[-1]["name"] if completed else (
                "None — this is your first episode." if episode_num == 1 else "Previous episode"
            )

            unlocked = pm.get_unlocked_topics()
            tomorrow_candidates = [t for t in unlocked if t["id"] != t_id]
            tomorrow_topic = (
                tomorrow_candidates[0]["name"]
                if tomorrow_candidates
                else "To be determined based on your progress."
            )

            markdown = generate_document(
                topic_name=topic_name,
                depth=depth,
                subtopics=subtopics if subtopics else [topic_name],
                source_material=source_material,
                profile_summary=pm.get_summary(),
                yesterday_topic=yesterday_topic,
                tomorrow_topic=tomorrow_topic,
            )
            result["cost_estimate"] += 0.10  # Document writer uses Opus
        except Exception as e:
            self._pipeline_errors.append(f"Document: {e}")

        if not markdown:
            self._pipeline_errors.append("Document: no content generated")
            self._pipeline_running = False
            result["errors"] = list(self._pipeline_errors)
            return result

        # Save markdown
        md_dir = os.path.join(PROJECT_ROOT, "output", "markdown")
        os.makedirs(md_dir, exist_ok=True)
        md_filename = f"episode_{episode_num:03d}_{t_id}.md"
        md_path = os.path.join(md_dir, md_filename)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown)

        result["word_count"] = len(markdown.split())

        # ── e. PDF ────────────────────────────────────────────────────
        pdf_path = None
        if not skip_pdf:
            try:
                pdf_path = render_pdf(
                    markdown_content=markdown,
                    episode_num=episode_num,
                    topic_name=topic_name,
                    phase=phase,
                    category=category,
                )
                result["pdf_path"] = pdf_path
            except Exception as e:
                self._pipeline_errors.append(f"PDF: {e}")

        # ── f. Assessment ─────────────────────────────────────────────
        questions = None
        if not skip_assessment:
            try:
                questions = generate_assessment(
                    episode_markdown=markdown,
                    episode_num=episode_num,
                    topic_name=topic_name,
                )
                if questions:
                    result["assessment_questions"] = len(questions)
                    result["cost_estimate"] += 0.01  # Assessment uses Haiku
            except Exception as e:
                self._pipeline_errors.append(f"Assessment: {e}")

        # ── g. Show notes ─────────────────────────────────────────────
        try:
            generate_show_notes(
                episode_markdown=markdown,
                episode_num=episode_num,
                topic_name=topic_name,
                phase=f"Phase {phase}" if isinstance(phase, int) else str(phase),
                category=category,
            )
            result["cost_estimate"] += 0.01  # Show notes uses Haiku
        except Exception as e:
            self._pipeline_errors.append(f"Show notes: {e}")

        # ── h. Update profile & database ──────────────────────────────
        try:
            pm.mark_episode_completed(t_id, episode_num)
        except Exception as e:
            self._pipeline_errors.append(f"Profile update: {e}")

        try:
            db = ArchonDB()
            db.log_episode(
                topic_id=t_id,
                topic_name=topic_name,
                depth=depth,
                phase=phase,
                pdf_path=pdf_path or "",
                markdown_path=md_path,
            )
            db.close()
        except Exception as e:
            self._pipeline_errors.append(f"Database: {e}")

        # ── i. Analytics ──────────────────────────────────────────────
        try:
            analytics = AnalyticsEngine()
            analytics.compute_daily_snapshot()
        except Exception as e:
            self._pipeline_errors.append(f"Analytics: {e}")

        # ── j. GitHub ─────────────────────────────────────────────────
        if not skip_push:
            try:
                push_result = git_push_episode(episode_num, topic_name)
                if not push_result["success"]:
                    self._pipeline_errors.append("GitHub: push failed")
            except Exception as e:
                self._pipeline_errors.append(f"GitHub: {e}")

        # ── Done ──────────────────────────────────────────────────────
        self._pipeline_running = False
        self._last_run = datetime.now().isoformat()
        self._last_episode = episode_num
        result["success"] = True
        result["errors"] = list(self._pipeline_errors)
        return result

    # ------------------------------------------------------------------
    # Assessments
    # ------------------------------------------------------------------

    def get_assessment(self, episode_num: int) -> dict:
        """Load assessment questions for an episode, including submission status."""
        # Find the episode in the database
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT id, topic_name FROM episodes WHERE id = ?", (episode_num,))
        ep_row = cursor.fetchone()
        if ep_row is None:
            return None

        episode_id = ep_row["id"]
        topic_name = ep_row["topic_name"]

        # Get all assessment rows for this episode
        scores = self.db.get_episode_scores(episode_id)
        total = len(scores)
        answered = sum(1 for s in scores if s.get("answered_at") is not None)
        correct = sum(1 for s in scores if s.get("is_correct"))
        score = round(correct / answered, 2) if answered > 0 else None

        questions = []
        for s in scores:
            tags = s.get("topic_tags", "")
            questions.append({
                "id": s["id"],
                "question_text": s["question_text"],
                "question_type": s["question_type"],
                "correct_answer": s["correct_answer"],
                "explanation": "",
                "difficulty": s["difficulty"],
                "topic_tags": tags.split(",") if tags else [],
                "user_answer": s.get("user_answer"),
                "is_correct": s.get("is_correct"),
                "options": None,
            })

        return {
            "episode_num": episode_num,
            "topic_name": topic_name,
            "total_questions": total,
            "answered": answered,
            "correct": correct,
            "score": score,
            "questions": questions,
        }

    def submit_assessment_answer(self, assessment_id: int, user_answer: str) -> dict:
        """Grade a submitted answer and update the database."""
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM assessments WHERE id = ?", (assessment_id,))
        row = cursor.fetchone()
        if row is None:
            return None

        q = dict(row)
        correct_answer = q["correct_answer"]
        question_type = q["question_type"]

        # Grade: for multiple choice, check letter match; otherwise mark as self-graded
        if question_type == "multiple_choice":
            is_correct = user_answer.strip().upper() == correct_answer.strip().upper()
        else:
            # For short answer / code / conceptual, exact match or self-graded
            is_correct = user_answer.strip().lower() == correct_answer.strip().lower()

        self.db.submit_answer(assessment_id, user_answer, is_correct)

        # Update profile confidence based on running episode score
        episode_id = q["episode_id"]
        scores = self.db.get_episode_scores(episode_id)
        answered = [s for s in scores if s.get("answered_at") is not None]
        if answered:
            running_score = sum(1 for s in answered if s["is_correct"]) / len(answered)

            # Find the topic_id for this episode
            cursor.execute("SELECT topic_id FROM episodes WHERE id = ?", (episode_id,))
            ep_row = cursor.fetchone()
            if ep_row:
                try:
                    self.profile_manager.update_confidence_from_assessment(
                        ep_row["topic_id"], running_score
                    )
                except Exception:
                    pass  # Non-critical; don't fail the grading

        return {
            "assessment_id": assessment_id,
            "is_correct": is_correct,
            "correct_answer": correct_answer,
            "explanation": "",
        }

    # ------------------------------------------------------------------
    # Progress & Analytics
    # ------------------------------------------------------------------

    def get_progress_overview(self) -> dict:
        """Compute current progress from profile and database."""
        profile = self.profile_manager.get_profile()
        graph = profile["knowledge_graph"]
        stats = self.db.get_overall_stats()
        streak = get_streak_count()

        episodes_completed = profile.get("episodes_completed", 0)
        total_episodes = 165

        # Determine current phase: the highest phase with any active topic
        current_phase = 1
        for t in graph:
            if t["confidence"] > 0 and t["phase"] > current_phase:
                current_phase = t["phase"]

        # Next topic
        next_topic_obj = self.profile_manager.get_next_topic()
        next_topic = next_topic_obj["name"] if next_topic_obj else None

        # Current topic: most recently worked on
        completed_topics = [t for t in graph if t.get("episode_history")]
        current_topic = completed_topics[-1]["name"] if completed_topics else None

        # Knowledge coverage: topics with confidence > 0.6
        topics_above = sum(1 for t in graph if t["confidence"] > 0.6)
        coverage = round(topics_above / len(graph), 2) if graph else 0.0

        # Category breakdown
        categories = {}
        for t in graph:
            cat = t["category"]
            if cat not in categories:
                categories[cat] = {"total": 0, "mastered": 0, "in_progress": 0, "confidence_sum": 0.0}
            categories[cat]["total"] += 1
            categories[cat]["confidence_sum"] += t["confidence"]
            if t["confidence"] >= 0.9:
                categories[cat]["mastered"] += 1
            elif t["confidence"] > 0.0:
                categories[cat]["in_progress"] += 1
        cat_result = {
            cat: {
                "total": v["total"],
                "mastered": v["mastered"],
                "in_progress": v["in_progress"],
                "avg_confidence": round(v["confidence_sum"] / v["total"], 2),
            }
            for cat, v in categories.items()
        }

        return {
            "episodes_completed": episodes_completed,
            "total_episodes": total_episodes,
            "current_streak": streak,
            "overall_score": stats["avg_score"],
            "current_phase": current_phase,
            "current_topic": current_topic,
            "next_topic": next_topic,
            "knowledge_coverage": coverage,
            "categories": cat_result,
        }

    def get_public_dashboard_data(self) -> dict:
        """Generate the recruiter-facing dashboard data."""
        return self.analytics.generate_public_dashboard_data()

    def get_knowledge_graph(self) -> dict:
        """Return the full knowledge graph with summary stats."""
        profile = self.profile_manager.get_profile()
        graph = profile["knowledge_graph"]

        total = len(graph)
        mastered = sum(1 for t in graph if t["confidence"] >= 0.9)
        in_progress = sum(1 for t in graph if 0.0 < t["confidence"] < 0.9)
        not_started = sum(1 for t in graph if t["confidence"] == 0.0)

        # Determine unlocked/locked
        topics_by_id = {t["id"]: t for t in graph}
        unlocked = 0
        locked = 0
        for t in graph:
            prereqs_met = all(
                topics_by_id.get(p, {}).get("confidence", 0) >= 0.6
                for p in t.get("prerequisites", [])
            )
            if prereqs_met:
                unlocked += 1
            else:
                locked += 1

        topics = []
        for t in graph:
            topics.append({
                "id": t["id"],
                "name": t["name"],
                "confidence": t["confidence"],
                "prerequisites": t.get("prerequisites", []),
                "category": t["category"],
                "phase": t["phase"],
                "episodes": t.get("episode_history", []),
                "has_code": t.get("has_code", True),
                "has_math": t.get("has_math", True),
            })

        return {
            "total_topics": total,
            "mastered": mastered,
            "in_progress": in_progress,
            "not_started": not_started,
            "unlocked": unlocked,
            "locked": locked,
            "topics": topics,
        }

    # ------------------------------------------------------------------
    # Sources
    # ------------------------------------------------------------------

    def get_sources(self) -> list:
        """Return all sources from the registry."""
        return list(self.source_registry.sources.values())

    def add_source(self, source_dict: dict) -> bool:
        """Add a new source, auto-detecting fetcher type from URL."""
        url = source_dict.get("url", "")

        # Auto-detect type and fetcher
        if "arxiv.org" in url:
            source_dict.setdefault("type", "api")
            source_dict.setdefault("fetcher", "arxiv_fetcher")
        elif "semanticscholar.org" in url:
            source_dict.setdefault("type", "api")
            source_dict.setdefault("fetcher", "semantic_scholar_fetcher")
        elif "news.ycombinator.com" in url:
            source_dict.setdefault("type", "api")
            source_dict.setdefault("fetcher", "hn_fetcher")
        else:
            source_dict.setdefault("type", "web")
            source_dict.setdefault("fetcher", "generic")

        source_dict.setdefault("enabled", True)
        source_dict.setdefault("categories", ["all"])
        source_dict.setdefault("quality", "medium")

        return self.source_registry.add_source(source_dict)

    def toggle_source(self, source_id: str, enabled: bool) -> bool:
        """Enable or disable a source."""
        source = self.source_registry.get_source(source_id)
        if source is None:
            return False
        self.source_registry.toggle_source(source_id, enabled)
        return True

    def test_source(self, source_id: str) -> dict:
        """Fetch one piece of content from a source to verify it works."""
        from src.utils.source_fetchers import fetch_generic

        source = self.source_registry.get_source(source_id)
        if source is None:
            return {"source_id": source_id, "success": False, "error": "Source not found"}

        try:
            result = fetch_generic(source["url"], max_chars=500)
            if result:
                return {
                    "source_id": source_id,
                    "success": True,
                    "title": result.get("title"),
                    "content_preview": result.get("content", "")[:200],
                    "error": None,
                }
            return {"source_id": source_id, "success": False, "title": None, "content_preview": None, "error": "No content returned"}
        except Exception as e:
            return {"source_id": source_id, "success": False, "title": None, "content_preview": None, "error": str(e)}

    # ------------------------------------------------------------------
    # Pipeline status
    # ------------------------------------------------------------------

    def get_pipeline_status(self) -> dict:
        """Return current pipeline state."""
        return {
            "is_running": self._pipeline_running,
            "last_run": self._last_run,
            "last_episode": self._last_episode,
            "errors": list(self._pipeline_errors),
        }


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

episode_service = EpisodeService()


# ---------------------------------------------------------------------------
# CLI smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    svc = EpisodeService()

    print("=== Progress Overview ===")
    overview = svc.get_progress_overview()
    print(f"  Episodes: {overview['episodes_completed']}/{overview['total_episodes']}")
    print(f"  Streak:   {overview['current_streak']} days")
    print(f"  Phase:    {overview['current_phase']}")
    print(f"  Next:     {overview['next_topic']}")
    print(f"  Coverage: {overview['knowledge_coverage']:.0%}")
    print()

    print("=== Episodes ===")
    episodes = svc.get_all_episodes()
    if episodes:
        for ep in episodes:
            score_str = f" (score: {ep['assessment_score']:.0%})" if ep["assessment_score"] is not None else ""
            print(f"  #{ep['episode_num']}: {ep['topic_name']} [{ep['depth']}]{score_str}")
    else:
        print("  (none)")
    print()

    print("=== Sources ===")
    sources = svc.get_sources()
    print(f"  {len(sources)} sources registered")
    print()

    print("=== Pipeline Status ===")
    status = svc.get_pipeline_status()
    print(f"  Running:  {status['is_running']}")
    print(f"  Last run: {status['last_run'] or 'never'}")
    print(f"  Errors:   {len(status['errors'])}")
