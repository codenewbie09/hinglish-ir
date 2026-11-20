"""MIRACL-hi loading and the --sample / --full corpus.

sample = every passage judged for train+dev queries (train is needed for tuning)
         + N random passages (config data.sample_random_passages), fixed seed.
"""
from __future__ import annotations

import argparse
import gzip
import json
import random
from functools import lru_cache

from src.config import ROOT, corpus_mode, load_config, path

RAW = ROOT / "data" / "raw"
TOPICS = RAW / "miracl-v1.0-hi" / "topics" / "topics.miracl-v1.0-hi-{split}.tsv"
QRELS = RAW / "miracl-v1.0-hi" / "qrels" / "qrels.miracl-v1.0-hi-{split}.tsv"
CORPUS_FILES = [RAW / "miracl-corpus-v1.0-hi" / f"docs-{i}.jsonl.gz" for i in (0, 1)]


def load_queries(split: str) -> dict[str, str]:
    out = {}
    with open(str(TOPICS).format(split=split), encoding="utf-8") as f:
        for line in f:
            qid, text = line.rstrip("\n").split("\t", 1)
            out[qid] = text
    return out


def load_qrels(split: str) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    with open(str(QRELS).format(split=split), encoding="utf-8") as f:
        for line in f:
            qid, _, did, rel = line.split()
            out.setdefault(qid, {})[did] = int(rel)
    return out


def iter_full_corpus():
    for fp in CORPUS_FILES:
        with gzip.open(fp, "rt", encoding="utf-8") as f:
            for line in f:
                yield json.loads(line)


def corpus_path(mode: str | None = None):
    return path("data", "processed", mode or corpus_mode(), "corpus.jsonl")


def build_corpus(mode: str) -> int:
    cfg = load_config()
    out = corpus_path(mode)
    if mode == "full":
        keep = None
    else:
        judged = {d for s in ("train", "dev") for r in load_qrels(s).values() for d in r}
        all_ids = [d["docid"] for d in iter_full_corpus()]
        rng = random.Random(cfg["seed"])
        pool = [d for d in all_ids if d not in judged]
        keep = judged | set(rng.sample(pool, cfg["data"]["sample_random_passages"]))
    n = 0
    with open(out, "w", encoding="utf-8") as f:
        for d in iter_full_corpus():
            if keep is None or d["docid"] in keep:
                f.write(json.dumps(d, ensure_ascii=False) + "\n")
                n += 1
    return n


@lru_cache(maxsize=2)
def load_corpus(mode: str | None = None) -> list[dict]:
    with open(corpus_path(mode), encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def doc_text(d: dict) -> str:
    return f"{d['title']} {d['text']}"


def add_mode_flags(ap: argparse.ArgumentParser) -> None:
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sample", action="store_true", help="sample corpus (default)")
    g.add_argument("--full", action="store_true", help="full 506k-passage corpus")


def apply_mode(args) -> str:
    import os

    mode = "full" if getattr(args, "full", False) else "sample"
    os.environ["HIR_MODE"] = mode
    return mode


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Build the sample/full corpus file")
    add_mode_flags(ap)
    mode = apply_mode(ap.parse_args())
    print(f"{mode}: wrote {build_corpus(mode)} passages to {corpus_path(mode)}")
