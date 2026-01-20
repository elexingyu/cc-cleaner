"""Yarn cache cleaner."""

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
class YarnCleaner(BaseCleaner):
    """Cleaner for Yarn caches."""

    name = "yarn"
    description = "Yarn package cache"
    risk_level = RiskLevel.SAFE

    def get_targets(self) -> list[CleanTarget]:
        """Get list of Yarn cache targets."""
        targets = []

        # Yarn cache location varies by OS
        if platform.system() == "Darwin":
            yarn_cache = expand_path("~/Library/Caches/Yarn")
        else:
            yarn_cache = expand_path("~/.cache/yarn")

        exists = yarn_cache.exists()
        size = get_dir_size(yarn_cache) if exists else 0

        targets.append(
            CleanTarget(
                name="yarn/cache",
                path=yarn_cache,
                description="Yarn package cache",
                risk_level=RiskLevel.SAFE,
                clean_method=CleanMethod.DELETE_DIR,
                size_bytes=size,
                exists=exists,
            )
        )

        # Yarn v2+ (berry) cache
        yarn_berry = expand_path("~/.yarn/berry/cache")
        berry_exists = yarn_berry.exists()
        berry_size = get_dir_size(yarn_berry) if berry_exists else 0

        if berry_exists:
            targets.append(
                CleanTarget(
                    name="yarn/berry",
                    path=yarn_berry,
                    description="Yarn Berry (v2+) cache",
                    risk_level=RiskLevel.SAFE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=berry_size,
                    exists=berry_exists,
                )
            )

        return targets
