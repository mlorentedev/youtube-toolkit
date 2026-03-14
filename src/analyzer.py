"""YouTube channel analysis and API interaction."""

import logging
from typing import Any

import googleapiclient.discovery
from googleapiclient.errors import HttpError

from .config import get_settings
from .metrics import calculate_engagement_metrics

logger = logging.getLogger(__name__)


class YouTubeChannelAnalyzer:
    def __init__(self, api_key: str | None = None) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.youtube_api_key
        if not self.api_key:
            msg = (
                "YouTube API key required. "
                "Set YOUTUBE_API_KEY environment variable or pass it directly."
            )
            raise ValueError(msg)

        self.youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=self.api_key
        )

    def validate_api_key(self) -> bool:
        """Validate the YouTube API key by making a minimal API call."""
        try:
            request = self.youtube.i18nRegions().list(part="snippet")
            request.execute()
            return True
        except HttpError as e:
            error_content = e.content.decode("utf-8") if e.content else str(e)
            if e.resp.status == 400:
                self._handle_400_error(error_content, e)
            elif e.resp.status == 403:
                self._handle_403_error(error_content, e)
            else:
                msg = f"API validation failed with status {e.resp.status}: {error_content}"
                raise RuntimeError(msg) from e
        except (ValueError, RuntimeError):
            raise
        except Exception as e:
            msg = f"Unexpected error validating API key: {e}"
            raise RuntimeError(msg) from e
        return False  # unreachable but satisfies mypy

    def get_channel_id_from_username(self, username: str) -> str:
        """Resolve channel ID from legacy username."""
        request = self.youtube.channels().list(part="id", forUsername=username)
        response: dict[str, Any] = request.execute()

        if "items" in response and len(response["items"]) > 0:
            return str(response["items"][0]["id"])
        msg = f"No channel found with username: {username}"
        raise ValueError(msg)

    def get_channel_id_from_custom_url(self, custom_url: str) -> str:
        """Resolve channel ID from custom URL (@handle)."""
        if custom_url.startswith("@"):
            custom_url = custom_url[1:]

        request = self.youtube.search().list(
            part="snippet", q=custom_url, type="channel", maxResults=1
        )
        response: dict[str, Any] = request.execute()

        if "items" in response and len(response["items"]) > 0:
            return str(response["items"][0]["snippet"]["channelId"])
        msg = f"No channel found with custom URL: @{custom_url}"
        raise ValueError(msg)

    def get_channel_info(self, channel_id: str) -> dict[str, Any]:
        """Get channel metadata and statistics."""
        request = self.youtube.channels().list(part="snippet,statistics", id=channel_id)
        response: dict[str, Any] = request.execute()

        if "items" not in response or len(response["items"]) == 0:
            msg = f"No channel found with ID: {channel_id}"
            raise ValueError(msg)

        channel_item = response["items"][0]
        return {
            "id": channel_id,
            "title": channel_item["snippet"]["title"],
            "description": channel_item["snippet"]["description"],
            "subscriber_count": channel_item["statistics"].get("subscriberCount"),
            "video_count": channel_item["statistics"].get("videoCount"),
            "view_count": channel_item["statistics"].get("viewCount"),
            "thumbnail": channel_item["snippet"]["thumbnails"]["default"]["url"],
            "url": f"https://www.youtube.com/channel/{channel_id}",
        }

    def get_channel_videos(
        self,
        channel_id: str | None = None,
        username: str | None = None,
        custom_url: str | None = None,
        max_results: int = 50,
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """Get videos from a channel with statistics."""
        if channel_id is None and username is None and custom_url is None:
            msg = "Must provide channel_id, username, or custom_url"
            raise ValueError(msg)

        if channel_id is None:
            if username:
                channel_id = self.get_channel_id_from_username(username)
            elif custom_url:
                channel_id = self.get_channel_id_from_custom_url(custom_url)

        assert channel_id is not None  # guaranteed by logic above
        channel_info = self.get_channel_info(channel_id)
        uploads_playlist_id = self._get_uploads_playlist(channel_id)
        videos = self._fetch_playlist_videos(uploads_playlist_id, max_results)
        videos_with_stats = self._get_videos_statistics(videos)

        return channel_info, videos_with_stats

    def get_multiple_channels_videos(
        self,
        channel_list: list[dict[str, Any]],
        max_results_per_channel: int = 20,
    ) -> list[dict[str, Any]]:
        """Get videos from multiple channels with engagement metrics."""
        all_channels_data: list[dict[str, Any]] = []
        failed_channels: list[dict[str, Any]] = []

        for channel in channel_list:
            try:
                channel_info, videos = self.get_channel_videos(
                    channel_id=channel.get("channel_id"),
                    username=channel.get("username"),
                    custom_url=channel.get("custom_url"),
                    max_results=max_results_per_channel,
                )

                subscriber_count = int(channel_info.get("subscriber_count", 0) or 0)
                videos_with_metrics = calculate_engagement_metrics(videos, subscriber_count)

                all_channels_data.append({"channel": channel_info, "videos": videos_with_metrics})
                logger.info("Retrieved %d videos from %s", len(videos), channel_info["title"])

            except Exception as e:
                failed_channels.append({"channel": channel, "error": str(e)})
                logger.warning("Error retrieving channel %s: %s", channel, e)

        if failed_channels:
            logger.warning("Failed to retrieve %d channels", len(failed_channels))

        return all_channels_data

    # --- Private helpers ---

    def _get_uploads_playlist(self, channel_id: str) -> str:
        """Get the uploads playlist ID for a channel."""
        request = self.youtube.channels().list(part="contentDetails", id=channel_id)
        response: dict[str, Any] = request.execute()

        if "items" not in response or len(response["items"]) == 0:
            msg = f"No channel found with ID: {channel_id}"
            raise ValueError(msg)

        return str(
            response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        )

    def _fetch_playlist_videos(
        self, playlist_id: str, max_results: int
    ) -> list[dict[str, Any]]:
        """Fetch video IDs and metadata from a playlist."""
        videos: list[dict[str, Any]] = []
        next_page_token: str | None = None

        while len(videos) < max_results:
            request = self.youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=playlist_id,
                maxResults=min(50, max_results - len(videos)),
                pageToken=next_page_token,
            )
            response: dict[str, Any] = request.execute()

            for item in response["items"]:
                video_id = item["contentDetails"]["videoId"]
                videos.append(
                    {
                        "id": video_id,
                        "title": item["snippet"]["title"],
                        "published_at": item["snippet"]["publishedAt"],
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                    }
                )

            next_page_token = response.get("nextPageToken")
            if not next_page_token or len(videos) >= max_results:
                break

        return videos

    def _get_videos_statistics(
        self, videos: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Fetch detailed statistics for videos in batches."""
        if not videos:
            return videos

        settings = get_settings()
        videos_with_stats: list[dict[str, Any]] = []

        for i in range(0, len(videos), settings.api_batch_size):
            batch = videos[i : i + settings.api_batch_size]
            video_ids = [video["id"] for video in batch]

            request = self.youtube.videos().list(
                part="statistics,contentDetails", id=",".join(video_ids)
            )
            response: dict[str, Any] = request.execute()

            stats_map: dict[str, dict[str, Any]] = {}
            for item in response.get("items", []):
                stats_map[item["id"]] = {
                    "statistics": item.get("statistics", {}),
                    "contentDetails": item.get("contentDetails", {}),
                }

            for video in batch:
                vid = video["id"]
                if vid in stats_map:
                    stats = stats_map[vid]["statistics"]
                    content = stats_map[vid]["contentDetails"]
                    video.update(
                        {
                            "view_count": int(stats.get("viewCount", 0)),
                            "like_count": int(stats.get("likeCount", 0)),
                            "comment_count": int(stats.get("commentCount", 0)),
                            "duration": content.get("duration", "PT0S"),
                        }
                    )
                else:
                    video.update(
                        {
                            "view_count": 0,
                            "like_count": 0,
                            "comment_count": 0,
                            "duration": "PT0S",
                        }
                    )
                videos_with_stats.append(video)

        return videos_with_stats

    @staticmethod
    def _handle_400_error(error_content: str, original: HttpError) -> None:
        """Handle HTTP 400 errors from the YouTube API."""
        if "API key not valid" in error_content or "invalid" in error_content.lower():
            msg = (
                "Invalid YouTube API key. Check your YOUTUBE_API_KEY in .env file.\n"
                "Get a valid key: https://console.cloud.google.com/apis/credentials"
            )
            raise ValueError(msg) from original
        if "API key expired" in error_content:
            msg = (
                "YouTube API key has expired. Generate a new key at:\n"
                "https://console.cloud.google.com/apis/credentials"
            )
            raise ValueError(msg) from original
        msg = f"API key validation failed: {error_content}"
        raise ValueError(msg) from original

    @staticmethod
    def _handle_403_error(error_content: str, original: HttpError) -> None:
        """Handle HTTP 403 errors from the YouTube API."""
        if "quotaExceeded" in error_content:
            msg = (
                "YouTube API quota exceeded. Daily limit reached.\n"
                "Quota resets at midnight Pacific Time. Try again later."
            )
            raise ValueError(msg) from original
        if "accessNotConfigured" in error_content:
            msg = (
                "YouTube Data API v3 is not enabled for this key.\n"
                "Enable: https://console.cloud.google.com/apis/library/youtube.googleapis.com"
            )
            raise ValueError(msg) from original
        msg = f"API access forbidden: {error_content}"
        raise ValueError(msg) from original
