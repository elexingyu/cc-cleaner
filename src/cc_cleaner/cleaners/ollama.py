"""Ollama cache cleaner."""

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
class OllamaCleaner(BaseCleaner):
    """Cleaner for Ollama model caches."""

    name = "ollama"
    description = "Ollama downloaded models"
    risk_level = RiskLevel.MODERATE

    def get_targets(self) -> list[CleanTarget]:
        """Get list of Ollama cache targets."""
        targets = []

        # ~/.ollama/models - Ollama models
        ollama_models = expand_path("~/.ollama/models")
        if ollama_models.exists():
            size = get_dir_size(ollama_models)
            targets.append(
                CleanTarget(
                    name="ollama/models",
                    path=ollama_models,
                    description="Ollama downloaded models (qwen, llama, etc.)",
                    risk_level=RiskLevel.MODERATE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=size,
                    exists=True,
                )
            )

        return targets
