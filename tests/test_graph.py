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
