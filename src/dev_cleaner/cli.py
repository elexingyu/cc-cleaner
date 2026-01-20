"""CLI entry point for dev-cleaner."""

from typing import Optional

import typer

from dev_cleaner.core import (
    RiskLevel,
    execute_clean_all,
    get_all_cleaner_infos,
    get_cleaner,
    get_cleaner_names,
)
from dev_cleaner.ui import (
    confirm_clean,
    console,
    print_clean_results,
    print_cleaner_detail,
    print_cleaner_list,
    print_error,
    print_status_table,
    print_warning,
)

# Import all cleaners to register them
import dev_cleaner.cleaners  # noqa: F401

app = typer.Typer(
    name="dev-cleaner",
    help="Clean development caches and free disk space",
    no_args_is_help=True,
)


@app.command()
def status(
    cleaner: Optional[str] = typer.Argument(
        None, help="Specific cleaner to show status for"
    ),
    all: bool = typer.Option(
        False, "--all", "-a", help="Show all cleaners including unavailable ones"
    ),
) -> None:
    """Show status of cleanable caches."""
    if cleaner:
        # Show specific cleaner
        c = get_cleaner(cleaner)
        if not c:
            print_error(f"Unknown cleaner: {cleaner}")
            print_error(f"Available cleaners: {', '.join(get_cleaner_names())}")
            raise typer.Exit(1)

        info = c.get_info()
        print_cleaner_detail(info)
    else:
        # Show all cleaners
        with console.status("[bold]Scanning caches...[/bold]"):
            infos = get_all_cleaner_infos()
        print_status_table(infos, show_all=all)


@app.command()
def clean(
    cleaners: list[str] = typer.Argument(
        ..., help="Cleaners to run (use 'all' for all safe cleaners)"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Preview what would be cleaned"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Skip confirmation and clean dangerous items"
    ),
) -> None:
    """Clean specified caches."""
    available_names = get_cleaner_names()

    # Handle "all" keyword
    if "all" in cleaners:
        cleaners = available_names
        console.print("[bold]Cleaning all available caches...[/bold]")
    else:
        # Validate cleaner names
        invalid = [c for c in cleaners if c not in available_names]
        if invalid:
            print_error(f"Unknown cleaners: {', '.join(invalid)}")
            print_error(f"Available cleaners: {', '.join(available_names)}")
            raise typer.Exit(1)

    # Get all targets from specified cleaners
    all_targets = []
    cleaner_names_to_clean = []

    with console.status("[bold]Scanning caches...[/bold]"):
        for name in cleaners:
            c = get_cleaner(name)
            if c:
                targets = c.get_targets()
                available_targets = [t for t in targets if t.exists]
                if available_targets:
                    all_targets.extend(available_targets)
                    cleaner_names_to_clean.append(name)

    if not all_targets:
        console.print("[dim]Nothing to clean.[/dim]")
        return

    # Show warnings for dangerous items
    dangerous = [t for t in all_targets if t.risk_level == RiskLevel.DANGEROUS]
    if dangerous and not force:
        print_warning(
            f"Found {len(dangerous)} dangerous item(s) that will be skipped. "
            "Use --force to include them."
        )

    # Confirm unless force or dry_run
    if not dry_run and not confirm_clean(cleaner_names_to_clean, force):
        console.print("[dim]Cancelled.[/dim]")
        return

    # Execute cleaning
    action = "Simulating cleanup" if dry_run else "Cleaning"
    with console.status(f"[bold]{action}...[/bold]"):
        results = execute_clean_all(
            all_targets,
            dry_run=dry_run,
            force=force,
            skip_dangerous=not force,
        )

    print_clean_results(results, dry_run=dry_run)


@app.command(name="list")
def list_cleaners() -> None:
    """List all available cleaners."""
    infos = get_all_cleaner_infos()
    print_cleaner_list(infos)


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
