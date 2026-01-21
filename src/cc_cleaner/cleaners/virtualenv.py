"""Python virtualenv cleaner."""

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
class VirtualenvCleaner(BaseCleaner):
    """Cleaner for Python virtualenv directories."""

    name = "virtualenv"
    description = "Python virtualenvs (~/.virtualenvs)"
    risk_level = RiskLevel.MODERATE

    def get_targets(self) -> list[CleanTarget]:
        """Get list of virtualenv targets."""
        targets = []

        # ~/.virtualenvs - virtualenvwrapper default location
        virtualenvs_dir = expand_path("~/.virtualenvs")
        if virtualenvs_dir.exists():
            size = get_dir_size(virtualenvs_dir)
            targets.append(
                CleanTarget(
                    name="virtualenv/all",
                    path=virtualenvs_dir,
                    description="All virtualenvwrapper environments (removes ALL venvs!)",
                    risk_level=RiskLevel.DANGEROUS,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=size,
                    exists=True,
                )
            )

        # ~/.local/share/virtualenvs - pipenv default location
        pipenv_venvs = expand_path("~/.local/share/virtualenvs")
        if pipenv_venvs.exists():
            size = get_dir_size(pipenv_venvs)
            targets.append(
                CleanTarget(
                    name="pipenv/virtualenvs",
                    path=pipenv_venvs,
                    description="Pipenv virtualenvs (removes ALL pipenv venvs!)",
                    risk_level=RiskLevel.DANGEROUS,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=size,
                    exists=True,
                )
            )

        return targets
