"""pip cache cleaner."""

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
class PipCleaner(BaseCleaner):
    """Cleaner for pip caches."""

    name = "pip"
    description = "pip package cache"
    risk_level = RiskLevel.SAFE

    def get_targets(self) -> list[CleanTarget]:
        """Get list of pip cache targets."""
        targets = []

        # pip cache location
        pip_cache = expand_path("~/.cache/pip")
        exists = pip_cache.exists()
        size = get_dir_size(pip_cache) if exists else 0

        targets.append(
            CleanTarget(
                name="pip/cache",
                path=pip_cache,
                description="pip package download cache",
                risk_level=RiskLevel.SAFE,
                clean_method=CleanMethod.DELETE_DIR,
                size_bytes=size,
                exists=exists,
            )
        )

        return targets
