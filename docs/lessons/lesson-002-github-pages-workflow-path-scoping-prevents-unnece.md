---
id: lesson-002-github-pages-workflow-path-scoping-prevents-unnece
type: lesson
status: active
created: "2026-03-04"
owner: manu
tags: [yt-metrics-cli, lesson, ci, github-actions, github-pages, optimization]
---

# GitHub Pages Workflow Path Scoping Prevents Unnecessary Deploys

**Context:** Configuring GitHub Pages deployment for the Starlight documentation site
**Problem:** Without path filtering, every push to master triggers a docs rebuild — even for source code, test, or config changes that don't affect the site.
**Solution:** Added `paths: ['site/**']` filter to the push trigger in `pages.yml`. Added `workflow_dispatch` for manual re-deploys. Set `concurrency` group with `cancel-in-progress: true`.
**Why:** Path-scoped workflows prevent wasted CI minutes and unnecessary deploys. The concurrency group ensures in-progress builds are cancelled when newer commits arrive, keeping the deployed site always reflecting the latest push.
**Tags:** `#ci` `#github-actions` `#github-pages` `#optimization`
