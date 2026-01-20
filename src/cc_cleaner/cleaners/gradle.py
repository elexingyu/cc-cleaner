"""Gradle cache cleaner."""

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
class GradleCleaner(BaseCleaner):
    """Cleaner for Gradle caches."""

    name = "gradle"
    description = "Gradle build caches and dependencies"
    risk_level = RiskLevel.MODERATE

    def get_targets(self) -> list[CleanTarget]:
        """Get list of Gradle cache targets."""
        targets = []
        gradle_home = expand_path("~/.gradle")

        # Gradle caches (dependencies)
        caches = gradle_home / "caches"
        caches_exists = caches.exists()
        caches_size = get_dir_size(caches) if caches_exists else 0

        if caches_exists:
            targets.append(
                CleanTarget(
                    name="gradle/caches",
                    path=caches,
                    description="Gradle dependency cache",
                    risk_level=RiskLevel.MODERATE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=caches_size,
                    exists=caches_exists,
                )
            )

        # Gradle daemon logs
        daemon = gradle_home / "daemon"
        daemon_exists = daemon.exists()
        daemon_size = get_dir_size(daemon) if daemon_exists else 0

        if daemon_exists:
            targets.append(
                CleanTarget(
                    name="gradle/daemon",
                    path=daemon,
                    description="Gradle daemon data and logs",
                    risk_level=RiskLevel.SAFE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=daemon_size,
                    exists=daemon_exists,
                )
            )

        # Gradle wrapper distributions
        wrapper = gradle_home / "wrapper" / "dists"
        wrapper_exists = wrapper.exists()
        wrapper_size = get_dir_size(wrapper) if wrapper_exists else 0

        if wrapper_exists:
            targets.append(
                CleanTarget(
                    name="gradle/wrapper",
                    path=wrapper,
                    description="Gradle wrapper distributions",
                    risk_level=RiskLevel.MODERATE,
                    clean_method=CleanMethod.DELETE_DIR,
                    size_bytes=wrapper_size,
                    exists=wrapper_exists,
                )
            )

        return targets
