"""Provider-agnostic LLM wrapper (OpenAI-compatible chat API) with a permanent cache.

Every response is cached in data/cache/llm.jsonl keyed by (model, messages,
temperature), so re-running never re-calls the API. Callers must say what
judgment the model is making (see PRINCIPLES #4); code does everything exact.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import threading
import time

import requests
from dotenv import load_dotenv

from src.config import load_config, path

load_dotenv()

PROVIDERS = {
    "groq": ("https://api.groq.com/openai/v1", "GROQ_API_KEY"),
    "openai": ("https://api.openai.com/v1", "OPENAI_API_KEY"),
    "together": ("https://api.together.xyz/v1", "TOGETHER_API_KEY"),
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
}
CACHE_PATH = path("data", "cache", "llm.jsonl")
_lock = threading.Lock()
_cache: dict[str, str] | None = None


def _load_cache() -> dict[str, str]:
    global _cache
    if _cache is None:
        _cache = {}
        if CACHE_PATH.exists():
            with open(CACHE_PATH, encoding="utf-8") as f:
                for line in f:
                    rec = json.loads(line)
                    _cache[rec["key"]] = rec["response"]
    return _cache


def _key(model, messages, temperature) -> str:
    blob = json.dumps([model, messages, temperature], ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()


def chat(messages: list[dict], model: str, temperature: float = 0.0, json_mode=True,
         offline: bool = False, **extra) -> str:
    """`extra` (e.g. reasoning_effort) is sent to the API but is not part of the cache key."""
    key = _key(model, messages, temperature)
    cache = _load_cache()
    if key in cache:
        return cache[key]
    if offline or os.environ.get("HIR_OFFLINE"):
        raise LookupError("LLM cache miss in offline mode")
    provider = load_config()["llm"]["provider"]
    base, key_env = PROVIDERS[provider]
    base = os.environ.get("LLM_BASE_URL", base)
    api_key = os.environ.get(os.environ.get("LLM_API_KEY_ENV", key_env))
    if not api_key:
        raise RuntimeError(f"set {key_env} in .env (provider {provider})")
    body = {"model": model, "messages": messages, "temperature": temperature, **extra}
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    for attempt in range(8):
        r = requests.post(f"{base}/chat/completions", json=body, timeout=180,
                          headers={"Authorization": f"Bearer {api_key}"})
        if r.status_code == 429 or r.status_code >= 500:
            wait = float(r.headers.get("retry-after", 2 ** attempt))
            time.sleep(min(wait, 60))
            continue
        if r.status_code == 400 and json_mode and "json" in r.text.lower():
            body.pop("response_format", None)  # model produced invalid JSON; retry free-form
            continue
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
        with _lock:
            cache[key] = content
            with open(CACHE_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps({"key": key, "model": model, "response": content},
                                   ensure_ascii=False) + "\n")
        return content
    raise RuntimeError(f"LLM call failed after retries: {r.status_code} {r.text[:200]}")


def parse_json(s: str) -> dict:
    """Best-effort JSON object parse; {} if the model returned something unusable."""
    for cand in (s, (re.search(r"\{.*\}", s, re.S) or [None])[0]):
        if cand:
            try:
                obj = json.loads(cand)
                return obj if isinstance(obj, dict) else {}
            except json.JSONDecodeError:
                pass
    return {}
