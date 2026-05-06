"""
Alaafia Outcome Map — GR File Additions
Outcomes unique to the Pregnancy Recode (GR file)
111,914 pregnancy records — covers every pregnancy in the 5-year recall period

Key insight: GR is pregnancy-level, not woman-level.
One woman can contribute multiple pregnancies.
This allows analysis of outcomes per pregnancy, not just per woman.

Author: Anthonio Oladimeji
"""

GR_OUTCOME_ADDITIONS = {

    # ─── PREGNANCY OUTCOMES ──────────────────────────────────────
    "pregnancy_outcome_type": {
        "label": "Pregnancy Outcome Type",
        "description": "Pregnancy outcome reclassified — live birth, stillbirth, miscarriage, abortion",
        "file": "GR",
        "variable": "p32",
        "category": "Reproductive Health",
        "coverage_pct": 100.0,
        "population": "pregnancies",
        "measurement": "categorical",
        "values": {1: "live_birth", 2: "stillbirth", 3: "miscarriage", 4: "abortion"},
        "note": "Primary pregnancy outcome variable. 111,914 pregnancies in recall period.",
    },

    "pregnancy_declared_outcome": {
        "label": "Pregnancy Outcome as Declared",
        "description": "Pregnancy outcome as declared by respondent before reclassification",
        "file": "GR",
        "variable": "p30",
        "category": "Reproductive Health",
        "coverage_pct": 100.0,
        "population": "pregnancies",
        "measurement": "categorical",
        "values": {1: "live_birth", 2: "stillbirth", 3: "miscarriage", 4: "abortion"},
        "note": "Compare with p32 to assess classification accuracy",
    },

    "baby_born_alive_signs": {
        "label": "Baby Born with Signs of Life",
        "description": "Baby cried, moved or breathed at birth",
        "file": "GR",
        "variable": "p31",
        "category": "Reproductive Health",
        "coverage_pct": 1.5,
        "population": "pregnancies",
        "measurement": "binary",
        "note": "Only asked for borderline stillbirth cases — critical for stillbirth classification",
    },

    "child_survived": {
        "label": "Child Survival",
        "description": "Child from this pregnancy is alive",
        "file": "GR",
        "variable": "p5",
        "category": "Child Health",
        "coverage_pct": 93.4,
        "population": "pregnancies",
        "measurement": "binary",
    },

    "child_age_at_death": {
        "label": "Child Age at Death",
        "description": "Age at death of child from this pregnancy",
        "file": "GR",
        "variable": "p7",
        "category": "Child Health",
        "coverage_pct": 10.2,
        "population": "pregnancies",
        "measurement": "continuous",
        "note": "In months — allows neonatal vs post-neonatal vs infant vs child mortality analysis",
    },

    "pregnancy_interval": {
        "label": "Preceding Pregnancy Interval",
        "description": "Months between previous pregnancy and this one",
        "file": "GR",
        "variable": "p11",
        "category": "Reproductive Health",
        "coverage_pct": 75.6,
        "population": "pregnancies",
        "measurement": "continuous",
        "note": "Short intervals <18 months increase risk of adverse outcomes",
    },

    "pregnancy_duration": {
        "label": "Pregnancy Duration",
        "description": "Duration of pregnancy in months",
        "file": "GR",
        "variable": "p20",
        "category": "Reproductive Health",
        "coverage_pct": 100.0,
        "population": "pregnancies",
        "measurement": "continuous",
        "note": "Allows preterm birth analysis — < 8 months indicates preterm",
    },

    "multiple_pregnancy": {
        "label": "Multiple Pregnancy",
        "description": "Pregnancy is a multiple birth (twins, triplets)",
        "file": "GR",
        "variable": "p0",
        "category": "Reproductive Health",
        "coverage_pct": 100.0,
        "population": "pregnancies",
        "measurement": "binary",
        "note": "Multiple pregnancies increase maternal and child risk",
    },

    # ─── MATERNAL DIETARY DIVERSITY IN PREGNANCY ─────────────────
    "maternal_dark_greens": {
        "label": "Maternal Dark Green Leafy Vegetable Intake",
        "description": "Woman had dark green leafy vegetables yesterday",
        "file": "GR",
        "variable": "v472j",
        "category": "Maternal Nutrition",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
        "note": "Iron and folate source — direct link to maternal anaemia pathway",
    },

    "maternal_animal_protein": {
        "label": "Maternal Animal Protein Intake",
        "description": "Woman had any meat (beef, pork, lamb, chicken) yesterday",
        "file": "GR",
        "variable": "v472h",
        "category": "Maternal Nutrition",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
    },

    "maternal_fish": {
        "label": "Maternal Fish/Shellfish Intake",
        "description": "Woman had fish or shellfish yesterday",
        "file": "GR",
        "variable": "v472n",
        "category": "Maternal Nutrition",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
        "note": "Primary protein source in Southern Nigeria — important for SS and SE zones",
    },

    "maternal_eggs": {
        "label": "Maternal Egg Intake",
        "description": "Woman had eggs yesterday",
        "file": "GR",
        "variable": "v472g",
        "category": "Maternal Nutrition",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
    },

    "maternal_vitamin_a_food": {
        "label": "Maternal Vitamin A-Rich Food Intake",
        "description": "Woman had pumpkin, carrots, squash, or sweet potatoes yesterday",
        "file": "GR",
        "variable": "v472i",
        "category": "Maternal Nutrition",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
    },

    "maternal_legumes": {
        "label": "Maternal Legume Intake",
        "description": "Woman had food from beans, peas, or lentils yesterday",
        "file": "GR",
        "variable": "v472o",
        "category": "Maternal Nutrition",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
        "note": "Plant-based iron — important in zones with low animal protein access",
    },

    "maternal_organ_meat": {
        "label": "Maternal Organ Meat Intake",
        "description": "Woman had liver, heart, or other organ meat yesterday",
        "file": "GR",
        "variable": "v472m",
        "category": "Maternal Nutrition",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
        "note": "Richest dietary iron source — directly linked to haemoglobin levels",
    },

    "maternal_dairy": {
        "label": "Maternal Dairy Intake",
        "description": "Woman had cheese, yogurt, or other milk products yesterday",
        "file": "GR",
        "variable": "v472p",
        "category": "Maternal Nutrition",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
    },

    "maternal_palm_oil": {
        "label": "Maternal Red Palm Oil Intake",
        "description": "Woman had red palm oil yesterday",
        "file": "GR",
        "variable": "v472u",
        "category": "Maternal Nutrition",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
        "note": "Nigerian-specific — red palm oil is major vitamin A source in Southern zones",
    },

    "maternal_ultra_processed": {
        "label": "Maternal Ultra-Processed Food Intake",
        "description": "Woman had chips, crisps, french fries, or instant noodles yesterday",
        "file": "GR",
        "variable": "v472t",
        "category": "Maternal Nutrition",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
        "note": "Urban dietary transition indicator — links to NCD risk",
    },

    # ─── TOBACCO & ALCOHOL ────────────────────────────────────────
    "maternal_cigarette_smoking": {
        "label": "Maternal Cigarette Smoking",
        "description": "Woman smokes cigarettes",
        "file": "GR",
        "variable": "v463a",
        "category": "Maternal Health",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
    },

    "maternal_tobacco_any": {
        "label": "Maternal Any Tobacco Use",
        "description": "Woman uses any tobacco product (cigarettes, pipe, chew, snuff)",
        "file": "GR",
        "variable": "v463z",
        "category": "Maternal Health",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
        "note": "v463z=1 means does NOT use — invert for tobacco use indicator",
    },

    "maternal_alcohol": {
        "label": "Maternal Alcohol Use",
        "description": "Number of days respondent drank alcoholic drinks in the past month",
        "file": "GR",
        "variable": "v485a",
        "category": "Maternal Health",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "continuous",
        "note": "Any alcohol during pregnancy is a risk factor for fetal outcomes",
    },

    # ─── HEALTHCARE ACCESS ────────────────────────────────────────
    "travel_time_to_facility": {
        "label": "Travel Time to Nearest Health Facility",
        "description": "Minutes to nearest healthcare facility",
        "file": "GR",
        "variable": "v483a",
        "category": "Health Access",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "continuous",
        "note": "Key equity variable — confirms cluster-level travel time in geospatial data",
    },

    "transport_mode_to_facility": {
        "label": "Mode of Transport to Health Facility",
        "description": "Mode of transportation to nearest healthcare facility",
        "file": "GR",
        "variable": "v483b",
        "category": "Health Access",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "categorical",
        "note": "Walking vs motorised — modifies travel time effect on health seeking",
    },

    "permission_to_seek_care": {
        "label": "Permission Required to Seek Care",
        "description": "Getting permission to go is a big problem when seeking medical help",
        "file": "GR",
        "variable": "v467b",
        "category": "Health Access",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
        "note": "Gender autonomy barrier to care — distinct from distance or money",
    },

    "money_for_treatment": {
        "label": "Money for Treatment a Problem",
        "description": "Getting money needed for treatment is a big problem",
        "file": "GR",
        "variable": "v467c",
        "category": "Health Access",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
    },

    "distance_to_facility_problem": {
        "label": "Distance to Facility a Problem",
        "description": "Distance to health facility is a big problem when seeking care",
        "file": "GR",
        "variable": "v467d",
        "category": "Health Access",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
    },

    # ─── CANCER SCREENING ────────────────────────────────────────
    "breast_cancer_screening": {
        "label": "Breast Cancer Screening",
        "description": "Breasts examined for cancer by a health care provider",
        "file": "GR",
        "variable": "v484a",
        "category": "Non-Communicable Disease",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "categorical",
        "values": {0: "never", 1: "yes_12months", 2: "yes_2_3years", 3: "yes_3plus_years"},
        "note": "First breast cancer screening data in Nigerian DHS",
    },

    "cervical_cancer_screening": {
        "label": "Cervical Cancer Screening",
        "description": "Ever tested for cervical cancer by a health care provider",
        "file": "GR",
        "variable": "v484b",
        "category": "Non-Communicable Disease",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "categorical",
        "values": {0: "never", 1: "yes_12months", 2: "yes_2_3years", 3: "yes_3plus_years"},
        "note": "First cervical cancer screening data in Nigerian DHS",
    },

    # ─── DOMESTIC WORK BURDEN ─────────────────────────────────────
    "domestic_work_hours": {
        "label": "Daily Domestic Work Hours",
        "description": "Number of accumulated hours per day spent on unpaid domestic work",
        "file": "GR",
        "variable": "s916a",
        "category": "Women's Empowerment",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "categorical",
        "note": "Unpaid labour burden — links to maternal exhaustion and health seeking behaviour",
    },

    # ─── IPV ATTITUDES ────────────────────────────────────────────
    "ipv_justified_goes_out": {
        "label": "IPV Justified — Wife Goes Out Without Telling",
        "description": "Beating justified if wife goes out without telling husband",
        "file": "GR",
        "variable": "v744a",
        "category": "Gender-Based Violence",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
    },

    "ipv_justified_refuses_sex": {
        "label": "IPV Justified — Wife Refuses Sex",
        "description": "Beating justified if wife refuses to have sex with husband",
        "file": "GR",
        "variable": "v744d",
        "category": "Gender-Based Violence",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
        "note": "Strong predictor of actual IPV experience — more sensitive than direct IPV question",
    },

    "ipv_justified_any": {
        "label": "IPV Justified — Any Reason",
        "description": "Beating justified for any of five reasons",
        "file": "GR",
        "variable": "v744e",
        "category": "Gender-Based Violence",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
        "note": "Composite — wife burns food included. Any acceptance of IPV is the indicator.",
    },

    # ─── PROPERTY & ASSETS ────────────────────────────────────────
    "owns_house": {
        "label": "House Ownership",
        "description": "Owns a house alone or jointly",
        "file": "GR",
        "variable": "v745a",
        "category": "Women's Empowerment",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "categorical",
        "values": {1: "alone", 2: "jointly", 3: "does_not_own"},
    },

    "owns_land": {
        "label": "Land Ownership",
        "description": "Owns land alone or jointly",
        "file": "GR",
        "variable": "v745b",
        "category": "Women's Empowerment",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "categorical",
        "values": {1: "alone", 2: "jointly", 3: "does_not_own"},
    },

    "earnings_autonomy": {
        "label": "Earnings Autonomy",
        "description": "Person who usually decides how to spend respondent's earnings",
        "file": "GR",
        "variable": "v739",
        "category": "Women's Empowerment",
        "coverage_pct": 56.9,
        "population": "women",
        "measurement": "categorical",
        "values": {1: "respondent_alone", 2: "respondent_and_husband", 3: "husband_alone", 4: "someone_else"},
    },

    "husband_pressured_pregnancy": {
        "label": "Husband Pressured Pregnancy",
        "description": "Husband or family member pressured respondent to become pregnant",
        "file": "GR",
        "variable": "v636",
        "category": "Reproductive Health",
        "coverage_pct": 91.6,
        "population": "women",
        "measurement": "binary",
        "note": "Reproductive coercion indicator — links to unintended pregnancy and adverse outcomes",
    },

    "husband_knows_hiv_status": {
        "label": "Knows Husband HIV Status",
        "description": "Respondent knows her husband or partner's HIV status",
        "file": "GR",
        "variable": "s1035b",
        "category": "HIV & Infectious Disease",
        "coverage_pct": 91.6,
        "population": "women",
        "measurement": "binary",
    },

    "emergency_contraception": {
        "label": "Emergency Contraception Use",
        "description": "Used emergency contraception in past 12 months",
        "file": "GR",
        "variable": "v3a13",
        "category": "Family Planning",
        "coverage_pct": 96.9,
        "population": "women",
        "measurement": "binary",
    },

    "wanted_last_pregnancy": {
        "label": "Pregnancy Wantedness",
        "description": "Whether the last pregnancy was wanted at the time",
        "file": "GR",
        "variable": "v367a",
        "category": "Reproductive Health",
        "coverage_pct": 52.8,
        "population": "women",
        "measurement": "categorical",
        "values": {1: "wanted_then", 2: "wanted_later", 3: "not_wanted"},
        "note": "Unwanted pregnancies associate with worse maternal and child outcomes",
    },
}

GR_NEW_CATEGORIES = {
    "Maternal Dietary Diversity": [
        "maternal_dark_greens",
        "maternal_animal_protein",
        "maternal_fish",
        "maternal_eggs",
        "maternal_vitamin_a_food",
        "maternal_legumes",
        "maternal_organ_meat",
        "maternal_dairy",
        "maternal_palm_oil",
        "maternal_ultra_processed",
    ],
}

if __name__ == "__main__":
    print(f"GR-specific outcome additions: {len(GR_OUTCOME_ADDITIONS)}")
    print()
    for key, val in GR_OUTCOME_ADDITIONS.items():
        print(f"  {val['label']} ({val['coverage_pct']}% coverage) — {val['file']}:{val['variable']}")
