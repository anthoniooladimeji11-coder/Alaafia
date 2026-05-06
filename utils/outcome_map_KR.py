"""
Alaafia Outcome Map — KR File Additions
New outcomes found exclusively or more precisely in KR (Children's Recode)
These supplement the IR-based outcome map.

Author: Anthonio Oladimeji
"""

KR_OUTCOME_ADDITIONS = {

    # ─── CHILD ANTHROPOMETRY (more precise in KR) ────────────────
    "child_bmi": {
        "label": "Child BMI",
        "description": "BMI-for-age standard deviation — overnutrition/undernutrition",
        "file": "KR",
        "variable": "hw73",
        "category": "Child Nutrition",
        "coverage_pct": 34.3,
        "population": "children",
        "measurement": "continuous",
        "note": "Both underweight (< -2SD) and overweight (> +2SD) detectable",
    },

    "child_anaemia_altitude_adjusted": {
        "label": "Child Anaemia (Altitude-Adjusted)",
        "description": "Haemoglobin anaemia level adjusted for altitude — WHO standard",
        "file": "KR",
        "variable": "hw57a",
        "category": "Child Nutrition",
        "coverage_pct": 30.2,
        "population": "children",
        "measurement": "categorical",
        "values": {1: "severe", 2: "moderate", 3: "mild", 4: "none"},
        "note": "More accurate than unadjusted — use this over hw53 where possible",
    },

    # ─── CHILD ILLNESS ───────────────────────────────────────────
    "child_cough": {
        "label": "Child Cough (Last 2 Weeks)",
        "description": "Child had cough in last 2 weeks",
        "file": "KR",
        "variable": "h31",
        "category": "Child Health",
        "coverage_pct": 92.1,
        "population": "children",
        "measurement": "binary",
    },

    "child_ari": {
        "label": "Child Acute Respiratory Infection",
        "description": "Child had cough with short rapid breaths — ARI indicator",
        "file": "KR",
        "variable": "h31b",
        "category": "Child Health",
        "coverage_pct": 92.1,
        "population": "children",
        "measurement": "binary",
    },

    "child_diarrhoea_kr": {
        "label": "Child Diarrhoea Treatment",
        "description": "Child with diarrhoea — amount offered to drink",
        "file": "KR",
        "variable": "h38",
        "category": "Child Health",
        "coverage_pct": 12.2,
        "population": "children",
        "measurement": "categorical",
        "note": "Covers ORS and fluid management — key diarrhoea management indicator",
    },

    "child_fever_no_treatment": {
        "label": "Child Fever — No Treatment Sought",
        "description": "Child had fever but nothing taken and no treatment sought",
        "file": "KR",
        "variable": "h37y",
        "category": "Child Health",
        "coverage_pct": 17.1,
        "population": "children",
        "measurement": "binary",
    },

    "child_malaria_rdt": {
        "label": "Child Malaria RDT Testing",
        "description": "Blood taken from child's finger/heel for malaria testing",
        "file": "KR",
        "variable": "h47",
        "category": "Child Health",
        "coverage_pct": 14.3,
        "population": "children",
        "measurement": "binary",
    },

    "child_fever_treatment_sought": {
        "label": "Child Fever — Treatment Sought",
        "description": "Child with fever received any treatment",
        "file": "KR",
        "variable": "h21",
        "category": "Child Health",
        "coverage_pct": 12.2,
        "population": "children",
        "measurement": "binary",
    },

    # ─── CHILD NUTRITION SUPPLEMENTS ────────────────────────────
    "child_vitamin_a": {
        "label": "Child Vitamin A Supplementation",
        "description": "Child received vitamin A dose in last 6 months",
        "file": "KR",
        "variable": "h34",
        "category": "Child Nutrition",
        "coverage_pct": 92.1,
        "population": "children",
        "measurement": "binary",
    },

    "child_weight_monitored": {
        "label": "Child Growth Monitoring",
        "description": "Health provider measured child's weight in last 3 months",
        "file": "KR",
        "variable": "h70a",
        "category": "Child Health",
        "coverage_pct": 92.1,
        "population": "children",
        "measurement": "binary",
    },

    "child_muac_monitored": {
        "label": "Child MUAC Monitoring",
        "description": "Health provider measured child's upper arm circumference in last 3 months",
        "file": "KR",
        "variable": "h70c",
        "category": "Child Nutrition",
        "coverage_pct": 92.1,
        "population": "children",
        "measurement": "binary",
        "note": "MUAC is primary acute malnutrition screening tool in Nigeria",
    },

    # ─── MALARIA PREVENTION IN PREGNANCY ─────────────────────────
    "iptp_fansidar": {
        "label": "IPTp — Fansidar in Pregnancy",
        "description": "Took SP/Fansidar during pregnancy for malaria prevention",
        "file": "KR",
        "variable": "m49a",
        "category": "Malaria Prevention",
        "coverage_pct": 50.5,
        "population": "women",
        "measurement": "binary",
        "note": "Intermittent Preventive Treatment in Pregnancy — WHO recommended",
    },

    "iptp_doses": {
        "label": "IPTp Doses Received",
        "description": "Number of times took Fansidar during pregnancy",
        "file": "KR",
        "variable": "ml1",
        "category": "Malaria Prevention",
        "coverage_pct": 31.7,
        "population": "women",
        "measurement": "continuous",
        "note": "WHO recommends 3+ doses — critical malaria-anaemia pathway variable",
    },

    "child_itn_use": {
        "label": "Child ITN Use",
        "description": "Type of mosquito net child slept under last night",
        "file": "KR",
        "variable": "ml0",
        "category": "Malaria Prevention",
        "coverage_pct": 46.1,
        "population": "children",
        "measurement": "categorical",
        "note": "Child-specific — different from mother's ITN use in IR",
    },

    # ─── NEWBORN CARE ────────────────────────────────────────────
    "early_bathing": {
        "label": "Early Newborn Bathing",
        "description": "Time after birth child was bathed",
        "file": "KR",
        "variable": "mnb1",
        "category": "Newborn Care",
        "coverage_pct": 50.5,
        "population": "newborns",
        "measurement": "continuous",
        "note": "WHO recommends delaying bath 24+ hours — early bathing increases hypothermia risk",
    },

    "cord_care": {
        "label": "Cord Care Practices",
        "description": "Anything applied to cord from cutting until it fell off",
        "file": "KR",
        "variable": "mnb6",
        "category": "Newborn Care",
        "coverage_pct": 50.5,
        "population": "newborns",
        "measurement": "binary",
    },

    "chlorhexidine_cord": {
        "label": "Chlorhexidine Cord Application",
        "description": "Chlorhexidine applied to cord — evidence-based infection prevention",
        "file": "KR",
        "variable": "mnb10",
        "category": "Newborn Care",
        "coverage_pct": 23.9,
        "population": "newborns",
        "measurement": "binary",
    },

    "skin_to_skin": {
        "label": "Skin-to-Skin Contact (Kangaroo Care)",
        "description": "Child put on mother's chest and bare skin after birth",
        "file": "KR",
        "variable": "m77",
        "category": "Newborn Care",
        "coverage_pct": 50.5,
        "population": "newborns",
        "measurement": "binary",
    },

    # ─── POSTNATAL DEPRESSION ────────────────────────────────────
    "postnatal_anxiety": {
        "label": "Postnatal Anxiety",
        "description": "Feeling nervous and anxious in first two days after delivery",
        "file": "KR",
        "variable": "s473aa",
        "category": "Maternal Mental Health",
        "coverage_pct": 50.5,
        "population": "women",
        "measurement": "categorical",
        "values": {1: "often", 2: "sometimes", 3: "never"},
    },

    "postnatal_depression": {
        "label": "Postnatal Depression",
        "description": "Feeling depressed or hopeless in first two days after delivery",
        "file": "KR",
        "variable": "s473ab",
        "category": "Maternal Mental Health",
        "coverage_pct": 50.5,
        "population": "women",
        "measurement": "categorical",
        "values": {1: "often", 2: "sometimes", 3: "never"},
        "note": "First postnatal mental health screening data in Nigerian DHS",
    },

    "postnatal_loss_of_interest": {
        "label": "Postnatal Loss of Interest",
        "description": "Losing interest or pleasure in doing anything in first two days",
        "file": "KR",
        "variable": "s473ac",
        "category": "Maternal Mental Health",
        "coverage_pct": 50.5,
        "population": "women",
        "measurement": "categorical",
        "values": {1: "often", 2: "sometimes", 3: "never"},
    },

    "postnatal_suicidal_ideation": {
        "label": "Postnatal Suicidal Ideation",
        "description": "Thinking of committing suicide in first two days after delivery",
        "file": "KR",
        "variable": "s473ad",
        "category": "Maternal Mental Health",
        "coverage_pct": 50.5,
        "population": "women",
        "measurement": "categorical",
        "values": {1: "often", 2: "sometimes", 3: "never"},
        "note": "Critical — first national data on postnatal suicidal ideation in Nigeria",
    },

    # ─── CHILD DIETARY DIVERSITY ─────────────────────────────────
    "child_vegetable_intake": {
        "label": "Child Vegetable Intake",
        "description": "Child given dark green leafy vegetables yesterday",
        "file": "KR",
        "variable": "v414j",
        "category": "Child Nutrition",
        "coverage_pct": 61.8,
        "population": "children",
        "measurement": "binary",
    },

    "child_animal_protein": {
        "label": "Child Animal Protein Intake",
        "description": "Child given meat, fish, eggs, or organ meat yesterday",
        "file": "KR",
        "variable": "v414h",
        "category": "Child Nutrition",
        "coverage_pct": 61.8,
        "population": "children",
        "measurement": "binary",
        "note": "Key iron source — direct link to child anaemia pathway",
    },

    "child_vitamin_a_food": {
        "label": "Child Vitamin A-Rich Food Intake",
        "description": "Child given mangoes, papayas, or other vitamin A fruits yesterday",
        "file": "KR",
        "variable": "v414k",
        "category": "Child Nutrition",
        "coverage_pct": 61.8,
        "population": "children",
        "measurement": "binary",
    },

    "child_stool_disposal": {
        "label": "Child Stool Disposal",
        "description": "Safe disposal of youngest child's stools",
        "file": "KR",
        "variable": "v465",
        "category": "Child Health",
        "coverage_pct": 61.8,
        "population": "children",
        "measurement": "categorical",
        "note": "Key WASH outcome — links to environmental enteropathy and stunting",
    },

    # ─── MENSTRUAL HYGIENE (unique to KR in this form) ──────────
    "menstrual_hygiene_material": {
        "label": "Menstrual Hygiene Material Use",
        "description": "Type of material used to collect menstrual blood",
        "file": "KR",
        "variable": "v247b",
        "category": "Women's Health",
        "coverage_pct": 72.1,
        "population": "women",
        "measurement": "binary",
        "note": "v247a=reusable pad, v247b=disposable pad, v247e=cloth, v247y=nothing",
    },

    "menstrual_privacy": {
        "label": "Menstrual Privacy",
        "description": "Able to change menstrual material in privacy during last cycle",
        "file": "KR",
        "variable": "v248",
        "category": "Women's Health",
        "coverage_pct": 72.1,
        "population": "women",
        "measurement": "categorical",
        "values": {1: "yes_always", 2: "yes_sometimes", 3: "no"},
    },

    # ─── FGM/C ───────────────────────────────────────────────────
    "fgm_procedure_type": {
        "label": "FGM/C Procedure Type",
        "description": "Type of female genital mutilation/cutting procedure performed",
        "file": "KR",
        "variable": "sgc6aa",
        "category": "Gender-Based Violence",
        "coverage_pct": 15.0,
        "population": "women",
        "measurement": "binary",
        "note": "sgc6aa=clitoris removal, sgc6ab=infibulation, sgc6ac=scraping, sgc6ad=cutting",
    },

    # ─── COVID-19 ────────────────────────────────────────────────
    "covid_vaccination": {
        "label": "COVID-19 Vaccination",
        "description": "Received COVID-19 vaccination",
        "file": "KR",
        "variable": "s1112p",
        "category": "Infectious Disease",
        "coverage_pct": 93.1,
        "population": "women",
        "measurement": "binary",
    },

    "covid_vaccination_willingness": {
        "label": "COVID-19 Vaccination Willingness",
        "description": "Willing to be vaccinated against COVID-19",
        "file": "KR",
        "variable": "s1112s",
        "category": "Infectious Disease",
        "coverage_pct": 70.1,
        "population": "women",
        "measurement": "binary",
    },

    # ─── ANC COUNSELLING QUALITY ──────────────────────────────────
    "anc_fp_counselling": {
        "label": "Family Planning Counselling at ANC",
        "description": "Received family planning counselling during antenatal care",
        "file": "KR",
        "variable": "s418aa",
        "category": "Maternal Health",
        "coverage_pct": 36.9,
        "population": "women",
        "measurement": "binary",
        "note": "Quality of ANC indicator — not just attendance but content",
    },
}

# Updated categories with KR additions
KR_NEW_CATEGORIES = {
    "Newborn Care":          ["early_bathing", "cord_care", "chlorhexidine_cord", "skin_to_skin"],
    "Maternal Mental Health": ["postnatal_anxiety", "postnatal_depression", "postnatal_loss_of_interest", "postnatal_suicidal_ideation"],
}

if __name__ == "__main__":
    print(f"KR-specific outcome additions: {len(KR_OUTCOME_ADDITIONS)}")
    print()
    for key, val in KR_OUTCOME_ADDITIONS.items():
        print(f"  {val['label']} ({val['coverage_pct']}% coverage) — {val['file']}:{val['variable']}")
