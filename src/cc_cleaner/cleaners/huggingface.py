"""Huggingface cache cleaner."""

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
class HuggingfaceCleaner(BaseCleaner):
    """Cleaner for Huggingface model and dataset caches."""

    name = "huggingface"
    description = "Huggingface models and datasets cache"
    risk_level = RiskLevel.MODERATE

    def get_targets(self) -> list[CleanTarget]:
        """Get list of Huggingface cache targets."""
        targets = []

        hf_cache = expand_path("~/.cache/huggingface")
        if not hf_cache.exists():
            return targets

        # Hub contains downloaded models
        hub_path = hf_cache / "hub"
        if hub_path.exists():
            size = get_dir_size(hub_path)
            targets.append(
                CleanTarget(
                    name="huggingface/models",
                    path=hub_path,
                    description="Huggingface downloaded models",
                    risk_level=RiskLevel.MODERATE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=size,
                    exists=True,
                )
            )

        # Datasets cache
        datasets_path = hf_cache / "datasets"
        if datasets_path.exists():
            size = get_dir_size(datasets_path)
            targets.append(
                CleanTarget(
                    name="huggingface/datasets",
                    path=datasets_path,
                    description="Huggingface downloaded datasets",
                    risk_level=RiskLevel.MODERATE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=size,
                    exists=True,
                )
            )

        return targets
