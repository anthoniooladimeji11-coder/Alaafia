import sys
sys.path.append('/Users/theoneglobal/epicause_ng')
import pandas as pd
import pyreadstat
import numpy as np

print("Loading data...")
df = pd.read_parquet("/Users/theoneglobal/epicause_ng/data/processed/ndhs2024_merged.parquet")
print(f"Base: {df.shape[0]:,} x {df.shape[1]:,}")

df_mr, _ = pyreadstat.read_dta(
    "/Users/theoneglobal/epicause_ng/data/raw/NGMR8BDT/NGMR8BFL.dta",
    usecols=['mv001','mv176','mv481','mv485a','mv463aa',
             'mv781','mv763a','mv761','mchd02','mchd07',
             'mv744e','sm816k','sm816b']
)
df_mr['mv485a'] = df_mr['mv485a'].where(df_mr['mv485a'] <= 30, np.nan)

# Aggregate properly
mr_agg = df_mr.groupby('mv001').agg(
    mr_hiv_tested_pct   = pd.NamedAgg('mv781',   lambda x: (x==1).mean()*100),
    mr_sti_pct          = pd.NamedAgg('mv763a',  lambda x: (x==1).mean()*100),
    mr_hypertension_pct = pd.NamedAgg('mchd02',  lambda x: (x==1).mean()*100),
    mr_diabetes_pct     = pd.NamedAgg('mchd07',  lambda x: (x==1).mean()*100),
    mr_alcohol_mean     = pd.NamedAgg('mv485a',  'mean'),
    mr_tobacco_pct      = pd.NamedAgg('mv463aa', lambda x: (x==1).mean()*100),
    mr_insurance_pct    = pd.NamedAgg('mv481',   lambda x: (x==1).mean()*100),
    mr_condom_pct       = pd.NamedAgg('mv761',   lambda x: (x==1).mean()*100),
    mr_ipv_pct          = pd.NamedAgg('mv744e',  lambda x: (x==1).mean()*100),
    mr_covid_vax_pct    = pd.NamedAgg('sm816k',  lambda x: (x==1).mean()*100),
    mr_hepb_pct         = pd.NamedAgg('sm816b',  lambda x: (x==1).mean()*100),
    mr_n_men            = pd.NamedAgg('mv781',   'count'),
).reset_index()

mr_agg = mr_agg.rename(columns={'mv001': 'v001'})
print(f"MR aggregated: {mr_agg.shape} | columns: {list(mr_agg.columns[:5])}")

df = df.merge(mr_agg, on='v001', how='left')
print(f"After merge: {df.shape}")
print(f"Coverage: {df['mr_hiv_tested_pct'].notna().mean()*100:.1f}%")

df.to_parquet("/Users/theoneglobal/epicause_ng/data/processed/ndhs2024_merged.parquet", index=False)
print("Saved.")
