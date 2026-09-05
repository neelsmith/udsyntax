import pytest
from spacy.tokens import Doc
from spacy.vocab import Vocab

from udsyntax import SyntaxGraph, corpus_to_polars


def test_from_doc_builds_nodes_and_edges(latin_doc):
    graph = SyntaxGraph.from_doc(latin_doc)

    assert len(graph.nodes) == 5
    # ROOT ("divisa", id 3) contributes no incoming edge; every other
    # token's dependency becomes one edge into it or another head.
    assert len(graph.edges) == 4

    root = graph.node(3)
    assert root.text == "divisa"
    assert root.is_root
    assert root.morph == {"VerbForm": "Fin", "Voice": "Pass"}

    subj = graph.node(0)
    assert subj.text == "Gallia"
    assert subj.head_id == 3
    assert subj.relation == "nsubj"


def test_root_nodes_and_children_of(latin_doc):
    graph = SyntaxGraph.from_doc(latin_doc)

    roots = graph.root_nodes()
    assert [n.id for n in roots] == [3]

    children = {n.id for n in graph.children_of(3)}
    assert children == {0, 1, 2, 4}


def test_verbal_units_finds_finite_verb_at_root(latin_doc):
    graph = SyntaxGraph.from_doc(latin_doc)
    units = graph.verbal_units()

    assert len(units) == 1
    assert units[0].verb_text == "divisa"
    assert units[0].depth == 1


def test_to_polars_has_one_row_per_token(latin_doc):
    graph = SyntaxGraph.from_doc(latin_doc)
    df = graph.to_polars()

    assert df.height == 5
    assert df["text"].to_list() == ["Gallia", "est", "omnis", "divisa", "."]
    assert "VerbForm" in df.columns


def test_to_networkx_round_trips_edges(latin_doc):
    graph = SyntaxGraph.from_doc(latin_doc)
    g = graph.to_networkx()

    assert g.number_of_nodes() == 5
    assert g.number_of_edges() == 4
    assert g.nodes[3]["text"] == "divisa"
    assert g.edges[3, 1]["relation"] == "cop"


def test_corpus_to_polars_adds_doc_index_and_urn_metadata(latin_doc):
    urn = "urn:cts:phi:phi0448.phi001.perseus-lat2:1.1.1"
    graph = SyntaxGraph.from_doc(latin_doc, urn=urn)

    df = corpus_to_polars([graph, graph])

    assert df.height == 10
    assert df["doc_index"].to_list() == [0] * 5 + [1] * 5
    assert set(df["work"].unique().to_list()) == {"phi001"}
    assert set(df["version"].unique().to_list()) == {"perseus-lat2"}


def test_corpus_to_polars_empty_list_returns_empty_frame():
    df = corpus_to_polars([])
    assert df.is_empty()


def test_to_mermaid_default_orientation_is_tb(latin_doc):
    graph = SyntaxGraph.from_doc(latin_doc)
    mermaid = graph.to_mermaid()

    lines = mermaid.splitlines()
    assert lines[0] == "graph TB"
    assert 'n3["divisa (3:VERB)"]' in mermaid
    assert "n3 -->|nsubj| n0" in mermaid
    assert "n3 -->|cop| n1" in mermaid


def test_to_mermaid_accepts_orientation(latin_doc):
    graph = SyntaxGraph.from_doc(latin_doc)
    mermaid = graph.to_mermaid(orientation="LR")
    assert mermaid.splitlines()[0] == "graph LR"


def test_to_mermaid_rejects_invalid_orientation(latin_doc):
    graph = SyntaxGraph.from_doc(latin_doc)
    with pytest.raises(ValueError):
        graph.to_mermaid(orientation="sideways")


def test_to_mermaid_escapes_special_characters():
    vocab = Vocab()
    doc = Doc(vocab, words=['"Hi|there"'], heads=[0], deps=["ROOT"], pos=["INTJ"])
    graph = SyntaxGraph.from_doc(doc)

    mermaid = graph.to_mermaid()
    assert "&quot;Hi&#124;there&quot;" in mermaid


def test_to_dot_basic_structure(latin_doc):
    # A single-clause sentence (one finite verb, the ROOT) -- every node
    # belongs to that one clause, so every node gets the same (first)
    # palette color.
    graph = SyntaxGraph.from_doc(latin_doc)
    dot = graph.to_dot()

    assert dot.startswith('digraph "SyntaxGraph" {')
    assert "    rankdir=TB;" in dot
    assert "    node [shape=box];" in dot
    assert dot.rstrip().endswith("}")

    blue = 'fillcolor="#82bbff", color="#2a78d6", fontcolor="#000000", style="filled"'
    assert f'n3 [label="divisa (VERB)", {blue}];' in dot
    assert f'n0 [label="Gallia (PROPN)", {blue}];' in dot
    assert 'n3 -> n0 [label="nsubj"];' in dot


def test_to_dot_accepts_orientation(latin_doc):
    graph = SyntaxGraph.from_doc(latin_doc)
    dot = graph.to_dot(orientation="LR")
    assert "    rankdir=LR;" in dot


def test_to_dot_rejects_invalid_orientation(latin_doc):
    graph = SyntaxGraph.from_doc(latin_doc)
    with pytest.raises(ValueError):
        graph.to_dot(orientation="sideways")
    with pytest.raises(ValueError):
        # "TD" is a Mermaid-only alias -- not valid DOT rankdir.
        graph.to_dot(orientation="TD")


def test_to_dot_uses_urn_as_graph_name(latin_doc):
    urn = "urn:cts:phi:phi0448.phi001.perseus-lat2:1.1.1"
    graph = SyntaxGraph.from_doc(latin_doc, urn=urn)
    dot = graph.to_dot()
    assert dot.startswith(f'digraph "{urn}" {{')


def test_to_dot_escapes_quotes_and_backslashes():
    vocab = Vocab()
    doc = Doc(
        vocab,
        words=["back\\slash", 'quo"te'],
        heads=[0, 0],
        deps=["ROOT", "dep"],
        pos=["X", "X"],
    )
    graph = SyntaxGraph.from_doc(doc)
    dot = graph.to_dot()

    assert "back\\\\slash" in dot
    assert 'quo\\"te' in dot


def test_to_dot_color_by_clause_false_leaves_nodes_uncolored(latin_doc):
    graph = SyntaxGraph.from_doc(latin_doc)
    dot = graph.to_dot(color_by_clause=False)

    assert "fillcolor" not in dot
    assert 'n3 [label="divisa (VERB)"];' in dot
    assert 'n0 [label="Gallia (PROPN)"];' in dot


def test_to_dot_colors_by_clause_with_subordination(subordinate_clause_doc):
    # "Cum venit Caesar vicit." (contrived, not real Latin): "venit" is a
    # subordinate finite verb (head "vicit", relation advclt), "vicit" is
    # the root finite verb. "Cum" (a dependent of "venit") should share
    # its clause's color; "Caesar" and "." (dependents of "vicit") should
    # share the root clause's color instead -- and the two colors should
    # differ, ordered by which clause's tokens appear first in the text.
    graph = SyntaxGraph.from_doc(subordinate_clause_doc)
    dot = graph.to_dot()

    subordinate = 'fillcolor="#82bbff", color="#2a78d6", fontcolor="#000000", style="filled"'
    main = 'fillcolor="#ffa682", color="#eb6834", fontcolor="#000000", style="filled"'

    assert f'n0 [label="Cum (SCONJ)", {subordinate}];' in dot
    assert f'n1 [label="venit (VERB)", {subordinate}];' in dot
    assert f'n2 [label="Caesar (PROPN)", {main}];' in dot
    assert f'n3 [label="vicit (VERB)", {main}];' in dot
    assert f'n4 [label=". (PUNCT)", {main}];' in dot


def test_to_dot_warns_when_more_than_eight_clauses():
    from udsyntax import SyntaxNode

    nodes = [
        SyntaxNode(
            id=i,
            text=f"verb{i}",
            lemma=f"verb{i}",
            pos="VERB",
            relation="ROOT",
            head_id=i,
            morph={"VerbForm": "Fin"},
        )
        for i in range(9)
    ]
    graph = SyntaxGraph(nodes=nodes, edges=[])

    with pytest.warns(UserWarning, match="9 clauses"):
        graph.to_dot()
