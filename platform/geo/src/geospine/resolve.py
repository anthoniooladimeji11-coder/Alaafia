"""Resolve free-text names or coordinates to canonical P-codes.

NameResolver  — fuzzy text  → pcode. The workhorse for building crosswalks from
                every upstream source (DHS state labels, DHIS2 org units, NBS
                tables, spreadsheet columns…). Scoped by level and optionally by
                parent so "Bassa" in Kogi ≠ "Bassa" in Plateau.

PointResolver — (lon, lat)  → {state, lga, ward} pcodes via point-in-polygon
                against the OCHA COD geometry (states + LGAs) and, if present,
                the GRID3 ward geometry.
"""

from __future__ import annotations

from dataclasses import dataclass

import duckdb
from rapidfuzz import fuzz, process

from . import config
from .normalize import name_key, norm_name

_MIN_SCORE = 88          # accept a fuzzy hit at or above this
_MARGIN = 6              # …only if it beats the runner-up by this much


@dataclass
class Match:
    query: str
    pcode: str | None
    name: str | None
    level: int
    score: float          # 100 = exact key match
    method: str           # exact_key | alias_key | fuzzy | none | ambiguous
    candidates: list[tuple[str, str, float]] | None = None  # (pcode, name, score)

    @property
    def ok(self) -> bool:
        return self.pcode is not None


class NameResolver:
    def __init__(self, level: int, parent_pcode: str | None = None,
                 duckdb_path=None):
        self.level = level
        self.parent_pcode = parent_pcode
        con = duckdb.connect(str(duckdb_path or config.DUCKDB_PATH), read_only=True)
        where = "u.level = ?"
        params: list = [level]
        if parent_pcode:
            # match on either direct parent or denormalised ancestor
            where += " AND (? IN (u.parent_pcode, u.adm1_pcode, u.adm2_pcode))"
            params.append(parent_pcode)
        self._units = con.execute(
            f"SELECT pcode, name, name_key FROM geo_unit u WHERE {where}", params
        ).fetchall()
        pcs = tuple(p for p, _, _ in self._units) or ("",)
        self._aliases = con.execute(
            f"SELECT alias_key, pcode FROM geo_alias WHERE pcode IN {pcs!r}"
        ).fetchall() if self._units else []
        con.close()

        self._by_key: dict[str, tuple[str, str]] = {}
        for pc, nm, nk in self._units:
            self._by_key.setdefault(nk, (pc, nm))
        self._alias_key: dict[str, str] = {}
        for ak, pc in self._aliases:
            self._alias_key.setdefault(ak, pc)
        self._choices = {pc: nm for pc, nm, _ in self._units}  # pcode -> name

    def resolve(self, text: str) -> Match:
        q = str(text)
        k = name_key(q)
        if not k:
            return Match(q, None, None, self.level, 0.0, "none")

        if k in self._by_key:
            pc, nm = self._by_key[k]
            return Match(q, pc, nm, self.level, 100.0, "exact_key")
        if k in self._alias_key:
            pc = self._alias_key[k]
            return Match(q, pc, self._choices.get(pc), self.level, 100.0, "alias_key")

        # fuzzy over unit names (normalised) keyed by pcode
        scored = process.extract(
            norm_name(q),
            {pc: nm for pc, nm in self._choices.items()},
            scorer=fuzz.token_set_ratio,
            limit=5,
        )
        cands = [(pc, nm, float(sc)) for nm, sc, pc in scored]
        if not cands:
            return Match(q, None, None, self.level, 0.0, "none")
        best_pc, best_nm, best_sc = cands[0]
        second = cands[1][2] if len(cands) > 1 else 0.0
        if best_sc >= _MIN_SCORE and (best_sc - second) >= _MARGIN:
            return Match(q, best_pc, best_nm, self.level, best_sc, "fuzzy", cands)
        return Match(q, None, None, self.level, best_sc, "ambiguous", cands)


class PointResolver:
    """Point-in-polygon against OCHA COD (state, LGA) + GRID3 (ward if present)."""

    def __init__(self):
        import geopandas as gpd

        shp_zip = config.RAW_OCHA / "nga_admin_boundaries.shp.zip"
        if not shp_zip.exists():
            raise FileNotFoundError(
                f"{shp_zip} missing — run `geospine fetch` (needs the OCHA COD shapefile)."
            )
        self._gpd = gpd
        # layer names inside the zip follow the sheet names
        self._a1 = self._read(shp_zip, "nga_admin1", "adm1_pcode")
        self._a2 = self._read(shp_zip, "nga_admin2", "adm2_pcode")
        # ward geometry keyed to the minted canonical pcode, written by build()
        self._a3 = None
        if config.WARD_GEOM_PARQUET.exists():
            self._a3 = gpd.read_parquet(config.WARD_GEOM_PARQUET).to_crs(4326)

    def _read(self, shp_zip, layer, code_col):
        g = self._gpd.read_file(f"zip://{shp_zip}!{layer}.shp").to_crs(4326)
        return g[[code_col, "geometry"]].rename(columns={code_col: "pcode"})

    def locate(self, lon: float, lat: float) -> dict[str, str | None]:
        from shapely.geometry import Point

        p = self._gpd.GeoSeries([Point(lon, lat)], crs=4326)
        out: dict[str, str | None] = {"state": None, "lga": None, "ward": None}
        for key, layer in (("state", self._a1), ("lga", self._a2), ("ward", self._a3)):
            if layer is None:
                continue
            hit = self._gpd.sjoin(
                self._gpd.GeoDataFrame(geometry=p), layer, predicate="within"
            )
            if len(hit):
                out[key] = str(hit.iloc[0]["pcode"])
        return out

    def locate_frame(self, df, lon="lon", lat="lat"):
        """Vectorised: one sjoin per layer for a whole DataFrame of points.
        Returns df with state_pcode_pt / lga_pcode_pt / ward_pcode_pt columns."""
        gpd = self._gpd
        pts = gpd.GeoDataFrame(
            df.copy(),
            geometry=gpd.points_from_xy(df[lon], df[lat]),
            crs=4326,
        ).reset_index(drop=True)
        pts["_i"] = range(len(pts))
        for col, layer in (("state_pcode_pt", self._a1),
                           ("lga_pcode_pt", self._a2),
                           ("ward_pcode_pt", self._a3)):
            if layer is None:
                pts[col] = None
                continue
            j = gpd.sjoin(pts[["_i", "geometry"]], layer, predicate="within", how="left")
            j = j.drop_duplicates("_i").set_index("_i")["pcode"]
            pts[col] = pts["_i"].map(j)
        return pts.drop(columns=["geometry", "_i"])
