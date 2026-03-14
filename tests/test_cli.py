"""Tests for Typer CLI interface."""

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from src.config import reset_settings
from src.main import app

runner = CliRunner()


class TestHelpOutput:
    """Tests for CLI help text."""

    def test_main_help(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "YouTube" in result.output
        assert "channels" in result.output
        assert "transcript" in result.output

    def test_channels_help(self) -> None:
        result = runner.invoke(app, ["channels", "--help"])
        assert result.exit_code == 0
        assert "--channels" in result.output
        assert "--max-results" in result.output
        assert "--output" in result.output

    def test_transcript_help(self) -> None:
        result = runner.invoke(app, ["transcript", "--help"])
        assert result.exit_code == 0
        assert "--video" in result.output
        assert "--langs" in result.output
        assert "--output" in result.output


class TestChannelsCommand:
    """Tests for channels subcommand."""

    def test_missing_api_key_exits(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
        reset_settings()

        result = runner.invoke(app, ["channels"])
        assert result.exit_code == 1
        assert "YOUTUBE_API_KEY" in result.output

    def test_missing_channels_file_exits(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("YOUTUBE_API_KEY", "test_key")
        monkeypatch.setenv("CHANNELS_FILE", "/nonexistent/channels.yml")
        reset_settings()

        # Patch at the source module (lazy import inside function)
        with patch("src.analyzer.googleapiclient.discovery.build"):
            result = runner.invoke(app, ["channels"])
            assert result.exit_code == 1
            assert "not found" in result.output


class TestTranscriptCommand:
    """Tests for transcript subcommand."""

    def test_transcript_download(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
        reset_settings()

        mock_downloader = MagicMock()
        mock_downloader.save_transcript.return_value = "output/test_transcript.txt"

        # Patch at the source module (lazy import inside function)
        with patch(
            "src.transcript.YouTubeTranscriptApi"
        ) as mock_api_cls:
            mock_client = MagicMock()
            mock_api_cls.return_value = mock_client
            mock_client.fetch.return_value = [{"text": "Test content"}]

            result = runner.invoke(app, ["transcript", "--video", "abc123"])
            assert result.exit_code == 0
            assert "Downloading transcript" in result.output
