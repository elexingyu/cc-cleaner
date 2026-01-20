"""Security utilities for safe file operations."""

import os
from pathlib import Path

# Directories that should NEVER be deleted
DANGEROUS_PATHS = frozenset([
    "/",
    "/bin",
    "/boot",
    "/dev",
    "/etc",
    "/home",
    "/lib",
    "/lib64",
    "/opt",
    "/proc",
    "/root",
    "/run",
    "/sbin",
    "/srv",
    "/sys",
    "/tmp",
    "/usr",
    "/var",
    # macOS specific
    "/Applications",
    "/Library",
    "/System",
    "/Users",
    "/Volumes",
    "/cores",
    "/private",
])

# Only allow deletion within these base directories
ALLOWED_BASE_PATHS = frozenset([
    "~",                    # User home
    "~/.cache",             # XDG cache
    "~/.local",             # XDG local
    "~/.config",            # XDG config (be careful)
    "~/Library/Caches",     # macOS caches
    "~/Library/Logs",       # macOS logs
])


class SecurityError(Exception):
    """Raised when a security check fails."""
    pass


def expand_and_resolve(path: Path) -> Path:
    """Expand ~ and resolve to absolute path without following symlinks."""
    expanded = Path(os.path.expanduser(str(path)))
    # Use resolve() but check for symlinks separately
    return expanded.absolute()


def is_path_safe(path: Path) -> tuple[bool, str]:
    """
    Check if a path is safe to delete.

    Returns:
        (is_safe, reason) - True if safe, False with reason if not
    """
    try:
        resolved = expand_and_resolve(path)
        resolved_str = str(resolved)

        # Check 1: Not a dangerous system path
        for dangerous in DANGEROUS_PATHS:
            if resolved_str == dangerous or resolved_str == dangerous + "/":
                return False, f"Refusing to delete system path: {dangerous}"

        # Check 2: Must be under user's home directory
        home = Path.home()
        try:
            resolved.relative_to(home)
        except ValueError:
            return False, f"Path is outside home directory: {resolved}"

        # Check 3: Not the home directory itself
        if resolved == home:
            return False, "Refusing to delete home directory"

        # Check 4: Not a first-level directory in home (extra safety)
        # e.g., ~/.claude is OK, but ~/Documents is not
        relative = resolved.relative_to(home)
        parts = relative.parts

        if len(parts) == 1:
            # First-level directory - only allow known cache directories
            first_level = parts[0]
            allowed_first_level = {
                ".cache", ".local", ".npm", ".yarn", ".pnpm-store",
                ".cargo", ".rustup", ".gradle", ".cocoapods",
                ".claude", ".cursor", ".copilot",
                ".uv", ".pip", ".go",
                "Library",  # macOS - further checks below
            }
            if first_level not in allowed_first_level:
                return False, f"Not a known cache directory: ~/{first_level}"

        # Check 5: Path doesn't contain suspicious patterns
        path_str = str(path)
        if ".." in path_str:
            return False, "Path contains directory traversal (..)"

        return True, "OK"

    except Exception as e:
        return False, f"Security check failed: {e}"


def is_symlink_safe(path: Path) -> tuple[bool, str]:
    """
    Check if a path is a symlink pointing to a dangerous location.

    Returns:
        (is_safe, reason) - True if safe or not a symlink, False if dangerous symlink
    """
    try:
        if not path.exists():
            return True, "Path does not exist"

        if not path.is_symlink():
            return True, "Not a symlink"

        # Resolve the symlink target
        target = path.resolve()
        target_str = str(target)

        # Check if symlink points to dangerous location
        for dangerous in DANGEROUS_PATHS:
            if target_str == dangerous or target_str.startswith(dangerous + "/"):
                # Allow if target is also under home
                try:
                    target.relative_to(Path.home())
                    return True, "Symlink target is under home"
                except ValueError:
                    return False, f"Symlink points to system path: {target}"

        return True, "Symlink target is safe"

    except Exception as e:
        return False, f"Symlink check failed: {e}"


def validate_path_for_deletion(path: Path) -> None:
    """
    Validate that a path is safe to delete.

    Raises:
        SecurityError: If the path is not safe to delete
    """
    # Check path safety
    safe, reason = is_path_safe(path)
    if not safe:
        raise SecurityError(reason)

    # Check symlink safety
    safe, reason = is_symlink_safe(path)
    if not safe:
        raise SecurityError(reason)


def validate_command(command: list[str]) -> None:
    """
    Validate that a command is safe to execute.

    Only allows known safe commands.

    Raises:
        SecurityError: If the command is not in the allowlist
    """
    if not command:
        raise SecurityError("Empty command")

    # Allowlist of safe commands
    allowed_commands = {
        "docker": {
            "builder prune -f",
            "image prune -f",
            "system prune -af",
        },
        "brew": {
            "cleanup",
            "cleanup --prune=all",
        },
    }

    executable = command[0]
    args = " ".join(command[1:]) if len(command) > 1 else ""

    if executable not in allowed_commands:
        raise SecurityError(f"Unknown command: {executable}")

    if args not in allowed_commands[executable]:
        raise SecurityError(f"Unknown arguments for {executable}: {args}")
