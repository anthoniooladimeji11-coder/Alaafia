"""
Alaafia Precompute Script — v2
Stratified by wealth quintile to capture demographic variation in causal pathways.

Runs:
- Tier 1: 6 zones × 5 wealth groups × 3 outcomes = 90 combinations
- Saves after every result — crash-safe
- Produces dominant pathway + alternative pathways per geography

Author: Anthonio Oladimeji
"""

import sys
import json
import os
from datetime import datetime
from collections import Counter

sys.path.append('/Users/theoneglobal/epicause_ng')

import pandas as pd
import numpy as np
from utils.tokeniser import tokenise_record
from utils.data_filter import load_merged_data, filter_by_geography, get_geography_stats
from agents.causal_agents import run_pipeline
from agents.equity_interrogation import run_equity_interrogation

OUTPUT_PATH = '/Users/theoneglobal/Iyawo/backend/src/data/alaafia_precomputed.json'
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

ZONES = ['NC', 'NE', 'NW', 'SE', 'SS', 'SW']
OUTCOMES = ['anaemia', 'stunting', 'wasting']
WEALTH_GROUPS = [1, 2, 3, 4, 5]
WEALTH_LABELS = {1:'poorest', 2:'poor', 3:'middle', 4:'rich', 5:'richest'}

ZONE_NAMES = {
    'NC':'North Central', 'NE':'North East', 'NW':'North West',
    'SE':'South East', 'SS':'South South', 'SW':'South West',
}

def filter_by_zone_wealth(df, zone, wealth, outcome, sample_n=1):
    zone_codes = {'NC':1,'NE':2,'NW':3,'SE':4,'SS':5,'SW':6}
    filtered = df[
        (df['v024'].astype(int) == zone_codes[zone]) &
        (df['v190'].astype(int) == wealth)
    ].copy()
    if outcome == 'anaemia':
        filtered = filtered[filtered['v457'].notna()]
    if len(filtered) == 0:
        return pd.DataFrame()
    return filtered.sample(n=min(sample_n, len(filtered)), random_state=42)

print("Loading NDHS 2024 merged dataset...")
df = load_merged_data()
print(f"Loaded {len(df):,} records\n")

# Load existing results to resume if interrupted
if os.path.exists(OUTPUT_PATH):
    with open(OUTPUT_PATH, 'r') as f:
        results = json.load(f)
    print(f"Resuming — {len(results)} results already computed\n")
else:
    results = {}

total = len(ZONES) * len(OUTCOMES)
done = 0

for zone in ZONES:
    for outcome in OUTCOMES:
        done += 1
        zone_key = f"{zone}:{outcome}"
        print(f"\n[{done}/{total}] Zone: {zone} ({ZONE_NAMES[zone]}) | Outcome: {outcome}")
        print("─" * 55)

        if zone_key in results:
            print(f"  Already computed — skipping")
            continue

        try:
            # Get zone-level stats
            stats = get_geography_stats(df, zone=zone)

            # Run pipeline for each wealth group
            wealth_pathways = {}
            all_pathways = []

            for wealth in WEALTH_GROUPS:
                wealth_label = WEALTH_LABELS[wealth]
                records = filter_by_zone_wealth(df, zone, wealth, outcome, sample_n=1)

                if len(records) == 0:
                    print(f"  [{wealth_label}] No records — skipping")
                    continue

                print(f"  [{wealth_label}] Running pipeline...")
                row = records.iloc[0]
                token = tokenise_record(row)
                result = run_pipeline(token, outcome, zone=zone)

                if 'final_pathway' not in result.get('final', {}):
                    print(f"  [{wealth_label}] Pipeline failed")
                    continue

                equity = run_equity_interrogation(result)
                pathway_data = {
                    'wealth_group': wealth_label,
                    'wealth_code': wealth,
                    'pathway': result['final'].get('final_pathway', ''),
                    'policy': result['final'].get('policy_implication', ''),
                    'equity_flag': result['final'].get('equity_flag', ''),
                    'confidence': result['final'].get('pathway_confidence', 0),
                    'quality_grade': result.get('quality', {}).get('quality_grade', ''),
                    'quality_score': result.get('quality', {}).get('overall_quality', 0),
                    'equity_driver': equity.get('equity_interrogation', {}).get('disparity_primary_driver', ''),
                    'beyond_poverty': equity.get('wealth_analysis', {}).get('beyond_poverty_factor', ''),
                    'structural_recommendation': equity.get('equity_interrogation', {}).get('structural_recommendation', ''),
                    'poverty_explains': equity.get('wealth_analysis', {}).get('poverty_explains_disparity', None),
                }
                wealth_pathways[wealth_label] = pathway_data
                all_pathways.append(pathway_data)
                print(f"  [{wealth_label}] ✓ Grade {pathway_data['quality_grade']} — {pathway_data['pathway'][:60]}...")

            if not all_pathways:
                print(f"  No successful pathways for {zone}/{outcome}")
                continue

            # Find dominant pathway — highest quality score
            dominant = max(all_pathways, key=lambda x: x.get('quality_score', 0))

            # Find alternative pathways — different from dominant
            alternatives = [
                p for p in all_pathways
                if p['wealth_group'] != dominant['wealth_group']
                and p.get('quality_score', 0) > 0.4
            ][:2]

            # Poverty pattern — does the pathway differ by wealth?
            poverty_varies = len(set(
                p['pathway'][:40] for p in all_pathways
            )) > 1

            results[zone_key] = {
                'zone': zone,
                'zone_name': ZONE_NAMES[zone],
                'outcome': outcome,
                'stats': stats,
                'dominant_pathway': dominant,
                'alternative_pathways': alternatives,
                'wealth_stratified': wealth_pathways,
                'poverty_varies_pathway': poverty_varies,
                'n_wealth_groups_computed': len(all_pathways),
                'computed_at': datetime.now().isoformat(),
            }

            # Save after every zone/outcome combination
            with open(OUTPUT_PATH, 'w') as f:
                json.dump(results, f, indent=2)

            print(f"\n  ✓ Saved {zone_key}")
            print(f"  ✓ Dominant pathway: {dominant['pathway'][:70]}...")
            print(f"  ✓ Wealth groups computed: {len(all_pathways)}/5")
            print(f"  ✓ Pathway varies by wealth: {poverty_varies}")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            continue

print(f"\n{'='*60}")
print(f"PRECOMPUTE COMPLETE")
print(f"Results: {len(results)}/{total}")
print(f"Saved to: {OUTPUT_PATH}")
print(f"{'='*60}")
