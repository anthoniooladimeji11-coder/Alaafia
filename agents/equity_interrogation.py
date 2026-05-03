"""
Alaafia — Layer 3: Equity Interrogation
Every accepted causal pathway is stratified by zone and wealth.
Asks: is this pathway operating differently across Nigeria?
Is disparity driven by differential exposure or differential susceptibility?

Author: Anthonio Oladimeji
"""

import subprocess
import json
import re
import pandas as pd
import sys
sys.path.append('/Users/theoneglobal/epicause_ng')
from utils.tokeniser import tokenise_record
from agents.causal_agents import run_pipeline, clean_ollama_output, extract_json

ZONE_PROFILES = {
    "NC": {"stunting": 52.1, "anaemia": 40.1, "poor_sanitation": 24.8, "unimproved_water": 33.6, "solid_fuel": 10.3},
    "NE": {"stunting": 52.1, "anaemia": 41.9, "poor_sanitation": 36.6, "unimproved_water": 34.6, "solid_fuel": 10.9},
    "NW": {"stunting": 35.5, "anaemia": 36.0, "poor_sanitation": 3.4,  "unimproved_water": 29.5, "solid_fuel": 13.3},
    "SE": {"stunting": 19.3, "anaemia": 55.4, "poor_sanitation": 2.7,  "unimproved_water": 14.5, "solid_fuel": 7.1},
    "SS": {"stunting": 20.0, "anaemia": 46.9, "poor_sanitation": 5.9,  "unimproved_water": 16.8, "solid_fuel": 8.1},
    "SW": {"stunting": 21.2, "anaemia": 41.1, "poor_sanitation": 1.2,  "unimproved_water": 5.4,  "solid_fuel": 11.3},
}

WEALTH_ANAEMIA = {
    "poorest": {"NC": 44.3, "NE": 45.2, "NW": 41.3, "SE": 68.1, "SS": 60.0, "SW": 34.4},
    "richest": {"NC": 29.4, "NE": 38.5, "NW": 32.7, "SE": 48.7, "SS": 41.2, "SW": 40.6},
}


def ask_ollama(prompt: str, model: str = "llama3.1:8b") -> str:
    result = subprocess.run(
        ["ollama", "run", model, prompt],
        capture_output=True, text=True, timeout=240
    )
    return result.stdout.strip()


def interrogate_pathway_equity(
    final_pathway: str,
    outcome: str,
    zone: str,
    policy_implication: str
) -> dict:
    """
    Layer 3 — Equity Interrogation.
    Takes an accepted causal pathway and asks three equity questions.
    """

    zone_data = ZONE_PROFILES.get(zone, {})
    all_zones_outcome = {z: ZONE_PROFILES[z].get(
        "anaemia" if "anaemia" in outcome else "stunting", 0
    ) for z in ZONE_PROFILES}

    highest_zone = max(all_zones_outcome, key=all_zones_outcome.get)
    lowest_zone = min(all_zones_outcome, key=all_zones_outcome.get)
    disparity = all_zones_outcome[highest_zone] - all_zones_outcome[lowest_zone]

    prompt = f"""You are Nigeria's leading health equity researcher.

An accepted causal pathway has been identified:
PATHWAY: {final_pathway}
OUTCOME: {outcome}
ZONE ANALYSED: {zone}

Zone-level outcome data across Nigeria:
{json.dumps(all_zones_outcome, indent=2)}

Highest burden zone: {highest_zone} ({all_zones_outcome[highest_zone]:.1f}%)
Lowest burden zone: {lowest_zone} ({all_zones_outcome[lowest_zone]:.1f}%)
Total disparity: {disparity:.1f} percentage points

Zone structural profile for {zone}:
{json.dumps(zone_data, indent=2)}

Wealth-stratified anaemia data:
Poorest quintile by zone: {json.dumps(WEALTH_ANAEMIA.get('poorest', {}), indent=2)}
Richest quintile by zone: {json.dumps(WEALTH_ANAEMIA.get('richest', {}), indent=2)}

Answer these three equity questions:

1. EXPOSURE DISPARITY: Does the identified pathway operate more strongly in some zones because those zones have higher EXPOSURE to the risk factor? Which zones and why?

2. SUSCEPTIBILITY DISPARITY: Does the pathway operate more strongly in some zones because the SAME exposure produces WORSE outcomes there — due to lower baseline nutrition, weaker health systems, or other vulnerability factors?

3. INTERVENTION EQUITY: Which zone would benefit MOST from intervening on this specific causal pathway? What is the expected equity impact if this intervention were implemented in the highest burden zone?

Return ONLY this JSON:
{{
  "exposure_disparity": {{
    "exists": true,
    "explanation": "which zones have higher exposure and why",
    "primary_zones_affected": ["zone1", "zone2"]
  }},
  "susceptibility_disparity": {{
    "exists": true,
    "explanation": "whether same exposure produces worse outcomes in some zones",
    "primary_zones_affected": ["zone1"]
  }},
  "disparity_primary_driver": "exposure OR susceptibility OR both",
  "highest_impact_intervention_zone": "{highest_zone}",
  "expected_equity_impact": "one sentence on expected reduction in disparity",
  "structural_recommendation": "specific policy recommendation targeting the equity gap"
}}"""

    response = ask_ollama(prompt, "natlas")
    result = extract_json(response)
    result["zone_analysed"] = zone
    result["outcome"] = outcome
    result["pathway"] = final_pathway
    result["disparity_pp"] = round(disparity, 1)
    result["highest_burden_zone"] = highest_zone
    result["lowest_burden_zone"] = lowest_zone
    return result


def wealth_stratified_analysis(outcome: str, zone: str) -> dict:
    """
    Analyse whether the outcome disparity is driven by wealth
    or operates independently of wealth within zones.
    """
    prompt = f"""You are a Nigerian health equity epidemiologist.

Maternal anaemia prevalence by wealth quintile and zone (NDHS 2024):
Poorest: NC=44.3%, NE=45.2%, NW=41.3%, SE=68.1%, SS=60.0%, SW=34.4%
Richest: NC=29.4%, NE=38.5%, NW=32.7%, SE=48.7%, SS=41.2%, SW=40.6%

Key observation: In South East Nigeria, even the RICHEST women have 48.7% anaemia —
higher than the POOREST women in North West (41.3%) and South West (34.4%).

This means SE anaemia is NOT primarily a poverty problem — it operates across wealth quintiles.

For zone {zone} and outcome {outcome}:
1. Is the outcome explained by poverty or does it persist across wealth quintiles?
2. What structural factor beyond poverty explains the zone pattern?
3. What does this mean for intervention design?

Return ONLY this JSON:
{{
  "poverty_explains_disparity": false,
  "evidence": "one sentence citing the wealth-stratified data",
  "beyond_poverty_factor": "what structural factor explains the pattern beyond wealth",
  "intervention_implication": "one sentence on what this means for targeting interventions"
}}"""

    response = ask_ollama(prompt, "natlas")
    result = extract_json(response)
    result["zone"] = zone
    result["outcome"] = outcome
    return result


def run_equity_interrogation(pipeline_result: dict) -> dict:
    """
    Run full Layer 3 equity interrogation on a completed pipeline result.
    """
    final = pipeline_result.get("final", {})
    zone = pipeline_result.get("zone", "unknown")
    outcome = pipeline_result.get("outcome", "unknown")

    if "final_pathway" not in final:
        return {"error": "no final pathway to interrogate"}

    print(f"\n{'='*65}")
    print(f"LAYER 3 — EQUITY INTERROGATION")
    print(f"Zone: {zone} | Outcome: {outcome}")
    print(f"{'='*65}")

    print("\n[Question 1 — Exposure vs Susceptibility Disparity]")
    equity = interrogate_pathway_equity(
        final_pathway=final["final_pathway"],
        outcome=outcome,
        zone=zone,
        policy_implication=final.get("policy_implication", "")
    )

    if "disparity_primary_driver" in equity:
        print(f"  ✓ Primary driver: {equity['disparity_primary_driver']}")
        print(f"  ✓ Highest impact zone: {equity.get('highest_impact_intervention_zone','')}")
        print(f"  ✓ Expected impact: {equity.get('expected_equity_impact','')}")
        print(f"  ✓ Recommendation: {equity.get('structural_recommendation','')}")
    else:
        print(f"  ✗ Parse issue: {equity.get('error','')}")

    print("\n[Question 2 — Wealth Stratification Analysis]")
    wealth = wealth_stratified_analysis(outcome, zone)

    if "poverty_explains_disparity" in wealth:
        print(f"  ✓ Poverty explains disparity: {wealth['poverty_explains_disparity']}")
        print(f"  ✓ Beyond-poverty factor: {wealth.get('beyond_poverty_factor','')}")
        print(f"  ✓ Intervention implication: {wealth.get('intervention_implication','')}")
    else:
        print(f"  ✗ Parse issue: {wealth.get('error','')}")

    return {
        "zone": zone,
        "outcome": outcome,
        "final_pathway": final["final_pathway"],
        "equity_interrogation": equity,
        "wealth_analysis": wealth
    }


if __name__ == "__main__":
    print("Loading NDHS 2024 merged dataset...")
    df = pd.read_parquet(
        "/Users/theoneglobal/epicause_ng/data/processed/ndhs2024_merged.parquet"
    )
    zone_map = {1:'NC',2:'NE',3:'NW',4:'SE',5:'SS',6:'SW'}
    anaemia_sub = df[df['v457'].notna()].copy()

    print("Running full pipeline + equity interrogation on SE and NW records...")
    equity_results = []

    for zone_code, zone_label in [(4, "SE"), (3, "NW")]:
        zone_sub = anaemia_sub[anaemia_sub['v024'].astype(int) == zone_code]
        row = zone_sub.sample(1, random_state=42).iloc[0]
        token = tokenise_record(row)

        print(f"\n--- Running Layer 2 pipeline for {zone_label} ---")
        pipeline_result = run_pipeline(token, "maternal_anaemia", zone=zone_label)

        print(f"\n--- Running Layer 3 equity interrogation for {zone_label} ---")
        equity_result = run_equity_interrogation(pipeline_result)
        equity_results.append(equity_result)

    print(f"\n{'='*65}")
    print("ALAAFIA — LAYERS 2 + 3 COMPLETE")
    print(f"Records processed: {len(equity_results)}")
    successful_equity = sum(1 for r in equity_results
                           if "disparity_primary_driver" in r.get("equity_interrogation", {}))
    print(f"Successful equity interrogations: {successful_equity}/{len(equity_results)}")
