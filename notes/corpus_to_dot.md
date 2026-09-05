# `scripts/corpus_to_dot.py`

A command-line entry point that selects a single citable passage by URN from one or more CEX corpus files, analyzes it, and prints its dependency graph as Graphviz DOT -- the corpus-driven counterpart to `scripts/text_to_dot.py` (see `notes/text_to_dot.md`), which takes the text directly instead of looking it up.

## Usage

```bash
python scripts/corpus_to_dot.py genesis.cex \
    --urn "urn:cts:compnov:bible.genesis.vulgate:1.1" --lang la | dot -Tpng -o graph.png

python scripts/corpus_to_dot.py vulgate.cex targum.cex \
    --urn "urn:cts:compnov:bible.genesis.targum_latin.normalized:1.1" --lang la | dot -Tsvg -o graph.svg
```

- `corpus` (positional, one or more): CEX files (`urn|text` lines) to search, read and concatenated in the order given via `udsyntax.read_cex_many`.
- `--urn` (required): the exact URN of the passage to select (via the new `udsyntax.select_urn`, an exact match, not the substring `urn_filter` that `read_cex`/`read_cex_many` accept). If more than one line across the given files shares this URN, a warning goes to stderr and the first one is used. If none matches, the script exits with an error naming the URN and the files searched.
- `--lang` / `-l` (required): `la` for Latin (`la_core_web_lg`) or `grc` for Ancient Greek (`grc_dep_web_lg`).
- `--model` / `-m`: override the default pipeline name for `--lang`.

The digraph is automatically named after `--urn` (via `SyntaxGraph.to_dot`'s existing "name after `self.urn`" behavior). Only the DOT source goes to stdout; everything else (the duplicate-match warning, errors, usage) goes to stderr, so the output is always safe to pipe directly into `dot`.

## Requirements

Same as `text_to_dot.py`: `udsyntax` and the spaCy pipeline for whichever `--lang` you pass, already installed (`pip install -e .` plus the LatinCy wheel; see the README).

## Library addition

Added `udsyntax.corpora.select_urn(pairs, urn)` (exported from the package root) alongside `read_cex`/`read_cex_many`: given a list of `(urn, text)` pairs, it returns the text for an exact URN match, raising `KeyError` if none matches. Covered by four new tests in `tests/test_corpora.py` (exact match, no accidental substring match, missing URN, first-match-wins on duplicates).

## Testing notes

Full suite is 27/27 (23 previous + 4 for `select_urn`). The script itself, like `text_to_dot.py`, has no automated tests of its own -- it's a thin wrapper. It was manually verified: `--help`, a missing `--urn`, a URN not found in the corpus, and a missing corpus file (this last one used to leak a raw `FileNotFoundError` traceback -- `select_text` now catches `OSError` from `read_cex_many` and reports it cleanly instead) all produce the expected message and a non-zero exit; a full run against `tests/data/sample.cex` with `_LOADERS["la"]` monkeypatched confirmed the right passage (by URN, not file order) reached the fake pipeline and the resulting DOT piped cleanly into `dot -Tsvg`; and passing the same file twice confirmed the duplicate-match warning fires on stderr without touching stdout.
