---
id: lesson-007-mismatched-secret-name-between-workflow-yaml-and-g
type: lesson
status: active
created: "2026-03-14"
owner: manu
tags: [yt-metrics-cli, lesson, ci, github-actions, secrets, silent-failure]
---

# Mismatched Secret Name Between Workflow YAML and GitHub Repo

**Context:** Phase 4 release pipeline — release-please workflow failing to authenticate
**Problem:** Workflow referenced `secrets.RELEASE_PLEASE_TOKEN` but the actual GitHub repo secret was named `RELEASE_TOKEN`. Single-character difference caused silent authentication failure.
**Solution:** Changed workflow from `secrets.RELEASE_PLEASE_TOKEN` to `secrets.RELEASE_TOKEN`.
**Why:** Secret name mismatches between workflow YAML and GitHub repo settings are silent failures — the workflow gets an empty string, not an error. Always verify secret names match exactly by checking both the workflow file and the GitHub repo settings page.
**Tags:** `#ci` `#github-actions` `#secrets` `#silent-failure`
