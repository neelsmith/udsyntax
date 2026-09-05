"""Core data model for a Universal Dependencies syntax graph.

These lightweight dataclasses mirror the ``SyntaxNode`` / ``SyntaxEdge`` /
``VerbalUnit`` sketch from the original marimo prototype
(``scratch/ud2syntax.py``), cleaned up into a stable, importable API.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SyntaxNode:
    """A single token in a dependency parse, as a syntax-graph node."""

    id: int
    text: str
    lemma: str
    pos: str
    relation: str
    head_id: int
    morph: dict = field(default_factory=dict)
    sent_id: int | None = None

    def __str__(self) -> str:
        return f"{self.text} ({self.id})"

    @property
    def is_root(self) -> bool:
        return self.relation == "ROOT"


@dataclass
class SyntaxEdge:
    """A directed dependency relation between two token ids."""

    src: int
    target: int
    relation: str

    def __str__(self) -> str:
        return f"{self.src} -> {self.target}: {self.relation}"


@dataclass
class VerbalUnit:
    """A finite verb and (eventually) the syntactic material organized around it.

    ``depth`` mirrors the original prototype's heuristic: only a verbal
    unit that is itself the sentence ``ROOT`` currently gets a depth
    (``1``); dependent verbal units are left as ``None`` pending a real
    subordination-depth calculation.
    """

    id: int
    verb_token_id: int
    verb_text: str
    depth: int | None = None
