"""Query variants: native, roman, mix25/50/75 (LLM), roman_rule (indic_transliteration).

    python -m src.variants            # all train+dev queries, cached to data/variants.jsonl
"""
from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor

from indic_transliteration import sanscript
from tqdm import tqdm

from src.config import load_config, path
from src.data import load_queries
from src.llm import chat, parse_json

VARIANTS_PATH = path("data", "variants.jsonl")
LLM_FIELDS = ("roman", "mix25", "mix50", "mix75")

SYSTEM = """You rewrite Hindi search queries the way real Indian users type them on a phone.
For every input query (Devanagari) return:
- "roman": the same query in casual romanized Hindi: Latin letters only, no diacritics,
  informal and inconsistent spelling as people really type (e.g. kya/kyaa, hai/h, mein/me,
  aur/or, double vowels sometimes, no capital letters needed).
- "mix25", "mix50", "mix75": romanized Hindi-English code-mixed versions in which about 25%,
  50% and 75% of the CONTENT words (nouns, verbs, adjectives, adverbs) are replaced by their
  natural English equivalents. Function words (ka, ki, hai, mein, kaun, kya ...) stay in
  romanized Hindi. Named entities are written as names in Latin script. Keep the meaning.
Never add or drop information. Reply with JSON only:
{"items": [{"id": "...", "roman": "...", "mix25": "...", "mix50": "...", "mix75": "..."}]}"""


def rule_roman(text: str) -> str:
    """Deterministic casual romanisation: Harvard-Kyoto, final schwa dropped, lower-cased."""
    import unicodedata

    text = unicodedata.normalize("NFD", text).replace("\u093c", "")  # drop nukta
    hk = sanscript.transliterate(text, sanscript.DEVANAGARI, sanscript.HK)
    words = []
    for w in re.findall(r"[A-Za-z~.]+|[0-9]+", hk):
        # inherent schwa at word end is silent in Hindi: HK short 'a' after a consonant
        if len(w) > 2 and w.endswith("a") and w[-2] not in "aAiIuUeEoO":
            w = w[:-1]
        w = w.replace("z", "sh").replace("S", "sh").replace("M", "n").replace("~", "n")
        w = w.replace("H", "h").replace(".", "").lower()
        if w:
            words.append(w)
    return " ".join(words)


def _llm_batch(batch: list[tuple[str, str]], model: str) -> dict[str, dict]:
    # Judgment: how a real user would romanise / code-mix this query (no exact rule exists).
    user = json.dumps({"queries": [{"id": q, "text": t} for q, t in batch]}, ensure_ascii=False)
    out = parse_json(chat([{"role": "system", "content": SYSTEM},
                           {"role": "user", "content": user}], model=model,
                           reasoning_effort="low"))
    res = {}
    for it in out.get("items", []):
        if it.get("id") and all(isinstance(it.get(f), str) and it[f].strip() for f in LLM_FIELDS):
            res[str(it["id"])] = {f: it[f].strip() for f in LLM_FIELDS}
    return res


def load_variants() -> dict[str, dict]:
    if not VARIANTS_PATH.exists():
        return {}
    with open(VARIANTS_PATH, encoding="utf-8") as f:
        return {r["qid"]: r for r in map(json.loads, f)}


def tuning_qids() -> list[str]:
    """Fixed random subset of train queries used for all tuning (rate-limit budget)."""
    import random

    cfg = load_config()
    qids = sorted(load_queries("train"))
    return sorted(random.Random(cfg["seed"]).sample(qids, cfg["tune_queries"]))


def generate(workers: int = 2) -> dict[str, dict]:
    cfg = load_config()["llm"]
    have = load_variants()
    todo = []
    tune = set(tuning_qids())
    for split in ("dev", "train"):
        for qid, text in load_queries(split).items():
            if qid not in have and (split == "dev" or qid in tune):
                todo.append((qid, text, split))
    bs = cfg["batch_size"]
    batches = [todo[i:i + bs] for i in range(0, len(todo), bs)]

    def run(batch):
        items = [(q, t) for q, t, _ in batch]
        got = _llm_batch(items, cfg["variant_model"])
        missing = [it for it in items if it[0] not in got]
        if missing:  # one batched retry, then singly as a last resort
            got.update(_llm_batch(missing, cfg["variant_model"]))
        for q, t in items:
            if q not in got:
                got.update(_llm_batch([(q, t)], cfg["variant_model"]))
        return batch, got

    with open(VARIANTS_PATH, "a", encoding="utf-8") as f, ThreadPoolExecutor(workers) as ex:
        for batch, got in tqdm(ex.map(run, batches), total=len(batches), desc="variants"):
            for qid, text, split in batch:
                if qid not in got:
                    print("WARN: no variant for", qid)
                    continue
                rec = {"qid": qid, "split": split, "native": text, **got[qid],
                       "roman_rule": rule_roman(text)}
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                have[qid] = rec
    return have


def queries_for(split: str, variant: str) -> dict[str, str]:
    """Variant text per query; train means the fixed tuning subset."""
    v = load_variants()
    qids = tuning_qids() if split == "train" else load_queries(split)
    return {qid: v[qid][variant] for qid in qids if qid in v}


if __name__ == "__main__":
    import sys

    v = generate()
    print(f"{len(v)} queries with variants in {VARIANTS_PATH}")
    for r in list(v.values())[:3]:
        print(json.dumps(r, ensure_ascii=False, indent=1))
