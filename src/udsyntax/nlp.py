"""Convenience wrappers for loading the spaCy pipelines used for Greek and Latin.

The pretrained pipelines this project has been tested against are the
LatinCy models ``la_core_web_lg`` and ``grc_dep_web_lg``
(https://huggingface.co/latincy). They're distributed as directly
installable wheels rather than through ``spacy download``, so udsyntax
does not install them for you -- add them as dependencies in your own
project (see the README) -- but it does cache whichever pipeline names
you load, so repeated calls are cheap.
"""
from __future__ import annotations

import functools

try:
    import spacy
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "udsyntax requires spaCy. Install it with `pip install spacy` "
        "(and a Greek/Latin pipeline such as la_core_web_lg / grc_dep_web_lg)."
    ) from exc

DEFAULT_LATIN_MODEL = "la_core_web_lg"
DEFAULT_GREEK_MODEL = "grc_dep_web_lg"


@functools.lru_cache(maxsize=None)
def load_pipeline(model_name: str):
    """Load (and cache) a spaCy pipeline by name."""
    return spacy.load(model_name)


def load_latin(model_name: str = DEFAULT_LATIN_MODEL):
    """Load (and cache) a Latin dependency-parsing pipeline."""
    return load_pipeline(model_name)


def load_greek(model_name: str = DEFAULT_GREEK_MODEL):
    """Load (and cache) an Ancient Greek dependency-parsing pipeline."""
    return load_pipeline(model_name)
