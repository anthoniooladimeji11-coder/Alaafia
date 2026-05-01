import pandas as pd

gc = pd.read_csv("/Users/theoneglobal/epicause_ng/data/raw/NGGC8AFL/NGGC8AFL.csv")

key_vars = ['DHSCLUST', 'Travel_Times', 'Malaria_Prevalence_2020',
            'Rainfall_2020', 'Enhanced_Vegetation_Index_2020',
            'Nightlights_Composite', 'ITN_Coverage_2020',
            'Mean_Temperature_2020', 'Elevation']

print("=== KEY GEOSPATIAL VARIABLES ===")
print(gc[key_vars].describe().round(2))

print("\n=== MISSING VALUES ===")
for v in key_vars:
    nn = gc[v].isna().sum()
    print(f"  {v}: {nn} missing of {len(gc)}")
