"""
Alaafia Validation Framework — Version 2
Evaluates causal pathway quality by reasoning criteria, NOT by matching
against pre-specified correct answers.

Philosophy:
- Ground truth in causal epidemiology is contested and evolving
- Pre-specifying answers would make agents pattern-match rather than discover
- Instead we evaluate the QUALITY OF REASONING that produced the pathway
- Literature comparison happens at the paper-writing stage as a RESULT not a constraint

Four evaluation dimensions:
1. Biological plausibility — does the mechanism make scientific sense
2. Directionality defensibility — is the causal direction sound
3. Confounder awareness — did the agent acknowledge confounding
4. Nigerian context specificity — is reasoning Nigeria-specific or generic

Author: Anthonio Oladimeji
"""

import subprocess
import json
import re


EVALUATION_CRITERIA = {

    "biological_plausibility": {
        "description": "Does the proposed causal mechanism have a known biological or social pathway?",
        "questions": [
            "Is there a plausible biological mechanism linking exposure to outcome?",
            "Is the mechanism specific enough to be testable?",
            "Does the pathway acknowledge intermediate biological steps?"
        ],
        "red_flags": [
            "vague language like 'leads to' without specifying mechanism",
            "skipping intermediate steps that are biologically necessary",
            "claiming direct exposure-to-outcome with no mediation"
        ]
    },

    "directionality": {
        "description": "Is the proposed causal direction defensible against reverse causation?",
        "questions": [
            "Could the outcome cause the exposure rather than the reverse?",
            "Is the temporal ordering of cause and effect clear?",
            "Has the agent considered bidirectional relationships?"
        ],
        "red_flags": [
            "anaemia causing poor sanitation rather than reverse",
            "stunting causing food insecurity rather than reverse",
            "no acknowledgment of possible reverse causation"
        ]
    },

    "confounder_awareness": {
        "description": "Did the agent acknowledge variables that could confound the proposed relationship?",
        "questions": [
            "Were wealth and education considered as confounders?",
            "Was zone/geography considered as a structural confounder?",
            "Was the role of unmeasured variables acknowledged?"
        ],
        "red_flags": [
            "no mention of confounding at all",
            "treating correlation as causation without confounder discussion",
            "ignoring wealth quintile as a universal confounder"
        ]
    },

    "nigeria_specificity": {
        "description": "Is the reasoning grounded in Nigerian context or imported from other settings?",
        "questions": [
            "Does the pathway account for Nigerian zone-specific differences?",
            "Is evidence from Nigeria cited or implied rather than Western settings?",
            "Does the reasoning account for Nigerian health system realities?"
        ],
        "red_flags": [
            "reasoning that would apply equally to any Sub-Saharan country",
            "no mention of zone, state, or Nigerian-specific structural factors",
            "applying Western causal assumptions to Nigerian context"
        ]
    }
}


KNOWN_CONFOUNDERS_NIGERIA = [
    "wealth_quintile",
    "geopolitical_zone",
    "urban_rural_residence",
    "female_education",
    "husband_education",
    "parity",
    "age",
    "season_of_data_collection",
    "cluster_malaria_prevalence",
    "travel_time_to_health_facility"
]


DIRECTIONALITY_RISKS = {
    "anaemia -> poor_sanitation": "reverse causation risk — anaemia does not cause sanitation",
    "stunting -> food_insecurity": "reverse causation risk — stunting does not cause food insecurity",
    "poverty -> anaemia": "confounding risk — poverty mediates through multiple pathways",
    "education -> health": "too distal — education affects health through multiple proximal pathways"
}


def evaluate_pathway_quality(
    proposed_pathway: str,
    key_mediators: list,
    reasoning: str,
    outcome: str,
    zone: str = None
) -> dict:
    """
    Evaluate a proposed causal pathway against the four quality criteria.
    Returns a structured quality report with scores and flags.
    Does NOT check against pre-specified correct answers.
    """

    scores = {}
    flags = []
    questions_passed = {}

    # 1. Biological plausibility
    plausibility_score = 0
    pathway_lower = proposed_pathway.lower()
    reasoning_lower = reasoning.lower() if reasoning else ""

    mechanism_words = ["through", "via", "by", "causing", "leads to",
                      "resulting in", "pathway", "mechanism", "mediated"]
    if any(w in pathway_lower for w in mechanism_words):
        plausibility_score += 1
    if len(key_mediators) >= 1:
        plausibility_score += 1
    if len(proposed_pathway.split("→")) >= 3 or len(proposed_pathway.split("->")) >= 3:
        plausibility_score += 1

    scores["biological_plausibility"] = min(plausibility_score / 3, 1.0)

    if plausibility_score < 2:
        flags.append("LOW PLAUSIBILITY: pathway lacks intermediate mechanistic steps")

    # 2. Directionality
    directionality_score = 1.0
    for risk_pair, risk_description in DIRECTIONALITY_RISKS.items():
        nodes = risk_pair.split(" -> ")
        if len(nodes) == 2:
            if nodes[0].replace("_"," ") in pathway_lower and nodes[1].replace("_"," ") in pathway_lower:
                directionality_score -= 0.3
                flags.append(f"DIRECTIONALITY RISK: {risk_description}")

    scores["directionality"] = max(directionality_score, 0)

    # 3. Confounder awareness
    confounder_score = 0
    all_text = pathway_lower + " " + reasoning_lower
    confounders_mentioned = [c for c in KNOWN_CONFOUNDERS_NIGERIA
                            if c.replace("_"," ") in all_text or c in all_text]
    confounder_score = min(len(confounders_mentioned) / 3, 1.0)

    scores["confounder_awareness"] = confounder_score

    if confounder_score < 0.3:
        flags.append(f"CONFOUNDER GAP: only {len(confounders_mentioned)} known confounders mentioned")

    # 4. Nigerian context specificity
    nigeria_score = 0
    nigeria_terms = ["nigeria", "nigerian", "zone", "north", "south",
                    "hausa", "igbo", "yoruba", "ndhs", "mics",
                    "geopolitical", "lga", "state", "abuja"]

    nigeria_mentions = sum(1 for t in nigeria_terms if t in all_text)
    nigeria_score = min(nigeria_mentions / 3, 1.0)

    scores["nigeria_specificity"] = nigeria_score

    if nigeria_score < 0.3:
        flags.append("CONTEXT GAP: reasoning is generic, not Nigeria-specific")

    # Overall quality score
    overall = sum(scores.values()) / len(scores)

    return {
        "outcome": outcome,
        "zone": zone,
        "proposed_pathway": proposed_pathway,
        "quality_scores": scores,
        "overall_quality": round(overall, 3),
        "quality_grade": "A" if overall > 0.75 else "B" if overall > 0.5 else "C" if overall > 0.25 else "D",
        "flags": flags,
        "confounders_mentioned": confounders_mentioned,
        "note": "This evaluates reasoning quality NOT correctness. Literature comparison is a separate research task."
    }


def print_quality_report(report: dict):
    print(f"\n{'='*60}")
    print(f"PATHWAY QUALITY REPORT")
    print(f"Outcome: {report['outcome']}")
    print(f"Zone: {report.get('zone', 'not specified')}")
    print(f"\nProposed: {report['proposed_pathway']}")
    print(f"\nQuality Scores:")
    for dimension, score in report['quality_scores'].items():
        bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
        print(f"  {dimension:<30} {bar} {score:.2f}")
    print(f"\nOverall Quality: {report['overall_quality']} (Grade {report['quality_grade']})")
    if report['flags']:
        print(f"\nFlags:")
        for flag in report['flags']:
            print(f"  ⚠ {flag}")
    print(f"\nConfounders mentioned: {report['confounders_mentioned']}")
    print(f"\nNote: {report['note']}")


if __name__ == "__main__":
    print("=== Alaafia Validation Framework v2 ===")
    print("Evaluating reasoning quality, not matching against pre-specified answers\n")

    test1 = evaluate_pathway_quality(
        proposed_pathway="poor sanitation → environmental enteropathy → nutrient malabsorption → stunting",
        key_mediators=["environmental enteropathy", "nutrient malabsorption"],
        reasoning="In North East Nigeria, open defecation and pit latrine without slab drive environmental enteropathy, a chronic subclinical gut inflammation that impairs nutrient absorption. This pathway is distinct from acute wasting and is the primary driver of the 52% stunting prevalence in this zone, not solid fuel which is uniformly distributed.",
        outcome="stunting",
        zone="north_east"
    )
    print_quality_report(test1)

    test2 = evaluate_pathway_quality(
        proposed_pathway="poverty leads to anaemia",
        key_mediators=[],
        reasoning="Poor people have anaemia because they cannot afford food.",
        outcome="maternal anaemia",
        zone="south_east"
    )
    print_quality_report(test2)
