# survey/ — the survey layer (INGEST)

Pipeline: `INGEST → RESOLVE (spine ✅) → MODEL → NARRATE → DELIVER`.
This is **INGEST**. It lands published health indicators on the geography
spine as one long, sourced, uncertainty-bearing table.

## v1 source — the DHS program API (StatCompiler)

Free, no key. Nigeria: **DHS 1990 / 2003 / 2008 / 2013 / 2018 / 2024** +
**MIS 2010 / 2015 / 2021**. National + 6 zones + 37 states (state level
from 2013 on).

**27 indicators** across 11 domains — child nutrition, anaemia,
immunisation, child health, child mortality, maternal/RH, family
planning, malaria, WASH, education, living standards
(`src/surveylayer/indicators.py`; all IDs verified against the API).

## Build

```bash
cd platform/survey
uv sync
uv run surveylayer fetch        # cache raw API pages -> data/raw/dhs_api/
uv run surveylayer build        # -> data/survey/survey_indicator.parquet (+ series dict, source meta, duckdb)
uv run surveylayer check
uv run surveylayer query "SELECT slug, geo_name, survey_year, value FROM survey_indicator WHERE slug='child_stunting' AND geo_level='state' AND survey_year=2024 ORDER BY value DESC LIMIT 5"
```

`uv run pytest` — 8 tests (schema, unique keys, value ranges, 100 %
spine resolution, state series since 2013, domain tags).

## Output — `survey_indicator.parquet`

One row per **(indicator, survey, geography)**. Columns:

| | |
|---|---|
| `indicator_id` `slug` `domain` `unit` `populace` `indicator_label` | what is measured (`unit`: `pct` / `prev_pct` / `rate_1000`) |
| `survey_id` `survey_type` `survey_year` | which round |
| `geo_level` `geo_pcode` `geo_name` `geo_unresolved` | keyed to the spine — `NG` / `ZONE_*` / `NG0NN` |
| `value` `ci_low` `ci_high` `denom_unweighted` `denom_weighted` | the estimate + what the API publishes about its precision |
| `is_preferred` `source` `retrieved_at` | provenance |

Plus `survey_series.parquet` (indicator dictionary + coverage counts) and
`survey_source_meta.parquet` (URL, licence, sha256, retrieval date).

## Known coverage gaps (source, not bugs — surfaced by `check`)

- **CIs on ~13 % of rows.** The API rarely publishes subnational SEs.
  ~90 % of rows carry an unweighted N, so area-level models can
  approximate sampling variance from `denom_unweighted` × a DHS design
  effect until the microdata lands.
- `excl_breastfeeding` — national only (DHS StatCompiler quirk).
- `child_anaemia_any`, `women_anaemia_any`, `pentavalent3` — no 2013
  round (NDHS 2013 didn't test anaemia / used older vaccine coding).
- `malaria_rdt_prev` — state level only in NDHS 2018; MIS rounds report
  it differently.

## Next

1. **Covariate stack** — LGA-level predictors (WorldPop population,
   GRID3 settlement density, VIIRS night-lights, travel time) for SAE.
2. **Area-level SAE (Fay–Herriot)** — smooth/shrink the 2024 state
   estimates with the covariates; no microdata needed. First proof of
   the MODEL step.
3. **Unit-level SAE** — survey microdata + GPS → LGA/ward estimates with
   credible intervals, calibrated to the state figures here. Blocked on
   DHS microdata approval; the state series here are the calibration
   targets.

## Licence

DHS data is redistributed under the DHS Program Terms of Use
(<https://dhsprogram.com/Data/terms-of-use.cfm>). Recorded per-pull in
`survey_source_meta.parquet`.
