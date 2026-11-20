"""Hindi text processing: Unicode normalisation, tokenisation, stop words, light stemmer.

Each step is a pure function so callers can toggle it (see `process`).
"""
from __future__ import annotations

import re
import unicodedata

_ZW = dict.fromkeys(map(ord, "​‌‍﻿"), None)
_DEVA_DIGITS = {ord(c): str(i) for i, c in enumerate("०१२३४५६७८९")}
# Devanagari letters + combining signs (no danda U+0964/0965, no Devanagari digits).
_TOKEN_RE = re.compile(r"[ऀ-ॣॱ-ॿ]+|[a-z0-9]+")


def normalise(text: str) -> str:
    """NFC, drop zero-width joiners, Devanagari digits -> ASCII, lowercase Latin."""
    text = unicodedata.normalize("NFC", text).translate(_ZW).translate(_DEVA_DIGITS)
    return text.lower()


def tokenize(text: str, normalise_first: bool = True) -> list[str]:
    if normalise_first:
        text = normalise(text)
    return _TOKEN_RE.findall(text)


HINDI_STOPWORDS = set(
    """अंदर अत अदि अप अपना अपनि अपनी अपने अभि अभी आदि आप इंहिं इंहें इंहों इतयादि इत्यादि इन इनका
    इन्हीं इन्हें इन्हों इस इसका इसकि इसकी इसके इसमें इसि इसी इसे उंहिं उंहें उंहों उन उनका उनकि उनकी उनके
    उनको उन्हीं उन्हें उन्हों उस उसके उसि उसी उसे एक एवं एस ऐसे और कई करता करते करना करने करें कहते कहा
    का काफ़ी कि किंहें किंहों कितना किन्हें किन्हों किया किर किस किसि किसी किसे की कुछ कुल के को कोइ कोई कोन
    कोनसा कौन कौनसा गया घर जब जहाँ जहां जा जिंहें जिंहों जितना जिधर जिन जिन्हें जिन्हों जिस जिसे जीधर जेसा
    जेसे जैसा जैसे जो तक तब तरह तिंहें तिंहों तिन तिन्हें तिन्हों तिस तिसे तो था थि थी थे दबारा दवारा दिया
    दुसरा दुसरे दूसरे दो द्वारा न नहिं नहीं ना निचे निहायत नीचे ने पर पहले पुरा पूरा पे फिर बनि बनी बहि बही
    बहुत बाद बाला बिलकुल भि भितर भी भीतर मगर मानो मे में यदि यह यहाँ यहां यहि यही या यिह ये रखें रवासा
    रहा रहे ऱ्वासा लिए लिये लेकिन व वगेरह वरग वर्ग वह वहाँ वहां वहिं वहीं वाले वुह वे वग़ैरह संग सकता सकते
    सबसे सभि सभी साथ साबुत साभ सारा से सो हि ही हुअ हुआ हुइ हुई हुए हे हें है हैं हो होता होति होती होते होना
    होने क्या किसने कब कहाँ कैसे क्यों""".split()
)
ENGLISH_STOPWORDS = set(
    """a an the of in on at to for from by with and or is are was were be been what which who whom
    when where why how does do did it its this that these those as""".split()
)
STOPWORDS = {normalise(w) for w in HINDI_STOPWORDS} | ENGLISH_STOPWORDS


def remove_stopwords(tokens: list[str]) -> list[str]:
    return [t for t in tokens if t not in STOPWORDS]


# Light suffix stripper after Ramanathan & Rao (2003): longest matching suffix
# is removed if at least 2 characters of stem remain. Applied to Devanagari only.
_SUFFIXES = sorted(
    """ा ि ी ु ू े ो ं ों ें ाँ ां ियाँ ियां ियों िया ाओं ाएं ाएँ ाओ ाए ाइ ाई ाया ायी ाये ेगा ेगी ेंगे ेंगी ूँगा ूंगा
    ूँगी ूंगी ाऊँगा ाऊंगा ाएगा ाएगी ाएंगे ाएँगे ता ती ते ना नी ने कर ाकर ाता ाती ाते ाना ानी ाने ाव ावट
    ाहट ापन पन वाला वाले वाली ाइयाँ ाइयां ाइयों ीय ीयों िक ित ीकरण करण ता ओं एं""".split(),
    key=len,
    reverse=True,
)


def stem(token: str) -> str:
    if not ("ऀ" <= token[:1] <= "ॿ"):
        return token
    for suf in _SUFFIXES:
        if token.endswith(suf) and len(token) - len(suf) >= 2:
            return token[: -len(suf)]
    return token


def process(text: str, *, normalise_text=True, stopwords=True, stemming=False) -> list[str]:
    toks = tokenize(text, normalise_first=normalise_text)
    if stopwords:
        toks = remove_stopwords(toks)
    if stemming:
        toks = [stem(t) for t in toks]
    return toks
