import json
import os

from src.document_writer import generate_document

# --- Episode 1 Configuration (hardcoded for Week 1) ---

episode_num = 1
topic_id = "vectors_and_spaces"
topic_name = "Scalars, Vectors, and Vector Spaces"
depth = "intro"

subtopics = [
    "What vectors really represent (not just arrays)",
    "Vector addition, scalar multiplication",
    "Basis vectors and linear independence",
    "Python code: NumPy vector operations",
]

source_material = (
    "Vectors are the foundational language of machine learning. At their core, vectors represent "
    "magnitude and direction — but more importantly, they represent points in a space where each "
    "dimension encodes a feature. A 3D vector isn't just (x, y, z); it could be (height, weight, age) "
    "for a patient, or (r, g, b) for a pixel. This geometric intuition — that data lives in spaces — "
    "is the single most important idea in ML.\n\n"
    "A vector space is a set of vectors that you can add together and scale, and the result stays in "
    "the same space. This closure property is what makes linear algebra so powerful: any linear "
    "combination of vectors in a space produces another vector in that space. Basis vectors are the "
    "minimal set of vectors that can generate every other vector in the space through linear "
    "combinations. Understanding basis and linear independence tells you the true dimensionality of "
    "your data — which matters for everything from PCA to neural network layer sizing.\n\n"
    "Cover scalar vs vector vs matrix hierarchy, the formal definition of a vector space (with the "
    "8 axioms explained intuitively), standard basis vectors in R^n, and hands-on NumPy operations "
    "including vector creation, addition, scalar multiplication, and visualization with matplotlib. "
    "Connect every concept forward: vectors become rows in datasets, columns in weight matrices, "
    "and the hidden representations inside neural networks."
)

yesterday_topic = "None — welcome to Archon! This is your first episode."

tomorrow_topic = (
    "Dot Products, Projections, and Cosine Similarity — we'll learn how to measure "
    "angles and similarity between vectors, which is fundamental to how search engines "
    "and recommendation systems work."
)

# --- Load learner profile ---

profile_path = os.path.join(os.path.dirname(__file__), "data", "profile.json")
with open(profile_path, "r", encoding="utf-8") as f:
    profile = json.load(f)

learner = profile["learner"]
profile_summary = (
    f"Name: {learner['name']}. Background: {learner['background']}. "
    f"Level: {learner['level']}. Target: {learner['target']}. "
    f"Episodes completed so far: {profile['episodes_completed']}."
)

# --- Generate the document ---

result = generate_document(
    topic_name=topic_name,
    depth=depth,
    subtopics=subtopics,
    source_material=source_material,
    profile_summary=profile_summary,
    yesterday_topic=yesterday_topic,
    tomorrow_topic=tomorrow_topic,
)

if result:
    output_dir = os.path.join(os.path.dirname(__file__), "output", "markdown")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "episode_001_vectors_and_spaces.md")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)

    word_count = len(result.split())

    print(f"\n\u2713 Episode 1 generated successfully")
    print(f"  Topic: {topic_name}")
    print(f"  Output: output/markdown/episode_001_vectors_and_spaces.md")
    print(f"  Word count: {word_count}")
    print()
    print("Next step: Read the document and verify quality.")

    # --- Update profile ---
    for topic in profile["knowledge_graph"]:
        if topic["id"] == topic_id:
            topic["confidence"] = 0.3
            break

    profile["episodes_completed"] = 1

    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)
        f.write("\n")
else:
    print("Document generation failed.")
