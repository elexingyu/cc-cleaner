# cc-cleaner

[![PyPI version](https://badge.fury.io/py/cc-cleaner.svg)](https://badge.fury.io/py/cc-cleaner)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](README.md) | [中文](README_CN.md)

**AI 编程时代的缓存清理工具**

> cc = Claude Code / Cursor / Copilot / Coding Cache

AI 编程时代，磁盘空间消耗速度是以前的 10 倍——快速迭代的项目、海量对话记录、爆炸式增长的包缓存。`cc-cleaner` 精准清理这些垃圾。

## 安装

```bash
curl -sSL https://raw.githubusercontent.com/elexingyu/cc-cleaner/master/install.sh | bash
```

<details>
<summary>其他安装方式</summary>

```bash
pipx install cc-cleaner   # pipx
uv tool install cc-cleaner # uv
pip install cc-cleaner     # pip
```
</details>

## 使用

```bash
cc-cleaner status          # 查看磁盘占用
cc-cleaner clean all       # 清理所有安全缓存
cc-cleaner clean claude    # 清理指定工具
cc-cleaner clean all -n    # 预览模式（不实际删除）
```

**示例输出：**

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

## 支持的清理器

| 分类 | 工具 |
|------|------|
| **AI 编程** | Claude Code |
| **JavaScript** | npm, yarn, pnpm |
| **Python** | pip, uv |
| **其他** | cargo, go, gradle, cocoapods, homebrew, docker |

## 风险等级

| 等级 | 默认清理 | 示例 |
|------|---------|------|
| **Safe** | 是 | 下载缓存、日志、遥测数据 |
| **Moderate** | 需 `--force` | 对话记录、共享存储 |
| **Dangerous** | 需 `--force` | Docker 系统清理 |

## 贡献

欢迎提交 PR 支持 **Cursor**、**GitHub Copilot**、**Windsurf** 等 AI 编程工具！

## 许可证

MIT
