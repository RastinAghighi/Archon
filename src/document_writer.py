import os
import yaml

from src.utils.claude_client import call_claude


SYSTEM_PROMPT = """You are an expert AI/ML educator creating a study document for a second-year CS student who is learning AI from scratch to prepare for big tech co-op interviews. This student can code well in Python but has no formal ML training.

OUTPUT FORMAT:
- Write in structured Markdown with clear section headers using ##
- LaTeX formulas wrapped in $$ for display math and $ for inline math
- Describe diagrams in a structured format on their own line:
  DIAGRAM: {"type": "flowchart|architecture|plot|matrix", "description": "...", "components": [...]}
- Python code snippets in ```python blocks with full comments explaining every line
- Every mathematical concept must include: intuition FIRST, then formal definition, then worked example

QUALITY REQUIREMENTS:
- Never hand-wave. If there is math, derive it step by step.
- Every formula must have an English explanation of what each symbol means.
- Every code example must be complete and runnable (assume numpy and matplotlib available).
- Include at least 3 visual elements (formulas, diagrams, plots).
- Include at least 2 worked examples with step-by-step solutions.
- If this topic has a seminal paper, mention it and explain its key contribution.

DOCUMENT STRUCTURE (follow exactly):
## Yesterday's Recap
(1 page — summarize previous episode's key points. If this is Episode 1, write a welcome message instead.)

## Today's Topic: {topic_name}
(1-2 pages — what we're learning, why it matters, where it fits in the bigger picture)

## Core Concepts
(5-7 pages — main explanations with analogies, LaTeX formulas, diagrams, code)

## Worked Examples
(3-4 pages — step-by-step walkthroughs with code and visuals)

## Common Pitfalls
(1 page — what learners typically get wrong at this level)

## Summary & Key Takeaways
(1 page — bullet points of everything covered, key formulas reference)

## Tomorrow's Preview
(half page — what's coming next, how it connects, questions to think about)

TARGET LENGTH: approximately 6,000 words.
"""


def build_user_prompt(topic_name, depth, subtopics, source_material, profile_summary, yesterday_topic, tomorrow_topic):
    return f"""Write a complete study document for the following episode.

TOPIC: {topic_name}
DEPTH: {depth}
SUBTOPICS TO COVER: {subtopics}

LEARNER PROFILE:
{profile_summary}

YESTERDAY'S TOPIC: {yesterday_topic if yesterday_topic else "None — this is the first episode."}
TOMORROW'S TOPIC: {tomorrow_topic if tomorrow_topic else "None — this is the final episode in this phase."}

SOURCE MATERIAL / KEY REFERENCES:
{source_material if source_material else "No specific source material provided. Use your knowledge to create the best possible explanation."}

Write the full document now, following the document structure exactly. Target approximately 6,000 words."""


def generate_document(topic_name, depth, subtopics, source_material, profile_summary, yesterday_topic, tomorrow_topic):
    print(f"Generating document for: {topic_name}...")

    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "settings.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    model = config["models"]["document_writer"]
    max_tokens = config["document_writer"]["max_tokens"]
    extended_thinking = config["document_writer"]["extended_thinking"]
    thinking_budget = config["document_writer"]["thinking_budget"]

    user_prompt = build_user_prompt(
        topic_name, depth, subtopics, source_material,
        profile_summary, yesterday_topic, tomorrow_topic,
    )

    result = call_claude(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_tokens=max_tokens,
        extended_thinking=extended_thinking,
        thinking_budget=thinking_budget,
    )

    if result:
        word_count = len(result.split())
        print(f"Document generated: {word_count} words")

    return result


if __name__ == "__main__":
    markdown = generate_document(
        topic_name="Scalars, Vectors, and Vector Spaces",
        depth="intro",
        subtopics=[
            "What vectors really represent",
            "Vector addition and scalar multiplication",
            "Basis vectors and linear independence",
            "NumPy vector operations",
        ],
        source_material="This is the first episode. Cover vectors from first principles. Include geometric intuition, mathematical notation, and Python code with NumPy.",
        profile_summary="Second-year CS student, comfortable with Python, no linear algebra background beyond high school.",
        yesterday_topic="None — this is Episode 1",
        tomorrow_topic="Dot Products, Projections, and Cosine Similarity",
    )

    if markdown:
        output_dir = os.path.join(os.path.dirname(__file__), "..", "output", "markdown")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "episode_001.md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown)
        print(f"Saved to: {output_path}")
    else:
        print("Document generation failed.")
