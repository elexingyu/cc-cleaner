"""Scan result caching to avoid redundant scans."""

import json
import time
from pathlib import Path
from typing import Any

# Cache file location
CACHE_DIR = Path.home() / ".cache" / "cc-cleaner"
CACHE_FILE = CACHE_DIR / "scan_cache.json"

# Cache expires after 5 minutes
CACHE_TTL_SECONDS = 300


def _ensure_cache_dir() -> None:
    """Ensure cache directory exists."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def save_scan_cache(infos: list[Any]) -> None:
    """Save scan results to cache file.

    Args:
        infos: List of CleanerInfo objects
    """
    _ensure_cache_dir()

    cache_data = {
        "timestamp": time.time(),
        "infos": [
            {
                "name": info.name,
                "description": info.description,
                "risk_level": info.risk_level.value,
                "total_size": info.total_size,
                "targets": [
                    {
                        "name": t.name,
                        "path": str(t.path) if t.path else None,
                        "description": t.description,
                        "risk_level": t.risk_level.value,
                        "clean_method": t.clean_method.value,
                        "size_bytes": t.size_bytes,
                        "exists": t.exists,
                        "command": t.command,
                    }
                    for t in info.targets
                ],
            }
            for info in infos
        ],
    }

    CACHE_FILE.write_text(json.dumps(cache_data, ensure_ascii=False))


def load_scan_cache() -> list[Any] | None:
    """Load scan results from cache if valid.

    Returns:
        List of CleanerInfo objects if cache is valid, None otherwise.
    """
    from cc_cleaner.core.base import CleanerInfo, CleanMethod, CleanTarget, RiskLevel

    if not CACHE_FILE.exists():
        return None

    try:
        cache_data = json.loads(CACHE_FILE.read_text())

        # Check if cache is expired
        timestamp = cache_data.get("timestamp", 0)
        if time.time() - timestamp > CACHE_TTL_SECONDS:
            return None

        # Reconstruct CleanerInfo objects
        infos = []
        for info_data in cache_data.get("infos", []):
            targets = [
                CleanTarget(
                    name=t["name"],
                    path=Path(t["path"]) if t["path"] else None,
                    description=t["description"],
                    risk_level=RiskLevel(t["risk_level"]),
                    clean_method=CleanMethod(t["clean_method"]),
                    size_bytes=t["size_bytes"],
                    exists=t["exists"],
                    command=t.get("command"),
                )
                for t in info_data["targets"]
            ]

            info = CleanerInfo(
                name=info_data["name"],
                description=info_data["description"],
                risk_level=RiskLevel(info_data["risk_level"]),
                total_size=info_data["total_size"],
                targets=targets,
            )
            infos.append(info)

        return infos

    except (json.JSONDecodeError, KeyError, ValueError):
        # Invalid cache, ignore
        return None


def clear_scan_cache() -> None:
    """Clear the scan cache."""
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()


def get_cache_age() -> float | None:
    """Get cache age in seconds, or None if no cache."""
    if not CACHE_FILE.exists():
        return None

    try:
        cache_data = json.loads(CACHE_FILE.read_text())
        timestamp = cache_data.get("timestamp", 0)
        return time.time() - timestamp
    except (json.JSONDecodeError, KeyError):
        return None
