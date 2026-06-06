"""
Alaafia Data Filter
Filters NDHS 2024 merged dataset by geography and population
before tokenisation and pipeline execution.
"""

import sys
sys.path.append('/Users/theoneglobal/epicause_ng')

import pandas as pd
import numpy as np

ZONE_CODES = {'NC':1,'NE':2,'NW':3,'SE':4,'SS':5,'SW':6}

STATE_MAP = {
    1:'Sokoto', 2:'Zamfara', 3:'Katsina', 4:'Jigawa',
    5:'Yobe', 6:'Borno', 7:'Adamawa', 8:'Gombe', 9:'Bauchi',
    10:'Kano', 11:'Kaduna', 12:'Kebbi', 13:'Niger', 14:'FCT Abuja',
    15:'Nasarawa', 16:'Plateau', 17:'Taraba', 18:'Benue',
    19:'Kogi', 20:'Kwara', 21:'Oyo', 22:'Osun', 23:'Ekiti',
    24:'Ondo', 25:'Edo', 26:'Anambra', 27:'Enugu', 28:'Ebonyi',
    29:'Cross River', 30:'Akwa Ibom', 31:'Abia', 32:'Imo',
    33:'Rivers', 34:'Bayelsa', 35:'Delta', 36:'Lagos', 37:'Ogun',
}

STATES_BY_ZONE = {
    'NC':[13,14,15,16,18,19,20],
    'NE':[5,6,7,8,9,17],
    'NW':[1,2,3,4,10,11,12],
    'SE':[26,27,28,31,32],
    'SS':[25,29,30,33,34,35],
    'SW':[21,22,23,24,36,37],
}

DATA_PATH = "/Users/theoneglobal/epicause_ng/data/processed/ndhs2024_merged.parquet"


def load_merged_data() -> pd.DataFrame:
    return pd.read_parquet(DATA_PATH)


def filter_by_geography(
    df: pd.DataFrame,
    zone: str = None,
    state_code: int = None,
    outcome: str = 'anaemia',
    sample_n: int = 5,
) -> pd.DataFrame:
    filtered = df.copy()

    if state_code:
        filtered = filtered[filtered['sstate'].astype(int) == state_code]
    elif zone:
        zone_code = ZONE_CODES.get(zone.upper())
        if zone_code:
            filtered = filtered[filtered['v024'].astype(int) == zone_code]

    if outcome == 'anaemia':
        filtered = filtered[filtered['v457'].notna()]

    if len(filtered) == 0:
        return pd.DataFrame()

    n = min(sample_n, len(filtered))
    return filtered.sample(n=n, random_state=42)


def get_geography_stats(
    df: pd.DataFrame,
    zone: str = None,
    state_code: int = None,
) -> dict:
    filtered = df.copy()

    if state_code:
        filtered = filtered[filtered['sstate'].astype(int) == state_code]
    elif zone:
        zone_code = ZONE_CODES.get(zone.upper())
        if zone_code:
            filtered = filtered[filtered['v024'].astype(int) == zone_code]

    if len(filtered) == 0:
        return {}

    anaemia_sub = filtered[filtered['v457'].notna()]
    anaemia_pct = (anaemia_sub['v457'].astype(float) < 4).mean() * 100 if len(anaemia_sub) > 0 else None

    hb = filtered['v453'].copy() / 10
    hb[hb >= 99] = None
    hb[hb < 5] = None

    solid_fuel       = filtered['hh_fuel'].isin([6,7,8,9,10]).mean() * 100
    unimproved_water = filtered['hh_water'].isin([32,42,43,96]).mean() * 100
    poor_sanitation  = filtered['hh_sanitation'].isin([23,41,51,96]).mean() * 100

    state_name = STATE_MAP.get(state_code, '') if state_code else ''
    zone_name  = zone.upper() if zone else ''

    # Stunting and wasting from KR cluster aggregates
    stunting_pct = filtered['kr_stunting_pct'].mean() if 'kr_stunting_pct' in filtered.columns else None
    wasting_pct  = filtered['kr_wasting_pct'].mean()  if 'kr_wasting_pct'  in filtered.columns else None

    return {
        'geography': state_name or zone_name,
        'n_records': len(filtered),
        'n_anaemia_measured': len(anaemia_sub),
        'anaemia_prevalence_pct': round(anaemia_pct, 1) if anaemia_pct else None,
        'stunting_prevalence_pct': round(float(stunting_pct), 1) if stunting_pct is not None else None,
        'wasting_prevalence_pct': round(float(wasting_pct), 1) if wasting_pct is not None else None,
        'median_hb_gdl': round(float(hb.median()), 2) if hb.notna().sum() > 0 else None,
        'solid_fuel_pct': round(solid_fuel, 1),
        'unimproved_water_pct': round(unimproved_water, 1),
        'poor_sanitation_pct': round(poor_sanitation, 1),
    }


if __name__ == "__main__":
    print("Loading data...")
    df = load_merged_data()

    print("\n=== ZONE FILTER TEST (SE) ===")
    result = filter_by_geography(df, zone='SE', outcome='anaemia', sample_n=3)
    print(f"Records returned: {len(result)}")
    print(f"Zones: {result['v024'].unique().tolist()}")

    print("\n=== STATE FILTER TEST (Lagos = 36) ===")
    result = filter_by_geography(df, state_code=36, outcome='anaemia', sample_n=3)
    print(f"Records returned: {len(result)}")
    print(f"States: {result['sstate'].unique().tolist()}")

    print("\n=== GEOGRAPHY STATS (Lagos) ===")
    stats = get_geography_stats(df, state_code=36)
    for k, v in stats.items():
        print(f"  {k}: {v}")

    print("\n=== GEOGRAPHY STATS (Borno = 6) ===")
    stats = get_geography_stats(df, state_code=6)
    for k, v in stats.items():
        print(f"  {k}: {v}")
