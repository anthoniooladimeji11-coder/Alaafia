"""DHS (NDHS / NMIS) geography → canonical spine.

DHS carries geography as:
  * v024   — "region": for Nigeria the 6 geopolitical zones (1..6)
  * sstate — country-specific state code (1..37)

`reference/dhs_geography.csv` holds the DHS code→name mapping taken verbatim
from the epicause_ng pipeline's `utils/nigeria_geography.py`. This module
attaches a canonical `pcode` to every state row by resolving the DHS state name
against `geo_unit`, and emits `crosswalk_dhs.parquet`:

  dhs_scheme  dhs_code  dhs_label       pcode      level  match_score  match_method
  sstate      14        FCT Abuja       NG015      1      100          alias_key
  v024        4         South East      (zone)     -      -            reference

NOTE ON VERIFICATION: the sstate numbering and the v024→zone mapping are
asserted by the source pipeline, not yet checked against the official DHS
recode manual for NGIR8. Validate against a real NDHS 2024 extract before this
crosswalk is trusted for joins. Rows carry `verified = false`.
"""

from __future__ import annotations

import duckdb
import pandas as pd

from .. import config
from ..resolve import NameResolver


def build() -> dict:
    ref = pd.read_csv(config.REFERENCE / "dhs_geography.csv")
    r1 = NameResolver(level=1)

    rows: list[dict] = []
    unresolved: list[str] = []

    # sstate → canonical state pcode
    for _, x in ref.iterrows():
        m = r1.resolve(x["dhs_state_name"])
        if not m.ok:
            unresolved.append(x["dhs_state_name"])
        rows.append({
            "dhs_scheme": "sstate",
            "dhs_code": int(x["dhs_sstate_code"]),
            "dhs_label": x["dhs_state_name"],
            "pcode": m.pcode,
            "canonical_name": m.name,
            "level": 1,
            "match_score": m.score,
            "match_method": m.method,
            "verified": False,
        })

    # v024 → geopolitical zone (the spine has no zone level; keep as labelled rows)
    for code, (abbr, name) in (
        ref.drop_duplicates("dhs_zone_code")
        .set_index("dhs_zone_code")[["dhs_zone_abbr", "dhs_zone_name"]]
        .iterrows()
    ):
        rows.append({
            "dhs_scheme": "v024",
            "dhs_code": int(code),
            "dhs_label": name,
            "pcode": f"ZONE_{abbr}",
            "canonical_name": name,
            "level": -1,
            "match_score": 100.0,
            "match_method": "reference",
            "verified": False,
        })

    df = pd.DataFrame(rows)
    df.to_parquet(config.CROSSWALK_DHS_PARQUET, index=False)

    con = duckdb.connect(str(config.DUCKDB_PATH))
    con.execute("DROP TABLE IF EXISTS crosswalk_dhs")
    con.register("cw", df)
    con.execute("CREATE TABLE crosswalk_dhs AS SELECT * FROM cw")
    con.close()

    return {
        "rows": len(df),
        "sstate_resolved": int((df.query("dhs_scheme=='sstate'")["pcode"].notna()).sum()),
        "sstate_total": int((df["dhs_scheme"] == "sstate").sum()),
        "unresolved": unresolved,
        "parquet": str(config.CROSSWALK_DHS_PARQUET),
    }
