# Re-Gen v3.0

Paleontological genome reconstruction pipeline using ancestral sequence reconstruction, CRISPR design, and phylogenetic bracketing.

## Installation

```bash
# Development install
pip install -e ".[dev]"

# With optional extras
pip install -e ".[hardware,ai]"
```

## Quick Start

```bash
# v3 pipeline (AI-orchestrated)
re-gen v3 --species "Tyrannosaurus rex" --ncbi-email user@example.com

# v2 pipeline (reference search + CRISPR)
re-gen v2 --gene "cytochrome b" --host-species "Struthio camelus" --ncbi-email user@example.com
```

## Project Structure

```
src/re_gen/
  core/           # CRISPR design, genome synthesis, validation, reconstruction
  data/           # Dinosaur database, paleontology, descendant mapping
  ncbi/           # NCBI/UniProt/CrossRef reference search
  ai/             # Ollama integration, AI tool-calling framework
  hardware/       # Device abstraction with simulation fallback
  pipeline/       # v2 and v3 orchestration pipelines
  cli.py          # CLI entry point
  exceptions.py   # Exception hierarchy
```

## Development

```bash
# Lint
ruff check src/re_gen/

# Format
ruff format src/re_gen/

# Test
pytest tests/ -v --cov=re_gen

# Type check
mypy src/re_gen/ --ignore-missing-imports
```

## Hardware Support

All hardware modules support **simulation mode** when physical devices aren't available:
- RPi.GPIO / gpiozero not installed → simulation mode
- Serial ports unavailable → simulation mode
- No configuration needed

## License

MIT
# Re-Gen-Project
