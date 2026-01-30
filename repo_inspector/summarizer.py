"""Report synthesis and orchestration."""

from dataclasses import dataclass
from typing import Callable

from .analyzer import Analyzer, AnalysisResult, SynthesisResult
from .chunker import Chunk, chunk_files
from .loader import RepoFile, get_file_stats


@dataclass
class InspectionResult:
    """Complete result of inspecting a repository."""

    summary: str
    diagram: str | None
    file_count: int
    chunk_count: int
    stats: dict


def inspect_repository(
    files: list[RepoFile],
    level: str = "beginner",
    generate_diagram: bool = False,
    api_key: str | None = None,
    on_progress: Callable[[str, int, int], None] | None = None,
) -> InspectionResult:
    """
    Inspect a repository and generate a comprehensive summary.

    Args:
        files: List of repository files to analyze
        level: Analysis level ('beginner' or 'senior')
        generate_diagram: Whether to generate a Mermaid diagram
        api_key: Optional Gemini API key
        on_progress: Optional callback for progress updates (stage, current, total)

    Returns:
        InspectionResult with the complete analysis
    """
    if not files:
        return InspectionResult(
            summary="No files found to analyze.",
            diagram=None,
            file_count=0,
            chunk_count=0,
            stats={},
        )

    # Get file statistics
    stats = get_file_stats(files)

    # Chunk files for analysis
    chunks = chunk_files(files)

    if not chunks:
        return InspectionResult(
            summary="No content to analyze after chunking.",
            diagram=None,
            file_count=len(files),
            chunk_count=0,
            stats=stats,
        )

    # Initialize analyzer
    analyzer = Analyzer(api_key=api_key)

    # Analyze each chunk
    analyses: list[AnalysisResult] = []
    for i, chunk in enumerate(chunks):
        if on_progress:
            on_progress("analyzing", i + 1, len(chunks))

        result = analyzer.analyze_chunk(chunk, level, i)
        analyses.append(result)

    # Synthesize results
    if on_progress:
        on_progress("synthesizing", 0, 0)

    synthesis = analyzer.synthesize(
        analyses,
        level,
        generate_diagram=generate_diagram,
    )

    return InspectionResult(
        summary=synthesis.summary,
        diagram=synthesis.diagram,
        file_count=len(files),
        chunk_count=len(chunks),
        stats=stats,
    )
