# `scripts/text_to_dot.py`

A command-line entry point that analyzes a string of Greek or Latin text and prints its dependency graph as Graphviz DOT, suitable for piping straight into `dot`.

## Usage

```bash
python scripts/text_to_dot.py "Gallia est omnis divisa in partes tres." --lang la | dot -Tpng -o graph.png
echo "Ἐν ἀρχῇ ἦν ὁ λόγος." | python scripts/text_to_dot.py --lang grc | dot -Tsvg -o graph.svg
```

- `text` (positional, optional): the string to analyze. If omitted (or passed as `-`), the script reads from stdin, so it works at either end of a pipeline.
- `--lang` / `-l` (required): `la` for Latin (`la_core_web_lg`) or `grc` for Ancient Greek (`grc_dep_web_lg`).
- `--model` / `-m`: override the default pipeline name for `--lang`, e.g. to point at a different LatinCy model.
- `--urn`: a CTS URN to use as the DOT graph's name (`digraph "urn:..." { ... }`).
- `--color` / `--no-color`: color nodes by clause (default) or draw plain, unfilled boxes. Passed straight through to `SyntaxGraph.to_dot(color_by_clause=...)`.

Only the DOT source is written to stdout; errors and usage text go to stderr, so the output is always safe to pipe directly into `dot` (`-Tsvg`, `-Tpng`, etc. all work).

## Requirements

Needs `udsyntax` and the spaCy pipeline for whichever `--lang` you pass already installed:

```bash
pip install -e .
pip install "la-core-web-lg @ https://huggingface.co/latincy/la_core_web_lg/resolve/main/la_core_web_lg-3.9.6-py3-none-any.whl"
```

## Testing notes

The script is a thin CLI wrapper around `udsyntax.load_latin` / `load_greek` / `SyntaxGraph.from_doc` / `SyntaxGraph.to_dot`, all of which have unit tests in `tests/`. The wrapper itself doesn't have automated tests (it isn't part of the installed package, and exercising it for real would mean downloading a multi-hundred-MB language model in CI). It was manually verified by:

- `--help`, a missing `--lang`, and empty stdin, each producing the expected message/exit code,
- a full run with `_LOADERS["la"]` monkeypatched to a fake pipeline (avoids the model download) confirming argument parsing, `SyntaxGraph` construction, and DOT output all wire together, and
- piping that DOT output into `dot -Tsvg` and confirming Graphviz accepted it and produced a valid SVG.

## Missing-pipeline errors

If the pipeline for `--lang` isn't installed in the interpreter running the script, `udsyntax.load_pipeline` now raises `ModelNotInstalledError` (an `OSError` subclass) instead of spaCy's bare `E050`. The scripts catch it and print, to stderr, the exact `<this python> -m pip install '<wheel spec>'` command for the default LatinCy models, then exit 1. Using `sys.executable` in the hint matters: the usual cause is installing the model into a different Python than the one running the script. The same handling is in `scripts/corpus_to_dot.py`; unit tests are in `tests/test_nlp.py`.
