"""
Module 2: Curriculum Planner
Auto-selects the next topic using Claude Haiku based on the learner's
knowledge profile, prerequisite graph, and recent episode history.
"""

import json
import os

import yaml

from src.utils.claude_client import call_claude
from src.profile_manager import ProfileManager


PLANNER_PROMPT = """You are a curriculum planner for an AI learning system called Archon.
Given the learner's knowledge profile and recent episode history, select the next topic to study.

RULES:
- Only select topics whose ALL prerequisites have confidence >= 0.6
- Among unlocked topics, prefer the one with lowest confidence
- Vary categories when possible — don't pick 5 linear algebra topics in a row if calculus is also unlocked
- The output will be a ~15-page study document with math, diagrams, and code examples
- Consider the learner's overall progress and what would be most impactful to learn next

Respond in ONLY valid JSON (no markdown, no backticks, no preamble):
{
  "topic_id": "the_topic_id",
  "topic_name": "Human Readable Topic Name",
  "depth": "intro|intermediate|deep_dive|paper_review",
  "subtopics": ["subtopic 1", "subtopic 2", "subtopic 3"],
  "reasoning": "Brief explanation of why this topic was chosen"
}
"""

HAIKU_MODEL = "claude-haiku-4-5-20251001"


def _determine_depth(confidence):
    """Pick depth based on current confidence in a topic."""
    if confidence < 0.2:
        return "intro"
    elif confidence < 0.5:
        return "intermediate"
    elif confidence < 0.75:
        return "deep_dive"
    else:
        return "paper_review"


def _fallback_selection(unlocked, recent_categories):
    """Lowest-confidence unlocked topic, preferring a different category from recent."""
    # Try to find one outside recent categories first
    for topic in unlocked:
        if topic["category"] not in recent_categories:
            return topic
    # Otherwise just take the lowest confidence
    return unlocked[0]


def plan_next_episode(profile_path="data/profile.json"):
    """Use Claude Haiku to select the next episode topic."""
    pm = ProfileManager(profile_path)
    profile = pm.get_profile()

    unlocked = pm.get_unlocked_topics()
    if not unlocked:
        print("Curriculum complete! No unlocked topics remaining.")
        return None

    # Gather recent episode history
    all_episodes = []
    for topic in profile["knowledge_graph"]:
        for ep in topic.get("episode_history", []):
            all_episodes.append((ep, topic["id"], topic["name"], topic["category"]))
    all_episodes.sort(key=lambda x: x[0], reverse=True)
    recent = all_episodes[:7]
    recent_categories = [r[3] for r in recent]

    episodes_completed = profile.get("episodes_completed", 0)
    next_episode_num = episodes_completed + 1

    # Determine current phase from unlocked topics
    current_phase = unlocked[0].get("phase", 1)

    # Build user prompt
    unlocked_lines = []
    for t in unlocked:
        unlocked_lines.append(
            f"- {t['id']}: \"{t['name']}\" | confidence: {t['confidence']:.2f} | category: {t['category']}"
        )

    recent_lines = []
    for ep_num, tid, tname, cat in recent:
        recent_lines.append(f"- Episode {ep_num}: {tname} ({cat})")

    user_prompt = (
        f"Episodes completed: {episodes_completed}\n"
        f"Current phase: {current_phase}\n\n"
        f"Unlocked topics (prerequisites met, confidence < 0.9):\n"
        + "\n".join(unlocked_lines)
        + "\n\nLast episodes (most recent first):\n"
        + ("\n".join(recent_lines) if recent_lines else "- None yet")
    )

    # Call Claude Haiku
    response = call_claude(
        model=HAIKU_MODEL,
        system_prompt=PLANNER_PROMPT,
        user_prompt=user_prompt,
        max_tokens=512,
    )

    # Parse and validate
    selected = None
    if response:
        try:
            selected = json.loads(response)
        except json.JSONDecodeError:
            # Try extracting JSON from response if there's extra text
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    selected = json.loads(response[start:end])
                except json.JSONDecodeError:
                    pass

    # Validate selected topic exists in the knowledge graph
    valid_ids = {t["id"] for t in profile["knowledge_graph"]}
    unlocked_ids = {t["id"] for t in unlocked}

    if selected and selected.get("topic_id") in unlocked_ids:
        topic_id = selected["topic_id"]
        topic = pm.get_topic(topic_id)
    else:
        # Fallback: pick lowest-confidence unlocked topic with category variety
        topic = _fallback_selection(unlocked, recent_categories)
        topic_id = topic["id"]
        depth = _determine_depth(topic["confidence"])
        selected = {
            "topic_id": topic_id,
            "topic_name": topic["name"],
            "depth": depth,
            "subtopics": [],
            "reasoning": f"Fallback selection: lowest confidence unlocked topic ({topic['confidence']:.2f})",
        }

    result = {
        "topic_id": selected["topic_id"],
        "topic_name": selected.get("topic_name", topic["name"]),
        "depth": selected.get("depth", _determine_depth(topic["confidence"])),
        "subtopics": selected.get("subtopics", []),
        "reasoning": selected.get("reasoning", ""),
        "category": topic["category"],
        "phase": topic.get("phase", 1),
        "episode_num": next_episode_num,
    }

    print(f"\U0001F4DA Next Episode: #{result['episode_num']}")
    print(f"   Topic: {result['topic_name']}")
    print(f"   Depth: {result['depth']}")
    print(f"   Category: {result['category']}")
    print(f"   Reason: {result['reasoning']}")

    return result


def plan_specific_topic(topic_id, profile_path="data/profile.json"):
    """Plan a specific topic regardless of prerequisites (manual override)."""
    pm = ProfileManager(profile_path)
    profile = pm.get_profile()

    topic = pm.get_topic(topic_id)
    if topic is None:
        print(f"Topic '{topic_id}' not found in knowledge graph.")
        return None

    episodes_completed = profile.get("episodes_completed", 0)
    next_episode_num = episodes_completed + 1
    depth = _determine_depth(topic["confidence"])

    # Ask Haiku for subtopics and refined depth
    user_prompt = (
        f"The learner has requested to study this specific topic:\n"
        f"- ID: {topic['id']}\n"
        f"- Name: {topic['name']}\n"
        f"- Category: {topic['category']}\n"
        f"- Current confidence: {topic['confidence']:.2f}\n"
        f"- Suggested depth: {depth}\n\n"
        f"Generate subtopics and confirm or adjust the depth."
    )

    response = call_claude(
        model=HAIKU_MODEL,
        system_prompt=PLANNER_PROMPT,
        user_prompt=user_prompt,
        max_tokens=512,
    )

    subtopics = []
    reasoning = f"Manual override: learner requested {topic['name']}"

    if response:
        try:
            parsed = json.loads(response)
            subtopics = parsed.get("subtopics", [])
            depth = parsed.get("depth", depth)
            reasoning = parsed.get("reasoning", reasoning)
        except json.JSONDecodeError:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    parsed = json.loads(response[start:end])
                    subtopics = parsed.get("subtopics", [])
                    depth = parsed.get("depth", depth)
                    reasoning = parsed.get("reasoning", reasoning)
                except json.JSONDecodeError:
                    pass

    result = {
        "topic_id": topic["id"],
        "topic_name": topic["name"],
        "depth": depth,
        "subtopics": subtopics,
        "reasoning": reasoning,
        "category": topic["category"],
        "phase": topic.get("phase", 1),
        "episode_num": next_episode_num,
    }

    print(f"\U0001F4DA Next Episode: #{result['episode_num']}")
    print(f"   Topic: {result['topic_name']}")
    print(f"   Depth: {result['depth']}")
    print(f"   Category: {result['category']}")
    print(f"   Reason: {result['reasoning']}")

    return result


if __name__ == "__main__":
    pm = ProfileManager()
    print("=" * 60)
    print("Archon Curriculum Planner")
    print("=" * 60)
    print(f"\nProgress: {pm.get_summary()}")
    print(f"Unlocked topics: {len(pm.get_unlocked_topics())}")
    for t in pm.get_unlocked_topics():
        print(f"  - {t['name']} ({t['confidence']:.0%})")

    print("\n" + "-" * 60)
    print("AUTO-PLANNING next episode...")
    print("-" * 60)
    plan = plan_next_episode()
    if plan:
        print(f"\nFull plan: {json.dumps(plan, indent=2)}")
    else:
        print("\nNo plan generated.")

    print("\n" + "-" * 60)
    print("MANUAL OVERRIDE: gradient_descent")
    print("-" * 60)
    specific = plan_specific_topic("gradient_descent")
    if specific:
        print(f"\nFull plan: {json.dumps(specific, indent=2)}")
    else:
        print("\nNo plan generated.")
