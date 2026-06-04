"""
Alaafia State-Level Precompute Script
Runs the full pipeline for all 37 Nigerian states × 3 outcomes
3 records per state (no wealth stratification at state level — 
sample sizes too small for 5-group split)

Output: alaafia_precomputed_states.json

Author: Anthonio Oladimeji
"""

import sys
import json
import os
from datetime import datetime

sys.path.append('/Users/theoneglobal/epicause_ng')

import pandas as pd
from utils.tokeniser import tokenise_record
from utils.data_filter import load_merged_data, get_geography_stats
from agents.causal_agents import run_pipeline
from agents.equity_interrogation import run_equity_interrogation

OUTPUT_PATH = '/Users/theoneglobal/Iyawo/backend/src/data/alaafia_precomputed_states.json'
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

STATE_MAP = {
    1:'Sokoto', 2:'Zamfara', 3:'Katsina', 4:'Jigawa',
    5:'Yobe', 6:'Borno', 7:'Adamawa', 8:'Gombe', 9:'Bauchi',
    10:'Kano', 11:'Kaduna', 12:'Kebbi', 13:'Niger', 14:'FCT Abuja',
    15:'Nasarawa', 16:'Plateau', 17:'Taraba', 18:'Benue',
    19:'Kogi', 20:'Kwara', 21:'Oyo', 22:'Osun', 23:'Ekiti',
    24:'Ondo', 25:'Edo', 26:'Anambra', 27:'Enugu', 28:'Ebonyi',
    29:'Cross River', 30:'Akwa Ibom', 31:'Abia', 32:'Imo',
    33:'Rivers', 34:'Bayelsa', 35:'Delta', 36:'Lagos', 37:'Ogun',
}

STATES_BY_ZONE = {
    'NC':[13,14,15,16,18,19,20],
    'NE':[5,6,7,8,9,17],
    'NW':[1,2,3,4,10,11,12],
    'SE':[26,27,28,31,32],
    'SS':[25,29,30,33,34,35],
    'SW':[21,22,23,24,36,37],
}

STATE_TO_ZONE = {}
for zone, states in STATES_BY_ZONE.items():
    for s in states:
        STATE_TO_ZONE[s] = zone

OUTCOMES = ['anaemia', 'stunting', 'wasting']
RECORDS_PER_STATE = 3

print("Loading NDHS 2024 merged dataset...")
df = load_merged_data()
print(f"Loaded {len(df):,} records\n")

# Load existing results
if os.path.exists(OUTPUT_PATH):
    with open(OUTPUT_PATH, 'r') as f:
        results = json.load(f)
    print(f"Resuming — {len(results)} results already computed\n")
else:
    results = {}

total = len(STATE_MAP) * len(OUTCOMES)
done = 0

for state_code, state_name in STATE_MAP.items():
    zone = STATE_TO_ZONE.get(state_code, 'unknown')

    for outcome in OUTCOMES:
        done += 1
        key = f"state_{state_code}:{outcome}"
        print(f"\n[{done}/{total}] {state_name} (State {state_code}, {zone}) | {outcome}")
        print("─" * 55)

        if key in results:
            print(f"  Already computed — skipping")
            continue

        try:
            # Filter records for this state
            state_df = df[df['sstate'].astype(int) == state_code].copy()

            if outcome == 'anaemia':
                state_df = state_df[state_df['v457'].notna()]

            if len(state_df) == 0:
                print(f"  No records found — skipping")
                continue

            print(f"  Available records: {len(state_df):,}")

            # Get stats
            stats = get_geography_stats(df, state_code=state_code)

            # Sample records
            n = min(RECORDS_PER_STATE, len(state_df))
            sampled = state_df.sample(n=n, random_state=42)

            # Run pipeline on each record
            state_results = []
            for idx, (_, row) in enumerate(sampled.iterrows()):
                token = tokenise_record(row)
                result = run_pipeline(token, outcome, zone=zone)

                if 'final_pathway' not in result.get('final', {}):
                    print(f"  Record {idx+1} failed")
                    continue

                equity = run_equity_interrogation(result)
                state_results.append({
                    'pathway': result['final'].get('final_pathway', ''),
                    'policy': result['final'].get('policy_implication', ''),
                    'equity_flag': result['final'].get('equity_flag', ''),
                    'confidence': result['final'].get('pathway_confidence', 0),
                    'quality_grade': result.get('quality', {}).get('quality_grade', ''),
                    'quality_score': result.get('quality', {}).get('overall_quality', 0),
                    'equity_driver': equity.get('equity_interrogation', {}).get('disparity_primary_driver', ''),
                    'beyond_poverty': equity.get('wealth_analysis', {}).get('beyond_poverty_factor', ''),
                    'structural_recommendation': equity.get('equity_interrogation', {}).get('structural_recommendation', ''),
                })
                print(f"  Record {idx+1} ✓ Grade {state_results[-1]['quality_grade']}")

            if not state_results:
                print(f"  No successful results")
                continue

            # Pick dominant
            dominant = max(state_results, key=lambda x: x.get('quality_score', 0))
            dominant['n_records'] = len(state_results)

            results[key] = {
                'state_code': state_code,
                'state_name': state_name,
                'zone': zone,
                'outcome': outcome,
                'stats': stats,
                'dominant_pathway': dominant,
                'all_pathways': state_results,
                'n_records_analysed': len(state_results),
                'computed_at': datetime.now().isoformat(),
            }

            with open(OUTPUT_PATH, 'w') as f:
                json.dump(results, f, indent=2)

            print(f"  ✓ Saved {key}")
            print(f"  ✓ Grade {dominant['quality_grade']} — {dominant['pathway'][:60]}...")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            continue

print(f"\n{'='*60}")
print(f"STATE PRECOMPUTE COMPLETE")
print(f"Results: {len(results)}/{total}")
print(f"Saved to: {OUTPUT_PATH}")
print(f"{'='*60}")
