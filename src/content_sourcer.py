"""
Module 3A: Content Sourcer
Orchestrates content fetching for each episode, combining curated and
registry-based sources into a single source bundle for downstream generation.
"""

import json
import os
import hashlib
import datetime

import yaml

from src.utils.source_fetchers import fetch_for_topic, fetch_arxiv, fetch_semantic_scholar, fetch_generic
from src.utils.claude_client import call_claude
from src.utils.database import ArchonDB


MAX_BUNDLE_CHARS = 15_000


def _log_source_fetch(db, episode_id, source_id, url, title, content_hash):
    """Insert a row into source_fetches (the table exists but ArchonDB has no wrapper yet)."""
    cursor = db.conn.cursor()
    cursor.execute(
        """
        INSERT INTO source_fetches (episode_id, source_id, url, title, content_hash)
        VALUES (?, ?, ?, ?, ?)
        """,
        (episode_id, source_id, url, title, content_hash),
    )
    db.conn.commit()


def source_content(topic_name, topic_id, depth, category, episode_num):
    """Fetch content from the source registry and log every fetch to the DB.

    Returns a formatted source bundle string.
    """
    items = fetch_for_topic(topic_name, category)

    # Prioritise by depth
    if depth in ("intro", "intermediate"):
        items.sort(key=lambda x: 0 if x.get("content_type") in ("blog", "discussion") else 1)
    elif depth in ("deep_dive", "paper_review"):
        items.sort(key=lambda x: 0 if x.get("content_type") == "paper" else 1)

    # Log every fetched item
    db = ArchonDB()
    for item in items:
        content_hash = hashlib.md5(item.get("content", "").encode()).hexdigest()
        _log_source_fetch(
            db,
            episode_id=episode_num,
            source_id=item.get("source_id", "unknown"),
            url=item.get("url", ""),
            title=item.get("title", ""),
            content_hash=content_hash,
        )
    db.close()

    # Build the bundle string
    bundle = f"## Source Material for: {topic_name}\n\n"
    num_sources = 0
    for item in items:
        entry = (
            f"### From: {item.get('source_name', 'Unknown')}\n"
            f"{item.get('title', '')}\n"
            f"{item.get('content', '')}\n\n---\n\n"
        )
        if len(bundle) + len(entry) > MAX_BUNDLE_CHARS:
            break
        bundle += entry
        num_sources += 1

    bundle = bundle[:MAX_BUNDLE_CHARS]
    print(f"Source bundle prepared: {num_sources} sources, {len(bundle)} chars")
    return bundle


def get_curated_content(topic_id):
    """Return curated source content for a topic, or None if none exists."""
    curated_path = os.path.join(
        os.path.dirname(__file__), "..", "config", "curated_sources.json"
    )
    curated_path = os.path.normpath(curated_path)

    if not os.path.exists(curated_path):
        with open(curated_path, "w", encoding="utf-8") as f:
            json.dump({"topics": {}}, f, indent=2)
        return None

    with open(curated_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    topic_entry = data.get("topics", {}).get(topic_id)
    if not topic_entry:
        return None

    urls = topic_entry if isinstance(topic_entry, list) else topic_entry.get("urls", [])
    if not urls:
        return None

    curated_items = []
    for url in urls:
        result = fetch_generic(url)
        if result:
            curated_items.append(result)

    if not curated_items:
        return None

    bundle = "## Curated Sources\n\n"
    for item in curated_items:
        bundle += (
            f"### From: Curated\n"
            f"{item.get('title', '')}\n"
            f"{item.get('content', '')}\n\n---\n\n"
        )

    print(f"Curated content: {len(curated_items)} sources, {len(bundle)} chars")
    return bundle


def build_source_bundle(topic_name, topic_id, depth, category, episode_num):
    """Combine curated (priority) and registry-fetched content into a final bundle."""
    curated = get_curated_content(topic_id) or ""
    fetched = source_content(topic_name, topic_id, depth, category, episode_num)

    if curated:
        bundle = curated + "\n" + fetched
    else:
        bundle = fetched

    bundle = bundle[:MAX_BUNDLE_CHARS]
    return bundle


if __name__ == "__main__":
    print("=" * 60)
    print("Testing content sourcer")
    print("=" * 60)

    bundle = build_source_bundle(
        topic_name="Scalars, Vectors, and Vector Spaces",
        topic_id="vectors_and_spaces",
        depth="intro",
        category="linear_algebra",
        episode_num=1,
    )

    print("\n--- Bundle Preview (first 2000 chars) ---")
    print(bundle[:2000])
    print(f"\n--- Total bundle length: {len(bundle)} chars ---")
