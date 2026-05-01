import pyreadstat
import pandas as pd

df, meta = pyreadstat.read_sav("/Users/theoneglobal/epicause_ng/data/raw/MICS2021/Nigeria MICS6 SPSS Datasets/ch.sav")

print("All columns:")
for c in df.columns:
    nn = df[c].notna().sum()
    if nn > 1000:
        print(f"  {c}: {nn:,} non-null — sample: {df[c].dropna().unique()[:3].tolist()}")
