"""Shape + integrity of the LGA covariate stack."""

import pandas as pd

from covariates.config import GEO_UNIT


def test_one_row_per_lga(lga):
    units = pd.read_parquet(GEO_UNIT, columns=["pcode", "level"])
    spine_lgas = set(units[units.level == 2].pcode)
    assert len(lga) == 774
    assert set(lga.lga_pcode) == spine_lgas
    assert not lga.lga_pcode.duplicated().any()


def test_always_on_covariates_complete(lga, cov_dict):
    for c in cov_dict[cov_dict.coverage == "all"].name:
        assert lga[c].notna().all(), f"{c} has nulls"


def test_facility_columns_follow_the_flag(lga):
    # NaN exactly where facility_data is False; numeric where True
    assert lga.loc[~lga.facility_data, "n_facilities"].isna().all()
    assert lga.loc[lga.facility_data, "n_facilities"].notna().all()
    assert lga.facility_data.sum() >= 400            # 24 states' worth of LGAs


def test_shares_in_unit_interval(lga):
    for c in ("builtup_fraction", "builtup_core_share", "nonhamlet_area_share",
              "pct_fac_functional", "pct_fac_public", "pct_fac_referral"):
        v = lga[c].dropna()
        assert v.between(0, 1).all(), c


def test_positive_magnitudes(lga):
    assert (lga.area_km2 > 0).all()
    assert (lga.bldg_count_total.dropna() >= 0).all()
    assert (lga.dist_nearest_city_km >= 0).all()
    assert lga.dist_nearest_city_km.max() < 1200          # Nigeria is ~1100 km across


def test_building_totals_match_assignable_source(lga):
    from covariates.config import GEO_SETTLEMENT
    s = pd.read_parquet(GEO_SETTLEMENT, columns=["lga_pcode", "bldg_count"])
    assignable = s[s.lga_pcode.isin(set(lga.lga_pcode))].bldg_count.sum()
    assert abs(lga.bldg_count_total.sum() - assignable) < 1


def test_dict_covers_every_covariate(lga, cov_dict):
    covs = {c for c in lga.columns
            if c not in {"lga_pcode", "lga_name", "state_pcode", "settlement_data",
                         "ward_data", "facility_data", "metro_merge_suspect"}}
    # every built column is documented; the dict may also list Tier B
    # columns that only appear after `covariates worldpop zonal`.
    assert covs.issubset(set(cov_dict.name))
    tier_a = set(cov_dict[~cov_dict.coverage.str.startswith("worldpop")].name)
    assert tier_a.issubset(covs)
