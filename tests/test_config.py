"""Tests for configuration via pydantic-settings."""

import pytest

from src.config import Settings, format_number, get_settings, reset_settings


class TestSettings:
    """Tests for Settings pydantic model."""

    def test_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
        settings = Settings()
        assert settings.youtube_api_key == ""
        assert settings.max_results_per_channel == 50
        assert settings.api_batch_size == 50
        assert settings.short_video_max == 300
        assert settings.long_video_min == 900
        assert settings.high_performance_multiplier == 1.5
        assert settings.low_performance_multiplier == 0.5
        assert settings.transcript_languages == ["es", "en"]

    def test_env_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("YOUTUBE_API_KEY", "test_key_123")
        monkeypatch.setenv("MAX_RESULTS_PER_CHANNEL", "25")
        settings = Settings()
        assert settings.youtube_api_key == "test_key_123"
        assert settings.max_results_per_channel == 25

    def test_api_key_empty_by_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
        settings = Settings()
        assert settings.youtube_api_key == ""
        assert not settings.youtube_api_key  # falsy


class TestGetSettings:
    """Tests for cached settings retrieval."""

    def test_caches_settings(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("YOUTUBE_API_KEY", "key1")
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_reset_clears_cache(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("YOUTUBE_API_KEY", "key1")
        s1 = get_settings()
        reset_settings()
        monkeypatch.setenv("YOUTUBE_API_KEY", "key2")
        s2 = get_settings()
        assert s1 is not s2
        assert s2.youtube_api_key == "key2"


class TestFormatNumber:
    """Tests for number formatting utility."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (1000, "1,000"),
            (1000000, "1,000,000"),
            (0, "0"),
            ("5000", "5,000"),
            (None, "N/A"),
            ("invalid", "N/A"),
            ("", "N/A"),
        ],
    )
    def test_format_number(self, value: object, expected: str) -> None:
        assert format_number(value) == expected
