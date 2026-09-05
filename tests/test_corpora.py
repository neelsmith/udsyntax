from pathlib import Path

import pytest

from udsyntax import read_cex, read_cex_many, select_urn

FIXTURE = Path(__file__).parent / "data" / "sample.cex"


def test_read_cex_all_lines():
    pairs = read_cex(FIXTURE)
    assert len(pairs) == 3
    assert pairs[0] == (
        "urn:cts:compnov:bible.genesis.vulgate:1.1",
        "In principio creavit Deus caelum et terram.",
    )


def test_read_cex_filters_by_urn_substring():
    pairs = read_cex(FIXTURE, urn_filter="vulgate")
    assert len(pairs) == 2
    assert all("vulgate" in urn for urn, _ in pairs)


def test_read_cex_many_concatenates_in_order():
    pairs = read_cex_many([FIXTURE, FIXTURE])
    assert len(pairs) == 6


def test_select_urn_finds_exact_match():
    pairs = read_cex(FIXTURE)
    text = select_urn(pairs, "urn:cts:compnov:bible.genesis.vulgate:1.2")
    assert text == "Terra autem erat inanis et vacua."


def test_select_urn_does_not_match_by_substring():
    pairs = read_cex(FIXTURE)
    with pytest.raises(KeyError):
        select_urn(pairs, "urn:cts:compnov:bible.genesis.vulgate:1")


def test_select_urn_raises_when_missing():
    pairs = read_cex(FIXTURE)
    with pytest.raises(KeyError):
        select_urn(pairs, "urn:cts:compnov:bible.genesis.vulgate:99.99")


def test_select_urn_first_match_wins_on_duplicates():
    pairs = [("urn:x", "first"), ("urn:x", "second")]
    assert select_urn(pairs, "urn:x") == "first"
