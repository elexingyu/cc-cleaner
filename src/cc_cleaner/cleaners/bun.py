"""Bun cache cleaner."""

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
class BunCleaner(BaseCleaner):
    """Cleaner for Bun package manager caches."""

    name = "bun"
    description = "Bun package cache and install cache"
    risk_level = RiskLevel.SAFE

    def get_targets(self) -> list[CleanTarget]:
        """Get list of Bun cache targets."""
        targets = []

        # ~/.bun/install/cache - package install cache
        install_cache = expand_path("~/.bun/install/cache")
        if install_cache.exists():
            size = get_dir_size(install_cache)
            targets.append(
                CleanTarget(
                    name="bun/install-cache",
                    path=install_cache,
                    description="Bun package install cache",
                    risk_level=RiskLevel.SAFE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=size,
                    exists=True,
                )
            )

        # ~/.bun/cache - general cache
        bun_cache = expand_path("~/.bun/cache")
        if bun_cache.exists():
            size = get_dir_size(bun_cache)
            targets.append(
                CleanTarget(
                    name="bun/cache",
                    path=bun_cache,
                    description="Bun general cache",
                    risk_level=RiskLevel.SAFE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=size,
                    exists=True,
                )
            )

        return targets
