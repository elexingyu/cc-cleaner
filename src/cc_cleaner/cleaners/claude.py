"""Claude Code cache cleaner."""

from cc_cleaner.core import (
    BaseCleaner,
    CleanMethod,
    CleanTarget,
    RiskLevel,
    expand_path,
    get_dir_size,
    register_cleaner,
)


@register_cleaner
class ClaudeCleaner(BaseCleaner):
    """Cleaner for Claude Code caches."""

    name = "claude"
    description = "Claude Code debug logs, telemetry, and caches"
    risk_level = RiskLevel.SAFE

    # Subdirectories under ~/.claude that are safe to clean
    SAFE_DIRS = [
        "debug",
        "telemetry",
        "statsig",
        "ide",
    ]

    def get_targets(self) -> list[CleanTarget]:
        """Get list of Claude Code cache targets."""
        targets = []
        claude_home = expand_path("~/.claude")

        # Safe directories - can be deleted without significant impact
        for dirname in self.SAFE_DIRS:
            path = claude_home / dirname
            exists = path.exists()
            size = get_dir_size(path) if exists else 0

            targets.append(
                CleanTarget(
                    name=f"claude/{dirname}",
                    path=path,
                    description=f"Claude Code {dirname} data",
                    risk_level=RiskLevel.SAFE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=size,
                    exists=exists,
                )
            )

        # Conversation transcript files (*.jsonl) - can get large
        # Only delete the transcript files, not the entire projects directory
        projects_path = claude_home / "projects"
        if projects_path.exists():
            jsonl_size = sum(
                f.stat().st_size
                for f in projects_path.rglob("*.jsonl")
                if f.is_file()
            )
            if jsonl_size > 0:
                targets.append(
                    CleanTarget(
                        name="claude/transcripts",
                        path=projects_path,
                        description="Claude Code conversation transcripts (*.jsonl files)",
                        risk_level=RiskLevel.MODERATE,
                        clean_method=CleanMethod.DELETE_FILES,
                        pattern="**/*.jsonl",
                        size_bytes=jsonl_size,
                        exists=True,
                    )
                )

        return targets
