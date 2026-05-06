import sys
sys.path.append('/Users/theoneglobal/epicause_ng')
import pandas as pd
import pyreadstat

print("="*60)
print("ALAAFIA — FULL DATA MERGE")
print("IR + HR + GC (existing) + KR + GR + CR")
print("="*60)

print("\nLoading existing merged dataset (IR + HR + GC)...")
df = pd.read_parquet(
    "/Users/theoneglobal/epicause_ng/data/processed/ndhs2024_merged.parquet"
)
print(f"Base: {df.shape[0]:,} records, {df.shape[1]:,} vars")

# ─── KR MERGE ────────────────────────────────────────────
print("\n[1/3] Loading KR (Children under 5)...")
df_kr, _ = pyreadstat.read_dta(
    "/Users/theoneglobal/epicause_ng/data/raw/NGKR8BDT/NGKR8BFL.dta",
    usecols=[
        'v001', 'bidx',
        'hw70', 'hw71', 'hw72', 'hw73',
        'hw53', 'hw57', 'hw57a',
        'h22', 'h31', 'h34',
        'h42', 'h43', 'h70a', 'h70c',
        'h47', 'h71', 'ml0',
        'v414h', 'v414j', 'v465',
        's473aa', 's473ab', 's473ac', 's473ad',
        'mnb1', 'mnb6', 'm77',
    ]
)
print(f"  KR loaded: {df_kr.shape[0]:,} children")

kr_agg = df_kr.groupby('v001').agg(
    kr_stunting_pct     =('hw70',    lambda x: ((x/100) < -2).mean() * 100),
    kr_wasting_pct      =('hw71',    lambda x: ((x/100) < -2).mean() * 100),
    kr_underweight_pct  =('hw72',    lambda x: ((x/100) < -2).mean() * 100),
    kr_haz_mean         =('hw70',    lambda x: (x/100).mean()),
    kr_whz_mean         =('hw71',    lambda x: (x/100).mean()),
    kr_child_anaemia_pct=('hw57a',   lambda x: (x < 4).mean() * 100),
    kr_fever_pct        =('h22',     lambda x: (x == 1).mean() * 100),
    kr_cough_pct        =('h31',     lambda x: (x == 1).mean() * 100),
    kr_vitamin_a_pct    =('h34',     lambda x: (x == 1).mean() * 100),
    kr_iron_supp_pct    =('h42',     lambda x: (x == 1).mean() * 100),
    kr_deworming_pct    =('h43',     lambda x: (x == 1).mean() * 100),
    kr_growth_monitor_pct=('h70a',   lambda x: (x == 1).mean() * 100),
    kr_muac_monitor_pct =('h70c',    lambda x: (x == 1).mean() * 100),
    kr_itn_child_pct    =('ml0',     lambda x: (x > 0).mean() * 100),
    kr_postnatal_dep_pct=('s473ab',  lambda x: (x == 1).mean() * 100),
    kr_postnatal_anx_pct=('s473aa',  lambda x: (x == 1).mean() * 100),
    kr_postnatal_sui_pct=('s473ad',  lambda x: (x == 1).mean() * 100),
    kr_skin_to_skin_pct =('m77',     lambda x: (x == 1).mean() * 100),
    kr_n_children       =('bidx',    'count'),
).reset_index()

df = df.merge(kr_agg, on='v001', how='left')
print(f"  After KR merge: {df.shape[1]:,} vars, coverage: {df['kr_stunting_pct'].notna().mean()*100:.1f}%")

# ─── GR MERGE ────────────────────────────────────────────
print("\n[2/3] Loading GR (Pregnancies)...")
df_gr, _ = pyreadstat.read_dta(
    "/Users/theoneglobal/epicause_ng/data/raw/NGGR8BDT/NGGR8BFL.dta",
    usecols=[
        'v001', 'v002', 'v003',
        'p32', 'p5', 'p7', 'p11', 'p20', 'p0',
        'v472j', 'v472h', 'v472n', 'v472m', 'v472o',
        'v472i', 'v472u', 'v472t',
        'v463a', 'v485a',
        'v483a', 'v467b', 'v467c', 'v467d',
        'v484a', 'v484b',
        's916a', 'v636',
        'v744a', 'v744d', 'v744e',
        'v745a', 'v745b', 'v739',
        'v367a',
    ]
)
print(f"  GR loaded: {df_gr.shape[0]:,} pregnancies")

gr_agg = df_gr.groupby(['v001','v002','v003']).agg(
    gr_stillbirth_pct       =('p32',   lambda x: (x == 2).mean() * 100),
    gr_miscarriage_pct      =('p32',   lambda x: (x == 3).mean() * 100),
    gr_pregnancy_loss_pct   =('p32',   lambda x: (x.isin([2,3])).mean() * 100),
    gr_child_died_pct       =('p5',    lambda x: (x == 0).mean() * 100),
    gr_short_interval_pct   =('p11',   lambda x: (x < 18).mean() * 100),
    gr_preterm_pct          =('p20',   lambda x: (x < 8).mean() * 100),
    gr_dark_greens          =('v472j', lambda x: (x == 1).mean()),
    gr_animal_protein       =('v472h', lambda x: (x == 1).mean()),
    gr_fish                 =('v472n', lambda x: (x == 1).mean()),
    gr_organ_meat           =('v472m', lambda x: (x == 1).mean()),
    gr_palm_oil             =('v472u', lambda x: (x == 1).mean()),
    gr_ultra_processed      =('v472t', lambda x: (x == 1).mean()),
    gr_smokes               =('v463a', lambda x: (x == 1).mean()),
    gr_alcohol_days         =('v485a', 'mean'),
    gr_travel_time_min      =('v483a', 'mean'),
    gr_permission_problem   =('v467b', lambda x: (x == 1).mean()),
    gr_money_problem        =('v467c', lambda x: (x == 1).mean()),
    gr_distance_problem     =('v467d', lambda x: (x == 1).mean()),
    gr_breast_screened      =('v484a', lambda x: (x > 0).mean()),
    gr_cervical_screened    =('v484b', lambda x: (x > 0).mean()),
    gr_domestic_hrs         =('s916a', 'mean'),
    gr_pressured_pregnant   =('v636',  lambda x: (x == 1).mean()),
    gr_ipv_justified_any    =('v744e', lambda x: (x == 1).mean()),
    gr_owns_house           =('v745a', lambda x: (x.isin([1,2])).mean()),
    gr_owns_land            =('v745b', lambda x: (x.isin([1,2])).mean()),
    gr_pregnancy_unwanted_pct=('v367a',lambda x: (x == 3).mean() * 100),
).reset_index()

df = df.merge(gr_agg, on=['v001','v002','v003'], how='left')
print(f"  After GR merge: {df.shape[1]:,} vars, coverage: {df['gr_stillbirth_pct'].notna().mean()*100:.1f}%")

# ─── CR MERGE ────────────────────────────────────────────
print("\n[3/3] Loading CR (Couples)...")
df_cr, _ = pyreadstat.read_dta(
    "/Users/theoneglobal/epicause_ng/data/raw/NGCR8BDT/NGCR8BFL.dta",
    usecols=[
        'v001', 'v002', 'v003',
        'mv106', 'mv714', 'mv012',
        'mv463a', 'mv463z', 'mv171a',
        'mv505', 'mv836',
        'd113', 'd114', 'd102',
        'd104', 'd106', 'd107', 'd108', 'd111',
        'd101a', 'd101c', 'd101d',
        'mv249', 'mv253',
        'v632', 'v850a', 'v850b',
        'mv825', 'mv828',
    ]
)
print(f"  CR loaded: {df_cr.shape[0]:,} couples")

cr_agg = df_cr.groupby(['v001','v002','v003']).agg(
    cr_husband_edu_level    =('mv106', 'first'),
    cr_husband_age          =('mv012', 'first'),
    cr_husband_working      =('mv714', 'first'),
    cr_husband_smokes       =('mv463a','first'),
    cr_husband_internet     =('mv171a','first'),
    cr_husband_n_wives      =('mv505', 'first'),
    cr_husband_partners     =('mv836', 'first'),
    cr_husband_alcohol      =('d113',  'first'),
    cr_husband_alcohol_freq =('d114',  'first'),
    cr_n_control_behaviours =('d102',  'first'),
    cr_ipv_emotional        =('d104',  'first'),
    cr_ipv_physical_severe  =('d107',  'first'),
    cr_ipv_sexual           =('d108',  'first'),
    cr_ipv_injuries         =('d111',  'first'),
    cr_husband_jealous      =('d101a', 'first'),
    cr_husband_limits_family=('d101d', 'first'),
    cr_husband_at_anc       =('mv249', 'first'),
    cr_husband_at_delivery  =('mv253', 'first'),
    cr_contraception_decider=('v632',  'first'),
    cr_wife_can_refuse_sex  =('v850a', 'first'),
    cr_husband_hiv_tested   =('mv828', 'first'),
).reset_index()

df = df.merge(cr_agg, on=['v001','v002','v003'], how='left')
print(f"  After CR merge: {df.shape[1]:,} vars, coverage: {df['cr_husband_edu_level'].notna().mean()*100:.1f}%")

# ─── SAVE ────────────────────────────────────────────────
print("\nSaving complete merged dataset...")
out_path = "/Users/theoneglobal/epicause_ng/data/processed/ndhs2024_merged.parquet"
df.to_parquet(out_path, index=False)

print(f"\n{'='*60}")
print(f"FULL MERGE COMPLETE")
print(f"Records: {df.shape[0]:,}")
print(f"Variables: {df.shape[1]:,}")
print(f"\nCoverage:")
print(f"  KR (child data):   {df['kr_stunting_pct'].notna().mean()*100:.1f}%")
print(f"  GR (pregnancy):    {df['gr_stillbirth_pct'].notna().mean()*100:.1f}%")
print(f"  CR (couples):      {df['cr_husband_edu_level'].notna().mean()*100:.1f}%")
print(f"\nKey stats:")
print(f"  Mean stunting:     {df['kr_stunting_pct'].mean():.1f}%")
print(f"  Mean wasting:      {df['kr_wasting_pct'].mean():.1f}%")
print(f"  Mean child anaemia:{df['kr_child_anaemia_pct'].mean():.1f}%")
print(f"{'='*60}")
