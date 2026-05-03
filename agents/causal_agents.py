"""
Alaafia — Multi-Agent Causal Reasoning Pipeline
Layer 2: DAG Proposer (Llama 3.1) → DAG Critic (Llama 3.1) → DAG Judge (N-ATLAS)
Author: Anthonio Oladimeji
"""

import subprocess
import json
import re
import pandas as pd
import sys
sys.path.append('/Users/theoneglobal/epicause_ng')
from utils.tokeniser import tokenise_record
from utils.validation_framework import evaluate_pathway_quality, print_quality_report

NIGERIA_PRIORS = """
NDHS 2024 ZONE PATTERNS:
- Stunting: NC 52.1%, NE 52.1%, NW 35.5%, SE 19.3%
- Maternal anaemia: SE 55.4%, SS 46.9%, NW 36.0%
- Solid fuel uniform across zones — NOT stunting driver
- Poor sanitation: NE 36.6%, NC 24.8%, NW 3.4%
- Unimproved water: NE 34.6%, SW 5.4%
- High malaria drives haemolysis and anaemia
- High parity causes maternal nutritional depletion and anaemia
- Husband education independently predicts wife anaemia
- Far health facility reduces ANC attendance
REQUIRED confounders: wealth_quintile, geopolitical_zone, female_education, parity, age, malaria_burden, travel_time_to_facility
"""

def clean_ollama_output(text: str) -> str:
    result = []
    i = 0
    while i < len(text):
        if text[i] == '\x1b' and i+1 < len(text) and text[i+1] == '[':
            j = i + 2
            while j < len(text) and text[j] not in 'mGKHFABCDJsuACBD':
                j += 1
            seq = text[i:j+1]
            back_match = re.match(r'\x1b\[(\d*)D', seq)
            if back_match:
                n = int(back_match.group(1)) if back_match.group(1) else 1
                result = result[:-n]
            i = j + 1
        else:
            result.append(text[i])
            i += 1
    return ''.join(result)

def extract_json(text: str) -> dict:
    text = clean_ollama_output(text)
    text = re.sub(r'```json', '', text)
    text = re.sub(r'```', '', text)
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        return {"error": "no_json_found", "raw": text[:200]}
    raw = match.group()
    cleaned = []
    in_string = False
    prev = None
    for ch in raw:
        if ch == '"' and prev != '\\':
            in_string = not in_string
        if in_string and ch in '\n\r':
            cleaned.append(' ')
        else:
            cleaned.append(ch)
        prev = ch
    raw = ''.join(cleaned)
    raw = re.sub(r':\s*([a-z_][a-z_0-9]*)\s*([,\}\]])', r': "\1"\2', raw)
    try:
        return json.loads(raw)
    except Exception as e:
        return {"error": f"{e}", "raw": raw[:300]}

def ask_ollama(prompt: str, model: str = "llama3.1:8b") -> str:
    result = subprocess.run(
        ["ollama", "run", model, prompt],
        capture_output=True, text=True, timeout=240
    )
    return result.stdout.strip()

def dag_proposer(token: str, outcome: str) -> dict:
    prompt = f"""You are a Nigerian epidemiologist identifying causal pathways.

Woman's health profile:
{token}

Outcome: {outcome}

Nigerian context:
{NIGERIA_PRIORS}

Identify the specific causal pathway from her exposures to {outcome}.
Use specific variable names from her profile as node names — not generic names.
You MUST list at least 3 confounders from: wealth_quintile, geopolitical_zone, female_education, parity, age, malaria_burden, travel_time_to_facility

Return ONLY this JSON:
{{
  "nodes": ["specific_exposure", "specific_mediator", "{outcome}"],
  "edges": [
    {{"from": "specific_exposure", "to": "specific_mediator", "mechanism": "specific biological or social mechanism", "confidence": 0.8}},
    {{"from": "specific_mediator", "to": "{outcome}", "mechanism": "specific biological mechanism", "confidence": 0.8}}
  ],
  "primary_pathway": "specific_exposure causes {outcome} via specific_mediator in this Nigerian zone",
  "key_mediators": ["specific_mediator"],
  "confounders_to_control": ["wealth_quintile", "geopolitical_zone", "female_education"],
  "reasoning": "two sentences explaining why this pathway fits this specific Nigerian token"
}}"""
    response = ask_ollama(prompt, "llama3.1:8b")
    result = extract_json(response)
    result["agent"] = "DAG Proposer — Llama 3.1 8B"
    return result

def dag_critic(token: str, proposed: dict, outcome: str) -> dict:
    prompt = f"""You are a rigorous methodologist challenging a causal DAG for Nigerian health data.

Woman's profile: {token}
Outcome: {outcome}
Proposed DAG: {json.dumps(proposed)}

Challenge this DAG — check reverse causation, unmeasured confounding, missing mediators, Nigeria context.
List any confounders missing from the proposed DAG.

Return ONLY this JSON:
{{
  "challenged_edges": [
    {{"edge": "from->to", "challenge_type": "confounding", "challenge": "specific critique", "severity": "moderate"}}
  ],
  "missing_nodes": ["important variable missing"],
  "missing_confounders": ["confounder not mentioned"],
  "alternative_pathway": "alternative causal story",
  "verdict": "accept",
  "verdict_reasoning": "two sentences explaining verdict grounded in Nigeria"
}}"""
    response = ask_ollama(prompt, "llama3.1:8b")
    result = extract_json(response)
    result["agent"] = "DAG Critic — Llama 3.1 8B"
    return result

def dag_judge(token: str, proposed: dict, critique: dict, outcome: str) -> dict:
    prompt = f"""You are Nigeria's senior public health expert making a final causal verdict.

Woman's profile: {token}
Outcome: {outcome}
Proposed: {json.dumps(proposed)}
Critique: {json.dumps(critique)}
Nigeria context: {NIGERIA_PRIORS}

Accept strong edges. Reject weak ones. Ground the equity flag in zone-specific Nigerian realities.
State the specific intervention that would work in this Nigerian zone.

Return ONLY this JSON:
{{
  "final_pathway": "complete causal pathway as one sentence specific to this Nigerian zone",
  "accepted_edges": [
    {{"from": "node1", "to": "node2", "confidence": 0.85, "mechanism": "mechanism"}}
  ],
  "pathway_confidence": 0.8,
  "policy_implication": "specific Nigerian structural intervention for this zone",
  "equity_flag": "why this outcome is worse in this zone than others in Nigeria",
  "nigerian_context_note": "specific Nigerian social or cultural context grounding this pathway"
}}"""
    response = ask_ollama(prompt, "natlas")
    result = extract_json(response)
    result["agent"] = "DAG Judge — N-ATLAS"
    return result

def run_pipeline(token: str, outcome: str, zone: str = None) -> dict:
    print(f"\n{'='*65}")
    print(f"TOKEN: {token[:120]}...")
    print(f"OUTCOME: {outcome} | ZONE: {zone or 'unknown'}")
    print(f"{'='*65}")

    print("\n[Agent 1 — DAG Proposer — Llama 3.1 8B]")
    proposed = dag_proposer(token, outcome)
    if "primary_pathway" in proposed:
        print(f"  ✓ {proposed['primary_pathway']}")
        print(f"  ✓ Confounders: {proposed.get('confounders_to_control', [])}")
    else:
        print(f"  ✗ {proposed.get('error','')} | {proposed.get('raw','')[:80]}")

    print("\n[Agent 2 — DAG Critic — Llama 3.1 8B]")
    critique = dag_critic(token, proposed, outcome)
    if "verdict" in critique:
        print(f"  ✓ Verdict: {critique['verdict']} — {critique.get('verdict_reasoning','')[:100]}")
    else:
        print(f"  ✗ {critique.get('error','')} | {critique.get('raw','')[:80]}")

    print("\n[Agent 3 — DAG Judge — N-ATLAS]")
    final = dag_judge(token, proposed, critique, outcome)
    if "final_pathway" in final:
        print(f"  ✓ {final['final_pathway']}")
        print(f"  ✓ Policy: {final.get('policy_implication','')}")
        print(f"  ✓ Equity: {final.get('equity_flag','')}")
    else:
        print(f"  ✗ {final.get('error','')} | {final.get('raw','')[:80]}")

    print("\n[Validation Framework]")
    if "final_pathway" in final:
        quality = evaluate_pathway_quality(
            proposed_pathway=final["final_pathway"],
            key_mediators=[e.get("to","") for e in final.get("accepted_edges",[])],
            reasoning=final.get("nigerian_context_note",""),
            outcome=outcome,
            zone=zone
        )
        print_quality_report(quality)
    else:
        print("  Skipped — no final pathway")
        quality = {"error": "no final pathway"}

    return {
        "token": token, "outcome": outcome, "zone": zone,
        "proposed_dag": proposed, "critique": critique,
        "final": final, "quality": quality
    }

if __name__ == "__main__":
    print("Loading NDHS 2024 merged dataset...")
    df = pd.read_parquet(
        "/Users/theoneglobal/epicause_ng/data/processed/ndhs2024_merged.parquet"
    )
    zone_map = {1:'NC',2:'NE',3:'NW',4:'SE',5:'SS',6:'SW'}
    anaemia_sub = df[df['v457'].notna()].copy()

    records = []
    for zone_code in [2, 4, 3]:
        zone_sub = anaemia_sub[anaemia_sub['v024'].astype(int) == zone_code]
        if len(zone_sub) > 0:
            records.append((zone_map[zone_code], zone_sub.sample(1, random_state=42).iloc[0]))

    results = []
    for i, (zone, row) in enumerate(records):
        token = tokenise_record(row)
        result = run_pipeline(token, "maternal_anaemia", zone=zone)
        results.append(result)
        print(f"\nRecord {i+1} of {len(records)} complete.")

    successful = sum(1 for r in results if "final_pathway" in r.get("final", {}))
    print(f"\n{'='*65}")
    print(f"ALAAFIA PIPELINE COMPLETE")
    print(f"Records processed: {len(results)}")
    print(f"Successful final pathways: {successful}/{len(results)}")
