"""YouTube Toolkit CLI - Channel analyzer and transcript downloader."""

import sys
import argparse
from datetime import datetime
from pathlib import Path
import yaml

from .config import (
    CHANNELS_FILE,
    DEFAULT_VIDEO_ID,
    DEFAULT_MAX_RESULTS,
    DEFAULT_OUTPUT_DIR,
    ENV_VIDEO_ID,
    ENV_MAX_RESULTS,
    ENV_OUTPUT_DIR,
    get_env
)
from .transcript import YouTubeTranscriptDownloader
from .analyzer import YouTubeChannelAnalyzer
from .exporters import (
    export_to_csv,
    export_channel_stats,
    export_engagement_trends_report,
    export_best_videos_report,
    export_latest_videos_report,
    export_output_readme
)


def load_channels(filename: Path = CHANNELS_FILE) -> list:
    """Load and validate channels from YAML file."""
    if not filename.exists():
        print(f"Error: {filename} not found. Create it with your channel list.")
        sys.exit(1)

    try:
        with open(filename, encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file {filename}: {e}")
        sys.exit(1)

    if not isinstance(data, list):
        print(f"Error: {filename} must contain a list of channel definitions")
        sys.exit(1)

    for i, channel in enumerate(data):
        if not isinstance(channel, dict):
            print(f"Error: Channel {i} must be a dictionary")
            sys.exit(1)
        if not any(k in channel for k in ['channel_id', 'username', 'custom_url']):
            print(f"Error: Channel {i} must have channel_id, username, or custom_url")
            sys.exit(1)

    return data


def run_channels_mode(args):
    """Analyze channels and generate reports."""
    channels = load_channels()
    analyzer = YouTubeChannelAnalyzer()

    print("Validating YouTube API key...")
    try:
        analyzer.validate_api_key()
        print("API key validated successfully.")
    except (ValueError, RuntimeError) as e:
        print(f"\nAPI Validation Error:\n{e}")
        sys.exit(1)

    max_results = int(get_env(ENV_MAX_RESULTS, DEFAULT_MAX_RESULTS))
    base_output_dir = Path(get_env(ENV_OUTPUT_DIR, DEFAULT_OUTPUT_DIR)).expanduser()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = base_output_dir / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nAnalyzing {len(channels)} channels (max {max_results} videos each)...")
    print(f"Output will be saved to: {output_dir}")

    channels_data = analyzer.get_multiple_channels_videos(
        channels,
        max_results_per_channel=max_results,
    )

    if not channels_data:
        print("No channel data retrieved. Exiting.")
        return

    csv_filename = output_dir / f"youtube_channels_videos_{timestamp}.csv"
    export_to_csv(channels_data, csv_filename)

    stats_filename = output_dir / f"youtube_channel_stats_{timestamp}.txt"
    export_channel_stats(channels_data, stats_filename)

    trends_filename = output_dir / f"youtube_engagement_trends_{timestamp}.txt"
    export_engagement_trends_report(channels_data, trends_filename)

    best_videos_filename = output_dir / f"youtube_best_videos_{timestamp}.txt"
    export_best_videos_report(channels_data, best_videos_filename, top_n=15)

    latest_videos_filename = output_dir / f"youtube_latest_videos_{timestamp}.txt"
    export_latest_videos_report(channels_data, latest_videos_filename, top_n=15)

    export_output_readme(output_dir, timestamp, channels_data)

    print("\nSample results:")
    for channel_data in channels_data[:3]:
        channel_info = channel_data["channel"]
        videos = channel_data["videos"]

        subscriber_count = channel_info.get('subscriber_count', 'N/A')
        print(f"\n{channel_info['title']} (Subscribers: {subscriber_count})")
        print("Recent videos:")

        for i, video in enumerate(videos[:3], 1):
            published_date = video["published_at"].split("T")[0]
            views = video.get('view_count', 0)
            engagement = video.get('engagement_rate_views', 0)
            print(f"  {i}. {video['title']} - {published_date}")
            print(f"     Views: {views:,} | Engagement: {engagement:.3f}%")

    print(f"\nReports generated in {output_dir}:")
    print(f"  - README.md (explains all files)")
    print(f"  - CSV: {csv_filename.name}")
    print(f"  - Channel stats: {stats_filename.name}")
    print(f"  - Engagement trends: {trends_filename.name}")
    print(f"  - Best videos: {best_videos_filename.name}")
    print(f"  - Latest videos: {latest_videos_filename.name}")


def run_video_mode(args):
    """Download video transcript."""
    video_id = args.video_id or get_env(ENV_VIDEO_ID, DEFAULT_VIDEO_ID)
    langs = args.langs.split(",") if args.langs else None

    print(f"Downloading transcript for video: {video_id}")
    if langs:
        print(f"Preferred languages: {langs}")

    downloader = YouTubeTranscriptDownloader(langs)
    downloader.save_transcript(video_id, args.output_dir)


def main():
    parser = argparse.ArgumentParser(
        description="YouTube Toolkit - Analyze channels and download transcripts"
    )
    subparsers = parser.add_subparsers(dest="mode", required=True)

    parser_channels = subparsers.add_parser(
        "channels",
        help="Analyze channels and generate reports"
    )
    parser_channels.add_argument(
        "--max-results",
        type=int,
        default=DEFAULT_MAX_RESULTS,
        help=f"Max videos per channel (default: {DEFAULT_MAX_RESULTS})"
    )
    parser_channels.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})"
    )

    parser_video = subparsers.add_parser(
        "video",
        help="Download video transcript"
    )
    parser_video.add_argument(
        "video_id",
        nargs="?",
        help=f"YouTube video ID (default: from {ENV_VIDEO_ID} env var)"
    )
    parser_video.add_argument(
        "--langs",
        default="",
        help="Preferred languages, comma separated (e.g., en,es)"
    )
    parser_video.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})"
    )

    args = parser.parse_args()

    try:
        if args.mode == "channels":
            run_channels_mode(args)
        elif args.mode == "video":
            run_video_mode(args)
        else:
            parser.print_help()
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
