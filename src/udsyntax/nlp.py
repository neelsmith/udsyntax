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
import shlex
import sys
from pathlib import Path

try:
    import spacy
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "udsyntax requires spaCy. Install it with `pip install spacy` "
        "(and a Greek/Latin pipeline such as la_core_web_lg / grc_dep_web_lg)."
    ) from exc

DEFAULT_LATIN_MODEL = "la_core_web_lg"
DEFAULT_GREEK_MODEL = "grc_dep_web_lg"

#: pip requirement specs for the pipelines udsyntax knows how to describe,
#: used to build a copy-pasteable install command when one is missing.
MODEL_INSTALL_SPECS: dict[str, str] = {
    DEFAULT_LATIN_MODEL: "la-core-web-lg @ https://huggingface.co/latincy/la_core_web_lg/resolve/main/la_core_web_lg-3.9.6-py3-none-any.whl",
    DEFAULT_GREEK_MODEL: "grc-dep-web-lg @ https://huggingface.co/latincy/grc_dep_web_lg/resolve/main/grc_dep_web_lg-3.8.1-py3-none-any.whl",
}


class ModelNotInstalledError(OSError):
    """Raised when a spaCy pipeline name is neither an installed package
    nor a path to a pipeline directory.

    Subclasses :class:`OSError` (what ``spacy.load`` itself raises) so
    existing ``except OSError`` handlers keep working; the message adds
    the pip command needed to install the missing pipeline into the
    Python interpreter that's actually running.
    """

    def __init__(self, model_name: str):
        self.model_name = model_name
        super().__init__(install_hint(model_name))


def install_hint(model_name: str) -> str:
    """Explain how to install ``model_name`` into the running interpreter."""
    python = shlex.quote(sys.executable or "python")
    lines = [f"The spaCy pipeline {model_name!r} isn't installed for {sys.executable}."]
    spec = MODEL_INSTALL_SPECS.get(model_name)
    if spec:
        lines += [
            "Install it with:",
            "",
            f"    {python} -m pip install {shlex.quote(spec)}",
        ]
    else:
        lines.append(
            "Install it as a Python package in this environment, or pass a path "
            "to a pipeline directory instead of a package name."
        )
    lines += [
        "",
        "(If you've already installed it, check that you're running the same "
        "Python/virtualenv you installed it into.)",
    ]
    return "\n".join(lines)


def _is_available(model_name: str) -> bool:
    return spacy.util.is_package(model_name) or Path(model_name).exists()


@functools.lru_cache(maxsize=None)
def load_pipeline(model_name: str):
    """Load (and cache) a spaCy pipeline by name or path.

    Raises:
        ModelNotInstalledError: if ``model_name`` is neither an installed
            pipeline package nor an existing path. The message includes
            the ``pip install`` command for the default LatinCy pipelines.
    """
    if not _is_available(model_name):
        raise ModelNotInstalledError(model_name)
    return spacy.load(model_name)


def load_latin(model_name: str = DEFAULT_LATIN_MODEL):
    """Load (and cache) a Latin dependency-parsing pipeline."""
    return load_pipeline(model_name)


def load_greek(model_name: str = DEFAULT_GREEK_MODEL):
    """Load (and cache) an Ancient Greek dependency-parsing pipeline."""
    return load_pipeline(model_name)
