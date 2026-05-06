"""
Alaafia Population Tokeniser — v2
Converts NDHS 2024 merged records into structured semantic tokens.
Now includes KR (child), GR (pregnancy), and CR (couples) variables.

Author: Anthonio Oladimeji
"""

import pandas as pd
import numpy as np


def safe(val, default='unknown'):
    if pd.isna(val):
        return default
    return val


def tokenise_record(row: pd.Series) -> str:
    tokens = []

    # ─── STRATUM ─────────────────────────────────────────
    zone_map = {1:'zone_north_central', 2:'zone_north_east',
                3:'zone_north_west', 4:'zone_south_east',
                5:'zone_south_south', 6:'zone_south_west'}
    zone = zone_map.get(int(safe(row.get('v024', 0), 0)), 'zone_unknown')
    tokens.append(f"STRATUM:{zone}")

    wealth_map = {1:'poorest', 2:'poor', 3:'middle', 4:'rich', 5:'richest'}
    wealth = wealth_map.get(int(safe(row.get('v190', 0), 0)), 'unknown')
    tokens.append(f"STRATUM:{wealth}")

    residence = 'urban' if safe(row.get('v025', 2)) == 1 else 'rural'
    tokens.append(f"STRATUM:{residence}")

    edu_map = {0:'no_education', 1:'primary', 2:'secondary', 3:'higher'}
    edu = edu_map.get(int(safe(row.get('v106', 0), 0)), 'unknown')
    tokens.append(f"STRATUM:education_{edu}")

    # State
    if not pd.isna(row.get('sstate')):
        tokens.append(f"STRATUM:state_{int(row['sstate'])}")

    # ─── EXPOSURES ───────────────────────────────────────
    # Cooking fuel
    fuel = safe(row.get('v161', 0), 0)
    try:
        fuel = int(fuel)
        if fuel in [1, 2, 3, 4, 5]:
            tokens.append("EXPOSURE:cooking_clean_fuel")
        elif fuel in [6, 7, 8, 9, 10, 11, 95, 96]:
            tokens.append("EXPOSURE:cooking_solid_fuel")
    except:
        pass

    # Water source
    water = safe(row.get('v113', 0), 0)
    try:
        water = int(water)
        if water in [11, 12, 13, 14, 21, 31, 41, 51, 61, 71, 72, 81, 91]:
            tokens.append("EXPOSURE:improved_water")
        else:
            tokens.append("EXPOSURE:unimproved_water")
    except:
        pass

    # Sanitation
    toilet = safe(row.get('v116', 0), 0)
    try:
        toilet = int(toilet)
        if toilet in [11, 12, 13, 14, 15, 21, 22, 41]:
            tokens.append("EXPOSURE:improved_sanitation")
        else:
            tokens.append("EXPOSURE:poor_sanitation")
    except:
        pass

    # Travel time to facility
    travel = safe(row.get('v483a', np.nan))
    if not pd.isna(travel):
        try:
            travel = float(travel)
            if travel <= 30:
                tokens.append("EXPOSURE:health_facility_close")
            elif travel <= 60:
                tokens.append("EXPOSURE:health_facility_moderate")
            else:
                tokens.append("EXPOSURE:health_facility_far")
        except:
            pass

    # Malaria burden (geospatial)
    malaria = safe(row.get('Malaria_Prevalence_2020', np.nan))
    if not pd.isna(malaria):
        try:
            malaria = float(malaria)
            if malaria < 0.1:
                tokens.append("EXPOSURE:low_malaria_burden")
            elif malaria < 0.3:
                tokens.append("EXPOSURE:moderate_malaria_burden")
            else:
                tokens.append("EXPOSURE:high_malaria_burden")
        except:
            pass

    # ITN coverage
    itn = safe(row.get('ITN_Coverage_2020', np.nan))
    if not pd.isna(itn):
        try:
            itn = float(itn)
            if itn >= 0.6:
                tokens.append("EXPOSURE:itn_coverage_high")
            elif itn >= 0.3:
                tokens.append("EXPOSURE:itn_coverage_moderate")
            else:
                tokens.append("EXPOSURE:itn_coverage_low")
        except:
            pass

    # Indoor smoking (HR)
    indoor_smoke = safe(row.get('hv252', np.nan))
    if not pd.isna(indoor_smoke):
        try:
            if int(indoor_smoke) in [1, 2]:
                tokens.append("EXPOSURE:indoor_smoking")
        except:
            pass

    # Food insecurity (HR)
    for fies_var, label in [('hfs7', 'hunger'), ('hfs8', 'no_food_whole_day')]:
        val = safe(row.get(fies_var, np.nan))
        if not pd.isna(val):
            try:
                if int(val) >= 3:
                    tokens.append(f"EXPOSURE:food_insecurity_{label}")
            except:
                pass

    # Maternal tobacco (GR)
    smokes = safe(row.get('gr_smokes', np.nan))
    if not pd.isna(smokes):
        try:
            if float(smokes) > 0.1:
                tokens.append("EXPOSURE:maternal_tobacco_use")
        except:
            pass

    # Maternal alcohol (GR)
    alcohol = safe(row.get('gr_alcohol_days', np.nan))
    if not pd.isna(alcohol):
        try:
            if float(alcohol) > 0:
                tokens.append("EXPOSURE:maternal_alcohol_use")
        except:
            pass

    # ─── MEDIATORS ───────────────────────────────────────
    # Parity
    parity = safe(row.get('v201', np.nan))
    if not pd.isna(parity):
        try:
            parity = int(parity)
            if parity == 0:
                tokens.append("MEDIATOR:nulliparous")
            elif parity <= 2:
                tokens.append("MEDIATOR:low_parity")
            elif parity <= 4:
                tokens.append("MEDIATOR:moderate_parity")
            else:
                tokens.append("MEDIATOR:high_parity")
        except:
            pass

    # Age
    age = safe(row.get('v012', np.nan))
    if not pd.isna(age):
        try:
            age = int(age)
            if age < 20:
                tokens.append("MEDIATOR:adolescent")
            elif age <= 34:
                tokens.append("MEDIATOR:prime_reproductive_age")
            else:
                tokens.append("MEDIATOR:advanced_maternal_age")
        except:
            pass

    # ANC visits
    anc = safe(row.get('m14_1', np.nan))
    if not pd.isna(anc):
        try:
            anc = int(anc)
            if anc == 0:
                tokens.append("MEDIATOR:no_anc")
            elif anc < 4:
                tokens.append("MEDIATOR:inadequate_anc")
            else:
                tokens.append("MEDIATOR:adequate_anc")
        except:
            pass

    # Contraceptive use
    contra = safe(row.get('v313', np.nan))
    if not pd.isna(contra):
        try:
            if int(contra) == 3:
                tokens.append("MEDIATOR:modern_contraception")
            elif int(contra) > 0:
                tokens.append("MEDIATOR:traditional_contraception")
            else:
                tokens.append("MEDIATOR:no_contraception")
        except:
            pass

    # Pregnancy interval (GR)
    short_interval = safe(row.get('gr_short_interval_pct', np.nan))
    if not pd.isna(short_interval):
        try:
            if float(short_interval) > 30:
                tokens.append("MEDIATOR:short_birth_interval")
        except:
            pass

    # ─── HUSBAND/PARTNER (CR) ─────────────────────────────
    husband_edu = safe(row.get('cr_husband_edu_level', np.nan))
    if not pd.isna(husband_edu):
        try:
            edu_map_h = {0:'no_education', 1:'primary', 2:'secondary', 3:'higher'}
            h_edu = edu_map_h.get(int(husband_edu), 'unknown')
            tokens.append(f"HUSBAND:education_{h_edu}")
        except:
            pass

    husband_age = safe(row.get('cr_husband_age', np.nan))
    wife_age = safe(row.get('v012', np.nan))
    if not pd.isna(husband_age) and not pd.isna(wife_age):
        try:
            age_gap = float(husband_age) - float(wife_age)
            if age_gap > 10:
                tokens.append("HUSBAND:large_age_gap")
            elif age_gap > 5:
                tokens.append("HUSBAND:moderate_age_gap")
            else:
                tokens.append("HUSBAND:small_age_gap")
        except:
            pass

    husband_alcohol = safe(row.get('cr_husband_alcohol', np.nan))
    if not pd.isna(husband_alcohol):
        try:
            if int(husband_alcohol) == 1:
                tokens.append("HUSBAND:drinks_alcohol")
        except:
            pass

    ipv_severe = safe(row.get('cr_ipv_physical_severe', np.nan))
    if not pd.isna(ipv_severe):
        try:
            if int(ipv_severe) == 1:
                tokens.append("MEDIATOR:severe_ipv_experienced")
        except:
            pass

    n_wives = safe(row.get('cr_husband_n_wives', np.nan))
    if not pd.isna(n_wives):
        try:
            if int(n_wives) > 1:
                tokens.append("HUSBAND:polygynous")
        except:
            pass

    # ─── CHILD OUTCOMES (KR cluster-level) ───────────────
    stunting = safe(row.get('kr_stunting_pct', np.nan))
    if not pd.isna(stunting):
        try:
            s = float(stunting)
            if s > 40:
                tokens.append("CLUSTER:high_stunting_burden")
            elif s > 20:
                tokens.append("CLUSTER:moderate_stunting_burden")
            else:
                tokens.append("CLUSTER:low_stunting_burden")
        except:
            pass

    wasting = safe(row.get('kr_wasting_pct', np.nan))
    if not pd.isna(wasting):
        try:
            w = float(wasting)
            if w > 15:
                tokens.append("CLUSTER:high_wasting_burden")
            elif w > 5:
                tokens.append("CLUSTER:moderate_wasting_burden")
            else:
                tokens.append("CLUSTER:low_wasting_burden")
        except:
            pass

    child_anaemia = safe(row.get('kr_child_anaemia_pct', np.nan))
    if not pd.isna(child_anaemia):
        try:
            ca = float(child_anaemia)
            if ca > 60:
                tokens.append("CLUSTER:high_child_anaemia")
            elif ca > 30:
                tokens.append("CLUSTER:moderate_child_anaemia")
            else:
                tokens.append("CLUSTER:low_child_anaemia")
        except:
            pass

    # Dietary diversity (GR cluster-level)
    for var, label in [
        ('gr_dark_greens', 'dark_greens'),
        ('gr_animal_protein', 'animal_protein'),
        ('gr_organ_meat', 'organ_meat'),
        ('gr_fish', 'fish'),
        ('gr_palm_oil', 'palm_oil'),
    ]:
        val = safe(row.get(var, np.nan))
        if not pd.isna(val):
            try:
                if float(val) > 0.5:
                    tokens.append(f"DIET:{label}_adequate")
                else:
                    tokens.append(f"DIET:{label}_low")
            except:
                pass

    # ─── BIOMARKERS ──────────────────────────────────────
    hb = safe(row.get('v453', np.nan))
    if not pd.isna(hb):
        try:
            hb_val = float(hb) / 10
            if hb_val < 99:
                if hb_val < 8.0:
                    tokens.append("BIOMARKER:severe_anaemia")
                elif hb_val < 10.0:
                    tokens.append("BIOMARKER:moderate_anaemia")
                elif hb_val < 11.0:
                    tokens.append("BIOMARKER:mild_anaemia")
                else:
                    tokens.append("BIOMARKER:normal_haemoglobin")
        except:
            pass

    # Anaemia level
    anaemia_level = safe(row.get('v457', np.nan))
    if not pd.isna(anaemia_level):
        try:
            al = int(anaemia_level)
            level_map = {1:'severe', 2:'moderate', 3:'mild', 4:'none'}
            tokens.append(f"OUTCOME:anaemia_{level_map.get(al, 'unknown')}")
        except:
            pass

    # Pregnancy loss (GR)
    preg_loss = safe(row.get('gr_pregnancy_loss_pct', np.nan))
    if not pd.isna(preg_loss):
        try:
            if float(preg_loss) > 20:
                tokens.append("OUTCOME:high_pregnancy_loss_cluster")
        except:
            pass

    # ─── EQUITY MARKERS ──────────────────────────────────
    tokens.append(f"EQUITY:{zone}")
    tokens.append(f"EQUITY:{wealth}")

    # Decision autonomy
    decision = safe(row.get('v743a', np.nan))
    if not pd.isna(decision):
        try:
            if int(decision) == 1:
                tokens.append("EQUITY:health_decision_autonomous")
            elif int(decision) in [2, 3]:
                tokens.append("EQUITY:health_decision_shared")
            else:
                tokens.append("EQUITY:health_decision_husband_controlled")
        except:
            pass

    # Financial autonomy
    bank = safe(row.get('v170', np.nan))
    if not pd.isna(bank):
        try:
            if int(bank) == 1:
                tokens.append("EQUITY:has_bank_account")
        except:
            pass

    return " | ".join(tokens)


if __name__ == "__main__":
    import sys
    sys.path.append('/Users/theoneglobal/epicause_ng')
    df = pd.read_parquet(
        "/Users/theoneglobal/epicause_ng/data/processed/ndhs2024_merged.parquet"
    )
    print(f"Dataset: {df.shape[0]:,} records, {df.shape[1]:,} vars")
    sample = df.sample(3, random_state=42)
    for i, (_, row) in enumerate(sample.iterrows()):
        token = tokenise_record(row)
        print(f"\nRecord {i+1}:")
        print(token)
        print(f"Token length: {len(token.split('|'))} fields")
