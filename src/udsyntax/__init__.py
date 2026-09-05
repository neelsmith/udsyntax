"""udsyntax: extract simple syntax graphs from spaCy Universal Dependencies parses.

Typical usage::

    from udsyntax import load_latin, SyntaxGraph

    nlp = load_latin()
    doc = nlp("Gallia est omnis divisa in partes tres.")
    graph = SyntaxGraph.from_doc(doc)
    df = graph.to_polars()
"""
from .corpora import read_cex, read_cex_many
from .graph import SyntaxGraph, corpus_to_polars
from .models import SyntaxEdge, SyntaxNode, VerbalUnit
from .nlp import (
    DEFAULT_GREEK_MODEL,
    DEFAULT_LATIN_MODEL,
    load_greek,
    load_latin,
    load_pipeline,
)
from .urn import CtsUrn, parse_cts_urn

__all__ = [
    "SyntaxGraph",
    "SyntaxNode",
    "SyntaxEdge",
    "VerbalUnit",
    "corpus_to_polars",
    "read_cex",
    "read_cex_many",
    "load_latin",
    "load_greek",
    "load_pipeline",
    "DEFAULT_LATIN_MODEL",
    "DEFAULT_GREEK_MODEL",
    "CtsUrn",
    "parse_cts_urn",
]

__version__ = "0.1.0"
