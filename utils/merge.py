import pyreadstat
import pandas as pd

print("Loading files...")

ir, _ = pyreadstat.read_dta("/Users/theoneglobal/epicause_ng/data/raw/NGIR8BDT/NGIR8BFL.dta")
hr, _ = pyreadstat.read_dta("/Users/theoneglobal/epicause_ng/data/raw/NGHR8BDT/NGHR8BFL.dta")
gc = pd.read_csv("/Users/theoneglobal/epicause_ng/data/raw/NGGC8AFL/NGGC8AFL.csv")

print(f"IR: {ir.shape}, HR: {hr.shape}, GC: {gc.shape}")

# Merge IR + HR on cluster + household
ir['v001'] = ir['v001'].astype(int)
ir['v002'] = ir['v002'].astype(int)
hr['hv001'] = hr['hv001'].astype(int)
hr['hv002'] = hr['hv002'].astype(int)

hr_slim = hr[['hv001','hv002','hv226','hv201','hv205','hv270']].copy()
hr_slim.columns = ['v001','v002','hh_fuel','hh_water','hh_sanitation','hh_wealth']

merged = ir.merge(hr_slim, on=['v001','v002'], how='left')
print(f"IR + HR merged: {merged.shape}")
print(f"HR merge rate: {merged['hh_fuel'].notna().mean()*100:.1f}%")

# Merge with GC on cluster
gc_slim = gc[['DHSCLUST','Travel_Times','Malaria_Prevalence_2020',
              'Rainfall_2020','Enhanced_Vegetation_Index_2020',
              'Nightlights_Composite','ITN_Coverage_2020',
              'Mean_Temperature_2020']].copy()
gc_slim.columns = ['v001','travel_time','malaria_prev','rainfall',
                   'ndvi','nightlights','itn_coverage','mean_temp']

merged = merged.merge(gc_slim, on='v001', how='left')
print(f"+ GC merged: {merged.shape}")
print(f"GC merge rate: {merged['travel_time'].notna().mean()*100:.1f}%")

# Save
merged.to_parquet("/Users/theoneglobal/epicause_ng/data/processed/ndhs2024_merged.parquet")
print("\nSaved to data/processed/ndhs2024_merged.parquet")
print(f"Final shape: {merged.shape}")
