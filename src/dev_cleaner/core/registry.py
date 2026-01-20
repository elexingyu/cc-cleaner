"""Registry for managing cleaners."""

from typing import Type

from .base import BaseCleaner, CleanerInfo

# Global registry of cleaners
_cleaners: dict[str, Type[BaseCleaner]] = {}


def register_cleaner(cls: Type[BaseCleaner]) -> Type[BaseCleaner]:
    """Decorator to register a cleaner class."""
    if not cls.name:
        raise ValueError(f"Cleaner {cls.__name__} must have a name")
    _cleaners[cls.name] = cls
    return cls


def get_cleaner(name: str) -> BaseCleaner | None:
    """Get a cleaner instance by name."""
    cls = _cleaners.get(name)
    return cls() if cls else None


def get_all_cleaners() -> list[BaseCleaner]:
    """Get all registered cleaner instances."""
    return [cls() for cls in _cleaners.values()]


def get_cleaner_names() -> list[str]:
    """Get all registered cleaner names."""
    return list(_cleaners.keys())


def get_all_cleaner_infos() -> list[CleanerInfo]:
    """Get info for all registered cleaners."""
    return [cleaner.get_info() for cleaner in get_all_cleaners()]


def get_available_cleaners() -> list[BaseCleaner]:
    """Get all cleaners that are available on this system."""
    return [c for c in get_all_cleaners() if c.is_available()]
