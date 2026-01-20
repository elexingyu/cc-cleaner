# cc-cleaner

[![PyPI version](https://badge.fury.io/py/cc-cleaner.svg)](https://badge.fury.io/py/cc-cleaner)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**The cache cleaner for the AI Coding era.**

> cc = Claude Code / Cursor / Copilot / Coding Cache

## The Problem

In the AI Coding era, tools like **Claude Code**, **Cursor**, and **GitHub Copilot** have revolutionized how we write code. But there's a hidden cost:

- **Rapid project iteration** - AI helps you scaffold projects in seconds, leaving behind `node_modules`, `venv`, build artifacts
- **Massive conversation logs** - Claude Code stores every conversation as `.jsonl` files (can grow to GB!)
- **Cache explosion** - Package managers (npm, pip, cargo) cache everything you've ever installed
- **Debug & telemetry data** - AI tools generate tons of logs and telemetry

**Result:** Your disk fills up 10x faster than before.

## The Solution

`cc-cleaner` is built specifically for AI-assisted developers. It knows exactly what to clean:

```bash
# Install
pipx install cc-cleaner

# See what's eating your disk
cc-cleaner status

# Clean safely
cc-cleaner clean
```

## Quick Start

```bash
# Show all cleanable caches with sizes
cc-cleaner status

# Clean all safe targets (dry run first)
cc-cleaner clean --dry-run

# Actually clean
cc-cleaner clean

# Clean specific tool
cc-cleaner clean claude
cc-cleaner clean npm
```

## What It Cleans

### AI Coding Tools

| Tool | What's Cleaned | Risk |
|------|----------------|------|
| **Claude Code** | Debug logs, telemetry, conversation transcripts (`.jsonl`) | Safe/Moderate |

### Package Managers

| Tool | What's Cleaned | Risk |
|------|----------------|------|
| **npm** | `~/.npm/_cacache`, `~/.npm/_logs` | Safe |
| **yarn** | Yarn cache, Berry cache | Safe |
| **pnpm** | Store, metadata cache | Moderate |
| **pip** | `~/.cache/pip` | Safe |
| **uv** | `~/.cache/uv` | Safe |
| **cargo** | Registry cache, git deps | Safe |
| **go** | Module cache, build cache | Safe |

### Build Tools & IDEs

| Tool | What's Cleaned | Risk |
|------|----------------|------|
| **Gradle** | Caches, daemon, wrapper dists | Moderate |
| **CocoaPods** | Specs repos, download cache | Moderate |
| **Homebrew** | Download cache, logs | Safe |
| **Docker** | Build cache, dangling images, system prune | Safe/Dangerous |

## Commands

### `cc-cleaner status [CLEANER]`

Show disk usage. See how much space you can reclaim.

```bash
cc-cleaner status          # All cleaners
cc-cleaner status claude   # Only Claude Code
cc-cleaner status --json   # JSON output for scripts
```

### `cc-cleaner clean [CLEANER]`

Clean caches. Safe by default.

```bash
cc-cleaner clean                    # Clean all safe targets
cc-cleaner clean npm                # Clean only npm
cc-cleaner clean --dry-run          # Preview only
cc-cleaner clean --include-moderate # Include moderate-risk targets
cc-cleaner clean --force            # Include dangerous targets
cc-cleaner clean -y                 # Skip confirmation
```

### `cc-cleaner list`

List all available cleaners.

## Risk Levels

| Level | Description | Cleaned By Default |
|-------|-------------|-------------------|
| **Safe** | Quick to rebuild, no impact | Yes |
| **Moderate** | May take time to rebuild | With `--include-moderate` |
| **Dangerous** | Potential data loss | With `--force` |

### What's Safe?

- npm/pip/cargo download caches (re-download on demand)
- Build caches (rebuild automatically)
- Log files (you probably don't need them)
- Claude Code telemetry/debug logs

### What's Moderate?

- Claude Code conversation transcripts (your chat history!)
- pnpm store (shared across projects)
- Gradle dependencies (slow to re-download)

### What's Dangerous?

- Docker system prune (removes all unused images/containers)

## Installation

### pipx (Recommended)

```bash
pipx install cc-cleaner
```

### uv

```bash
uv tool install cc-cleaner
```

### pip

```bash
pip install cc-cleaner
```

## Real World Usage

### Weekly Cleanup Routine

```bash
# Check what's taking space
cc-cleaner status

# Clean safe stuff (no confirmation needed)
cc-cleaner clean -y

# Review and clean moderate stuff
cc-cleaner clean --include-moderate
```

### After Heavy AI Coding Session

```bash
# Claude Code transcripts can grow huge
cc-cleaner status claude

# Clean old conversations (keep your sanity and disk space)
cc-cleaner clean claude --include-moderate
```

### Before Running Low on Disk

```bash
# Nuclear option - clean everything safe + moderate
cc-cleaner clean --include-moderate -y

# Check Docker specifically
cc-cleaner status docker
cc-cleaner clean docker --force  # If you really need space
```

## Contributing

Adding a new cleaner is easy:

```python
from cc_cleaner.core import (
    BaseCleaner, CleanMethod, CleanTarget, RiskLevel,
    expand_path, get_dir_size, register_cleaner,
)

@register_cleaner
class MyCleaner(BaseCleaner):
    name = "my-tool"
    description = "My AI coding tool caches"
    risk_level = RiskLevel.SAFE

    def get_targets(self) -> list[CleanTarget]:
        cache = expand_path("~/.my-tool/cache")
        return [
            CleanTarget(
                name="my-tool/cache",
                path=cache,
                description="My tool cache",
                risk_level=RiskLevel.SAFE,
                clean_method=CleanMethod.DELETE_DIR,
                size_bytes=get_dir_size(cache) if cache.exists() else 0,
                exists=cache.exists(),
            )
        ]
```

PRs welcome for:
- **Cursor** cache locations
- **GitHub Copilot** cache locations
- **Windsurf** / other AI coding tools
- Any tool that AI coders frequently use

## License

MIT

---

**Built for the AI Coding era.** Stop running out of disk space.
