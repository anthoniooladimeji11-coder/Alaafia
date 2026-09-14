# covariates/ — the covariate stack

Auxiliary predictors at **LGA level** (774 rows, keyed to the geography
spine) for small-area estimation of the survey indicators. This is what
lets a model borrow strength from ~50 sampled clusters to every LGA.

## Tier A — from repo data, no downloads

```bash
cd platform/covariates
uv sync
uv run covariates build          # -> data/covariates/covariates_lga.parquet (+ dict, duckdb)
uv run covariates check
uv run covariates query "SELECT lga_name, bldg_density_km2, dist_nearest_city_km FROM covariates_lga ORDER BY bldg_density_km2 DESC NULLS LAST LIMIT 5"
```

**27 covariates** in 5 groups (`covariates_dict.parquet` has the full
list with source + coverage):

| group | covariates |
|---|---|
| geometry | `area_km2`, `centroid_lon/lat`, `n_wards` |
| settlement | `n_settlements`, `n_builtup_settlements`, `settlement_density_km2`, `mean_settlement_bldg` |
| building | `bldg_count_total`, `bldg_area_m2_total`, `bldg_density_km2`, `builtup_fraction`, `builtup_core_share`, `nonhamlet_area_share`, `log_bldg_count` |
| facility | `n_facilities`, `n_phc`, `n_referral`, `fac_per_100k_bldg`, `phc_per_100k_bldg`, `fac_per_1000km2`, `pct_fac_functional`, `pct_fac_public`, `pct_fac_referral` |
| accessibility | `dist_nearest_city_km`, `dist_lagos_km`, `dist_abuja_km` |

### Coverage flags (a column is NaN, not 0, where the source doesn't reach)

| flag | meaning | affected |
|---|---|---|
| `facility_data` | GRID3 Health Facilities v3.0 covers this state | 513 LGAs true, 261 NaN |
| `ward_data` | GRID3 Operational Wards v3.0 covers this state | same 24 states |
| `settlement_data` | the LGA got ≥1 discrete GRID3 settlement extent | 760 true, 14 NaN |
| `metro_merge_suspect` | LGA sits on a major city but reads near-rural — GRID3's merged settlement blobs dumped the conurbation's buildings into one neighbour; **use WorldPop `pop_density_km2` here, not the building columns** | 65 LGAs |

## Tier B — WorldPop population (raster zonal stats)

The building columns are biased in ~65 dense metro LGAs (Lagos, Kano,
Ibadan, Sokoto, Kaduna inner cities). WorldPop's 1 km raster distributes
population by actual built-up area regardless of admin-polygon merging,
so its zonal sum per LGA is the trustworthy density signal.

```bash
uv sync --extra raster                    # rasterio + exactextract
uv run covariates worldpop fetch --only-total
uv run covariates worldpop zonal          # adds pop_2020, pop_density_km2 (+ pct_u5 if age files fetched)
```

`worldpop fetch` (no flag) also pulls the under-5 age–sex rasters →
`pop_u5_2020`, `pct_u5`. If a WorldPop URL 404s, get the current path
from <https://hub.worldpop.org/> and update `RASTERS` in `worldpop.py`.

## Next covariates (later)

Night-lights (VIIRS VNL V2), travel time to healthcare (MAP 2019),
CHIRPS rainfall / MODIS EVI, ACLED conflict-event density. Same zonal
pattern; add as rasters to `worldpop.py` or a sibling module.

## Tests

`uv run pytest` — 7 tests: one row per spine LGA, always-on covariates
complete, facility columns follow the flag, shares in [0,1], magnitudes
sane, building totals reconcile to source, dict covers every column.

## Sources & licences

- GRID3 NGA Settlement Extents v3.1, Operational Wards v3.0, Health
  Facilities v3.0 — via the geography spine (CC-BY / CC-BY-SA).
- WorldPop (Tier B) — CC-BY 4.0, <https://www.worldpop.org>.
