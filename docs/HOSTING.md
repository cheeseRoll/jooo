# Dashboard hosting

The repo is **public**, so GitHub Pages serves `docs/index.html` for free.

## One-time setup (Harsh, ~30 seconds)

GitHub → `cheeseRoll/jooo` → **Settings → Pages** →
Source: *Deploy from a branch* → Branch: `claude/job-scraper-finance-kr9ayd`
(switch to `main` after merge), folder **`/docs`** → Save.

Dashboard URL: **https://cheeseroll.github.io/jooo/**
Bookmark it on your phone. It updates automatically every night when the
pipeline commits a new `docs/index.html`.

## Note for the nightly session

Nothing to do here — Pages redeploys on every push to the configured branch.
If Pages is not yet enabled (URL 404s), publish `docs/index.html` as a Claude
Artifact as a stopgap and remind Harsh to enable Pages.
