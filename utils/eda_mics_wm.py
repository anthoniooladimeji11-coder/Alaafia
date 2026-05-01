import pyreadstat
import pandas as pd

df, meta = pyreadstat.read_sav("/Users/theoneglobal/epicause_ng/data/raw/MICS2021/Nigeria MICS6 SPSS Datasets/wm.sav")

print("=== ZONE VALUES ===")
print(df['zone'].value_counts())

print("\n=== SHAPE & KEY VARS ===")
key = ['zone','HH6','WB4','WB5','wmweight','WDOI','WDOB']
for v in key:
    if v in df.columns:
        print(f"  {v} — non-null: {df[v].notna().sum():,} — sample: {df[v].dropna().unique()[:4].tolist()}")
    else:
        print(f"  {v} — MISSING")

anemia_cols = [c for c in df.columns if 'anemia' in c.lower() or 'anaemia' in c.lower() or 'haem' in c.lower() or 'hemo' in c.lower()]
print(f"\nAnaemia/haemoglobin columns: {anemia_cols}")

wash_cols = [c for c in df.columns if any(x in c.upper() for x in ['WS','WATER','TOILET','FUEL','COOK'])]
print(f"\nWASH columns: {wash_cols[:15]}")
