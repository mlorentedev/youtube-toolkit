"""Text report exporters for channel statistics and engagement trends."""

import logging
from datetime import datetime
from io import TextIOWrapper
from pathlib import Path
from typing import Any

from src.config import format_number, get_settings

logger = logging.getLogger(__name__)


def export_channel_stats(channels_data: list[dict[str, Any]], filename: str | Path) -> None:
    """Export detailed channel statistics to text file."""
    if not channels_data:
        logger.warning("No data to export.")
        return

    with open(filename, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("YOUTUBE CHANNEL STATISTICS REPORT\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")

        for channel_data in channels_data:
            _write_channel_section(f, channel_data)

        f.write("=" * 80 + "\n")
        f.write(f"End of Report - {len(channels_data)} channels analyzed\n")
        f.write("=" * 80 + "\n")

    logger.info("Exported channel statistics for %d channels to %s", len(channels_data), filename)


def export_engagement_trends_report(
    channels_data: list[dict[str, Any]], filename: str | Path
) -> None:
    """Export comprehensive engagement trends analysis."""
    if not channels_data:
        logger.warning("No data to export.")
        return

    with open(filename, "w", encoding="utf-8") as f:
        f.write("=" * 100 + "\n")
        f.write("YOUTUBE ENGAGEMENT TRENDS ANALYSIS REPORT\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 100 + "\n\n")

        all_videos = _collect_all_videos(channels_data)
        if not all_videos:
            f.write("No videos found for analysis.\n")
            return

        _write_global_stats(f, all_videos)
        _write_channel_rankings(f, channels_data)
        _write_content_patterns(f, all_videos)
        _write_top_content(f, channels_data)

        f.write("\n" + "=" * 100 + "\n")
        f.write("End of Engagement Trends Report\n")
        f.write("=" * 100 + "\n")

    logger.info("Exported engagement trends analysis to %s", filename)


# --- Private helpers ---


def _write_channel_section(f: TextIOWrapper, channel_data: dict[str, Any]) -> None:
    """Write a single channel's statistics section."""
    channel_info = channel_data["channel"]
    videos: list[dict[str, Any]] = channel_data["videos"]
    video_count = len(videos)

    f.write("-" * 80 + "\n")
    f.write(f"CHANNEL: {channel_info['title']}\n")
    f.write("-" * 80 + "\n")
    f.write(f"URL: {channel_info['url']}\n")
    f.write(f"Subscribers: {format_number(channel_info.get('subscriber_count'))}\n")
    f.write(f"Total Views: {format_number(channel_info.get('view_count'))}\n")
    f.write(f"Total Videos: {format_number(channel_info.get('video_count'))}\n")

    description = channel_info["description"][:100]
    if len(channel_info["description"]) > 100:
        description += "..."
    f.write(f"Description: {description}\n\n")
    f.write(f"ANALYZED VIDEOS: {video_count}\n")

    if videos:
        _write_date_range(f, videos, video_count)
        _write_engagement_summary(f, videos, video_count)

    f.write("\n\n")


def _write_date_range(
    f: TextIOWrapper, videos: list[dict[str, Any]], video_count: int
) -> None:
    """Write date range and upload frequency."""
    earliest = min(videos, key=lambda x: x["published_at"])
    latest = max(videos, key=lambda x: x["published_at"])

    f.write(f"Earliest Video Date: {earliest['published_at'].split('T')[0]}\n")
    f.write(f"Latest Video Date: {latest['published_at'].split('T')[0]}\n")

    if video_count > 1:
        start = datetime.fromisoformat(earliest["published_at"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(latest["published_at"].replace("Z", "+00:00"))
        days_diff = (end - start).days
        if days_diff > 0:
            uploads_per_month = (video_count / days_diff) * 30
            f.write(f"Estimated Upload Frequency: {uploads_per_month:.1f} videos per month\n")


def _write_engagement_summary(
    f: TextIOWrapper, videos: list[dict[str, Any]], video_count: int
) -> None:
    """Write engagement metrics summary for a channel."""
    settings = get_settings()
    f.write("\nENGAGEMENT METRICS ANALYSIS:\n")

    avg_views = sum(v.get("view_count", 0) for v in videos) / video_count
    avg_likes = sum(v.get("like_count", 0) for v in videos) / video_count
    avg_comments = sum(v.get("comment_count", 0) for v in videos) / video_count
    avg_eng_views = sum(v.get("engagement_rate_views", 0) for v in videos) / video_count

    f.write(f"Average Views per Video: {avg_views:,.0f}\n")
    f.write(f"Average Likes per Video: {avg_likes:,.0f}\n")
    f.write(f"Average Comments per Video: {avg_comments:,.0f}\n")
    f.write(f"Average Engagement Rate (by Views): {avg_eng_views:.3f}%\n")

    _write_top_videos(f, videos, "TOP 5 MOST VIEWED VIDEOS", "view_count")
    _write_top_videos(f, videos, "TOP 5 HIGHEST ENGAGEMENT VIDEOS", "engagement_rate_views")

    high_threshold = avg_eng_views * settings.high_performance_multiplier
    high = [
        v for v in videos
        if v.get("engagement_rate_views", 0) > high_threshold
    ]
    low_threshold = avg_eng_views * settings.low_performance_multiplier
    low = [
        v for v in videos
        if v.get("engagement_rate_views", 0) < low_threshold
    ]

    f.write("\nPERFORMANCE DISTRIBUTION:\n")
    high_pct = len(high) / video_count * 100
    low_pct = len(low) / video_count * 100
    high_mult = settings.high_performance_multiplier
    low_mult = settings.low_performance_multiplier
    f.write(
        f"High Performing (>{high_mult}x avg):"
        f" {len(high)} ({high_pct:.1f}%)\n"
    )
    f.write(
        f"Low Performing (<{low_mult}x avg):"
        f" {len(low)} ({low_pct:.1f}%)\n"
    )

    _write_recent_videos(f, videos)


def _write_top_videos(
    f: TextIOWrapper,
    videos: list[dict[str, Any]],
    header: str,
    sort_key: str,
) -> None:
    """Write top N videos sorted by a metric."""
    top = sorted(videos, key=lambda x: x.get(sort_key, 0), reverse=True)[:5]
    f.write(f"\n{header}:\n")
    for i, video in enumerate(top, 1):
        title = video["title"][:60] + ("..." if len(video["title"]) > 60 else "")
        f.write(f"{i}. {title}\n")
        f.write(f"   Views: {video.get('view_count', 0):,} | ")
        f.write(f"Engagement: {video.get('engagement_rate_views', 0):.3f}%\n")


def _write_recent_videos(f: TextIOWrapper, videos: list[dict[str, Any]]) -> None:
    """Write recent videos with metrics."""
    f.write("\nRECENT VIDEOS WITH METRICS:\n")
    recent = sorted(videos, key=lambda x: x["published_at"], reverse=True)[:5]
    for i, video in enumerate(recent, 1):
        date = video["published_at"].split("T")[0]
        title = video["title"][:50] + ("..." if len(video["title"]) > 50 else "")
        f.write(f"{i}. {title} ({date})\n")
        views = video.get("view_count", 0)
        eng = video.get("engagement_rate_views", 0)
        dur = video.get("duration_seconds", 0)
        f.write(f"   Views: {views:,} | Engagement: {eng:.3f}% | Duration: {dur}s\n")


def _collect_all_videos(channels_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collect all videos from all channels."""
    all_videos: list[dict[str, Any]] = []
    for cd in channels_data:
        all_videos.extend(cd["videos"])
    return all_videos


def _write_global_stats(f: TextIOWrapper, all_videos: list[dict[str, Any]]) -> None:
    """Write global statistics across all channels."""
    total = len(all_videos)
    total_views = sum(v.get("view_count", 0) for v in all_videos)
    total_likes = sum(v.get("like_count", 0) for v in all_videos)
    total_comments = sum(v.get("comment_count", 0) for v in all_videos)

    f.write("GLOBAL STATISTICS ACROSS ALL CHANNELS:\n")
    f.write("-" * 50 + "\n")
    f.write(f"Total Videos Analyzed: {total:,}\n")
    f.write(f"Total Views: {total_views:,}\n")
    f.write(f"Total Likes: {total_likes:,}\n")
    f.write(f"Total Comments: {total_comments:,}\n")
    f.write(f"Average Views per Video: {total_views / total:,.0f}\n")
    f.write(f"Average Likes per Video: {total_likes / total:,.0f}\n")
    f.write(f"Average Comments per Video: {total_comments / total:,.0f}\n\n")


def _write_channel_rankings(
    f: TextIOWrapper, channels_data: list[dict[str, Any]]
) -> None:
    """Write channel rankings by engagement metrics."""
    f.write("CHANNEL RANKING BY ENGAGEMENT METRICS:\n")
    f.write("-" * 50 + "\n")

    metrics: list[dict[str, Any]] = []
    for cd in channels_data:
        videos = cd["videos"]
        if not videos:
            continue
        info = cd["channel"]
        sub = _parse_subscriber_count(info.get("subscriber_count"))
        avg_eng = sum(v.get("engagement_rate_views", 0) for v in videos) / len(videos)
        avg_views = sum(v.get("view_count", 0) for v in videos) / len(videos)
        avg_vr = sum(v.get("view_rate", 0) for v in videos) / len(videos)
        metrics.append({
            "name": info["title"],
            "subscribers": sub,
            "avg_engagement": avg_eng,
            "avg_views": avg_views,
            "avg_view_rate": avg_vr,
        })

    metrics.sort(key=lambda x: x["avg_engagement"], reverse=True)
    f.write("BY AVERAGE ENGAGEMENT RATE (Views):\n")
    for i, ch in enumerate(metrics[:10], 1):
        f.write(f"{i:2d}. {ch['name'][:40]:<40} | ")
        f.write(f"Engagement: {ch['avg_engagement']:6.3f}% | ")
        f.write(f"Avg Views: {ch['avg_views']:8,.0f} | ")
        f.write(f"Subscribers: {ch['subscribers']:8,}\n")

    metrics.sort(key=lambda x: x["avg_view_rate"], reverse=True)
    f.write("\nBY AVERAGE VIEW RATE (Views/Subscribers):\n")
    for i, ch in enumerate(metrics[:10], 1):
        f.write(f"{i:2d}. {ch['name'][:40]:<40} | ")
        f.write(f"View Rate: {ch['avg_view_rate']:6.2f}% | ")
        f.write(f"Avg Views: {ch['avg_views']:8,.0f} | ")
        f.write(f"Subscribers: {ch['subscribers']:8,}\n")


def _write_content_patterns(f: TextIOWrapper, all_videos: list[dict[str, Any]]) -> None:
    """Write content performance patterns by duration."""
    settings = get_settings()
    f.write("\nCONTENT PERFORMANCE PATTERNS:\n")
    f.write("-" * 50 + "\n")

    short = [v for v in all_videos if v.get("duration_seconds", 0) < settings.short_video_max]
    medium = [
        v for v in all_videos
        if settings.short_video_max <= v.get("duration_seconds", 0) < settings.long_video_min
    ]
    long = [v for v in all_videos if v.get("duration_seconds", 0) >= settings.long_video_min]

    duration_groups = [
        ("Short (<5min)", short),
        ("Medium (5-15min)", medium),
        ("Long (>15min)", long),
    ]
    for label, group in duration_groups:
        if group:
            avg = sum(v.get("engagement_rate_views", 0) for v in group) / len(group)
            f.write(f"{label}: {len(group):,} videos | Avg Engagement: {avg:.3f}%\n")


def _write_top_content(f: TextIOWrapper, channels_data: list[dict[str, Any]]) -> None:
    """Write top performing content across all channels."""
    f.write("\nTOP PERFORMING CONTENT ACROSS ALL CHANNELS:\n")
    f.write("-" * 50 + "\n")

    all_with_channel: list[dict[str, Any]] = []
    for cd in channels_data:
        name = cd["channel"]["title"]
        for v in cd["videos"]:
            vc = v.copy()
            vc["channel_name"] = name
            all_with_channel.append(vc)

    top_eng = sorted(
        all_with_channel,
        key=lambda x: x.get("engagement_rate_views", 0),
        reverse=True,
    )[:10]
    f.write("TOP 10 VIDEOS BY ENGAGEMENT RATE:\n")
    for i, v in enumerate(top_eng, 1):
        f.write(f"{i:2d}. {v['channel_name']} | {v['title'][:40]}\n")
        f.write(f"     Engagement: {v.get('engagement_rate_views', 0):.3f}% | ")
        f.write(f"Views: {v.get('view_count', 0):,} | ")
        f.write(f"Duration: {v.get('duration_seconds', 0)}s\n")

    viral = sorted(all_with_channel, key=lambda x: x.get("view_rate", 0), reverse=True)[:5]
    f.write("\nTOP 5 VIRAL VIDEOS (High View Rate):\n")
    for i, v in enumerate(viral, 1):
        f.write(f"{i}. {v['channel_name']} | {v['title'][:40]}\n")
        f.write(f"   View Rate: {v.get('view_rate', 0):.2f}% | Views: {v.get('view_count', 0):,}\n")


def _parse_subscriber_count(value: Any) -> int:
    """Parse subscriber count from API response."""
    if not value:
        return 0
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0
