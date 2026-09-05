"""Shared test fixtures.

Building a real spaCy pipeline needs a downloaded model (the LatinCy /
grc_dep_web_lg wheels udsyntax targets aren't installed in CI or in
`pip install -e ".[dev]"`). Instead, these fixtures construct a
:class:`spacy.tokens.Doc` directly with the annotations a parser would
have produced, which is enough to exercise `SyntaxGraph.from_doc`.
"""
from __future__ import annotations

import pytest
from spacy.tokens import Doc
from spacy.vocab import Vocab


@pytest.fixture
def latin_doc() -> Doc:
    """"Gallia est omnis divisa." as a pre-parsed Doc (fake dependency parse)."""
    vocab = Vocab()
    words = ["Gallia", "est", "omnis", "divisa", "."]
    heads = [3, 3, 3, 3, 3]
    deps = ["nsubj", "cop", "advmod", "ROOT", "punct"]
    pos = ["PROPN", "AUX", "ADJ", "VERB", "PUNCT"]
    lemmas = ["Gallia", "sum", "omnis", "divido", "."]
    morphs = [
        "Case=Nom|Gender=Fem|Number=Sing",
        "",
        "Case=Nom|Degree=Pos",
        "VerbForm=Fin|Voice=Pass",
        "",
    ]
    return Doc(vocab, words=words, heads=heads, deps=deps, pos=pos, lemmas=lemmas, morphs=morphs)
