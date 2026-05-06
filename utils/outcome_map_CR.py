"""
Alaafia Outcome Map — CR File Additions
Outcomes unique to the Couples Recode (CR file)
6,828 matched husband-wife pairs

The CR file is the only source of MALE health data in NDHS 2024.
All mv-prefixed variables are husband/male partner data.
This enables dyadic analysis — how husband's characteristics affect wife's outcomes.

Key insight: Husband education, alcohol use, HIV status, tobacco use,
and attitudes toward IPV all predict wife's health outcomes independently
of wife's own characteristics.

Author: Anthonio Oladimeji
"""

CR_OUTCOME_ADDITIONS = {

    # ─── HUSBAND EDUCATION & WORK ─────────────────────────────────
    "husband_education_level": {
        "label": "Husband Education Level",
        "description": "Husband or partner's highest educational level",
        "file": "CR",
        "variable": "mv106",
        "category": "Dyadic Health",
        "coverage_pct": 100.0,
        "population": "couples",
        "measurement": "categorical",
        "values": {0: "no_education", 1: "primary", 2: "secondary", 3: "higher"},
        "note": "Independently predicts wife anaemia — no-education husbands: 45.5% wife anaemia vs higher edu: 36.1%",
    },

    "husband_education_years": {
        "label": "Husband Education Years",
        "description": "Husband or partner's total number of years of education",
        "file": "CR",
        "variable": "mv715",
        "category": "Dyadic Health",
        "coverage_pct": 100.0,
        "population": "couples",
        "measurement": "continuous",
    },

    "husband_currently_working": {
        "label": "Husband Employment Status",
        "description": "Husband currently working",
        "file": "CR",
        "variable": "mv714",
        "category": "Dyadic Health",
        "coverage_pct": 100.0,
        "population": "couples",
        "measurement": "binary",
    },

    "husband_occupation": {
        "label": "Husband Occupation",
        "description": "Husband's occupation grouped",
        "file": "CR",
        "variable": "mv717",
        "category": "Dyadic Health",
        "coverage_pct": 100.0,
        "population": "couples",
        "measurement": "categorical",
        "note": "Agricultural vs non-agricultural — key for food security pathways",
    },

    # ─── HUSBAND HEALTH BEHAVIOURS ────────────────────────────────
    "husband_alcohol": {
        "label": "Husband Alcohol Use",
        "description": "Husband or partner drinks alcohol",
        "file": "CR",
        "variable": "d113",
        "category": "Dyadic Health",
        "coverage_pct": 79.9,
        "population": "couples",
        "measurement": "binary",
        "note": "Strong IPV predictor — husband alcohol drives domestic violence pathway to maternal health",
    },

    "husband_alcohol_frequency": {
        "label": "Husband Alcohol Frequency",
        "description": "Frequency of husband or partner being drunk",
        "file": "CR",
        "variable": "d114",
        "category": "Dyadic Health",
        "coverage_pct": 16.9,
        "population": "couples",
        "measurement": "categorical",
        "values": {1: "almost_every_day", 2: "at_least_weekly", 3: "less_than_weekly"},
        "note": "Frequency matters — daily drinking associated with severe IPV",
    },

    "husband_tobacco_cigarettes": {
        "label": "Husband Cigarette Smoking",
        "description": "Husband smokes cigarettes",
        "file": "CR",
        "variable": "mv463a",
        "category": "Dyadic Health",
        "coverage_pct": 100.0,
        "population": "couples",
        "measurement": "binary",
        "note": "Indoor smoking exposure — links to child respiratory outcomes",
    },

    "husband_tobacco_any": {
        "label": "Husband Any Tobacco Use",
        "description": "Husband uses any tobacco product",
        "file": "CR",
        "variable": "mv463z",
        "category": "Dyadic Health",
        "coverage_pct": 100.0,
        "population": "couples",
        "measurement": "binary",
        "note": "mv463z=1 means does NOT use — invert for tobacco use indicator",
    },

    "husband_internet_use": {
        "label": "Husband Internet Use",
        "description": "Husband uses the internet",
        "file": "CR",
        "variable": "mv171a",
        "category": "Dyadic Health",
        "coverage_pct": 100.0,
        "population": "couples",
        "measurement": "categorical",
        "values": {0: "never", 1: "almost_every_day", 2: "at_least_weekly", 3: "less_than_weekly"},
        "note": "Digital access proxy — links to health information seeking",
    },

    # ─── HUSBAND HIV & SEXUAL HEALTH ─────────────────────────────
    "husband_hiv_testing": {
        "label": "Husband HIV Testing",
        "description": "Husband ever tested for HIV",
        "file": "CR",
        "variable": "mv828",
        "category": "HIV & Infectious Disease",
        "coverage_pct": 43.3,
        "population": "couples",
        "measurement": "binary",
    },

    "husband_lifetime_partners": {
        "label": "Husband Lifetime Sexual Partners",
        "description": "Total lifetime number of sexual partners — husband",
        "file": "CR",
        "variable": "mv836",
        "category": "HIV & Infectious Disease",
        "coverage_pct": 100.0,
        "population": "couples",
        "measurement": "continuous",
        "note": "HIV risk exposure indicator — important for serodiscordant couple analysis",
    },

    "husband_hiv_attitudes": {
        "label": "Husband HIV Attitudes",
        "description": "Husband would buy vegetables from vendor with HIV",
        "file": "CR",
        "variable": "mv825",
        "category": "HIV & Infectious Disease",
        "coverage_pct": 100.0,
        "population": "couples",
        "measurement": "categorical",
        "note": "HIV stigma indicator — affects wife's willingness to test and disclose",
    },

    "husband_prep_knowledge": {
        "label": "Husband PrEP Knowledge",
        "description": "Husband's knowledge and attitude to PrEP to prevent HIV",
        "file": "CR",
        "variable": "mv859",
        "category": "HIV & Infectious Disease",
        "coverage_pct": 100.0,
        "population": "couples",
        "measurement": "categorical",
    },

    "husband_self_reported_health": {
        "label": "Husband Self-Reported Health",
        "description": "Husband's self-assessment of his health",
        "file": "CR",
        "variable": "mv176",
        "category": "Dyadic Health",
        "coverage_pct": 100.0,
        "population": "couples",
        "measurement": "categorical",
        "values": {1: "very_good", 2: "good", 3: "average", 4: "bad", 5: "very_bad"},
    },

    # ─── INTIMATE PARTNER VIOLENCE ────────────────────────────────
    "ipv_emotional": {
        "label": "Emotional IPV",
        "description": "Ever experienced emotional violence from husband — humiliated, threatened, insulted",
        "file": "CR",
        "variable": "d104",
        "category": "Gender-Based Violence",
        "coverage_pct": 79.9,
        "population": "couples",
        "measurement": "binary",
        "note": "DHS domestic violence module — subsample of women selected",
    },

    "ipv_physical_less_severe": {
        "label": "Less Severe Physical IPV",
        "description": "Ever pushed, shaken, slapped, or had something thrown at her by husband",
        "file": "CR",
        "variable": "d106",
        "category": "Gender-Based Violence",
        "coverage_pct": 79.9,
        "population": "couples",
        "measurement": "binary",
    },

    "ipv_physical_severe": {
        "label": "Severe Physical IPV",
        "description": "Ever kicked, dragged, strangled, burnt or attacked with weapon by husband",
        "file": "CR",
        "variable": "d107",
        "category": "Gender-Based Violence",
        "coverage_pct": 79.9,
        "population": "couples",
        "measurement": "binary",
        "note": "Severe IPV directly linked to adverse pregnancy outcomes, anaemia, and maternal mortality",
    },

    "ipv_sexual": {
        "label": "Sexual IPV",
        "description": "Ever physically forced into unwanted sex or sexual acts by husband",
        "file": "CR",
        "variable": "d108",
        "category": "Gender-Based Violence",
        "coverage_pct": 79.9,
        "population": "couples",
        "measurement": "binary",
    },

    "ipv_injuries": {
        "label": "IPV-Related Injuries",
        "description": "Ever experienced injuries (bruises, broken bones, serious injuries) from husband's actions",
        "file": "CR",
        "variable": "d111",
        "category": "Gender-Based Violence",
        "coverage_pct": 79.9,
        "population": "couples",
        "measurement": "binary",
        "note": "Physical consequence measure — more severe than attitude or prevalence measures",
    },

    # ─── CONTROLLING BEHAVIOURS ────────────────────────────────────
    "husband_controlling_jealous": {
        "label": "Husband Controlling — Jealousy",
        "description": "Husband jealous if respondent talks with other men",
        "file": "CR",
        "variable": "d101a",
        "category": "Gender-Based Violence",
        "coverage_pct": 79.9,
        "population": "couples",
        "measurement": "categorical",
        "values": {1: "never", 2: "sometimes", 3: "often", 4: "always"},
    },

    "husband_controlling_limits_contact": {
        "label": "Husband Controlling — Limits Female Friends",
        "description": "Husband does not permit respondent to meet female friends",
        "file": "CR",
        "variable": "d101c",
        "category": "Gender-Based Violence",
        "coverage_pct": 79.9,
        "population": "couples",
        "measurement": "categorical",
        "note": "Social isolation — limits health information and support networks",
    },

    "husband_controlling_family": {
        "label": "Husband Controlling — Limits Family Contact",
        "description": "Husband tries to limit respondent's contact with family",
        "file": "CR",
        "variable": "d101d",
        "category": "Gender-Based Violence",
        "coverage_pct": 79.9,
        "population": "couples",
        "measurement": "categorical",
        "note": "Isolation from family support — key pathway to delayed health seeking",
    },

    "number_of_controlling_behaviours": {
        "label": "Number of Controlling Behaviours",
        "description": "Number of control issues answered yes by husband",
        "file": "CR",
        "variable": "d102",
        "category": "Gender-Based Violence",
        "coverage_pct": 79.9,
        "population": "couples",
        "measurement": "continuous",
        "note": "Composite score 0-5 — higher scores predict worse maternal and child health outcomes",
    },

    # ─── COUPLE DECISION MAKING ───────────────────────────────────
    "husband_anc_attendance": {
        "label": "Husband Attended ANC with Wife",
        "description": "Husband present during check-ups for most recent child",
        "file": "CR",
        "variable": "mv249",
        "category": "Dyadic Health",
        "coverage_pct": 36.6,
        "population": "couples",
        "measurement": "binary",
        "note": "Male engagement in maternal care — strong predictor of ANC quality and compliance",
    },

    "husband_attended_delivery": {
        "label": "Husband Attended Delivery",
        "description": "Husband went with child's mother to health facility for birth",
        "file": "CR",
        "variable": "mv253",
        "category": "Dyadic Health",
        "coverage_pct": 27.6,
        "population": "couples",
        "measurement": "binary",
    },

    "contraception_decision_maker": {
        "label": "Contraception Decision Maker",
        "description": "Person who usually decides on use of contraception",
        "file": "CR",
        "variable": "v632",
        "category": "Family Planning",
        "coverage_pct": 100.0,
        "population": "couples",
        "measurement": "categorical",
        "values": {1: "mainly_respondent", 2: "mainly_husband", 3: "joint_decision", 4: "other"},
        "note": "Male control over contraception is a key unmet need pathway",
    },

    "wife_can_refuse_sex": {
        "label": "Wife Can Refuse Sex",
        "description": "Respondent can refuse sex with husband or partner",
        "file": "CR",
        "variable": "v850a",
        "category": "Gender-Based Violence",
        "coverage_pct": 100.0,
        "population": "couples",
        "measurement": "categorical",
        "values": {1: "yes", 2: "no", 3: "depends"},
        "note": "Sexual autonomy indicator — links to STI risk and reproductive coercion",
    },

    "wife_can_request_condom": {
        "label": "Wife Can Request Condom Use",
        "description": "Respondent can ask partner to use a condom",
        "file": "CR",
        "variable": "v850b",
        "category": "HIV & Infectious Disease",
        "coverage_pct": 100.0,
        "population": "couples",
        "measurement": "categorical",
        "values": {1: "yes", 2: "no", 3: "depends"},
    },

    "husband_wife_justified_refuse_sex": {
        "label": "Husband Accepts Wife Refusing Sex",
        "description": "Wife justified refusing sex when husband has other women",
        "file": "CR",
        "variable": "mv633b",
        "category": "Gender-Based Violence",
        "coverage_pct": 100.0,
        "population": "couples",
        "measurement": "categorical",
        "note": "Male attitude — whether husband accepts wife's sexual autonomy",
    },

    "husband_number_of_wives": {
        "label": "Number of Wives/Partners",
        "description": "Number of wives or partners the husband has",
        "file": "CR",
        "variable": "mv505",
        "category": "Dyadic Health",
        "coverage_pct": 100.0,
        "population": "couples",
        "measurement": "continuous",
        "note": "Polygyny — links to resource dilution, wife competition for healthcare, STI risk",
    },

    "husband_age": {
        "label": "Husband Age",
        "description": "Current age of husband or partner",
        "file": "CR",
        "variable": "mv012",
        "category": "Dyadic Health",
        "coverage_pct": 100.0,
        "population": "couples",
        "measurement": "continuous",
        "note": "Age gap husband-wife: NC = 11.2 yrs, SS/SW = 6.9 yrs — key equity variable",
    },
}

CR_NEW_CATEGORIES = {
    "Dyadic Health": [
        "husband_education_level",
        "husband_education_years",
        "husband_currently_working",
        "husband_occupation",
        "husband_alcohol",
        "husband_alcohol_frequency",
        "husband_tobacco_cigarettes",
        "husband_tobacco_any",
        "husband_internet_use",
        "husband_self_reported_health",
        "husband_anc_attendance",
        "husband_attended_delivery",
        "contraception_decision_maker",
        "husband_number_of_wives",
        "husband_age",
    ],
}

if __name__ == "__main__":
    print(f"CR-specific outcome additions: {len(CR_OUTCOME_ADDITIONS)}")
    print()
    for key, val in CR_OUTCOME_ADDITIONS.items():
        print(f"  {val['label']} ({val['coverage_pct']}% coverage) — {val['file']}:{val['variable']}")
