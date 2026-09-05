from pathlib import Path

from udsyntax import read_cex, read_cex_many

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
