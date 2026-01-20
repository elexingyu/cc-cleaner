"""Cleaners module - import all cleaners to register them."""

from . import (
    cargo,
    claude,
    cocoapods,
    docker,
    go,
    gradle,
    homebrew,
    npm,
    pip,
    pnpm,
    uv,
    yarn,
)

__all__ = [
    "cargo",
    "claude",
    "cocoapods",
    "docker",
    "go",
    "gradle",
    "homebrew",
    "npm",
    "pip",
    "pnpm",
    "uv",
    "yarn",
]
