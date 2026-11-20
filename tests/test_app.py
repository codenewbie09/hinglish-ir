"""Drives app.py headlessly with Streamlit's AppTest. Needs the sample index (make index)."""
import pytest

from src.config import ROOT

pytestmark = pytest.mark.skipif(
    not (ROOT / "data" / "processed" / "sample" / "index.pkl").exists(), reason="no sample index")


@pytest.fixture(scope="module")
def at():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=300)
    app.run()
    return app


def _texts(at):
    return " ".join(m.value for m in at.markdown)


def test_default_query_renders_both_columns(at):
    assert not at.exception, at.exception
    assert [s.value for s in at.subheader] == ["Baseline: BM25", "System: full"]
    assert "Normalised query" in _texts(at)


@pytest.mark.parametrize("system", ["bm25", "+translit", "+phonetic", "+expansion", "full",
                                    "dense", "hybrid"])
def test_every_system(at, system):
    at.selectbox[1].set_value(system).run()
    assert not at.exception, at.exception
    assert at.subheader[1].value == f"System: {system}"
    assert len(at.markdown) > 4  # result cards rendered


@pytest.mark.parametrize("query", ["भगत सिंह की मृत्यु कब हुई थी", "Elon Musk ka birth kab hua",
                                   "!!!", "zzzzqqq", "a"])
def test_odd_queries_do_not_crash(at, query):
    at.selectbox[1].set_value("full").run()
    at.text_input[0].set_value(query).run()
    assert not at.exception, at.exception
    assert not at.error, [e.value for e in at.error]


def test_example_dropdown(at):
    at.selectbox[0].set_value("google ki khoj kisne ki thi").run()
    assert not at.exception
    assert at.text_input[0].value == "google ki khoj kisne ki thi"
