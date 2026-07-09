"""Official public ATS board APIs — the primary source for startup jobs.

Each fetcher takes a company entry from data/companies.yaml:
  {name, ats, token, stage} → list of normalized job dicts.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from normalize import make_job  # noqa: E402
from util import get_json, strip_html  # noqa: E402


def greenhouse(co: dict) -> list[dict]:
    data = get_json(f"https://boards-api.greenhouse.io/v1/boards/{co['token']}/jobs?content=true",
                    min_gap=0.4)
    jobs = []
    for j in (data or {}).get("jobs", []):
        loc = (j.get("location") or {}).get("name", "")
        jobs.append(make_job(
            title=j.get("title"), company=co["name"], location=loc,
            url=j.get("absolute_url"), source="greenhouse",
            posted_at=(j.get("first_published") or j.get("updated_at") or "")[:10] or None,
            description=strip_html(j.get("content", "")),
            remote="remote" in loc.lower(), stage=co.get("stage")))
    return jobs


def lever(co: dict) -> list[dict]:
    data = get_json(f"https://api.lever.co/v0/postings/{co['token']}?mode=json", min_gap=0.4)
    jobs = []
    for j in data or []:
        cats = j.get("categories") or {}
        loc = cats.get("location") or ""
        import datetime
        ts = j.get("createdAt")
        posted = datetime.date.fromtimestamp(ts / 1000).isoformat() if ts else None
        jobs.append(make_job(
            title=j.get("text"), company=co["name"], location=loc,
            url=j.get("hostedUrl"), source="lever", posted_at=posted,
            description=strip_html(j.get("descriptionPlain") or j.get("description", "")),
            remote="remote" in (loc + str(j.get("workplaceType", ""))).lower(),
            stage=co.get("stage")))
    return jobs


def ashby(co: dict) -> list[dict]:
    data = get_json(f"https://api.ashbyhq.com/posting-api/job-board/{co['token']}"
                    "?includeCompensation=true", min_gap=0.4)
    jobs = []
    for j in (data or {}).get("jobs", []):
        loc = j.get("location") or ""
        comp = j.get("compensation") or {}
        salary = (comp.get("compensationTierSummary") or None)
        jobs.append(make_job(
            title=j.get("title"), company=co["name"], location=loc,
            url=j.get("jobUrl") or j.get("applyUrl"), source="ashby",
            posted_at=(j.get("publishedAt") or "")[:10] or None,
            description=strip_html(j.get("descriptionHtml") or j.get("descriptionPlain", "")),
            salary=salary, remote=bool(j.get("isRemote")), stage=co.get("stage")))
    return jobs


def workable(co: dict) -> list[dict]:
    data = get_json(f"https://apply.workable.com/api/v1/widget/accounts/{co['token']}?details=true",
                    min_gap=0.6)
    jobs = []
    for j in (data or {}).get("jobs", []):
        city = j.get("city") or ""
        country = j.get("country") or ""
        loc = ", ".join(x for x in (city, country) if x)
        jobs.append(make_job(
            title=j.get("title"), company=co["name"], location=loc,
            url=j.get("url") or j.get("application_url"), source="workable",
            posted_at=(j.get("published_on") or "")[:10] or None,
            description=strip_html(j.get("description", "")),
            remote=(j.get("telecommuting") is True), stage=co.get("stage")))
    return jobs


def smartrecruiters(co: dict) -> list[dict]:
    data = get_json(f"https://api.smartrecruiters.com/v1/companies/{co['token']}/postings?limit=100",
                    min_gap=0.6)
    jobs = []
    for j in (data or {}).get("content", []):
        locd = j.get("location") or {}
        loc = ", ".join(x for x in (locd.get("city"), locd.get("country")) if x)
        jobs.append(make_job(
            title=j.get("name"), company=co["name"], location=loc,
            url=f"https://jobs.smartrecruiters.com/{co['token']}/{j.get('id')}",
            source="smartrecruiters",
            posted_at=(j.get("releasedDate") or "")[:10] or None,
            description="",  # list endpoint has no description; scorer opens URL if needed
            remote=bool(locd.get("remote")), stage=co.get("stage")))
    return jobs


FETCHERS = {
    "greenhouse": greenhouse,
    "lever": lever,
    "ashby": ashby,
    "workable": workable,
    "smartrecruiters": smartrecruiters,
}


def fetch_company(co: dict) -> list[dict]:
    fn = FETCHERS.get(co.get("ats"))
    if not fn or not co.get("token"):
        return []
    try:
        return fn(co)
    except Exception as e:  # one bad board must never kill the run
        print(f"  ! {co['name']} ({co.get('ats')}): {e}")
        return []
