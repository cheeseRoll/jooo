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

Pages redeploys on every push to the configured branch — nothing to do once enabled.

Until Harsh enables Pages, the dashboard is published as a Claude Artifact at
**https://claude.ai/code/artifact/d747e32a-644a-479b-98b8-28385caabd16** — after
rebuilding `docs/index.html`, strip the outer `<html>/<head>/<body>` shell (keep
`<title>` + `<style>` + body content) and re-publish via the Artifact tool with
`url` set to that address so the link stays stable. Stop re-publishing once
Pages is live (check https://cheeseroll.github.io/jooo/).
