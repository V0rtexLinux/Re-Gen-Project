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
# Automatic species selection
re-gen --email user@example.com

# Specific dinosaur, full 9-stage pipeline (selection -> phylogenetic
# mapping -> fossil extraction -> genome reconstruction -> CRISPR package ->
# DNA synthesis -> embryo injection -> incubation -> AI report)
re-gen --email user@example.com --dinosaur "Tyrannosaurus rex"

# With a real fossil fragment (FASTA) and physical hardware enabled
re-gen \
    --email user@example.com \
    --dinosaur "Velociraptor mongoliensis" \
    --fossil my_fossil.fasta \
    --hardware \
    --arduino-port /dev/ttyUSB0

# Run only the reconstruction phases (0-3), skip CRISPR/hardware/report
re-gen --email user@example.com --dinosaur "Triceratops horridus" --fase-fim 3

# List all catalogued species / show the pipeline architecture map
re-gen --lista
re-gen --arquitetura

# Launch the GUI
re-gen --gui
```

## Project Structure

```
src/re_gen/
  core/           # CRISPR design, genome synthesis, validation, reconstruction
  data/           # Dinosaur database (60 species), paleontology, descendant mapping
  ncbi/           # NCBI Entrez deep reference search
  ai/             # Ollama integration, AI tool-calling framework
  hardware/       # Device abstraction with simulation fallback
  monitoring/     # PubMed/tech-watch monitoring
  gui/            # PyQt5 desktop GUI
  pipeline/       # Unified 9-stage reconstruction/revival pipeline
  cli.py          # CLI entry point
  exceptions.py   # Exception hierarchy

docs/             # UTERO_OVO.md hardware documentation
tests/            # Unit test suite (pytest)
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
