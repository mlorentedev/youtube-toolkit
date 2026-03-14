"""URL list exporters for best and latest videos."""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def export_best_videos_report(
    channels_data: list[dict[str, Any]], filename: str | Path, top_n: int = 15
) -> None:
    """Export top N best videos by engagement rate for each channel."""
    if not channels_data:
        logger.warning("No data to export.")
        return

    with open(filename, "w", encoding="utf-8") as f:
        for channel_data in channels_data:
            videos = channel_data["videos"]
            if videos:
                best = sorted(
                    videos, key=lambda x: x.get("engagement_rate_views", 0), reverse=True
                )[:top_n]
                for video in best:
                    f.write(f"{video['url']}\n")

    logger.info("Exported top %d best videos report to %s", top_n, filename)


def export_latest_videos_report(
    channels_data: list[dict[str, Any]], filename: str | Path, top_n: int = 15
) -> None:
    """Export top N latest videos for each channel."""
    if not channels_data:
        logger.warning("No data to export.")
        return

    with open(filename, "w", encoding="utf-8") as f:
        for channel_data in channels_data:
            videos = channel_data["videos"]
            if videos:
                latest = sorted(
                    videos, key=lambda x: x.get("published_at", ""), reverse=True
                )[:top_n]
                for video in latest:
                    f.write(f"{video['url']}\n")

    logger.info("Exported top %d latest videos report to %s", top_n, filename)
