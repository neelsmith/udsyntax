#!/usr/bin/env python3
"""Build static API documentation for udsyntax with pdoc.

Usage:
    python scripts/build_docs.py [output_dir]

Reads the docstrings already in src/udsyntax/*.py and renders them with
pdoc into docs/ (or output_dir), alongside the quarto-built site.

pdoc always writes its own index.html (a redirect to udsyntax.html). That
would clobber the quarto home page, so pdoc renders into a temporary
directory and everything *except* the top-level index.html is copied
into the output directory. An existing index.html there is never
touched.

Requires the `docs` extra, which also needs the package itself
importable (pdoc imports udsyntax to read its docstrings):

    pip install -e ".[docs]"
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = REPO_ROOT / "docs"

# Files pdoc writes that must not overwrite anything in the output directory.
SKIP = {"index.html"}


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
    with tempfile.TemporaryDirectory(prefix="udsyntax-pdoc-") as tmp:
        result = subprocess.run(
            [sys.executable, "-m", "pdoc", "udsyntax", "-o", tmp],
            cwd=REPO_ROOT,
        )
        if result.returncode != 0:
            return result.returncode

        copied = []
        for item in sorted(Path(tmp).iterdir()):
            if item.name in SKIP:
                continue
            dest = output_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)
            copied.append(item.name)

    print(f"\nAPI docs written to {output_dir}: {', '.join(copied)}")
    print(f"(left {', '.join(sorted(SKIP))} untouched for quarto)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
