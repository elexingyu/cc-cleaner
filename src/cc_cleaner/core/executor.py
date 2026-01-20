"""Execution engine for cleaning operations."""

import shutil
import subprocess
from pathlib import Path

from .base import CleanMethod, CleanResult, CleanTarget, RiskLevel
from .scanner import get_dir_size
from .security import SecurityError, validate_command, validate_path_for_deletion


def delete_directory(path: Path, dry_run: bool = False) -> tuple[bool, int, str | None]:
    """Delete a directory and return (success, freed_bytes, error)."""
    if not path.exists():
        return True, 0, None

    # Security check
    try:
        validate_path_for_deletion(path)
    except SecurityError as e:
        return False, 0, f"Security check failed: {e}"

    size = get_dir_size(path)

    if dry_run:
        return True, size, None

    try:
        # Check if path is a symlink - delete the symlink, not the target
        if path.is_symlink():
            path.unlink()
        else:
            shutil.rmtree(path)
        return True, size, None
    except Exception as e:
        return False, 0, str(e)


def delete_files(
    path: Path, pattern: str, dry_run: bool = False
) -> tuple[bool, int, str | None]:
    """Delete files matching a pattern and return (success, freed_bytes, error)."""
    if not path.exists():
        return True, 0, None

    # Security check on base path
    try:
        validate_path_for_deletion(path)
    except SecurityError as e:
        return False, 0, f"Security check failed: {e}"

    total_freed = 0
    errors = []

    try:
        for entry in path.glob(pattern):
            try:
                # Skip symlinks entirely for safety
                if entry.is_symlink():
                    continue

                if entry.is_file():
                    size = entry.stat().st_size
                    if not dry_run:
                        entry.unlink()
                    total_freed += size
                elif entry.is_dir():
                    # Validate each subdirectory before deletion
                    try:
                        validate_path_for_deletion(entry)
                    except SecurityError:
                        continue  # Skip unsafe paths silently

                    size = get_dir_size(entry)
                    if not dry_run:
                        shutil.rmtree(entry)
                    total_freed += size
            except Exception as e:
                errors.append(f"{entry}: {e}")
    except Exception as e:
        return False, total_freed, str(e)

    if errors:
        return False, total_freed, "; ".join(errors)

    return True, total_freed, None


def run_command(command: list[str], dry_run: bool = False) -> tuple[bool, int, str | None]:
    """Run a cleanup command and return (success, freed_bytes, error).

    Args:
        command: Command as a list of strings (NOT a shell string)
        dry_run: If True, don't actually run the command
    """
    if dry_run:
        return True, 0, None

    # Security check - only allow whitelisted commands
    try:
        validate_command(command)
    except SecurityError as e:
        return False, 0, f"Security check failed: {e}"

    try:
        result = subprocess.run(
            command,  # List form, no shell=True
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            return False, 0, result.stderr or "Command failed"
        return True, 0, None
    except subprocess.TimeoutExpired:
        return False, 0, "Command timed out"
    except Exception as e:
        return False, 0, str(e)


def execute_clean(target: CleanTarget, dry_run: bool = False) -> CleanResult:
    """Execute cleaning for a single target."""
    if not target.exists and target.clean_method != CleanMethod.COMMAND:
        return CleanResult(target=target, success=True, freed_bytes=0)

    if target.clean_method == CleanMethod.DELETE_DIR:
        if target.path is None:
            return CleanResult(
                target=target, success=False, error="No path specified for DELETE_DIR"
            )
        success, freed, error = delete_directory(target.path, dry_run)

    elif target.clean_method == CleanMethod.DELETE_FILES:
        if target.path is None or target.pattern is None:
            return CleanResult(
                target=target,
                success=False,
                error="Path and pattern required for DELETE_FILES",
            )
        success, freed, error = delete_files(target.path, target.pattern, dry_run)

    elif target.clean_method == CleanMethod.COMMAND:
        if target.command is None:
            return CleanResult(
                target=target, success=False, error="No command specified"
            )
        success, freed, error = run_command(target.command, dry_run)
        # For commands, we use the pre-calculated size as freed amount
        if success:
            freed = target.size_bytes

    else:
        return CleanResult(
            target=target, success=False, error=f"Unknown clean method: {target.clean_method}"
        )

    return CleanResult(target=target, success=success, freed_bytes=freed, error=error)


def execute_clean_all(
    targets: list[CleanTarget],
    dry_run: bool = False,
    force: bool = False,
    skip_dangerous: bool = True,
) -> list[CleanResult]:
    """Execute cleaning for multiple targets."""
    results = []

    for target in targets:
        # Skip dangerous targets unless force is specified
        if target.risk_level == RiskLevel.DANGEROUS and skip_dangerous and not force:
            results.append(
                CleanResult(
                    target=target,
                    success=False,
                    error="Skipped: requires --force flag",
                )
            )
            continue

        result = execute_clean(target, dry_run)
        results.append(result)

    return results
