# Archon — Final Project Blueprint

## Vision

Archon is a personalized AI learning platform that generates a rich, visual ~15-page study document every night, tests your knowledge with daily assessments, tracks your progress through a live public dashboard, and auto-publishes everything to GitHub — creating an unbroken 165-day streak of verifiable AI/ML learning. It takes you from zero AI knowledge to research-paper fluency by August 2026, timed for big tech co-op applications.

---

## System Architecture

### Nightly Pipeline (runs at 2 AM)

```
Azure Functions (Orchestrator)
    │
    ├─▶ Module 1: Load learner profile (Azure Blob)
    ├─▶ Module 2: Curriculum Planner (Claude Haiku) → pick topic
    ├─▶ Module 3A: Content Sourcer (AWS Lambda) → fetch blogs/docs
    ├─▶ Module 3B: Paper Intelligence (AWS Lambda) → fetch/parse papers
    │       └─▶ Store all fetched sources in SQLite (metadata) + S3 (content)
    ├─▶ Module 3C: Source Ranker (Claude Sonnet) → pick best sources
    ├─▶ Module 4: Document Writer (Claude Opus + extended thinking) → study doc
    ├─▶ Module 5: PDF Renderer (GCP) → visual PDF with LaTeX/diagrams/code
    ├─▶ Module 6: Assessment Generator (Claude Haiku) → daily quiz
    ├─▶ Module 7: Analytics Engine (Python) → update progress metrics
    ├─▶ Module 8: Show Notes (Claude Sonnet) → summary
    ├─▶ Update learner profile (Azure Blob)
    ├─▶ Module 9: GitHub Auto-Upload → push episode + data
    └─▶ Notify → "Episode ready"
```

### Morning Consumption

| Option | What | Cost |
|--------|------|------|
| Read PDF | Visual study doc with formulas, diagrams, code | Free |
| ElevenReader | Single narrator reads PDF aloud | Free (Ultra) |
| GenFM | ElevenReader AI rewrites into two-host podcast | Free (Ultra) |
| Custom podcast | Claude Opus script → ElevenLabs API | Uses credits (rare) |

### Daily Assessment

After studying, you visit the dashboard and take a quiz generated from that day's episode. Scores update your knowledge graph with real measured confidence, not assumptions.

### Public Showcase

Recruiters click a link on your resume and see live learning analytics: completion progress, knowledge heatmap, assessment scores over time, daily streak, category breakdown.

---

## Modules

### Module 1: Learner Profile Manager
- **Purpose**: Tracks what you know via knowledge graph with confidence scores
- **Storage**: JSON in Azure Blob Storage
- **Starting level**: Second-year CS, Python/Java, no AI/ML background
- **Confidence updates**: Based on assessment scores (real data), with time decay for spaced repetition
- **Cloud**: Azure

### Module 2: Curriculum Planner
- **Purpose**: Selects tomorrow's topic respecting prerequisites and confidence thresholds
- **Model**: Claude Haiku (cheapest, sufficient for structured JSON selection)
- **Input**: Learner profile + last 7 episodes
- **Output**: JSON with topic_id, depth, subtopics, reasoning
- **Cloud**: Azure

### Module 3A: Content Sourcer
- **Purpose**: Fetches blogs, docs, course notes, community content
- **Fetcher types**: Generic (trafilatura for any URL) + specialized (arXiv API, Semantic Scholar API, Hacker News API, GitHub API, Papers With Code API)
- **Source registry**: JSON config file, editable via frontend dashboard
- **All fetched content**: Stored in SQLite (metadata) + S3 (full text, deleted after 7 days)
- **Cloud**: AWS Lambda

### Module 3B: Paper Intelligence Engine
- **Purpose**: Discovers, downloads, parses, comprehends, and translates research papers to your level
- **Discovery**: Semantic Scholar API (citation counts, influence scores, related papers)
- **Parsing**: PyMuPDF for PDF text extraction including formulas and figure captions
- **Comprehension**: Claude Opus reads full paper, identifies key contribution, methodology, results
- **Translation**: Rewrites at your current level, progressively using more original notation as confidence grows
- **Activates**: Phase 3 onwards (episode ~65), becomes primary source by Phase 6
- **Cloud**: AWS Lambda (discovery/parsing) + Azure (Opus calls)

### Module 3C: Source Ranker
- **Purpose**: Given fetched sources, picks the most relevant for today's topic
- **Model**: Claude Sonnet (good at relevance scoring, cheaper than Opus)
- **Cloud**: Azure

### Module 4: Document Writer
- **Purpose**: Core module. Generates ~6,000-word structured study document
- **Model**: Claude Opus with extended thinking enabled (budget: 10,000 tokens)
- **Document structure**: Yesterday's Recap → Introduction → Core Concepts (with LaTeX, diagrams, code) → Worked Examples → Common Pitfalls → Summary → Tomorrow's Preview
- **Quality rules**: Every formula derived step-by-step with English explanations, every code example complete and runnable, at least 3 visuals per episode
- **Cloud**: Azure

### Module 5: PDF Renderer
- **Purpose**: Transforms Markdown into professional visual PDF
- **Tools**: WeasyPrint (PDF generation), matplotlib + seaborn (plots), graphviz (diagrams), Pygments (code highlighting), Jinja2 (templates)
- **Cloud**: GCP Compute Engine / Cloud Functions

### Module 6: Assessment Generator
- **Purpose**: Creates 5-10 quiz questions from each episode for real knowledge measurement
- **Model**: Claude Haiku (cheap, excellent for question generation)
- **Question types**: Multiple choice (3-4 per quiz), short answer (2-3), code challenge (1 when relevant)
- **Output**: JSON with questions, correct answers, difficulty level, topic tags
- **Scoring**: Feeds back into Module 1 to update confidence scores with real data
- **Cloud**: Azure

### Module 7: Analytics Engine
- **Purpose**: Computes progress metrics and generates data for the public dashboard
- **Metrics computed**:
  - Episodes completed / total
  - Daily streak count
  - Assessment scores per episode (trend over time)
  - Average score by category (linear algebra, deep learning, etc.)
  - Knowledge graph coverage percentage
  - Learning velocity (topics per week)
  - Confidence distribution across all topics
- **Storage**: SQLite for historical data, JSON snapshots for the frontend
- **Cloud**: Azure (or computed locally as part of pipeline)

### Module 8: Show Notes Generator
- **Purpose**: Summarizes the episode for quick reference
- **Model**: Claude Sonnet
- **Cloud**: Azure

### Module 9: GitHub Auto-Upload
- **Purpose**: Pushes episode PDF, assessment data, and analytics to your GitHub repo every morning
- **Method**: Git CLI commands (add, commit, push) using GitHub Personal Access Token
- **Commit message**: "Episode {N}: {Topic Name}"
- **Result**: Daily green square on GitHub contribution graph, 165-day unbroken streak
- **Cloud**: Runs as final step in orchestrator

---

## Source Registry

### Pre-loaded Sources

**Academic (API fetchers)**
- arXiv (arxiv API)
- Semantic Scholar (API)
- Papers With Code (API)
- OpenReview (web scraper)

**Industry Research Blogs (generic fetcher)**
- Anthropic blog
- Google DeepMind blog
- OpenAI blog
- Meta AI (FAIR) blog
- Microsoft Research blog
- Hugging Face blog

**Educational (generic fetcher)**
- Lilian Weng's blog (lilianweng.github.io)
- Jay Alammar's blog
- Distill.pub
- 3Blue1Brown transcripts
- Andrej Karpathy's blog
- Stanford CS229/CS231n/CS224n notes

**Community (API fetchers)**
- Hacker News (HN API)
- Reddit r/MachineLearning (web scraper)
- GitHub Trending (GitHub API)
- Hugging Face daily papers

**News (generic fetcher)**
- MIT Technology Review
- The Gradient
- Import AI newsletter

### Source Registry Schema
```json
{
  "sources": [
    {
      "id": "lilian_weng",
      "name": "Lilian Weng's Blog",
      "url": "https://lilianweng.github.io",
      "type": "web",
      "fetcher": "generic",
      "categories": ["deep_learning", "transformers", "rl"],
      "quality": "high",
      "enabled": true
    }
  ]
}
```

**Adding a new source via frontend**: If fetcher is "generic", no code needed — trafilatura handles any URL. Only sources needing structured API data require a custom fetcher (5 already built: arXiv, Semantic Scholar, HN, GitHub, Papers With Code).

---

## Database Schema (SQLite)

```sql
-- Source fetch log (raw content deleted after 7 days)
CREATE TABLE source_fetches (
    id INTEGER PRIMARY KEY,
    episode_id INTEGER,
    source_id TEXT,
    url TEXT,
    title TEXT,
    content_hash TEXT,
    was_selected BOOLEAN,
    selection_reason TEXT,
    fetched_at TIMESTAMP,
    content_expires_at TIMESTAMP
);

-- Episode log
CREATE TABLE episodes (
    id INTEGER PRIMARY KEY,
    topic_id TEXT,
    topic_name TEXT,
    depth TEXT,
    phase INTEGER,
    generated_at TIMESTAMP,
    pdf_path TEXT,
    markdown_path TEXT,
    show_notes_path TEXT,
    github_commit_sha TEXT
);

-- Assessment results
CREATE TABLE assessments (
    id INTEGER PRIMARY KEY,
    episode_id INTEGER,
    question_text TEXT,
    question_type TEXT,  -- 'multiple_choice', 'short_answer', 'code_challenge'
    correct_answer TEXT,
    user_answer TEXT,
    is_correct BOOLEAN,
    difficulty TEXT,  -- 'easy', 'medium', 'hard'
    topic_tags TEXT,  -- JSON array
    answered_at TIMESTAMP
);

-- Daily analytics snapshots
CREATE TABLE analytics_snapshots (
    id INTEGER PRIMARY KEY,
    date DATE,
    episodes_completed INTEGER,
    streak_days INTEGER,
    avg_score_today REAL,
    avg_score_overall REAL,
    knowledge_coverage REAL,  -- 0.0 to 1.0
    category_scores TEXT,  -- JSON object
    snapshot_data TEXT  -- Full JSON for frontend
);
```

---

## Three-Cloud Strategy

| Cloud | Budget | Role | Resume Keywords |
|-------|--------|------|-----------------|
| GCP ($411) | Compute & rendering | PDF rendering, heavy compute | Compute Engine, Cloud Functions, Cloud Storage |
| AWS ($100) | Content & storage | Source fetching (Lambda), episode archive (S3) | S3, Lambda, CloudWatch, boto3, serverless |
| Azure ($100) | Orchestration & API | Pipeline coordinator, secrets, monitoring | Azure Functions, Key Vault, Blob Storage, Monitor |

---

## Frontend

### Phase 1 (Week 5-6): Functional Dashboard
- **Stack**: React + shadcn/ui + Tailwind CSS
- **Pages**:
  - **Dashboard**: Episode history, current progress, next topic
  - **Sources**: View/add/edit/disable sources, test source button
  - **Assessment**: Daily quiz interface, submit answers, see scores
  - **Analytics**: Charts showing progress over time
  - **Settings**: Model configs, schedule, notification preferences
- **Built by**: Claude Code (no Figma needed)
- **Hosted on**: Vercel (free tier)

### Phase 2 (post-applications): 3D Showcase
- **Stack**: Next.js + React Three Fiber + GSAP + Framer Motion + Spline
- **Feature**: 3D interactive knowledge graph (165 nodes, color-coded, animated)
- **Hosted on**: Vercel with custom domain

### Public Recruiter Dashboard (separate route, always live)
- **URL**: archon.yourdomain.dev/progress (or custom domain)
- **Shows**:
  - Progress: "142 of 165 episodes completed"
  - Knowledge heatmap (green = mastered, yellow = in progress, gray = upcoming)
  - Assessment score trend over time
  - Current streak: "142 consecutive days"
  - Category breakdown: "Linear Algebra: 94%, Transformers: 87%, RL: 72%"
  - Last updated timestamp (proves it's live)
- **No login required** — anyone with the link sees it
- **Data source**: analytics_snapshots table, served as static JSON updated nightly

---

## Model Usage & Cost

| Module | Model | Cost/Episode | Why This Model |
|--------|-------|-------------|----------------|
| Curriculum Planner | Haiku | ~$0.002 | Structured JSON task, rule-following |
| Source Ranker | Sonnet | ~$0.01 | Relevance scoring, doesn't need Opus |
| Paper Intelligence | Opus | ~$0.15 | Reading full papers requires deep reasoning |
| Document Writer | Opus (extended thinking) | ~$0.50 | The product — quality is everything |
| Assessment Generator | Haiku | ~$0.01 | Question generation from existing content |
| Show Notes | Sonnet | ~$0.02 | Summarizing Opus output, doesn't need Opus |
| **Total** | | **~$0.69** | **~$21/month** |

### Budget
- Monthly API cost: ~$21
- With Student Builder credits ($50): ~2.5 months free
- Cloud infrastructure: covered by $611 in credits (18+ months)
- ElevenReader: free (1 year Ultra)
- Domain: ~$12/year
- Vercel hosting: free tier
- **Effective cost: ~$21/month after credits expire**

---

## Curriculum: 165 Episodes in 7 Phases

### Phase 1: Mathematical Foundations (Episodes 1-30)
**Linear Algebra (1-10)**: Vectors → Matrices → Eigenvalues → SVD → Norms → Matrix Calculus → Data as Matrices → Recommender Capstone

**Calculus for ML (11-18)**: Derivatives → Partial Derivatives → Chain Rule → Optimization → Gradient Descent → SGD/Mini-batch → Adam → Capstone

**Probability & Statistics (19-28)**: Probability → Bayes → Distributions → Gaussian → Expectation/Variance → MLE → Information Theory → Monte Carlo → Hypothesis Testing → Naive Bayes Capstone

**Integration (29-30)**: How math connects to ML → Review & self-assessment

### Phase 2: Classical Machine Learning (Episodes 31-60)
**Core ML (31-38)**: What is ML → Linear Regression → Polynomial/Features → Regularization → Logistic Regression → Evaluation Metrics → Bias-Variance → Cross-Validation

**Trees (39-43)**: Decision Trees → Random Forests → Gradient Boosting → Feature Importance → ML Pipeline Capstone

**Unsupervised (44-50)**: K-Means → Hierarchical/DBSCAN → PCA → t-SNE/UMAP → SVM → GMM/EM → Classical ML Capstone

### Phase 3: Deep Learning Foundations (Episodes 51-80)
**Neural Nets (51-60)**: Perceptron → MLP → Activations → Backprop Derivation → Backprop Implementation → Training Practices → Dropout → BatchNorm → PyTorch Intro → MNIST Capstone

**CNNs (61-70)**: Convolutions → CNN Architecture → LeNet/AlexNet → VGG → ResNet (paper) → Modern CNNs → Transfer Learning → Object Detection → Segmentation → CNN Capstone

**RNNs (71-80)**: RNN Basics → BPTT → LSTM → GRU → Word2Vec → GloVe → Seq2Seq → Attention (paper) → Attention Visualized → Text Generation Capstone

### Phase 4: Transformers & Modern NLP (Episodes 81-110)
**Transformer Architecture (81-92)**: Self-Attention → Multi-Head → Positional Encoding → Transformer Block → Full Transformer (paper) → Training → BERT (paper) → GPT (paper) → Scaling Laws → Tokenization/BPE → LoRA/Fine-tuning → Mini-GPT Capstone

**Modern LLM (93-110)**: Instruction Tuning → RLHF → DPO → Prompt Engineering → RAG → Agents/ReAct → Multi-Modal/ViT → Flash Attention → Quantization → LLM Evaluation → Paper Deep Dives (8 episodes)

### Phase 5: Generative Models & Advanced (Episodes 111-140)
**Generative (111-122)**: Autoencoders → VAE → GAN → GAN Variants → Diffusion Intuition → DDPM Math (paper) → Latent Diffusion → Flow Matching → Text-to-Image → Audio Gen → Video Gen → Generative Capstone

**RL (123-135)**: MDPs → Bellman → Monte Carlo → TD/Q-Learning → DQN (paper) → Policy Gradients → PPO (paper) → RLHF Practice → Multi-Agent → Model-Based → Offline → Hierarchical → RL Capstone

**AI Safety (136-140)**: Alignment Problem → Constitutional AI (paper) → Mechanistic Interpretability → Red Teaming → Safety Research State

### Phase 6: Research Paper Mastery (Episodes 141-160)
How to read papers → 18 episodes of deep paper studies (2-3 episodes per paper)

### Phase 7: Interview Prep (Episodes 161-165)
Theory questions → System design → Coding challenges → Portfolio narrative → Mock interview

---

## Project Structure

```
Archon/
├── config/
│   ├── settings.yaml
│   ├── curriculum.json            # 165-topic knowledge graph
│   └── sources.json               # Source registry
├── data/
│   ├── profile.json               # Learner profile
│   ├── archon.db                  # SQLite database
│   └── episodes/                  # Episode metadata
├── output/
│   ├── pdfs/
│   ├── markdown/
│   ├── assessments/               # Daily quiz JSON files
│   └── show_notes/
├── src/
│   ├── profile_manager.py         # Module 1
│   ├── curriculum_planner.py      # Module 2
│   ├── content_sourcer.py         # Module 3A
│   ├── paper_engine.py            # Module 3B
│   ├── source_ranker.py           # Module 3C
│   ├── document_writer.py         # Module 4
│   ├── pdf_renderer.py            # Module 5
│   ├── assessment_generator.py    # Module 6
│   ├── analytics_engine.py        # Module 7
│   ├── show_notes_generator.py    # Module 8
│   ├── github_uploader.py         # Module 9
│   ├── orchestrator.py            # Pipeline coordinator
│   └── utils/
│       ├── claude_client.py       # Unified Claude API (Opus/Sonnet/Haiku)
│       ├── cloud_storage.py       # Multi-cloud storage abstraction
│       ├── source_fetchers.py     # Generic + specialized fetchers
│       ├── pdf_extractor.py       # PDF to text for papers
│       ├── diagram_generator.py   # Graphviz/matplotlib
│       └── database.py            # SQLite operations
├── templates/
│   ├── episode_template.html
│   └── episode_style.css
├── frontend/                      # React dashboard (Phase 1)
│   ├── src/
│   ├── public/
│   └── package.json
├── cloud/
│   ├── gcp/render_function/
│   ├── aws/lambda_sourcer/
│   └── azure/orchestrator_function/
├── requirements.txt
├── generate_episode.py            # Local entry point
└── README.md
```

---

## Development Roadmap

### Week 1: Core Pipeline Proof of Concept
Build Module 4 (Document Writer) and generate Episode 1 locally.

### Week 2: PDF Rendering
Build Module 5. Turn Markdown into professional visual PDFs.

### Week 3: Content Pipeline
Build Modules 2, 3A, 3C. Auto-select topics and fetch sources.

### Week 4: Assessments + Database
Build Modules 6, 7. Daily quizzes, SQLite storage, analytics.

### Week 5-6: Frontend Dashboard + Cloud Deployment
Build React dashboard. Deploy to three clouds. Set up nightly automation.

### Week 7: Paper Engine + GitHub Upload
Build Module 3B. Add Module 9. Public recruiter dashboard live.

### Week 8+: Polish and Iterate
Tune prompts, expand sources, build Phase 2 3D showcase.

---

## Key Design Principles

1. **PDF-First**: Visual study documents are the core product. Audio is a free bonus via ElevenReader.
2. **Measured Learning**: Daily assessments create real data. Confidence scores reflect actual knowledge, not assumptions.
3. **Multi-Cloud**: GCP renders, AWS sources, Azure orchestrates. Genuine experience with all three for your resume.
4. **Opus Where It Matters**: Document Writer and Paper Intelligence use Opus. Everything else uses cheaper models. ~$21/month.
5. **Public Proof**: Live recruiter dashboard with real analytics. 165-day GitHub streak. Verifiable, not claimable.
6. **Extensible Sources**: Generic fetcher handles any URL. Source registry editable via frontend. No code needed for most new sources.
7. **Math-First**: 30 episodes of pure math before ML. This foundation separates you from tutorial-watchers.
