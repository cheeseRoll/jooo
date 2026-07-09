"""Aggregator APIs (cover Indeed/Naukri/portal content indirectly).

All need free keys, read from environment secrets; each source silently skips
when its key is absent so the pipeline degrades gracefully.

  Adzuna : ADZUNA_APP_ID + ADZUNA_APP_KEY   (developer.adzuna.com — free)
  Jooble : JOOBLE_KEY                        (jooble.org/api/about — free)
  JSearch: RAPIDAPI_KEY                      (rapidapi.com JSearch — free tier)
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from normalize import make_job  # noqa: E402
from util import get_json, post_json, strip_html  # noqa: E402

QUERIES = ["FP&A", "strategic finance", "business finance", "financial planning and analysis"]


def adzuna(days: int = 7) -> list[dict]:
    app_id, app_key = os.getenv("ADZUNA_APP_ID"), os.getenv("ADZUNA_APP_KEY")
    if not (app_id and app_key):
        return []
    jobs = []
    # (country_code, where) — India + realistic on-site-abroad markets Adzuna covers
    targets = [("in", "Bangalore"), ("sg", "Singapore"), ("gb", "London"), ("us", "")]
    for cc, where in targets:
        for q in QUERIES:
            data = get_json(
                f"https://api.adzuna.com/v1/api/jobs/{cc}/search/1"
                f"?app_id={app_id}&app_key={app_key}&results_per_page=50"
                f"&what={q.replace(' ', '%20')}&where={where}&max_days_old={days}"
                "&content-type=application/json", min_gap=1.5)
            for j in (data or {}).get("results", []):
                loc = ", ".join((j.get("location") or {}).get("area", [])[::-1][:2])
                sal = j.get("salary_min")
                jobs.append(make_job(
                    title=j.get("title"), company=(j.get("company") or {}).get("display_name"),
                    location=loc, url=j.get("redirect_url"), source="adzuna",
                    posted_at=(j.get("created") or "")[:10] or None,
                    description=strip_html(j.get("description", "")),
                    salary=f"{sal:.0f}+" if sal else None))
    return jobs


def jooble(days: int = 7) -> list[dict]:
    key = os.getenv("JOOBLE_KEY")
    if not key:
        return []
    jobs = []
    for loc in ["Bengaluru", "Dubai", "Singapore"]:
        for q in QUERIES[:2]:
            data = post_json(f"https://jooble.org/api/{key}",
                             {"keywords": q, "location": loc, "datecreatedfrom": f"{days} days"})
            for j in (data or {}).get("jobs", []):
                jobs.append(make_job(
                    title=j.get("title"), company=j.get("company"),
                    location=j.get("location"), url=j.get("link"), source="jooble",
                    posted_at=(j.get("updated") or "")[:10] or None,
                    description=strip_html(j.get("snippet", ""))))
    return jobs


def jsearch(days: int = 7) -> list[dict]:
    key = os.getenv("RAPIDAPI_KEY")
    if not key:
        return []
    import requests
    jobs = []
    searches = [
        "FP&A analyst in Bengaluru", "strategic finance in Bengaluru",
        "FP&A analyst in Dubai", "strategic finance in Singapore",
    ]
    for q in searches:
        try:
            r = requests.get(
                "https://jsearch.p.rapidapi.com/search",
                params={"query": q, "date_posted": "week" if days >= 7 else "3days",
                        "num_pages": 1},
                headers={"X-RapidAPI-Key": key, "X-RapidAPI-Host": "jsearch.p.rapidapi.com"},
                timeout=20)
            data = r.json() if r.status_code == 200 else {}
        except requests.RequestException:
            continue
        for j in data.get("data", []):
            loc = ", ".join(x for x in (j.get("job_city"), j.get("job_country")) if x)
            jobs.append(make_job(
                title=j.get("job_title"), company=j.get("employer_name"),
                location=loc, url=j.get("job_apply_link"), source="jsearch",
                posted_at=(j.get("job_posted_at_datetime_utc") or "")[:10] or None,
                description=strip_html(j.get("job_description", "")),
                remote=bool(j.get("job_is_remote"))))
    return jobs


def fetch_all(days: int = 7) -> list[dict]:
    out = []
    for name, fn in [("adzuna", adzuna), ("jooble", jooble), ("jsearch", jsearch)]:
        try:
            got = fn(days)
        except Exception as e:
            print(f"  ! {name}: {e}")
            got = []
        print(f"  {name}: {len(got)}" + ("" if got else "  (no key or no results)"))
        out.extend(got)
    return out
