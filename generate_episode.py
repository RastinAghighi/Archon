import argparse
import json
import os
import sys
from datetime import datetime

from src.profile_manager import ProfileManager
from src.document_writer import generate_document
from src.pdf_renderer import render_pdf
from src.assessment_generator import generate_assessment, take_assessment
from src.analytics_engine import AnalyticsEngine
from src.utils.database import ArchonDB


def generate_episode(args):
    # ── Step 1: Load profile and select topic ──
    print("\n" + "=" * 60)
    print("ARCHON — Episode Generator")
    print("=" * 60)

    pm = ProfileManager()
    print(f"\n{pm.get_summary()}\n")

    if args.topic:
        # Find topic by ID or name
        topic = pm.get_topic(args.topic)
        if topic is None:
            # Try matching by name substring
            for t in pm.get_profile()["knowledge_graph"]:
                if args.topic.lower() in t["name"].lower():
                    topic = t
                    break
        if topic is None:
            print(f"Error: Topic '{args.topic}' not found in knowledge graph.")
            return
    else:
        topic = pm.get_next_topic()
        if topic is None:
            print("No unlocked topics available. All topics may be mastered!")
            return

    episode_num = args.episode if args.episode else pm.get_profile().get("episodes_completed", 0) + 1
    topic_id = topic["id"]
    topic_name = topic["name"]
    depth = topic.get("depth", "intro")
    phase = topic.get("phase", 1)
    category = topic.get("category", "unknown")

    print(f"Episode {episode_num}: {topic_name}")
    print(f"  Phase: {phase} | Category: {category} | Depth: {depth}")

    # Determine yesterday/tomorrow topics from context
    history = topic.get("episode_history", [])
    yesterday_topic = None
    if episode_num > 1:
        # Look at knowledge graph for previously completed topics
        graph = pm.get_profile()["knowledge_graph"]
        completed = [t for t in graph if t.get("episode_history")]
        if completed:
            yesterday_topic = completed[-1]["name"]

    if yesterday_topic is None:
        yesterday_topic = "None — this is your first episode." if episode_num == 1 else "Previous episode"

    # Peek at next unlocked topic for tomorrow preview
    unlocked = pm.get_unlocked_topics()
    tomorrow_candidates = [t for t in unlocked if t["id"] != topic_id]
    tomorrow_topic = tomorrow_candidates[0]["name"] if tomorrow_candidates else "To be determined based on your progress."

    # Build source material from topic info
    subtopics = topic.get("subtopics", [topic_name])
    source_material = topic.get("source_material", f"Cover {topic_name} thoroughly for an AI/ML learner.")

    # ── Step 2: Generate document ──
    print(f"\nGenerating study document...")
    profile_summary = pm.get_summary()

    try:
        markdown = generate_document(
            topic_name=topic_name,
            depth=depth,
            subtopics=subtopics,
            source_material=source_material,
            profile_summary=profile_summary,
            yesterday_topic=yesterday_topic,
            tomorrow_topic=tomorrow_topic,
        )
    except Exception as e:
        print(f"Error generating document: {e}")
        return

    if not markdown:
        print("Document generation failed — no content returned.")
        return

    # Save markdown
    md_dir = os.path.join(os.path.dirname(__file__), "output", "markdown")
    os.makedirs(md_dir, exist_ok=True)
    md_filename = f"episode_{episode_num:03d}_{topic_id}.md"
    md_path = os.path.join(md_dir, md_filename)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    word_count = len(markdown.split())
    print(f"Document generated ({word_count} words)")
    print(f"  Saved: output/markdown/{md_filename}")

    # ── Step 3: Render PDF ──
    pdf_path = None
    if not args.skip_pdf:
        print(f"\nRendering PDF...")
        try:
            pdf_path = render_pdf(
                markdown_content=markdown,
                episode_num=episode_num,
                topic_name=topic_name,
                phase=phase,
                category=category,
            )
            print(f"PDF rendered: {pdf_path}")
        except Exception as e:
            print(f"PDF rendering failed: {e}")
            print("  Continuing without PDF...")
    else:
        print("\nSkipping PDF rendering (--skip-pdf)")

    # ── Step 4: Generate assessment ──
    questions = None
    if not args.skip_assessment:
        print(f"\nGenerating assessment...")
        try:
            questions = generate_assessment(
                episode_markdown=markdown,
                episode_num=episode_num,
                topic_name=topic_name,
            )
            if questions:
                print(f"Assessment generated: {len(questions)} questions")
            else:
                print("Assessment generation returned no questions.")
        except Exception as e:
            print(f"Assessment generation failed: {e}")
            print("  Continuing without assessment...")
    else:
        print("\nSkipping assessment generation (--skip-assessment)")

    # ── Step 5: Update profile ──
    print(f"\nUpdating profile...")
    try:
        pm.mark_episode_completed(topic_id, episode_num)
        print("Profile updated")
    except Exception as e:
        print(f"Profile update failed: {e}")

    # ── Step 6: Log to database ──
    print(f"\nLogging to database...")
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
        print("Episode logged to database")
    except Exception as e:
        print(f"Database logging failed: {e}")

    # ── Step 7: Compute analytics ──
    print(f"\nComputing analytics...")
    try:
        engine = AnalyticsEngine()
        engine.print_summary()
    except Exception as e:
        print(f"Analytics computation failed: {e}")

    # ── Step 8: Take quiz (if requested) ──
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

    # ── Final summary ──
    print(f"\n{'=' * 60}")
    print(f"Episode {episode_num} complete!")
    print(f"{'=' * 60}")
    print(f"\n  Generated files:")
    print(f"    Markdown: output/markdown/{md_filename}")
    if pdf_path:
        print(f"    PDF:      {pdf_path}")
    if questions:
        print(f"    Quiz:     output/assessments/episode_{episode_num:03d}_assessment.json")
    print(f"\n  Open the PDF or feed it to ElevenReader.")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Archon — Generate a study episode from your knowledge graph"
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Override topic selection (topic ID or partial name match)",
    )
    parser.add_argument(
        "--episode",
        type=int,
        default=None,
        help="Specify episode number (default: auto-increment)",
    )
    parser.add_argument(
        "--skip-pdf",
        action="store_true",
        help="Skip PDF rendering",
    )
    parser.add_argument(
        "--skip-assessment",
        action="store_true",
        help="Skip assessment generation",
    )
    parser.add_argument(
        "--take-quiz",
        action="store_true",
        help="Immediately start the quiz after generation",
    )

    args = parser.parse_args()
    generate_episode(args)
