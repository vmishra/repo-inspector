# repo-inspector

**Understand any codebase in minutes.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

A CLI tool that uses AI to analyze codebases and explain what they do, how they're structured, and how data flows through them.

---

## Quick Start

**1. Install**

```bash
pip install repo-inspector
```

**2. Set your Gemini API key**

Get a free API key at [Google AI Studio](https://aistudio.google.com/app/apikey), then:

```bash
export GEMINI_API_KEY=your-api-key-here
```

**3. Analyze any repo**

```bash
repo-inspector /path/to/any/repo
```

That's it. You'll get a complete breakdown of what the code does.

---

## What You Get

When you run `repo-inspector`, it analyzes the codebase and outputs:

| Section | Description |
|---------|-------------|
| **Purpose** | What the repository does and who it's for |
| **Tech Stack** | Languages, frameworks, and key dependencies |
| **Architecture** | How the code is organized and why |
| **Key Folders** | What each directory is responsible for |
| **Entry Points** | Where execution starts |
| **Data Flow** | How data moves through the system |
| **Diagram** | Visual architecture diagram (optional) |

---

## Options

```
repo-inspector <path> [OPTIONS]

Options:
  --level, -l     beginner (default) or senior
  --diagram, -d   Include a Mermaid architecture diagram
  --format, -f    text (default) or markdown
  --api-key       API key (alternative to env var)
  --version, -v   Show version
```

---

## Examples

### Basic analysis

```bash
repo-inspector .
```

### Senior-level technical deep dive

```bash
repo-inspector . --level senior
```

### Generate architecture diagram

```bash
repo-inspector . --diagram
```

### Export as Markdown documentation

```bash
repo-inspector . --format markdown > ARCHITECTURE.md
```

### All options combined

```bash
repo-inspector . --level senior --diagram --format markdown
```

---

## Explanation Levels

### Beginner (default)

Perfect for:
- Onboarding new team members
- Understanding unfamiliar codebases
- Learning how projects are structured

The output explains concepts clearly, avoids jargon, and focuses on the "what" and "why".

### Senior

Perfect for:
- Architectural reviews
- Technical due diligence
- Experienced engineers who want the details

The output is concise and technical, covering patterns, trade-offs, and potential risks.

---

## Supported Languages

| Category | Extensions |
|----------|------------|
| **Web** | `.js` `.ts` `.jsx` `.tsx` |
| **Backend** | `.py` `.go` `.java` `.rb` `.php` |
| **Systems** | `.rs` `.c` `.cpp` `.h` `.hpp` |
| **Mobile** | `.swift` `.kt` |
| **Other** | `.cs` `.scala` `.sh` `.bash` |
| **Config** | `.yaml` `.yml` `.json` `.toml` |
| **Docs** | `.md` |

---

## How It Works

1. **Scans** the repository for source files (skips `node_modules`, `.git`, build artifacts, etc.)
2. **Chunks** the code intelligently to fit within context limits
3. **Analyzes** each chunk using Gemini AI
4. **Synthesizes** all analyses into a coherent summary
5. **Outputs** in your preferred format

---

## Installation

### From PyPI

```bash
pip install repo-inspector
```

### From source

```bash
git clone https://github.com/yourusername/repo-inspector.git
cd repo-inspector
pip install -e .
```

### Requirements

- Python 3.10 or higher
- Gemini API key (free tier available)

---

## Configuration

### API Key Setup

**Option 1: Environment variable (recommended)**

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export GEMINI_API_KEY=your-api-key-here
```

**Option 2: Pass directly**

```bash
repo-inspector . --api-key your-api-key-here
```

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key and set it as shown above

The free tier is generous and sufficient for most use cases.

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## License

MIT
