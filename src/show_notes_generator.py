import json
import os
import yaml
from datetime import datetime

from src.utils.claude_client import call_claude


SHOW_NOTES_PROMPT = """You are generating concise show notes for an AI learning episode. Given the full study document, create a brief summary that someone can reference quickly.

Format your response as clean Markdown:
# Episode {episode_num}: {topic_name}
**Date**: {date}
**Phase**: {phase} | **Category**: {category}

## Key Concepts
- Bullet point summary of main concepts (5-8 bullets)

## Important Formulas
- List key formulas covered (if any)

## Code Snippets to Remember
- List the most important code patterns (2-3 max)

## Connections to ML
- How this topic connects to machine learning (2-3 bullets)

## What to Review Before Next Episode
- Key prerequisites for the next topic

Keep it concise — this is a quick reference, not a full document. Target ~500 words.
"""


def generate_show_notes(episode_markdown, episode_num, topic_name, phase, category, date_str=None):
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "settings.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    model = config["models"]["show_notes"]

    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    user_prompt = (
        f"Generate show notes for the following episode.\n\n"
        f"Episode Number: {episode_num}\n"
        f"Topic: {topic_name}\n"
        f"Phase: {phase}\n"
        f"Category: {category}\n"
        f"Date: {date_str}\n\n"
        f"Study Document:\n{episode_markdown[:8000]}"
    )

    result = call_claude(
        model=model,
        system_prompt=SHOW_NOTES_PROMPT,
        user_prompt=user_prompt,
        max_tokens=2000,
    )

    if not result:
        print("Show notes generation failed — no response from API.")
        return None

    output_dir = os.path.join(os.path.dirname(__file__), "..", "output", "show_notes")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"episode_{episode_num:03d}_notes.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"Show notes generated for Episode {episode_num}: {topic_name}")
    return result


if __name__ == "__main__":
    md_dir = os.path.join(os.path.dirname(__file__), "..", "output", "markdown")

    md_content = None
    latest_file = None
    if os.path.isdir(md_dir):
        md_files = sorted(f for f in os.listdir(md_dir) if f.endswith(".md"))
        if md_files:
            latest_file = md_files[-1]
            with open(os.path.join(md_dir, latest_file), "r", encoding="utf-8") as f:
                md_content = f.read()

    if not md_content:
        print("No episode markdown found in output/markdown/. Generate an episode first.")
    else:
        notes = generate_show_notes(
            episode_markdown=md_content,
            episode_num=1,
            topic_name="Scalars, Vectors, and Vector Spaces",
            phase="Phase 1: Mathematical Foundations",
            category="Linear Algebra",
        )
        if notes:
            print(f"\n{'='*60}")
            print(notes)
