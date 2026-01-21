"""Interactive selection UI for cache cleaning."""

import sys
from dataclasses import dataclass, field

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from cc_cleaner.core import CleanerInfo, RiskLevel, format_size


@dataclass
class SelectionState:
    """State for interactive selection."""
    items: list[CleanerInfo]
    selected: list[bool] = field(default_factory=list)
    cursor: int = 0

    def __post_init__(self) -> None:
        if not self.selected:
            # Default: select SAFE items only
            self.selected = [item.risk_level == RiskLevel.SAFE for item in self.items]

    @property
    def selected_size(self) -> int:
        """Get total size of selected items."""
        return sum(
            item.total_size
            for item, sel in zip(self.items, self.selected)
            if sel
        )

    @property
    def selected_names(self) -> list[str]:
        """Get names of selected items."""
        return [
            item.name
            for item, sel in zip(self.items, self.selected)
            if sel
        ]

    @property
    def selected_count(self) -> int:
        """Get count of selected items."""
        return sum(self.selected)


def get_risk_style(risk_level: RiskLevel) -> str:
    """Get color style for risk level."""
    return {
        RiskLevel.SAFE: "green",
        RiskLevel.MODERATE: "yellow",
        RiskLevel.DANGEROUS: "red",
    }.get(risk_level, "white")


def render_selection(state: SelectionState, console: Console) -> None:
    """Render the selection UI."""
    # Clear screen
    console.clear()

    table = Table(
        show_header=True,
        header_style="bold",
        title="[bold blue]Select caches to clean[/bold blue]",
        padding=(0, 1),
    )
    table.add_column("#", width=3, justify="right")
    table.add_column("", width=3)  # checkbox
    table.add_column("Cleaner", style="cyan", width=15)
    table.add_column("Size", justify="right", width=10)
    table.add_column("Risk", width=12)
    table.add_column("Description")

    for i, (item, selected) in enumerate(zip(state.items, state.selected)):
        is_cursor = i == state.cursor
        # Use unicode checkmark for better visibility
        checkbox = "[green]✓[/green]" if selected else "[dim]○[/dim]"

        risk_style = get_risk_style(item.risk_level)
        risk_label = {
            RiskLevel.SAFE: "Safe",
            RiskLevel.MODERATE: "Moderate",
            RiskLevel.DANGEROUS: "Danger",
        }.get(item.risk_level, "")

        # Highlight current row
        row_style = "reverse" if is_cursor else ""
        cursor_marker = ">" if is_cursor else ""

        table.add_row(
            cursor_marker,
            checkbox,
            item.name,
            format_size(item.total_size),
            f"[{risk_style}]{risk_label}[/{risk_style}]",
            item.description[:35] + "..." if len(item.description) > 35 else item.description,
            style=row_style,
        )

    console.print(table)
    console.print()

    # Footer with totals
    console.print(
        f"[bold]Selected:[/bold] {state.selected_count} items, "
        f"[bold green]{format_size(state.selected_size)}[/bold green]"
    )
    console.print()
    console.print(
        "[dim]↑/↓[/dim] Navigate  "
        "[dim]Space[/dim] Toggle  "
        "[dim]a[/dim] All  "
        "[dim]n[/dim] None  "
        "[dim]s[/dim] Safe only  "
        "[dim]Enter[/dim] Confirm  "
        "[dim]q[/dim] Quit"
    )


def interactive_select(cleaner_infos: list[CleanerInfo]) -> list[str] | None:
    """
    Show interactive selection UI and return selected cleaner names.

    Returns:
        List of selected cleaner names, or None if cancelled.
    """
    # Filter to only items with size > 0
    items = [info for info in cleaner_infos if info.total_size > 0]

    if not items:
        return []

    # Sort by size descending
    items = sorted(items, key=lambda x: x.total_size, reverse=True)

    state = SelectionState(items=items)
    console = Console()

    # Check if we have a proper terminal
    if not sys.stdin.isatty():
        console.print("[yellow]Interactive mode not available (not a TTY)[/yellow]")
        console.print("Use: cc-cleaner clean <cleaner1> <cleaner2> ...")
        return None

    try:
        import termios
        import tty

        # Get fresh file descriptor
        fd = sys.stdin.fileno()

        # Save terminal settings
        old_settings = termios.tcgetattr(fd)

        try:
            # Render initial state
            render_selection(state, console)

            # Set terminal to raw mode
            tty.setraw(fd)

            while True:
                # Read a single character
                char = sys.stdin.read(1)

                # Handle escape sequences (arrow keys)
                if char == '\x1b':
                    seq = sys.stdin.read(2)
                    if seq == '[A':  # Up arrow
                        state.cursor = max(0, state.cursor - 1)
                    elif seq == '[B':  # Down arrow
                        state.cursor = min(len(items) - 1, state.cursor + 1)
                elif char == ' ':  # Space - toggle selection
                    state.selected[state.cursor] = not state.selected[state.cursor]
                elif char == 'a':  # Select all
                    state.selected = [True] * len(items)
                elif char == 'n':  # Select none
                    state.selected = [False] * len(items)
                elif char == 's':  # Select safe only
                    state.selected = [item.risk_level == RiskLevel.SAFE for item in items]
                elif char == '\r' or char == '\n':  # Enter - confirm
                    # Restore terminal before returning
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    console.clear()
                    return state.selected_names
                elif char == 'q' or char == '\x03':  # q or Ctrl+C - quit
                    # Restore terminal before returning
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    console.clear()
                    return None

                # Restore terminal temporarily to render
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                render_selection(state, console)
                tty.setraw(fd)

        finally:
            # Ensure terminal settings are restored
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    except ImportError:
        # termios not available (Windows)
        console.print("[yellow]Interactive mode not available on this platform[/yellow]")
        console.print("Use: cc-cleaner clean <cleaner1> <cleaner2> ...")
        return None
    except Exception as e:
        console.print(f"[red]Error in interactive mode:[/red] {e}")
        return None
