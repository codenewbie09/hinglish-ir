"""Roman -> Devanagari transliteration with a persistent cache.

Backend 1: AI4Bharat IndicXlit in a separate Python 3.10 venv (.venv-xlit), driven
as a subprocess (fairseq does not install on the main Python).
Backend 2 (fallback): LLM transliteration, see src/normalise.py.
"""
from __future__ import annotations

import json
import subprocess
import threading

from src.config import ROOT, path

CACHE_PATH = path("data", "cache", "xlit.json")
XLIT_PY = ROOT / ".venv-xlit" / "bin" / "python"
_lock = threading.Lock()
_cache: dict[str, list[str]] | None = None
_proc: subprocess.Popen | None = None


def available() -> bool:
    return XLIT_PY.exists()


def _load() -> dict[str, list[str]]:
    global _cache
    if _cache is None:
        _cache = json.loads(CACHE_PATH.read_text("utf-8")) if CACHE_PATH.exists() else {}
    return _cache


def _save() -> None:
    CACHE_PATH.write_text(json.dumps(_cache, ensure_ascii=False, indent=0), "utf-8")


def _worker() -> subprocess.Popen:
    global _proc
    if _proc is None or _proc.poll() is not None:
        _proc = subprocess.Popen(
            [str(XLIT_PY), str(ROOT / "scripts" / "xlit_worker.py")],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, encoding="utf-8", cwd=ROOT,
        )
        ready = json.loads(_proc.stdout.readline())
        assert ready.get("ready"), ready
    return _proc


def transliterate(words: list[str]) -> dict[str, list[str]]:
    """Top-2 Devanagari candidates per romanised word ([] if no backend can do it)."""
    cache = _load()
    with _lock:
        todo = sorted({w for w in words if w not in cache})
        if todo and available():
            p = _worker()
            p.stdin.write(json.dumps({"words": todo}) + "\n")
            p.stdin.flush()
            cache.update(json.loads(p.stdout.readline())["out"])
            _save()
    return {w: cache.get(w, []) for w in words}
