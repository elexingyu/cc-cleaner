"""CocoaPods cache cleaner."""

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
class CocoaPodsCleaner(BaseCleaner):
    """Cleaner for CocoaPods caches."""

    name = "cocoapods"
    description = "CocoaPods pod cache and repos"
    risk_level = RiskLevel.MODERATE

    def get_targets(self) -> list[CleanTarget]:
        """Get list of CocoaPods cache targets."""
        targets = []

        # Only available on macOS
        if platform.system() != "Darwin":
            return targets

        cocoapods_home = expand_path("~/.cocoapods")

        # Repos (specs cache)
        repos = cocoapods_home / "repos"
        repos_exists = repos.exists()
        repos_size = get_dir_size(repos) if repos_exists else 0

        if repos_exists:
            targets.append(
                CleanTarget(
                    name="cocoapods/repos",
                    path=repos,
                    description="CocoaPods spec repositories",
                    risk_level=RiskLevel.MODERATE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=repos_size,
                    exists=repos_exists,
                )
            )

        # Cache directory
        cache = expand_path("~/Library/Caches/CocoaPods")
        cache_exists = cache.exists()
        cache_size = get_dir_size(cache) if cache_exists else 0

        if cache_exists:
            targets.append(
                CleanTarget(
                    name="cocoapods/cache",
                    path=cache,
                    description="CocoaPods download cache",
                    risk_level=RiskLevel.SAFE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=cache_size,
                    exists=cache_exists,
                )
            )

        return targets
