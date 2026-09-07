---
id: lesson-010-gh-project-item-add-can-silently-succeed-without-p
type: lesson
status: active
created: "2026-06-28"
owner: manu
tags: [yt-metrics-cli, lesson, github, graphql, bitacora, silent-failure]
---

# `gh project item-add` Can Silently Succeed Without Persisting

**Context:** Adding 14 yt-metrics-cli issues to the bitácora board
**Problem:** `gh project item-add` returned valid item IDs and `gh project item-edit` returned no errors, but subsequent `gh project item-list` showed the items were not on the board. The commands succeeded at the API level but the board state didn't reflect it — likely due to GraphQL rate limiting causing partial writes.
**Solution:** After bulk board operations, verify items actually landed by searching the board list by URL or title. Don't trust the add/edit return codes alone. If verification fails, re-add after rate limit reset.
**Why:** GraphQL rate limits can cause silent partial failures — the mutation returns a success response but the server-side state doesn't persist. Always verify board state after bulk operations.
**Tags:** `#github` `#graphql` `#bitacora` `#silent-failure`
