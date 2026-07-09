"""Single Job schema shared by every source.

Job dict fields:
  id           sha1(company|title|location)[:16] — stable across sources/days
  title, company, location  strings
  url          direct application/posting URL
  posted_at    ISO date string or None
  description  plain text, truncated
  source       e.g. "greenhouse", "linkedin", "adzuna"
  salary       string or None
  remote       bool — remote-only posting
  stage        funding stage from companies.yaml if known (else None)
  geo_tag / fit_score / band / why / resume_tips / red_flags  — filled by scorer
  status       new -> scored -> applied / rejected / expired
  first_seen   ISO date
"""
import hashlib
import re
from datetime import date


def norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", (t or "").lower()).strip()


def job_id(company: str, title: str, location: str) -> str:
    key = f"{(company or '').lower().strip()}|{norm_title(title)}|{(location or '').lower().strip()[:24]}"
    return hashlib.sha1(key.encode()).hexdigest()[:16]


def make_job(*, title, company, location, url, source, posted_at=None,
             description="", salary=None, remote=False, stage=None) -> dict:
    return {
        "id": job_id(company, title, location),
        "title": (title or "").strip(),
        "company": (company or "").strip(),
        "location": (location or "").strip(),
        "url": url,
        "posted_at": posted_at,
        "description": description or "",
        "source": source,
        "salary": salary,
        "remote": bool(remote),
        "stage": stage,
        "status": "new",
        "first_seen": date.today().isoformat(),
    }
