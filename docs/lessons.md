---
id: "youtube-toolkit-lessons"
type: lesson
status: active
tags: [youtube-toolkit, lessons]
created: "2026-03-13"
owner: manu
---

# youtube-toolkit: Lessons Learned

> Post-mortems, gotchas, and patterns discovered during development.

## Lessons

### [2026-03-14] Video ID Input Validation to Prevent Path Traversal
**Context:** Phase 6 security audit of transcript.py
**Problem:** `video_id` was used directly in file paths (`f"{video_id}_transcript.txt"`) and API calls without format validation. A malicious ID containing `../` could traverse directories when writing transcript files.
**Solution:** Added `_validate_video_id()` static method with regex `^[a-zA-Z0-9_-]{1,20}$` called at the start of `get_transcript()`, before any file or API operation.
**Why:** Any user-supplied string used in file path construction must be validated against an allowlist pattern. Defense-in-depth — even if the caller sanitizes, the callee should enforce its own contract.
**Tags:** `#security` `#input-validation` `#path-traversal`

### [2026-03-14] Replace assert with Explicit ValueError for Control Flow
**Context:** Phase 6 clean code audit found `assert channel_id is not None` in `analyzer.py:get_channel_videos()`
**Problem:** `assert` statements are stripped when Python runs with the `-O` (optimize) flag, making the guard silently disappear in production. The assert was used for mypy type narrowing, not as a test assertion.
**Solution:** Replaced with `if channel_id is None: raise ValueError("Could not resolve channel ID from provided identifiers")`.
**Why:** `assert` is for development-time invariant checking, not runtime control flow. Code that depends on asserts for correctness breaks under `-O`. Use explicit `if/raise` for any guard that must always execute.
**Tags:** `#python` `#clean-code` `#assert-antipattern`

### [2026-03-14] Session Close-Out Workflow: Memory + Docs + Vault + PR
**Context:** End of the maturation sprint — needed to ensure all knowledge artifacts stayed in sync.
**Problem:** Without a structured close-out, documentation, vault notes, and memory drift from actual code state. The Starlight site and CLAUDE.md were already stale by session end.
**Solution:** Established a session-end checklist: (1) update Claude-Mem memory, (2) update repo docs (CLAUDE.md, site), (3) sync Obsidian vault context note, (4) open PR if any files changed.
**Why:** Knowledge artifacts decay fastest right after code changes. Batching updates at session end catches drift before it compounds across sessions.
**Tags:** `#workflow` `#knowledge-management` `#session-hygiene`

### [2026-03-14] ANSI Color Codes in Typer/Rich CLI Test Output Break Assertions
**Context:** Phase 3 CI pipeline — CLI help tests failing on GitHub Actions
**Problem:** Tests asserting `'--channels' in result.output` failed because Typer/Rich renders ANSI escape codes (e.g., `\x1b[1;36m-\x1b[0m\x1b[1;36m-channels\x1b[0m`) that split option flag strings. Both Python 3.12 and 3.13 affected — not version-specific.
**Solution:** Added `_strip_ansi(text: str) -> str` helper using `re.sub(r"\x1b\[[0-9;]*m", "", text)` to strip ANSI codes before assertions. Applied to `test_channels_help` and `test_transcript_help`.
**Why:** Typer uses Rich for styled terminal output. CliRunner captures raw output including ANSI sequences. Any test asserting plain text substrings in CLI help output will break. Either strip ANSI before assertions or disable color in the test runner.
**Tags:** `#testing` `#cli` `#typer` `#rich` `#ansi`

### [2026-03-14] Mismatched Secret Name Between Workflow YAML and GitHub Repo
**Context:** Phase 4 release pipeline — release-please workflow failing to authenticate
**Problem:** Workflow referenced `secrets.RELEASE_PLEASE_TOKEN` but the actual GitHub repo secret was named `RELEASE_TOKEN`. Single-character difference caused silent authentication failure.
**Solution:** Changed workflow from `secrets.RELEASE_PLEASE_TOKEN` to `secrets.RELEASE_TOKEN`.
**Why:** Secret name mismatches between workflow YAML and GitHub repo settings are silent failures — the workflow gets an empty string, not an error. Always verify secret names match exactly by checking both the workflow file and the GitHub repo settings page.
**Tags:** `#ci` `#github-actions` `#secrets` `#silent-failure`

### [2026-03-14] release-please First Run Fails Expectedly on Fresh Repos
**Context:** Phase 4 release pipeline — first master push after adding release workflow
**Problem:** Release workflow failed in 7s on first master push. CI passed on same push. Appeared broken but was expected behavior.
**Solution:** No code fix needed. release-please needs the token secret and pypi environment configured before it can succeed. First run always fails until manual setup is completed.
**Why:** release-please requires prior release history or bootstrap configuration to create its first Release PR. The first workflow run on a fresh repo will always fail. Document this expectation in the PR body so the failure isn't mistaken for a bug.
**Tags:** `#ci` `#release-please` `#gotcha`

### [2026-03-04] Starlight 0.37 + Astro 5 Requires Explicit content.config.ts
**Context:** Setting up Astro Starlight documentation site for the project
**Problem:** `.md` files in the docs directory were silently ignored — only `.mdx` files were discovered and rendered. No error messages.
**Solution:** Created `site/src/content.config.ts` with `docsLoader` from `@astrojs/starlight/loaders` and `docsSchema` from `@astrojs/starlight/schema`. Collection must be named `"docs"`.
**Why:** Starlight 0.37 + Astro 5 changed content discovery behavior. Without an explicit content.config.ts, only `.mdx` files are auto-discovered. This is a silent failure — no warnings, no errors, just missing pages.
**Tags:** `#astro` `#starlight` `#docs` `#silent-failure`

### [2026-03-04] GitHub Pages Workflow Path Scoping Prevents Unnecessary Deploys
**Context:** Configuring GitHub Pages deployment for the Starlight documentation site
**Problem:** Without path filtering, every push to master triggers a docs rebuild — even for source code, test, or config changes that don't affect the site.
**Solution:** Added `paths: ['site/**']` filter to the push trigger in `pages.yml`. Added `workflow_dispatch` for manual re-deploys. Set `concurrency` group with `cancel-in-progress: true`.
**Why:** Path-scoped workflows prevent wasted CI minutes and unnecessary deploys. The concurrency group ensures in-progress builds are cancelled when newer commits arrive, keeping the deployed site always reflecting the latest push.
**Tags:** `#ci` `#github-actions` `#github-pages` `#optimization`

### [2026-06-28] GraphQL Rate Limits Block Board Operations — Use REST Fallback
**Context:** Migrating backlog items to GitHub issues and adding them to the bitácora board
**Problem:** `gh project item-add` and `gh project item-edit` use GraphQL internally. Heavy board operations (field resolution, 14 item adds with field sets) exhaust the 5000/hour GraphQL limit, causing silent failures — commands return empty JSON or error, and items appear added but fields don't persist.
**Solution:** (1) Use `gh api` with REST endpoints for issue/PR operations (`repos/.../issues`, `repos/.../pulls`) — these use the separate 5000/hour REST limit. (2) For board operations, add items first, then set fields in a second pass after a brief pause. (3) Verify items landed by searching by URL, not by ID field (which may not persist on rate-limit failure).
**Why:** GitHub's GraphQL and REST APIs have independent rate limits. `gh` CLI commands like `gh project` and `gh pr view` use GraphQL; `gh api repos/...` uses REST. When one is exhausted, the other still works. Always have a REST fallback for critical operations.
**Tags:** `#github` `#graphql` `#rate-limit` `#bitacora` `#gotcha`

### [2026-06-28] `gh project item-add` Can Silently Succeed Without Persisting
**Context:** Adding 14 yt-metrics-cli issues to the bitácora board
**Problem:** `gh project item-add` returned valid item IDs and `gh project item-edit` returned no errors, but subsequent `gh project item-list` showed the items were not on the board. The commands succeeded at the API level but the board state didn't reflect it — likely due to GraphQL rate limiting causing partial writes.
**Solution:** After bulk board operations, verify items actually landed by searching the board list by URL or title. Don't trust the add/edit return codes alone. If verification fails, re-add after rate limit reset.
**Why:** GraphQL rate limits can cause silent partial failures — the mutation returns a success response but the server-side state doesn't persist. Always verify board state after bulk operations.
**Tags:** `#github` `#graphql` `#bitacora` `#silent-failure`
