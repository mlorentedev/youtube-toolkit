"""YouTube transcript downloading."""

from pathlib import Path
from typing import List, Optional
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

from .config import DEFAULT_LANGUAGES, ENV_TRANSCRIPT_FIXTURES, get_env


class YouTubeTranscriptDownloader:
    def __init__(self, languages: Optional[List[str]] = None):
        self.languages = languages or DEFAULT_LANGUAGES
        self.client = YouTubeTranscriptApi()

    def get_transcript(self, video_id: str) -> str:
        try:
            transcript = self.client.fetch(video_id, languages=self.languages)
            return self._format_transcript(transcript)
        except (TranscriptsDisabled, NoTranscriptFound):
            print(f"No transcript found in {self.languages}, trying available transcripts...")
            try:
                available = self.client.list(video_id)
                chosen = next(iter(available))
                transcript = chosen.fetch()
                return self._format_transcript(transcript)
            except Exception as e:
                fallback = self._load_fallback_transcript(video_id)
                if fallback is not None:
                    return fallback
                raise RuntimeError(f"No transcript available for this video: {e}")
        except Exception as e:
            fallback = self._load_fallback_transcript(video_id)
            if fallback is not None:
                return fallback
            raise RuntimeError(f"Unexpected error: {e}")

    def save_transcript(self, video_id: str, output_dir: str = "."):
        text = self.get_transcript(video_id)
        output_dir = Path(output_dir).expanduser()
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = output_dir / f"{video_id}_transcript.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Transcript saved to {filename}")

    def _format_transcript(self, transcript) -> str:
        lines = []
        for entry in transcript:
            text = (
                entry.get("text", "")
                if isinstance(entry, dict)
                else getattr(entry, "text", "")
            )
            text = text.strip()
            if text:
                lines.append(text)
        return "\n".join(lines)

    def _load_fallback_transcript(self, video_id: str) -> Optional[str]:
        fallback_dir = get_env(ENV_TRANSCRIPT_FIXTURES)
        if not fallback_dir:
            return None

        candidate = Path(fallback_dir).expanduser() / f"{video_id}.txt"
        if candidate.exists() and candidate.is_file():
            print(f"Using local transcript from {candidate}")
            content = candidate.read_text(encoding="utf-8").strip()
            return content if content else None

        return None
