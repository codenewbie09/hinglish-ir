"""Query normalisation: script detection (more components added in stage 3)."""
from __future__ import annotations


def detect_script(token: str) -> str:
    if any("ऀ" <= c <= "ॿ" for c in token):
        return "deva"
    if any("a" <= c.lower() <= "z" for c in token):
        return "latin"
    return "other"


def normalise_token(tok: str, cfg: dict) -> dict:
    """Return the per-token trace and the weighted terms it contributes."""
    script = detect_script(tok)
    info = {"token": tok, "script": script, "terms": [(tok, 1.0)]}
    return info
