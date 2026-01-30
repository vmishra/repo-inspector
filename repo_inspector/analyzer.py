"""LLM-based code analysis using Gemini."""

import os
from dataclasses import dataclass

from google import genai
from google.genai import types

from .chunker import Chunk
from .prompts import get_analysis_prompt, get_synthesis_prompt, get_diagram_prompt


@dataclass
class AnalysisResult:
    """Result of analyzing a chunk of code."""

    chunk_index: int
    analysis: str


@dataclass
class SynthesisResult:
    """Final synthesized analysis of the repository."""

    summary: str
    diagram: str | None = None


class Analyzer:
    """Handles LLM-based code analysis."""

    def __init__(self, api_key: str | None = None):
        """
        Initialize the analyzer.

        Args:
            api_key: Gemini API key. If not provided, reads from GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key required. Set GEMINI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.0-flash"

    def _generate(self, prompt: str) -> str:
        """Generate content using Gemini."""
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ]

        config = types.GenerateContentConfig(
            temperature=0.3,  # Lower temperature for more consistent analysis
            max_output_tokens=8192,
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=config,
        )

        return response.text

    def analyze_chunk(self, chunk: Chunk, level: str, chunk_index: int) -> AnalysisResult:
        """
        Analyze a single chunk of code.

        Args:
            chunk: The chunk of files to analyze
            level: Analysis level ('beginner' or 'senior')
            chunk_index: Index of this chunk for tracking

        Returns:
            AnalysisResult with the analysis text
        """
        prompt_template = get_analysis_prompt(level)
        code_content = chunk.to_text()
        prompt = prompt_template.replace("{code}", code_content)

        analysis = self._generate(prompt)

        return AnalysisResult(
            chunk_index=chunk_index,
            analysis=analysis,
        )

    def synthesize(
        self,
        analyses: list[AnalysisResult],
        level: str,
        generate_diagram: bool = False,
    ) -> SynthesisResult:
        """
        Synthesize chunk analyses into a final report.

        Args:
            analyses: List of chunk analysis results
            level: Analysis level ('beginner' or 'senior')
            generate_diagram: Whether to generate a Mermaid diagram

        Returns:
            SynthesisResult with the final summary and optional diagram
        """
        # Combine all analyses
        combined_analyses = "\n\n---\n\n".join(
            f"### Chunk {a.chunk_index + 1} Analysis\n\n{a.analysis}" for a in analyses
        )

        # Generate synthesis
        synthesis_prompt = get_synthesis_prompt(level)
        prompt = synthesis_prompt.replace("{analyses}", combined_analyses)
        summary = self._generate(prompt)

        # Generate diagram if requested
        diagram = None
        if generate_diagram:
            diagram_prompt = get_diagram_prompt()
            prompt = diagram_prompt.replace("{analysis}", summary)
            diagram_response = self._generate(prompt)

            # Extract mermaid code block
            diagram = self._extract_mermaid(diagram_response)

        return SynthesisResult(
            summary=summary,
            diagram=diagram,
        )

    def _extract_mermaid(self, response: str) -> str:
        """Extract Mermaid diagram code from response."""
        # Look for mermaid code block
        if "```mermaid" in response:
            start = response.find("```mermaid") + len("```mermaid")
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()

        # If no code block, try to use the whole response
        # (in case LLM just output raw mermaid)
        lines = response.strip().split("\n")
        if lines and lines[0].startswith("flowchart"):
            return response.strip()

        return response.strip()
