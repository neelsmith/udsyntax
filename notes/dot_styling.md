# `to_dot()` styling, modeled on arsgrammatica

`SyntaxGraph.to_dot()` (`src/udsyntax/graph.py`) was restyled after
[neelsmith/arsgrammatica](https://github.com/neelsmith/arsgrammatica)'s own
`arsgrammatica.dot.tokengraph_to_dot()`, whose output the plain, unstyled DOT
`to_dot()` used to produce looked ugly next to. arsgrammatica's data model
(an LLM-derived `tokengraph` of `TokenAnalysis` records, with two related-token
slots per token, "unit verb" cross-references, and elided/implied tokens) is
structurally quite different from udsyntax's UD/spaCy single-parent dependency
tree, so this isn't a port of their code -- it's the same *visual* conventions
(box shapes, fill/stroke/text coloring, escaping, attribute ordering)
reimplemented against udsyntax's own `SyntaxNode`/`SyntaxEdge` model.

## What changed

- `node [shape=box];` is now declared once at the top of the digraph.
  Previously nothing set this, so Graphviz fell back to its own default
  (ellipses) -- likely the single biggest reason the old output looked
  plain.
- Every node is colored by **clause**: the finite verb nearest it going up
  the dependency tree (a token that IS a finite verb anchors its own
  clause). This required new logic udsyntax didn't have before --
  `_clause_anchor_for()` in `graph.py` walks a token's `head_id` chain
  until it hits a token with `morph["VerbForm"] == "Fin"`, or the root (no
  clause, left uncolored), or detects a cycle (malformed `head_id` data,
  also left uncolored, never an infinite loop).
- Colors cycle through an 8-slot pastel palette (`_CLAUSE_PALETTE` in
  `graph.py`), assigned in order of each clause's first appearance among
  the graph's tokens. **The palette's hex values are copied verbatim from
  arsgrammatica's `verbal_units._VERBAL_UNIT_PALETTE`** -- that's the part
  of "mimic its visual styling" taken most literally, since matching their
  actual colors was the point. Past 8 distinct clauses in one graph, colors
  repeat and `to_dot()` emits a `UserWarning` (doesn't raise) -- same
  as arsgrammatica's own "colors repeat" warning, just via Python's
  `warnings` module instead of a returned warnings list (see "API
  differences" below).
- `to_dot()` gained an `orientation` parameter, mapped straight onto
  DOT's own `rankdir` attribute. Previously `to_dot()` had no orientation
  control at all and always used Graphviz's own default (`TB`) -- which,
  after a round trip of getting this backwards mid-conversation, turned
  out to be the right default after all: since an edge always runs from
  a token to its dependent, and Graphviz's default ranking puts a node
  with no incoming edges (a sentence root) at rank 0, `rankdir=TB` puts
  the root at the top with dependents below -- the traditional
  syntax-tree reading -- while `rankdir=BT` would put the root at the
  *bottom* instead. `to_mermaid()`'s own `orientation` default was
  changed to match (`"TB"`, was `"BT"`) for the same reason -- its edges
  are encoded the identical way (`n<head> -->|relation| n<dependent>`),
  so the same rank-0-at-the-root reasoning applies there too.
- `to_dot()` gained a `color_by_clause` parameter (default `True`) to turn
  clause coloring off and get plain, unfilled boxes.
- Node labels dropped the token id (`"text (id:pos)"` -> `"text (pos)"`)
  -- arsgrammatica's own labels are just the bare surface word, no id or
  POS at all; keeping the POS tag (dropping only the id) was a deliberate
  middle ground -- see "Decisions" below.

## Decisions made explicit (asked, not assumed)

Two choices were checked with the user rather than guessed:

1. **Node label content** -- match arsgrammatica exactly (bare word only)
   vs. keep the POS tag, styled nicer. Chose to keep POS: it's useful
   context for a syntax package's own diagrams, more useful than the
   internal node id was.
2. **Clause coloring** -- implement it (the bulk of the new code in this
   pass) vs. skip coloring and just adopt box shape/escaping/attribute
   conventions. Chose to implement it, since it's the single biggest
   visual driver of "looks like arsgrammatica."

## What was deliberately left out of scope

- **`rank_by_depth`** -- arsgrammatica's dot renderer also forces
  same-depth verbal-unit anchors onto the same Graphviz rank via
  `{rank=same; ...}` subgraph statements, using a subordination-depth
  notion their `verbal_units.compute_aat_depths()` computes. udsyntax's own
  `VerbalUnit.depth` has had a matching gap since it was first written
  (only ever set to `1` for a ROOT-level verb, `None` otherwise -- see
  `models.py`'s docstring and `SyntaxGraph.verbal_units()`) -- implementing
  real subordination depth would resolve both at once, but is layout
  guidance rather than *visual* styling (color/shape/fonts), so it's out of
  scope for this pass. `_clause_anchor_for()` here already computes
  almost what's needed (which finite verb governs a token); a follow-up
  wanting `rank_by_depth` would extend that to walk clause-anchor-to-
  clause-anchor instead of stopping at the first one.
- **`to_mermaid()`** was not touched -- the user's ask was specifically
  about `to_dot()`'s ugliness. Its labels still include the node id
  (`"text (id:pos)"`), and it has no clause coloring.
- Punctuation tokens are still included as graph nodes (arsgrammatica
  excludes them from its own `tokengraph` entirely) -- changing *which*
  nodes appear is a different, bigger change than restyling the ones
  that already do.

## API differences from arsgrammatica (deliberate, not oversights)

- `tokengraph_to_dot()` returns `(dot_source, warnings)`; `to_dot()` still
  returns a plain `str`, matching `to_mermaid()`'s existing shape and
  keeping `scripts/text_to_dot.py` / `scripts/corpus_to_dot.py` (both do
  `print(graph.to_dot())`) working unchanged. The "more than 8 clauses"
  warning is instead raised as a real Python `UserWarning` via the
  standard library `warnings` module.
- arsgrammatica's `orientation` is documented as deliberately
  unvalidated ("a typo just becomes an attribute value Graphviz itself
  will reject"). udsyntax's `to_dot()` validates against
  `DOT_ORIENTATIONS` (`TB`/`BT`/`LR`/`RL`) and raises `ValueError` on
  anything else -- matching `to_mermaid()`'s own existing validation
  behavior in this package, rather than arsgrammatica's more permissive
  one.

## Testing

Full suite: 32/32 passing (27 previous + 5 new -- basic styled structure,
`orientation` accepted/rejected including the Mermaid-only `"TD"` alias,
`color_by_clause=False`, multi-clause coloring via a new
`subordinate_clause_doc` fixture in `tests/conftest.py`, and the
more-than-8-clauses warning via directly constructed `SyntaxNode`s, no
spaCy `Doc` needed for that last one). Also spot-checked by hand: rendered
`to_dot()` output through the real `dot -Tpng` binary and looked at the
resulting image for both a single-clause sentence (uniform color) and a
two-clause one (two distinct colors, correctly split at the subordinating
conjunction), and again after switching the default from `"BT"` to
`"TB"` -- confirming the root verb now renders at the top with its
dependents below, rather than at the bottom.
