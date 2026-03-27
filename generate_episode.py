import argparse
import json
import os
from datetime import datetime

from src.profile_manager import ProfileManager
from src.curriculum_planner import plan_next_episode, plan_specific_topic
from src.content_sourcer import build_source_bundle
from src.source_ranker import select_best_sources
from src.paper_engine import PaperEngine
from src.document_writer import generate_document
from src.pdf_renderer import render_pdf
from src.assessment_generator import generate_assessment, take_assessment
from src.analytics_engine import AnalyticsEngine
from src.show_notes_generator import generate_show_notes
from src.github_uploader import git_push_episode
from src.utils.database import ArchonDB


def generate_episode(args):
    print("\n" + "=" * 60)
    print("ARCHON — Episode Generator (Full Pipeline)")
    print("=" * 60)

    # ── Step 1: Profile ──────────────────────────────────────────
    print("\n[Step 1/10] Loading profile...")
    try:
        pm = ProfileManager()
        pm.apply_time_decay()
        pm.save()
        print(f"\n{pm.get_summary()}\n")
    except Exception as e:
        print(f"Profile load failed: {e}")
        return

    # ── Step 2: Plan ─────────────────────────────────────────────
    print("[Step 2/10] Planning episode...")
    try:
        if args.topic:
            plan = plan_specific_topic(args.topic)
        else:
            plan = plan_next_episode()

        if plan is None:
            print("No plan generated — cannot continue.")
            return

        topic_id = plan["topic_id"]
        topic_name = plan["topic_name"]
        depth = plan["depth"]
        subtopics = plan["subtopics"]
        category = plan["category"]
        phase = plan.get("phase", 1)
        episode_num = args.episode if args.episode else plan["episode_num"]

        print(f"\n  Episode {episode_num}: {topic_name}")
        print(f"  Depth: {depth} | Phase: {phase} | Category: {category}")
        if subtopics:
            print(f"  Subtopics: {', '.join(subtopics)}")
        print(f"  Reasoning: {plan.get('reasoning', 'N/A')}")
    except Exception as e:
        print(f"Planning failed: {e}")
        return

    # ── Step 3: Source content ───────────────────────────────────
    print("\n[Step 3/10] Sourcing content...")
    source_material = ""
    try:
        if args.skip_sources:
            source_material = (
                f"Cover {topic_name} thoroughly for an AI/ML learner. "
                f"Depth: {depth}. Subtopics: {', '.join(subtopics) if subtopics else topic_name}."
            )
            print("  Skipped sourcing (--skip-sources). Using placeholder.")
        elif args.use_paper or depth == "paper_review":
            print("  Using Paper Engine...")
            engine = PaperEngine()
            paper_result = engine.process_paper(topic_name, learner_level="beginner")
            if paper_result and paper_result.get("analysis"):
                source_material = paper_result["analysis"]
                if paper_result.get("translated_explanation"):
                    source_material += "\n\n" + paper_result["translated_explanation"]
                print(f"  Paper processed: {paper_result.get('title', 'Unknown')}")
            else:
                print("  Paper engine returned no results. Falling back to content sourcer.")
                source_material = build_source_bundle(topic_name, topic_id, depth, category, episode_num)
        else:
            source_material = build_source_bundle(topic_name, topic_id, depth, category, episode_num)
            print(f"  Source bundle: {len(source_material)} chars")
    except Exception as e:
        print(f"  Source fetching failed: {e}")
        source_material = f"Cover {topic_name} thoroughly for an AI/ML learner."
        print("  Using fallback placeholder.")

    # ── Step 4: Generate document ────────────────────────────────
    print("\n[Step 4/10] Generating document...")
    markdown = None
    try:
        # Determine yesterday/tomorrow topics for document context
        profile = pm.get_profile()
        graph = profile["knowledge_graph"]
        completed = [t for t in graph if t.get("episode_history")]
        yesterday_topic = completed[-1]["name"] if completed else (
            "None — this is your first episode." if episode_num == 1 else "Previous episode"
        )

        unlocked = pm.get_unlocked_topics()
        tomorrow_candidates = [t for t in unlocked if t["id"] != topic_id]
        tomorrow_topic = tomorrow_candidates[0]["name"] if tomorrow_candidates else "To be determined based on your progress."

        markdown = generate_document(
            topic_name=topic_name,
            depth=depth,
            subtopics=subtopics if subtopics else [topic_name],
            source_material=source_material,
            profile_summary=pm.get_summary(),
            yesterday_topic=yesterday_topic,
            tomorrow_topic=tomorrow_topic,
        )
    except Exception as e:
        print(f"  Document generation failed: {e}")

    if not markdown:
        print("  No document content returned. Cannot continue.")
        return

    # Save markdown
    md_dir = os.path.join(os.path.dirname(__file__), "output", "markdown")
    os.makedirs(md_dir, exist_ok=True)
    md_filename = f"episode_{episode_num:03d}_{topic_id}.md"
    md_path = os.path.join(md_dir, md_filename)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    word_count = len(markdown.split())
    print(f"  Document generated: {word_count} words")
    print(f"  Saved: output/markdown/{md_filename}")

    # ── Step 5: Render PDF ───────────────────────────────────────
    pdf_path = None
    if not args.skip_pdf:
        print("\n[Step 5/10] Rendering PDF...")
        try:
            pdf_path = render_pdf(
                markdown_content=markdown,
                episode_num=episode_num,
                topic_name=topic_name,
                phase=phase,
                category=category,
            )
            print(f"  PDF rendered: {pdf_path}")
        except Exception as e:
            print(f"  PDF rendering failed: {e}")
    else:
        print("\n[Step 5/10] Skipping PDF (--skip-pdf)")

    # ── Step 6: Generate assessment ──────────────────────────────
    questions = None
    if not args.skip_assessment:
        print("\n[Step 6/10] Generating assessment...")
        try:
            questions = generate_assessment(
                episode_markdown=markdown,
                episode_num=episode_num,
                topic_name=topic_name,
            )
            if questions:
                print(f"  Assessment generated: {len(questions)} questions")
            else:
                print("  Assessment generation returned no questions.")
        except Exception as e:
            print(f"  Assessment generation failed: {e}")
    else:
        print("\n[Step 6/10] Skipping assessment (--skip-assessment)")

    # ── Step 7: Generate show notes ──────────────────────────────
    print("\n[Step 7/10] Generating show notes...")
    show_notes = None
    try:
        show_notes = generate_show_notes(
            episode_markdown=markdown,
            episode_num=episode_num,
            topic_name=topic_name,
            phase=f"Phase {phase}" if isinstance(phase, int) else str(phase),
            category=category,
        )
        if show_notes:
            print(f"  Show notes saved ({len(show_notes.split())} words)")
    except Exception as e:
        print(f"  Show notes generation failed: {e}")

    # ── Step 8: Update profile ───────────────────────────────────
    print("\n[Step 8/10] Updating profile...")
    try:
        pm.mark_episode_completed(topic_id, episode_num)
        print("  Profile updated")
    except Exception as e:
        print(f"  Profile update failed: {e}")

    try:
        db = ArchonDB()
        db.log_episode(
            topic_id=topic_id,
            topic_name=topic_name,
            depth=depth,
            phase=phase,
            pdf_path=pdf_path or "",
            markdown_path=md_path,
        )
        db.close()
        print("  Episode logged to database")
    except Exception as e:
        print(f"  Database logging failed: {e}")

    # ── Step 9: Compute analytics ────────────────────────────────
    print("\n[Step 9/10] Computing analytics...")
    try:
        analytics = AnalyticsEngine()
        analytics.print_summary()
    except Exception as e:
        print(f"  Analytics computation failed: {e}")

    # ── Step 10: Push to GitHub ──────────────────────────────────
    push_result = None
    if not args.skip_push:
        print("\n[Step 10/10] Pushing to GitHub...")
        try:
            push_result = git_push_episode(episode_num, topic_name)
            if push_result["success"]:
                print(f"  Commit: {push_result['commit_sha'][:8]}")
            else:
                print("  Push failed (see errors above)")
        except Exception as e:
            print(f"  GitHub push failed: {e}")
    else:
        print("\n[Step 10/10] Skipping GitHub push (--skip-push)")

    # ── Take quiz (if requested) ─────────────────────────────────
    if args.take_quiz and questions:
        print(f"\nStarting quiz...")
        score = take_assessment(episode_num)
        print(f"\nUpdating confidence based on score: {score:.0%}")
        try:
            pm.update_confidence_from_assessment(topic_id, score)
        except Exception as e:
            print(f"Confidence update failed: {e}")
    elif args.take_quiz and not questions:
        print("\nCannot take quiz — no assessment was generated.")

    # ── Final summary ────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print(f"  Episode {episode_num} complete: {topic_name}")
    print(f"{'=' * 60}")
    print(f"\n  Generated files:")
    print(f"    Markdown:   output/markdown/{md_filename}")
    if pdf_path:
        print(f"    PDF:        {pdf_path}")
    if questions:
        print(f"    Assessment: output/assessments/episode_{episode_num:03d}_assessment.json")
    if show_notes:
        print(f"    Show notes: output/show_notes/episode_{episode_num:03d}_notes.md")
    if push_result and push_result["success"]:
        print(f"    Git commit: {push_result['commit_sha'][:8]}")
    print(f"\n  Word count: {word_count}")
    print(f"  Open the PDF or feed it to ElevenReader.")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Archon — Generate a full study episode"
    )
    parser.add_argument(
        "--topic", type=str, default=None,
        help="Override topic selection (topic_id)",
    )
    parser.add_argument(
        "--episode", type=int, default=None,
        help="Specify episode number (default: auto-increment)",
    )
    parser.add_argument(
        "--skip-pdf", action="store_true",
        help="Skip PDF rendering",
    )
    parser.add_argument(
        "--skip-assessment", action="store_true",
        help="Skip assessment generation",
    )
    parser.add_argument(
        "--skip-push", action="store_true",
        help="Skip GitHub push",
    )
    parser.add_argument(
        "--skip-sources", action="store_true",
        help="Skip content fetching (use placeholder for offline testing)",
    )
    parser.add_argument(
        "--take-quiz", action="store_true",
        help="Immediately start the quiz after generation",
    )
    parser.add_argument(
        "--use-paper", action="store_true",
        help="Force the paper engine for this episode's sources",
    )

    args = parser.parse_args()
    generate_episode(args)
