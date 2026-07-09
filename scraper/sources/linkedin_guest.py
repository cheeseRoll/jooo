"""LinkedIn guest jobs endpoint — no login, returns HTML cards for a search query.

Polite by design: few queries, ~2s gaps, last-24h/week windows only. This is the
wide-net complement to the ATS watchlist (catches companies we don't track yet).
"""
import re
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from normalize import make_job  # noqa: E402
from util import get, strip_html  # noqa: E402

BASE = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

# (keywords, location, geoId) — geoId pins LinkedIn's location disambiguation
SEARCHES = [
    ("strategic finance", "Bengaluru, Karnataka, India", "105214831"),
    ("FP&A analyst", "Bengaluru, Karnataka, India", "105214831"),
    ("business finance", "Bengaluru, Karnataka, India", "105214831"),
    ("financial planning analysis", "Bengaluru, Karnataka, India", "105214831"),
    ("corporate finance startup", "Bengaluru, Karnataka, India", "105214831"),
    ("FP&A analyst", "United Arab Emirates", "104305776"),
    ("strategic finance", "United Arab Emirates", "104305776"),
    ("FP&A analyst", "Singapore", "102454443"),
    ("strategic finance", "Singapore", "102454443"),
]

CARD = re.compile(
    r'<div class="base-search-card[^"]*".*?'
    r'<h3 class="base-search-card__title">\s*(?P<title>.*?)\s*</h3>.*?'
    r'<h4 class="base-search-card__subtitle">.*?>(?P<company>[^<]+)<.*?'
    r'<span class="job-search-card__location">\s*(?P<location>[^<]+?)\s*</span>'
    r'(?:.*?datetime="(?P<date>\d{4}-\d{2}-\d{2})")?',
    re.S)
LINK = re.compile(r'<a class="base-card__full-link[^"]*"\s+href="([^"]+)"')


def _search(keywords: str, location: str, geo_id: str, days: int) -> list[dict]:
    q = urllib.parse.urlencode({
        "keywords": keywords, "location": location, "geoId": geo_id,
        "f_TPR": f"r{days * 86400}", "start": 0,
    })
    r = get(f"{BASE}?{q}", min_gap=2.5)
    if r is None:
        return []
    html_text = r.text
    links = LINK.findall(html_text)
    jobs = []
    for i, m in enumerate(CARD.finditer(html_text)):
        url = links[i].split("?")[0] if i < len(links) else None
        if not url:
            continue
        loc = strip_html(m["location"], 80)
        jobs.append(make_job(
            title=strip_html(m["title"], 120), company=strip_html(m["company"], 80),
            location=loc, url=url, source="linkedin",
            posted_at=m["date"], description="",
            remote="remote" in loc.lower()))
    return jobs


def fetch(days: int = 2) -> list[dict]:
    out = []
    for kw, loc, geo in SEARCHES:
        got = _search(kw, loc, geo, days)
        print(f"  linkedin: '{kw}' @ {loc.split(',')[0]}: {len(got)}")
        out.extend(got)
    return out
