# jooo — Job Hunt Machine for Harsh Belde

A nightly pipeline that finds Strategic Finance / FP&A / Business Finance roles at
**Series B+ startups** in **Bengaluru or on-site abroad** (visa-sponsoring preferred,
no remote), scores them against `profile/profile.md`, publishes a dashboard, and manages
the application tracker + cover-mail drafts.

## Nightly pipeline (what the Routine session must do, in order)

1. **Pull latest**: `git pull origin claude/job-scraper-finance-kr9ayd` (or main once merged).
2. **Scraping happens on GitHub Actions, not here** — this environment's network policy
   blocks the ATS/job-board hosts. The `scrape` workflow (`.github/workflows/scrape.yml`,
   nightly cron 15:00 UTC) runs `scraper/run.py` on a GitHub runner and commits
   `data/jobs.json` + `data/new_jobs.json`. In this session: pull and check
   `data/jobs.json`'s `last_run`. If stale (> 1 day), trigger the workflow via the
   github MCP `actions_run_trigger` tool, wait for it to finish, pull again.
3. **Score** (you, the session, are the scorer — no external API):
   - Read `profile/profile.md` (rubric) and `profile/resume_master.md`.
   - For each job in `data/new_jobs.json`: apply the rubric. Web-search companies whose
     stage/quality you don't know (query: "<company> funding series"). **Series A or
     younger → cap score at 45 and tag TOO_EARLY** (Harsh wants Series B minimum).
   - Roles asking for financial modelling / 3-statement modelling are a fit bonus.
   - Write results to `data/scores/YYYY-MM-DD.json` matching the schema in
     `scripts/score_schema.json`, then run `python3 scripts/merge_scores.py` to fold
     scores into `data/jobs.json`.
4. **Process "Applied" feedback**:
   - List open GitHub issues in this repo titled `Applied: <job_id>` (github MCP tools).
   - For each: run `python3 scripts/tracker.py mark-applied <job_id>`, then research
     2–3 best contacts (CFO / Head of Finance / founder / recruiter) via web search —
     names, roles, emails (label pattern-guesses as such), LinkedIn URLs.
   - Write a cover letter (voice rules at the bottom of `profile/profile.md`), create a
     **Gmail draft** (Gmail MCP `create_draft`) addressed to the contacts.
   - Record contacts + status "draft created" via
     `python3 scripts/tracker.py set-contacts <job_id> ...`, close the issue with a short
     comment.
5. **Build dashboard**: `python3 scripts/build_dashboard.py` → `docs/index.html`.
   Re-publish per `docs/HOSTING.md`.
6. **Commit & push** everything (`data/`, `docs/`, `tracker/`) to the working branch.
   Push with retries (2s/4s/8s/16s backoff on network errors).
7. **Notify**: push notification with a one-line summary, e.g.
   "12 new jobs · 3 scored 80+ · top: Strategic Finance Associate @ X (BLR)".

## Weekly (Sundays)

- Discover newly funded Series B+ startups (web search: "Series B funding announced India",
  Dubai/Singapore/SEA equivalents), probe their ATS (see `scraper/sources/probe.py`),
  append to `data/companies.yaml`.

## Rules

- Never fabricate resume/cover-letter content. Tailoring = wording & emphasis only.
- Never auto-submit applications. Harsh applies himself; the system removes friction.
- API keys live in environment secrets (ADZUNA_APP_ID, ADZUNA_APP_KEY, JOOBLE_KEY,
  RAPIDAPI_KEY). Never commit keys.
- Be polite to endpoints: the scraper already rate-limits; don't hammer manually.
- `data/jobs.json` is append-only history; never delete records (statuses change instead).

## Repo map

- `profile/` — who Harsh is, what he wants, scoring rubric (read first, always)
- `scraper/` — source modules + pipeline (`run.py` is the entry point)
- `data/companies.yaml` — ATS watchlist (the crown jewel; grows weekly)
- `data/jobs.json` — all jobs ever seen, with status + scores
- `scripts/` — dashboard builder, tracker CLI, score merging
- `docs/index.html` — the dashboard (static, self-contained)
- `tracker/applications.xlsx` — Harsh's application tracker
