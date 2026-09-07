---
id: lesson-006-ansi-color-codes-in-typer-rich-cli-test-output-bre
type: lesson
status: active
created: "2026-03-14"
owner: manu
tags: [yt-metrics-cli, lesson, testing, cli, typer, rich, ansi]
---

# ANSI Color Codes in Typer/Rich CLI Test Output Break Assertions

**Context:** Phase 3 CI pipeline — CLI help tests failing on GitHub Actions
**Problem:** Tests asserting `'--channels' in result.output` failed because Typer/Rich renders ANSI escape codes (e.g., `\x1b[1;36m-\x1b[0m\x1b[1;36m-channels\x1b[0m`) that split option flag strings. Both Python 3.12 and 3.13 affected — not version-specific.
**Solution:** Added `_strip_ansi(text: str) -> str` helper using `re.sub(r"\x1b\[[0-9;]*m", "", text)` to strip ANSI codes before assertions. Applied to `test_channels_help` and `test_transcript_help`.
**Why:** Typer uses Rich for styled terminal output. CliRunner captures raw output including ANSI sequences. Any test asserting plain text substrings in CLI help output will break. Either strip ANSI before assertions or disable color in the test runner.
**Tags:** `#testing` `#cli` `#typer` `#rich` `#ansi`
