import pytest

from udsyntax import parse_cts_urn


def test_parse_full_urn():
    urn = "urn:cts:compnov:bible.genesis.vulgate:1.1"
    parsed = parse_cts_urn(urn)
    assert parsed.namespace == "compnov"
    assert parsed.group == "bible"
    assert parsed.work == "genesis"
    assert parsed.version == "vulgate"
    assert parsed.passage == "1.1"
    assert str(parsed) == urn


def test_parse_urn_missing_passage():
    parsed = parse_cts_urn("urn:cts:compnov:bible.genesis.vulgate")
    assert parsed.passage is None
    assert parsed.version == "vulgate"


def test_rejects_non_cts_urn():
    with pytest.raises(ValueError):
        parse_cts_urn("not a urn")
