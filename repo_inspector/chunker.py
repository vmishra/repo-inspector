"""Smart chunking strategy for LLM context management."""

from dataclasses import dataclass, field

from .loader import RepoFile


@dataclass
class Chunk:
    """A chunk of files to be analyzed together."""

    files: list[RepoFile] = field(default_factory=list)
    total_size: int = 0

    def add_file(self, file: RepoFile) -> None:
        """Add a file to this chunk."""
        self.files.append(file)
        self.total_size += len(file.content)

    def to_text(self) -> str:
        """Convert chunk to text format for LLM input."""
        parts = []
        for f in self.files:
            parts.append(f"=== {f.path} ===")
            parts.append(f.content)
            parts.append("")
        return "\n".join(parts)


# Target ~100KB per chunk - Gemini has 1M token context so we can be generous
TARGET_CHUNK_SIZE = 100 * 1024


def get_directory_group(path: str) -> str:
    """Get the top-level directory group for a file path."""
    parts = path.split("/")
    if len(parts) == 1:
        return "__root__"
    return parts[0]


def chunk_files(files: list[RepoFile], target_size: int = TARGET_CHUNK_SIZE) -> list[Chunk]:
    """
    Split files into chunks for analysis.

    Strategy:
    1. Group files by top-level directory
    2. Try to keep related files together
    3. Split if a group exceeds target size
    4. Prioritize README and entry point files in first chunk

    Args:
        files: List of repository files
        target_size: Target size in bytes per chunk

    Returns:
        List of Chunk objects
    """
    if not files:
        return []

    # Separate priority files (README, entry points)
    priority_files = []
    regular_files = []

    for f in files:
        name_lower = f.path.lower()
        if (
            "readme" in name_lower
            or f.path in ("main.py", "app.py", "index.js", "index.ts", "main.go", "main.rs")
            or name_lower.endswith("__init__.py")
        ):
            priority_files.append(f)
        else:
            regular_files.append(f)

    # Group regular files by directory
    directory_groups: dict[str, list[RepoFile]] = {}
    for f in regular_files:
        group = get_directory_group(f.path)
        if group not in directory_groups:
            directory_groups[group] = []
        directory_groups[group].append(f)

    chunks: list[Chunk] = []

    # First chunk: priority files
    if priority_files:
        priority_chunk = Chunk()
        for f in priority_files:
            if priority_chunk.total_size + len(f.content) > target_size and priority_chunk.files:
                chunks.append(priority_chunk)
                priority_chunk = Chunk()
            priority_chunk.add_file(f)
        if priority_chunk.files:
            chunks.append(priority_chunk)

    # Process directory groups
    current_chunk: Chunk | None = None

    for group_name in sorted(directory_groups.keys()):
        group_files = directory_groups[group_name]

        # Sort files within group by path for consistency
        group_files.sort(key=lambda f: f.path)

        for f in group_files:
            file_size = len(f.content)

            # If file alone exceeds target, it gets its own chunk
            if file_size > target_size:
                if current_chunk and current_chunk.files:
                    chunks.append(current_chunk)
                    current_chunk = None
                single_chunk = Chunk()
                single_chunk.add_file(f)
                chunks.append(single_chunk)
                continue

            # Start new chunk if needed
            if current_chunk is None:
                current_chunk = Chunk()

            # If adding this file would exceed target, start new chunk
            if current_chunk.total_size + file_size > target_size and current_chunk.files:
                chunks.append(current_chunk)
                current_chunk = Chunk()

            current_chunk.add_file(f)

    # Don't forget the last chunk from directory processing
    if current_chunk and current_chunk.files:
        chunks.append(current_chunk)

    return chunks


def get_chunk_summary(chunks: list[Chunk]) -> str:
    """Get a summary of the chunking result."""
    total_files = sum(len(c.files) for c in chunks)
    total_size = sum(c.total_size for c in chunks)

    lines = [
        f"Split {total_files} files into {len(chunks)} chunks",
        f"Total content size: {total_size / 1024:.1f} KB",
    ]

    for i, chunk in enumerate(chunks):
        lines.append(f"  Chunk {i + 1}: {len(chunk.files)} files, {chunk.total_size / 1024:.1f} KB")

    return "\n".join(lines)
