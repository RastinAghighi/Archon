# Archon

A personalized AI learning platform that generates daily study documents with visual PDFs, assessments, and progress analytics for mastering AI/ML from scratch to research-paper fluency.

## Current Status

**Week 3** -- Full content pipeline with auto-sourcing and paper intelligence

## Features

- **Claude Opus-powered study documents** -- Extended thinking generates 25-30 page episodes with LaTeX formulas, code examples, and worked problems
- **Professional PDF rendering** -- xhtml2pdf pipeline with syntax-highlighted code blocks, rendered LaTeX, and matplotlib diagrams
- **Daily assessment quizzes** -- Claude Haiku generates topic-specific quizzes; scores feed back into the knowledge graph
- **Knowledge graph** -- 165 topics across 7 phases, from linear algebra fundamentals to research-paper reproduction
- **Confidence scoring** -- Real assessment performance drives per-topic confidence values
- **Spaced repetition** -- Time-decay on confidence scores surfaces topics that need review
- **Analytics engine** -- Daily progress snapshots with public dashboard data export
- **SQLite persistence** -- All episode metadata, assessment results, and analytics stored locally
- **Multi-source content fetching** -- arXiv, Semantic Scholar, Hacker News, and 19+ sources feed real-world context into every episode
- **Paper Intelligence Engine** -- Discover, download, parse, and comprehend research papers automatically using PyMuPDF and Claude
- **Claude Haiku-powered curriculum planning** -- Prerequisite-aware topic selection ensures optimal learning order
- **Source ranking with Claude Sonnet** -- Quality filtering scores and ranks fetched content for relevance before inclusion
- **Configurable source registry** -- JSON-based source definitions, extensible via frontend later
- **Auto-generated show notes** -- Quick-reference summaries of each episode for review
- **GitHub auto-upload with streak tracking** -- Automated commits and push with daily streak monitoring

## Tech Stack

| Component | Technology |
|-----------|------------|
| Core language | Python |
| Document generation | Claude API (Opus with extended thinking) |
| Curriculum planning | Claude API (Haiku) |
| Source ranking | Claude API (Sonnet) |
| Assessments | Claude API (Haiku) |
| PDF rendering | xhtml2pdf + Jinja2 templates |
| Paper parsing | PyMuPDF (fitz) |
| Web scraping | trafilatura + BeautifulSoup4 |
| Academic APIs | arxiv, Semantic Scholar, Hacker News |
| Diagrams | matplotlib + seaborn |
| Math rendering | LaTeX via Markdown extensions |
| Code highlighting | Pygments |
| Database | SQLite |
| Config | YAML + JSON + python-dotenv |
| Version control | GitHub API (auto-upload) |

## Quick Start

```bash
# Clone the repository
git clone https://github.com/RastinAghighi/Archon.git
cd Archon

# Create and activate a virtual environment
py -m venv venv
venv\Scripts\activate           # Windows
# source venv/bin/activate      # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Set your API key
set ANTHROPIC_API_KEY=your-key-here             # Windows
# export ANTHROPIC_API_KEY="your-key-here"      # Linux/macOS

# Generate your first episode (document + PDF + assessment + analytics)
py generate_episode.py
```

## Project Structure

```
Archon/
├── config/
│   ├── settings.yaml              # Model and generation settings
│   ├── sources.json               # Source registry (19+ content sources)
│   └── curated_sources.json       # Curated high-quality source list
├── data/
│   ├── profile.json               # Learner profile and knowledge graph (165 topics)
│   ├── episodes/                  # Stored episode data
│   └── archon.db                  # SQLite database
├── output/
│   ├── markdown/                  # Generated study episodes (.md)
│   ├── pdfs/                      # Rendered PDF documents
│   │   └── diagrams/             # Generated matplotlib diagrams
│   ├── assessments/               # Quiz results (.json)
│   └── analytics/                 # Daily snapshots and public dashboard data
├── src/
│   ├── __init__.py
│   ├── document_writer.py         # Episode generation with Opus extended thinking
│   ├── pdf_renderer.py            # xhtml2pdf PDF pipeline
│   ├── assessment_generator.py    # Quiz generation with Haiku
│   ├── analytics_engine.py        # Progress snapshots and dashboard export
│   ├── profile_manager.py         # Confidence scoring and spaced repetition
│   ├── content_sourcer.py         # Multi-source content fetching engine
│   ├── curriculum_planner.py      # Haiku-powered prerequisite-aware planning
│   ├── paper_engine.py            # Paper Intelligence Engine (discover/parse/comprehend)
│   ├── source_ranker.py           # Sonnet-powered relevance scoring
│   ├── show_notes_generator.py    # Auto-generated episode show notes
│   ├── github_uploader.py         # GitHub auto-upload with streak tracking
│   └── utils/
│       ├── __init__.py
│       ├── claude_client.py       # Claude API client (Opus/Sonnet/Haiku)
│       ├── database.py            # SQLite schema and queries
│       ├── markdown_converter.py  # Markdown-to-HTML with LaTeX and code blocks
│       ├── diagram_generator.py   # matplotlib/seaborn chart generation
│       └── source_fetchers.py     # Individual source fetch implementations
├── templates/
│   ├── episode_template.html      # Jinja2 PDF template
│   └── episode_style.css          # PDF stylesheet
├── generate_episode.py            # Main entry point — runs full pipeline
├── requirements.txt
├── LICENSE
└── .gitignore
```

## Roadmap

| Week | Milestone | Status |
|------|-----------|--------|
| 1 | Core pipeline -- document generation with Claude Opus extended thinking | Done |
| 1 | PDF rendering with LaTeX, code highlighting, and diagrams | Done |
| 2 | Assessment engine -- daily quizzes generated by Claude Haiku | Done |
| 2 | Analytics engine -- daily snapshots and public dashboard data | Done |
| 2 | Profile manager -- confidence scoring and spaced repetition | Done |
| 3 | Content sourcing -- multi-source fetching from 19+ sources | Done |
| 3 | Paper Intelligence Engine -- discover, parse, and comprehend research papers | Done |
| 3 | Curriculum planner -- prerequisite-aware topic selection with Haiku | Done |
| 3 | Source ranker -- Claude Sonnet relevance scoring and quality filtering | Done |
| 3 | Show notes generator and GitHub auto-upload with streak tracking | Done |
| 4 | Cloud deployment -- GCP Cloud Run API service | Planned |
| 5 | AWS integration -- S3 storage and Lambda functions | Planned |
| 6 | Azure integration -- Cosmos DB and Functions | Planned |
| 7 | React frontend -- progress dashboard and episode viewer | Planned |
| 8 | Public recruiter dashboard -- read-only progress showcase | Planned |
| 9 | ElevenReader integration -- audio summaries of episodes | Planned |

## Planned Architecture

- **Three-cloud deployment** -- GCP (primary API), AWS (storage/compute), Azure (database/serverless)
- **React frontend** -- Interactive dashboard for viewing episodes, assessments, and progress
- **Public recruiter dashboard** -- Read-only view showcasing learning progress and completed topics
- **ElevenReader integration** -- AI-generated audio narration of study episodes

## License

[MIT](LICENSE)
