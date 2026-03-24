import json
import os
import re
import yaml
from datetime import datetime

from src.utils.claude_client import call_claude
from src.utils.database import ArchonDB


ASSESSMENT_PROMPT = """You are a quiz generator for an AI/ML learning system. Given a study document, generate assessment questions to test the learner's understanding.

Generate exactly 7 questions in this mix:
- 3 multiple choice questions (4 options each, one correct)
- 2 short answer questions
- 1 conceptual question (explain in your own words)
- 1 code challenge (write or complete a short code snippet)

RULES:
- Questions should test understanding, not memorization
- Include at least one question about mathematical concepts if the episode covers math
- Include at least one question that connects this topic to the bigger picture of AI/ML
- Code challenges should be completable in 5-10 lines
- Difficulty mix: 2 easy, 3 medium, 2 hard

Respond in ONLY valid JSON (no markdown, no backticks, no preamble):
{
  "questions": [
    {
      "question": "...",
      "type": "multiple_choice",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct_answer": "B",
      "explanation": "...",
      "difficulty": "easy",
      "topic_tags": ["vectors", "linear_algebra"]
    },
    {
      "question": "...",
      "type": "short_answer",
      "correct_answer": "...",
      "explanation": "...",
      "difficulty": "medium",
      "topic_tags": ["..."]
    },
    {
      "question": "...",
      "type": "code_challenge",
      "correct_answer": "```python\\n...\\n```",
      "explanation": "...",
      "difficulty": "hard",
      "topic_tags": ["..."]
    }
  ]
}
"""


def generate_assessment(episode_markdown, episode_num, topic_name):
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "settings.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    model = config["models"]["assessment_generator"]

    user_prompt = (
        f"Generate assessment questions for Episode {episode_num}: {topic_name}\n\n"
        f"Study material:\n{episode_markdown[:3000]}"
    )

    result = call_claude(
        model=model,
        system_prompt=ASSESSMENT_PROMPT,
        user_prompt=user_prompt,
        max_tokens=2000,
    )

    if not result:
        print("Assessment generation failed — no response from API.")
        return None

    # Strip markdown backtick wrapping if present
    cleaned = result.strip()
    cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
    cleaned = re.sub(r'\s*```$', '', cleaned)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"Failed to parse assessment JSON: {e}")
        print(f"Raw response:\n{result[:500]}")
        return None

    questions = data.get("questions", [])

    # Save to file
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output", "assessments")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"episode_{episode_num:03d}_assessment.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Log to database
    db = ArchonDB()
    for q in questions:
        db.log_assessment(
            episode_id=episode_num,
            question_text=q["question"],
            question_type=q["type"],
            correct_answer=q.get("correct_answer", ""),
            difficulty=q.get("difficulty", "medium"),
            topic_tags=",".join(q.get("topic_tags", [])),
        )
    db.close()

    print(f"Assessment generated: {len(questions)} questions for Episode {episode_num}")
    return questions


def take_assessment(episode_num):
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output", "assessments")
    path = os.path.join(output_dir, f"episode_{episode_num:03d}_assessment.json")

    if not os.path.exists(path):
        print(f"No assessment found for Episode {episode_num}.")
        return 0.0

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    questions = data.get("questions", [])
    if not questions:
        print("Assessment file contains no questions.")
        return 0.0

    # Get assessment IDs from database
    db = ArchonDB()
    db_rows = db.get_episode_scores(episode_num)
    # Map question text to assessment id
    id_map = {}
    for row in db_rows:
        if row["user_answer"] is None:
            id_map.setdefault(row["question_text"], row["id"])

    correct = 0
    total = len(questions)

    for i, q in enumerate(questions, 1):
        print(f"\n{'='*60}")
        print(f"Question {i}/{total} [{q.get('difficulty', '?').upper()}] ({q['type']})")
        print(f"{'='*60}")
        print(f"\n{q['question']}\n")

        if q["type"] == "multiple_choice" and "options" in q:
            for opt in q["options"]:
                print(f"  {opt}")
            print()

        user_answer = input("Your answer: ").strip()

        if q["type"] == "multiple_choice":
            correct_letter = q.get("correct_answer", "").strip().upper()
            user_letter = user_answer[:1].upper()
            is_correct = user_letter == correct_letter
            if is_correct:
                print("Correct!")
                correct += 1
            else:
                print(f"Incorrect. The correct answer is: {correct_letter}")
            print(f"Explanation: {q.get('explanation', '')}")
        else:
            print(f"\nCorrect answer: {q.get('correct_answer', 'N/A')}")
            print(f"Explanation: {q.get('explanation', '')}")
            grade = input("\nDid you get it right? (y/n): ").strip().lower()
            is_correct = grade == "y"
            if is_correct:
                correct += 1

        # Update database
        assessment_id = id_map.get(q["question"])
        if assessment_id:
            db.submit_answer(assessment_id, user_answer, is_correct)

    db.close()

    percentage = (correct / total * 100) if total > 0 else 0
    print(f"\n{'='*60}")
    print(f"You scored {correct}/{total} ({percentage:.0f}%)")
    print(f"{'='*60}")

    return correct / total if total > 0 else 0.0


if __name__ == "__main__":
    md_dir = os.path.join(os.path.dirname(__file__), "..", "output", "markdown")

    md_content = None
    if os.path.isdir(md_dir):
        md_files = sorted(f for f in os.listdir(md_dir) if f.endswith(".md"))
        if md_files:
            with open(os.path.join(md_dir, md_files[0]), "r", encoding="utf-8") as f:
                md_content = f.read()

    if not md_content:
        print("No episode markdown found in output/markdown/. Generate an episode first.")
    else:
        questions = generate_assessment(md_content, episode_num=1, topic_name="Scalars, Vectors, and Vector Spaces")

        if questions:
            print(f"\n{'='*60}")
            print("ASSESSMENT PREVIEW")
            print(f"{'='*60}")
            for i, q in enumerate(questions, 1):
                print(f"\n{i}. [{q.get('difficulty', '?').upper()}] ({q['type']})")
                print(f"   {q['question']}")
                if q["type"] == "multiple_choice" and "options" in q:
                    for opt in q["options"]:
                        print(f"      {opt}")

            choice = input("\nWould you like to take the assessment now? (y/n): ").strip().lower()
            if choice == "y":
                take_assessment(1)
