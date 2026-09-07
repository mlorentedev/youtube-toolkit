---
id: lesson-008-release-please-first-run-fails-expectedly-on-fresh
type: lesson
status: active
created: "2026-03-14"
owner: manu
tags: [yt-metrics-cli, lesson, ci, release-please, gotcha]
---

# release-please First Run Fails Expectedly on Fresh Repos

**Context:** Phase 4 release pipeline — first master push after adding release workflow
**Problem:** Release workflow failed in 7s on first master push. CI passed on same push. Appeared broken but was expected behavior.
**Solution:** No code fix needed. release-please needs the token secret and pypi environment configured before it can succeed. First run always fails until manual setup is completed.
**Why:** release-please requires prior release history or bootstrap configuration to create its first Release PR. The first workflow run on a fresh repo will always fail. Document this expectation in the PR body so the failure isn't mistaken for a bug.
**Tags:** `#ci` `#release-please` `#gotcha`
