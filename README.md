# YouTube Channel Scraper and Analyzer

This project is a Python-based command-line interface (CLI) application designed to analyze YouTube channels and download video transcripts. It leverages the YouTube Data API v3 to gather channel statistics and video details, and the `youtube-transcript-api` to fetch video transcripts.

## Features

* **Channel Analysis:** Analyze a list of YouTube channels to gather statistics and video details.
* **Engagement Metrics:** Calculate various engagement metrics for videos.
* **Data Export:** Export channel and video data to CSV, detailed channel statistics reports, comprehensive engagement trends analysis, and reports for best/latest videos.
* **Transcript Downloader:** Download transcripts for individual YouTube videos.

## Setup

### Prerequisites

Before you begin, ensure you have the following installed:

* **Python 3.12+**: [Download Python](https://www.python.org/downloads/)
* **Poetry**: A dependency management and packaging tool for Python.

    ```bash
    pip install poetry
    ```

* **Task (Taskfile)**: A task runner / build tool.

    ```bash
    go install github.com/go-task/task/v3/cmd/task@latest
    ```

* **YouTube Data API Key**: You'll need an API key from the Google Cloud Console to access the YouTube Data API. [Get your API Key](https://developers.google.com/youtube/v3/getting-started)

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/your-repo/youtube-channel-scrapper.git
    cd youtube-channel-scrapper
    ```

2. **Install dependencies using Poetry:**

    ```bash
    task install
    ```

## Configuration

### Environment Variables (`.env`)

Create a `.env` file in the root of the project by copying `.env.example` (if it exists) or creating one manually. This file should contain your `YOUTUBE_API_KEY` and can also specify `VIDEO_ID`, `MAX_RESULTS_PER_CHANNEL`, `OUTPUT_DIR`, and `YOUTUBE_TRANSCRIPT_FIXTURES_DIR`.

Example `.env` file:

```ini
# .env
YOUTUBE_API_KEY=your-youtube-api-key
VIDEO_ID=tLkRAqmAEtE # Default video ID for transcript download
MAX_RESULTS_PER_CHANNEL=100
OUTPUT_DIR=./output
YOUTUBE_TRANSCRIPT_FIXTURES_DIR=./fixtures/transcripts
```

### `channels.yml`

The list of YouTube channels to analyze is defined in `channels.yml`. This file should contain a YAML list of dictionaries, where each dictionary specifies a channel using either `channel_id`, `username`, or `custom_url`.

Example `channels.yml`:

```yaml
- custom_url: "@christianlempa"
- custom_url: "@iximiuz"
- custom_url: "@mischavandenburg"
# Add more channels as needed
```

## Usage

All commands are run using `task`.

### Analyze YouTube Channels

This command analyzes the channels listed in `channels.yml`, fetches their videos, calculates engagement metrics, and generates several reports in the `output/` directory:

* `youtube_channels_videos_<timestamp>.csv`: Raw video data in CSV format.
* `youtube_channel_stats_<timestamp>.txt`: Detailed statistics for each channel.
* `youtube_engagement_trends_<timestamp>.txt`: Comprehensive engagement trends analysis.
* `youtube_best_videos_<timestamp>.txt`: URLs of the 15 best videos (by engagement rate) for each channel.
* `youtube_latest_videos_<timestamp>.txt`: URLs of the 15 latest videos for each channel.

```bash
task run:channels
```

You can override `MAX_RESULTS_PER_CHANNEL` and `OUTPUT_DIR` by setting them in your `.env` file or as environment variables.

### Download a Video Transcript

This command downloads the transcript for a single YouTube video. By default, it uses the `VIDEO_ID` from your `.env` file, but you can provide the `video_id` as an argument.

```bash
# Download transcript for a specific video ID
poetry run python src/main.py video <video_id> --langs en,es --output-dir ./output
```

You can also run the default video (if defined in `main.py`) using `task`:

```bash
task run:video
```

You can specify preferred languages using the `YT_LANGS` environment variable (e.g., `YT_LANGS=en,fr task run:video`).

## Development

### Update Dependencies

To update the project's dependencies:

```bash
task update
```

### Poetry Shell

To spawn a Poetry-managed shell for ad-hoc commands:

```bash
task shell
```
