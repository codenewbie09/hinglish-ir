# 5. Per-query expansion gate: dedupe yes, df gate no

Status: accepted (2026-11-22)

## Context
The ablation showed bilingual expansion hurting pure-roman queries on the full corpus.
Looking at the Latin tokens the lexicon tags as English in roman dev queries, two causes
showed up:
- loanwords and names whose Hindi "equivalent" *is* their transliteration
  (film → फिल्म, cricket → क्रिकेट), so expansion counts the same term twice;
- wrong senses from the context-free lexicon (congress → संसद, us → हम, star → तारा).

## Options (both exact code, no extra model call; `src/normalise.py:gate_expansion`)
1. **Dedupe**: drop an equivalent identical to the transliteration.
2. **df gate**: drop all equivalents when df(transliteration) ≥ r · df(best equivalent).
   The idea: if the transliteration is already a common Devanagari word, the token is a
   name, a loanword or romanised Hindi, not English that needs translating.
3. A model call per query to decide. Rejected: a second judgment from the same family of
   models that makes the lexicon errors, plus the cost and latency.

## Decision
Both rules were tuned on the 400 train queries (sample index, same objective as ADR 0003:
mean nDCG@10 over native/roman/mix25/mix50/mix75), grid r ∈ {off, 0.1, 0.25, 0.5, 1, 2}
× dedupe on/off (`results/tuning_gate_sample.csv`). The rule for picking, fixed before
looking at dev: the simplest setting within 0.001 of the best.
- Dedupe: 0.4125 → 0.4182 on train, better on every non-native level. **Adopted.**
- df gate: every r below 2 is worse. r = 2 is +0.0007 over dedupe alone, at the edge of
  the grid, where the gate is already close to off. **Not adopted** (negative result).

The new systems `full+gate` and `hybrid+gate` sit next to `full` and `hybrid`. The
original systems are unchanged, so earlier numbers stay comparable.

## Consequences
- Results on dev: see the README (key findings) and `significance_*.csv`
  (`full+gate` vs `full`, `hybrid+gate` vs `hybrid`).
- It does not fix the wrong-sense cases (congress → संसद). That needs context, i.e. a
  query-level judgment, which is still open.
