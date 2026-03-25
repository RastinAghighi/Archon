import json
import os
from datetime import date, datetime

from src.utils.database import ArchonDB


class AnalyticsEngine:
    def __init__(self):
        self.db = ArchonDB()
        profile_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "profile.json"
        )
        with open(profile_path, "r", encoding="utf-8") as f:
            self.profile = json.load(f)

    def compute_daily_snapshot(self):
        today = str(date.today())
        stats = self.db.get_overall_stats()
        knowledge_graph = self.profile["knowledge_graph"]
        episodes_completed = self.profile["episodes_completed"]
        total_episodes = 165

        completion_percentage = round(episodes_completed / total_episodes * 100, 1)

        # Today's average score
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT AVG(CASE WHEN is_correct = 1 THEN 100.0 ELSE 0.0 END) "
            "FROM assessments WHERE DATE(answered_at) = ?",
            (today,),
        )
        row = cursor.fetchone()
        avg_score_today = round(row[0], 1) if row[0] is not None else 0.0

        # Knowledge coverage: topics with confidence > 0.6
        topics_above = sum(1 for t in knowledge_graph if t["confidence"] > 0.6)
        knowledge_coverage = round(topics_above / len(knowledge_graph) * 100, 1) if knowledge_graph else 0.0

        # Category scores: average confidence per category
        category_totals = {}
        for t in knowledge_graph:
            cat = t["category"]
            if cat not in category_totals:
                category_totals[cat] = {"sum": 0.0, "count": 0}
            category_totals[cat]["sum"] += t["confidence"]
            category_totals[cat]["count"] += 1
        category_scores = {
            cat: round(v["sum"] / v["count"], 2) for cat, v in category_totals.items()
        }

        # Phase progress: completion % per phase
        phase_topics = {}
        for t in knowledge_graph:
            p = t["phase"]
            if p not in phase_topics:
                phase_topics[p] = {"total": 0, "completed": 0}
            phase_topics[p]["total"] += 1
            if t["confidence"] > 0.6:
                phase_topics[p]["completed"] += 1
        phase_progress = {
            f"phase_{p}": round(v["completed"] / v["total"] * 100, 1)
            for p, v in sorted(phase_topics.items())
        }

        # Estimated study hours (45 min per episode)
        total_study_hours = round(episodes_completed * 45 / 60, 1)

        snapshot = {
            "date": today,
            "episodes_completed": episodes_completed,
            "total_episodes": total_episodes,
            "completion_percentage": completion_percentage,
            "streak_days": stats["current_streak"],
            "avg_score_today": avg_score_today,
            "avg_score_overall": stats["avg_score"],
            "knowledge_coverage": knowledge_coverage,
            "category_scores": category_scores,
            "phase_progress": phase_progress,
            "total_study_hours": total_study_hours,
        }

        # Save to database
        self.db.save_analytics_snapshot(snapshot)

        # Save to JSON
        output_dir = os.path.join(os.path.dirname(__file__), "..", "output", "analytics")
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, "latest_snapshot.json"), "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2)

        return snapshot

    def get_score_history(self):
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT a.episode_id, e.generated_at,
                   AVG(CASE WHEN a.is_correct = 1 THEN 100.0 ELSE 0.0 END) as score
            FROM assessments a
            JOIN episodes e ON a.episode_id = e.id
            WHERE a.answered_at IS NOT NULL
            GROUP BY a.episode_id
            ORDER BY a.episode_id
            """
        )
        return [
            {
                "episode_num": row[0],
                "date": row[1],
                "score": round(row[2], 1),
            }
            for row in cursor.fetchall()
        ]

    def get_category_breakdown(self):
        knowledge_graph = self.profile["knowledge_graph"]
        categories = {}
        for t in knowledge_graph:
            cat = t["category"]
            if cat not in categories:
                categories[cat] = {
                    "total_topics": 0,
                    "mastered": 0,
                    "in_progress": 0,
                    "not_started": 0,
                    "confidence_sum": 0.0,
                }
            categories[cat]["total_topics"] += 1
            categories[cat]["confidence_sum"] += t["confidence"]
            if t["confidence"] > 0.8:
                categories[cat]["mastered"] += 1
            elif t["confidence"] > 0.0:
                categories[cat]["in_progress"] += 1
            else:
                categories[cat]["not_started"] += 1

        return {
            cat: {
                "total_topics": v["total_topics"],
                "mastered": v["mastered"],
                "in_progress": v["in_progress"],
                "not_started": v["not_started"],
                "avg_confidence": round(v["confidence_sum"] / v["total_topics"], 2),
            }
            for cat, v in categories.items()
        }

    def generate_public_dashboard_data(self):
        snapshot = self.compute_daily_snapshot()
        score_history = self.get_score_history()
        category_breakdown = self.get_category_breakdown()

        dashboard = {
            "completion_percentage": snapshot["completion_percentage"],
            "streak_days": snapshot["streak_days"],
            "category_breakdown": category_breakdown,
            "score_trend": [
                {"episode_num": s["episode_num"], "score": s["score"]}
                for s in score_history
            ],
            "phase_progress": snapshot["phase_progress"],
            "last_updated": snapshot["date"],
        }

        output_dir = os.path.join(os.path.dirname(__file__), "..", "output", "analytics")
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, "public_dashboard.json"), "w", encoding="utf-8") as f:
            json.dump(dashboard, f, indent=2)

        return dashboard

    def print_summary(self):
        import sys
        snapshot = self.compute_daily_snapshot()
        ep = snapshot["episodes_completed"]
        total = snapshot["total_episodes"]
        pct = snapshot["completion_percentage"]
        streak = snapshot["streak_days"]
        today_score = snapshot["avg_score_today"]
        overall_score = snapshot["avg_score_overall"]
        coverage = snapshot["knowledge_coverage"]

        streak_label = "day" if streak == 1 else "days"

        lines = [
            f"  Episodes: {ep}/{total} ({pct}%)",
            f"  Streak: {streak} {streak_label}",
            f"  Today's Score: {today_score}%",
            f"  Overall Score: {overall_score}%",
            f"  Knowledge Coverage: {coverage}%",
        ]

        width = 38
        out = sys.stdout
        if hasattr(out, "reconfigure"):
            out.reconfigure(encoding="utf-8")
        print(f"\u2554{'\u2550' * width}\u2557")
        print(f"\u2551{'ARCHON \u2014 Daily Summary':^{width}}\u2551")
        print(f"\u2560{'\u2550' * width}\u2563")
        for line in lines:
            print(f"\u2551{line:<{width}}\u2551")
        print(f"\u255a{'\u2550' * width}\u255d")


if __name__ == "__main__":
    engine = AnalyticsEngine()
    engine.compute_daily_snapshot()
    engine.print_summary()
    engine.generate_public_dashboard_data()
    print("\nAnalytics computed successfully")
