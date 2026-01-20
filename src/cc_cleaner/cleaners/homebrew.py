"""Homebrew cache cleaner."""

import platform

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
class HomebrewCleaner(BaseCleaner):
    """Cleaner for Homebrew caches."""

    name = "homebrew"
    description = "Homebrew download cache"
    risk_level = RiskLevel.SAFE

    def get_targets(self) -> list[CleanTarget]:
        """Get list of Homebrew cache targets."""
        targets = []

        # Only available on macOS
        if platform.system() != "Darwin":
            return targets

        # Homebrew cache
        brew_cache = expand_path("~/Library/Caches/Homebrew")
        exists = brew_cache.exists()
        size = get_dir_size(brew_cache) if exists else 0

        targets.append(
            CleanTarget(
                name="homebrew/cache",
                path=brew_cache,
                description="Homebrew downloaded packages",
                risk_level=RiskLevel.SAFE,
                clean_method=CleanMethod.DELETE_DIR,
                size_bytes=size,
                exists=exists,
            )
        )

        # Homebrew logs
        brew_logs = expand_path("~/Library/Logs/Homebrew")
        logs_exists = brew_logs.exists()
        logs_size = get_dir_size(brew_logs) if logs_exists else 0

        if logs_exists:
            targets.append(
                CleanTarget(
                    name="homebrew/logs",
                    path=brew_logs,
                    description="Homebrew build logs",
                    risk_level=RiskLevel.SAFE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=logs_size,
                    exists=logs_exists,
                )
            )

        return targets
