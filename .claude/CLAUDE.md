# youtube-toolkit

> CLI for YouTube channel analysis and transcript downloading.

## Architecture

- **CLI Layer:** `src/main.py` — Entry point with `channels` and `transcript` commands
- **Config:** `src/config.py` — Constants and environment variable management
- **Core:** `src/analyzer.py` — YouTube API wrapper (channel resolution, batch video stats)
- **Metrics:** `src/metrics.py` — Pure engagement calculations (6 computed fields)
- **Transcript:** `src/transcript.py` — Transcript download with 3-level fallback
- **Export:** `src/exporters.py` — Report generators (CSV, TXT, README)

## Technical Standards

| Requirement | Tool/Pattern |
|---|---|
| Python | 3.12+ |
| Type hints | mypy --strict |
| Dependencies | uv |
| Formatting | Ruff |
| Testing | pytest + pytest-cov |
| Build | hatchling |

## Key Paths

| Path | Role |
|---|---|
| `src/main.py` | CLI entry point |
| `src/config.py` | Configuration and constants |
| `src/analyzer.py` | YouTube API wrapper |
| `src/metrics.py` | Engagement metric calculations |
| `src/transcript.py` | Transcript downloader with fallback chain |
| `src/exporters.py` | Report generators (CSV, text, README) |
| `tests/` | pytest suite |
| `site/` | Astro Starlight documentation |

## Verification Commands

All commands go through the Makefile:

```bash
make install    # Create venv + install deps
make lint       # Ruff linter
make typecheck  # mypy --strict
make test       # pytest with coverage
make check      # lint + typecheck + test
make build      # check + uv build
make run        # Run channel analysis
make clean      # Remove build artifacts
```
