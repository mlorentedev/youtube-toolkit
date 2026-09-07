---
id: lesson-003-video-id-input-validation-to-prevent-path-traversa
type: lesson
status: active
created: "2026-03-14"
owner: manu
tags: [yt-metrics-cli, lesson, security, input-validation, path-traversal]
---

# Video ID Input Validation to Prevent Path Traversal

**Context:** Phase 6 security audit of transcript.py
**Problem:** `video_id` was used directly in file paths (`f"{video_id}_transcript.txt"`) and API calls without format validation. A malicious ID containing `../` could traverse directories when writing transcript files.
**Solution:** Added `_validate_video_id()` static method with regex `^[a-zA-Z0-9_-]{1,20}$` called at the start of `get_transcript()`, before any file or API operation.
**Why:** Any user-supplied string used in file path construction must be validated against an allowlist pattern. Defense-in-depth — even if the caller sanitizes, the callee should enforce its own contract.
**Tags:** `#security` `#input-validation` `#path-traversal`
