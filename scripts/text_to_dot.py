#!/usr/bin/env python3
"""Analyze a string of Greek or Latin text and print its dependency graph as Graphviz DOT.

Usage:
    python scripts/text_to_dot.py "Gallia est omnis divisa in partes tres." --lang la | dot -Tpng -o graph.png
    echo "Ἐν ἀρχῇ ἦν ὁ λόγος." | python scripts/text_to_dot.py --lang grc | dot -Tsvg -o graph.svg

TEXT is read from the first positional argument, or from stdin if it's
omitted (or given as "-"), so the script fits either end of a pipeline.
Only the DOT source goes to stdout -- everything else (errors, usage)
goes to stderr -- so it's always safe to pipe straight into `dot`.

Requires udsyntax and a spaCy pipeline for the chosen language to already
be installed (see the README for the LatinCy wheel URLs):

    pip install -e .
"""
from __future__ import annotations

import argparse
import sys

try:
    from udsyntax import SyntaxGraph, load_greek, load_latin
except ImportError:
    print(
        "udsyntax isn't importable. Install the package first:\n"
        "    pip install -e .",
        file=sys.stderr,
    )
    raise SystemExit(1)

_LOADERS = {"la": load_latin, "grc": load_greek}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "text",
        nargs="?",
        help='Text to analyze. Reads stdin if omitted or given as "-".',
    )
    parser.add_argument(
        "--lang",
        "-l",
        choices=sorted(_LOADERS),
        required=True,
        help="Language pipeline to use: la (Latin) or grc (Ancient Greek).",
    )
    parser.add_argument(
        "--model",
        "-m",
        help="Override the default spaCy pipeline name for --lang "
        "(defaults to la_core_web_lg / grc_dep_web_lg).",
    )
    parser.add_argument(
        "--urn",
        help="CTS URN to label the digraph with (used as the DOT graph name).",
    )
    return parser.parse_args(argv)


def read_text(arg: str | None) -> str:
    raw = sys.stdin.read() if arg is None or arg == "-" else arg
    text = raw.strip()
    if not text:
        raise SystemExit("no text given: pass it as an argument or pipe it in on stdin")
    return text


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    text = read_text(args.text)

    load = _LOADERS[args.lang]
    nlp = load(args.model) if args.model else load()
    doc = nlp(text)

    graph = SyntaxGraph.from_doc(doc, urn=args.urn)
    print(graph.to_dot())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
