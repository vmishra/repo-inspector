"""Mermaid diagram formatting and validation."""


def format_diagram(mermaid_code: str) -> str:
    """
    Format and clean Mermaid diagram code.

    Args:
        mermaid_code: Raw Mermaid diagram code

    Returns:
        Cleaned and formatted Mermaid code
    """
    lines = mermaid_code.strip().split("\n")
    cleaned_lines = []

    for line in lines:
        # Remove any leading/trailing whitespace
        line = line.strip()

        # Skip empty lines at start/end
        if not line and not cleaned_lines:
            continue

        cleaned_lines.append(line)

    # Remove trailing empty lines
    while cleaned_lines and not cleaned_lines[-1]:
        cleaned_lines.pop()

    return "\n".join(cleaned_lines)


def wrap_for_markdown(mermaid_code: str) -> str:
    """
    Wrap Mermaid code in a markdown code block.

    Args:
        mermaid_code: Mermaid diagram code

    Returns:
        Mermaid code wrapped in ```mermaid code block
    """
    formatted = format_diagram(mermaid_code)
    return f"```mermaid\n{formatted}\n```"


def wrap_for_text(mermaid_code: str) -> str:
    """
    Format Mermaid code for text output.

    Args:
        mermaid_code: Mermaid diagram code

    Returns:
        Formatted Mermaid code with header
    """
    formatted = format_diagram(mermaid_code)
    return f"Mermaid Diagram:\n\n{formatted}"


def validate_mermaid(mermaid_code: str) -> tuple[bool, str | None]:
    """
    Basic validation of Mermaid diagram syntax.

    Args:
        mermaid_code: Mermaid diagram code to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    code = mermaid_code.strip()

    if not code:
        return False, "Empty diagram"

    lines = code.split("\n")
    first_line = lines[0].strip().lower()

    # Check for valid diagram type
    valid_starts = [
        "flowchart",
        "graph",
        "sequencediagram",
        "classdiagram",
        "statediagram",
        "erdiagram",
        "gantt",
        "pie",
        "journey",
    ]

    if not any(first_line.startswith(s) for s in valid_starts):
        return False, f"Invalid diagram type: {first_line}"

    # Check for basic structure (at least some content after header)
    content_lines = [l for l in lines[1:] if l.strip()]
    if not content_lines:
        return False, "Diagram has no content"

    return True, None
