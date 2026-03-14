"""Shared test fixtures for youtube-toolkit."""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from src.config import reset_settings


@pytest.fixture(autouse=True)
def _clean_settings() -> Any:
    """Reset cached settings before each test."""
    reset_settings()
    yield
    reset_settings()


@pytest.fixture()
def env_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set a fake YouTube API key in the environment."""
    monkeypatch.setenv("YOUTUBE_API_KEY", "fake_test_api_key_123")


@pytest.fixture()
def sample_channel_response() -> dict[str, Any]:
    """Realistic YouTube channels().list() API response."""
    return {
        "items": [
            {
                "id": "UC_test_channel_id",
                "snippet": {
                    "title": "Test Channel",
                    "description": "A test channel for unit testing",
                    "customUrl": "@testchannel",
                    "thumbnails": {"default": {"url": "https://example.com/thumb.jpg"}},
                },
                "statistics": {
                    "subscriberCount": "100000",
                    "viewCount": "5000000",
                    "videoCount": "200",
                },
                "contentDetails": {
                    "relatedPlaylists": {"uploads": "UU_test_channel_id"},
                },
            }
        ],
    }


@pytest.fixture()
def sample_playlist_response() -> dict[str, Any]:
    """Realistic playlistItems().list() API response."""
    return {
        "items": [
            {
                "snippet": {
                    "title": f"Test Video {i}",
                    "publishedAt": f"2025-0{i + 1}-15T12:00:00Z",
                    "channelTitle": "Test Channel",
                },
                "contentDetails": {"videoId": f"vid_{i}"},
            }
            for i in range(3)
        ],
    }


@pytest.fixture()
def sample_videos_response() -> dict[str, Any]:
    """Realistic videos().list() API response with statistics."""
    return {
        "items": [
            {
                "id": f"vid_{i}",
                "statistics": {
                    "viewCount": str(50000 * (i + 1)),
                    "likeCount": str(2500 * (i + 1)),
                    "commentCount": str(150 * (i + 1)),
                },
                "contentDetails": {"duration": "PT12M30S"},
            }
            for i in range(3)
        ],
    }


@pytest.fixture()
def sample_channels_yaml(tmp_path: Path) -> Path:
    """Create a temporary channels.yml file."""
    channels_file = tmp_path / "channels.yml"
    channels_file.write_text(
        '- custom_url: "@testchannel"\n- channel_id: "UC_test_id"\n'
    )
    return channels_file


@pytest.fixture()
def mock_youtube_service() -> MagicMock:
    """Mock Google API client for YouTube Data API v3."""
    return MagicMock()


@pytest.fixture()
def output_dir(tmp_path: Path) -> Path:
    """Temporary output directory for test reports."""
    out = tmp_path / "output"
    out.mkdir()
    return out


@pytest.fixture()
def sample_channels_data() -> list[dict[str, Any]]:
    """Full channels_data structure as returned by analyzer."""
    return [
        {
            "channel": {
                "id": "UC_test_1",
                "title": "Test Channel One",
                "description": "First test channel",
                "subscriber_count": "100000",
                "video_count": "200",
                "view_count": "5000000",
                "thumbnail": "https://example.com/thumb1.jpg",
                "url": "https://www.youtube.com/channel/UC_test_1",
            },
            "videos": [
                {
                    "id": f"vid_{i}",
                    "title": f"Video Title {i}",
                    "published_at": f"2025-06-{15 + i}T12:00:00Z",
                    "url": f"https://www.youtube.com/watch?v=vid_{i}",
                    "view_count": 50000 * (i + 1),
                    "like_count": 2500 * (i + 1),
                    "comment_count": 150 * (i + 1),
                    "duration_seconds": 750,
                    "engagement_rate_views": round(
                        ((2500 * (i + 1) + 150 * (i + 1)) / (50000 * (i + 1))) * 100, 3
                    ),
                    "engagement_rate_subscribers": 0.0,
                    "view_rate": 0.0,
                    "like_rate": 0.0,
                    "comment_rate": 0.0,
                    "views_per_minute": 0.0,
                }
                for i in range(5)
            ],
        },
    ]
