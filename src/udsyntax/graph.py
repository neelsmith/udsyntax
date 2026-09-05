"""Build a simple syntax graph (nodes + edges) from a spaCy ``Doc``."""
from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Iterable

from .models import SyntaxEdge, SyntaxNode, VerbalUnit
from .urn import parse_cts_urn

#: Direction keywords Mermaid accepts for a flowchart's ``graph``/``flowchart`` header.
MERMAID_ORIENTATIONS = frozenset({"TB", "TD", "BT", "RL", "LR"})

#: Direction keywords Graphviz's DOT accepts for a digraph's ``rankdir`` attribute.
#: (No ``"TD"`` here -- that's a Mermaid-only alias for ``"TB"``, not something
#: Graphviz itself recognizes.)
DOT_ORIENTATIONS = frozenset({"TB", "BT", "LR", "RL"})

#: Categorical palette for coloring `to_dot()` nodes by clause: 8 (fill,
#: stroke, text) triples, cycled through in order of each clause's first
#: appearance among a graph's tokens. Copied verbatim from
#: neelsmith/arsgrammatica's own `verbal_units._VERBAL_UNIT_PALETTE`
#: (arsgrammatica/verbal_units.py), whose dot/mermaid renderers this
#: package's `to_dot()` styling is modeled on: a light, low-saturation
#: pastel `fill` per slot, that same hue at full saturation as `stroke`,
#: and black `text` throughout for reliable contrast against every fill.
_CLAUSE_PALETTE: list[tuple[str, str, str]] = [
    ("#82bbff", "#2a78d6", "#000000"),  # blue
    ("#ffa682", "#eb6834", "#000000"),  # orange
    ("#70ffcc", "#1baf7a", "#000000"),  # aqua
    ("#ffd170", "#eda100", "#000000"),  # yellow
    ("#ff94bc", "#e87ba4", "#000000"),  # magenta
    ("#7aff7a", "#008300", "#000000"),  # green
    ("#a494ff", "#4a3aa7", "#000000"),  # violet
    ("#ff9594", "#e34948", "#000000"),  # red
]


def _mermaid_escape(text: str) -> str:
    """Escape text for use inside a quoted Mermaid node or edge label."""
    return (
        text.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("|", "&#124;")
    )


def _dot_escape(text: str) -> str:
    """Escape text for use inside a quoted Graphviz DOT string."""
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _clause_anchor_for(node_id: int, nodes_by_id: dict) -> int | None:
    """The nearest finite-verb ancestor of a node, walking up ``head_id``
    -- the node itself, if it's already a finite verb (``morph["VerbForm"]
    == "Fin"``); otherwise whichever finite verb governs it, however many
    edges up the dependency tree that takes. This is `to_dot()`'s notion
    of "clause": every token belongs to the clause anchored by the
    nearest finite verb above it, the same way arsgrammatica's
    `verbal_units.assign_verbal_units()` groups its own richer token
    model by clause (see that function's docstring) -- adapted here to a
    single-parent UD tree, where "which finite verb governs this token"
    has one unambiguous answer instead of needing arsgrammatica's
    reverse-relation special cases.

    Returns ``None`` if no finite verb is reached before the root (a
    verbless fragment, or a nominal sentence with no finite predicate) or
    a cycle is detected (malformed ``head_id`` data) -- either way, "no
    clause" for `to_dot()`'s coloring to leave uncolored.
    """
    visited: set = set()
    current_id = node_id
    while current_id not in visited:
        visited.add(current_id)
        node = nodes_by_id.get(current_id)
        if node is None:
            return None
        if node.morph.get("VerbForm") == "Fin":
            return node.id
        if node.is_root:
            return None
        current_id = node.head_id
    return None  # cycle in head_id data


def _assign_clause_colors(
    nodes: list[SyntaxNode], assignment: dict
) -> tuple[dict, str | None]:
    """Map each clause anchor id found in ``assignment`` to a
    `_CLAUSE_PALETTE` color, ordered by that clause's first appearance
    among ``nodes`` (the same "order of first appearance" rule
    arsgrammatica's `verbal_units.assign_verbal_unit_colors()` uses).
    Colors cycle (mod 8) past the 8th clause; returns a warning message
    (or ``None``) for `to_dot()` to surface as a ``UserWarning`` when that
    happens, rather than silently letting two different clauses look
    identical with no way to tell.
    """
    order: list[int] = []
    seen: set = set()
    for n in nodes:
        unit = assignment.get(n.id)
        if unit is not None and unit not in seen:
            seen.add(unit)
            order.append(unit)

    warning = None
    if len(order) > len(_CLAUSE_PALETTE):
        warning = (
            f"{len(order)} clauses but only {len(_CLAUSE_PALETTE)} distinct "
            "colors in to_dot()'s palette -- colors repeat and may be "
            "ambiguous between clauses"
        )

    colors = {
        unit: _CLAUSE_PALETTE[i % len(_CLAUSE_PALETTE)] for i, unit in enumerate(order)
    }
    return colors, warning


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

    def to_mermaid(self, orientation: str = "TB") -> str:
        """Render this graph as a Mermaid flowchart definition.

        Each node is rendered as ``n<id>["text (id:pos)"]`` and each
        dependency edge as ``n<head> -->|relation| n<dependent>``, so the
        arrow direction always runs from a token to its dependent,
        regardless of ``orientation``.

        Parameters
        ----------
        orientation:
            The direction keyword written after ``graph`` in the header
            line -- one of ``"TB"``, ``"TD"``, ``"BT"``, ``"RL"``, or
            ``"LR"`` (see the Mermaid flowchart docs). Defaults to
            ``"TB"`` (top-to-bottom): since an edge always runs from a
            token to its dependent, this puts the governing token (the
            one with no incoming edge -- a sentence root) at the top and
            its dependents below, the traditional syntax-tree reading.

        No external dependency is required -- this returns plain text
        that can be pasted into any Mermaid-aware renderer (GitHub,
        Claude/Cowork artifacts, the Mermaid Live Editor, etc.).
        """
        if orientation not in MERMAID_ORIENTATIONS:
            raise ValueError(
                f"orientation must be one of {sorted(MERMAID_ORIENTATIONS)}, got {orientation!r}"
            )

        lines = [f"graph {orientation}"]
        for n in self.nodes:
            label = _mermaid_escape(f"{n.text} ({n.id}:{n.pos})")
            lines.append(f'    n{n.id}["{label}"]')
        for e in self.edges:
            label = _mermaid_escape(e.relation)
            lines.append(f"    n{e.src} -->|{label}| n{e.target}")
        return "\n".join(lines)

    def to_dot(self, orientation: str = "TB", *, color_by_clause: bool = True) -> str:
        """Render this graph as a Graphviz DOT ``digraph`` definition,
        styled after neelsmith/arsgrammatica's own dot renderer
        (``arsgrammatica.dot.tokengraph_to_dot()``): filled, boxy nodes
        colored by clause, laid out with an explicit ``rankdir``, rather
        than plain unstyled nodes left to Graphviz's own default ellipses.

        Each node is rendered as ``n<id> [label="text (pos)", fillcolor=
        "...", color="...", fontcolor="...", style="filled"];`` -- or, when
        ``color_by_clause`` is False or a token belongs to no clause, just
        ``n<id> [label="text (pos)"];`` (an unfilled box). Each dependency
        edge is ``n<head> -> n<dependent> [label="relation"];``. The
        digraph is named after ``self.urn`` when present, otherwise
        ``"SyntaxGraph"``.

        Parameters
        ----------
        orientation:
            DOT's own ``rankdir`` value: ``"TB"`` (the default -- since
            an edge always runs from a token to its dependent, this puts
            the governing token (a sentence root has no incoming edge)
            at the top and its dependents below, the traditional
            syntax-tree reading, matching `to_mermaid()`'s own default),
            ``"BT"``, ``"LR"``, or ``"RL"``.
        color_by_clause:
            Color every token by the clause it belongs to -- the nearest
            finite verb above it in the dependency tree, per
            `_clause_anchor_for()` (a token that IS a finite verb anchors
            its own clause) -- cycling through the same 8-color pastel
            palette arsgrammatica uses. A token with no finite verb
            anywhere above it (a verbless fragment) is left uncolored.
            Emits a ``UserWarning`` (never raises) if a passage has more
            than 8 clauses, since colors repeat past the 8th.

        No external dependency is required -- this returns plain DOT
        source text; feed it to the ``dot`` command line tool or the
        ``graphviz`` Python package to render an image.
        """
        if orientation not in DOT_ORIENTATIONS:
            raise ValueError(
                f"orientation must be one of {sorted(DOT_ORIENTATIONS)}, got {orientation!r}"
            )

        colors_by_node: dict = {}
        if color_by_clause:
            nodes_by_id = {n.id: n for n in self.nodes}
            assignment = {n.id: _clause_anchor_for(n.id, nodes_by_id) for n in self.nodes}
            palette, repeats_warning = _assign_clause_colors(self.nodes, assignment)
            if repeats_warning:
                warnings.warn(repeats_warning, stacklevel=2)
            for n in self.nodes:
                unit = assignment.get(n.id)
                colors_by_node[n.id] = palette.get(unit) if unit is not None else None

        graph_name = _dot_escape(self.urn if self.urn else "SyntaxGraph")
        lines = [
            f'digraph "{graph_name}" {{',
            f"    rankdir={orientation};",
            "    node [shape=box];",
            "",
        ]
        for n in self.nodes:
            label = _dot_escape(f"{n.text} ({n.pos})")
            attrs = [f'label="{label}"']
            color = colors_by_node.get(n.id)
            if color is not None:
                fill, stroke, text_color = color
                attrs.append(f'fillcolor="{fill}"')
                attrs.append(f'color="{stroke}"')
                attrs.append(f'fontcolor="{text_color}"')
                attrs.append('style="filled"')
            lines.append(f"    n{n.id} [{', '.join(attrs)}];")

        lines.append("")
        for e in self.edges:
            label = _dot_escape(e.relation)
            lines.append(f'    n{e.src} -> n{e.target} [label="{label}"];')
        lines.append("}")
        return "\n".join(lines)


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
