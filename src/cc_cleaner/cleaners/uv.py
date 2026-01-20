"""uv (Python package manager) cache cleaner."""

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
class UvCleaner(BaseCleaner):
    """Cleaner for uv caches."""

    name = "uv"
    description = "uv Python package cache"
    risk_level = RiskLevel.SAFE

    def get_targets(self) -> list[CleanTarget]:
        """Get list of uv cache targets."""
        targets = []

        # uv cache location
        uv_cache = expand_path("~/.cache/uv")
        exists = uv_cache.exists()
        size = get_dir_size(uv_cache) if exists else 0

        targets.append(
            CleanTarget(
                name="uv/cache",
                path=uv_cache,
                description="uv package download and build cache",
                risk_level=RiskLevel.SAFE,
                clean_method=CleanMethod.DELETE_DIR,
                size_bytes=size,
                exists=exists,
            )
        )

        return targets
