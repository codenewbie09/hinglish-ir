"""Query normalisation for romanised / code-mixed Hindi queries.

a. script detection per token (exact)
b. transliteration roman -> Devanagari (IndicXlit; LLM fallback)
c. phonetic keys (src/phonetic.py; used as a second index field by the pipeline)
d. bilingual expansion: English tokens get Hindi equivalents (LLM dictionary)

LLM output is cached per token in data/cache/lexicon.json so the demo and the
evaluation share it and nothing is ever re-requested.
"""
from __future__ import annotations

import json
import threading

from src import xlit
from src.config import load_config, path
from src.llm import chat, parse_json

LEXICON_PATH = path("data", "cache", "lexicon.json")
_lock = threading.Lock()
_lexicon: dict[str, dict] | None = None

# Romanised Hindi function words: dropped before transliteration (exact list, not a model call).
ROMAN_STOPWORDS = set(
    """ka ki ke ko se me mein mai main mei mien hai hain h he hy hei ha tha thi the thy kya kyaa kia
    kaun kon koun kaunsa konsa kaunse konse kis kisne kisko kise kab kaha kahan kaise kese kyu kyun kyon
    kitna kitni kitne aur or ya bhi hi to pe par tak wala wali wale vala vali vale ek hota hoti hote hua
    hui hue huaa hue ne jo""".split()
)


def detect_script(token: str) -> str:
    if any("ऀ" <= c <= "ॿ" for c in token):
        return "deva"
    if any("a" <= c.lower() <= "z" for c in token):
        return "latin"
    return "other"


# ---------------------------------------------------------------- LLM lexicon
LEXICON_PROMPT = """You are a Hindi-English lexicon for a search engine. The tokens come from
search queries typed in romanised Hindi mixed with English. For EACH token decide:
- "english": true if the token is an English word (or English abbreviation) as used in the query,
  false if it is a romanised Hindi word or a name.
- "hindi": if english is true, the 1-2 most common Hindi equivalents in Devanagari as written on
  Hindi Wikipedia (e.g. "religion" -> ["धर्म"], "leader" -> ["नेता"]); otherwise [].
- "deva": the token written in Devanagari script (transliteration, not translation).
Reply JSON only: {"items": [{"w": "...", "english": true, "hindi": ["..."], "deva": "..."}]}"""


def _load_lexicon() -> dict[str, dict]:
    global _lexicon
    if _lexicon is None:
        _lexicon = json.loads(LEXICON_PATH.read_text("utf-8")) if LEXICON_PATH.exists() else {}
    return _lexicon


def _lexicon_batch(words: list[str]) -> dict[str, dict]:
    # Judgment: is this Latin token English or romanised Hindi, and what Hindi word means the
    # same? Needs world knowledge (no exact rule), hence a model call.
    cfg = load_config()["llm"]
    out = parse_json(chat([{"role": "system", "content": LEXICON_PROMPT},
                           {"role": "user", "content": json.dumps({"tokens": words})}],
                          model=cfg["normalise_model"], reasoning_effort="low"))
    res = {}
    for it in out.get("items", []):
        w = str(it.get("w", "")).lower()
        if w in words:
            hindi = [h for h in it.get("hindi") or [] if isinstance(h, str) and h.strip()]
            res[w] = {"english": bool(it.get("english")), "hindi": hindi[:2],
                      "deva": str(it.get("deva") or "")}
    return res


def lexicon(words: list[str], batch: int = 40) -> dict[str, dict]:
    lex = _load_lexicon()
    todo = sorted({w for w in words if w not in lex})
    if todo:
        from concurrent.futures import ThreadPoolExecutor

        chunks = [todo[i:i + batch] for i in range(0, len(todo), batch)]
        with ThreadPoolExecutor(2) as ex:
            for got in ex.map(_lexicon_batch, chunks):
                with _lock:
                    lex.update(got)
        missing = [w for w in todo if w not in lex]
        for w in missing:  # model skipped some: ask one at a time
            lex.update(_lexicon_batch([w]) or {w: {"english": False, "hindi": [], "deva": ""}})
        with _lock:
            LEXICON_PATH.write_text(json.dumps(lex, ensure_ascii=False, indent=0), "utf-8")
    return {w: lex.get(w, {"english": False, "hindi": [], "deva": ""}) for w in words}


def transliterate(words: list[str]) -> dict[str, list[str]]:
    """Cached IndicXlit output first (shipped, so results reproduce without .venv-xlit);
    misses go to IndicXlit if installed, else to the LLM lexicon's 'deva' field."""
    out = xlit.cached(words)
    misses = [w for w in words if w not in out]
    if misses:
        if xlit.available():
            out.update(xlit.transliterate(misses))
        else:
            out.update({w: [e["deva"]] if e["deva"] else [] for w, e in lexicon(misses).items()})
    return {w: out[w] for w in words}


def prefetch(queries: list[str], cfg: dict) -> None:
    """Batch all Latin tokens of many queries through the (cached) backends up front."""
    from src.text import tokenize

    words = sorted({t for q in queries for t in tokenize(q) if detect_script(t) == "latin"})
    content = [w for w in words if w not in ROMAN_STOPWORDS]
    if cfg.get("translit"):
        transliterate(content)
    if cfg.get("expansion"):
        lexicon(content)


# ---------------------------------------------------------------- per token
def _phrase_df(phrase: str, df) -> int:
    """df of a (possibly multi-word) expansion: its rarest word."""
    from src.text import tokenize

    return min((df(w) or 0 for w in tokenize(phrase)), default=0)


def gate_expansion(translit: str | None, hindi: list[str], cfg: dict, df=None) -> tuple[list[str], bool]:
    """Exact rules deciding which Hindi equivalents to add (both off by default, tuned on train):
    expansion_dedupe     - drop an equivalent identical to the transliteration (loanwords:
                           film -> फिल्म) so the same term is not counted twice
    expansion_gate_ratio - drop all equivalents if df(translit) >= ratio * df(best equivalent):
                           the token already matches a well-attested Devanagari word, so it is
                           more likely a name / loanword / romanised Hindi than English to translate
    Returns (kept equivalents, gated)."""
    if cfg.get("expansion_dedupe") and translit:
        hindi = [h for h in hindi if h != translit]
    ratio = cfg.get("expansion_gate_ratio") or 0
    if ratio and df is not None and translit and hindi:
        if (df(translit) or 0) >= ratio * max(_phrase_df(h, df) for h in hindi):
            return [], True
    return hindi, False


def normalise_token(tok: str, cfg: dict, df=None) -> dict:
    """Per-token trace + weighted Devanagari/Latin terms it contributes to the query.
    df: document frequency lookup of the main index (only the expansion gate uses it)."""
    script = detect_script(tok)
    info = {"token": tok, "script": script, "translit": None, "english": None,
            "expansion": [], "terms": [(tok, 1.0)]}
    if script != "latin" or not (cfg.get("translit") or cfg.get("expansion")):
        return info
    if cfg.get("stopwords", True) and tok in ROMAN_STOPWORDS:
        info["terms"] = []
        info["dropped"] = "roman stopword"
        return info
    terms: list[tuple[str, float]] = []
    keep_latin = 1.0
    if cfg.get("translit"):
        try:
            cands = transliterate([tok])[tok]
        except Exception as e:  # noqa: BLE001 - demo must not crash on a backend failure
            cands, info["warning"] = [], f"transliteration unavailable ({type(e).__name__})"
        if cands:
            info["translit"] = cands[0]
            terms.append((cands[0], 1.0))
            if cfg.get("translit_top2_weight", 0) and len(cands) > 1:
                terms.append((cands[1], cfg["translit_top2_weight"]))
            keep_latin = cfg.get("latin_keep_weight", 1.0)
    if cfg.get("expansion"):
        try:
            e = lexicon([tok])[tok]
        except Exception as ex:  # noqa: BLE001
            e = {"english": None, "hindi": [], "deva": ""}
            info["warning"] = f"expansion unavailable ({type(ex).__name__})"
        info["english"] = e["english"]
        if e["english"]:
            hindi, gated = gate_expansion(info["translit"], e["hindi"], cfg, df)
            if gated:
                info["gated"] = True
            info["expansion"] = hindi
            terms += [(h, cfg.get("expansion_weight", 0.5)) for h in hindi]
            keep_latin = max(keep_latin, cfg.get("english_keep_weight", 1.0))
    if keep_latin:
        terms.append((tok, keep_latin))
    info["terms"] = terms
    return info


def to_devanagari(query: str) -> str:
    """Whole-query transliteration (stop words included) - input for the dense encoder."""
    from src.text import tokenize

    toks = tokenize(query)
    lat = [t for t in toks if detect_script(t) == "latin"]
    tr = transliterate(lat) if lat else {}
    return " ".join((tr.get(t) or [t])[0] if detect_script(t) == "latin" else t for t in toks)
