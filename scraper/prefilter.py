"""Cheap rule filter applied before Claude scoring. Mirrors the hard criteria in
profile/profile.md — role family, location (BLR or abroad on-site, no remote-only),
seniority ceiling."""
import re

TITLE_INCLUDE = [
    "fp&a", "fpna", "fp and a", "fp & a",
    "financial planning", "strategic finance", "strategy and finance", "finance & strategy",
    "business finance", "corporate finance", "finance business partner",
    "finance analyst", "financial analyst", "finance associate", "finance manager",
    "founder's office", "founders office", "founder office",
    "unit economics", "financial model", "financial modelling", "financial modeling",
    "revenue finance", "growth finance", "commercial finance", "finance strategy",
    "investor relations analyst", "corporate development analyst",
]
# titles needing finance evidence in the description too
TITLE_CONDITIONAL = ["chief of staff", "strategy analyst", "business analyst"]
DESC_FINANCE = ["fp&a", "financial model", "3 statement", "three statement", "budget",
                "forecast", "unit economics", "p&l", "cash flow", "variance", "cfo"]

TITLE_EXCLUDE = [
    "accounts payable", "accounts receivable", "payroll", "bookkeep", "tax ",
    "taxation", "audit", "compliance", "company secretary", "kyc", "underwrit",
    "collections", "credit analyst", "loan", "intern", "director", "vice president",
    "vp ", "vp,", "vp-", "head of", "president", "controller", "cfo",
]

BLR = ["bengaluru", "bangalore", "blr"]
INDIA_OTHER = ["mumbai", "delhi", "new delhi", "gurgaon", "gurugram", "noida", "hyderabad",
               "pune", "chennai", "kolkata", "ahmedabad", "jaipur", "kochi", "indore",
               "chandigarh", "india"]  # bare "india" without a BLR city → not targetable

MAX_YEARS = 8
YEARS_RE = re.compile(r"(\d{1,2})\s*(?:\+|-\s*\d{1,2})?\s*(?:years|yrs|y\b)", re.I)


def _title_ok(title: str, desc: str) -> bool:
    t = f" {title.lower()} "
    if any(x in t for x in TITLE_EXCLUDE):
        return False
    if any(x in t for x in TITLE_INCLUDE):
        return True
    if any(x in t for x in TITLE_CONDITIONAL):
        d = desc.lower()
        return sum(k in d for k in DESC_FINANCE) >= 2
    return False


def _location_ok(job: dict) -> bool:
    loc = job["location"].lower()
    if job.get("remote") and not any(b in loc for b in BLR):
        return False  # remote-only, not anchored to BLR
    if not loc:
        return False
    if any(b in loc for b in BLR):
        return True
    if loc.strip() in ("remote", "anywhere", "worldwide"):
        return False
    # India but not Bengaluru → drop; anything else → abroad, keep
    if any(c in loc for c in INDIA_OTHER):
        return False
    return True


def _seniority_ok(job: dict) -> bool:
    d = job["description"]
    if not d:
        return True
    mins = [int(m.group(1)) for m in YEARS_RE.finditer(d) if int(m.group(1)) <= 30]
    # only reject when the SMALLEST years-ask is clearly senior
    return not (mins and min(mins) >= MAX_YEARS)


def keep(job: dict) -> bool:
    return (_title_ok(job["title"], job["description"])
            and _location_ok(job)
            and _seniority_ok(job))


def apply(jobs: list[dict]) -> list[dict]:
    kept = [j for j in jobs if keep(j)]
    print(f"prefilter: {len(jobs)} → {len(kept)}")
    return kept
