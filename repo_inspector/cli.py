"""CLI entrypoint for repo-inspector."""

import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from . import __version__
from .loader import load_repository
from .output import output_result
from .summarizer import inspect_repository

app = typer.Typer(
    name="repo-inspector",
    help="Understand any codebase in minutes.",
    no_args_is_help=True,
)

console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"repo-inspector {__version__}")
        raise typer.Exit()


@app.command()
def inspect(
    path: Annotated[
        Path,
        typer.Argument(
            help="Path to the repository to analyze",
            exists=True,
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
        ),
    ],
    level: Annotated[
        str,
        typer.Option(
            "--level",
            "-l",
            help="Explanation level: 'beginner' or 'senior'",
        ),
    ] = "beginner",
    diagram: Annotated[
        bool,
        typer.Option(
            "--diagram",
            "-d",
            help="Generate a Mermaid architecture diagram",
        ),
    ] = False,
    output_format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Output format: 'text' or 'markdown'",
        ),
    ] = "text",
    api_key: Annotated[
        Optional[str],
        typer.Option(
            "--api-key",
            envvar="GEMINI_API_KEY",
            help="Gemini API key (or set GEMINI_API_KEY env var)",
        ),
    ] = None,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit",
        ),
    ] = None,
) -> None:
    """
    Analyze a repository and generate a comprehensive summary.

    Examples:

        repo-inspector .

        repo-inspector /path/to/repo --level senior

        repo-inspector . --diagram --format markdown
    """
    # Validate level
    if level not in ("beginner", "senior"):
        console.print(f"[red]Error:[/red] Invalid level '{level}'. Use 'beginner' or 'senior'.")
        raise typer.Exit(1)

    # Validate format
    if output_format not in ("text", "markdown"):
        console.print(
            f"[red]Error:[/red] Invalid format '{output_format}'. Use 'text' or 'markdown'."
        )
        raise typer.Exit(1)

    # Check API key
    if not api_key:
        console.print(
            "[red]Error:[/red] Gemini API key required. "
            "Set GEMINI_API_KEY environment variable or use --api-key option."
        )
        raise typer.Exit(1)

    try:
        # Load repository files
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            progress.add_task("Loading repository files...", total=None)
            files = load_repository(path)

        if not files:
            console.print("[yellow]No files found to analyze.[/yellow]")
            console.print(
                "Make sure the repository contains supported file types "
                "(.py, .js, .ts, .go, .java, .yaml, .json, .md, etc.)"
            )
            raise typer.Exit(0)

        console.print(f"[dim]Found {len(files)} files to analyze[/dim]")

        # Run analysis with progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task_id = progress.add_task("Analyzing...", total=None)

            def on_progress(stage: str, current: int, total: int) -> None:
                if stage == "analyzing":
                    progress.update(task_id, description=f"Analyzing chunk {current}/{total}...")
                elif stage == "synthesizing":
                    progress.update(task_id, description="Synthesizing results...")

            result = inspect_repository(
                files,
                level=level,
                generate_diagram=diagram,
                api_key=api_key,
                on_progress=on_progress,
            )

        # Output results
        output_result(result, output_format, console)

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if "--verbose" in sys.argv:
            console.print_exception()
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
