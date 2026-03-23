# Archon — Claude Code Step-by-Step Prompts

## How to Use This File

1. Open your terminal, navigate to your Archon directory: `cd path/to/Archon`
2. Launch Claude Code: `claude`
3. Copy-paste ONE prompt at a time from below
4. Wait for Claude Code to finish
5. Run the VERIFY command to confirm it worked
6. Only then proceed to the next step

Do NOT skip verification steps. If something fails, fix it before moving on.

---

## WEEK 1: Core Pipeline — Generate Episode 1

---

### Step 1: Project Structure

```
Create the following folder structure for the Archon project in this directory. Create empty __init__.py files in src/ and src/utils/ to make them Python packages. Do not create any file contents yet — only the folders and empty placeholder files.

Archon/
├── config/
│   ├── (empty, files created in later steps)
├── data/
│   ├── episodes/
├── output/
│   ├── pdfs/
│   ├── markdown/
│   ├── assessments/
│   └── show_notes/
├── src/
│   ├── __init__.py
│   └── utils/
│       └── __init__.py
├── templates/
├── frontend/
├── cloud/
│   ├── gcp/
│   ├── aws/
│   └── azure/
```

Only create the folder structure and __init__.py files. Nothing else.
```

**VERIFY**: Run `find . -type d | head -20` and confirm all folders exist.

---

### Step 2: Requirements File

```
Create a requirements.txt file for the Archon project. For Week 1, we only need:

anthropic          # Claude API SDK
pyyaml             # Config file parsing
python-dotenv      # Environment variable loading

Add these as the initial dependencies. We will add more (matplotlib, graphviz, weasyprint, etc.) in later weeks.
```

**VERIFY**: Run `cat requirements.txt` and confirm the three packages are listed.

---

### Step 3: Install Dependencies

```
Create a Python virtual environment in this project directory and install the dependencies from requirements.txt.

Commands to run:
python -m venv venv
source venv/bin/activate   (or venv\Scripts\activate on Windows)
pip install -r requirements.txt

Run these commands now.
```

**VERIFY**: Run `pip list | grep anthropic` and confirm the anthropic package is installed.

---

### Step 4: Settings Configuration

```
Create config/settings.yaml with the following structure:

api:
  anthropic_api_key: ${ANTHROPIC_API_KEY}    # Read from environment variable
  
models:
  document_writer: "claude-opus-4-20250514"
  curriculum_planner: "claude-haiku-4-5-20251001"
  source_ranker: "claude-sonnet-4-20250514"
  show_notes: "claude-sonnet-4-20250514"
  assessment_generator: "claude-haiku-4-5-20251001"

document_writer:
  max_tokens: 8192
  extended_thinking: true
  thinking_budget: 10000
  target_words: 6000
  target_pages: 15

episode:
  default_study_time_minutes: 60

output:
  pdfs_dir: "output/pdfs"
  markdown_dir: "output/markdown"
  assessments_dir: "output/assessments"
  show_notes_dir: "output/show_notes"

database:
  path: "data/archon.db"

Only create this one file. Do not create any Python code yet.
```

**VERIFY**: Run `cat config/settings.yaml` and confirm the structure looks correct.

---

### Step 5: Learner Profile

```
Create data/profile.json with the following content. This is the initial learner profile for a second-year CS student starting AI/ML from scratch.

Include:
- learner info: name as "Learner" (placeholder), background description, level "beginner", target "Big tech co-op by August 2026", started date as today
- episodes_completed: 0
- knowledge_graph: Include ONLY the Phase 1 topics (episodes 1-30) for now. Each topic needs:
  - id (snake_case)
  - name (human readable)
  - confidence: 0.0
  - prerequisites: array of topic ids that must have confidence >= 0.6 to unlock this
  - category: "linear_algebra", "calculus", "probability", or "math_integration"
  - phase: 1
  - episodes: array with the episode number(s)
  - has_code: true
  - has_math: true

The Phase 1 topics and their prerequisites are:

LINEAR ALGEBRA (episodes 1-10):
1. vectors_and_spaces — no prerequisites
2. dot_products_projections — prerequisites: [vectors_and_spaces]
3. matrices_multiplication — prerequisites: [vectors_and_spaces]
4. matrix_properties — prerequisites: [matrices_multiplication]
5. eigenvalues_eigenvectors — prerequisites: [matrix_properties]
6. svd — prerequisites: [eigenvalues_eigenvectors]
7. norms_distances — prerequisites: [vectors_and_spaces]
8. matrix_calculus — prerequisites: [matrices_multiplication]
9. data_as_matrices — prerequisites: [matrices_multiplication, norms_distances]
10. recommender_capstone — prerequisites: [svd, data_as_matrices]

CALCULUS (episodes 11-18):
11. derivatives — no prerequisites
12. partial_derivatives — prerequisites: [derivatives]
13. chain_rule — prerequisites: [partial_derivatives]
14. optimization — prerequisites: [partial_derivatives]
15. gradient_descent — prerequisites: [optimization, chain_rule]
16. sgd_minibatch — prerequisites: [gradient_descent]
17. advanced_optimizers — prerequisites: [sgd_minibatch]
18. calculus_capstone — prerequisites: [advanced_optimizers]

PROBABILITY (episodes 19-28):
19. probability_basics — no prerequisites
20. bayes_theorem — prerequisites: [probability_basics]
21. random_variables — prerequisites: [probability_basics]
22. gaussian_distribution — prerequisites: [random_variables]
23. expectation_variance — prerequisites: [random_variables]
24. mle — prerequisites: [gaussian_distribution, expectation_variance]
25. information_theory — prerequisites: [probability_basics]
26. monte_carlo — prerequisites: [expectation_variance]
27. hypothesis_testing — prerequisites: [gaussian_distribution]
28. naive_bayes_capstone — prerequisites: [bayes_theorem, mle, information_theory]

INTEGRATION (episodes 29-30):
29. math_connects_to_ml — prerequisites: [recommender_capstone, calculus_capstone, naive_bayes_capstone]
30. math_review — prerequisites: [math_connects_to_ml]

Format it as clean, readable JSON. Only create this file.
```

**VERIFY**: Run `python -c "import json; d=json.load(open('data/profile.json')); print(f'Topics: {len(d[\"knowledge_graph\"])}')"` and confirm it prints `Topics: 30`.

---

### Step 6: Claude API Client Utility

```
Create src/utils/claude_client.py — a unified wrapper around the Anthropic Python SDK.

This module should:

1. Load the API key from the ANTHROPIC_API_KEY environment variable
2. Provide a single function: call_claude(model, system_prompt, user_prompt, max_tokens=4096, extended_thinking=False, thinking_budget=10000)
3. The function should:
   - Create an Anthropic client
   - If extended_thinking is True, use the appropriate API parameter for extended thinking with the specified budget
   - Make the API call
   - Return the response text content (just the string, not the full response object)
   - Handle errors gracefully: print the error message and return None if the call fails
4. Include a simple test at the bottom under if __name__ == "__main__": that calls Haiku with "Say hello" to verify the API key works

Use the anthropic Python SDK. Import anthropic at the top.
Do NOT hardcode any API keys.
Only create this one file.
```

**VERIFY**: Run `python src/utils/claude_client.py` — it should print a greeting from Claude. If it fails with an auth error, check your ANTHROPIC_API_KEY environment variable.

---

### Step 7: Document Writer — Prompt Template

```
Create src/document_writer.py with ONLY the prompt template for now. Do not write the API call logic yet — that's the next step.

The file should contain:

1. A constant string SYSTEM_PROMPT that contains the full system prompt for the document writer. Here it is:

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

2. A function build_user_prompt(topic_name, depth, subtopics, source_material, profile_summary, yesterday_topic, tomorrow_topic) that returns a formatted user prompt string combining all these inputs.

3. Nothing else — no API calls, no main block. Just the template and the builder function.

Only create this one file.
```

**VERIFY**: Run `python -c "from src.document_writer import SYSTEM_PROMPT; print(f'Prompt length: {len(SYSTEM_PROMPT)} chars')"` and confirm it loads without errors.

---

### Step 8: Document Writer — API Call Logic

```
Open src/document_writer.py and ADD (do not replace existing code) the following:

1. Import call_claude from src.utils.claude_client
2. Import yaml and load config/settings.yaml to get model name and extended thinking settings

3. Add a function generate_document(topic_name, depth, subtopics, source_material, profile_summary, yesterday_topic, tomorrow_topic) that:
   - Calls build_user_prompt() to construct the user prompt
   - Reads the model name from settings.yaml (models.document_writer)
   - Reads extended_thinking and thinking_budget from settings.yaml
   - Calls call_claude() with the SYSTEM_PROMPT, the user prompt, the model, max_tokens=8192, and extended thinking settings
   - Returns the generated markdown string
   - Prints progress messages: "Generating document for: {topic_name}..." and "Document generated: {word_count} words"

4. Add an if __name__ == "__main__": block that tests generate_document with:
   - topic_name: "Scalars, Vectors, and Vector Spaces"
   - depth: "intro"
   - subtopics: ["What vectors really represent", "Vector addition and scalar multiplication", "Basis vectors and linear independence", "NumPy vector operations"]
   - source_material: "This is the first episode. Cover vectors from first principles. Include geometric intuition, mathematical notation, and Python code with NumPy."
   - profile_summary: "Second-year CS student, comfortable with Python, no linear algebra background beyond high school."
   - yesterday_topic: "None — this is Episode 1"
   - tomorrow_topic: "Dot Products, Projections, and Cosine Similarity"
   - Save the result to output/markdown/episode_001.md
   - Print the file path on success

Do NOT modify the existing SYSTEM_PROMPT or build_user_prompt function. Only add the new function and the test block.
```

**VERIFY**: Run `python src/document_writer.py` — this will make a real API call to Claude Opus. It may take 1-2 minutes. When it finishes, check that output/markdown/episode_001.md exists and contains a full study document. Read through it — does it teach well?

---

### Step 9: Generate Episode Script

```
Create generate_episode.py in the project root. This is the main entry point for generating episodes.

For Week 1, this is a simplified version that hardcodes Episode 1. It should:

1. Import generate_document from src.document_writer
2. Import json to load the learner profile

3. Define the episode configuration inline (hardcoded for now):
   episode_num = 1
   topic_id = "vectors_and_spaces"
   topic_name = "Scalars, Vectors, and Vector Spaces"
   depth = "intro"
   subtopics = [
       "What vectors really represent (not just arrays)",
       "Vector addition, scalar multiplication",
       "Basis vectors and linear independence",
       "Python code: NumPy vector operations"
   ]
   source_material = (a 2-3 paragraph description of what to cover for this topic — write something useful here about vectors, spaces, basis, and why they matter for ML)
   yesterday_topic = "None — welcome to Archon! This is your first episode."
   tomorrow_topic = "Dot Products, Projections, and Cosine Similarity — we'll learn how to measure angles and similarity between vectors, which is fundamental to how search engines and recommendation systems work."

4. Load the learner profile from data/profile.json and extract a brief summary string

5. Call generate_document() with all the parameters

6. Save the output to output/markdown/episode_001_vectors_and_spaces.md

7. Print:
   - "✓ Episode 1 generated successfully"
   - "  Topic: Scalars, Vectors, and Vector Spaces"
   - "  Output: output/markdown/episode_001_vectors_and_spaces.md"
   - "  Word count: {count}"
   - ""
   - "Next step: Read the document and verify quality."

8. Update the profile: set vectors_and_spaces confidence to 0.3 (listened but not yet assessed) and increment episodes_completed to 1. Save back to data/profile.json.

Only create this one file.
```

**VERIFY**: Run `python generate_episode.py` — this calls Claude Opus and generates your first episode. Read the output file. This is the most important verification: **does the document teach you about vectors in a way that's clear, thorough, and engaging?**

---

### Step 10: README

```
Create a README.md for the Archon project. Include:

1. Project name: Archon
2. One-line description: "A personalized AI learning platform that generates daily study documents, assessments, and progress analytics for mastering AI/ML from scratch."
3. A brief overview (3-4 sentences) explaining what Archon does
4. Current status: "Week 1 — Core pipeline proof of concept"
5. Tech stack section listing: Python, Claude API (Opus/Sonnet/Haiku), SQLite, and noting that GCP/AWS/Azure deployment is planned
6. Quick start instructions:
   - Clone repo
   - Create virtual environment
   - pip install -r requirements.txt
   - Set ANTHROPIC_API_KEY environment variable
   - python generate_episode.py
7. Project structure showing the folder layout
8. A roadmap section with Week 1-8 milestones
9. License: MIT

Write it professionally — this README will be visible on your public GitHub repo.
Only create this one file.
```

**VERIFY**: Read the README. Does it look professional? Would you be proud to show this repo to a recruiter?

---

## END OF WEEK 1

At this point you should have:
- [x] Complete project structure
- [x] Working Claude API connection
- [x] Document writer that generates ~15-page study documents
- [x] Your first episode: "Scalars, Vectors, and Vector Spaces"
- [x] A professional README
- [x] An updated learner profile

**Before moving to Week 2**, do this:
1. Read Episode 1 thoroughly. Note anything that could be better.
2. Feed the Markdown file to ElevenReader — test both narration and GenFM.
3. If the document quality needs improvement, iterate on the SYSTEM_PROMPT in step 7.

**Week 2 prompts** (PDF rendering, assessment generator, database) will be provided in a separate file. Get Week 1 working perfectly first.

---

## WEEK 2 PREVIEW (prompts provided after Week 1 is complete)

- Step 11: Create SQLite database with schema
- Step 12: Build PDF template (HTML + CSS for WeasyPrint)
- Step 13: Build diagram generator (matplotlib + graphviz)
- Step 14: Build PDF renderer module
- Step 15: Build assessment generator (Claude Haiku)
- Step 16: Build analytics engine
- Step 17: Wire assessment scoring into learner profile
- Step 18: Generate Episode 2 with full PDF + assessment
- Step 19: Test the complete local pipeline for 3 episodes
- Step 20: Initialize Git repo and push to GitHub
```

**VERIFY**: After Week 2, you should have: professional PDFs with rendered LaTeX and diagrams, daily quizzes, a SQLite database tracking everything, and your repo live on GitHub with green squares.
