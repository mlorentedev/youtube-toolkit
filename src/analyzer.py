"""YouTube channel analysis and API interaction."""

from typing import List, Dict, Optional, Tuple
import googleapiclient.discovery
from googleapiclient.errors import HttpError

from .config import ENV_API_KEY, get_env, YOUTUBE_API_BATCH_SIZE
from .metrics import calculate_engagement_metrics


class YouTubeChannelAnalyzer:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or get_env(ENV_API_KEY)
        if not self.api_key:
            raise ValueError(f"YouTube API key required. Set {ENV_API_KEY} environment variable.")

        self.youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=self.api_key
        )

    def validate_api_key(self) -> bool:
        """Validate the YouTube API key by making a minimal API call.

        Returns:
            bool: True if API key is valid

        Raises:
            ValueError: If API key is invalid or quota exceeded
            RuntimeError: If API call fails for other reasons
        """
        try:
            request = self.youtube.i18nRegions().list(part="snippet")
            request.execute()
            return True
        except HttpError as e:
            error_content = e.content.decode('utf-8') if e.content else str(e)

            if e.resp.status == 400:
                if 'API key not valid' in error_content or 'invalid' in error_content.lower():
                    raise ValueError(
                        f"Invalid YouTube API key. Please check your {ENV_API_KEY} in .env file.\n"
                        f"Get a valid API key from: https://console.cloud.google.com/apis/credentials"
                    )
                elif 'API key expired' in error_content:
                    raise ValueError(
                        f"YouTube API key has expired. Please generate a new key at:\n"
                        f"https://console.cloud.google.com/apis/credentials"
                    )
                else:
                    raise ValueError(f"API key validation failed: {error_content}")
            elif e.resp.status == 403:
                if 'quotaExceeded' in error_content:
                    raise ValueError(
                        "YouTube API quota exceeded. Your daily quota limit has been reached.\n"
                        "Quota resets at midnight Pacific Time. Try again later or request quota increase."
                    )
                elif 'accessNotConfigured' in error_content:
                    raise ValueError(
                        "YouTube Data API v3 is not enabled for this API key.\n"
                        "Enable it at: https://console.cloud.google.com/apis/library/youtube.googleapis.com"
                    )
                else:
                    raise ValueError(f"API access forbidden: {error_content}")
            else:
                raise RuntimeError(f"API validation failed with status {e.resp.status}: {error_content}")
        except Exception as e:
            if isinstance(e, (ValueError, RuntimeError)):
                raise
            raise RuntimeError(f"Unexpected error validating API key: {str(e)}")

    def get_channel_id_from_username(self, username: str) -> str:
        """Resolve channel ID from legacy username."""
        request = self.youtube.channels().list(
            part="id",
            forUsername=username
        )
        response = request.execute()

        if "items" in response and len(response["items"]) > 0:
            return response["items"][0]["id"]
        raise ValueError(f"No channel found with username: {username}")

    def get_channel_id_from_custom_url(self, custom_url: str) -> str:
        """Resolve channel ID from custom URL (@handle)."""
        if custom_url.startswith('@'):
            custom_url = custom_url[1:]

        request = self.youtube.search().list(
            part="snippet",
            q=custom_url,
            type="channel",
            maxResults=1
        )
        response = request.execute()

        if "items" in response and len(response["items"]) > 0:
            return response["items"][0]["snippet"]["channelId"]
        raise ValueError(f"No channel found with custom URL: @{custom_url}")

    def get_channel_info(self, channel_id: str) -> Dict:
        """Get channel metadata and statistics."""
        request = self.youtube.channels().list(
            part="snippet,statistics",
            id=channel_id
        )
        response = request.execute()

        if "items" not in response or len(response["items"]) == 0:
            raise ValueError(f"No channel found with ID: {channel_id}")

        channel_info = response["items"][0]
        return {
            "id": channel_id,
            "title": channel_info["snippet"]["title"],
            "description": channel_info["snippet"]["description"],
            "subscriber_count": channel_info["statistics"].get("subscriberCount"),
            "video_count": channel_info["statistics"].get("videoCount"),
            "view_count": channel_info["statistics"].get("viewCount"),
            "thumbnail": channel_info["snippet"]["thumbnails"]["default"]["url"],
            "url": f"https://www.youtube.com/channel/{channel_id}"
        }

    def get_channel_videos(
        self,
        channel_id: Optional[str] = None,
        username: Optional[str] = None,
        custom_url: Optional[str] = None,
        max_results: int = 50
    ) -> Tuple[Dict, List[Dict]]:
        """Get videos from a channel with statistics."""
        if channel_id is None and username is None and custom_url is None:
            raise ValueError("Must provide channel_id, username, or custom_url")

        if channel_id is None:
            if username:
                channel_id = self.get_channel_id_from_username(username)
            elif custom_url:
                channel_id = self.get_channel_id_from_custom_url(custom_url)

        channel_info = self.get_channel_info(channel_id)

        request = self.youtube.channels().list(
            part="contentDetails",
            id=channel_id
        )
        response = request.execute()

        if "items" not in response or len(response["items"]) == 0:
            raise ValueError(f"No channel found with ID: {channel_id}")

        uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        videos = []
        next_page_token = None

        while len(videos) < max_results:
            request = self.youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=uploads_playlist_id,
                maxResults=min(50, max_results - len(videos)),
                pageToken=next_page_token
            )
            response = request.execute()

            for item in response["items"]:
                video_info = {
                    "id": item["contentDetails"]["videoId"],
                    "title": item["snippet"]["title"],
                    "published_at": item["snippet"]["publishedAt"],
                    "url": f"https://www.youtube.com/watch?v={item['contentDetails']['videoId']}"
                }
                videos.append(video_info)

            next_page_token = response.get("nextPageToken")
            if not next_page_token or len(videos) >= max_results:
                break

        videos_with_stats = self.get_videos_statistics(videos)

        return channel_info, videos_with_stats

    def get_videos_statistics(self, videos: List[Dict]) -> List[Dict]:
        """Fetch detailed statistics for videos in batches."""
        if not videos:
            return videos

        videos_with_stats = []

        for i in range(0, len(videos), YOUTUBE_API_BATCH_SIZE):
            batch = videos[i:i+YOUTUBE_API_BATCH_SIZE]
            video_ids = [video['id'] for video in batch]

            request = self.youtube.videos().list(
                part="statistics,contentDetails",
                id=','.join(video_ids)
            )
            response = request.execute()

            stats_map = {}
            for item in response.get('items', []):
                stats_map[item['id']] = {
                    'statistics': item.get('statistics', {}),
                    'contentDetails': item.get('contentDetails', {})
                }

            for video in batch:
                video_id = video['id']
                if video_id in stats_map:
                    stats = stats_map[video_id]['statistics']
                    content_details = stats_map[video_id]['contentDetails']

                    video.update({
                        'view_count': int(stats.get('viewCount', 0)),
                        'like_count': int(stats.get('likeCount', 0)),
                        'comment_count': int(stats.get('commentCount', 0)),
                        'duration': content_details.get('duration', 'PT0S')
                    })
                else:
                    video.update({
                        'view_count': 0,
                        'like_count': 0,
                        'comment_count': 0,
                        'duration': 'PT0S'
                    })

                videos_with_stats.append(video)

        return videos_with_stats

    def get_multiple_channels_videos(
        self,
        channel_list: List[Dict],
        max_results_per_channel: int = 20
    ) -> List[Dict]:
        """Get videos from multiple channels with engagement metrics."""
        all_channels_data = []
        failed_channels = []

        for channel in channel_list:
            try:
                channel_id = channel.get('channel_id')
                username = channel.get('username')
                custom_url = channel.get('custom_url')

                channel_info, videos = self.get_channel_videos(
                    channel_id=channel_id,
                    username=username,
                    custom_url=custom_url,
                    max_results=max_results_per_channel
                )

                subscriber_count = int(channel_info.get('subscriber_count', 0) or 0)
                videos_with_metrics = calculate_engagement_metrics(videos, subscriber_count)

                all_channels_data.append({
                    "channel": channel_info,
                    "videos": videos_with_metrics
                })

                print(f"Retrieved {len(videos)} videos from {channel_info['title']}")

            except Exception as e:
                failed_channels.append({'channel': channel, 'error': str(e)})
                print(f"Error retrieving channel {channel}: {e}")

        if failed_channels:
            print(f"\nFailed to retrieve {len(failed_channels)} channels:")
            for item in failed_channels:
                print(f"  - {item['channel']}: {item['error']}")

        return all_channels_data
