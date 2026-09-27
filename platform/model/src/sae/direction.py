"""Whether a HIGHER value means a WORSE outcome, per indicator.

The single source of truth for indicator direction — consumed by
`run.py` (writes `indicator_meta.parquet`) and, through that file, by
anything downstream that colours, ranks, or narrates a value (the
estimates explorer, the brief generator). Every indicator this model
fits must be classified in exactly one of these two sets;
`classify()` raises loudly on anything left out or double-booked
rather than letting a caller guess and mis-colour or mis-narrate it.
"""

from __future__ import annotations

WORSE_WHEN_HIGH = {
    "child_stunting", "child_underweight", "child_wasting", "child_anaemia_any",
    "women_anaemia_any", "women_thin_bmi", "zero_dose", "unmet_need_fp",
    "open_defecation", "malaria_rdt_prev",
    "infant_mortality", "neonatal_mortality", "under5_mortality",
}
BETTER_WHEN_HIGH = {
    "diarrhoea_ors_rhf", "fully_vaccinated", "measles1", "pentavalent3",
    "excl_breastfeeding", "women_literate", "mcpr_all_women",
    "household_electricity", "fever_care_sought", "iptp3", "itn_access",
    "anc4", "improved_water", "improved_sanitation",
}


def classify(slugs: set[str]) -> dict[str, bool]:
    """slug -> worse_high, for every slug in `slugs`. Raises if any slug
    isn't classified in exactly one of the two sets above."""
    unclassified = slugs - WORSE_WHEN_HIGH - BETTER_WHEN_HIGH
    both = slugs & WORSE_WHEN_HIGH & BETTER_WHEN_HIGH
    if unclassified or both:
        raise ValueError(f"fix WORSE_WHEN_HIGH/BETTER_WHEN_HIGH in direction.py: "
                         f"unclassified={unclassified} in_both={both}")
    return {s: (s in WORSE_WHEN_HIGH) for s in slugs}
