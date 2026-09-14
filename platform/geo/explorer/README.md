# explorer/ — the geography-spine explorer

A single-page, dependency-light map that lets anyone browse the spine:
nation → state → LGA → ward centroid, with health-facility points, four
colour-by modes, search, and an honest read on **layer coverage**.

Published as an Artifact:
<https://claude.ai/code/artifact/a65e76bc-c880-4ba5-be3c-4e7a135bfc67>

## Build

```bash
cd platform/geo
./.venv/bin/python explorer/build_bundle.py
```

Reads the committed spine outputs (`data/spine/geo_unit.parquet`,
`geo_facility.parquet`, `geo_source_meta.parquet`) + the raw OCHA
admin-boundary shapefile (`data/raw/ocha_cod/`), simplifies geometry with
`npx mapshaper`, and writes:

| file | what |
|---|---|
| `build/spine_bundle.json` | ~1.8 MB — every state/LGA row, ward centroids, packed facility points, simplified TopoJSON, source metadata |
| `build/index.html` | `template.html` with the bundle inlined — **this is what gets published** |

`build/` is gitignored (regenerable). `template.html` and
`build_bundle.py` are the source.

## Publish / update

Re-run the build, then re-publish `build/index.html` to the **same**
Artifact URL (`url=…` above). Never `preview_start` a server for it —
update the Artifact.

## What it does and doesn't claim

- Complete for all 37 states: admin hierarchy, settlement counts, P-codes.
- **Partial (24 states): wards + health facilities.** GRID3 Operational
  Wards v3.0 and Health Facilities v3.0 only cover 24 states / 511 LGAs.
  The other 13 — Akwa Ibom, Anambra, Benue, Cross River, Ebonyi, Edo,
  Ekiti, Imo, Lagos, Ondo, Plateau, Rivers, Taraba — are LGA-level only.
  The map draws that boundary explicitly (hollow + hachure), not hidden.
- ~35,774 of 41,778 facilities carry coordinates; the rest resolve to an
  LGA by name only and are counted but not plotted.
