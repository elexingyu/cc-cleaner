"""Directory scanning utilities."""

import os
from pathlib import Path


def get_dir_size(path: Path) -> int:
    """Calculate total size of a directory in bytes."""
    if not path.exists():
        return 0

    if path.is_file():
        return path.stat().st_size

    total = 0
    try:
        for entry in path.rglob("*"):
            try:
                if entry.is_file() and not entry.is_symlink():
                    total += entry.stat().st_size
            except (PermissionError, OSError):
                continue
    except (PermissionError, OSError):
        pass

    return total


def get_files_size(path: Path, pattern: str) -> int:
    """Calculate total size of files matching a pattern."""
    if not path.exists():
        return 0

    total = 0
    try:
        for entry in path.glob(pattern):
            try:
                if entry.is_file() and not entry.is_symlink():
                    total += entry.stat().st_size
            except (PermissionError, OSError):
                continue
    except (PermissionError, OSError):
        pass

    return total


def path_exists(path: Path) -> bool:
    """Check if a path exists."""
    return path.exists()


def expand_path(path_str: str) -> Path:
    """Expand ~ and environment variables in a path string."""
    return Path(os.path.expandvars(os.path.expanduser(path_str)))
