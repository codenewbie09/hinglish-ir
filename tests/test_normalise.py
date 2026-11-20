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
