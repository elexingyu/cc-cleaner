"""Rich console output utilities."""

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.text import Text

from cc_cleaner.core import CleanerInfo, CleanResult, RiskLevel, format_size

console = Console()


def get_risk_style(risk_level: RiskLevel) -> str:
    """Get color style for risk level."""
    return {
        RiskLevel.SAFE: "green",
        RiskLevel.MODERATE: "yellow",
        RiskLevel.DANGEROUS: "red",
    }.get(risk_level, "white")


def get_risk_label(risk_level: RiskLevel) -> str:
    """Get label for risk level."""
    return {
        RiskLevel.SAFE: "Safe",
        RiskLevel.MODERATE: "Moderate",
        RiskLevel.DANGEROUS: "Dangerous",
    }.get(risk_level, "Unknown")


def print_status_table(cleaner_infos: list[CleanerInfo], show_all: bool = False) -> None:
    """Print status table showing all cleaners and their sizes."""
    table = Table(title="Development Cache Status", show_header=True)
    table.add_column("Cleaner", style="cyan")
    table.add_column("Description")
    table.add_column("Size", justify="right", style="bold")
    table.add_column("Risk", justify="center")
    table.add_column("Available", justify="center")

    total_size = 0
    available_size = 0

    for info in sorted(cleaner_infos, key=lambda x: x.total_size, reverse=True):
        is_available = info.total_size > 0
        if not show_all and not is_available:
            continue

        risk_style = get_risk_style(info.risk_level)
        risk_label = get_risk_label(info.risk_level)

        size_text = info.format_size() if is_available else "-"
        available_text = "[green]Yes[/green]" if is_available else "[dim]No[/dim]"

        table.add_row(
            info.name,
            info.description,
            size_text,
            f"[{risk_style}]{risk_label}[/{risk_style}]",
            available_text,
        )

        total_size += info.total_size
        if is_available:
            available_size += info.total_size

    console.print(table)
    console.print()
    console.print(f"[bold]Total cleanable:[/bold] {format_size(available_size)}")


def print_cleaner_detail(info: CleanerInfo) -> None:
    """Print detailed info for a single cleaner."""
    risk_style = get_risk_style(info.risk_level)
    risk_label = get_risk_label(info.risk_level)

    console.print(Panel(
        f"[bold]{info.name}[/bold] - {info.description}\n"
        f"Risk Level: [{risk_style}]{risk_label}[/{risk_style}]\n"
        f"Total Size: [bold]{info.format_size()}[/bold]",
        title=f"Cleaner: {info.name}",
    ))

    if info.targets:
        table = Table(show_header=True)
        table.add_column("Target")
        table.add_column("Path")
        table.add_column("Size", justify="right")
        table.add_column("Exists", justify="center")

        for target in info.targets:
            path_str = str(target.path) if target.path else target.command or "-"
            exists_str = "[green]Yes[/green]" if target.exists else "[dim]No[/dim]"
            size_str = target.format_size() if target.exists else "-"

            table.add_row(
                target.name,
                path_str,
                size_str,
                exists_str,
            )

        console.print(table)


def print_cleaner_list(cleaner_infos: list[CleanerInfo]) -> None:
    """Print list of all available cleaners."""
    table = Table(title="Available Cleaners", show_header=True)
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Risk Level")

    for info in sorted(cleaner_infos, key=lambda x: x.name):
        risk_style = get_risk_style(info.risk_level)
        risk_label = get_risk_label(info.risk_level)

        table.add_row(
            info.name,
            info.description,
            f"[{risk_style}]{risk_label}[/{risk_style}]",
        )

    console.print(table)


def print_clean_results(results: list[CleanResult], dry_run: bool = False) -> None:
    """Print results of cleaning operation."""
    table = Table(
        title="Cleaning Results" + (" (Dry Run)" if dry_run else ""),
        show_header=True,
    )
    table.add_column("Target")
    table.add_column("Status", justify="center")
    table.add_column("Freed", justify="right")
    table.add_column("Note")

    total_freed = 0

    for result in results:
        if result.success:
            status = "[green]OK[/green]"
            freed = result.format_freed()
            total_freed += result.freed_bytes
            note = ""
        else:
            status = "[red]Failed[/red]"
            freed = "-"
            note = result.error or ""

        table.add_row(
            result.target.name,
            status,
            freed,
            note,
        )

    console.print(table)
    console.print()

    action = "Would free" if dry_run else "Freed"
    console.print(f"[bold]{action}:[/bold] {format_size(total_freed)}")


def confirm_clean(cleaners: list[str], force: bool = False) -> bool:
    """Ask for confirmation before cleaning."""
    if force:
        return True

    console.print(f"\n[yellow]About to clean:[/yellow] {', '.join(cleaners)}")
    return console.input("[bold]Continue? (y/N):[/bold] ").lower().strip() == "y"


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[red]Error:[/red] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[yellow]Warning:[/yellow] {message}")


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[green]Success:[/green] {message}")


def create_progress() -> Progress:
    """Create a progress bar for scanning."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    )


def create_scan_progress() -> Progress:
    """Create a progress bar for scanning caches."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=30),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
        transient=True,  # Remove progress bar when done
    )
