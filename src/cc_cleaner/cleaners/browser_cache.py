"""Browser cache cleaner (Chrome, Safari, etc.)."""

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
class BrowserCacheCleaner(BaseCleaner):
    """Cleaner for browser caches (Chrome, Safari)."""

    name = "browser-cache"
    description = "Browser caches (Chrome, Safari)"
    risk_level = RiskLevel.MODERATE

    def get_targets(self) -> list[CleanTarget]:
        """Get list of browser cache targets."""
        targets = []

        system = platform.system()

        if system == "Darwin":
            # macOS Chrome cache
            chrome_cache = expand_path("~/Library/Caches/Google/Chrome")
            if chrome_cache.exists():
                size = get_dir_size(chrome_cache)
                targets.append(
                    CleanTarget(
                        name="chrome/cache",
                        path=chrome_cache,
                        description="Google Chrome cache (won't affect history/bookmarks)",
                        risk_level=RiskLevel.SAFE,
                        clean_method=CleanMethod.DELETE_DIR,
                        size_bytes=size,
                        exists=True,
                    )
                )

            # macOS Safari cache
            safari_cache = expand_path("~/Library/Caches/com.apple.Safari")
            if safari_cache.exists():
                size = get_dir_size(safari_cache)
                targets.append(
                    CleanTarget(
                        name="safari/cache",
                        path=safari_cache,
                        description="Safari browser cache",
                        risk_level=RiskLevel.SAFE,
                        clean_method=CleanMethod.DELETE_DIR,
                        size_bytes=size,
                        exists=True,
                    )
                )

            # macOS Firefox cache
            firefox_cache = expand_path("~/Library/Caches/Firefox")
            if firefox_cache.exists():
                size = get_dir_size(firefox_cache)
                targets.append(
                    CleanTarget(
                        name="firefox/cache",
                        path=firefox_cache,
                        description="Firefox browser cache",
                        risk_level=RiskLevel.SAFE,
                        clean_method=CleanMethod.DELETE_DIR,
                        size_bytes=size,
                        exists=True,
                    )
                )

            # macOS Arc cache
            arc_cache = expand_path("~/Library/Caches/company.thebrowser.Browser")
            if arc_cache.exists():
                size = get_dir_size(arc_cache)
                targets.append(
                    CleanTarget(
                        name="arc/cache",
                        path=arc_cache,
                        description="Arc browser cache",
                        risk_level=RiskLevel.SAFE,
                        clean_method=CleanMethod.DELETE_DIR,
                        size_bytes=size,
                        exists=True,
                    )
                )

        elif system == "Linux":
            # Linux Chrome cache
            chrome_cache = expand_path("~/.cache/google-chrome")
            if chrome_cache.exists():
                size = get_dir_size(chrome_cache)
                targets.append(
                    CleanTarget(
                        name="chrome/cache",
                        path=chrome_cache,
                        description="Google Chrome cache",
                        risk_level=RiskLevel.SAFE,
                        clean_method=CleanMethod.DELETE_DIR,
                        size_bytes=size,
                        exists=True,
                    )
                )

            # Linux Firefox cache
            firefox_cache = expand_path("~/.cache/mozilla/firefox")
            if firefox_cache.exists():
                size = get_dir_size(firefox_cache)
                targets.append(
                    CleanTarget(
                        name="firefox/cache",
                        path=firefox_cache,
                        description="Firefox browser cache",
                        risk_level=RiskLevel.SAFE,
                        clean_method=CleanMethod.DELETE_DIR,
                        size_bytes=size,
                        exists=True,
                    )
                )

        return targets
