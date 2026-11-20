"""Streamlit demo: baseline BM25 vs a chosen system, side by side.

    streamlit run app.py            # sample corpus
    HIR_MODE=full streamlit run app.py
"""
import os

import streamlit as st

from src.engine import ALL_SYSTEMS, Engine

st.set_page_config(page_title="Hinglish IR", layout="wide")
MODE = os.environ.get("HIR_MODE", "sample")
EXAMPLES = [
    "roth ira pe tax kitna lagta hai",
    "pakistan mein konsa religion sabse bada hai",
    "google ki khoj kisne ki thi",
    "pratham vishv yuddh kab hua tha",
    "Elon Musk ka birth kab hua",
    "भगत सिंह की मृत्यु कब हुई थी",
]


@st.cache_resource(show_spinner="Loading index (first run only)...")
def engine(mode: str) -> Engine:
    return Engine(mode)


def show_results(res: dict, explain: bool):
    q = res["repr"]
    st.markdown(f"**Normalised query:** `{q.normalised_text() or '(empty)'}`")
    for w in res["warnings"]:
        st.warning(w)
    if not res["hits"]:
        st.info("No results.")
    for i, h in enumerate(res["hits"], 1):
        with st.container(border=True):
            st.markdown(f"**{i}. {h['title']}**  \n`{h['docid']}` · score {h['score']:.3f}")
            st.write(h["text"][:400] + ("..." if len(h["text"]) > 400 else ""))
            if explain and h["terms"]:
                top = sorted(h["terms"].items(), key=lambda x: -x[1])[:8]
                st.caption("term scores: " + ", ".join(f"{t} = {c:.2f}" for t, c in top))


st.title("Hinglish → Hindi retrieval")
st.caption(f"MIRACL-hi ({MODE} corpus). Type in Devanagari, romanised Hindi, or Hindi-English mix.")

c1, c2, c3 = st.columns([5, 2, 1])
with c1:
    example = st.selectbox("Example queries", [""] + EXAMPLES, index=0)
    query = st.text_input("Search", value=example or "roth ira pe tax kitna lagta hai")
with c2:
    system = st.selectbox("System (right column)", ALL_SYSTEMS, index=ALL_SYSTEMS.index("full"))
with c3:
    k = st.number_input("Top k", 1, 20, 5)
    explain = st.checkbox("Explain", value=True)

if query.strip():
    try:
        eng = engine(MODE)
        with st.spinner("Searching..."):
            base = eng.search(query, "bm25", k=int(k), explain=explain)
            ours = eng.search(query, system, k=int(k), explain=explain)
    except Exception as e:  # keep the demo alive and show what failed
        st.error(f"Search failed: {type(e).__name__}: {e}")
        st.stop()

    with st.expander("Per-token analysis", expanded=True):
        rows = [{"token": t["token"], "script": t["script"],
                 "transliteration": t.get("translit") or "",
                 "English?": "" if t.get("english") is None else ("yes" if t["english"] else "no"),
                 "Hindi expansion": "/".join(t.get("expansion") or []),
                 "note": t.get("dropped", "")}
                for t in ours["repr"].tokens]
        st.dataframe(rows, use_container_width=True, hide_index=True)

    left, right = st.columns(2)
    with left:
        st.subheader("Baseline: BM25")
        show_results(base, explain)
    with right:
        st.subheader(f"System: {system}")
        show_results(ours, explain)
