#!/usr/bin/env python3
"""Select a passage by URN from one or more CEX corpus files, analyze it,
and print its dependency graph as Graphviz DOT.

Usage:
    python scripts/corpus_to_dot.py genesis.cex \\
        --urn "urn:cts:compnov:bible.genesis.vulgate:1.1" --lang la | dot -Tpng -o graph.png

    python scripts/corpus_to_dot.py vulgate.cex targum.cex \\
        --urn "urn:cts:compnov:bible.genesis.targum_latin.normalized:1.1" --lang la | dot -Tsvg -o graph.svg

Reads one or more CEX files (`urn|text` lines; see udsyntax.corpora),
finds the line whose URN exactly matches --urn, runs its text through
the chosen spaCy pipeline, and writes only the DOT source to stdout --
errors and usage go to stderr -- so it's always safe to pipe straight
into `dot`.

Requires udsyntax and a spaCy pipeline for the chosen language to already
be installed (see the README for the LatinCy wheel URLs):

    pip install -e .
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from udsyntax import SyntaxGraph, load_greek, load_latin, read_cex_many, select_urn
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
        "corpus",
        nargs="+",
        type=Path,
        help="One or more CEX corpus files (urn|text lines) to search.",
    )
    parser.add_argument(
        "--urn",
        required=True,
        help="Exact URN of the passage to select, e.g. "
        "urn:cts:compnov:bible.genesis.vulgate:1.1",
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
    return parser.parse_args(argv)


def select_text(corpus_files: list[Path], urn: str) -> str:
    try:
        pairs = read_cex_many(corpus_files)
    except OSError as exc:
        raise SystemExit(f"couldn't read corpus file: {exc}")

    match_count = sum(1 for u, _ in pairs if u == urn)
    if match_count > 1:
        print(
            f"warning: {match_count} lines matched URN {urn!r}; using the first one",
            file=sys.stderr,
        )

    try:
        return select_urn(pairs, urn)
    except KeyError:
        files = ", ".join(str(p) for p in corpus_files)
        raise SystemExit(f"no line with URN {urn!r} found in {files}")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    text = select_text(args.corpus, args.urn).strip()
    if not text:
        raise SystemExit(f"the passage for URN {args.urn!r} is empty")

    load = _LOADERS[args.lang]
    nlp = load(args.model) if args.model else load()
    doc = nlp(text)

    graph = SyntaxGraph.from_doc(doc, urn=args.urn)
    print(graph.to_dot())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
