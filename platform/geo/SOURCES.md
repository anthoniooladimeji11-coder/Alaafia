# Geography spine — data sources

Every upstream file is declared in `src/geospine/sources.py` and fetched by
`geospine fetch` into `data/raw/`. Each download writes a `*._manifest.json`
(url, bytes, sha256, retrieved_at) next to it; `geospine build` stamps those
into the `geo_source_meta` table.

| key | dataset | provider | licence | role |
|---|---|---|---|---|
| `ocha_cod_xlsx` | Nigeria – Subnational Administrative Boundaries (names + P-codes) | OCHA FISS | CC-BY-IGO 3.0 | **admin0–2 backbone**: 1 national, 37 states, 774 LGAs, P-code scheme, centroids, senatorial districts |
| `ocha_cod_shp` | …same, geometry (shapefile) | OCHA FISS | CC-BY-IGO 3.0 | polygon geometry for state + LGA point-in-polygon |
| `grid3_wards` | GRID3 NGA – Operational Wards v3.0 | GRID3 / CIESIN | **CC-BY-SA 4.0** | **level-3 wards**: 5,872 polygons + alt-name lists (no P-code upstream — minted here) |
| `grid3_settlements` | GRID3 NGA – Settlement Extents **v3.1** (polygons) | GRID3 / CIESIN | **CC-BY-SA 4.0** | **level-4 settlements** (~736 MB zip, HDX CDN). `geospine fetch --big` + `geospine settlements`. Reduced to a points table; polygons git-ignored. |
| `grid3_settlements_v4_1` | GRID3 NGA – Settlement Extents v4.1 | GRID3 / Columbia CIESIN | CC-BY-SA 4.0 | newer (~2.1 GB, Columbia Academic Commons). Swap in for v3.1 when bandwidth allows. |
| `grid3_health_facilities` | GRID3 NGA – Health Facilities v3.0 | GRID3 | CC-BY 4.0 | Tier-2 input — **`geo_facility.parquet`**: 41,778 facilities geocoded to state/LGA/ward, with NHFR code, level, ownership, functional status. |

## P-code scheme

OCHA COD hierarchical codes, extended for wards:

```
NG                     national
NG0dd                  state        (NG001 … NG037)
NG0dd0dd               LGA          (NG001001 = Aba North, Abia)
NG0dd0dd0dd            ward         MINTED: <lga_pcode> + 3-digit sequence,
                                    wards ordered by normalised name within LGA
```

Ward codes are **synthetic and stable within a build** (deterministic order).
If GRID3 revises its ward set, ward codes shift — treat `pcode` at level 3 as
version-bound to `grid3_wards v3.0` until a released ward P-code standard exists.

## Licence note (for the founder / counsel)

`grid3_wards` and `grid3_settlements` are **CC-BY-SA 4.0**. Share-alike attaches
to redistribution of the *boundary geometry* itself (e.g. shipping the ward
polygons in a product). Analytical outputs computed *using* the boundaries
(estimates, counts, rankings) are generally not "adaptations" of the geometry in
the copyleft sense, but this should be confirmed before the geometry layer is
resold or embedded. OCHA COD is CC-BY-IGO 3.0 (attribution only). Attribution
strings for all sources live in `geo_source_meta`.

## Not yet ingested (next)

- GRID3 settlement extents v4.1 (level 4)
- GRID3 health facilities v3.0 (geocode → ward)
- Historical admin versions / boundary-change crosswalks (LGA/ward creations & renames over time)
- NBS state/LGA codes, DHIS2/NHMIS org-unit hierarchy, HFR — as additional crosswalks
