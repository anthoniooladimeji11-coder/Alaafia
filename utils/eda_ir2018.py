import pyreadstat
import pandas as pd

df, meta = pyreadstat.read_dta("/Users/theoneglobal/epicause_ng/data/raw/NDHS_2018/NGIR7BDT/NGIR7BFL.DTA")

print("Shape:", df.shape)

zone_map = {1:'NC',2:'NE',3:'NW',4:'SE',5:'SS',6:'SW'}
wealth_map = {1:'poorest',2:'poor',3:'middle',4:'rich',5:'richest'}
anaemia_map = {1:'severe',2:'moderate',3:'mild',4:'none'}

df['zone'] = df['v024'].astype(int).map(zone_map)
df['any_anaemia'] = (df['v457'].astype(float) < 4).astype(int)
df['hb_clean'] = df['v453'] / 10
df.loc[df['hb_clean'] >= 99, 'hb_clean'] = None
df.loc[df['hb_clean'] < 5, 'hb_clean'] = None

sub = df[df['v457'].notna()].copy()

print("\n=== 2018 ANAEMIA BY ZONE ===")
for zone, grp in sub.groupby('zone'):
    pct = grp['any_anaemia'].mean() * 100
    n = len(grp)
    print(f"  {zone}: {pct:.1f}% (n={n:,})")

print("\n=== 2018 vs 2024 COMPARISON ===")
print("Zone    2018_anaemia%   2024_anaemia%   Change")
print("-" * 50)
data_2024 = {'NC':40.1,'NE':41.9,'NW':36.0,'SE':55.4,'SS':46.9,'SW':41.1}
for zone, grp in sub.groupby('zone'):
    pct_2018 = grp['any_anaemia'].mean() * 100
    pct_2024 = data_2024.get(zone, 0)
    change = pct_2024 - pct_2018
    direction = "▲" if change > 0 else "▼"
    print(f"  {zone}      {pct_2018:.1f}%           {pct_2024:.1f}%        {direction}{abs(change):.1f}%")
