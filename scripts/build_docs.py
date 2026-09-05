#!/usr/bin/env python3
"""Build static API documentation for udsyntax with pdoc.

Usage:
    python scripts/build_docs.py [output_dir]

Reads the docstrings already in src/udsyntax/*.py and renders them as a
static HTML site (default: docs/api/, gitignored -- this is a local,
on-demand build, not something committed to the repo).

Requires the `docs` extra, which also needs the package itself
importable (pdoc imports udsyntax to read its docstrings):

    pip install -e ".[docs]"
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = REPO_ROOT / "docs" 


def main(argv: list[str]) -> int:
    output_dir = Path(argv[0]).resolve() if argv else DEFAULT_OUTPUT

    try:
        import pdoc  # noqa: F401
    except ImportError:
        print(
            "pdoc is not installed. Install the docs extra first:\n"
            '    pip install -e ".[docs]"',
            file=sys.stderr,
        )
        return 1

    try:
        import udsyntax  # noqa: F401
    except ImportError:
        print(
            "udsyntax itself isn't importable -- pdoc needs to import it "
            "to read its docstrings. Install the package first:\n"
            '    pip install -e ".[docs]"',
            file=sys.stderr,
        )
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [sys.executable, "-m", "pdoc", "udsyntax", "-o", str(output_dir)],
        cwd=REPO_ROOT,
    )
    if result.returncode == 0:
        print(f"\nAPI docs written to {output_dir}/api.html")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
