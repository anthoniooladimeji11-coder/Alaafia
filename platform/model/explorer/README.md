# explorer/ — the estimates explorer

The model's output, browsable: pick any of the 22 modelled indicators,
see it choropleth'd across 37 states, drill into one to see its 774
LGAs. Every view shows the direct survey figure next to the modelled
one, the margin of error, and — at LGA level — an unmissable banner
that these are synthetic, not locally measured.

## Build

```bash
cd platform/model/explorer
../../geo/.venv/bin/python build_bundle.py    # needs geopandas — use the geo package's venv
```

Reads `platform/model/data/model/{fh_state,sae_lga}.parquet`,
`platform/survey/data/survey/survey_series.parquet`, and the geo
spine's `geo_unit.parquet` + OCHA shapefile (for geometry, same
mapshaper recipe as `platform/geo/explorer`). Writes `build/index.html`
— publish that.

`build/` is gitignored (regenerable). `template.html` and
`build_bundle.py` are the source.

## Design choices worth knowing

- **Colour always means the same thing.** Green is good, red is
  concerning, regardless of whether high values are good (e.g.
  improved water) or bad (e.g. stunting) for a given indicator — the
  ramp direction flips per indicator (`WORSE_WHEN_HIGH` /
  `BETTER_WHEN_HIGH` in `build_bundle.py`), not the data. The build
  fails loudly if a new indicator isn't classified in exactly one of
  those sets, rather than silently defaulting it and mis-colouring it.
- **LGA level is visibly different from state level.** A red-bordered
  banner and an in-panel "read this carefully" box explain that LGA
  figures are a synthetic regression benchmarked to the state number,
  not sampled locally — every time, not just the first time.
- **A CSS rule setting `font-size` on `.glabel` will silently break
  zoom-independent label sizing** — SVG presentation attributes (how
  the per-frame JS sizes labels) lose to *any* stylesheet rule, even
  one that looks unrelated. Hit this once already (see the comment
  above `.glabel` in `template.html`); don't remove it without reason.
