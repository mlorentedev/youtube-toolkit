---
id: lesson-009-graphql-rate-limits-block-board-operations-use-res
type: lesson
status: active
created: "2026-06-28"
owner: manu
tags: [yt-metrics-cli, lesson, github, graphql, rate-limit, bitacora, gotcha]
---

# GraphQL Rate Limits Block Board Operations — Use REST Fallback

**Context:** Migrating backlog items to GitHub issues and adding them to the bitácora board
**Problem:** `gh project item-add` and `gh project item-edit` use GraphQL internally. Heavy board operations (field resolution, 14 item adds with field sets) exhaust the 5000/hour GraphQL limit, causing silent failures — commands return empty JSON or error, and items appear added but fields don't persist.
**Solution:** (1) Use `gh api` with REST endpoints for issue/PR operations (`repos/.../issues`, `repos/.../pulls`) — these use the separate 5000/hour REST limit. (2) For board operations, add items first, then set fields in a second pass after a brief pause. (3) Verify items landed by searching by URL, not by ID field (which may not persist on rate-limit failure).
**Why:** GitHub's GraphQL and REST APIs have independent rate limits. `gh` CLI commands like `gh project` and `gh pr view` use GraphQL; `gh api repos/...` uses REST. When one is exhausted, the other still works. Always have a REST fallback for critical operations.
**Tags:** `#github` `#graphql` `#rate-limit` `#bitacora` `#gotcha`
