---
id: lesson-001-starlight-0-37-astro-5-requires-explicit-content-c
type: lesson
status: active
created: "2026-03-04"
owner: manu
tags: [yt-metrics-cli, lesson, astro, starlight, docs, silent-failure]
---

# Starlight 0.37 + Astro 5 Requires Explicit content.config.ts

**Context:** Setting up Astro Starlight documentation site for the project
**Problem:** `.md` files in the docs directory were silently ignored — only `.mdx` files were discovered and rendered. No error messages.
**Solution:** Created `site/src/content.config.ts` with `docsLoader` from `@astrojs/starlight/loaders` and `docsSchema` from `@astrojs/starlight/schema`. Collection must be named `"docs"`.
**Why:** Starlight 0.37 + Astro 5 changed content discovery behavior. Without an explicit content.config.ts, only `.mdx` files are auto-discovered. This is a silent failure — no warnings, no errors, just missing pages.
**Tags:** `#astro` `#starlight` `#docs` `#silent-failure`
