import pandas as pd
import numpy as np

ZONE_MAP = {1:'north_central',2:'north_east',3:'north_west',
            4:'south_east',5:'south_south',6:'south_west'}

WEALTH_MAP = {1:'poorest',2:'poor',3:'middle',4:'rich',5:'richest'}

RESIDENCE_MAP = {1:'urban',2:'rural'}

EDUCATION_MAP = {0:'no_education',1:'primary',2:'secondary',3:'higher'}

FUEL_MAP = {1:'electricity',2:'lpg',3:'natural_gas',4:'biogas',
            5:'kerosene',6:'coal',7:'charcoal',8:'wood',
            9:'straw',10:'dung',95:'no_cooking',96:'other'}

SOLID_FUEL = {6,7,8,9,10}
CLEAN_FUEL = {1,2,3,4,5}

WATER_MAP = {11:'piped_dwelling',12:'piped_yard',13:'piped_neighbor',
             21:'protected_well',31:'protected_spring',41:'rainwater',
             51:'tanker',61:'bottled',71:'filtered',
             32:'unprotected_spring',42:'surface_water',43:'river',96:'other'}

UNIMPROVED_WATER = {32,42,43,96}

SANITATION_MAP = {11:'flush_sewer',12:'flush_septic',13:'flush_pit',
                  21:'ventilated_pit',22:'pit_slab',23:'pit_no_slab',
                  31:'composting',41:'hanging',51:'open_defecation',96:'other'}

POOR_SANITATION = {23,41,51,96}

ANAEMIA_MAP = {1:'severe',2:'moderate',3:'mild',4:'none'}


def safe_int(val):
    try:
        if pd.isna(val):
            return None
        return int(val)
    except:
        return None


def tokenise_record(row: pd.Series) -> str:
    tokens = []

    # ── STRATUM ──
    zone = safe_int(row.get('v024'))
    if zone:
        tokens.append(f"STRATUM:zone_{ZONE_MAP.get(zone,'unknown')}")

    wealth = safe_int(row.get('v190'))
    if wealth:
        tokens.append(f"STRATUM:{WEALTH_MAP.get(wealth,'unknown')}")

    res = safe_int(row.get('v025'))
    if res:
        tokens.append(f"STRATUM:{RESIDENCE_MAP.get(res,'unknown')}")

    edu = safe_int(row.get('v106'))
    if edu is not None:
        tokens.append(f"STRATUM:education_{EDUCATION_MAP.get(edu,'unknown')}")

    # ── EXPOSURE: household level ──
    fuel = safe_int(row.get('hh_fuel'))
    if fuel:
        fuel_label = 'solid_fuel' if fuel in SOLID_FUEL else 'clean_fuel'
        tokens.append(f"EXPOSURE:cooking_{fuel_label}")

    water = safe_int(row.get('hh_water'))
    if water:
        water_label = 'unimproved_water' if water in UNIMPROVED_WATER else 'improved_water'
        tokens.append(f"EXPOSURE:{water_label}")

    sanit = safe_int(row.get('hh_sanitation'))
    if sanit:
        sanit_label = 'poor_sanitation' if sanit in POOR_SANITATION else 'improved_sanitation'
        tokens.append(f"EXPOSURE:{sanit_label}")

    # ── EXPOSURE: geospatial ──
    travel = row.get('travel_time')
    if pd.notna(travel):
        if travel > 60:
            tokens.append("EXPOSURE:health_facility_far")
        elif travel > 30:
            tokens.append("EXPOSURE:health_facility_moderate")
        else:
            tokens.append("EXPOSURE:health_facility_close")

    malaria = row.get('malaria_prev')
    if pd.notna(malaria):
        if malaria > 0.4:
            tokens.append("EXPOSURE:high_malaria_burden")
        elif malaria > 0.2:
            tokens.append("EXPOSURE:moderate_malaria_burden")
        else:
            tokens.append("EXPOSURE:low_malaria_burden")

    itn = row.get('itn_coverage')
    if pd.notna(itn):
        tokens.append(f"EXPOSURE:itn_coverage_{'low' if itn < 0.3 else 'moderate' if itn < 0.6 else 'high'}")

    # ── MEDIATORS ──
    parity = safe_int(row.get('v220'))
    if parity is not None:
        if parity == 0:
            tokens.append("MEDIATOR:nulliparous")
        elif parity <= 2:
            tokens.append("MEDIATOR:low_parity")
        elif parity <= 4:
            tokens.append("MEDIATOR:moderate_parity")
        else:
            tokens.append("MEDIATOR:high_parity")

    anc = row.get('m14_1')
    if pd.notna(anc):
        if anc == 0:
            tokens.append("MEDIATOR:no_anc")
        elif anc < 4:
            tokens.append("MEDIATOR:suboptimal_anc")
        else:
            tokens.append("MEDIATOR:adequate_anc")

    age = row.get('v012')
    if pd.notna(age):
        if age < 20:
            tokens.append("MEDIATOR:adolescent_mother")
        elif age < 35:
            tokens.append("MEDIATOR:prime_reproductive_age")
        else:
            tokens.append("MEDIATOR:advanced_maternal_age")

    # ── BIOMARKER ──
    hb = row.get('v453')
    if pd.notna(hb):
        hb_val = hb / 10
        if hb_val < 99:
            if hb_val < 8.0:
                tokens.append("BIOMARKER:severe_anaemia")
            elif hb_val < 11.0:
                tokens.append("BIOMARKER:mild_moderate_anaemia")
            else:
                tokens.append("BIOMARKER:no_anaemia")

    # ── OUTCOME ──
    anaemia = safe_int(row.get('v457'))
    if anaemia:
        tokens.append(f"OUTCOME:anaemia_{ANAEMIA_MAP.get(anaemia,'unknown')}")

    # ── EQUITY ──
    if zone:
        tokens.append(f"EQUITY:zone_{ZONE_MAP.get(zone,'unknown')}")
    if wealth:
        tokens.append(f"EQUITY:{WEALTH_MAP.get(wealth,'unknown')}")

    return " | ".join(tokens)


def tokenise_dataset(parquet_path: str, sample_n: int = None) -> pd.DataFrame:
    print("Loading merged dataset...")
    df = pd.read_parquet(parquet_path)

    if sample_n:
        df = df.sample(n=sample_n, random_state=42)

    print(f"Tokenising {len(df):,} records...")
    df['population_token'] = df.apply(tokenise_record, axis=1)

    print(f"\nDone. Sample token:")
    print(df['population_token'].iloc[0])
    return df


if __name__ == "__main__":
    df = tokenise_dataset(
        "/Users/theoneglobal/epicause_ng/data/processed/ndhs2024_merged.parquet",
        sample_n=100
    )
    print(f"\nToken length stats:")
    df['token_length'] = df['population_token'].str.len()
    print(df['token_length'].describe().round(0))

    df[['v001','v002','v024','v190','population_token']].to_csv(
        "/Users/theoneglobal/epicause_ng/data/tokens/sample_tokens.csv",
        index=False
    )
    print("\nSample tokens saved to data/tokens/sample_tokens.csv")
