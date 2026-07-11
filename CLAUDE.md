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
4. **Process "Applied" and "Mailed" feedback** (open GitHub issues, github MCP tools):
   - Issues titled `Applied: <job_id>`: run `python3 scripts/tracker.py mark-applied
     <job_id>`, then research 2–3 best contacts (CFO / Head of Finance / founder /
     recruiter) via web search — names, roles, emails (label pattern-guesses as such),
     LinkedIn URLs. Write a cover letter (voice rules at the bottom of
     `profile/profile.md`), create a **Gmail draft** (Gmail MCP `create_draft`)
     addressed to the contacts. Record contacts via `python3 scripts/tracker.py
     set-contacts <job_id> ...`, close the issue with a short comment.
   - Issues titled `Mailed: <job_id>` (Harsh sent the cover mail): run
     `python3 scripts/tracker.py mark-mailed <job_id>`, close the issue silently.
   - **Mail sweep (since 2026-07-11)**: Harsh does all job mail from
     `harshbelde3@gmail.com` and the Gmail connector reads that account
     (re-linked 2026-07-11). If a session ever finds the connector back on
     `harshbelde@gmail.com`, flag it in the summary and fall back to searching
     `from:harshbelde3@gmail.com newer_than:7d` + `mark-mailed`. Run three
     sweeps (Gmail MCP `search_threads`; log each hit with `python3
     scripts/tracker.py log-mail <job_id> --dir in|out|ack|bounce --who "<addr>"
     --subject "..." --date YYYY-MM-DD`; status bumps: out → mailed, in →
     response; ack/bounce only log, bounce also flags the xlsx row "resend!"):
     1. **Sent**: `in:sent newer_than:7d` — match cover mails to tracker jobs by
        recipient domain / company name / subject → `log-mail --dir out`. A
        cover mail to a scored-but-untracked jobs.json job means Harsh applied:
        `mark-applied` first (fix `applied_on` if the mail shows an earlier date).
     2. **Inbox**: `in:inbox newer_than:7d` — mail from domains of recorded
        contacts or companies of applied jobs: human replies → `log-mail --dir
        in`; automated application-received mails (Lever/Greenhouse/etc.) →
        `--dir ack`; delivery failures (mailer-daemon) → `--dir bounce` and
        call the bounce out in the summary so Harsh resends.
     3. **LinkedIn**: `from:linkedin.com newer_than:7d` — "your application was
        sent to <Company>": if that job isn't tracked, `tracker.py mark-applied
        <job_id>` (match company + role to data/jobs.json), then `log-mail
        --dir ack` for the confirmation; recruiter InMail / real messages →
        `--dir in`. Ignore job alerts, invitations, profile-view digests.
     This replaces `Mailed:` issues for most cases. Any application mail that
     matches no jobs.json row (e.g. a company we never scraped) goes in the
     session summary — never guess a match, never invent a jobs.json record.
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
