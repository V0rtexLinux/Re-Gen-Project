"""CLI entry point for the re-gen package."""

from __future__ import annotations

import sys


def main() -> int:
    """Dispatch to the unified pipeline or the GUI."""
    args = sys.argv[1:]

    if "--version" in args or "-V" in args:
        from re_gen import __version__

        print(f"re-gen {__version__}")
        return 0

    if "--help" in args or "-h" in args:
        print("re-gen - Paleontological genome reconstruction pipeline")
        print()
        print("Usage:")
        print("  re-gen --gui        Launch graphical interface")
        print("  re-gen [options]    Run the unified 8-phase pipeline")
        print()
        print("Global options:")
        print("  --gui              Launch PyQt5 GUI application")
        print("  --version, -V      Show version")
        print("  --help, -h         Show this help")
        print()
        print("Pipeline options (forwarded to the unified pipeline):")
        print("  --email EMAIL      Required. Email used for the NCBI Entrez API")
        print("  --dinosaur NAME    Scientific name (e.g. 'Tyrannosaurus rex')")
        print("  --fossil FILE      FASTA file with a real fossil fragment")
        print("  --hardware         Enable physical hardware (Raspberry Pi GPIO)")
        print("  --lista            List available species and exit")
        print("  --arquitetura      Show the pipeline architecture map and exit")
        print("  Run 're-gen --pipeline-help' for the full list of options.")
        return 0

    # GUI mode
    if "--gui" in args:
        args.remove("--gui")
        sys.argv = [sys.argv[0]] + args
        from re_gen.gui.app import run_gui

        return run_gui()

    if "--pipeline-help" in args:
        args = [a for a in args if a != "--pipeline-help"] + ["--help"]

    sys.argv = [sys.argv[0]] + args
    from re_gen.pipeline.unified import main as pipeline_main

    return pipeline_main()
