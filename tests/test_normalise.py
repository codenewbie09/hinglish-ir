from src.normalise import normalise_token
from src.pipeline import Searcher, system_config
from src.index import FieldIndex, InvertedIndex
from src.text import process, stem


def test_devanagari_tokens_pass_through():
    info = normalise_token("भारत", system_config("full"))
    assert info["terms"] == [("भारत", 1.0)] and info["script"] == "deva"


def test_roman_stopwords_dropped_when_normalising():
    assert normalise_token("hai", system_config("+translit"))["terms"] == []
    # baseline does nothing to Latin tokens
    assert normalise_token("hai", system_config("bm25"))["terms"] == [("hai", 1.0)]


def test_stemmer_is_light():
    assert stem("लड़कियों") != "लड़कियों"
    assert stem("घर") == "घर"
    assert process("भारत की राजधानी", stemming=False) == ["भारत", "राजधानी"]


def test_pipeline_baseline_on_toy_index():
    docs = [["भारत", "राजधानी"], ["गंगा", "नदी"]]
    fields = {f: FieldIndex.build(docs) for f in ("tok", "stem", "phon")}
    s = Searcher(index=InvertedIndex(["d0", "d1"], fields))
    _, hits = s.search("गंगा नदी", "bm25", k=2)
    assert hits[0][0] == "d1"


def test_searcher_accepts_bm25_parameters():
    docs = [["भारत", "राजधानी"], ["गंगा", "नदी"]]
    fields = {f: FieldIndex.build(docs) for f in ("tok", "stem", "phon")}
    s = Searcher(index=InvertedIndex(["d0", "d1"], fields), k1=0.9, b=0.4)
    assert all(m.k1 == 0.9 and m.b == 0.4 for m in s.bm25.values())


# ---- per-query expansion gate (off by default; tuned on train) -------------------------
import pytest

from src import normalise

DF = {"फिल्म": 1800, "कांग्रेस": 700, "संसद": 450, "इंडिया": 600, "भारत": 11000}
LEX = {"film": ["फिल्म"], "congress": ["संसद"], "india": ["भारत"]}
XL = {"film": ["फिल्म"], "congress": ["कांग्रेस"], "india": ["इंडिया"]}


@pytest.fixture
def fake_backends(monkeypatch):
    monkeypatch.setattr(normalise, "transliterate", lambda ws: {w: XL.get(w, []) for w in ws})
    monkeypatch.setattr(normalise, "lexicon", lambda ws: {
        w: {"english": w in LEX, "hindi": LEX.get(w, []), "deva": ""} for w in ws})


def _cfg(**kw):
    return {**system_config("full"), "latin_keep_weight": 0.0, "expansion_weight": 1.0,
            "translit_top2_weight": 0.0, "english_keep_weight": 0.0, **kw}


def _deva_terms(info):
    return [t for t, _ in info["terms"]]


def test_gate_off_by_default_keeps_old_behaviour(fake_backends):
    info = normalise.normalise_token("film", _cfg(), df=DF.get)
    assert _deva_terms(info) == ["फिल्म", "फिल्म"]


def test_dedupe_drops_expansion_equal_to_transliteration(fake_backends):
    info = normalise.normalise_token("film", _cfg(expansion_dedupe=True), df=DF.get)
    assert _deva_terms(info) == ["फिल्म"] and info["expansion"] == []


def test_df_gate_drops_expansion_when_transliteration_is_well_attested(fake_backends):
    cfg = _cfg(expansion_gate_ratio=1.0)
    congress = normalise.normalise_token("congress", cfg, df=DF.get)   # 700 >= 1.0 * 450
    india = normalise.normalise_token("india", cfg, df=DF.get)         # 600 <  1.0 * 11000
    assert _deva_terms(congress) == ["कांग्रेस"] and congress["gated"]
    assert _deva_terms(india) == ["इंडिया", "भारत"] and not india.get("gated")


def test_gate_needs_document_frequencies(fake_backends):
    # without an index (df=None) the gate cannot decide and expansion is kept
    info = normalise.normalise_token("congress", _cfg(expansion_gate_ratio=1.0))
    assert _deva_terms(info) == ["कांग्रेस", "संसद"]
