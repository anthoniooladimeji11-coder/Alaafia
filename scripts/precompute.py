"""
Alaafia Precompute Script — v3
Stratified by wealth quintile, 3 records per cell for stability.
Aggregates pathways across records to find the most consistent one.

Runs:
- Tier 1: 6 zones × 3 outcomes × 5 wealth groups × 3 records = 270 pipeline calls
- Saves after every zone/outcome combination — crash-safe resume

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
from utils.data_filter import load_merged_data, get_geography_stats
from agents.causal_agents import run_pipeline
from agents.equity_interrogation import run_equity_interrogation

OUTPUT_PATH = '/Users/theoneglobal/Iyawo/backend/src/data/alaafia_precomputed.json'
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

ZONES = ['NC', 'NE', 'NW', 'SE', 'SS', 'SW']
OUTCOMES = ['anaemia', 'stunting', 'wasting']
WEALTH_GROUPS = [1, 2, 3, 4, 5]
WEALTH_LABELS = {1:'poorest', 2:'poor', 3:'middle', 4:'rich', 5:'richest'}
RECORDS_PER_CELL = 3

ZONE_NAMES = {
    'NC':'North Central', 'NE':'North East', 'NW':'North West',
    'SE':'South East', 'SS':'South South', 'SW':'South West',
}

ZONE_CODES = {'NC':1,'NE':2,'NW':3,'SE':4,'SS':5,'SW':6}

def filter_by_zone_wealth(df, zone, wealth, outcome, sample_n=3):
    filtered = df[
        (df['v024'].astype(int) == ZONE_CODES[zone]) &
        (df['v190'].astype(int) == wealth)
    ].copy()
    if outcome == 'anaemia':
        filtered = filtered[filtered['v457'].notna()]
    if len(filtered) == 0:
        return pd.DataFrame()
    # Use different random seeds for each record
    return filtered.sample(n=min(sample_n, len(filtered)), random_state=99)

def aggregate_pathways(pathway_results):
    """
    Aggregate multiple pathway results into a single representative one.
    Uses the highest quality score as dominant.
    Checks consistency across records.
    """
    if not pathway_results:
        return None

    # Find dominant — highest quality score
    dominant = max(pathway_results, key=lambda x: x.get('quality_score', 0))

    # Check pathway consistency — do records agree on the primary driver?
    pathway_texts = [p.get('pathway', '')[:40] for p in pathway_results]
    unique_starts = len(set(pathway_texts))
    consistency = 1.0 - (unique_starts - 1) / max(len(pathway_results), 1)

    dominant['pathway_consistency'] = round(consistency, 2)
    dominant['n_records'] = len(pathway_results)
    dominant['records_agree'] = unique_starts == 1

    # Average confidence across records
    confidences = [p.get('confidence', 0) for p in pathway_results if p.get('confidence')]
    if confidences:
        dominant['mean_confidence'] = round(sum(confidences) / len(confidences), 3)

    return dominant

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
            existing = results[zone_key]
            # Check if already has multi-record data
            dominant = existing.get('dominant_pathway', {})
            if dominant.get('n_records', 1) >= RECORDS_PER_CELL:
                print(f"  Already computed with {dominant.get('n_records')} records — skipping")
                continue
            print(f"  Recomputing with {RECORDS_PER_CELL} records per cell...")

        try:
            stats = get_geography_stats(df, zone=zone)
            wealth_pathways = {}
            all_pathways = []

            for wealth in WEALTH_GROUPS:
                wealth_label = WEALTH_LABELS[wealth]
                records = filter_by_zone_wealth(df, zone, wealth, outcome, sample_n=RECORDS_PER_CELL)

                if len(records) == 0:
                    print(f"  [{wealth_label}] No records — skipping")
                    continue

                print(f"  [{wealth_label}] Running {len(records)} records...")
                cell_results = []

                for idx, (_, row) in enumerate(records.iterrows()):
                    token = tokenise_record(row)
                    result = run_pipeline(token, outcome, zone=zone)

                    if 'final_pathway' not in result.get('final', {}):
                        print(f"    Record {idx+1} failed")
                        continue

                    equity = run_equity_interrogation(result)
                    cell_results.append({
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
                    })
                    print(f"    Record {idx+1} ✓ Grade {cell_results[-1]['quality_grade']}")

                if not cell_results:
                    continue

                # Aggregate across records in this cell
                aggregated = aggregate_pathways(cell_results)
                wealth_pathways[wealth_label] = aggregated
                all_pathways.extend(cell_results)

                consistency = aggregated.get('pathway_consistency', 0)
                print(f"  [{wealth_label}] Aggregated {len(cell_results)} records | Consistency: {consistency:.0%}")

            if not all_pathways:
                print(f"  No successful pathways for {zone}/{outcome}")
                continue

            # Find dominant across all wealth groups
            dominant = max(all_pathways, key=lambda x: x.get('quality_score', 0))
            dominant = aggregate_pathways([p for p in all_pathways
                                          if p['wealth_group'] == dominant['wealth_group']])

            # Alternative pathways from other wealth groups
            alternatives = [
                aggregate_pathways([p for p in all_pathways if p['wealth_group'] == wl])
                for wl in set(p['wealth_group'] for p in all_pathways)
                if wl != dominant.get('wealth_group')
            ]
            alternatives = [a for a in alternatives if a and a.get('quality_score', 0) > 0.4][:2]

            poverty_varies = len(set(p['pathway'][:40] for p in all_pathways)) > 1

            results[zone_key] = {
                'zone': zone,
                'zone_name': ZONE_NAMES[zone],
                'outcome': outcome,
                'stats': stats,
                'dominant_pathway': dominant,
                'alternative_pathways': alternatives,
                'wealth_stratified': wealth_pathways,
                'poverty_varies_pathway': poverty_varies,
                'n_wealth_groups_computed': len(wealth_pathways),
                'total_records_analysed': len(all_pathways),
                'computed_at': datetime.now().isoformat(),
            }

            with open(OUTPUT_PATH, 'w') as f:
                json.dump(results, f, indent=2)

            print(f"\n  ✓ Saved {zone_key}")
            print(f"  ✓ Total records: {len(all_pathways)}")
            print(f"  ✓ Dominant: Grade {dominant.get('quality_grade')} — {dominant.get('pathway','')[:60]}...")
            print(f"  ✓ Pathway varies by wealth: {poverty_varies}")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            continue

print(f"\n{'='*60}")
print(f"PRECOMPUTE v3 COMPLETE")
print(f"Results: {len(results)}/{total}")
print(f"Saved to: {OUTPUT_PATH}")
print(f"{'='*60}")
