"""Fold data/scores/*.json into data/jobs.json (status new → scored).

  python3 scripts/merge_scores.py [scores-file]   # default: newest file in data/scores/
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JOBS_DB = ROOT / "data" / "jobs.json"
SCORES_DIR = ROOT / "data" / "scores"

SCORE_FIELDS = ["fit_score", "band", "geo_tag", "stage", "why", "resume_tips", "red_flags"]


def main():
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
    else:
        files = sorted(SCORES_DIR.glob("*.json"))
        if not files:
            sys.exit("no score files in data/scores/")
        path = files[-1]

    scores = json.loads(path.read_text())
    db = json.loads(JOBS_DB.read_text())
    jobs = db["jobs"]

    merged = missing = 0
    for s in scores:
        job = jobs.get(s["id"])
        if job is None:
            missing += 1
            continue
        for f in SCORE_FIELDS:
            if f in s:
                job[f] = s[f]
        if job.get("status") == "new":
            job["status"] = "scored"
        merged += 1

    JOBS_DB.write_text(json.dumps(db, indent=1, ensure_ascii=False))
    print(f"merged {merged} scores from {path.name}" + (f", {missing} ids not in db" if missing else ""))


if __name__ == "__main__":
    main()
