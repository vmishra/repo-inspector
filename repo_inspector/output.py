"""Output formatting for different formats."""

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from .diagrams import wrap_for_markdown, wrap_for_text
from .summarizer import InspectionResult


def format_text(result: InspectionResult, console: Console) -> None:
    """
    Output inspection result as formatted text to console.

    Args:
        result: The inspection result to format
        console: Rich console for output
    """
    # Header
    console.print()
    console.print(
        Panel(
            Text("Repository Analysis", style="bold cyan"),
            subtitle=f"{result.file_count} files analyzed in {result.chunk_count} chunks",
        )
    )
    console.print()

    # Main summary (rendered as markdown for nice formatting)
    md = Markdown(result.summary)
    console.print(md)

    # Diagram if present
    if result.diagram:
        console.print()
        console.print(Panel(Text("Architecture Diagram", style="bold green")))
        console.print()
        console.print(wrap_for_text(result.diagram))

    console.print()


def format_markdown(result: InspectionResult) -> str:
    """
    Format inspection result as Markdown string.

    Args:
        result: The inspection result to format

    Returns:
        Markdown formatted string
    """
    parts = []

    # Header
    parts.append("# Repository Analysis")
    parts.append("")
    parts.append(f"*{result.file_count} files analyzed in {result.chunk_count} chunks*")
    parts.append("")

    # Main summary
    parts.append(result.summary)

    # Diagram if present
    if result.diagram:
        parts.append("")
        parts.append("## Architecture Diagram")
        parts.append("")
        parts.append(wrap_for_markdown(result.diagram))

    parts.append("")

    return "\n".join(parts)


def output_result(
    result: InspectionResult,
    output_format: str,
    console: Console,
) -> None:
    """
    Output inspection result in the specified format.

    Args:
        result: The inspection result to output
        output_format: 'text' or 'markdown'
        console: Rich console for output
    """
    if output_format == "markdown":
        markdown_output = format_markdown(result)
        console.print(markdown_output)
    else:
        format_text(result, console)
