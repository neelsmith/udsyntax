"""A minimal, tolerant parser for CTS URNs.

CTS (Canonical Text Services) URNs identify citable passages of text as
``urn:cts:namespace:group.work.version:passage``. This project's CEX
corpus files (see :mod:`udsyntax.corpora`) key every line by one of these.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CtsUrn:
    """The parsed components of a CTS URN."""

    namespace: str
    group: str | None
    work: str | None
    version: str | None
    passage: str | None
    raw: str

    def __str__(self) -> str:
        return self.raw


def parse_cts_urn(urn: str) -> CtsUrn:
    """Parse a CTS URN string into its components.

    Tolerant of URNs missing a version or passage component -- fields
    that aren't present come back as ``None``. Raises ``ValueError`` if
    ``urn`` isn't a CTS URN at all (i.e. doesn't start with ``urn:cts:``).
    """
    parts = urn.strip().split(":")
    if len(parts) < 3 or parts[0] != "urn" or parts[1] != "cts":
        raise ValueError(f"not a CTS URN: {urn!r}")

    namespace = parts[2]
    work_component = parts[3] if len(parts) > 3 else ""
    passage = parts[4] if len(parts) > 4 else None

    work_parts = work_component.split(".") if work_component else []
    group = work_parts[0] if len(work_parts) > 0 else None
    work = work_parts[1] if len(work_parts) > 1 else None
    version = work_parts[2] if len(work_parts) > 2 else None

    return CtsUrn(
        namespace=namespace,
        group=group,
        work=work,
        version=version,
        passage=passage,
        raw=urn,
    )
