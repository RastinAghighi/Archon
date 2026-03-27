"""
Source fetchers for Archon content pipeline.
Handles fetching content from academic APIs, blogs, news, and community sources.
"""

import json
import time
from pathlib import Path

import requests
import trafilatura
from bs4 import BeautifulSoup


# ---------------------------------------------------------------------------
# SourceRegistry
# ---------------------------------------------------------------------------

class SourceRegistry:
    """Loads and manages the source registry from config/sources.json."""

    def __init__(self, config_path="config/sources.json"):
        self.config_path = Path(config_path)
        with open(self.config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.sources = {s["id"]: s for s in data["sources"]}

    def get_enabled_sources(self, category=None):
        """Return enabled sources, optionally filtered by category."""
        results = [s for s in self.sources.values() if s["enabled"]]
        if category:
            results = [
                s for s in results
                if category in s["categories"] or "all" in s["categories"]
            ]
        return results

    def get_source(self, source_id):
        """Return a specific source by id."""
        return self.sources.get(source_id)

    def add_source(self, source_dict):
        """Add a new source. Returns True if added, False if id exists."""
        sid = source_dict.get("id")
        if sid in self.sources:
            return False
        self.sources[sid] = source_dict
        self._save()
        return True

    def toggle_source(self, source_id, enabled):
        """Enable or disable a source."""
        if source_id in self.sources:
            self.sources[source_id]["enabled"] = enabled
            self._save()

    def _save(self):
        data = {"sources": list(self.sources.values())}
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Generic web fetcher
# ---------------------------------------------------------------------------

def fetch_generic(url, max_chars=5000):
    """Extract clean text from a web URL using trafilatura, with BS4 fallback."""
    try:
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (compatible; Archon/1.0)"
        })
        resp.raise_for_status()
        html = resp.text

        # Try trafilatura first
        text = trafilatura.extract(html, include_comments=False, include_tables=False)

        title = None
        soup = BeautifulSoup(html, "html.parser")
        tag = soup.find("title")
        if tag:
            title = tag.get_text(strip=True)

        # Fallback to BeautifulSoup if trafilatura returns nothing
        if not text:
            for el in soup(["script", "style", "nav", "footer", "header"]):
                el.decompose()
            text = soup.get_text(separator="\n", strip=True)

        if not text:
            return None

        text = text[:max_chars]
        title = title or url

        print(f"Fetched: {title} ({len(text)} chars)")
        return {
            "url": url,
            "title": title,
            "content": text,
            "source_type": "web",
        }
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


# ---------------------------------------------------------------------------
# arXiv fetcher
# ---------------------------------------------------------------------------

def fetch_arxiv(query, max_results=5):
    """Search arXiv for papers matching the query."""
    try:
        import arxiv

        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )

        results = []
        for paper in client.results(search):
            results.append({
                "title": paper.title,
                "authors": [a.name for a in paper.authors],
                "abstract": paper.summary,
                "published": paper.published.isoformat(),
                "pdf_url": paper.pdf_url,
                "arxiv_id": paper.entry_id.split("/")[-1],
            })

        print(f"arXiv: Found {len(results)} papers for '{query}'")
        return results
    except Exception as e:
        print(f"arXiv error: {e}")
        return []


# ---------------------------------------------------------------------------
# Semantic Scholar fetcher
# ---------------------------------------------------------------------------

def fetch_semantic_scholar(query, max_results=5):
    """Search Semantic Scholar for papers."""
    try:
        time.sleep(1)  # rate-limit courtesy
        resp = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            params={
                "query": query,
                "limit": max_results,
                "fields": "title,abstract,authors,citationCount,year,url",
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        results = []
        for paper in data.get("data", []):
            results.append({
                "title": paper.get("title", ""),
                "abstract": paper.get("abstract", ""),
                "authors": [a.get("name", "") for a in (paper.get("authors") or [])],
                "citation_count": paper.get("citationCount", 0),
                "year": paper.get("year"),
                "url": paper.get("url", ""),
            })

        print(f"Semantic Scholar: Found {len(results)} papers for '{query}'")
        return results
    except Exception as e:
        print(f"Semantic Scholar error: {e}")
        return []


# ---------------------------------------------------------------------------
# Hacker News fetcher
# ---------------------------------------------------------------------------

def fetch_hacker_news(query=None, max_results=10):
    """Search Hacker News via the Algolia API."""
    try:
        search_query = query or "machine learning AI"
        resp = requests.get(
            "https://hn.algolia.com/api/v1/search",
            params={
                "query": search_query,
                "tags": "story",
                "hitsPerPage": max_results,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        results = []
        for hit in data.get("hits", []):
            results.append({
                "title": hit.get("title", ""),
                "url": hit.get("url", ""),
                "points": hit.get("points", 0),
                "num_comments": hit.get("num_comments", 0),
                "created_at": hit.get("created_at", ""),
            })

        print(f"HN: Found {len(results)} stories")
        return results
    except Exception as e:
        print(f"Hacker News error: {e}")
        return []


# ---------------------------------------------------------------------------
# Main pipeline entry point
# ---------------------------------------------------------------------------

FETCHER_MAP = {
    "arxiv_fetcher": ("arxiv", fetch_arxiv, "paper"),
    "semantic_scholar_fetcher": ("semantic_scholar", fetch_semantic_scholar, "paper"),
    "hn_fetcher": ("hacker_news", fetch_hacker_news, "discussion"),
    "github_fetcher": (None, None, None),  # placeholder for future implementation
}


def fetch_for_topic(topic_name, category, sources_config_path="config/sources.json"):
    """Fetch content for a topic from all enabled sources in a category."""
    registry = SourceRegistry(sources_config_path)
    sources = registry.get_enabled_sources(category)
    all_items = []
    sources_used = 0

    for source in sources:
        fetcher_name = source["fetcher"]

        try:
            # --- API fetchers ---
            if fetcher_name in FETCHER_MAP and fetcher_name != "generic":
                _, fetcher_fn, content_type = FETCHER_MAP[fetcher_name]
                if fetcher_fn is None:
                    continue

                raw = fetcher_fn(topic_name)
                sources_used += 1

                for item in raw:
                    all_items.append({
                        "source_id": source["id"],
                        "source_name": source["name"],
                        "title": item.get("title", ""),
                        "content": item.get("abstract") or item.get("content") or "",
                        "url": item.get("url") or item.get("pdf_url") or "",
                        "content_type": content_type,
                    })

            # --- Generic web fetcher ---
            elif fetcher_name == "generic":
                result = fetch_generic(source["url"])
                sources_used += 1

                if result:
                    all_items.append({
                        "source_id": source["id"],
                        "source_name": source["name"],
                        "title": result["title"],
                        "content": result["content"],
                        "url": result["url"],
                        "content_type": "blog",
                    })

        except Exception as e:
            print(f"Skipping {source['name']}: {e}")
            continue

    print(f"Fetched {len(all_items)} items from {sources_used} sources")
    return all_items


# ---------------------------------------------------------------------------
# CLI test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("Testing source fetchers")
    print("=" * 60)

    # Test generic web fetch
    print("\n--- Generic Web Fetch ---")
    result = fetch_generic("https://lilianweng.github.io/posts/2023-06-23-agent/")
    if result:
        print(f"  Title: {result['title']}")
        print(f"  Content preview: {result['content'][:200]}...")
    else:
        print("  (no result)")

    # Test arXiv
    print("\n--- arXiv ---")
    papers = fetch_arxiv("attention mechanism transformer")
    for p in papers[:3]:
        print(f"  [{p['arxiv_id']}] {p['title']}")

    # Test Semantic Scholar
    print("\n--- Semantic Scholar ---")
    papers = fetch_semantic_scholar("attention mechanism")
    for p in papers[:3]:
        print(f"  [{p['year']}] {p['title']} (cited {p['citation_count']}x)")

    # Test Hacker News
    print("\n--- Hacker News ---")
    stories = fetch_hacker_news("transformer neural network")
    for s in stories[:3]:
        print(f"  {s['title']} ({s['points']} pts, {s['num_comments']} comments)")

    # Summary
    print("\n" + "=" * 60)
    total = (1 if result else 0) + len(papers) + len(stories)
    print(f"Total items fetched: {total}")
    print("=" * 60)
