"""npm cache cleaner."""

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
class NpmCleaner(BaseCleaner):
    """Cleaner for npm caches."""

    name = "npm"
    description = "npm package cache"
    risk_level = RiskLevel.SAFE

    def get_targets(self) -> list[CleanTarget]:
        """Get list of npm cache targets."""
        targets = []

        # Main npm cache
        npm_cache = expand_path("~/.npm")
        exists = npm_cache.exists()
        size = get_dir_size(npm_cache) if exists else 0

        targets.append(
            CleanTarget(
                name="npm/_cacache",
                path=npm_cache / "_cacache",
                description="npm download cache",
                risk_level=RiskLevel.SAFE,
                clean_method=CleanMethod.DELETE_DIR,
                size_bytes=get_dir_size(npm_cache / "_cacache") if (npm_cache / "_cacache").exists() else 0,
                exists=(npm_cache / "_cacache").exists(),
            )
        )

        targets.append(
            CleanTarget(
                name="npm/_logs",
                path=npm_cache / "_logs",
                description="npm log files",
                risk_level=RiskLevel.SAFE,
                clean_method=CleanMethod.DELETE_DIR,
                size_bytes=get_dir_size(npm_cache / "_logs") if (npm_cache / "_logs").exists() else 0,
                exists=(npm_cache / "_logs").exists(),
            )
        )

        return targets
