import json
import os
import sqlite3
from datetime import date, datetime, timedelta

import yaml


def _load_db_path():
    config_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "config", "settings.yaml"
    )
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config["database"]["path"]


class ArchonDB:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = _load_db_path()

        # Resolve relative paths against project root
        if not os.path.isabs(db_path):
            project_root = os.path.join(os.path.dirname(__file__), "..", "..")
            db_path = os.path.join(project_root, db_path)

        db_path = os.path.normpath(db_path)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS source_fetches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                episode_id INTEGER,
                source_id TEXT,
                url TEXT,
                title TEXT,
                content_hash TEXT,
                was_selected BOOLEAN DEFAULT 0,
                selection_reason TEXT,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                content_expires_at TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id TEXT,
                topic_name TEXT,
                depth TEXT,
                phase INTEGER,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                pdf_path TEXT,
                markdown_path TEXT,
                show_notes_path TEXT,
                github_commit_sha TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                episode_id INTEGER,
                question_text TEXT,
                question_type TEXT,
                correct_answer TEXT,
                user_answer TEXT,
                is_correct BOOLEAN,
                difficulty TEXT,
                topic_tags TEXT,
                answered_at TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                episodes_completed INTEGER,
                streak_days INTEGER,
                avg_score_today REAL,
                avg_score_overall REAL,
                knowledge_coverage REAL,
                category_scores TEXT,
                snapshot_data TEXT
            )
        """)

        self.conn.commit()

    def log_episode(self, topic_id, topic_name, depth, phase, pdf_path, markdown_path):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO episodes (topic_id, topic_name, depth, phase, pdf_path, markdown_path)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (topic_id, topic_name, depth, phase, pdf_path, markdown_path),
        )
        self.conn.commit()
        return cursor.lastrowid

    def log_assessment(
        self, episode_id, question_text, question_type, correct_answer, difficulty, topic_tags
    ):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO assessments (episode_id, question_text, question_type, correct_answer, difficulty, topic_tags)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (episode_id, question_text, question_type, correct_answer, difficulty, topic_tags),
        )
        self.conn.commit()
        return cursor.lastrowid

    def submit_answer(self, assessment_id, user_answer, is_correct):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE assessments
            SET user_answer = ?, is_correct = ?, answered_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (user_answer, is_correct, assessment_id),
        )
        self.conn.commit()

    def get_episode_scores(self, episode_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM assessments WHERE episode_id = ?",
            (episode_id,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_overall_stats(self):
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM episodes")
        total_episodes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM assessments WHERE answered_at IS NOT NULL")
        total_questions = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM assessments WHERE is_correct = 1")
        total_correct = cursor.fetchone()[0]

        avg_score = (total_correct / total_questions * 100) if total_questions > 0 else 0.0

        # Calculate streak: consecutive days (ending today) with at least one episode
        cursor.execute(
            "SELECT DISTINCT DATE(generated_at) as d FROM episodes ORDER BY d DESC"
        )
        days = [row[0] for row in cursor.fetchall()]

        current_streak = 0
        check_date = date.today()
        for d in days:
            if d == str(check_date):
                current_streak += 1
                check_date -= timedelta(days=1)
            else:
                break

        return {
            "total_episodes": total_episodes,
            "total_questions": total_questions,
            "total_correct": total_correct,
            "avg_score": round(avg_score, 1),
            "current_streak": current_streak,
        }

    def save_analytics_snapshot(self, snapshot_data):
        stats = self.get_overall_stats()
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO analytics_snapshots
            (date, episodes_completed, streak_days, avg_score_today, avg_score_overall,
             knowledge_coverage, category_scores, snapshot_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(date.today()),
                stats["total_episodes"],
                stats["current_streak"],
                stats["avg_score"],
                stats["avg_score"],
                0.0,
                None,
                json.dumps(snapshot_data),
            ),
        )
        self.conn.commit()

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    db = ArchonDB()

    # Log a test episode
    episode_id = db.log_episode(
        topic_id="vectors_and_spaces",
        topic_name="Scalars, Vectors, and Vector Spaces",
        depth="intro",
        phase=1,
        pdf_path="output/pdfs/episode_001.pdf",
        markdown_path="output/markdown/episode_001_vectors_and_spaces.md",
    )
    print(f"Logged episode {episode_id}: Scalars, Vectors, and Vector Spaces")

    # Log 3 test assessment questions
    q1 = db.log_assessment(
        episode_id, "What is a vector space?", "short_answer",
        "A set of vectors closed under addition and scalar multiplication",
        "easy", "vectors,linear_algebra",
    )
    q2 = db.log_assessment(
        episode_id, "How many axioms define a vector space?", "multiple_choice",
        "8", "medium", "vectors,linear_algebra",
    )
    q3 = db.log_assessment(
        episode_id, "Write NumPy code to create a 3D unit vector along the x-axis.",
        "code", "np.array([1, 0, 0])", "easy", "vectors,numpy",
    )
    print(f"Logged {3} assessment questions")

    # Submit test answers
    db.submit_answer(q1, "A collection of vectors you can add and scale", True)
    db.submit_answer(q2, "8", True)
    db.submit_answer(q3, "np.array([1, 0, 0])", True)
    print("Submitted test answers")

    # Print overall stats
    stats = db.get_overall_stats()
    print(f"\nOverall Stats:")
    print(f"  Episodes completed: {stats['total_episodes']}")
    print(f"  Questions answered: {stats['total_questions']}")
    print(f"  Correct answers:    {stats['total_correct']}")
    print(f"  Average score:      {stats['avg_score']}%")
    print(f"  Current streak:     {stats['current_streak']} day(s)")

    # Print episode scores
    scores = db.get_episode_scores(episode_id)
    print(f"\nEpisode {episode_id} scores:")
    for s in scores:
        print(f"  Q{s['id']}: {'Correct' if s['is_correct'] else 'Incorrect'} — {s['question_text'][:50]}")

    db.close()
    print("\nDatabase initialized successfully")
