import pyreadstat
import pandas as pd

df, meta = pyreadstat.read_dta("/Users/theoneglobal/epicause_ng/data/raw/NGCR8BDT/NGCR8BFL.dta")

zone_map = {1:'NC',2:'NE',3:'NW',4:'SE',5:'SS',6:'SW'}
edu_map = {0:'none',1:'primary',2:'secondary',3:'higher'}

df['zone'] = df['v024'].astype(int).map(zone_map)
df['any_anaemia'] = (df['v457'].astype(float) < 4).astype(int)
df['w_edu'] = df['v106'].astype(int).map(edu_map)
df['m_edu'] = df['mv106'].astype(int).map(edu_map)
df['m_alcohol'] = df['mv171a'].astype(int)
df['m_age'] = df['mv012'].astype(int)
df['w_age'] = df['v012'].astype(int)
df['age_gap'] = df['m_age'] - df['w_age']

sub = df[df['v457'].notna()].copy()

print("=== WOMEN ANAEMIA BY HUSBAND EDUCATION ===")
print(sub.groupby('m_edu')['any_anaemia'].mean().round(3)*100)

print("\n=== WOMEN ANAEMIA BY HUSBAND ALCOHOL USE ===")
print(sub.groupby('m_alcohol')['any_anaemia'].mean().round(3)*100)

print("\n=== AGE GAP HUSBAND-WIFE BY ZONE ===")
print(df.groupby('zone')['age_gap'].agg(['mean','median']).round(1))

print("\n=== HUSBAND VS WIFE EDUCATION BY ZONE ===")
for zone, grp in df.groupby('zone'):
    w_none = (grp['v106']==0).mean()*100
    m_none = (grp['mv106']==0).mean()*100
    print(f"  {zone}: wife no edu={w_none:.1f}%  husband no edu={m_none:.1f}%")
