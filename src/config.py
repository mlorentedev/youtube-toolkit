"""Configuration via environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API credentials (empty = not set, validated per command)
    youtube_api_key: str = ""

    # API settings
    max_results_per_channel: int = 50
    api_batch_size: int = 50

    # Output
    output_dir: Path = Path("./output")

    # Transcript
    video_id: str = "tLkRAqmAEtE"
    youtube_transcript_fixtures_dir: str = ""
    transcript_languages: list[str] = ["es", "en"]  # noqa: B006

    # Channels config
    channels_file: Path = Path("channels.yml")

    # Metric thresholds (for performance classification)
    high_performance_multiplier: float = 1.5
    low_performance_multiplier: float = 0.5

    # Duration thresholds (seconds)
    short_video_max: int = 300
    long_video_min: int = 900


_settings: Settings | None = None


def get_settings() -> Settings:
    """Load and cache settings from environment."""
    global _settings  # noqa: PLW0603
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """Reset cached settings (useful for testing)."""
    global _settings  # noqa: PLW0603
    _settings = None


def format_number(value: object) -> str:
    """Format number with thousand separators or return 'N/A'."""
    if value is None:
        return "N/A"
    try:
        return f"{int(str(value)):,}"
    except (ValueError, TypeError):
        return "N/A"
