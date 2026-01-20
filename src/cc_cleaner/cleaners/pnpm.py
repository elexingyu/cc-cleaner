"""pnpm cache cleaner."""

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
class PnpmCleaner(BaseCleaner):
    """Cleaner for pnpm caches."""

    name = "pnpm"
    description = "pnpm package store and cache"
    risk_level = RiskLevel.MODERATE

    def get_targets(self) -> list[CleanTarget]:
        """Get list of pnpm cache targets."""
        targets = []

        # pnpm store (content-addressable storage)
        pnpm_store = expand_path("~/.local/share/pnpm/store")
        store_exists = pnpm_store.exists()
        store_size = get_dir_size(pnpm_store) if store_exists else 0

        if store_exists:
            targets.append(
                CleanTarget(
                    name="pnpm/store",
                    path=pnpm_store,
                    description="pnpm content-addressable store",
                    risk_level=RiskLevel.MODERATE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=store_size,
                    exists=store_exists,
                )
            )

        # pnpm cache
        pnpm_cache = expand_path("~/.cache/pnpm")
        cache_exists = pnpm_cache.exists()
        cache_size = get_dir_size(pnpm_cache) if cache_exists else 0

        if cache_exists:
            targets.append(
                CleanTarget(
                    name="pnpm/cache",
                    path=pnpm_cache,
                    description="pnpm metadata cache",
                    risk_level=RiskLevel.SAFE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=cache_size,
                    exists=cache_exists,
                )
            )

        return targets
