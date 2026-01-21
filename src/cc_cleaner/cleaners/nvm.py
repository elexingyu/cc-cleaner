"""NVM (Node Version Manager) cache cleaner."""

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
class NVMCleaner(BaseCleaner):
    """Cleaner for NVM (Node Version Manager) caches."""

    name = "nvm"
    description = "NVM Node.js versions and caches"
    risk_level = RiskLevel.MODERATE

    def get_targets(self) -> list[CleanTarget]:
        """Get list of NVM cache targets."""
        targets = []

        nvm_dir = expand_path("~/.nvm")
        if not nvm_dir.exists():
            return targets

        # ~/.nvm/.cache - NVM download cache
        nvm_cache = nvm_dir / ".cache"
        if nvm_cache.exists():
            size = get_dir_size(nvm_cache)
            targets.append(
                CleanTarget(
                    name="nvm/cache",
                    path=nvm_cache,
                    description="NVM download cache",
                    risk_level=RiskLevel.SAFE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=size,
                    exists=True,
                )
            )

        # ~/.nvm/versions - installed Node versions (MODERATE risk)
        # Only show size, let user decide
        versions_dir = nvm_dir / "versions"
        if versions_dir.exists():
            size = get_dir_size(versions_dir)
            targets.append(
                CleanTarget(
                    name="nvm/versions",
                    path=versions_dir,
                    description="NVM installed Node.js versions (removes ALL versions!)",
                    risk_level=RiskLevel.DANGEROUS,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=size,
                    exists=True,
                )
            )

        return targets
