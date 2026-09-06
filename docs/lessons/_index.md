---
id: yt-metrics-cli-lessons-index
type: index
status: active
created: "2026-09-06"
owner: manu
tags: [yt-metrics-cli, lessons, index]
---

# Lessons Learned Index

Post-mortems, gotchas and patterns discovered while building yt-metrics-cli. One file per lesson, numbered in the order they were learned; `scripts/check-lessons.sh` guards the numbering and this index.

| # | Date | Title | File | Tags |
|---|---|---|---|---|
| 001 | 2026-03-04 | Starlight 0.37 + Astro 5 Requires Explicit content.config.ts | [lesson-001-starlight-0-37-astro-5-requires-explicit-content-c.md](lesson-001-starlight-0-37-astro-5-requires-explicit-content-c.md) | `astro`, `starlight`, `docs`, `silent-failure` |
| 002 | 2026-03-04 | GitHub Pages Workflow Path Scoping Prevents Unnecessary Deploys | [lesson-002-github-pages-workflow-path-scoping-prevents-unnece.md](lesson-002-github-pages-workflow-path-scoping-prevents-unnece.md) | `ci`, `github-actions`, `github-pages`, `optimization` |
| 003 | 2026-03-14 | Video ID Input Validation to Prevent Path Traversal | [lesson-003-video-id-input-validation-to-prevent-path-traversa.md](lesson-003-video-id-input-validation-to-prevent-path-traversa.md) | `security`, `input-validation`, `path-traversal` |
| 004 | 2026-03-14 | Replace assert with Explicit ValueError for Control Flow | [lesson-004-replace-assert-with-explicit-valueerror-for-contro.md](lesson-004-replace-assert-with-explicit-valueerror-for-contro.md) | `python`, `clean-code`, `assert-antipattern` |
| 005 | 2026-03-14 | Session Close-Out Workflow: Memory + Docs + Vault + PR | [lesson-005-session-close-out-workflow-memory-docs-vault-pr.md](lesson-005-session-close-out-workflow-memory-docs-vault-pr.md) | `workflow`, `knowledge-management`, `session-hygiene` |
| 006 | 2026-03-14 | ANSI Color Codes in Typer/Rich CLI Test Output Break Assertions | [lesson-006-ansi-color-codes-in-typer-rich-cli-test-output-bre.md](lesson-006-ansi-color-codes-in-typer-rich-cli-test-output-bre.md) | `testing`, `cli`, `typer`, `rich`, `ansi` |
| 007 | 2026-03-14 | Mismatched Secret Name Between Workflow YAML and GitHub Repo | [lesson-007-mismatched-secret-name-between-workflow-yaml-and-g.md](lesson-007-mismatched-secret-name-between-workflow-yaml-and-g.md) | `ci`, `github-actions`, `secrets`, `silent-failure` |
| 008 | 2026-03-14 | release-please First Run Fails Expectedly on Fresh Repos | [lesson-008-release-please-first-run-fails-expectedly-on-fresh.md](lesson-008-release-please-first-run-fails-expectedly-on-fresh.md) | `ci`, `release-please`, `gotcha` |
| 009 | 2026-06-28 | GraphQL Rate Limits Block Board Operations — Use REST Fallback | [lesson-009-graphql-rate-limits-block-board-operations-use-res.md](lesson-009-graphql-rate-limits-block-board-operations-use-res.md) | `github`, `graphql`, `rate-limit`, `bitacora`, `gotcha` |
| 010 | 2026-06-28 | `gh project item-add` Can Silently Succeed Without Persisting | [lesson-010-gh-project-item-add-can-silently-succeed-without-p.md](lesson-010-gh-project-item-add-can-silently-succeed-without-p.md) | `github`, `graphql`, `bitacora`, `silent-failure` |
