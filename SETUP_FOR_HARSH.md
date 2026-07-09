# Your 10-minute setup checklist

Everything else is automated. These four things need a human (you):

## 1. Enable the dashboard (30 sec)
GitHub → this repo → **Settings → Pages** → Deploy from a branch →
branch `claude/job-scraper-finance-kr9ayd`, folder `/docs` → Save.
Your job board: **https://cheeseroll.github.io/jooo/** — bookmark on your phone.

## 2. Create 3 free API keys (~8 min, no credit card)
These widen coverage to Indeed/Naukri/Google-Jobs content. The system works
without them (ATS boards + LinkedIn), but do it once and forget it:

1. **Adzuna** — https://developer.adzuna.com → register → copy App ID + App Key
2. **Jooble** — https://jooble.org/api/about → request key (arrives by email)
3. **JSearch** — https://rapidapi.com → sign up → subscribe to "JSearch" free plan
   → copy your RapidAPI key

Then: repo → **Settings → Secrets and variables → Actions → New repository secret**,
add: `ADZUNA_APP_ID`, `ADZUNA_APP_KEY`, `JOOBLE_KEY`, `RAPIDAPI_KEY`.

## 3. Daily flow (your side, ~15 min/evening)
1. Open the dashboard. Jobs are ranked by fit; badges show BLR / ABROAD+VISA / stage.
2. Read the "Resume tweaks" line, adjust your resume if worth it, hit **Apply ↗**.
3. Click **Mark applied ✓** — it opens a prefilled GitHub issue, just press "Submit".
4. Next morning: the tracker has the row, contacts are researched, and a cover-letter
   draft is sitting in your **Gmail drafts** addressed to the right people. Edit, send.

## 4. Growing the net
Add any company you're curious about to `data/candidates.txt` (format:
`Name | Series B | City`) — the next probe run finds its job board automatically.
Or just tell Claude in a session.
