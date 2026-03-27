"""
Module 3B: Paper Engine
Discovers, downloads, parses, comprehends, and translates research papers
using arXiv, Semantic Scholar, PyMuPDF, and Claude.
"""

import os
import json
import hashlib
import tempfile
import time

import requests
import arxiv
import fitz  # PyMuPDF

from src.utils.claude_client import call_claude


PAPER_COMPREHENSION_PROMPT = """You are an expert at reading and explaining research papers. Given the full text of an academic paper, provide a comprehensive analysis.

Your analysis should include:
1. PAPER OVERVIEW: Title, authors, year, venue (if known)
2. KEY CONTRIBUTION: What is the main innovation or finding? (2-3 sentences)
3. PROBLEM STATEMENT: What problem does this paper solve?
4. METHODOLOGY: How do they solve it? Explain the approach step by step.
5. KEY RESULTS: What are the main experimental results or theoretical proofs?
6. WHY IT MATTERS: Why is this paper important for the field?
7. CONNECTIONS: How does this relate to other important work?
8. SIMPLIFIED EXPLANATION: Explain the core idea as if teaching a {learner_level} student. Use analogies. Be thorough but accessible.

Be thorough and precise. If the paper contains important equations, explain each variable and what the equation means intuitively.
"""


class PaperEngine:
    """End-to-end pipeline for discovering, parsing, and comprehending research papers."""

    def __init__(self):
        self.arxiv_client = arxiv.Client()

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def discover_papers(self, topic, max_results=5):
        """Search arXiv and Semantic Scholar, combine and deduplicate results."""
        papers = []
        seen_titles = set()

        # --- arXiv ---
        try:
            search = arxiv.Search(
                query=topic,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance,
            )
            for p in self.arxiv_client.results(search):
                title_key = p.title.lower().strip()
                if title_key not in seen_titles:
                    seen_titles.add(title_key)
                    papers.append({
                        "title": p.title,
                        "authors": [a.name for a in p.authors],
                        "abstract": p.summary,
                        "year": p.published.year,
                        "arxiv_id": p.entry_id.split("/")[-1],
                        "pdf_url": p.pdf_url,
                        "citation_count": 0,
                    })
        except Exception as e:
            print(f"arXiv discovery error: {e}")

        # --- Semantic Scholar ---
        try:
            time.sleep(1)  # rate-limit courtesy
            resp = requests.get(
                "https://api.semanticscholar.org/graph/v1/paper/search",
                params={
                    "query": topic,
                    "limit": max_results,
                    "fields": "title,abstract,authors,citationCount,year,externalIds,url",
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

            for p in data.get("data", []):
                title_key = (p.get("title") or "").lower().strip()
                if title_key and title_key not in seen_titles:
                    seen_titles.add(title_key)
                    ext_ids = p.get("externalIds") or {}
                    arxiv_id = ext_ids.get("ArXiv", "")
                    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}" if arxiv_id else ""
                    papers.append({
                        "title": p.get("title", ""),
                        "authors": [a.get("name", "") for a in (p.get("authors") or [])],
                        "abstract": p.get("abstract") or "",
                        "year": p.get("year"),
                        "arxiv_id": arxiv_id,
                        "pdf_url": pdf_url,
                        "citation_count": p.get("citationCount", 0),
                    })
                else:
                    # Update citation count for duplicates found earlier via arXiv
                    for existing in papers:
                        if existing["title"].lower().strip() == title_key:
                            existing["citation_count"] = max(
                                existing["citation_count"],
                                p.get("citationCount", 0),
                            )
                            break
        except Exception as e:
            print(f"Semantic Scholar discovery error: {e}")

        # Sort by citation count descending
        papers.sort(key=lambda x: x.get("citation_count", 0), reverse=True)

        print(f"Discovered {len(papers)} papers for '{topic}'")
        return papers

    # ------------------------------------------------------------------
    # Download
    # ------------------------------------------------------------------

    def download_paper(self, pdf_url, save_dir="data/papers"):
        """Download a paper PDF and return the local file path."""
        os.makedirs(save_dir, exist_ok=True)

        # Build a safe filename from the URL
        url_hash = hashlib.md5(pdf_url.encode()).hexdigest()[:12]
        # Try to extract arxiv id for a readable name
        parts = pdf_url.rstrip("/").split("/")
        name_part = parts[-1] if parts else url_hash
        name_part = name_part.replace(".pdf", "")
        filename = f"{name_part}_{url_hash}.pdf"
        filepath = os.path.join(save_dir, filename)

        if os.path.exists(filepath):
            print(f"Already downloaded: {filename}")
            return filepath

        try:
            resp = requests.get(pdf_url, timeout=60, headers={
                "User-Agent": "Mozilla/5.0 (compatible; Archon/1.0)",
            })
            resp.raise_for_status()

            with open(filepath, "wb") as f:
                f.write(resp.content)

            print(f"Downloaded: {filename}")
            return filepath
        except Exception as e:
            print(f"Download error for {pdf_url}: {e}")
            return None

    # ------------------------------------------------------------------
    # Parse
    # ------------------------------------------------------------------

    def parse_paper(self, pdf_path, max_pages=30):
        """Extract text from a PDF using PyMuPDF."""
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            print(f"Failed to open PDF {pdf_path}: {e}")
            return None

        pages_to_read = min(len(doc), max_pages)
        page_texts = []
        for i in range(pages_to_read):
            page_texts.append(doc[i].get_text())

        full_text = "\n--- Page Break ---\n".join(page_texts)

        # Try to extract title from first page (first large-font text)
        title = ""
        try:
            first_page = doc[0]
            blocks = first_page.get_text("dict")["blocks"]
            max_size = 0
            for block in blocks:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        if span["size"] > max_size:
                            max_size = span["size"]
                            title = span["text"]
        except Exception:
            pass

        # Try to extract abstract
        abstract = ""
        lower_text = full_text.lower()
        abs_start = lower_text.find("abstract")
        if abs_start != -1:
            abs_text = full_text[abs_start + len("abstract"):]
            # Take text until the next section heading or 2000 chars
            for marker in ["\n1 ", "\n1.", "\nintroduction", "\n\n\n"]:
                end = abs_text.lower().find(marker)
                if end != -1:
                    abs_text = abs_text[:end]
                    break
            abstract = abs_text[:2000].strip()

        doc.close()

        result = {
            "full_text": full_text,
            "title": title.strip() or os.path.basename(pdf_path),
            "abstract": abstract,
            "num_pages": pages_to_read,
        }

        print(f"Parsed: {result['title']} ({result['num_pages']} pages, {len(full_text)} chars)")
        return result

    # ------------------------------------------------------------------
    # Comprehend (Opus — expensive)
    # ------------------------------------------------------------------

    def comprehend_paper(self, paper_text, paper_title, learner_level="beginner"):
        """Send paper text to Claude Opus for deep comprehension analysis."""
        # Truncate to fit context window
        paper_text = paper_text[:50_000]

        prompt = PAPER_COMPREHENSION_PROMPT.replace("{learner_level}", learner_level)

        user_prompt = (
            f"Paper Title: {paper_title}\n\n"
            f"Full Paper Text:\n{paper_text}"
        )

        analysis = call_claude(
            model="claude-opus-4-5-20250514",
            system_prompt=prompt,
            user_prompt=user_prompt,
            max_tokens=8192,
        )

        if analysis:
            print(f"Comprehended: {paper_title}")
        else:
            print(f"Comprehension failed for: {paper_title}")

        return analysis

    # ------------------------------------------------------------------
    # Translate for learner level (Sonnet — cheaper)
    # ------------------------------------------------------------------

    def translate_for_learner(self, paper_analysis, topic_name, learner_level="beginner"):
        """Rewrite the paper analysis at the appropriate learner level."""
        level_instructions = {
            "beginner": (
                "Rewrite this paper analysis for a complete beginner. "
                "Use simple analogies and everyday language. Avoid mathematical notation entirely. "
                "Focus on building intuition about why this matters and what the core idea is."
            ),
            "intermediate": (
                "Rewrite this paper analysis for an intermediate learner. "
                "Include some mathematical notation where helpful, but always explain what it means. "
                "Go deeper into the methodology while keeping explanations accessible."
            ),
            "advanced": (
                "Rewrite this paper analysis for an advanced learner. "
                "Use the original mathematical notation and technical terminology. "
                "Focus on methodology details, experimental design, and connections to related work."
            ),
        }

        instruction = level_instructions.get(learner_level, level_instructions["beginner"])

        system_prompt = (
            "You are an expert science communicator who adapts technical content "
            "for different audiences. Preserve accuracy while adjusting complexity."
        )

        user_prompt = (
            f"Topic context: {topic_name}\n"
            f"Target level: {learner_level}\n\n"
            f"Instructions: {instruction}\n\n"
            f"Paper analysis to translate:\n{paper_analysis}"
        )

        translated = call_claude(
            model="claude-sonnet-4-5-20250514",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=4096,
        )

        if translated:
            print(f"Translated analysis for {learner_level} level")
        else:
            print("Translation failed — returning original analysis")
            translated = paper_analysis

        return translated

    # ------------------------------------------------------------------
    # Full pipeline
    # ------------------------------------------------------------------

    def process_paper(self, topic, learner_level="beginner"):
        """Full pipeline: discover → download → parse → comprehend → translate."""
        result = {
            "title": None,
            "authors": None,
            "year": None,
            "analysis": None,
            "translated_explanation": None,
            "pdf_path": None,
        }

        # Discover
        papers = self.discover_papers(topic)
        if not papers:
            print("No papers found — aborting pipeline")
            return result

        # Select best paper (already sorted by citation count)
        best = papers[0]
        result["title"] = best["title"]
        result["authors"] = best["authors"]
        result["year"] = best["year"]

        # Download
        if not best.get("pdf_url"):
            print(f"No PDF URL for '{best['title']}' — aborting pipeline")
            return result

        pdf_path = self.download_paper(best["pdf_url"])
        if not pdf_path:
            return result
        result["pdf_path"] = pdf_path

        # Parse
        parsed = self.parse_paper(pdf_path)
        if not parsed:
            return result

        # Comprehend (expensive Opus call)
        analysis = self.comprehend_paper(parsed["full_text"], best["title"], learner_level)
        if not analysis:
            return result
        result["analysis"] = analysis

        # Translate
        translated = self.translate_for_learner(analysis, topic, learner_level)
        result["translated_explanation"] = translated

        return result


# ---------------------------------------------------------------------------
# CLI test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Paper Engine")
    print("=" * 60)

    engine = PaperEngine()

    # Test discovery
    print("\n--- Discovering papers ---")
    papers = engine.discover_papers("attention mechanism transformer")

    if papers:
        print(f"\nFound {len(papers)} papers:")
        for i, p in enumerate(papers):
            print(f"  [{i}] {p['title']} (cited {p['citation_count']}x, {p['year']})")

        # Download and parse the first one
        best = papers[0]
        if best.get("pdf_url"):
            print(f"\n--- Downloading: {best['title']} ---")
            pdf_path = engine.download_paper(best["pdf_url"])

            if pdf_path:
                print(f"\n--- Parsing ---")
                parsed = engine.parse_paper(pdf_path)

                if parsed:
                    print(f"\nFirst 1000 chars of parsed text:")
                    print(parsed["full_text"][:1000])
                    print("...")
        else:
            print("No PDF URL available for top paper")

        # Skip comprehension
        print("\n--- Skipping Opus comprehension in test mode (too expensive for testing) ---")
    else:
        print("No papers found")

    print("\n" + "=" * 60)
    print("Paper Engine test complete")
    print("=" * 60)
