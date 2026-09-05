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


@pytest.fixture
def subordinate_clause_doc() -> Doc:
    """"Cum venit Caesar vicit." (contrived, not real Latin) as a
    pre-parsed Doc: two finite verbs, "venit" (a subordinate clause,
    introduced by "Cum") governed by "vicit" (the root clause's verb) via
    an adverbial-clause relation -- enough to exercise `to_dot()`'s
    clause-coloring across more than one clause."""
    vocab = Vocab()
    words = ["Cum", "venit", "Caesar", "vicit", "."]
    heads = [1, 3, 3, 3, 3]
    deps = ["mark", "advcl", "nsubj", "ROOT", "punct"]
    pos = ["SCONJ", "VERB", "PROPN", "VERB", "PUNCT"]
    lemmas = ["cum", "venio", "Caesar", "vinco", "."]
    morphs = [
        "",
        "VerbForm=Fin",
        "Case=Nom|Gender=Masc|Number=Sing",
        "VerbForm=Fin",
        "",
    ]
    return Doc(vocab, words=words, heads=heads, deps=deps, pos=pos, lemmas=lemmas, morphs=morphs)
