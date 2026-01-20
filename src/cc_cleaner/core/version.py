"""Version checking utilities for cc-cleaner."""

import json
import time
from pathlib import Path
from typing import Optional
from urllib.request import urlopen
from urllib.error import URLError

# Cache file location
CACHE_DIR = Path.home() / ".cache" / "cc-cleaner"
VERSION_CACHE_FILE = CACHE_DIR / "version_check.json"
CACHE_TTL_SECONDS = 24 * 60 * 60  # 24 hours

PYPI_URL = "https://pypi.org/pypi/cc-cleaner/json"


def get_current_version() -> str:
    """Get the currently installed version."""
    try:
        from importlib.metadata import version
        return version("cc-cleaner")
    except Exception:
        return "0.0.0"


def _parse_version(version_str: str) -> tuple[int, ...]:
    """Parse version string to tuple for comparison."""
    try:
        return tuple(int(x) for x in version_str.split(".")[:3])
    except (ValueError, AttributeError):
        return (0, 0, 0)


def _read_cache() -> Optional[dict]:
    """Read cached version info if still valid."""
    try:
        if not VERSION_CACHE_FILE.exists():
            return None

        data = json.loads(VERSION_CACHE_FILE.read_text())
        cached_time = data.get("timestamp", 0)

        if time.time() - cached_time < CACHE_TTL_SECONDS:
            return data
        return None
    except Exception:
        return None


def _write_cache(latest_version: str) -> None:
    """Write version info to cache."""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "timestamp": time.time(),
            "latest_version": latest_version,
        }
        VERSION_CACHE_FILE.write_text(json.dumps(data))
    except Exception:
        pass  # Silently ignore cache write errors


def fetch_latest_version(timeout: float = 2.0) -> Optional[str]:
    """Fetch the latest version from PyPI.

    Args:
        timeout: Request timeout in seconds (default 2s to not slow down CLI)

    Returns:
        Latest version string or None if fetch failed
    """
    # Check cache first
    cached = _read_cache()
    if cached:
        return cached.get("latest_version")

    try:
        with urlopen(PYPI_URL, timeout=timeout) as response:
            data = json.loads(response.read().decode())
            latest = data.get("info", {}).get("version")
            if latest:
                _write_cache(latest)
            return latest
    except (URLError, TimeoutError, json.JSONDecodeError, Exception):
        return None


def check_for_update() -> Optional[str]:
    """Check if a newer version is available.

    Returns:
        The latest version string if an update is available, None otherwise
    """
    current = get_current_version()
    latest = fetch_latest_version()

    if not latest:
        return None

    current_tuple = _parse_version(current)
    latest_tuple = _parse_version(latest)

    if latest_tuple > current_tuple:
        return latest

    return None


def get_upgrade_message(latest_version: str) -> str:
    """Get the upgrade notification message."""
    current = get_current_version()
    return (
        f"[dim]Update available: {current} → [green]{latest_version}[/green]. "
        f"Run [cyan]pipx upgrade cc-cleaner[/cyan] or [cyan]uv tool upgrade cc-cleaner[/cyan][/dim]"
    )
