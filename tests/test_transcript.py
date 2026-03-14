"""Tests for transcript downloader with mocked API."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.config import reset_settings


class TestGetTranscript:
    """Tests for transcript download with fallback chain."""

    def test_successful_download(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
        reset_settings()

        with patch("src.transcript.YouTubeTranscriptApi") as mock_api_cls:
            mock_client = MagicMock()
            mock_api_cls.return_value = mock_client
            mock_client.fetch.return_value = [
                {"text": "Hello world"},
                {"text": "Second line"},
            ]

            from src.transcript import YouTubeTranscriptDownloader

            downloader = YouTubeTranscriptDownloader(["en"])
            result = downloader.get_transcript("test_video")

            assert result == "Hello world\nSecond line"
            mock_client.fetch.assert_called_once_with("test_video", languages=["en"])

    def test_fallback_to_available_transcript(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
        reset_settings()

        from youtube_transcript_api import NoTranscriptFound

        with patch("src.transcript.YouTubeTranscriptApi") as mock_api_cls:
            mock_client = MagicMock()
            mock_api_cls.return_value = mock_client
            mock_client.fetch.side_effect = NoTranscriptFound(
                "vid", ["en"], {}  # type: ignore[arg-type]
            )

            mock_transcript = MagicMock()
            mock_transcript.fetch.return_value = [{"text": "Fallback text"}]
            mock_client.list.return_value = iter([mock_transcript])

            from src.transcript import YouTubeTranscriptDownloader

            downloader = YouTubeTranscriptDownloader(["en"])
            result = downloader.get_transcript("test_video")

            assert result == "Fallback text"

    def test_local_fixture_fallback(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        fixture_dir = tmp_path / "fixtures"
        fixture_dir.mkdir()
        (fixture_dir / "test_vid.txt").write_text("Local transcript content")

        monkeypatch.setenv(
            "YOUTUBE_TRANSCRIPT_FIXTURES_DIR", str(fixture_dir)
        )
        monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
        reset_settings()

        with patch("src.transcript.YouTubeTranscriptApi") as mock_api_cls:
            mock_client = MagicMock()
            mock_api_cls.return_value = mock_client
            mock_client.fetch.side_effect = Exception("Network error")

            from src.transcript import YouTubeTranscriptDownloader

            downloader = YouTubeTranscriptDownloader(["en"])
            result = downloader.get_transcript("test_vid")

            assert result == "Local transcript content"

    def test_no_transcript_available_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
        monkeypatch.delenv("YOUTUBE_TRANSCRIPT_FIXTURES_DIR", raising=False)
        reset_settings()

        with patch("src.transcript.YouTubeTranscriptApi") as mock_api_cls:
            mock_client = MagicMock()
            mock_api_cls.return_value = mock_client
            mock_client.fetch.side_effect = Exception("No transcript")

            from src.transcript import YouTubeTranscriptDownloader

            downloader = YouTubeTranscriptDownloader(["en"])
            with pytest.raises(RuntimeError, match="Unexpected error"):
                downloader.get_transcript("nonexistent_vid")


class TestSaveTranscript:
    """Tests for saving transcripts to disk."""

    def test_saves_to_file(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
        reset_settings()

        with patch("src.transcript.YouTubeTranscriptApi") as mock_api_cls:
            mock_client = MagicMock()
            mock_api_cls.return_value = mock_client
            mock_client.fetch.return_value = [{"text": "Saved content"}]

            from src.transcript import YouTubeTranscriptDownloader

            downloader = YouTubeTranscriptDownloader(["en"])
            saved_path = downloader.save_transcript("vid123", str(tmp_path))

            assert saved_path.exists()
            assert saved_path.name == "vid123_transcript.txt"
            assert saved_path.read_text() == "Saved content"
