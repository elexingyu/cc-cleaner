"""CLI entry point for dev-cleaner."""

from typing import Optional

import typer

from cc_cleaner.core import (
    RiskLevel,
    check_for_update,
    execute_clean_all,
    get_all_cleaner_infos,
    get_cleaner,
    get_cleaner_names,
    get_upgrade_message,
)
from cc_cleaner.ui import (
    confirm_clean,
    console,
    create_scan_progress,
    print_clean_results,
    print_cleaner_detail,
    print_cleaner_list,
    print_error,
    print_status_table,
    print_warning,
)

# Import all cleaners to register them
import cc_cleaner.cleaners  # noqa: F401

app = typer.Typer(
    name="cc-cleaner",
    help="The cache cleaner for the AI Coding era",
    no_args_is_help=True,
    add_completion=False,
)


def _check_and_notify_update() -> None:
    """Check for updates and print notification if available."""
    try:
        latest = check_for_update()
        if latest:
            console.print()
            console.print(get_upgrade_message(latest))
    except Exception:
        pass  # Silently ignore any errors


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
        # Show all cleaners with progress
        from cc_cleaner.core import get_all_cleaners

        cleaners_list = get_all_cleaners()
        infos = []

        with create_scan_progress() as progress:
            task = progress.add_task("Scanning...", total=len(cleaners_list))
            for c in cleaners_list:
                progress.update(task, description=f"Scanning [cyan]{c.name}[/cyan]...")
                infos.append(c.get_info())
                progress.advance(task)

        print_status_table(infos, show_all=all)

    _check_and_notify_update()


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

    with create_scan_progress() as progress:
        task = progress.add_task("Scanning...", total=len(cleaners))
        for name in cleaners:
            progress.update(task, description=f"Scanning [cyan]{name}[/cyan]...")
            c = get_cleaner(name)
            if c:
                targets = c.get_targets()
                available_targets = [t for t in targets if t.exists]
                if available_targets:
                    all_targets.extend(available_targets)
                    cleaner_names_to_clean.append(name)
            progress.advance(task)

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

    _check_and_notify_update()


@app.command(name="list")
def list_cleaners() -> None:
    """List all available cleaners."""
    infos = get_all_cleaner_infos()
    print_cleaner_list(infos)

    _check_and_notify_update()


@app.command(name="version")
def show_version() -> None:
    """Show the current version."""
    from cc_cleaner.core import get_current_version

    console.print(f"cc-cleaner [bold]{get_current_version()}[/bold]")
    _check_and_notify_update()


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
