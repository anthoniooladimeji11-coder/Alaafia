# brief/ — the brief generator

First cut at `DELIVER`. Turns the model's output into the actual shape
revenue line #1 sells: a state's full modelled profile — every
indicator against the national figure, ranked among the other states,
sourced and margin-of-error'd throughout. Up to now the estimates only
existed as parquet files and a browsing tool; this is the first thing
built here that's an actual document, not a dataset.

**No invented commentary.** Every sentence in a brief is an f-string
template filled from real numbers (`render.py`'s module docstring) —
never a model asked to "write something about this state." If you want
narrative prose on top of these numbers later, that's a distinct
`NARRATE` step with its own review, not something to fold in here
silently.

## Run it

```bash
cd platform/brief
uv sync
uv run brief states                    # list state pcodes
uv run brief generate NG021             # one brief -> build/NG021.html
uv run brief generate-all               # all 37 -> build/
uv run pytest
```

`build/*.html` are committed — each is a small (~20 KB), fully
self-contained deliverable someone can open or send without touching
this repo again.

## What's in a brief

- **Headline strip** — the 3 biggest concerns and 3 biggest strengths
  vs. the national figure, direction-aware (a high number is only a
  "concern" if high is actually bad for that indicator).
- **Every indicator, by domain** — state estimate + 95% interval,
  national figure, signed delta, rank among the other states that
  indicator could be fitted for (not always 37 — see below), and
  whether the margin of error came from the survey's own published CI
  or an approximation.
- **A methods section** that says plainly what a Fay–Herriot estimate
  is and points at `platform/model/README.md` for the rest.

## Honesty details worth knowing

- **The rank denominator isn't always 37.** `diarrhoea_ors_rhf` only
  had enough state coverage in 28 states this round — a state's rank
  for it reads "28th of 28", never silently "/37".
- **A missing national comparison shows as "—", never a fabricated
  number.** `women_literate` has no national row in the DHS API's
  NG2024DHS pull even though 37 states have their own estimate — the
  brief shows the state figure and rank, and leaves delta/national
  blank rather than guessing.
- **`indicator_meta.parquet`** (which slug is "higher is worse" vs.
  "higher is better") now lives in `platform/model/` itself, written
  by `sae build` — both this package and the estimates explorer read
  the same file instead of keeping their own copies that could drift
  apart.

## Not built yet

Per-LGA briefs (same shape, one level down — straightforward once
wanted), a PDF export (the HTML prints reasonably via the browser's
own print dialog already), and the `NARRATE` step proper (grounded
prose generation with its own fact-checking pass, not a template).
