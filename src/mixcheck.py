"""How code-mixed are the mix25/50/75 variants really? (README limitation: never checked.)

Two measures per query, both over Latin content tokens (roman stop words, English stop
words and numbers removed):
  english_share  - share the cached LLM lexicon tags as English (needs data/cache/lexicon.json)
  replaced_share - share of the roman variant's content tokens that the mix variant no longer
                   contains (exact token diff, no model involved)

    python -m src.mixcheck            # dev queries -> results/mix_ratio.csv
"""
from __future__ import annotations

import json

import numpy as np

from src.normalise import LEXICON_PATH, ROMAN_STOPWORDS, detect_script
from src.text import ENGLISH_STOPWORDS, tokenize

TARGETS = {"roman": 0.0, "mix25": 0.25, "mix50": 0.50, "mix75": 0.75}


def content_tokens(query: str) -> list[str]:
    return [t for t in tokenize(query) if detect_script(t) == "latin" and not t.isdigit()
            and t not in ROMAN_STOPWORDS and t not in ENGLISH_STOPWORDS]


def english_share(query: str, lexicon: dict) -> float | None:
    known = [t for t in content_tokens(query) if t in lexicon]
    return sum(bool(lexicon[t]["english"]) for t in known) / len(known) if known else None


def replaced_share(roman: str, mixed: str) -> float | None:
    base = content_tokens(roman)
    if not base:
        return None
    kept = set(content_tokens(mixed))
    return sum(t not in kept for t in base) / len(base)


def summarise(values: list[float | None]) -> dict:
    x = np.array([v for v in values if v is not None], dtype=float)
    return {"n": int(len(x)), "mean": float(x.mean()), "median": float(np.median(x)),
            "q25": float(np.percentile(x, 25)), "q75": float(np.percentile(x, 75)),
            "zero": float(np.mean(x == 0))}


def main():
    import pandas as pd

    from src.config import path
    from src.variants import load_variants

    lex = json.loads(LEXICON_PATH.read_text("utf-8"))
    dev = [r for r in load_variants().values() if r["split"] == "dev"]
    rows = []
    for level, target in TARGETS.items():
        for measure, vals in [
            ("english_share", [english_share(r[level], lex) for r in dev]),
            ("replaced_share", [replaced_share(r["roman"], r[level]) for r in dev]),
        ]:
            rows.append({"variant": level, "target": target, "measure": measure, **summarise(vals)})
    df = pd.DataFrame(rows)
    out = path("results", "mix_ratio.csv")
    df.to_csv(out, index=False, float_format="%.3f")
    print(df.to_string(index=False, float_format="%.3f"))
    print(f"-> {out}")


if __name__ == "__main__":
    main()
