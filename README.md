# YouTube Toolkit

A Python CLI application for analyzing YouTube channels and downloading video transcripts. Built with a modular architecture for maintainability and extensibility.

## Features

* **Channel Analysis:** Analyze multiple YouTube channels simultaneously
* **API Key Validation:** Validates YouTube API key before operations with helpful error messages
* **Comprehensive Metrics:** Engagement rates, view rates, performance distribution
* **Multiple Export Formats:** CSV data, detailed TXT reports, URL lists
* **Transcript Downloader:** Multi-language support with automatic fallback
* **Self-Documenting Output:** Each analysis generates a README explaining all files

## Quick Start

### Prerequisites

* **Python 3.12+**
* **Poetry** - `pip install poetry`
* **Task (Taskfile)** - `go install github.com/go-task/task/v3/cmd/task@latest`
* **YouTube Data API Key** - [Get API Key](https://developers.google.com/youtube/v3/getting-started)

### Installation

```bash
git clone <repository-url>
cd youtube-toolkit
task install
```

### Configuration

Create `.env` file:

```ini
# Required
YOUTUBE_API_KEY=your-youtube-api-key-here

# Optional
MAX_RESULTS_PER_CHANNEL=100
OUTPUT_DIR=./output
VIDEO_ID=dQw4w9WgXcQ
```

Create `channels.yml`:

```yaml
- custom_url: "@technotim"
- custom_url: "@christianlempa"
- channel_id: "UCxxxxxxxxxxxxxx"
```

## Usage

### Analyze Channels

```bash
task run:channels
```

Generates timestamped reports in `output/<timestamp>/`:
* **README.md** - Explains all generated files
* **CSV** - Raw data with all metrics
* **Channel Stats** - Per-channel detailed analysis (top 5 videos)
* **Engagement Trends** - Cross-channel comparisons
* **Best Videos** - Top 15 by engagement (URLs)
* **Latest Videos** - 15 most recent (URLs)

Each analysis run creates a separate timestamped folder (e.g., `output/20231123_143022/`) to keep results organized.

### Download Transcript

```bash
task run:video

# Or specify video ID
poetry run python -m src.main video <video_id> --langs en,es
```

## Engagement Metrics

| Metric | Formula | Use Case |
|--------|---------|----------|
| Engagement Rate (Views) | `(likes + comments) / views × 100` | Audience interaction |
| View Rate | `views / subscribers × 100` | Viral potential (>100%) |
| Like Rate | `likes / views × 100` | Content satisfaction |
| Comment Rate | `comments / views × 100` | Discussion level |

## Project Structure

```
src/
├── main.py          # CLI entry point
├── config.py        # Configuration & constants
├── metrics.py       # Engagement calculations
├── transcript.py    # Transcript downloader
├── analyzer.py      # YouTube API wrapper
└── exporters.py     # Report generators
```

### Key Design Principles

* Type hints throughout for IDE support
* Runtime validation with clear error messages
* Modular architecture for maintainability
* Batch API processing (50 videos per request)

## Development

```bash
# Update dependencies
task update

# Poetry shell
task shell

# Run in development
poetry run python -m src.main channels --help
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `YOUTUBE_API_KEY` | ✅ | - | YouTube Data API v3 key |
| `MAX_RESULTS_PER_CHANNEL` | No | `50` | Videos per channel |
| `OUTPUT_DIR` | No | `./output` | Report output directory |
| `VIDEO_ID` | No | - | Default video for transcripts |
| `YOUTUBE_TRANSCRIPT_FIXTURES_DIR` | No | - | Local transcript fallback |

## License

See LICENSE file for details.
