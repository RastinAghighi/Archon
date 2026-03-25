import json
import os
from datetime import datetime


class ProfileManager:
    def __init__(self, profile_path="data/profile.json"):
        self.profile_path = profile_path
        with open(profile_path, "r") as f:
            self.profile = json.load(f)

    def get_profile(self):
        return self.profile

    def get_topic(self, topic_id):
        for topic in self.profile["knowledge_graph"]:
            if topic["id"] == topic_id:
                return topic
        return None

    def get_unlocked_topics(self):
        topics_by_id = {t["id"]: t for t in self.profile["knowledge_graph"]}
        unlocked = []

        for topic in self.profile["knowledge_graph"]:
            if topic["confidence"] >= 0.9:
                continue
            prereqs_met = all(
                topics_by_id[p]["confidence"] >= 0.6
                for p in topic["prerequisites"]
                if p in topics_by_id
            )
            if prereqs_met:
                unlocked.append(topic)

        unlocked.sort(key=lambda t: t["confidence"])
        return unlocked

    def get_next_topic(self):
        unlocked = self.get_unlocked_topics()
        return unlocked[0] if unlocked else None

    def update_confidence_from_assessment(self, topic_id, assessment_score):
        topic = self.get_topic(topic_id)
        if topic is None:
            return
        new_confidence = 0.4 * topic["confidence"] + 0.6 * assessment_score
        topic["confidence"] = min(new_confidence, 1.0)
        self.save()

    def apply_time_decay(self):
        for topic in self.profile["knowledge_graph"]:
            if topic["confidence"] > 0.0:
                topic["confidence"] = round(topic["confidence"] * 0.98, 4)
        self.save()

    def mark_episode_completed(self, topic_id, episode_num):
        topic = self.get_topic(topic_id)
        if topic is None:
            return
        if topic["confidence"] < 0.3:
            topic["confidence"] = 0.3
        if "episode_history" not in topic:
            topic["episode_history"] = []
        if episode_num not in topic["episode_history"]:
            topic["episode_history"].append(episode_num)
        self.profile["episodes_completed"] = self.profile.get("episodes_completed", 0) + 1
        self.save()

    def save(self):
        with open(self.profile_path, "w") as f:
            json.dump(self.profile, f, indent=2)

    def get_summary(self):
        learner = self.profile["learner"]
        episodes = self.profile.get("episodes_completed", 0)
        graph = self.profile["knowledge_graph"]

        # Category averages
        categories = {}
        for topic in graph:
            cat = topic["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(topic["confidence"])

        cat_avgs = {
            cat: sum(scores) / len(scores)
            for cat, scores in categories.items()
        }
        sorted_cats = sorted(cat_avgs.items(), key=lambda x: x[1], reverse=True)

        top_3 = [f"{c} ({v:.0%})" for c, v in sorted_cats[:3]]
        weakest = sorted_cats[-1] if sorted_cats else None

        lines = [
            f"Level: {learner['level']}",
            f"Episodes completed: {episodes}",
            f"Strongest: {', '.join(top_3)}",
        ]
        if weakest:
            lines.append(f"Weakest: {weakest[0]} ({weakest[1]:.0%})")

        return " | ".join(lines)


if __name__ == "__main__":
    pm = ProfileManager()

    print("=== Profile Summary ===")
    print(pm.get_summary())
    print()

    next_topic = pm.get_next_topic()
    print(f"Next recommended topic: {next_topic['name'] if next_topic else 'None'}")
    print()

    unlocked = pm.get_unlocked_topics()
    print(f"Currently unlocked topics ({len(unlocked)}):")
    for t in unlocked:
        print(f"  - {t['name']} (confidence: {t['confidence']:.0%})")
    print()

    # Test: mark episode 1 completed and update confidence
    print("=== Test: marking episode 1 completed, assessment score 0.85 ===")
    pm.mark_episode_completed("vectors_and_spaces", 1)
    pm.update_confidence_from_assessment("vectors_and_spaces", 0.85)

    print(f"vectors_and_spaces confidence: {pm.get_topic('vectors_and_spaces')['confidence']:.2f}")
    print()
    print("=== Updated Summary ===")
    print(pm.get_summary())
