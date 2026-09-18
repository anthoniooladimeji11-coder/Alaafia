"""Registry of upstream geography sources.

Every file the spine ingests is declared here with its URL, licence, and the
local path it lands at. `fetch.py` reads this; `build.py` stamps provenance rows
from it into `geo_source_meta`.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import config


@dataclass(frozen=True)
class Source:
    key: str
    title: str
    url: str
    dest: str  # path relative to data/raw/
    licence: str
    provider: str
    note: str = ""

    @property
    def path(self):
        return config.RAW / self.dest


SOURCES: dict[str, Source] = {
    # ── OCHA Common Operational Dataset — admin boundaries (admin0-3) ──────
    # The sector-standard P-code spine for Nigeria. admin1 = 37 states,
    # admin2 = 774 LGAs, admin3 = partial ward layer (~714, humanitarian
    # coverage only — full wards come from GRID3).
    "ocha_cod_xlsx": Source(
        key="ocha_cod_xlsx",
        title="Nigeria - Subnational Administrative Boundaries (names + P-codes)",
        url=(
            "https://data.humdata.org/dataset/81ac1d38-f603-4a98-804d-325c658599a3/"
            "resource/f1865f35-a07e-4de3-9183-e4222e475527/download/nga_admin_boundaries.xlsx"
        ),
        dest="ocha_cod/nga_admin_boundaries.xlsx",
        licence="CC-BY-IGO 3.0",
        provider="OCHA Field Information Services Section (FISS)",
    ),
    "ocha_cod_shp": Source(
        key="ocha_cod_shp",
        title="Nigeria - Subnational Administrative Boundaries (geometry, shapefile)",
        url=(
            "https://data.humdata.org/dataset/81ac1d38-f603-4a98-804d-325c658599a3/"
            "resource/01c65fd9-bd0c-4608-aa1e-2e86bbccf3e5/download/nga_admin_boundaries.shp.zip"
        ),
        dest="ocha_cod/nga_admin_boundaries.shp.zip",
        licence="CC-BY-IGO 3.0",
        provider="OCHA Field Information Services Section (FISS)",
    ),
    # ── GRID3 — the full operational ward layer (~9,000 wards) ────────────
    "grid3_wards": Source(
        key="grid3_wards",
        title="GRID3 NGA - Operational Wards v3.0",
        url=(
            "https://data.humdata.org/dataset/db8702fe-7d11-484e-aed5-31b3fc32850c/"
            "resource/37e5f2c6-ec94-4060-932d-755b99dd963e/download/grid3_nga_operational_wards_v3_0.gpkg"
        ),
        dest="grid3/GRID3_NGA_operational_wards_v3_0.gpkg",
        licence="CC-BY-SA 4.0",
        provider="GRID3 (Geo-Referenced Infrastructure and Demographic Data for Development)",
        note="~199 MB. CC-BY-SA — share-alike applies to redistribution of the boundary geometry.",
    ),
    # ── GRID3 — settlement extents (level 4). Large; fetch deliberately. ──
    # v3.1 (736 MB, HDX CDN) is the working layer. v4.1 (2.1 GB, Columbia
    # Academic Commons) is newer — swap it in when bandwidth allows.
    "grid3_settlements": Source(
        key="grid3_settlements",
        title="GRID3 NGA - Settlement Extents v3.1 (polygons)",
        url=(
            "https://data.humdata.org/dataset/af838671-b9a6-4ae9-8ed5-eea750b05597/"
            "resource/0a22d6fc-7f1f-4f50-aead-09ef7be0455d/download/"
            "grid3_nga_settlement_extents_v3_1_gpkg.zip"
        ),
        dest="grid3/GRID3_NGA_settlement_extents_v3_1_gpkg.zip",
        licence="CC-BY-SA 4.0",
        provider="GRID3 / CIESIN, Columbia University",
        note="~736 MB zip. Settlement polygons + attributes (type, building count/area). "
        "Reduced to a points table by build(); polygons kept in a gitignored geoparquet.",
    ),
    "grid3_settlements_v4_1": Source(
        key="grid3_settlements_v4_1",
        title="GRID3 NGA - Settlement Extents v4.1",
        url="https://academiccommons.columbia.edu/doi/10.7916/wbrj-a107/download",
        dest="grid3/GRID3_NGA_settlement_extents_v4_1.gpkg",
        licence="CC-BY-SA 4.0",
        provider="GRID3 / Columbia CIESIN",
        note="~2.1 GB, Columbia Academic Commons (not HDX CDN). Newer than v3.1. Only with --big.",
    ),
    # ── GRID3 — health facilities (Tier-2 spine input; not admin geography) ─
    "grid3_health_facilities": Source(
        key="grid3_health_facilities",
        title="GRID3 NGA - Health Facilities v3.0",
        url=(
            "https://data.humdata.org/dataset/a1e3e4bc-3699-4fe1-bd17-b38f4e7108d2/"
            "resource/f45c9266-0458-4160-a902-32661a6a67ed/download/grid3_nga_health_facilities_v3_0.gpkg"
        ),
        dest="grid3/GRID3_NGA_health_facilities_v3_0.gpkg",
        licence="CC-BY 4.0",
        provider="GRID3",
        note="~34 MB. Facility registry — the denominator layer. Not admin geography; "
        "kept here so the spine can geocode facilities to ward.",
    ),
}

# Large but needed by a build step — pulled by `fetch --big`.
BIG = {"grid3_settlements"}
# Large AND not needed by any build (a newer alternative to `grid3_settlements`).
# Only fetched when named explicitly: `geospine fetch grid3_settlements_v4_1`.
OPTIONAL = {"grid3_settlements_v4_1"}
