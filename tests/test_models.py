from udsyntax import SyntaxEdge, SyntaxNode, VerbalUnit


def test_syntax_node_str_and_is_root():
    root = SyntaxNode(id=0, text="Gallia", lemma="Gallia", pos="PROPN", relation="ROOT", head_id=0)
    assert str(root) == "Gallia (0)"
    assert root.is_root

    dep = SyntaxNode(id=1, text="est", lemma="sum", pos="AUX", relation="cop", head_id=0)
    assert not dep.is_root


def test_syntax_edge_str():
    edge = SyntaxEdge(src=0, target=1, relation="cop")
    assert str(edge) == "0 -> 1: cop"


def test_verbal_unit_defaults():
    vu = VerbalUnit(id=0, verb_token_id=3, verb_text="est")
    assert vu.depth is None
