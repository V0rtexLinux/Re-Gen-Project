"""CLI entry point for re-gen package."""

from __future__ import annotations

import sys


def main() -> int:
    """Dispatch to the appropriate pipeline version or GUI."""
    args = sys.argv[1:]

    if "--version" in args or "-V" in args:
        from re_gen import __version__

        print(f"re-gen {__version__}")
        return 0

    if "--help" in args or "-h" in args:
        print("re-gen - Paleontological genome reconstruction pipeline")
        print()
        print("Usage:")
        print("  re-gen --gui       Launch graphical interface")
        print("  re-gen v2 ...      Run v2 pipeline (reference search + CRISPR)")
        print("  re-gen v3 ...      Run v3 pipeline (AI-orchestrated synthesis)")
        print()
        print("Options:")
        print("  --gui              Launch PyQt5 GUI application")
        print("  --version, -V      Show version")
        print("  --help, -h         Show this help")
        return 0

    # GUI mode
    if "--gui" in args:
        args.remove("--gui")
        sys.argv = [sys.argv[0]] + args
        from re_gen.gui.app import run_gui

        return run_gui()

    # Default: v3 is the main pipeline
    if "v2" in args:
        args.remove("v2")
        sys.argv = [sys.argv[0]] + args
        from re_gen.pipeline.main import main as v2_main

        return v2_main()

    sys.argv = [sys.argv[0]] + args
    from re_gen.pipeline.main_v3 import main as v3_main

    return v3_main()
