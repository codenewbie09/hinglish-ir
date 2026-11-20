from src.fusion import rrf


def test_rrf_rewards_agreement():
    out = [d for d, _ in rrf([["a", "b", "c"], ["b", "a", "d"]], k=60)]
    assert out[:2] in (["a", "b"], ["b", "a"])
    assert set(out) == {"a", "b", "c", "d"}


def test_rrf_weights():
    out = [d for d, _ in rrf([["a"], ["b"]], weights=[1.0, 2.0])]
    assert out == ["b", "a"]
