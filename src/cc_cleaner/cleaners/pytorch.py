"""PyTorch cache cleaner."""

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
class PyTorchCleaner(BaseCleaner):
    """Cleaner for PyTorch model caches."""

    name = "pytorch"
    description = "PyTorch model and hub cache"
    risk_level = RiskLevel.MODERATE

    def get_targets(self) -> list[CleanTarget]:
        """Get list of PyTorch cache targets."""
        targets = []

        # ~/.cache/torch - PyTorch model cache
        torch_cache = expand_path("~/.cache/torch")
        if torch_cache.exists():
            size = get_dir_size(torch_cache)
            targets.append(
                CleanTarget(
                    name="pytorch/cache",
                    path=torch_cache,
                    description="PyTorch model and hub cache",
                    risk_level=RiskLevel.MODERATE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=size,
                    exists=True,
                )
            )

        return targets
