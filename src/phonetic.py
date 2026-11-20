"""Soundex-style phonetic key for Hindi, computed on the Devanagari form.

Merges what romanised typing and transliteration routinely confuse:
vowel length (ि/ी, ु/ू), e/ai and o/au, nasalisation (ं ँ and half-nasal
consonants), aspiration (ख->क, भ->ब ...), nukta, retroflex/dental t/d/n,
and the three sibilants. Consecutive duplicate codes collapse.
"""
from __future__ import annotations

import unicodedata

_CONS = {
    "क": "k", "ख": "k", "ग": "g", "घ": "g", "ङ": "n",
    "च": "c", "छ": "c", "ज": "j", "झ": "j", "ञ": "n",
    "ट": "t", "ठ": "t", "ड": "d", "ढ": "d", "ण": "n",
    "त": "t", "थ": "t", "द": "d", "ध": "d", "न": "n",
    "प": "p", "फ": "p", "ब": "b", "भ": "b", "म": "m",
    "य": "y", "र": "r", "ल": "l", "व": "v", "ळ": "l",
    "श": "s", "ष": "s", "स": "s", "ह": "h",
}
_VOWELS = {  # independent vowels and matras
    "अ": "a", "आ": "a", "ा": "",
    "इ": "i", "ई": "i", "ि": "i", "ी": "i",
    "उ": "u", "ऊ": "u", "ु": "u", "ू": "u",
    "ए": "e", "ऐ": "e", "े": "e", "ै": "e",
    "ओ": "o", "औ": "o", "ो": "o", "ौ": "o",
    "ऋ": "r", "ृ": "r", "ऑ": "o", "ॉ": "o", "ॅ": "e",
}
_DROP = set("ंँः़्ऽ")
_NASALS = set("नमणङञ")
_VIRAMA = "्"


def _deva_key(word: str) -> str:
    chars = list(unicodedata.normalize("NFD", word))
    out: list[str] = []
    for i, ch in enumerate(chars):
        nxt = chars[i + 1] if i + 1 < len(chars) else ""
        nxt2 = chars[i + 2] if i + 2 < len(chars) else ""
        # half nasal before a consonant (हिन्दी) behaves like anusvara (हिंदी)
        if ch in _NASALS and nxt == _VIRAMA and nxt2 in _CONS:
            continue
        if ch in _DROP:
            continue
        code = _CONS.get(ch) or _VOWELS.get(ch)
        if code is None:
            continue
        if code and (not out or out[-1] != code):
            out.append(code)
    return "".join(out)


def _latin_key(word: str) -> str:
    word = word.lower()
    out = [word[:1]] if word else []
    for ch in word[1:]:
        if ch in "aeiouyhw":
            continue
        if out[-1] != ch:
            out.append(ch)
    return "L" + "".join(out)


def phonetic_key(token: str) -> str:
    if any("ऀ" <= c <= "ॿ" for c in token):
        return "P" + _deva_key(token)
    return _latin_key(token)
