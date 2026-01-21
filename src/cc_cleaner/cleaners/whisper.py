"""Whisper cache cleaner."""

from cc_cleaner.core import (
    BaseCleaner,
    CleanMethod,
    CleanTarget,
    RiskLevel,
    expand_path,
    get_dir_size,
    register_cleaner,
)


@register_cleaner
class WhisperCleaner(BaseCleaner):
    """Cleaner for OpenAI Whisper model caches."""

    name = "whisper"
    description = "OpenAI Whisper model cache"
    risk_level = RiskLevel.MODERATE

    def get_targets(self) -> list[CleanTarget]:
        """Get list of Whisper cache targets."""
        targets = []

        # ~/.cache/whisper - Whisper models
        whisper_cache = expand_path("~/.cache/whisper")
        if whisper_cache.exists():
            size = get_dir_size(whisper_cache)
            targets.append(
                CleanTarget(
                    name="whisper/cache",
                    path=whisper_cache,
                    description="OpenAI Whisper model cache",
                    risk_level=RiskLevel.MODERATE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=size,
                    exists=True,
                )
            )

        return targets
