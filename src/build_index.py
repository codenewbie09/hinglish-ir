"""Build the three-field inverted index: tok (plain), stem (stemmed), phon (phonetic keys).

    python -m src.build_index [--sample|--full]
"""
from __future__ import annotations

import argparse
import time

from tqdm import tqdm

from src import text
from src.config import path
from src.data import add_mode_flags, apply_mode, doc_text, load_corpus
from src.index import FieldIndex, InvertedIndex
from src.phonetic import phonetic_key


def index_path(mode: str):
    return path("data", "processed", mode, "index.pkl")


def build(mode: str) -> InvertedIndex:
    corpus = load_corpus(mode)
    t0 = time.time()
    # Documents keep stop words (query-side removal is a toggle); see README.
    toks = [text.tokenize(doc_text(d)) for d in tqdm(corpus, desc="tokenise")]
    print(f"tokenised {len(toks)} docs in {time.time()-t0:.0f}s")
    stem_cache: dict[str, str] = {}
    phon_cache: dict[str, str] = {}

    def stems(ts):
        return [stem_cache.get(t) or stem_cache.setdefault(t, text.stem(t)) for t in ts]

    def phons(ts):
        return [phon_cache.get(t) or phon_cache.setdefault(t, phonetic_key(t)) for t in ts]

    fields = {
        "tok": FieldIndex.build(toks),
        "stem": FieldIndex.build(stems(t) for t in toks),
        "phon": FieldIndex.build(phons(t) for t in toks),
    }
    ix = InvertedIndex([d["docid"] for d in corpus], fields)
    for name, f in fields.items():
        print(f"field {name}: vocab={len(f.vocab):,} postings={len(f.docs):,} avgdl={f.avgdl:.1f}")
    print(f"index built in {time.time()-t0:.0f}s")
    return ix


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    add_mode_flags(ap)
    mode = apply_mode(ap.parse_args())
    build(mode).save(index_path(mode))
    print("saved", index_path(mode))
