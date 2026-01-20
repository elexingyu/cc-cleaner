"""Core data models and base classes for dev-cleaner."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class RiskLevel(Enum):
    """Risk level for cleaning operations."""

    SAFE = "safe"  # Safe to delete, quick to rebuild
    MODERATE = "moderate"  # Show warning, may take time to rebuild
    DANGEROUS = "dangerous"  # Requires --force, significant impact


class CleanMethod(Enum):
    """Method used for cleaning."""

    DELETE_DIR = "delete_dir"  # Delete entire directory
    DELETE_FILES = "delete_files"  # Delete files matching pattern
    COMMAND = "command"  # Execute a cleanup command


@dataclass
class CleanTarget:
    """Represents a target to be cleaned."""

    name: str
    path: Path | None  # None for command-based cleaning
    description: str
    risk_level: RiskLevel = RiskLevel.SAFE
    clean_method: CleanMethod = CleanMethod.DELETE_DIR
    command: list[str] | None = None  # For COMMAND method (list form, no shell)
    pattern: str | None = None  # For DELETE_FILES method
    size_bytes: int = 0
    exists: bool = False

    def format_size(self) -> str:
        """Format size in human-readable form."""
        return format_size(self.size_bytes)


@dataclass
class CleanResult:
    """Result of a cleaning operation."""

    target: CleanTarget
    success: bool
    freed_bytes: int = 0
    error: str | None = None

    def format_freed(self) -> str:
        """Format freed space in human-readable form."""
        return format_size(self.freed_bytes)


@dataclass
class CleanerInfo:
    """Information about a cleaner."""

    name: str
    description: str
    risk_level: RiskLevel
    targets: list[CleanTarget] = field(default_factory=list)
    total_size: int = 0

    def format_size(self) -> str:
        """Format total size in human-readable form."""
        return format_size(self.total_size)


class BaseCleaner(ABC):
    """Abstract base class for all cleaners."""

    name: str = ""
    description: str = ""
    risk_level: RiskLevel = RiskLevel.SAFE

    @abstractmethod
    def get_targets(self) -> list[CleanTarget]:
        """Get list of clean targets with their sizes."""
        pass

    def clean(
        self, targets: list[CleanTarget] | None = None, dry_run: bool = False
    ) -> list[CleanResult]:
        """Clean the targets. If targets is None, clean all existing targets."""
        from .executor import execute_clean  # Avoid circular import

        if targets is None:
            targets = [t for t in self.get_targets() if t.exists]

        return [execute_clean(target, dry_run) for target in targets]

    def get_info(self) -> CleanerInfo:
        """Get cleaner info with scanned targets."""
        targets = self.get_targets()
        total_size = sum(t.size_bytes for t in targets if t.exists)
        return CleanerInfo(
            name=self.name,
            description=self.description,
            risk_level=self.risk_level,
            targets=targets,
            total_size=total_size,
        )

    def is_available(self) -> bool:
        """Check if this cleaner is available on the current system."""
        targets = self.get_targets()
        return any(t.exists for t in targets)


def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable string."""
    if size_bytes == 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} B"
    return f"{size:.1f} {units[unit_index]}"
