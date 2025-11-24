"""Engagement metrics calculation."""

import re
from typing import List, Dict


def parse_duration(duration: str) -> int:
    """Parse YouTube duration format (PT#H#M#S) to seconds."""
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration)

    if not match:
        return 0

    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)

    return hours * 3600 + minutes * 60 + seconds


def calculate_engagement_metrics(videos: List[Dict], subscriber_count: int) -> List[Dict]:
    """Calculate engagement metrics for videos."""
    enhanced_videos = []

    for video in videos:
        enhanced_video = video.copy()

        view_count = video.get('view_count', 0)
        like_count = video.get('like_count', 0)
        comment_count = video.get('comment_count', 0)

        engagement_rate_views = 0
        if view_count > 0:
            engagement_rate_views = ((like_count + comment_count) / view_count) * 100

        engagement_rate_subscribers = 0
        if subscriber_count > 0:
            engagement_rate_subscribers = ((like_count + comment_count) / subscriber_count) * 100

        view_rate = 0
        if subscriber_count > 0:
            view_rate = (view_count / subscriber_count) * 100

        like_rate = 0
        if view_count > 0:
            like_rate = (like_count / view_count) * 100

        comment_rate = 0
        if view_count > 0:
            comment_rate = (comment_count / view_count) * 100

        duration_seconds = parse_duration(video.get('duration', 'PT0S'))

        views_per_minute = 0
        if duration_seconds > 0:
            views_per_minute = view_count / (duration_seconds / 60)

        enhanced_video.update({
            'engagement_rate_views': round(engagement_rate_views, 3),
            'engagement_rate_subscribers': round(engagement_rate_subscribers, 3),
            'view_rate': round(view_rate, 2),
            'like_rate': round(like_rate, 3),
            'comment_rate': round(comment_rate, 3),
            'duration_seconds': duration_seconds,
            'views_per_minute': round(views_per_minute, 2)
        })

        enhanced_videos.append(enhanced_video)

    return enhanced_videos
