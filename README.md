# udsyntax

Extract simple syntax graphs from spaCy's Universal Dependencies parses of Greek and Latin texts.

> See [release notes](https://github.com/neelsmith/udsyntax/blob/main/releases.md)

1. load citable Greek/Latin text corpora from CEX files
2. analyze them with spaCy pipelines (developed against the LatinCy `la_core_web_lg` and `grc_dep_web_lg` models)
3. flatten the resulting parse into a small, framework-independent `SyntaxNode` / `SyntaxEdge` graph model that can be exported to a polars `DataFrame` or a `networkx` graph.

## Installation

Install `uvsyntax` from GitHub:

```bash
pip install git+https://github.com/neelsmith/udsyntax.git
```

You'll also need a spaCy pipeline for whichever language you're parsing. `udsyntax` doesn't install these for you, since they're distributed as direct-URL wheels rather than through `spacy download`:

```bash
pip install "la-core-web-lg @ https://huggingface.co/latincy/la_core_web_lg/resolve/main/la_core_web_lg-3.8.0-py3-none-any.whl"
pip install "grc-dep-web-lg @ https://huggingface.co/latincy/grc_dep_web_lg/resolve/main/grc_dep_web_lg-3.8.1-py3-none-any.whl"
```

If you want to export graphs to networkx, install the optional `graph` extra:

```bash
pip install "udsyntax[graph] @ git+https://github.com/neelsmith/udsyntax.git"
```

## Quick start

```python
from udsyntax import load_latin, SyntaxGraph

nlp = load_latin()  # loads la_core_web_lg, cached after the first call
doc = nlp("Gallia est omnis divisa in partes tres.")

graph = SyntaxGraph.from_doc(doc)
df = graph.to_polars()   # one row per token
g = graph.to_networkx()  # requires the `graph` extra
```

