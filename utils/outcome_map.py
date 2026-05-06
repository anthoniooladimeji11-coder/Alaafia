"""
Alaafia Complete Outcome Map
All measurable health outcomes across NDHS 2024 files
Mapped from direct reading of variable labels across IR, KR, HR, GR, CR files

Author: Anthonio Oladimeji
"""

OUTCOME_MAP = {

    # ─── MATERNAL NUTRITION & BLOOD ─────────────────────────────
    "maternal_anaemia": {
        "label": "Maternal Anaemia",
        "description": "Haemoglobin-based anaemia status in women 15-49",
        "file": "IR",
        "variable": "v457",
        "variable_hb": "v453",
        "category": "Maternal Nutrition",
        "coverage_pct": 36.0,
        "population": "women",
        "measurement": "categorical",
        "values": {1: "severe", 2: "moderate", 3: "mild", 4: "none"},
        "binary": {"anaemic": "v457 < 4"},
    },

    # ─── CHILD NUTRITION & GROWTH ────────────────────────────────
    "child_stunting": {
        "label": "Child Stunting",
        "description": "Height-for-age z-score < -2 SD in children under 5",
        "file": "KR",
        "variable": "hw70",
        "category": "Child Nutrition",
        "coverage_pct": 33.8,
        "population": "children",
        "measurement": "continuous_to_binary",
        "binary": {"stunted": "hw70/100 < -2.0"},
    },

    "child_severe_stunting": {
        "label": "Severe Child Stunting",
        "description": "Height-for-age z-score < -3 SD in children under 5",
        "file": "KR",
        "variable": "hw70",
        "category": "Child Nutrition",
        "coverage_pct": 33.8,
        "population": "children",
        "measurement": "continuous_to_binary",
        "binary": {"severely_stunted": "hw70/100 < -3.0"},
    },

    "child_wasting": {
        "label": "Child Wasting",
        "description": "Weight-for-height z-score < -2 SD — acute malnutrition",
        "file": "KR",
        "variable": "hw71",
        "category": "Child Nutrition",
        "coverage_pct": 33.9,
        "population": "children",
        "measurement": "continuous_to_binary",
        "binary": {"wasted": "hw71/100 < -2.0"},
    },

    "child_underweight": {
        "label": "Child Underweight",
        "description": "Weight-for-age z-score < -2 SD in children under 5",
        "file": "KR",
        "variable": "hw72",
        "category": "Child Nutrition",
        "coverage_pct": 33.8,
        "population": "children",
        "measurement": "continuous_to_binary",
        "binary": {"underweight": "hw72/100 < -2.0"},
    },

    "child_anaemia": {
        "label": "Child Anaemia",
        "description": "Haemoglobin-based anaemia in children under 5",
        "file": "KR",
        "variable": "hw53",
        "category": "Child Nutrition",
        "coverage_pct": 31.5,
        "population": "children",
        "measurement": "continuous_to_binary",
        "binary": {"anaemic": "hw53/10 < 11.0"},
    },

    # ─── MATERNAL & REPRODUCTIVE HEALTH ─────────────────────────
    "antenatal_care": {
        "label": "Antenatal Care Attendance",
        "description": "Number of ANC visits for last birth",
        "file": "IR",
        "variable": "m14_1",
        "category": "Maternal Health",
        "coverage_pct": 45.0,
        "population": "women",
        "measurement": "continuous_to_binary",
        "binary": {"adequate_anc": "m14_1 >= 4"},
    },

    "skilled_birth_attendance": {
        "label": "Skilled Birth Attendance",
        "description": "Delivery attended by skilled health personnel",
        "file": "IR",
        "variable": "m3a_1",
        "category": "Maternal Health",
        "coverage_pct": 45.0,
        "population": "women",
        "measurement": "binary",
    },

    "facility_delivery": {
        "label": "Facility Delivery",
        "description": "Delivery in a health facility",
        "file": "IR",
        "variable": "m15_1",
        "category": "Maternal Health",
        "coverage_pct": 45.0,
        "population": "women",
        "measurement": "binary",
    },

    "caesarean_section": {
        "label": "Caesarean Section Rate",
        "description": "Delivery by caesarean section",
        "file": "IR",
        "variable": "m17_1",
        "category": "Maternal Health",
        "coverage_pct": 45.0,
        "population": "women",
        "measurement": "binary",
    },

    "postnatal_care_mother": {
        "label": "Postnatal Care (Mother)",
        "description": "Mother received postnatal check after delivery",
        "file": "IR",
        "variable": "m62_1",
        "category": "Maternal Health",
        "coverage_pct": 45.0,
        "population": "women",
        "measurement": "binary",
    },

    "iron_supplementation": {
        "label": "Iron Supplementation in Pregnancy",
        "description": "Given or bought iron tablets/syrup during pregnancy",
        "file": "IR",
        "variable": "m45_1",
        "category": "Maternal Nutrition",
        "coverage_pct": 35.8,
        "population": "women",
        "measurement": "binary",
    },

    "low_birthweight": {
        "label": "Low Birthweight",
        "description": "Birth weight less than 2.5 kg",
        "file": "IR",
        "variable": "m19_1",
        "category": "Maternal Health",
        "coverage_pct": 35.2,
        "population": "women",
        "measurement": "continuous_to_binary",
        "binary": {"low_birthweight": "m19_1/1000 < 2.5"},
    },

    # ─── PREGNANCY OUTCOMES ──────────────────────────────────────
    "pregnancy_loss": {
        "label": "Pregnancy Loss",
        "description": "Stillbirth or miscarriage in pregnancy history",
        "file": "GR",
        "variable": "p32",
        "category": "Reproductive Health",
        "coverage_pct": 100.0,
        "population": "pregnancies",
        "measurement": "binary",
        "binary": {"loss": "p32 in [2,3]"},
    },

    "stillbirth": {
        "label": "Stillbirth",
        "description": "Pregnancy ending in stillbirth",
        "file": "GR",
        "variable": "p32",
        "category": "Reproductive Health",
        "coverage_pct": 100.0,
        "population": "pregnancies",
        "measurement": "binary",
        "binary": {"stillbirth": "p32 == 2"},
    },

    # ─── FAMILY PLANNING ─────────────────────────────────────────
    "contraceptive_use": {
        "label": "Contraceptive Use",
        "description": "Currently using any contraceptive method",
        "file": "IR",
        "variable": "v313",
        "category": "Family Planning",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
        "binary": {"using": "v313 > 0"},
    },

    "modern_contraception": {
        "label": "Modern Contraceptive Use",
        "description": "Currently using a modern contraceptive method",
        "file": "IR",
        "variable": "v313",
        "category": "Family Planning",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
        "binary": {"using_modern": "v313 == 3"},
    },

    "unmet_need": {
        "label": "Unmet Need for Family Planning",
        "description": "Women who want to stop or delay childbearing but not using contraception",
        "file": "IR",
        "variable": "v626a",
        "category": "Family Planning",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
    },

    # ─── HIV & STIs ──────────────────────────────────────────────
    "hiv_testing": {
        "label": "HIV Testing",
        "description": "Ever tested for HIV",
        "file": "IR",
        "variable": "v781",
        "category": "HIV & Infectious Disease",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
    },

    "hiv_test_antenatal": {
        "label": "HIV Testing During ANC",
        "description": "Tested for HIV during antenatal care",
        "file": "IR",
        "variable": "v828",
        "category": "HIV & Infectious Disease",
        "coverage_pct": 45.0,
        "population": "women",
        "measurement": "binary",
    },

    "sti_symptoms": {
        "label": "STI Symptoms",
        "description": "Had STI or STI symptoms in last 12 months",
        "file": "IR",
        "variable": "v763a",
        "category": "HIV & Infectious Disease",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
    },

    # ─── CHILD VACCINATION ───────────────────────────────────────
    "bcg_vaccination": {
        "label": "BCG Vaccination",
        "description": "Child received BCG vaccine",
        "file": "IR",
        "variable": "h2_1",
        "category": "Child Health",
        "coverage_pct": 34.4,
        "population": "children",
        "measurement": "binary",
    },

    "dpt3_vaccination": {
        "label": "DPT3 Vaccination",
        "description": "Child received 3 doses of DPT vaccine",
        "file": "IR",
        "variable": "h7_1",
        "category": "Child Health",
        "coverage_pct": 34.4,
        "population": "children",
        "measurement": "binary",
    },

    "measles_vaccination": {
        "label": "Measles Vaccination",
        "description": "Child received measles vaccine",
        "file": "IR",
        "variable": "h9_1",
        "category": "Child Health",
        "coverage_pct": 34.4,
        "population": "children",
        "measurement": "binary",
    },

    "full_vaccination": {
        "label": "Full Vaccination Coverage",
        "description": "Child received all basic vaccines",
        "file": "IR",
        "variable": "h11_1",
        "category": "Child Health",
        "coverage_pct": 34.4,
        "population": "children",
        "measurement": "binary",
    },

    # ─── CHILD ILLNESS & TREATMENT ───────────────────────────────
    "child_fever": {
        "label": "Child Fever (Last 2 Weeks)",
        "description": "Child had fever in last 2 weeks",
        "file": "IR",
        "variable": "h22_1",
        "category": "Child Health",
        "coverage_pct": 34.4,
        "population": "children",
        "measurement": "binary",
    },

    "child_diarrhoea": {
        "label": "Child Diarrhoea (Last 2 Weeks)",
        "description": "Child had diarrhoea in last 2 weeks",
        "file": "IR",
        "variable": "h11_1",
        "category": "Child Health",
        "coverage_pct": 34.4,
        "population": "children",
        "measurement": "binary",
    },

    "child_malaria_diagnosis": {
        "label": "Child Malaria Diagnosis",
        "description": "Child told by provider they had malaria",
        "file": "IR",
        "variable": "h71_1",
        "category": "Child Health",
        "coverage_pct": 7.9,
        "population": "children",
        "measurement": "binary",
    },

    "malaria_treatment": {
        "label": "Malaria Treatment (Child)",
        "description": "Child with fever received antimalarial treatment",
        "file": "IR",
        "variable": "h37a_1",
        "category": "Child Health",
        "coverage_pct": 9.5,
        "population": "children",
        "measurement": "binary",
    },

    # ─── BREASTFEEDING & INFANT FEEDING ──────────────────────────
    "early_breastfeeding": {
        "label": "Early Breastfeeding Initiation",
        "description": "Child put to breast within 1 hour of birth",
        "file": "IR",
        "variable": "m34_1",
        "category": "Infant Nutrition",
        "coverage_pct": 33.7,
        "population": "women",
        "measurement": "binary",
    },

    "exclusive_breastfeeding": {
        "label": "Exclusive Breastfeeding",
        "description": "Child under 6 months exclusively breastfed",
        "file": "IR",
        "variable": "v404",
        "category": "Infant Nutrition",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
    },

    # ─── NON-COMMUNICABLE DISEASES ───────────────────────────────
    "hypertension": {
        "label": "Hypertension",
        "description": "Ever told by provider they have high blood pressure",
        "file": "IR",
        "variable": "chb02",
        "category": "Non-Communicable Disease",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
    },

    "hypertension_on_medication": {
        "label": "Hypertension on Medication",
        "description": "Taking medication to control blood pressure",
        "file": "IR",
        "variable": "chb04",
        "category": "Non-Communicable Disease",
        "coverage_pct": 6.8,
        "population": "women",
        "measurement": "binary",
    },

    "diabetes": {
        "label": "Diabetes",
        "description": "Ever told by provider they have high blood sugar or diabetes",
        "file": "IR",
        "variable": "chd07",
        "category": "Non-Communicable Disease",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
    },

    # ─── OBSTETRIC FISTULA ───────────────────────────────────────
    "obstetric_fistula": {
        "label": "Obstetric Fistula",
        "description": "Currently experiencing constant leakage of urine or stool from vagina",
        "file": "IR",
        "variable": "fi1",
        "category": "Maternal Health",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
    },

    # ─── TUBERCULOSIS ────────────────────────────────────────────
    "tb_awareness": {
        "label": "TB Awareness",
        "description": "Has heard of tuberculosis",
        "file": "IR",
        "variable": "s1109a",
        "category": "Infectious Disease",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
    },

    # ─── HEPATITIS ───────────────────────────────────────────────
    "hepatitis_b_testing": {
        "label": "Hepatitis B Testing",
        "description": "Ever tested for hepatitis B",
        "file": "IR",
        "variable": "s1112b",
        "category": "Infectious Disease",
        "coverage_pct": 52.6,
        "population": "women",
        "measurement": "binary",
    },

    "hepatitis_b_vaccination": {
        "label": "Hepatitis B Vaccination",
        "description": "Vaccinated against hepatitis B",
        "file": "IR",
        "variable": "s1112e",
        "category": "Infectious Disease",
        "coverage_pct": 52.6,
        "population": "women",
        "measurement": "binary",
    },

    # ─── HEALTH SEEKING BEHAVIOUR ────────────────────────────────
    "health_insurance": {
        "label": "Health Insurance Coverage",
        "description": "Covered by health insurance",
        "file": "IR",
        "variable": "v481",
        "category": "Health Access",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
    },

    "self_reported_health": {
        "label": "Self-Reported Health Status",
        "description": "Woman's self-assessment of her health",
        "file": "IR",
        "variable": "v176",
        "category": "General Health",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "categorical",
        "values": {1: "very good", 2: "good", 3: "average", 4: "bad", 5: "very bad"},
    },

    "problems_accessing_care": {
        "label": "Problems Accessing Healthcare",
        "description": "Big problem getting permission to go to the doctor",
        "file": "IR",
        "variable": "v467a",
        "category": "Health Access",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
    },

    "mosquito_net_use": {
        "label": "Mosquito Net Use",
        "description": "Slept under mosquito bed net last night",
        "file": "IR",
        "variable": "ml101",
        "category": "Malaria Prevention",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
    },

    # ─── DOMESTIC VIOLENCE ───────────────────────────────────────
    "physical_violence": {
        "label": "Physical Violence",
        "description": "Ever experienced physical violence",
        "file": "IR",
        "variable": "v044",
        "category": "Gender-Based Violence",
        "coverage_pct": 44.0,
        "population": "women",
        "measurement": "binary",
        "note": "Only asked of selected subsample",
    },

    # ─── WOMEN'S EMPOWERMENT ─────────────────────────────────────
    "decision_making_autonomy": {
        "label": "Healthcare Decision Autonomy",
        "description": "Woman has final say in decisions about her own healthcare",
        "file": "IR",
        "variable": "v743a",
        "category": "Women's Empowerment",
        "coverage_pct": 65.7,
        "population": "women",
        "measurement": "binary",
    },

    "financial_autonomy": {
        "label": "Financial Autonomy",
        "description": "Has an account in a bank or other financial institution",
        "file": "IR",
        "variable": "v170",
        "category": "Women's Empowerment",
        "coverage_pct": 100.0,
        "population": "women",
        "measurement": "binary",
    },

    # ─── CHILD NUTRITION SUPPLEMENTATION ─────────────────────────
    "child_iron_supplementation": {
        "label": "Child Iron Supplementation",
        "description": "Child given iron pills, sprinkles or syrup in last 12 months",
        "file": "IR",
        "variable": "h42_1",
        "category": "Child Nutrition",
        "coverage_pct": 45.6,
        "population": "children",
        "measurement": "binary",
    },

    "child_deworming": {
        "label": "Child Deworming",
        "description": "Child given drugs for intestinal parasites in last 6 months",
        "file": "IR",
        "variable": "h43_1",
        "category": "Child Health",
        "coverage_pct": 45.6,
        "population": "children",
        "measurement": "binary",
    },

    "child_micronutrient_powder": {
        "label": "Child Micronutrient Powder",
        "description": "Child given multiple micronutrient powder in last 12 months",
        "file": "IR",
        "variable": "h80a_1",
        "category": "Child Nutrition",
        "coverage_pct": 45.6,
        "population": "children",
        "measurement": "binary",
    },
}

# ─── CATEGORIES for product UI ───────────────────────────────
OUTCOME_CATEGORIES = {
    "Maternal Nutrition":        ["maternal_anaemia", "iron_supplementation", "low_birthweight"],
    "Child Nutrition":           ["child_stunting", "child_severe_stunting", "child_wasting", "child_underweight", "child_anaemia", "child_iron_supplementation", "child_deworming", "child_micronutrient_powder"],
    "Maternal Health":           ["antenatal_care", "skilled_birth_attendance", "facility_delivery", "caesarean_section", "postnatal_care_mother", "obstetric_fistula"],
    "Reproductive Health":       ["pregnancy_loss", "stillbirth", "contraceptive_use", "modern_contraception", "unmet_need"],
    "Child Health":              ["child_fever", "child_diarrhoea", "child_malaria_diagnosis", "malaria_treatment", "bcg_vaccination", "dpt3_vaccination", "measles_vaccination", "full_vaccination"],
    "Infant Nutrition":          ["early_breastfeeding", "exclusive_breastfeeding"],
    "HIV & Infectious Disease":  ["hiv_testing", "hiv_test_antenatal", "sti_symptoms", "hepatitis_b_testing", "hepatitis_b_vaccination", "tb_awareness"],
    "Non-Communicable Disease":  ["hypertension", "hypertension_on_medication", "diabetes"],
    "Health Access":             ["health_insurance", "problems_accessing_care", "self_reported_health"],
    "Malaria Prevention":        ["mosquito_net_use"],
    "Gender-Based Violence":     ["physical_violence"],
    "Women's Empowerment":       ["decision_making_autonomy", "financial_autonomy"],
}

if __name__ == "__main__":
    print(f"Total outcomes mapped: {len(OUTCOME_MAP)}")
    print(f"Categories: {len(OUTCOME_CATEGORIES)}")
    print()
    for cat, outcomes in OUTCOME_CATEGORIES.items():
        print(f"{cat} ({len(outcomes)}):")
        for o in outcomes:
            label = OUTCOME_MAP[o]['label']
            coverage = OUTCOME_MAP[o]['coverage_pct']
            print(f"  - {label} ({coverage}% coverage)")
        print()
