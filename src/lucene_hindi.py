"""Port of Lucene's HindiAnalyzer, to test whether it explains our gap to the MIRACL BM25 baseline.

Chain (HindiAnalyzer.createComponents, Lucene main): tokenizer -> lower case -> decimal digits
-> IndicNormalizer -> HindiNormalizer -> StopFilter(stopwords.txt) -> HindiStemmer.
Rules are copied from the Lucene sources (Apache-2.0):
  analysis/in/IndicNormalizer.java, analysis/hi/{HindiNormalizer,HindiStemmer}.java,
  analysis/hi/stopwords.txt
Tokenisation uses our tokenizer (src/text.py), not Lucene's StandardTokenizer (UAX#29).
"""
from __future__ import annotations

from src import text

# IndicNormalizer, Devanagari entries: (first, second, third or None) -> composed
_COMPOSE = [
    ("अ", "ा", "ॅ", "ऑ"), ("अ", "ा", "ॆ", "ऒ"), ("अ", "ा", "े", "ओ"), ("अ", "ा", "ै", "औ"),
    ("अ", "ा", None, "आ"), ("अ", "ॅ", None, "ॲ"), ("अ", "ॆ", None, "ऄ"), ("अ", "ॉ", None, "ऑ"),
    ("अ", "ॊ", None, "ऒ"), ("अ", "ो", None, "ओ"), ("अ", "ौ", None, "औ"),
    ("आ", "ॅ", None, "ऑ"), ("आ", "ॆ", None, "ऒ"), ("आ", "े", None, "ओ"), ("आ", "ै", None, "औ"),
    ("उ", "ु", None, "ऊ"), ("ए", "ॅ", None, "ऍ"), ("ए", "ॆ", None, "ऎ"), ("ए", "े", None, "ऐ"),
    ("क", "़", None, "क़"), ("ख", "़", None, "ख़"), ("ग", "़", None, "ग़"),
    ("ज", "़", None, "ज़"), ("ड", "़", None, "ड़"), ("ढ", "़", None, "ढ़"),
    ("न", "़", None, "ऩ"), ("फ", "़", None, "फ़"), ("य", "़", None, "य़"),
    ("र", "़", None, "ऱ"), ("ळ", "़", None, "ऴ"),
    ("ा", "ॅ", None, "ॉ"), ("ा", "ॆ", None, "ॊ"), ("ा", "े", None, "ो"), ("ा", "ै", None, "ौ"),
]
_FIRST = {c for c, *_ in _COMPOSE}


def _deva(c: str) -> bool:
    return "ऀ" <= c <= "ॿ"


def indic_compose(s: str) -> str:
    out, i = list(s), 0
    while i < len(out):
        if out[i] in _FIRST and i + 1 < len(out) and _deva(out[i + 1]):
            nxt2 = out[i + 2] if i + 2 < len(out) and (_deva(out[i + 2]) or out[i + 2] == "‍") else None
            for a, b, c, res in _COMPOSE:
                if a == out[i] and b == out[i + 1] and (c is None or c == nxt2):
                    out[i] = res
                    del out[i + 1:i + (3 if c is not None else 2)]
                    break
        i += 1
    return "".join(out)


_HINDI_MAP = str.maketrans({
    # nukta letters -> base
    "ऩ": "न", "ऱ": "र", "ऴ": "ळ", "क़": "क",
    "ख़": "ख", "ग़": "ग", "ज़": "ज", "ड़": "ड",
    "ढ़": "ढ", "फ़": "फ", "य़": "य",
    # candrabindu -> anusvara
    "ँ": "ं",
    # chandra / short vowels
    "ॅ": "े", "ॆ": "े", "ॉ": "ो", "ॊ": "ो",
    "ऍ": "ए", "ऎ": "ए", "ऑ": "ओ", "ऒ": "ओ",
    "ॲ": "अ",
    # long -> short independent vowels
    "आ": "अ", "ई": "इ", "ऊ": "उ", "ॠ": "ऋ",
    "ॡ": "ऌ", "ऐ": "ए", "औ": "ओ",
    # long -> short dependent vowels
    "ी": "ि", "ू": "ु", "ॄ": "ृ", "ॣ": "ॢ",
    "ै": "े", "ौ": "ो",
    # deleted: nukta, ZWJ, ZWNJ (virama handled below, after the dead-na rule)
    "़": None, "‍": None, "‌": None,
})


def hindi_normalise(s: str) -> str:
    out = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == "न" and i + 1 < len(s) and s[i + 1] == "्":  # dead na -> anusvara
            out.append("ं")
            i += 2
            continue
        out.append(c)
        i += 1
    # the remaining rules are context-free single-character maps / deletions
    return "".join(out).translate(_HINDI_MAP).replace("्", "")


_BUCKETS = [  # (min length exclusive, suffixes of exactly that removal length)
    (6, "ाएंगी ाएंगे ाऊंगी ाऊंगा ाइयाँ ाइयों ाइयां"),
    (5, "ाएगी ाएगा ाओगी ाओगे एंगी ेंगी एंगे ेंगे ूंगी ूंगा ातीं नाओं नाएं ताओं ताएं ियाँ ियों ियां"),
    (4, "ाकर ाइए ाईं ाया ेगी ेगा ोगी ोगे ाने ाना ाते ाती ाता तीं ाओं ाएं ुओं ुएं ुआं"),
    (3, "कर ाओ िए ाई ाए ने नी ना ते ीं ती ता ाँ ां ों ें"),
    (2, "ो े ू ु ी ि ा"),
]
_BUCKETS = [(n, tuple(sfx.split())) for n, sfx in _BUCKETS]


def stem(tok: str) -> str:
    for min_len, suffixes in _BUCKETS:
        if len(tok) > min_len and tok.endswith(suffixes):
            return tok[: -len(suffixes[0])]
    return tok


STOPWORDS = set("""
अंदर अत अपना अपनी अपने अभी आदि आप इत्यादि इन इनका इन्हीं इन्हें इन्हों इस इसका इसकी इसके इसमें इसी इसे
उन उनका उनकी उनके उनको उन्हीं उन्हें उन्हों उस उसके उसी उसे एक एवं एस ऐसे और कई कर करता करते करना करने
करें कहते कहा का काफ़ी कि कितना किन्हें किन्हों किया किर किस किसी किसे की कुछ कुल के को कोई कौन कौनसा गया
घर जब जहाँ जा जितना जिन जिन्हें जिन्हों जिस जिसे जीधर जैसा जैसे जो तक तब तरह तिन तिन्हें तिन्हों तिस तिसे
तो था थी थे दबारा दिया दुसरा दूसरे दो द्वारा न नहीं ना निहायत नीचे ने पर पहले पूरा पे फिर बनी बही बहुत
बाद बाला बिलकुल भी भीतर मगर मानो मे में यदि यह यहाँ यही या यिह ये रखें रहा रहे ऱ्वासा लिए लिये लेकिन
व वर्ग वह वहाँ वहीं वाले वुह वे वग़ैरह संग सकता सकते सबसे सभी साथ साबुत साभ सारा से सो ही हुआ हुई हुए
है हैं हो होता होती होते होना होने
अपनि जेसे होति सभि तिंहों इंहों दवारा इसि किंहें थि उंहों ओर जिंहें वहिं अभि बनि हि उंहिं उंहें हें
वगेरह एसे रवासा कोन निचे काफि उसि पुरा भितर हे बहि वहां कोइ यहां जिंहों तिंहें किसि कइ यहि इंहिं जिधर
इंहें अदि इतयादि हुइ कोनसा इसकि दुसरे जहां अप किंहों उनकि भि वरग हुअ जेसा नहिं
""".split())  # Lucene compares the normalised token against this raw list (as in Lucene)


def analyse(s: str) -> list[str]:
    toks = (hindi_normalise(indic_compose(t)) for t in text.tokenize(s))
    return [stem(t) for t in toks if t and t not in STOPWORDS]
