"""YouTube transcript downloading."""

import logging
from pathlib import Path
from typing import Any

from youtube_transcript_api import (
    NoTranscriptFound,
    TranscriptsDisabled,
    YouTubeTranscriptApi,
)

from .config import get_settings

logger = logging.getLogger(__name__)


class YouTubeTranscriptDownloader:
    def __init__(self, languages: list[str] | None = None) -> None:
        settings = get_settings()
        self.languages = languages or settings.transcript_languages
        self.client = YouTubeTranscriptApi()

    def get_transcript(self, video_id: str) -> str:
        """Download transcript with multi-language fallback chain."""
        try:
            transcript = self.client.fetch(video_id, languages=self.languages)
            return self._format_transcript(transcript)
        except (TranscriptsDisabled, NoTranscriptFound):
            logger.info("No transcript in %s, trying available transcripts...", self.languages)
            try:
                available = self.client.list(video_id)
                chosen = next(iter(available))
                transcript = chosen.fetch()
                return self._format_transcript(transcript)
            except Exception as e:
                fallback = self._load_fallback_transcript(video_id)
                if fallback is not None:
                    return fallback
                msg = f"No transcript available for this video: {e}"
                raise RuntimeError(msg) from e
        except Exception as e:
            fallback = self._load_fallback_transcript(video_id)
            if fallback is not None:
                return fallback
            msg = f"Unexpected error fetching transcript: {e}"
            raise RuntimeError(msg) from e

    def save_transcript(self, video_id: str, output_dir: str = ".") -> Path:
        """Download and save transcript to file."""
        text = self.get_transcript(video_id)
        output_path = Path(output_dir).expanduser()
        output_path.mkdir(parents=True, exist_ok=True)
        filename = output_path / f"{video_id}_transcript.txt"
        filename.write_text(text, encoding="utf-8")
        logger.info("Transcript saved to %s", filename)
        return filename

    def _format_transcript(self, transcript: Any) -> str:
        """Format transcript entries into plain text."""
        lines: list[str] = []
        for entry in transcript:
            text = (
                entry.get("text", "") if isinstance(entry, dict) else getattr(entry, "text", "")
            )
            text = text.strip()
            if text:
                lines.append(text)
        return "\n".join(lines)

    def _load_fallback_transcript(self, video_id: str) -> str | None:
        """Try loading transcript from local fixtures directory."""
        settings = get_settings()
        if not settings.youtube_transcript_fixtures_dir:
            return None

        candidate = Path(settings.youtube_transcript_fixtures_dir).expanduser() / f"{video_id}.txt"
        if candidate.exists() and candidate.is_file():
            logger.info("Using local transcript from %s", candidate)
            content = candidate.read_text(encoding="utf-8").strip()
            return content if content else None

        return None
