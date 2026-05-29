# yt-metrics-cli

[![CI](https://github.com/mlorentedev/yt-metrics-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/mlorentedev/yt-metrics-cli/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-Starlight-purple)](https://mlorentedev.github.io/yt-metrics-cli/)

CLI tool that analyzes YouTube channels and downloads video transcripts, generating engagement metrics and structured reports.

## Problem

YouTube Studio gives you analytics for **your own** channels. If you want to compare multiple channels, benchmark engagement rates, or bulk-download transcripts for research, you're stuck with manual work or fragmented browser extensions.

**yt-metrics-cli** solves this: point it at a list of channels, get CSV data, engagement reports, and transcript files in one command.

## Quick Start

```bash
# Install
pip install yt-metrics-cli
# or
uv tool install yt-metrics-cli

# Set your API key
export YOUTUBE_API_KEY=your_key_here
# Get one at: https://console.cloud.google.com/apis/credentials

# Create channels.yml
cat > channels.yml << 'EOF'
- custom_url: "@mkbhd"
- custom_url: "@veritasium"
EOF

# Analyze
yt-metrics channels
```

## Features

| Feature | Description |
|---------|-------------|
| Multi-channel analysis | Analyze N channels in one run |
| Engagement metrics | View rate, like rate, comment rate, viral detection |
| CSV export | Raw data with all computed fields |
| Text reports | Channel stats, trends, top/latest video URLs |
| Transcript download | Multi-language with 3-level fallback chain |
| API resilience | Exponential backoff on rate limits (403/429) |

## Usage

### Analyze Channels

```bash
yt-metrics channels                        # Use defaults from .env
yt-metrics channels -c my_channels.yml     # Custom channel list
yt-metrics channels -n 100 -o ./reports    # 100 videos, custom output
```

Generates timestamped reports in `output/<timestamp>/`:

- **CSV** — Raw data with all metrics per video
- **Channel Stats** — Per-channel analysis with top 5 videos
- **Engagement Trends** — Cross-channel comparisons and rankings
- **Best/Latest Videos** — URL lists for quick access
- **README** — Index explaining all generated files

### Download Transcripts

```bash
yt-metrics transcript -v dQw4w9WgXcQ       # Specific video
yt-metrics transcript -v abc123 -l es,en    # Language preference
```

## Engagement Metrics

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| Engagement Rate | `(likes + comments) / views * 100` | Overall audience interaction |
| View Rate | `views / subscribers * 100` | Reach beyond subscriber base (>100% = viral) |
| Like Rate | `likes / views * 100` | Content satisfaction signal |
| Comment Rate | `comments / views * 100` | Discussion engagement level |

## Configuration

All settings can be set via environment variables or `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `YOUTUBE_API_KEY` | *(required)* | YouTube Data API v3 key |
| `MAX_RESULTS_PER_CHANNEL` | `50` | Videos to fetch per channel |
| `OUTPUT_DIR` | `./output` | Report output directory |
| `CHANNELS_FILE` | `channels.yml` | Channel list file path |
| `VIDEO_ID` | — | Default video for transcript mode |
| `TRANSCRIPT_LANGUAGES` | `es,en` | Preferred transcript languages |

## Development

```bash
git clone https://github.com/mlorentedev/yt-metrics-cli.git
cd yt-metrics-cli
make install    # Create venv + install deps
make check      # Lint + typecheck + test
make build      # Full build
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

[MIT](LICENSE)

## Documentation

Project-bound knowledge lives in [`docs/`](docs/) (docs-as-code): ADRs, runbooks, troubleshooting, and lessons.
