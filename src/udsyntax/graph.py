"""Build a simple syntax graph (nodes + edges) from a spaCy ``Doc``."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .models import SyntaxEdge, SyntaxNode, VerbalUnit
from .urn import parse_cts_urn


@dataclass
class SyntaxGraph:
    """A dependency parse represented as syntax-graph nodes and edges."""

    nodes: list[SyntaxNode] = field(default_factory=list)
    edges: list[SyntaxEdge] = field(default_factory=list)
    urn: str | None = None

    @classmethod
    def from_doc(cls, doc, *, urn: str | None = None) -> "SyntaxGraph":
        """Build a ``SyntaxGraph`` from a parsed spaCy ``Doc``.

        ``doc`` must come from a pipeline that has run a dependency
        parser (its tokens need ``.dep_``, ``.head``, and ``.morph``).
        """
        nodes: list[SyntaxNode] = []
        edges: list[SyntaxEdge] = []
        has_sents = doc.has_annotation("SENT_START")
        for tok in doc:
            sent_id = tok.sent.start if has_sents else None
            nodes.append(
                SyntaxNode(
                    id=tok.i,
                    text=tok.text,
                    lemma=tok.lemma_,
                    pos=tok.pos_,
                    relation=tok.dep_,
                    head_id=tok.head.i,
                    morph=tok.morph.to_dict(),
                    sent_id=sent_id,
                )
            )
            if tok.dep_ != "ROOT":
                edges.append(SyntaxEdge(src=tok.head.i, target=tok.i, relation=tok.dep_))
        return cls(nodes=nodes, edges=edges, urn=urn)

    def node(self, node_id: int) -> SyntaxNode:
        for n in self.nodes:
            if n.id == node_id:
                return n
        raise KeyError(node_id)

    def root_nodes(self) -> list[SyntaxNode]:
        return [n for n in self.nodes if n.is_root]

    def children_of(self, node_id: int) -> list[SyntaxNode]:
        child_ids = {e.target for e in self.edges if e.src == node_id}
        return [n for n in self.nodes if n.id in child_ids]

    def verbal_units(self) -> list[VerbalUnit]:
        """Finite verbs in this graph, as ``VerbalUnit`` records.

        See :class:`udsyntax.models.VerbalUnit` for the current
        limitation on ``depth``.
        """
        units = []
        for i, n in enumerate(node for node in self.nodes if node.morph.get("VerbForm") == "Fin"):
            depth = 1 if n.is_root else None
            units.append(VerbalUnit(id=i, verb_token_id=n.id, verb_text=n.text, depth=depth))
        return units

    def to_polars(self):
        """Render this graph's nodes as a polars ``DataFrame``, one row per token."""
        import polars as pl

        rows = []
        for n in self.nodes:
            row = {
                "id": n.id,
                "text": n.text,
                "lemma": n.lemma,
                "pos": n.pos,
                "syntax": n.relation,
                "parentid": n.head_id,
                "sent_id": n.sent_id,
                **n.morph,
            }
            rows.append(row)
        return pl.DataFrame(rows)

    def to_networkx(self):
        """Render this graph as a ``networkx.DiGraph``, with token data as node attrs.

        Requires the optional ``networkx`` dependency (``pip install
        "udsyntax[graph]"``).
        """
        import networkx as nx

        g = nx.DiGraph()
        for n in self.nodes:
            g.add_node(n.id, text=n.text, lemma=n.lemma, pos=n.pos, relation=n.relation, **n.morph)
        for e in self.edges:
            g.add_edge(e.src, e.target, relation=e.relation)
        return g


def corpus_to_polars(graphs: Iterable[SyntaxGraph]):
    """Concatenate several ``SyntaxGraph``\\ s into one polars ``DataFrame``.

    Adds a ``doc_index`` column (position of each graph in ``graphs``).
    When a graph's ``urn`` is a parseable CTS URN, ``group`` / ``work`` /
    ``version`` / ``passage`` columns are added alongside it.
    """
    import polars as pl

    frames = []
    for i, g in enumerate(graphs):
        df = g.to_polars().with_columns(pl.lit(i).alias("doc_index"))
        if g.urn:
            try:
                parsed = parse_cts_urn(g.urn)
            except ValueError:
                df = df.with_columns(pl.lit(g.urn).alias("urn"))
            else:
                df = df.with_columns(
                    pl.lit(g.urn).alias("urn"),
                    pl.lit(parsed.group).alias("group"),
                    pl.lit(parsed.work).alias("work"),
                    pl.lit(parsed.version).alias("version"),
                    pl.lit(parsed.passage).alias("passage"),
                )
        frames.append(df)
    return pl.concat(frames, how="diagonal_relaxed") if frames else pl.DataFrame()
