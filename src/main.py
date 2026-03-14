"""YouTube Toolkit CLI — Channel analyzer and transcript downloader."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any

import typer
import yaml
from rich.console import Console

from .config import get_settings
from .exporters import (
    export_best_videos_report,
    export_channel_stats,
    export_engagement_trends_report,
    export_latest_videos_report,
    export_output_readme,
    export_to_csv,
)

app = typer.Typer(
    name="youtube-toolkit",
    help="CLI for YouTube channel analysis and transcript downloading.",
    no_args_is_help=True,
)
console = Console()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


@app.command()
def channels(
    channels_file: Annotated[
        Path | None,
        typer.Option("--channels", "-c", help="Path to channels YAML file"),
    ] = None,
    max_results: Annotated[
        int | None,
        typer.Option("--max-results", "-n", help="Max videos per channel"),
    ] = None,
    output_dir: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output directory"),
    ] = None,
) -> None:
    """Analyze YouTube channels and generate reports."""
    settings = get_settings()

    if not settings.youtube_api_key:
        console.print(
            "[red]Error:[/red] YOUTUBE_API_KEY not set. "
            "Add it to your .env file or set the environment variable."
        )
        raise typer.Exit(code=1)

    from .analyzer import YouTubeChannelAnalyzer

    resolved_channels_file = channels_file or settings.channels_file
    resolved_max_results = max_results or settings.max_results_per_channel
    resolved_output_dir = (output_dir or settings.output_dir).expanduser()

    channel_list = _load_channels(resolved_channels_file)
    analyzer = YouTubeChannelAnalyzer()

    console.print("Validating YouTube API key...")
    try:
        analyzer.validate_api_key()
        console.print("[green]API key validated successfully.[/green]")
    except (ValueError, RuntimeError) as e:
        console.print(f"[red]API Validation Error:[/red] {e}")
        raise typer.Exit(code=1) from None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_output_dir = resolved_output_dir / timestamp
    run_output_dir.mkdir(parents=True, exist_ok=True)

    console.print(
        f"\nAnalyzing {len(channel_list)} channels"
        f" (max {resolved_max_results} videos each)..."
    )
    console.print(f"Output: {run_output_dir}")

    channels_data = analyzer.get_multiple_channels_videos(
        channel_list, max_results_per_channel=resolved_max_results
    )

    if not channels_data:
        console.print("[yellow]No channel data retrieved. Exiting.[/yellow]")
        return

    _generate_reports(channels_data, run_output_dir, timestamp)
    _print_sample_results(channels_data)

    console.print(f"\n[green]Reports generated in {run_output_dir}[/green]")


@app.command()
def transcript(
    video_id: Annotated[
        str | None,
        typer.Option("--video", "-v", help="YouTube video ID"),
    ] = None,
    languages: Annotated[
        str | None,
        typer.Option("--langs", "-l", help="Languages, comma separated"),
    ] = None,
    output_dir: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output directory"),
    ] = None,
) -> None:
    """Download transcript for a YouTube video."""
    from .transcript import YouTubeTranscriptDownloader

    settings = get_settings()
    resolved_video_id = video_id or settings.video_id
    resolved_output = str((output_dir or settings.output_dir).expanduser())
    langs = languages.split(",") if languages else None

    console.print(f"Downloading transcript for video: {resolved_video_id}")
    if langs:
        console.print(f"Preferred languages: {langs}")

    downloader = YouTubeTranscriptDownloader(langs)
    saved_path = downloader.save_transcript(resolved_video_id, resolved_output)
    console.print(f"[green]Transcript saved to {saved_path}[/green]")


# --- Private helpers ---


def _load_channels(filename: Path) -> list[dict[str, Any]]:
    """Load and validate channels from YAML file."""
    if not filename.exists():
        console.print(
            f"[red]Error:[/red] {filename} not found. "
            "Create it with your channel list."
        )
        raise typer.Exit(code=1)

    try:
        with open(filename, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        console.print(f"[red]Error parsing YAML:[/red] {e}")
        raise typer.Exit(code=1) from None

    if not isinstance(data, list):
        console.print(
            f"[red]Error:[/red] {filename} must contain "
            "a list of channel definitions"
        )
        raise typer.Exit(code=1)

    for i, channel in enumerate(data):
        if not isinstance(channel, dict):
            console.print(
                f"[red]Error:[/red] Channel {i} must be a dictionary"
            )
            raise typer.Exit(code=1)
        if not any(k in channel for k in ("channel_id", "username", "custom_url")):
            console.print(
                f"[red]Error:[/red] Channel {i} must have"
                " channel_id, username, or custom_url"
            )
            raise typer.Exit(code=1)

    return data


def _generate_reports(
    channels_data: list[dict[str, Any]],
    output_dir: Path,
    timestamp: str,
) -> None:
    """Generate all report files."""
    csv_path = output_dir / f"youtube_channels_videos_{timestamp}.csv"
    export_to_csv(channels_data, csv_path)
    stats_path = output_dir / f"youtube_channel_stats_{timestamp}.txt"
    export_channel_stats(channels_data, stats_path)
    trends_path = output_dir / f"youtube_engagement_trends_{timestamp}.txt"
    export_engagement_trends_report(channels_data, trends_path)
    best_path = output_dir / f"youtube_best_videos_{timestamp}.txt"
    export_best_videos_report(channels_data, best_path)
    latest_path = output_dir / f"youtube_latest_videos_{timestamp}.txt"
    export_latest_videos_report(channels_data, latest_path)
    export_output_readme(output_dir, timestamp, channels_data)


def _print_sample_results(
    channels_data: list[dict[str, Any]],
) -> None:
    """Print sample results to console."""
    console.print("\nSample results:")
    for channel_data in channels_data[:3]:
        info = channel_data["channel"]
        videos = channel_data["videos"]

        subs = info.get("subscriber_count", "N/A")
        console.print(
            f"\n[bold]{info['title']}[/bold]"
            f" (Subscribers: {subs})"
        )
        for i, video in enumerate(videos[:3], 1):
            date = str(video["published_at"]).split("T")[0]
            views = video.get("view_count", 0)
            eng = video.get("engagement_rate_views", 0)
            console.print(f"  {i}. {video['title']} - {date}")
            console.print(f"     Views: {views:,} | Engagement: {eng:.3f}%")
