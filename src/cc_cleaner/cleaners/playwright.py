"""Playwright browser cache cleaner."""

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
class PlaywrightCleaner(BaseCleaner):
    """Cleaner for Playwright browser binaries."""

    name = "playwright"
    description = "Playwright browser binaries (Chromium, Firefox, WebKit)"
    risk_level = RiskLevel.SAFE

    def get_targets(self) -> list[CleanTarget]:
        """Get list of Playwright cache targets."""
        targets = []

        # Determine cache location based on OS
        system = platform.system()
        if system == "Darwin":
            cache_path = expand_path("~/Library/Caches/ms-playwright")
        elif system == "Linux":
            cache_path = expand_path("~/.cache/ms-playwright")
        else:
            return targets  # Windows not supported yet

        if cache_path.exists():
            size = get_dir_size(cache_path)
            targets.append(
                CleanTarget(
                    name="playwright/browsers",
                    path=cache_path,
                    description="Playwright browser binaries (reinstall with: npx playwright install)",
                    risk_level=RiskLevel.SAFE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=size,
                    exists=True,
                )
            )

        return targets
