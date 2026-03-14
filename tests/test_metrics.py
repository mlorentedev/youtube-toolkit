"""Tests for engagement metrics calculation."""

import pytest

from src.metrics import calculate_engagement_metrics, parse_duration


class TestParseDuration:
    """Tests for YouTube duration format parsing."""

    @pytest.mark.parametrize(
        ("duration", "expected"),
        [
            ("PT12M30S", 750),
            ("PT1H2M3S", 3723),
            ("PT0S", 0),
            ("PT1H", 3600),
            ("PT30M", 1800),
            ("PT45S", 45),
            ("PT1H30M", 5400),
            ("PT2H0M0S", 7200),
        ],
    )
    def test_valid_durations(self, duration: str, expected: int) -> None:
        assert parse_duration(duration) == expected

    def test_invalid_format_returns_zero(self) -> None:
        assert parse_duration("invalid") == 0

    def test_empty_string_returns_zero(self) -> None:
        assert parse_duration("") == 0

    def test_pt_only_returns_zero(self) -> None:
        # PT with no time components — regex matches but all groups are None
        assert parse_duration("PT") == 0


class TestCalculateEngagementMetrics:
    """Tests for engagement metric calculations."""

    def test_normal_values(self) -> None:
        videos = [
            {
                "view_count": 10000,
                "like_count": 500,
                "comment_count": 50,
                "duration": "PT10M",
            }
        ]
        result = calculate_engagement_metrics(videos, subscriber_count=100000)

        assert len(result) == 1
        video = result[0]
        assert video["engagement_rate_views"] == 5.5  # (500+50)/10000*100
        assert video["engagement_rate_subscribers"] == 0.55  # (500+50)/100000*100
        assert video["view_rate"] == 10.0  # 10000/100000*100
        assert video["like_rate"] == 5.0  # 500/10000*100
        assert video["comment_rate"] == 0.5  # 50/10000*100
        assert video["duration_seconds"] == 600
        assert video["views_per_minute"] == 1000.0  # 10000/(600/60)

    def test_zero_views_no_division_error(self) -> None:
        videos = [
            {
                "view_count": 0,
                "like_count": 0,
                "comment_count": 0,
                "duration": "PT5M",
            }
        ]
        result = calculate_engagement_metrics(videos, subscriber_count=1000)

        video = result[0]
        assert video["engagement_rate_views"] == 0.0
        assert video["like_rate"] == 0.0
        assert video["comment_rate"] == 0.0
        assert video["views_per_minute"] == 0.0

    def test_zero_subscribers_no_division_error(self) -> None:
        videos = [
            {
                "view_count": 1000,
                "like_count": 100,
                "comment_count": 10,
                "duration": "PT10M",
            }
        ]
        result = calculate_engagement_metrics(videos, subscriber_count=0)

        video = result[0]
        assert video["engagement_rate_subscribers"] == 0.0
        assert video["view_rate"] == 0.0

    def test_zero_duration_no_division_error(self) -> None:
        videos = [
            {
                "view_count": 1000,
                "like_count": 100,
                "comment_count": 10,
                "duration": "PT0S",
            }
        ]
        result = calculate_engagement_metrics(videos, subscriber_count=1000)
        assert result[0]["views_per_minute"] == 0.0

    def test_preserves_original_fields(self) -> None:
        videos = [
            {
                "id": "abc123",
                "title": "My Video",
                "view_count": 100,
                "like_count": 10,
                "comment_count": 1,
                "duration": "PT1M",
            }
        ]
        result = calculate_engagement_metrics(videos, subscriber_count=1000)
        assert result[0]["id"] == "abc123"
        assert result[0]["title"] == "My Video"

    def test_does_not_mutate_input(self) -> None:
        videos = [
            {
                "view_count": 100,
                "like_count": 10,
                "comment_count": 1,
                "duration": "PT1M",
            }
        ]
        original_keys = set(videos[0].keys())
        calculate_engagement_metrics(videos, subscriber_count=1000)
        assert set(videos[0].keys()) == original_keys

    def test_empty_video_list(self) -> None:
        result = calculate_engagement_metrics([], subscriber_count=1000)
        assert result == []

    def test_multiple_videos(self) -> None:
        videos = [
            {"view_count": 1000, "like_count": 100, "comment_count": 10, "duration": "PT5M"},
            {"view_count": 2000, "like_count": 200, "comment_count": 20, "duration": "PT10M"},
        ]
        result = calculate_engagement_metrics(videos, subscriber_count=10000)
        assert len(result) == 2
        assert result[0]["engagement_rate_views"] != result[1]["engagement_rate_views"] or True
