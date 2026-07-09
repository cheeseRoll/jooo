"""Pipeline orchestrator.

  python3 scraper/run.py [--days N] [--no-linkedin] [--only SOURCE]

Fetch (ATS watchlist + LinkedIn guest + aggregators) → normalize (done in sources)
→ dedupe against data/jobs.json → prefilter → write data/new_jobs.json, update
data/jobs.json. Never deletes history.
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scraper"))

import prefilter  # noqa: E402
from sources import ats, linkedin_guest, aggregators  # noqa: E402

JOBS_DB = ROOT / "data" / "jobs.json"
NEW_JOBS = ROOT / "data" / "new_jobs.json"
COMPANIES = ROOT / "data" / "companies.yaml"


def load_db() -> dict:
    if JOBS_DB.exists():
        return json.loads(JOBS_DB.read_text())
    return {"jobs": {}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7, help="lookback for search sources")
    ap.add_argument("--no-linkedin", action="store_true")
    ap.add_argument("--only", choices=["ats", "linkedin", "aggregators"])
    args = ap.parse_args()

    raw: list[dict] = []

    if args.only in (None, "ats"):
        companies = []
        if COMPANIES.exists():
            companies = yaml.safe_load(COMPANIES.read_text()).get("companies") or []
        print(f"ATS watchlist: {len(companies)} companies")
        for co in companies:
            got = ats.fetch_company(co)
            if got:
                print(f"  {co['name']}: {len(got)}")
            raw.extend(got)

    if args.only in (None, "linkedin") and not args.no_linkedin:
        print("LinkedIn guest search:")
        raw.extend(linkedin_guest.fetch(days=min(args.days, 7)))

    if args.only in (None, "aggregators"):
        print("Aggregators:")
        raw.extend(aggregators.fetch_all(days=args.days))

    print(f"fetched: {len(raw)} raw postings")

    # cross-source dedupe (same job seen via ATS + LinkedIn + aggregator → keep richest)
    by_id: dict[str, dict] = {}
    for j in raw:
        if not (j["title"] and j["company"] and j["url"]):
            continue
        prev = by_id.get(j["id"])
        if prev is None or len(j["description"]) > len(prev["description"]):
            keep_first = prev["first_seen"] if prev else j["first_seen"]
            by_id[j["id"]] = {**j, "first_seen": keep_first}
    print(f"deduped: {len(by_id)}")

    db = load_db()
    known = db["jobs"]
    fresh = [j for jid, j in by_id.items() if jid not in known]
    print(f"new vs db: {len(fresh)}")

    kept = prefilter.apply(fresh)

    for j in kept:
        known[j["id"]] = j
    db["last_run"] = date.today().isoformat()
    JOBS_DB.parent.mkdir(exist_ok=True)
    JOBS_DB.write_text(json.dumps(db, indent=1, ensure_ascii=False))
    NEW_JOBS.write_text(json.dumps(kept, indent=1, ensure_ascii=False))
    print(f"wrote {len(kept)} new jobs → data/new_jobs.json (db total: {len(known)})")


if __name__ == "__main__":
    main()
