# dev-cleaner

[![PyPI version](https://badge.fury.io/py/dev-cleaner.svg)](https://badge.fury.io/py/dev-cleaner)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A CLI tool to clean development caches and free disk space. Supports npm, pip, Cargo, Docker, Homebrew, Claude Code, and more.

## Installation

### Using pipx (recommended)

```bash
pipx install dev-cleaner
```

### Using uv

```bash
uv tool install dev-cleaner
```

### Using pip

```bash
pip install dev-cleaner
```

## Quick Start

```bash
# Show status of all cleaners with disk usage
dev-cleaner status

# Show status for a specific cleaner
dev-cleaner status npm

# Clean all safe targets (dry run)
dev-cleaner clean --dry-run

# Clean all safe targets
dev-cleaner clean

# Clean a specific cleaner
dev-cleaner clean npm

# Clean with confirmation prompts disabled
dev-cleaner clean -y

# List all available cleaners
dev-cleaner list
```

## Supported Cleaners

| Cleaner | Description | Default Risk |
|---------|-------------|--------------|
| `npm` | npm package cache (`~/.npm/_cacache`, `~/.npm/_logs`) | Safe |
| `yarn` | Yarn package cache | Safe |
| `pnpm` | pnpm store and cache | Moderate |
| `pip` | pip package cache | Safe |
| `uv` | uv Python package cache | Safe |
| `cargo` | Cargo (Rust) registry and git cache | Safe |
| `go` | Go module and build cache | Safe |
| `gradle` | Gradle caches and daemon | Moderate |
| `cocoapods` | CocoaPods cache and repos (macOS) | Moderate |
| `homebrew` | Homebrew download cache (macOS) | Safe |
| `docker` | Docker build cache, images, system prune | Dangerous |
| `claude` | Claude Code debug logs, telemetry, transcripts | Safe/Moderate |

## Commands

### `status [CLEANER]`

Show disk usage for all cleaners or a specific one.

```bash
dev-cleaner status          # All cleaners
dev-cleaner status npm      # Only npm
dev-cleaner status --json   # JSON output
```

### `clean [CLEANER]`

Clean caches. By default, only cleans targets with risk level "safe".

```bash
dev-cleaner clean                    # Clean all safe targets
dev-cleaner clean npm                # Clean only npm
dev-cleaner clean --dry-run          # Preview without deleting
dev-cleaner clean --include-moderate # Include moderate-risk targets
dev-cleaner clean --force            # Include dangerous targets (use with caution!)
dev-cleaner clean -y                 # Skip confirmation prompts
```

### `list`

List all available cleaners.

```bash
dev-cleaner list
```

## Risk Levels

Each clean target has a risk level that determines when it will be cleaned:

| Level | Description | When Cleaned |
|-------|-------------|--------------|
| **Safe** | Quick to rebuild, no significant impact | Default (`clean`) |
| **Moderate** | May take time to rebuild | With `--include-moderate` |
| **Dangerous** | Significant impact, data loss possible | With `--force` |

### Examples by Risk Level

**Safe:**
- npm/pip/cargo download caches
- Build caches (Go, Docker builder)
- Log files

**Moderate:**
- pnpm content-addressable store
- Gradle dependency cache
- Claude Code conversation transcripts

**Dangerous:**
- Docker system prune (removes all unused images/containers)

## Safety Features

- **Dry run mode**: Preview what will be deleted with `--dry-run`
- **Risk-based filtering**: Only safe targets are cleaned by default
- **Confirmation prompts**: Interactive confirmation before destructive operations
- **Detailed output**: Shows exactly what's being cleaned and how much space is freed

## Examples

### Free up disk space quickly

```bash
# See what's taking space
dev-cleaner status

# Clean all safe caches
dev-cleaner clean -y

# If you need more space, include moderate-risk targets
dev-cleaner clean --include-moderate -y
```

### Clean specific tool caches

```bash
# After npm issues, clear the cache
dev-cleaner clean npm

# Clean Python package caches (pip + uv)
dev-cleaner clean pip
dev-cleaner clean uv

# Clean Rust build artifacts
dev-cleaner clean cargo
```

### Docker cleanup

```bash
# Safe: only build cache
dev-cleaner clean docker

# Aggressive: full system prune (requires --force)
dev-cleaner clean docker --force
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Adding a New Cleaner

1. Create a new file in `src/dev_cleaner/cleaners/`
2. Implement a class that inherits from `BaseCleaner`
3. Implement the `get_targets()` method
4. Register with `@register_cleaner` decorator

Example:

```python
from dev_cleaner.core import (
    BaseCleaner,
    CleanMethod,
    CleanTarget,
    RiskLevel,
    expand_path,
    get_dir_size,
    register_cleaner,
)

@register_cleaner
class MyCleaner(BaseCleaner):
    name = "my-tool"
    description = "My tool caches"
    risk_level = RiskLevel.SAFE

    def get_targets(self) -> list[CleanTarget]:
        cache_path = expand_path("~/.my-tool/cache")
        return [
            CleanTarget(
                name="my-tool/cache",
                path=cache_path,
                description="My tool download cache",
                risk_level=RiskLevel.SAFE,
                clean_method=CleanMethod.DELETE_DIR,
                size_bytes=get_dir_size(cache_path) if cache_path.exists() else 0,
                exists=cache_path.exists(),
            )
        ]
```

## License

MIT License - see [LICENSE](LICENSE) for details.
