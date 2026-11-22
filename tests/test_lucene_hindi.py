"""Port of Lucene's HindiAnalyzer (Indic + Hindi normaliser, stop filter, Hindi stemmer)."""
from src.lucene_hindi import analyse, hindi_normalise, indic_compose, stem


def test_indic_compose_joins_vowel_sequences():
    assert indic_compose("अा") == "आ"
    assert indic_compose("अाे") == "ओ"          # 3-char sequence wins over the 2-char one
    assert indic_compose("\u0915\u093c") == "\u0958"  # base + nukta -> precomposed


def test_hindi_normaliser_rules():
    assert hindi_normalise("हिंदी") == hindi_normalise("हिन्दी")   # dead na -> anusvara
    assert hindi_normalise("माँ") == "मां"                         # candrabindu -> anusvara
    assert hindi_normalise("आम") == "अम"                           # independent long vowel -> short
    assert hindi_normalise("ज़मीन") == "जमिन"                     # nukta dropped, long i -> short
    assert hindi_normalise("ज़मीन") == "जमिन"                  # precomposed nukta letter
    assert hindi_normalise("क्या") == "कया"                        # virama deleted, matra aa kept
    assert hindi_normalise("कौन") == "कोन"                         # au -> o
    assert hindi_normalise("ab‍c") == "abc"                   # ZWJ deleted


def test_stemmer_buckets_and_length_conditions():
    assert stem("लडकियों") == "लडक"     # bucket 4 'ियों', len 7 > 5
    assert stem("खाएंगे") == "खा"       # 6 chars: bucket 5 needs len > 6, so bucket 4 'एंगे'
    assert stem("घर") == "घर"           # too short for bucket 1 (len > 2)
    assert stem("घरो") == "घर"          # bucket 1
    assert stem("करना") == "कर"         # bucket 2 'ना'


def test_analyse_runs_the_chain_in_lucene_order():
    # stop words are matched after normalisation: 'में' -> 'में' is unchanged and is a stop word,
    # 'और' -> 'ओर' is in the normalised-forms part of the list
    assert analyse("भारत में और लड़कियों") == ["भारत", "लडक"]
    # digits and Latin are lower-cased and kept
    assert analyse("COVID १९") == ["covid", "19"]


def test_lucene_index_and_search_on_toy_corpus():
    from src.build_index import build_lucene_index
    from src.eval import lucene_search
    from src.pipeline import Searcher

    corpus = [{"docid": "d0", "title": "भारत", "text": "भारत की राजधानी"},
              {"docid": "d1", "title": "गंगा", "text": "गंगा नदियों में है"}]
    ix = build_lucene_index(corpus)
    assert ix.doc_ids == ["d0", "d1"] and set(ix.fields) == {"tok"}
    assert "है" not in ix.fields["tok"].vocab          # stop words removed from documents
    s = Searcher(index=ix, k1=0.9, b=0.4)
    assert lucene_search(s, "नदी", 2)[0] == "d1"        # 'नदियों' and 'नदी' stem alike
