import subprocess
import os
from datetime import datetime, timedelta


def _run_git(args):
    """Run a git command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            cwd=os.path.join(os.path.dirname(__file__), ".."),
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except FileNotFoundError:
        return 1, "", "git not found"


def git_push_episode(episode_num, topic_name, files_to_add=None):
    if files_to_add is None:
        files_to_add = [
            "output/pdfs/",
            "output/markdown/",
            "output/assessments/",
            "output/show_notes/",
            "output/analytics/",
            "data/profile.json",
        ]

    # Stage files
    for path in files_to_add:
        code, out, err = _run_git(["add", path])
        if code != 0:
            print(f"Warning: git add {path} failed: {err}")

    # Commit
    commit_message = f"Episode {episode_num}: {topic_name}"
    code, out, err = _run_git(["commit", "-m", commit_message])
    if code != 0:
        print(f"Git commit failed: {err}")
        return {"success": False, "commit_sha": None, "message": commit_message}

    # Get commit SHA
    code, sha, err = _run_git(["rev-parse", "HEAD"])
    if code != 0:
        sha = "unknown"

    # Push
    code, out, err = _run_git(["push"])
    if code != 0:
        print(f"Git push failed: {err}")
        return {"success": False, "commit_sha": sha, "message": commit_message}

    print(f"\U0001f4e4 Pushed to GitHub: Episode {episode_num}: {topic_name}")
    print(f"   Commit: {sha[:8]}")
    return {"success": True, "commit_sha": sha, "message": commit_message}


def check_git_status():
    # Get branch name
    code, branch, _ = _run_git(["branch", "--show-current"])
    if code != 0:
        branch = "unknown"

    # Get status
    code, status_output, _ = _run_git(["status", "--porcelain"])
    modified_files = [line.strip() for line in status_output.splitlines() if line.strip()]
    clean = len(modified_files) == 0

    return {"branch": branch, "clean": clean, "modified_files": modified_files}


def get_streak_count():
    code, log_output, _ = _run_git(["log", "--format=%ad", "--date=short"])
    if code != 0 or not log_output:
        print("\U0001f525 GitHub streak: 0 days")
        return 0

    # Get unique commit dates
    commit_dates = sorted(set(log_output.splitlines()), reverse=True)

    # Count consecutive days backwards from today
    today = datetime.now().date()
    streak = 0
    check_date = today

    for date_str in commit_dates:
        try:
            commit_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            continue

        if commit_date == check_date:
            streak += 1
            check_date -= timedelta(days=1)
        elif commit_date < check_date:
            break

    print(f"\U0001f525 GitHub streak: {streak} days")
    return streak


if __name__ == "__main__":
    status = check_git_status()
    print(f"Branch: {status['branch']}")
    print(f"Clean: {status['clean']}")
    if status["modified_files"]:
        print("Modified files:")
        for f in status["modified_files"]:
            print(f"  {f}")

    print()
    get_streak_count()

    print("\nGitHub uploader ready. Use git_push_episode() to push.")
