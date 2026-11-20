# Merge to main without the author's summary (principle 8 exception)
Date: 2026-11-20 · Status: accepted

## Context
Principle 8 requires a 3–5 line summary, in the author's own words, before anything merges
to `main`, checked against the diff. The first full version of the project (`build` at
`e69fc21`: data, index, BM25, normalisation, dense, fusion, eval, demo, results) was ready
with the course deadline about 24 hours away.

## Decision
At the author's explicit request, `build` was fast-forwarded into `main` at `e69fc21`
without the summary. This is a one-off exception; the principle itself is unchanged.

## Consequences
- Easier: the reviewable state is on `main` now, before the deadline.
- Harder: nothing on `main` shows that the author can explain this change, which is the
  risk principle 8 guards against (reviews, interviews, the course viva).
- Follow-up: write the summary after the deadline and record it here. The README
  "Key findings" and ADRs 0001–0003 are the starting points.
- Revisit if exceptions repeat: then the rule, or the deadline planning, needs changing.
