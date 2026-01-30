"""Prompt templates for repository analysis."""

from pathlib import Path

PROMPTS_DIR = Path(__file__).parent


def load_prompt(name: str) -> str:
    """Load a prompt template by name."""
    prompt_file = PROMPTS_DIR / f"{name}.txt"
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt template not found: {name}")
    return prompt_file.read_text()


def get_analysis_prompt(level: str) -> str:
    """Get the analysis prompt for the specified level."""
    return load_prompt(level)


def get_synthesis_prompt(level: str) -> str:
    """Get the synthesis prompt for the specified level."""
    return load_prompt(f"{level}_synthesis")


def get_diagram_prompt() -> str:
    """Get the diagram generation prompt."""
    return load_prompt("diagram")
