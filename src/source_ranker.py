"""
Module 3C: Source Ranker
Ranks fetched sources by relevance using Claude Sonnet, selecting the
best materials for downstream content generation.
"""

import json
import yaml

from src.utils.claude_client import call_claude


RANKER_PROMPT = """You are a content curator for an AI learning system. Given a topic and a list of source materials, rank them by relevance and quality for teaching this topic to the specified learner level.

For each source, assign a relevance score from 0 to 10 and a brief justification.

Respond in ONLY valid JSON (no markdown, no backticks):
{
  "ranked_sources": [
    {
      "index": 0,
      "score": 9,
      "justification": "Directly covers the topic with clear examples"
    }
  ],
  "recommended_count": 3
}
"""


def rank_sources(topic_name, depth, learner_level, sources_list):
    """Rank sources by relevance using Claude Sonnet and return the top selections."""
    if not sources_list:
        return []

    if len(sources_list) <= 3:
        print(f"Only {len(sources_list)} sources — skipping ranking for '{topic_name}'")
        return [{"index": i, "score": 10, "justification": "Auto-included (≤3 sources)", "source": s}
                for i, s in enumerate(sources_list)]

    # Build user prompt with source previews
    source_descriptions = []
    for i, source in enumerate(sources_list):
        title = source.get("title", "Untitled")
        content_preview = source.get("content", "")[:500]
        source_descriptions.append(f"[{i}] Title: {title}\nPreview: {content_preview}")

    user_prompt = (
        f"Topic: {topic_name}\n"
        f"Depth: {depth}\n"
        f"Learner Level: {learner_level}\n\n"
        f"Sources to rank:\n\n" + "\n\n".join(source_descriptions)
    )

    response = call_claude(
        model="claude-sonnet-4-5-20250514",
        system_prompt=RANKER_PROMPT,
        user_prompt=user_prompt,
    )

    if not response:
        print("Ranking failed — returning all sources unranked")
        return [{"index": i, "score": 5, "justification": "Ranking unavailable", "source": s}
                for i, s in enumerate(sources_list)]

    try:
        result = json.loads(response)
    except json.JSONDecodeError:
        print("Failed to parse ranking response — returning all sources unranked")
        return [{"index": i, "score": 5, "justification": "Parse error", "source": s}
                for i, s in enumerate(sources_list)]

    ranked = result.get("ranked_sources", [])
    recommended_count = result.get("recommended_count", 5)

    # Attach original source data and sort by score descending
    for entry in ranked:
        idx = entry.get("index", 0)
        if 0 <= idx < len(sources_list):
            entry["source"] = sources_list[idx]

    ranked.sort(key=lambda x: x.get("score", 0), reverse=True)
    top = ranked[:recommended_count]

    print(f"Ranked {len(sources_list)} sources → selected top {len(top)} for '{topic_name}'")
    return top


def select_best_sources(topic_name, depth, learner_level, sources_list, max_sources=5):
    """Convenience wrapper: rank sources and return just the source dicts."""
    ranked = rank_sources(topic_name, depth, learner_level, sources_list)
    selected = [entry["source"] for entry in ranked[:max_sources] if "source" in entry]
    return selected


if __name__ == "__main__":
    test_sources = [
        {"title": "Understanding Gradient Descent Intuitively", "content": "Gradient descent is an optimization algorithm used to minimize a function by iteratively moving in the direction of steepest descent. It is the backbone of training neural networks and many ML models."},
        {"title": "Backpropagation and Gradient Flow", "content": "Backpropagation computes gradients layer by layer, allowing gradient descent to update weights efficiently in deep networks. The chain rule is applied recursively through the computation graph."},
        {"title": "Stochastic vs Batch Gradient Descent", "content": "SGD updates weights using a single sample, while batch gradient descent uses the full dataset. Mini-batch gradient descent is a practical compromise between variance and computation cost."},
        {"title": "History of Ancient Roman Architecture", "content": "The Romans developed concrete and perfected the arch, enabling construction of massive structures like the Colosseum and aqueducts across their empire."},
        {"title": "Introduction to Watercolor Painting", "content": "Watercolor painting uses water-soluble pigments and requires careful control of water-to-paint ratios. Techniques include wet-on-wet, dry brush, and glazing."},
    ]

    print("=" * 60)
    print("Testing source ranker")
    print("=" * 60)

    results = rank_sources(
        topic_name="gradient descent",
        depth="intro",
        learner_level="beginner with basic calculus knowledge",
        sources_list=test_sources,
    )

    print("\nRanking Results:")
    for entry in results:
        source = entry.get("source", {})
        print(f"  [{entry['index']}] Score: {entry['score']} — {source.get('title', '?')}")
        print(f"       {entry['justification']}")
