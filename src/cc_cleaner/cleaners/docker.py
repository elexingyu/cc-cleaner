"""Docker cache cleaner."""

import shutil
import subprocess

from cc_cleaner.core import (
    BaseCleaner,
    CleanMethod,
    CleanTarget,
    RiskLevel,
    register_cleaner,
)


def docker_available() -> bool:
    """Check if Docker CLI is available."""
    return shutil.which("docker") is not None


def get_docker_disk_usage() -> dict[str, int]:
    """Get Docker disk usage by category."""
    if not docker_available():
        return {}

    try:
        result = subprocess.run(
            ["docker", "system", "df", "--format", "{{.Type}}\t{{.Size}}"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return {}

        usage = {}
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                category = parts[0].lower()
                size_str = parts[1]
                usage[category] = parse_docker_size(size_str)

        return usage
    except Exception:
        return {}


def parse_docker_size(size_str: str) -> int:
    """Parse Docker size string to bytes."""
    size_str = size_str.strip().upper()
    if size_str == "0B" or size_str == "0":
        return 0

    units = {
        "B": 1,
        "KB": 1024,
        "MB": 1024**2,
        "GB": 1024**3,
        "TB": 1024**4,
    }

    for unit, multiplier in units.items():
        if size_str.endswith(unit):
            try:
                value = float(size_str[: -len(unit)])
                return int(value * multiplier)
            except ValueError:
                return 0

    return 0


@register_cleaner
class DockerCleaner(BaseCleaner):
    """Cleaner for Docker caches."""

    name = "docker"
    description = "Docker dangling images, stopped containers, build cache"
    risk_level = RiskLevel.DANGEROUS

    def get_targets(self) -> list[CleanTarget]:
        """Get list of Docker cache targets."""
        targets = []

        if not docker_available():
            return targets

        usage = get_docker_disk_usage()

        # Build cache (safe to clean)
        build_cache_size = usage.get("build cache", 0)
        targets.append(
            CleanTarget(
                name="docker/build-cache",
                path=None,
                description="Docker build cache",
                risk_level=RiskLevel.SAFE,
                clean_method=CleanMethod.COMMAND,
                command=["docker", "builder", "prune", "-f"],
                size_bytes=build_cache_size,
                exists=build_cache_size > 0,
            )
        )

        # Dangling images (moderate - might need them)
        targets.append(
            CleanTarget(
                name="docker/dangling-images",
                path=None,
                description="Docker dangling images (untagged)",
                risk_level=RiskLevel.MODERATE,
                clean_method=CleanMethod.COMMAND,
                command=["docker", "image", "prune", "-f"],
                size_bytes=0,  # Hard to estimate
                exists=True,  # Assume there might be some
            )
        )

        # Full prune (dangerous)
        total_size = sum(usage.values())
        targets.append(
            CleanTarget(
                name="docker/system-prune",
                path=None,
                description="Docker full system prune (all unused data)",
                risk_level=RiskLevel.DANGEROUS,
                clean_method=CleanMethod.COMMAND,
                command=["docker", "system", "prune", "-af"],
                size_bytes=total_size,
                exists=total_size > 0,
            )
        )

        return targets
