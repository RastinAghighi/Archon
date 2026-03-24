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

    print(f"User prompt length: {len(user_prompt)} chars / {len(user_prompt.split())} words")
    print(f"System prompt length: {len(SYSTEM_PROMPT)} chars")
    print(f"API params: model={model}, max_tokens={max_tokens}, thinking={extended_thinking}, thinking_budget={thinking_budget}")

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
        print(f"Response length: {len(result)} chars / {word_count} words")

    return result


if __name__ == "__main__":
    source = """This is Episode 1 of the linear algebra foundations series. Cover vectors from absolute first principles,
assuming the learner has no formal linear algebra background beyond high school math.

KEY CONCEPTS TO COVER IN DEPTH:
1. SCALARS vs VECTORS: Define scalars as single real numbers. Define vectors as ordered lists of numbers.
   Explain notation: bold v for vectors, italic for scalars. Show column vector notation.
2. GEOMETRIC INTERPRETATION: Vectors as arrows in 2D and 3D space. Magnitude (length) and direction.
   The position vector vs. free vector distinction. Draw 2D coordinate systems with example vectors.
3. VECTOR ADDITION: Parallelogram rule, head-to-tail method. Algebraic definition component-wise.
   Show geometric diagrams for addition. Prove commutativity of vector addition geometrically.
4. SCALAR MULTIPLICATION: Scaling a vector changes its magnitude. Negative scalars reverse direction.
   Show geometric effect. Define algebraic rule: c*[v1, v2] = [c*v1, c*v2].
5. LINEAR INDEPENDENCE: A set of vectors is linearly independent if no vector can be written as a
   linear combination of the others. Give 2D and 3D examples. Show what linear dependence looks like
   geometrically (collinear vectors in 2D).
6. BASIS VECTORS: Standard basis e1, e2, e3. Any vector in R^n can be written as a linear combination
   of basis vectors. Explain span. Non-standard bases exist — any set of n linearly independent
   vectors in R^n forms a basis.
7. SPAN: The span of a set of vectors is all possible linear combinations. Span of one non-zero vector
   is a line. Span of two independent vectors in R^3 is a plane.
8. VECTOR SPACES: Define the 8 axioms (closure under addition, closure under scalar multiplication,
   associativity, commutativity, additive identity, additive inverse, multiplicative identity,
   distributivity). Give R^2 and R^3 as concrete examples. Mention that polynomials and functions
   can also form vector spaces.
9. SUBSPACES: A subset of a vector space that is itself a vector space. The zero vector test, closure
   under addition and scalar multiplication. Lines and planes through the origin are subspaces of R^3.
10. NUMPY OPERATIONS: np.array creation, vector addition with +, scalar multiplication with *,
    np.linalg.norm for magnitude, np.dot for dot product preview, stacking vectors, reshaping.
    Include complete runnable code examples with output comments.

WORKED EXAMPLES TO INCLUDE:
- Given vectors u=[1,2] and v=[3,-1], compute u+v, 2u, u-v, and show geometrically
- Show that {[1,0], [0,1]} is linearly independent but {[1,2], [2,4]} is not
- Verify that R^2 satisfies the vector space axioms with a specific example
- Complete NumPy session creating vectors, performing operations, computing norms

Include at least 3 DIAGRAM directives for visual elements (vector addition diagram, basis vectors diagram, etc.)."""

    markdown = generate_document(
        topic_name="Scalars, Vectors, and Vector Spaces",
        depth="intro",
        subtopics=[
            "What vectors really represent geometrically",
            "Vector addition and scalar multiplication",
            "Basis vectors and linear independence",
            "Vector spaces and their axioms",
            "Python NumPy vector operations",
        ],
        source_material=source,
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
