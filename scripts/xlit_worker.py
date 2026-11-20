"""IndicXlit worker. Runs inside .venv-xlit (Python 3.10 + fairseq).

Protocol: one JSON object per stdin line {"words": [...]} -> one stdout line
{"out": {word: [top-k Devanagari candidates]}}. Prints {"ready": true} first.
"""
import json
import os
import sys

# The official AI4Bharat checkpoint pickles argparse.Namespace; torch>=2.6 refuses
# that under weights_only=True. We trust this source (see docs/adr/0002).
os.environ.setdefault("TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD", "1")
_stdout = sys.stdout
sys.stdout = sys.stderr  # the library prints progress; keep protocol channel clean

from ai4bharat.transliteration import XlitEngine  # noqa: E402

engine = XlitEngine("hi", beam_width=4, rescore=False, src_script_type="roman")
_stdout.write(json.dumps({"ready": True}) + "\n")
_stdout.flush()
for line in sys.stdin:
    words = json.loads(line)["words"]
    out = {}
    for i in range(0, len(words), 64):
        chunk = words[i:i + 64]
        try:
            # returns [flat list] with topk candidates per word, in input order
            flat = engine.batch_transliterate_words(chunk, "en", "hi", topk=2)[0]
            if len(flat) != 2 * len(chunk):
                raise ValueError("unexpected batch shape")
            for j, w in enumerate(chunk):
                out[w] = flat[2 * j: 2 * j + 2]
        except Exception:  # fall back to per-word on any batch failure
            for w in chunk:
                try:
                    out[w] = engine.translit_word(w, topk=2)["hi"]
                except Exception as e:  # noqa: BLE001
                    out[w] = []
                    print("xlit error", w, e, file=sys.stderr)
    _stdout.write(json.dumps({"out": out}, ensure_ascii=False) + "\n")
    _stdout.flush()
