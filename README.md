# Archon

A personalized AI learning platform that generates daily study documents, assessments, and progress analytics for mastering AI/ML from scratch.

## Overview

Archon is an AI-powered tutor that builds a custom curriculum tailored to your background and learning pace. Each day, it generates a structured study episode — a comprehensive document covering one topic in your AI/ML journey — using Claude's extended thinking capabilities for depth and accuracy. Archon tracks your progress through a knowledge graph, adapting future content based on what you've already mastered and where you need reinforcement.

## Current Status

**Week 1** — Core pipeline proof of concept

## Tech Stack

- **Python** — Core application language
- **Claude API** — Opus (extended thinking for document generation), Sonnet (analysis), Haiku (lightweight tasks)
- **SQLite** — Local data persistence and progress tracking
- **Deployment** — GCP / AWS / Azure (planned)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/RastinAghighi/Archon.git
cd Archon

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY="your-key-here"        # Linux/macOS
set ANTHROPIC_API_KEY=your-key-here             # Windows

# Generate your first episode
python generate_episode.py
```

## Project Structure

```
Archon/
├── config/
│   └── settings.yaml           # Model and generation settings
├── data/
│   └── profile.json            # Learner profile and knowledge graph
├── output/
│   └── markdown/               # Generated study episodes
├── src/
│   ├── __init__.py
│   ├── document_writer.py      # Episode generation with Opus extended thinking
│   └── utils/
│       ├── __init__.py
│       └── claude_client.py    # Claude API client (Opus/Sonnet/Haiku)
├── generate_episode.py         # Main entry point
├── requirements.txt
├── LICENSE
└── .gitignore
```

## Roadmap

| Week | Milestone |
|------|-----------|
| 1 | Core pipeline — document generation with Claude Opus extended thinking |
| 2 | Assessment engine — quizzes, problem sets, and answer evaluation |
| 3 | Knowledge graph — adaptive topic sequencing and spaced repetition |
| 4 | Progress analytics — dashboards and performance tracking |
| 5 | Multi-format output — PDF export, interactive notebooks |
| 6 | Voice and multimedia — audio summaries, diagram generation |
| 7 | Cloud deployment — API service with user authentication |
| 8 | Polish and launch — testing, documentation, and public release |

## License

[MIT](LICENSE)
