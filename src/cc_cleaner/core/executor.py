"""Execution engine for cleaning operations."""

import shutil
import subprocess
from pathlib import Path

from .base import CleanMethod, CleanResult, CleanTarget, RiskLevel
from .scanner import get_dir_size


def delete_directory(path: Path, dry_run: bool = False) -> tuple[bool, int, str | None]:
    """Delete a directory and return (success, freed_bytes, error)."""
    if not path.exists():
        return True, 0, None

    size = get_dir_size(path)

    if dry_run:
        return True, size, None

    try:
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

    total_freed = 0
    errors = []

    try:
        for entry in path.glob(pattern):
            try:
                if entry.is_file() and not entry.is_symlink():
                    size = entry.stat().st_size
                    if not dry_run:
                        entry.unlink()
                    total_freed += size
                elif entry.is_dir() and not entry.is_symlink():
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


def run_command(command: str, dry_run: bool = False) -> tuple[bool, int, str | None]:
    """Run a cleanup command and return (success, freed_bytes, error)."""
    if dry_run:
        return True, 0, None

    try:
        result = subprocess.run(
            command,
            shell=True,
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
