"""Export functionality for channel data and reports."""

import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from .config import format_number, SHORT_VIDEO_MAX, MEDIUM_VIDEO_MAX


def export_to_csv(channels_data: List[Dict], filename: str):
    """Export channel and video data to CSV."""
    if not channels_data:
        print("No data to export.")
        return

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow([
            "Channel", "Subscribers", "Video Title", "Published Date", "Video URL",
            "Views", "Likes", "Comments", "Duration (seconds)",
            "Engagement Rate (Views %)", "Engagement Rate (Subscribers %)",
            "View Rate (%)", "Like Rate (%)", "Comment Rate (%)", "Views per Minute"
        ])

        for channel_data in channels_data:
            channel_info = channel_data["channel"]
            videos = channel_data["videos"]

            channel_name = channel_info["title"]
            subscriber_count = channel_info.get("subscriber_count", "N/A")

            for video in videos:
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
                    video.get("views_per_minute", 0)
                ])

    total_videos = sum(len(channel_data["videos"]) for channel_data in channels_data)
    print(f"Exported {total_videos} videos from {len(channels_data)} channels to {filename}")


def export_channel_stats(channels_data: List[Dict], filename: str):
    """Export detailed channel statistics to text file."""
    if not channels_data:
        print("No data to export.")
        return

    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(f"YOUTUBE CHANNEL STATISTICS REPORT\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")

        for channel_data in channels_data:
            channel_info = channel_data["channel"]
            videos = channel_data["videos"]

            video_count = len(videos)
            earliest_video = min(videos, key=lambda x: x["published_at"]) if videos else None
            latest_video = max(videos, key=lambda x: x["published_at"]) if videos else None

            subscriber_count = format_number(channel_info.get("subscriber_count"))
            view_count = format_number(channel_info.get("view_count"))
            total_video_count = format_number(channel_info.get("video_count"))

            f.write("-" * 80 + "\n")
            f.write(f"CHANNEL: {channel_info['title']}\n")
            f.write("-" * 80 + "\n")
            f.write(f"URL: {channel_info['url']}\n")
            f.write(f"Subscribers: {subscriber_count}\n")
            f.write(f"Total Views: {view_count}\n")
            f.write(f"Total Videos: {total_video_count}\n")
            description = channel_info['description'][:100]
            if len(channel_info['description']) > 100:
                description += '...'
            f.write(f"Description: {description}\n\n")

            f.write(f"ANALYZED VIDEOS: {video_count}\n")
            if earliest_video:
                f.write(f"Earliest Video Date: {earliest_video['published_at'].split('T')[0]}\n")
            if latest_video:
                f.write(f"Latest Video Date: {latest_video['published_at'].split('T')[0]}\n")

            if video_count > 1 and earliest_video and latest_video:
                start_date = datetime.fromisoformat(earliest_video['published_at'].replace('Z', '+00:00'))
                end_date = datetime.fromisoformat(latest_video['published_at'].replace('Z', '+00:00'))
                days_diff = (end_date - start_date).days
                if days_diff > 0:
                    uploads_per_month = (video_count / days_diff) * 30
                    f.write(f"Estimated Upload Frequency: {uploads_per_month:.1f} videos per month\n")

            f.write("\nENGAGEMENT METRICS ANALYSIS:\n")

            if videos:
                total_views = sum(video.get('view_count', 0) for video in videos)
                total_likes = sum(video.get('like_count', 0) for video in videos)
                total_comments = sum(video.get('comment_count', 0) for video in videos)
                avg_views = total_views / video_count if video_count > 0 else 0
                avg_likes = total_likes / video_count if video_count > 0 else 0
                avg_comments = total_comments / video_count if video_count > 0 else 0

                avg_engagement_views = sum(video.get('engagement_rate_views', 0) for video in videos) / video_count if video_count > 0 else 0
                avg_engagement_subscribers = sum(video.get('engagement_rate_subscribers', 0) for video in videos) / video_count if video_count > 0 else 0
                avg_view_rate = sum(video.get('view_rate', 0) for video in videos) / video_count if video_count > 0 else 0
                avg_like_rate = sum(video.get('like_rate', 0) for video in videos) / video_count if video_count > 0 else 0
                avg_comment_rate = sum(video.get('comment_rate', 0) for video in videos) / video_count if video_count > 0 else 0

                f.write(f"Average Views per Video: {avg_views:,.0f}\n")
                f.write(f"Average Likes per Video: {avg_likes:,.0f}\n")
                f.write(f"Average Comments per Video: {avg_comments:,.0f}\n")
                f.write(f"Average Engagement Rate (by Views): {avg_engagement_views:.3f}%\n")
                f.write(f"Average Engagement Rate (by Subscribers): {avg_engagement_subscribers:.3f}%\n")
                f.write(f"Average View Rate: {avg_view_rate:.2f}%\n")
                f.write(f"Average Like Rate: {avg_like_rate:.3f}%\n")
                f.write(f"Average Comment Rate: {avg_comment_rate:.3f}%\n")

                top_viewed = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)[:5]
                top_engaged = sorted(videos, key=lambda x: x.get('engagement_rate_views', 0), reverse=True)[:5]

                f.write(f"\nTOP 5 MOST VIEWED VIDEOS:\n")
                for i, video in enumerate(top_viewed, 1):
                    views = video.get('view_count', 0)
                    engagement = video.get('engagement_rate_views', 0)
                    title = video['title'][:60]
                    if len(video['title']) > 60:
                        title += '...'
                    f.write(f"{i}. {title}\n")
                    f.write(f"   Views: {views:,} | Engagement: {engagement:.3f}%\n")

                f.write(f"\nTOP 5 HIGHEST ENGAGEMENT VIDEOS:\n")
                for i, video in enumerate(top_engaged, 1):
                    views = video.get('view_count', 0)
                    engagement = video.get('engagement_rate_views', 0)
                    title = video['title'][:60]
                    if len(video['title']) > 60:
                        title += '...'
                    f.write(f"{i}. {title}\n")
                    f.write(f"   Views: {views:,} | Engagement: {engagement:.3f}%\n")

                high_performing_videos = [v for v in videos if v.get('engagement_rate_views', 0) > avg_engagement_views * 1.5]
                low_performing_videos = [v for v in videos if v.get('engagement_rate_views', 0) < avg_engagement_views * 0.5]

                f.write(f"\nPERFORMANCE DISTRIBUTION:\n")
                f.write(f"High Performing Videos (>1.5x avg engagement): {len(high_performing_videos)} ({len(high_performing_videos)/video_count*100:.1f}%)\n")
                f.write(f"Low Performing Videos (<0.5x avg engagement): {len(low_performing_videos)} ({len(low_performing_videos)/video_count*100:.1f}%)\n")

            f.write(f"\nRECENT VIDEOS WITH METRICS:\n")
            recent_videos = sorted(videos, key=lambda x: x["published_at"], reverse=True)[:5]
            for i, video in enumerate(recent_videos, 1):
                published_date = video["published_at"].split("T")[0]
                views = video.get('view_count', 0)
                engagement = video.get('engagement_rate_views', 0)
                title = video['title'][:50]
                if len(video['title']) > 50:
                    title += '...'
                f.write(f"{i}. {title} ({published_date})\n")
                f.write(f"   Views: {views:,} | Engagement: {engagement:.3f}% | Duration: {video.get('duration_seconds', 0)}s\n")

            f.write("\n\n")

        f.write("=" * 80 + "\n")
        f.write(f"End of Report - {len(channels_data)} channels analyzed\n")
        f.write("=" * 80 + "\n")

    print(f"Exported channel statistics for {len(channels_data)} channels to {filename}")


def export_engagement_trends_report(channels_data: List[Dict], filename: str):
    """Export comprehensive engagement trends analysis."""
    if not channels_data:
        print("No data to export.")
        return

    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write(f"YOUTUBE ENGAGEMENT TRENDS ANALYSIS REPORT\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 100 + "\n\n")

        all_videos = []
        for channel_data in channels_data:
            all_videos.extend(channel_data["videos"])

        if not all_videos:
            f.write("No videos found for analysis.\n")
            return

        total_videos = len(all_videos)
        total_views = sum(video.get('view_count', 0) for video in all_videos)
        total_likes = sum(video.get('like_count', 0) for video in all_videos)
        total_comments = sum(video.get('comment_count', 0) for video in all_videos)

        f.write("GLOBAL STATISTICS ACROSS ALL CHANNELS:\n")
        f.write("-" * 50 + "\n")
        f.write(f"Total Videos Analyzed: {total_videos:,}\n")
        f.write(f"Total Views: {total_views:,}\n")
        f.write(f"Total Likes: {total_likes:,}\n")
        f.write(f"Total Comments: {total_comments:,}\n")
        f.write(f"Average Views per Video: {total_views/total_videos:,.0f}\n")
        f.write(f"Average Likes per Video: {total_likes/total_videos:,.0f}\n")
        f.write(f"Average Comments per Video: {total_comments/total_videos:,.0f}\n\n")

        f.write("CHANNEL RANKING BY ENGAGEMENT METRICS:\n")
        f.write("-" * 50 + "\n")

        channel_metrics = []
        for channel_data in channels_data:
            channel_info = channel_data["channel"]
            videos = channel_data["videos"]

            if videos:
                avg_engagement = sum(video.get('engagement_rate_views', 0) for video in videos) / len(videos)
                avg_views = sum(video.get('view_count', 0) for video in videos) / len(videos)
                avg_view_rate = sum(video.get('view_rate', 0) for video in videos) / len(videos)

                subscriber_count = channel_info.get('subscriber_count')
                if subscriber_count:
                    try:
                        subscriber_count = int(subscriber_count)
                    except (ValueError, TypeError):
                        subscriber_count = 0
                else:
                    subscriber_count = 0

                channel_metrics.append({
                    'name': channel_info['title'],
                    'subscribers': subscriber_count,
                    'video_count': len(videos),
                    'avg_engagement': avg_engagement,
                    'avg_views': avg_views,
                    'avg_view_rate': avg_view_rate
                })

        channel_metrics.sort(key=lambda x: x['avg_engagement'], reverse=True)

        f.write("BY AVERAGE ENGAGEMENT RATE (Views):\n")
        for i, channel in enumerate(channel_metrics[:10], 1):
            f.write(f"{i:2d}. {channel['name'][:40]:<40} | ")
            f.write(f"Engagement: {channel['avg_engagement']:6.3f}% | ")
            f.write(f"Avg Views: {channel['avg_views']:8,.0f} | ")
            f.write(f"Subscribers: {channel['subscribers']:8,}\n")

        f.write(f"\nBY AVERAGE VIEW RATE (Views/Subscribers):\n")
        channel_metrics.sort(key=lambda x: x['avg_view_rate'], reverse=True)
        for i, channel in enumerate(channel_metrics[:10], 1):
            f.write(f"{i:2d}. {channel['name'][:40]:<40} | ")
            f.write(f"View Rate: {channel['avg_view_rate']:6.2f}% | ")
            f.write(f"Avg Views: {channel['avg_views']:8,.0f} | ")
            f.write(f"Subscribers: {channel['subscribers']:8,}\n")

        f.write(f"\nCONTENT PERFORMANCE PATTERNS:\n")
        f.write("-" * 50 + "\n")

        short_videos = [v for v in all_videos if v.get('duration_seconds', 0) < SHORT_VIDEO_MAX]
        medium_videos = [v for v in all_videos if SHORT_VIDEO_MAX <= v.get('duration_seconds', 0) < MEDIUM_VIDEO_MAX]
        long_videos = [v for v in all_videos if v.get('duration_seconds', 0) >= MEDIUM_VIDEO_MAX]

        if short_videos:
            avg_engagement_short = sum(v.get('engagement_rate_views', 0) for v in short_videos) / len(short_videos)
            f.write(f"Short Videos (<5min): {len(short_videos):,} videos | Avg Engagement: {avg_engagement_short:.3f}%\n")

        if medium_videos:
            avg_engagement_medium = sum(v.get('engagement_rate_views', 0) for v in medium_videos) / len(medium_videos)
            f.write(f"Medium Videos (5-15min): {len(medium_videos):,} videos | Avg Engagement: {avg_engagement_medium:.3f}%\n")

        if long_videos:
            avg_engagement_long = sum(v.get('engagement_rate_views', 0) for v in long_videos) / len(long_videos)
            f.write(f"Long Videos (>15min): {len(long_videos):,} videos | Avg Engagement: {avg_engagement_long:.3f}%\n")

        f.write(f"\nTOP PERFORMING CONTENT ACROSS ALL CHANNELS:\n")
        f.write("-" * 50 + "\n")

        all_videos_with_channel = []
        for channel_data in channels_data:
            channel_name = channel_data["channel"]["title"]
            for video in channel_data["videos"]:
                video_copy = video.copy()
                video_copy['channel_name'] = channel_name
                all_videos_with_channel.append(video_copy)

        top_engagement = sorted(all_videos_with_channel, key=lambda x: x.get('engagement_rate_views', 0), reverse=True)[:10]
        f.write("TOP 10 VIDEOS BY ENGAGEMENT RATE:\n")
        for i, video in enumerate(top_engagement, 1):
            f.write(f"{i:2d}. {video['channel_name']} | {video['title'][:40]}\n")
            f.write(f"     Engagement: {video.get('engagement_rate_views', 0):.3f}% | ")
            f.write(f"Views: {video.get('view_count', 0):,} | ")
            f.write(f"Duration: {video.get('duration_seconds', 0)}s\n")

        viral_videos = sorted(all_videos_with_channel, key=lambda x: x.get('view_rate', 0), reverse=True)[:5]
        f.write(f"\nTOP 5 VIRAL VIDEOS (High View Rate):\n")
        for i, video in enumerate(viral_videos, 1):
            f.write(f"{i}. {video['channel_name']} | {video['title'][:40]}\n")
            f.write(f"   View Rate: {video.get('view_rate', 0):.2f}% | ")
            f.write(f"Views: {video.get('view_count', 0):,}\n")

        f.write("\n" + "=" * 100 + "\n")
        f.write(f"End of Engagement Trends Report\n")
        f.write("=" * 100 + "\n")

    print(f"Exported engagement trends analysis to {filename}")


def export_best_videos_report(channels_data: List[Dict], filename: str, top_n: int = 15):
    """Export top N best videos by engagement rate for each channel."""
    if not channels_data:
        print("No data to export.")
        return

    with open(filename, 'w', encoding='utf-8') as f:
        for channel_data in channels_data:
            videos = channel_data["videos"]
            if videos:
                best_videos = sorted(videos, key=lambda x: x.get('engagement_rate_views', 0), reverse=True)[:top_n]
                for video in best_videos:
                    f.write(f"{video['url']}\n")

    print(f"Exported top {top_n} best videos report to {filename}")


def export_latest_videos_report(channels_data: List[Dict], filename: str, top_n: int = 15):
    """Export top N latest videos for each channel."""
    if not channels_data:
        print("No data to export.")
        return

    with open(filename, 'w', encoding='utf-8') as f:
        for channel_data in channels_data:
            videos = channel_data["videos"]
            if videos:
                latest_videos = sorted(videos, key=lambda x: x.get('published_at', ''), reverse=True)[:top_n]
                for video in latest_videos:
                    f.write(f"{video['url']}\n")

    print(f"Exported top {top_n} latest videos report to {filename}")


def export_output_readme(output_dir: Path, timestamp: str, channels_data: List[Dict]):
    """Generate README.md in output directory explaining all generated files."""
    readme_path = output_dir / "README.md"

    total_channels = len(channels_data)
    total_videos = sum(len(cd["videos"]) for cd in channels_data)

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(f"# YouTube Analysis Report - {timestamp}\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}\n\n")

        f.write(f"## Analysis Summary\n\n")
        f.write(f"- **Channels Analyzed:** {total_channels}\n")
        f.write(f"- **Total Videos:** {total_videos}\n")
        f.write(f"- **Average Videos per Channel:** {total_videos / total_channels if total_channels > 0 else 0:.1f}\n\n")

        f.write(f"## Generated Files\n\n")

        f.write(f"### `youtube_channels_videos_{timestamp}.csv`\n")
        f.write(f"**Format:** CSV (Comma-Separated Values)\n\n")
        f.write(f"**Description:** Raw data export containing all videos from all analyzed channels with complete metrics.\n\n")
        f.write(f"**Columns:**\n")
        f.write(f"- Channel name and subscriber count\n")
        f.write(f"- Video title, published date, and URL\n")
        f.write(f"- Raw statistics: views, likes, comments, duration (seconds)\n")
        f.write(f"- Calculated metrics: engagement rates, view rate, like rate, comment rate, views per minute\n\n")
        f.write(f"**Use Cases:**\n")
        f.write(f"- Import into Excel/Google Sheets for custom analysis\n")
        f.write(f"- Data visualization with BI tools\n")
        f.write(f"- Further processing with pandas/R\n\n")

        f.write(f"---\n\n")

        f.write(f"### `youtube_channel_stats_{timestamp}.txt`\n")
        f.write(f"**Format:** Plain text report\n\n")
        f.write(f"**Description:** Detailed statistics for each analyzed channel including:\n\n")
        f.write(f"**Per Channel:**\n")
        f.write(f"- Channel metadata (subscribers, total views, total videos)\n")
        f.write(f"- Upload frequency analysis\n")
        f.write(f"- Average engagement metrics across all videos\n")
        f.write(f"- Top 5 most viewed videos\n")
        f.write(f"- Top 5 highest engagement videos\n")
        f.write(f"- Performance distribution (high vs. low performing videos)\n")
        f.write(f"- Recent videos with metrics\n\n")
        f.write(f"**Use Cases:**\n")
        f.write(f"- Quick overview of individual channel performance\n")
        f.write(f"- Identify content patterns and trends\n")
        f.write(f"- Compare channel metrics over time\n\n")

        f.write(f"---\n\n")

        f.write(f"### `youtube_engagement_trends_{timestamp}.txt`\n")
        f.write(f"**Format:** Plain text report\n\n")
        f.write(f"**Description:** Cross-channel comparison and trend analysis including:\n\n")
        f.write(f"**Global Analysis:**\n")
        f.write(f"- Aggregate statistics across all channels\n")
        f.write(f"- Channel rankings by engagement rate\n")
        f.write(f"- Channel rankings by view rate\n")
        f.write(f"- Content performance by duration (short vs. medium vs. long videos)\n")
        f.write(f"- Top 10 videos by engagement across all channels\n")
        f.write(f"- Top 5 viral videos (highest view rates)\n\n")
        f.write(f"**Use Cases:**\n")
        f.write(f"- Compare channels against each other\n")
        f.write(f"- Identify industry benchmarks\n")
        f.write(f"- Discover viral content patterns\n")
        f.write(f"- Optimize content strategy based on trends\n\n")

        f.write(f"---\n\n")

        f.write(f"### `youtube_best_videos_{timestamp}.txt`\n")
        f.write(f"**Format:** Plain text (URL list)\n\n")
        f.write(f"**Description:** Top 15 videos with highest engagement rate from each channel.\n\n")
        f.write(f"**Content:**\n")
        f.write(f"- One YouTube URL per line\n")
        f.write(f"- Sorted by engagement rate (descending)\n")
        f.write(f"- Up to 15 videos per channel\n\n")
        f.write(f"**Use Cases:**\n")
        f.write(f"- Quick access to best-performing content\n")
        f.write(f"- Content inspiration and research\n")
        f.write(f"- Batch processing URLs with other tools\n")
        f.write(f"- Create playlists or reference libraries\n\n")

        f.write(f"---\n\n")

        f.write(f"### `youtube_latest_videos_{timestamp}.txt`\n")
        f.write(f"**Format:** Plain text (URL list)\n\n")
        f.write(f"**Description:** 15 most recent videos from each channel.\n\n")
        f.write(f"**Content:**\n")
        f.write(f"- One YouTube URL per line\n")
        f.write(f"- Sorted by published date (newest first)\n")
        f.write(f"- Up to 15 videos per channel\n\n")
        f.write(f"**Use Cases:**\n")
        f.write(f"- Track recent content from competitors/peers\n")
        f.write(f"- Identify current content trends\n")
        f.write(f"- Monitor channel activity\n")
        f.write(f"- Research latest topics and formats\n\n")

        f.write(f"---\n\n")

        f.write(f"## Engagement Metrics Explained\n\n")
        f.write(f"All reports include the following calculated metrics:\n\n")
        f.write(f"| Metric | Formula | Interpretation |\n")
        f.write(f"|--------|---------|----------------|\n")
        f.write(f"| **Engagement Rate (Views)** | `(likes + comments) / views × 100` | Higher = more audience interaction |\n")
        f.write(f"| **Engagement Rate (Subscribers)** | `(likes + comments) / subscribers × 100` | Engagement relative to channel size |\n")
        f.write(f"| **View Rate** | `views / subscribers × 100` | >100% indicates viral potential |\n")
        f.write(f"| **Like Rate** | `likes / views × 100` | Viewer satisfaction indicator |\n")
        f.write(f"| **Comment Rate** | `comments / views × 100` | Audience discussion level |\n")
        f.write(f"| **Views per Minute** | `views / (duration / 60)` | Content efficiency metric |\n\n")

        f.write(f"## Channels Analyzed\n\n")
        for i, channel_data in enumerate(channels_data, 1):
            channel_info = channel_data["channel"]
            video_count = len(channel_data["videos"])
            subscribers = format_number(channel_info.get('subscriber_count'))
            f.write(f"{i}. **{channel_info['title']}** - {subscribers} subscribers ({video_count} videos analyzed)\n")

        f.write(f"\n---\n\n")
        f.write(f"*Generated by YouTube Toolkit*\n")

    print(f"Generated README.md in output directory: {readme_path}")
