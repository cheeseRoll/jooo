# jooo — Harsh's Job Hunt Machine

Finds Strategic Finance / FP&A / Business Finance roles at **Series B+ startups**
(Bengaluru + on-site abroad, visa-sponsoring preferred), scores each one against
my profile, and manages the application pipeline end to end.

## How it works

```
GitHub Actions (nightly 20:30 IST)          Claude Routine (nightly ~21:30 IST)
┌─────────────────────────────┐             ┌──────────────────────────────────┐
│ scraper/run.py              │   commits   │ scores new jobs vs profile/      │
│  · ATS boards (companies.yaml)│──────────▶│ web-checks unknown companies     │
│  · LinkedIn guest search    │  data/*.json│ builds docs/index.html dashboard │
│  · Adzuna/Jooble/JSearch    │             │ processes "Applied:" issues:     │
└─────────────────────────────┘             │  tracker.xlsx + contacts +       │
                                            │  Gmail cover-letter draft        │
                                            └──────────────────────────────────┘
```

- **Dashboard**: `docs/index.html` (GitHub Pages) — fit score, geo/visa tags, stage,
  freshness, why-it-fits, resume tweaks, direct Apply link.
- **"Mark applied ✓"** on the dashboard opens a prefilled GitHub issue; the nightly
  session turns it into a tracker row + researched contacts + a Gmail draft.
- **Tracker**: `tracker/applications.xlsx`.

## Manual commands

```bash
pip install -r requirements.txt
python3 scraper/run.py                  # full scrape (needs open egress — runs on CI)
python3 scraper/sources/probe.py "Company Name"   # find a company's ATS token
python3 scripts/build_dashboard.py      # rebuild docs/index.html from data/jobs.json
python3 scripts/tracker.py list         # show tracked applications
```

## Secrets (GitHub → Settings → Secrets and variables → Actions)

| Secret | Get it from | Needed for |
|---|---|---|
| `ADZUNA_APP_ID`, `ADZUNA_APP_KEY` | developer.adzuna.com (free) | Indeed-ish coverage IN/SG/GB/US |
| `JOOBLE_KEY` | jooble.org/api/about (free) | broad portal coverage incl. Naukri content |
| `RAPIDAPI_KEY` | rapidapi.com → JSearch (free tier) | Google-for-Jobs coverage |

Without keys, the ATS watchlist + LinkedIn guest still run — keys just widen the net.

See `CLAUDE.md` for the nightly session's runbook and `profile/profile.md` for the
scoring rubric.
