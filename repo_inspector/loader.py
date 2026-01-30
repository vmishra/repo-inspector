"""File discovery and filtering for repository analysis."""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RepoFile:
    """Represents a file in the repository."""

    path: str
    content: str
    extension: str


ALLOWED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".go",
    ".java",
    ".yaml",
    ".yml",
    ".json",
    ".md",
    ".rs",
    ".rb",
    ".php",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".swift",
    ".kt",
    ".scala",
    ".sh",
    ".bash",
    ".toml",
    ".cfg",
    ".ini",
}

IGNORED_DIRECTORIES = {
    "node_modules",
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".venv",
    "venv",
    "env",
    ".env",
    ".tox",
    ".nox",
    "target",
    "vendor",
    ".idea",
    ".vscode",
    "coverage",
    ".coverage",
    "htmlcov",
    ".next",
    ".nuxt",
    "out",
    ".turbo",
}

IGNORED_FILES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "Pipfile.lock",
    "Cargo.lock",
    "Gemfile.lock",
    "composer.lock",
    "go.sum",
}

MAX_FILE_SIZE = 50 * 1024  # 50KB


def is_minified(filename: str) -> bool:
    """Check if a file appears to be minified."""
    return ".min." in filename or filename.endswith(".min.js") or filename.endswith(".min.css")


def is_generated(filename: str) -> bool:
    """Check if a file appears to be generated."""
    generated_patterns = [
        ".generated.",
        ".g.dart",
        ".pb.go",
        "_pb2.py",
        ".d.ts",
    ]
    return any(pattern in filename for pattern in generated_patterns)


def should_ignore_file(filepath: Path) -> bool:
    """Determine if a file should be ignored."""
    filename = filepath.name

    if filename in IGNORED_FILES:
        return True

    if is_minified(filename):
        return True

    if is_generated(filename):
        return True

    if filename.startswith("."):
        return True

    return False


def should_ignore_directory(dirname: str) -> bool:
    """Determine if a directory should be ignored."""
    return dirname in IGNORED_DIRECTORIES or dirname.startswith(".")


def load_repository(repo_path: str | Path) -> list[RepoFile]:
    """
    Load all relevant files from a repository.

    Args:
        repo_path: Path to the repository root

    Returns:
        List of RepoFile objects containing file information
    """
    repo_path = Path(repo_path).resolve()

    if not repo_path.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    if not repo_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {repo_path}")

    files: list[RepoFile] = []

    for root, dirs, filenames in os.walk(repo_path):
        # Filter out ignored directories in-place to prevent descending into them
        dirs[:] = [d for d in dirs if not should_ignore_directory(d)]

        for filename in filenames:
            filepath = Path(root) / filename

            # Check extension
            ext = filepath.suffix.lower()
            if ext not in ALLOWED_EXTENSIONS:
                continue

            # Check if file should be ignored
            if should_ignore_file(filepath):
                continue

            # Check file size
            try:
                file_size = filepath.stat().st_size
                if file_size > MAX_FILE_SIZE:
                    continue
                if file_size == 0:
                    continue
            except OSError:
                continue

            # Read file content
            try:
                content = filepath.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                # Skip files that can't be read as text
                continue

            # Get relative path from repo root
            relative_path = str(filepath.relative_to(repo_path))

            files.append(
                RepoFile(
                    path=relative_path,
                    content=content,
                    extension=ext,
                )
            )

    # Sort files to ensure deterministic ordering
    # Prioritize README and common entry points
    def sort_key(f: RepoFile) -> tuple[int, str]:
        name_lower = f.path.lower()
        if "readme" in name_lower:
            return (0, f.path)
        if f.path in ("main.py", "app.py", "index.js", "index.ts", "main.go", "main.rs"):
            return (1, f.path)
        if "main" in name_lower or "index" in name_lower or "app" in name_lower:
            return (2, f.path)
        return (3, f.path)

    files.sort(key=sort_key)

    return files


def get_file_stats(files: list[RepoFile]) -> dict:
    """Get statistics about loaded files."""
    extensions: dict[str, int] = {}
    total_size = 0
    total_lines = 0

    for f in files:
        ext = f.extension
        extensions[ext] = extensions.get(ext, 0) + 1
        total_size += len(f.content)
        total_lines += f.content.count("\n") + 1

    return {
        "file_count": len(files),
        "total_size_bytes": total_size,
        "total_lines": total_lines,
        "extensions": extensions,
    }
