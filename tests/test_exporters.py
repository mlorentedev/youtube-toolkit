"""Tests for report exporters."""

from pathlib import Path
from typing import Any

from src.exporters import (
    export_best_videos_report,
    export_channel_stats,
    export_engagement_trends_report,
    export_latest_videos_report,
    export_output_readme,
    export_to_csv,
)


class TestCsvExporter:
    """Tests for CSV export."""

    def test_creates_csv_file(
        self, output_dir: Path, sample_channels_data: list[dict[str, Any]]
    ) -> None:
        csv_path = output_dir / "test.csv"
        export_to_csv(sample_channels_data, csv_path)

        assert csv_path.exists()
        content = csv_path.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == 6  # 1 header + 5 videos
        assert "Channel" in lines[0]
        assert "Test Channel One" in lines[1]

    def test_empty_data_no_file(self, output_dir: Path) -> None:
        csv_path = output_dir / "empty.csv"
        export_to_csv([], csv_path)
        assert not csv_path.exists()

    def test_csv_headers(
        self, output_dir: Path, sample_channels_data: list[dict[str, Any]]
    ) -> None:
        csv_path = output_dir / "headers.csv"
        export_to_csv(sample_channels_data, csv_path)

        header = csv_path.read_text().split("\n")[0]
        expected_columns = [
            "Channel", "Subscribers", "Video Title", "Views",
            "Likes", "Comments", "Engagement Rate",
        ]
        for col in expected_columns:
            assert col in header


class TestChannelStatsExporter:
    """Tests for channel stats text report."""

    def test_creates_report(
        self, output_dir: Path, sample_channels_data: list[dict[str, Any]]
    ) -> None:
        report_path = output_dir / "stats.txt"
        export_channel_stats(sample_channels_data, report_path)

        assert report_path.exists()
        content = report_path.read_text()
        assert "YOUTUBE CHANNEL STATISTICS REPORT" in content
        assert "Test Channel One" in content
        assert "TOP 5 MOST VIEWED" in content

    def test_empty_data_no_file(self, output_dir: Path) -> None:
        report_path = output_dir / "empty_stats.txt"
        export_channel_stats([], report_path)
        assert not report_path.exists()


class TestEngagementTrendsExporter:
    """Tests for engagement trends report."""

    def test_creates_report(
        self, output_dir: Path, sample_channels_data: list[dict[str, Any]]
    ) -> None:
        report_path = output_dir / "trends.txt"
        export_engagement_trends_report(sample_channels_data, report_path)

        assert report_path.exists()
        content = report_path.read_text()
        assert "ENGAGEMENT TRENDS" in content
        assert "GLOBAL STATISTICS" in content

    def test_empty_data_no_file(self, output_dir: Path) -> None:
        report_path = output_dir / "empty_trends.txt"
        export_engagement_trends_report([], report_path)
        assert not report_path.exists()


class TestUrlExporters:
    """Tests for best and latest videos URL exporters."""

    def test_best_videos_report(
        self, output_dir: Path, sample_channels_data: list[dict[str, Any]]
    ) -> None:
        report_path = output_dir / "best.txt"
        export_best_videos_report(sample_channels_data, report_path, top_n=3)

        assert report_path.exists()
        lines = report_path.read_text().strip().split("\n")
        assert len(lines) == 3
        assert all("youtube.com/watch" in line for line in lines)

    def test_latest_videos_report(
        self, output_dir: Path, sample_channels_data: list[dict[str, Any]]
    ) -> None:
        report_path = output_dir / "latest.txt"
        export_latest_videos_report(sample_channels_data, report_path, top_n=3)

        assert report_path.exists()
        lines = report_path.read_text().strip().split("\n")
        assert len(lines) == 3

    def test_empty_data_no_file(self, output_dir: Path) -> None:
        export_best_videos_report([], output_dir / "empty_best.txt")
        export_latest_videos_report([], output_dir / "empty_latest.txt")
        assert not (output_dir / "empty_best.txt").exists()
        assert not (output_dir / "empty_latest.txt").exists()


class TestReadmeExporter:
    """Tests for output README generator."""

    def test_creates_readme(
        self, output_dir: Path, sample_channels_data: list[dict[str, Any]]
    ) -> None:
        export_output_readme(output_dir, "20250615_120000", sample_channels_data)

        readme_path = output_dir / "README.md"
        assert readme_path.exists()
        content = readme_path.read_text()
        assert "# YouTube Analysis Report" in content
        assert "20250615_120000" in content
        assert "Test Channel One" in content
        assert "Engagement Metrics Explained" in content

    def test_readme_has_channel_list(
        self, output_dir: Path, sample_channels_data: list[dict[str, Any]]
    ) -> None:
        export_output_readme(output_dir, "20250615_120000", sample_channels_data)

        content = (output_dir / "README.md").read_text()
        assert "Channels Analyzed" in content
        assert "Test Channel One" in content
