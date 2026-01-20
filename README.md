# cc-cleaner

[![PyPI version](https://badge.fury.io/py/cc-cleaner.svg)](https://badge.fury.io/py/cc-cleaner)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**The cache cleaner for the AI Coding era.**

> cc = Claude Code / Cursor / Copilot / Coding Cache

In the AI Coding era, your disk fills up 10x faster—rapid project iteration, massive conversation logs, exploding package caches. `cc-cleaner` knows exactly what to clean.

## Install

```bash
curl -sSL https://raw.githubusercontent.com/elexingyu/cc-cleaner/master/install.sh | bash
```

<details>
<summary>Other installation methods</summary>

```bash
pipx install cc-cleaner   # pipx
uv tool install cc-cleaner # uv
pip install cc-cleaner     # pip
```
</details>

## Usage

```bash
cc-cleaner status          # See what's eating your disk
cc-cleaner clean all       # Clean all safe caches
cc-cleaner clean claude    # Clean specific tool
cc-cleaner clean all -n    # Dry run (preview only)
```

**Example output:**

```
$ cc-cleaner status

                        Development Cache Status
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┓
┃ Cleaner   ┃ Description                  ┃     Size ┃   Risk   ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━┩
│ uv        │ uv Python package cache      │   5.9 GB │   Safe   │
│ npm       │ npm package cache            │   1.2 GB │   Safe   │
│ claude    │ Claude Code logs & telemetry │ 299.6 MB │   Safe   │
│ cargo     │ Cargo registry cache         │ 102.5 MB │   Safe   │
└───────────┴──────────────────────────────┴──────────┴──────────┘

Total cleanable: 7.5 GB
```

## Supported Cleaners

| Category | Tools |
|----------|-------|
| **AI Coding** | Claude Code |
| **JavaScript** | npm, yarn, pnpm |
| **Python** | pip, uv |
| **Others** | cargo, go, gradle, cocoapods, homebrew, docker |

## Risk Levels

| Level | Cleaned By Default | Examples |
|-------|-------------------|----------|
| **Safe** | Yes | Download caches, logs, telemetry |
| **Moderate** | `--force` | Conversation transcripts, shared stores |
| **Dangerous** | `--force` | Docker system prune |

## Contributing

PRs welcome for **Cursor**, **GitHub Copilot**, **Windsurf**, and other AI coding tools!

## License

MIT
