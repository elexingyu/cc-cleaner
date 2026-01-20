"""Go module cache cleaner."""

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
class GoCleaner(BaseCleaner):
    """Cleaner for Go module caches."""

    name = "go"
    description = "Go module cache"
    risk_level = RiskLevel.SAFE

    def get_targets(self) -> list[CleanTarget]:
        """Get list of Go cache targets."""
        targets = []

        # Go module cache
        go_mod_cache = expand_path("~/go/pkg/mod/cache")
        cache_exists = go_mod_cache.exists()
        cache_size = get_dir_size(go_mod_cache) if cache_exists else 0

        if cache_exists:
            targets.append(
                CleanTarget(
                    name="go/mod-cache",
                    path=go_mod_cache,
                    description="Go module download cache",
                    risk_level=RiskLevel.SAFE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=cache_size,
                    exists=cache_exists,
                )
            )

        # Go build cache
        go_build_cache = expand_path("~/.cache/go-build")
        build_exists = go_build_cache.exists()
        build_size = get_dir_size(go_build_cache) if build_exists else 0

        if build_exists:
            targets.append(
                CleanTarget(
                    name="go/build-cache",
                    path=go_build_cache,
                    description="Go build cache",
                    risk_level=RiskLevel.SAFE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=build_size,
                    exists=build_exists,
                )
            )

        return targets
