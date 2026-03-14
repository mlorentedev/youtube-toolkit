"""CSV export for channel and video data."""

import csv
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def export_to_csv(channels_data: list[dict[str, Any]], filename: str | Path) -> None:
    """Export channel and video data to CSV."""
    if not channels_data:
        logger.warning("No data to export.")
        return

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow([
            "Channel", "Subscribers", "Video Title", "Published Date", "Video URL",
            "Views", "Likes", "Comments", "Duration (seconds)",
            "Engagement Rate (Views %)", "Engagement Rate (Subscribers %)",
            "View Rate (%)", "Like Rate (%)", "Comment Rate (%)", "Views per Minute",
        ])

        for channel_data in channels_data:
            channel_info = channel_data["channel"]
            channel_name = channel_info["title"]
            subscriber_count = channel_info.get("subscriber_count", "N/A")

            for video in channel_data["videos"]:
                writer.writerow([
                    channel_name,
                    subscriber_count,
                    video["title"],
                    video["published_at"],
                    video["url"],
                    video.get("view_count", 0),
                    video.get("like_count", 0),
                    video.get("comment_count", 0),
                    video.get("duration_seconds", 0),
                    video.get("engagement_rate_views", 0),
                    video.get("engagement_rate_subscribers", 0),
                    video.get("view_rate", 0),
                    video.get("like_rate", 0),
                    video.get("comment_rate", 0),
                    video.get("views_per_minute", 0),
                ])

    total_videos = sum(len(cd["videos"]) for cd in channels_data)
    logger.info(
        "Exported %d videos from %d channels to %s",
        total_videos, len(channels_data), filename,
    )
