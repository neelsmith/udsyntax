"""Loading text corpora from CEX (CITE Exchange) files.

A CEX citable-text-collection is a sequence of ``urn|text`` lines. This
module generalizes the ad hoc, file-specific loaders in the original
notebook prototype (``scratch/ud2syntax.py``) into reusable readers that
work with any corpus in that format.
"""
from __future__ import annotations

from pathlib import Path


def read_cex(
    path,
    *,
    urn_filter: str | None = None,
    encoding: str = "utf-8",
) -> list[tuple[str, str]]:
    """Read a CEX file of ``urn|text`` lines.

    Parameters
    ----------
    path:
        Path to a ``.cex`` file.
    urn_filter:
        If given, keep only lines whose URN contains this substring
        (e.g. ``"vulgate"``, ``"septuagint"``, ``"targum_latin"``).
    encoding:
        Text encoding to use when reading the file.

    Returns
    -------
    A list of ``(urn, text)`` tuples, in file order. Blank lines are
    skipped.
    """
    path = Path(path)
    pairs: list[tuple[str, str]] = []
    with path.open("r", encoding=encoding) as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            urn, _, text = line.partition("|")
            if urn_filter is not None and urn_filter not in urn:
                continue
            pairs.append((urn, text))
    return pairs


def read_cex_many(
    paths,
    *,
    urn_filter: str | None = None,
    encoding: str = "utf-8",
) -> list[tuple[str, str]]:
    """Read and concatenate several CEX files, in the order given."""
    pairs: list[tuple[str, str]] = []
    for path in paths:
        pairs.extend(read_cex(path, urn_filter=urn_filter, encoding=encoding))
    return pairs


def select_urn(pairs, urn: str) -> str:
    """Return the text paired with an exact URN match.

    ``pairs`` is a list of ``(urn, text)`` tuples such as those returned
    by :func:`read_cex` / :func:`read_cex_many`. Unlike the ``urn_filter``
    those readers accept, the match here is exact, not a substring --
    this is how you pick out one citable passage once you already know
    its full URN.

    Raises ``KeyError`` if no pair has this exact URN. When more than one
    pair shares the URN, the first one wins.
    """
    for u, text in pairs:
        if u == urn:
            return text
    raise KeyError(f"no line with URN {urn!r}")
