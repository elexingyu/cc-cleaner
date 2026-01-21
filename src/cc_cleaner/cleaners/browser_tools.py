"""Browser automation tools cache cleaner."""

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
class BrowserToolsCleaner(BaseCleaner):
    """Cleaner for browser automation tools caches."""

    name = "browser-tools"
    description = "Browser automation caches (Puppeteer, Selenium profiles)"
    risk_level = RiskLevel.SAFE

    def get_targets(self) -> list[CleanTarget]:
        """Get list of browser tools cache targets."""
        targets = []

        # ~/.cache/browser-tools - MCP browser tools
        bt_cache = expand_path("~/.cache/browser-tools")
        if bt_cache.exists():
            size = get_dir_size(bt_cache)
            targets.append(
                CleanTarget(
                    name="browser-tools/profiles",
                    path=bt_cache,
                    description="MCP browser-tools Chrome profiles",
                    risk_level=RiskLevel.SAFE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=size,
                    exists=True,
                )
            )

        # ~/.cache/puppeteer - Puppeteer browser cache
        puppeteer_cache = expand_path("~/.cache/puppeteer")
        if puppeteer_cache.exists():
            size = get_dir_size(puppeteer_cache)
            targets.append(
                CleanTarget(
                    name="puppeteer/browsers",
                    path=puppeteer_cache,
                    description="Puppeteer downloaded browsers",
                    risk_level=RiskLevel.SAFE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=size,
                    exists=True,
                )
            )

        # ~/.cache/selenium - Selenium WebDriver cache
        selenium_cache = expand_path("~/.cache/selenium")
        if selenium_cache.exists():
            size = get_dir_size(selenium_cache)
            targets.append(
                CleanTarget(
                    name="selenium/drivers",
                    path=selenium_cache,
                    description="Selenium WebDriver binaries",
                    risk_level=RiskLevel.SAFE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=size,
                    exists=True,
                )
            )

        return targets
