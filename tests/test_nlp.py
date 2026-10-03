"""Tests for udsyntax.nlp's handling of missing spaCy pipelines.

No real model is loaded here: these only check that a pipeline name
that isn't installed produces a helpful ModelNotInstalledError instead
of spaCy's bare E050 OSError.
"""
from __future__ import annotations

import sys

import pytest

from udsyntax import nlp
from udsyntax.nlp import (
    DEFAULT_LATIN_MODEL,
    MODEL_INSTALL_SPECS,
    ModelNotInstalledError,
    install_hint,
    load_latin,
    load_pipeline,
)


@pytest.fixture(autouse=True)
def _clear_cache():
    load_pipeline.cache_clear()
    yield
    load_pipeline.cache_clear()


def test_missing_default_model_raises_with_install_command(monkeypatch):
    monkeypatch.setattr(nlp, "_is_available", lambda name: False)
    with pytest.raises(ModelNotInstalledError) as excinfo:
        load_latin()
    message = str(excinfo.value)
    assert DEFAULT_LATIN_MODEL in message
    assert MODEL_INSTALL_SPECS[DEFAULT_LATIN_MODEL] in message
    assert "-m pip install" in message
    assert excinfo.value.model_name == DEFAULT_LATIN_MODEL


def test_model_not_installed_is_an_oserror(monkeypatch):
    monkeypatch.setattr(nlp, "_is_available", lambda name: False)
    with pytest.raises(OSError):
        load_pipeline("no_such_pipeline_xyz")


def test_unknown_model_hint_has_no_pip_command():
    hint = install_hint("no_such_pipeline_xyz")
    assert "no_such_pipeline_xyz" in hint
    assert "pip install" not in hint


def test_hint_names_running_interpreter():
    assert sys.executable in install_hint(DEFAULT_LATIN_MODEL)


def test_really_missing_pipeline_is_detected():
    # No mocking: a nonsense name is neither a package nor a path.
    with pytest.raises(ModelNotInstalledError):
        load_pipeline("no_such_pipeline_xyz")
