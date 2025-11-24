"""Configuration and constants."""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CHANNELS_FILE = PROJECT_ROOT / "channels.yml"

# Duration thresholds (seconds)
SHORT_VIDEO_MAX = 300      # 5 minutes
MEDIUM_VIDEO_MAX = 900     # 15 minutes

# Default values
DEFAULT_LANGUAGES = ["es", "en"]
DEFAULT_MAX_RESULTS = 50
DEFAULT_OUTPUT_DIR = Path("./output")
DEFAULT_VIDEO_ID = "tLkRAqmAEtE"

# API limits
YOUTUBE_API_BATCH_SIZE = 50
YOUTUBE_API_MAX_RESULTS_PER_REQUEST = 50

# Environment variable keys
ENV_API_KEY = "YOUTUBE_API_KEY"
ENV_VIDEO_ID = "VIDEO_ID"
ENV_MAX_RESULTS = "MAX_RESULTS_PER_CHANNEL"
ENV_OUTPUT_DIR = "OUTPUT_DIR"
ENV_TRANSCRIPT_FIXTURES = "YOUTUBE_TRANSCRIPT_FIXTURES_DIR"


def get_env(key: str, default=None):
    """Get environment variable with optional default."""
    return os.environ.get(key, default)


def format_number(value) -> str:
    """Format number with thousand separators or return 'N/A'."""
    if value is None:
        return 'N/A'
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return 'N/A'
