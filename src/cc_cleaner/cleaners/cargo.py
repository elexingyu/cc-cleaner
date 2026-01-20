"""Cargo (Rust) cache cleaner."""

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
class CargoCleaner(BaseCleaner):
    """Cleaner for Cargo caches."""

    name = "cargo"
    description = "Cargo (Rust) registry cache and build artifacts"
    risk_level = RiskLevel.SAFE

    def get_targets(self) -> list[CleanTarget]:
        """Get list of Cargo cache targets."""
        targets = []
        cargo_home = expand_path("~/.cargo")

        # Registry cache
        registry_cache = cargo_home / "registry" / "cache"
        cache_exists = registry_cache.exists()
        cache_size = get_dir_size(registry_cache) if cache_exists else 0

        if cache_exists:
            targets.append(
                CleanTarget(
                    name="cargo/registry-cache",
                    path=registry_cache,
                    description="Cargo registry cache (compressed crates)",
                    risk_level=RiskLevel.SAFE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=cache_size,
                    exists=cache_exists,
                )
            )

        # Registry source (extracted crates)
        registry_src = cargo_home / "registry" / "src"
        src_exists = registry_src.exists()
        src_size = get_dir_size(registry_src) if src_exists else 0

        if src_exists:
            targets.append(
                CleanTarget(
                    name="cargo/registry-src",
                    path=registry_src,
                    description="Cargo registry source (extracted crates)",
                    risk_level=RiskLevel.SAFE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=src_size,
                    exists=src_exists,
                )
            )

        # Git checkouts
        git_db = cargo_home / "git" / "db"
        git_exists = git_db.exists()
        git_size = get_dir_size(git_db) if git_exists else 0

        if git_exists:
            targets.append(
                CleanTarget(
                    name="cargo/git-db",
                    path=git_db,
                    description="Cargo git dependency cache",
                    risk_level=RiskLevel.SAFE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=git_size,
                    exists=git_exists,
                )
            )

        return targets
