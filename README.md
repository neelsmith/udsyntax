# udsyntax

Extract simple syntax graphs from spaCy's Universal Dependencies parses of Greek and Latin texts.

`udsyntax` packages up three things that used to live together in a scratch notebook (`scratch/ud2syntax.py`):

1. loading citable Greek/Latin text corpora from CEX files,
2. running them through spaCy dependency-parsing pipelines (developed against the LatinCy `la_core_web_lg` and `grc_dep_web_lg` models), and
3. flattening the resulting parse into a small, framework-independent `SyntaxNode` / `SyntaxEdge` graph model that can be exported to a polars `DataFrame` or a networkx graph.

## Installation

This package isn't published on PyPI. Install it straight from GitHub:

```bash
pip install git+https://github.com/neelsmith/udsyntax.git
```

You'll also need a spaCy pipeline for whichever language you're parsing. udsyntax doesn't install these for you, since they're distributed as direct-URL wheels rather than through `spacy download`:

```bash
pip install "la-core-web-lg @ https://huggingface.co/latincy/la_core_web_lg/resolve/main/la_core_web_lg-3.8.0-py3-none-any.whl"
pip install "grc-dep-web-lg @ https://huggingface.co/latincy/grc_dep_web_lg/resolve/main/grc_dep_web_lg-3.8.1-py3-none-any.whl"
```

If you want to export graphs to networkx, install the optional extra:

```bash
pip install "udsyntax[graph] @ git+https://github.com/neelsmith/udsyntax.git"
```

## Usage

```python
from udsyntax import load_latin, SyntaxGraph

nlp = load_latin()  # loads la_core_web_lg, cached after the first call
doc = nlp("Gallia est omnis divisa in partes tres.")

graph = SyntaxGraph.from_doc(doc)
for edge in graph.edges:
    print(edge)

df = graph.to_polars()   # one row per token
g = graph.to_networkx()  # requires the `graph` extra
```

### Loading a CEX corpus

CEX files are `urn|text` lines, one per citable passage. `read_cex` can filter by a substring of the URN, which is how the original notebook separated the Vulgate, Targum, and Septuagint out of a single file:

```python
from udsyntax import read_cex

lines = read_cex("genesis.cex", urn_filter="vulgate")
urns = [urn for urn, _ in lines]
texts = [text for _, text in lines]
```

### Building a corpus-wide DataFrame

```python
from udsyntax import load_latin, SyntaxGraph, corpus_to_polars

nlp = load_latin()
graphs = [SyntaxGraph.from_doc(nlp(text), urn=urn) for urn, text in lines]
corpus_df = corpus_to_polars(graphs)
```

When a graph's `urn` is a parseable CTS URN (`urn:cts:namespace:group.work.version:passage`), `corpus_to_polars` adds `group` / `work` / `version` / `passage` columns automatically.

## Development

```bash
git clone https://github.com/neelsmith/udsyntax.git
cd udsyntax
pip install -e ".[dev]"
pytest
```

The original exploratory notebook lives in `scratch/ud2syntax.py` (gitignored; open it with `marimo edit scratch/ud2syntax.py`).

### API docs

`scripts/build_docs.py` renders the docstrings in `src/udsyntax/` as a static HTML site with [pdoc](https://pdoc.dev/):

```bash
pip install -e ".[docs]"
python scripts/build_docs.py        # writes docs/api/index.html
open docs/api/index.html            # or just open it in a browser
```

`docs/api/` is a local, gitignored build -- nothing is published or committed automatically. Pass a different output directory as an argument if you'd rather build elsewhere: `python scripts/build_docs.py somewhere/else`.
