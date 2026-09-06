---
id: lesson-004-replace-assert-with-explicit-valueerror-for-contro
type: lesson
status: active
created: "2026-03-14"
owner: manu
tags: [yt-metrics-cli, lesson, python, clean-code, assert-antipattern]
---

# Replace assert with Explicit ValueError for Control Flow

**Context:** Phase 6 clean code audit found `assert channel_id is not None` in `analyzer.py:get_channel_videos()`
**Problem:** `assert` statements are stripped when Python runs with the `-O` (optimize) flag, making the guard silently disappear in production. The assert was used for mypy type narrowing, not as a test assertion.
**Solution:** Replaced with `if channel_id is None: raise ValueError("Could not resolve channel ID from provided identifiers")`.
**Why:** `assert` is for development-time invariant checking, not runtime control flow. Code that depends on asserts for correctness breaks under `-O`. Use explicit `if/raise` for any guard that must always execute.
**Tags:** `#python` `#clean-code` `#assert-antipattern`
