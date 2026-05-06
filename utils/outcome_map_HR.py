"""
Alaafia Outcome Map — HR File Additions
Outcomes unique to the Household Recode (HR file)
These are household-level exposures and outcomes not available in IR or KR.

Author: Anthonio Oladimeji
"""

HR_OUTCOME_ADDITIONS = {

    # ─── FOOD SECURITY (UNIQUE TO HR — NOT IN IR OR KR) ──────────
    "food_insecurity_worry": {
        "label": "Household Food Insecurity — Worry",
        "description": "Household worried about food for lack of money or resources",
        "file": "HR",
        "variable": "hfs1",
        "category": "Food Security",
        "coverage_pct": 100.0,
        "population": "households",
        "measurement": "categorical",
        "values": {1: "never", 2: "rarely", 3: "sometimes", 4: "often"},
        "note": "FIES — Food Insecurity Experience Scale. First time in Nigerian DHS.",
    },

    "food_insecurity_unable_healthy": {
        "label": "Household Unable to Eat Healthy Food",
        "description": "Household members unable to eat healthy food for lack of money",
        "file": "HR",
        "variable": "hfs2",
        "category": "Food Security",
        "coverage_pct": 100.0,
        "population": "households",
        "measurement": "categorical",
        "values": {1: "never", 2: "rarely", 3: "sometimes", 4: "often"},
    },

    "food_insecurity_skipped_meal": {
        "label": "Household Skipped Meals",
        "description": "Household members skipped a meal because of lack of money",
        "file": "HR",
        "variable": "hfs4",
        "category": "Food Security",
        "coverage_pct": 100.0,
        "population": "households",
        "measurement": "categorical",
        "values": {1: "never", 2: "rarely", 3: "sometimes", 4: "often"},
    },

    "food_insecurity_hungry": {
        "label": "Household Hunger",
        "description": "Household members were hungry and did not eat because of lack of money",
        "file": "HR",
        "variable": "hfs7",
        "category": "Food Security",
        "coverage_pct": 100.0,
        "population": "households",
        "measurement": "categorical",
        "values": {1: "never", 2: "rarely", 3: "sometimes", 4: "often"},
        "note": "Severe food insecurity indicator — directly links to child stunting pathway",
    },

    "food_insecurity_no_eat_day": {
        "label": "Household Did Not Eat All Day",
        "description": "Household members did not eat for a whole day because of lack of money",
        "file": "HR",
        "variable": "hfs8",
        "category": "Food Security",
        "coverage_pct": 100.0,
        "population": "households",
        "measurement": "categorical",
        "values": {1: "never", 2: "rarely", 3: "sometimes", 4: "often"},
    },

    "food_insecurity_moderate": {
        "label": "Moderate Food Insecurity Score",
        "description": "Moderate or severe food insecurity probability (FIES score)",
        "file": "HR",
        "variable": "hfs_mod",
        "category": "Food Security",
        "coverage_pct": 99.6,
        "population": "households",
        "measurement": "continuous",
        "note": "Validated FAO FIES scale — 0-1 probability score",
    },

    "food_insecurity_severe": {
        "label": "Severe Food Insecurity Score",
        "description": "Severe food insecurity probability (FIES score)",
        "file": "HR",
        "variable": "hfs_sev",
        "category": "Food Security",
        "coverage_pct": 99.6,
        "population": "households",
        "measurement": "continuous",
        "note": "Most severe end of food insecurity — direct pathway to wasting",
    },

    # ─── WATER QUALITY & TREATMENT ───────────────────────────────
    "water_insufficient": {
        "label": "Water Insufficiency",
        "description": "Water for drinking not sufficient in the last month",
        "file": "HR",
        "variable": "hv201b",
        "category": "WASH",
        "coverage_pct": 100.0,
        "population": "households",
        "measurement": "categorical",
        "note": "Beyond just source type — captures actual sufficiency",
    },

    "water_treatment": {
        "label": "Water Treatment Practice",
        "description": "Anything done to water to make safe to drink",
        "file": "HR",
        "variable": "hv237",
        "category": "WASH",
        "coverage_pct": 100.0,
        "population": "households",
        "measurement": "binary",
    },

    "water_boiled": {
        "label": "Water Boiling",
        "description": "Water usually treated by boiling",
        "file": "HR",
        "variable": "hv237a",
        "category": "WASH",
        "coverage_pct": 100.0,
        "population": "households",
        "measurement": "binary",
    },

    "water_chlorinated": {
        "label": "Water Chlorination",
        "description": "Water usually treated by adding bleach or chlorine",
        "file": "HR",
        "variable": "hv237b",
        "category": "WASH",
        "coverage_pct": 100.0,
        "population": "households",
        "measurement": "binary",
    },

    "iodised_salt": {
        "label": "Iodised Salt Use",
        "description": "Result of salt test for iodine",
        "file": "HR",
        "variable": "hv234a",
        "category": "Nutrition",
        "coverage_pct": 100.0,
        "population": "households",
        "measurement": "categorical",
        "values": {0: "no_iodine", 1: "lt_15ppm", 2: "15_to_lt_40ppm", 3: "ge_40ppm", 9: "not_tested"},
        "note": "Critical micronutrient indicator — iodine deficiency causes goitre and cognitive impairment",
    },

    # ─── HANDWASHING ─────────────────────────────────────────────
    "handwashing_place": {
        "label": "Handwashing Facility",
        "description": "Place where household members wash their hands",
        "file": "HR",
        "variable": "hv230a",
        "category": "WASH",
        "coverage_pct": 100.0,
        "population": "households",
        "measurement": "categorical",
        "values": {1: "in_dwelling", 2: "in_yard", 3: "elsewhere", 4: "no_place"},
    },

    "handwashing_water_present": {
        "label": "Water Present at Handwashing Place",
        "description": "Presence of water at hand washing place",
        "file": "HR",
        "variable": "hv230b",
        "category": "WASH",
        "coverage_pct": 75.0,
        "population": "households",
        "measurement": "binary",
    },

    "handwashing_soap_present": {
        "label": "Soap Present at Handwashing Place",
        "description": "Soap or detergent present at handwashing place",
        "file": "HR",
        "variable": "hv232",
        "category": "WASH",
        "coverage_pct": 75.0,
        "population": "households",
        "measurement": "binary",
        "note": "Basic handwashing compliance indicator — links to diarrhoea and child stunting",
    },

    # ─── INDOOR AIR QUALITY ───────────────────────────────────────
    "indoor_smoking": {
        "label": "Indoor Smoking Frequency",
        "description": "Frequency household members smoke inside the house",
        "file": "HR",
        "variable": "hv252",
        "category": "Indoor Air Quality",
        "coverage_pct": 100.0,
        "population": "households",
        "measurement": "categorical",
        "values": {1: "every_day", 2: "some_days", 3: "never", 4: "no_smoker"},
        "note": "Indoor smoking exposure — distinct from cooking fuel — links to child respiratory health",
    },

    "cooking_indoor_outdoor": {
        "label": "Indoor/Outdoor Cooking",
        "description": "Food cooked in the house, separate building, or outdoors",
        "file": "HR",
        "variable": "hv241",
        "category": "Indoor Air Quality",
        "coverage_pct": 98.0,
        "population": "households",
        "measurement": "categorical",
        "values": {1: "in_house", 2: "separate_building", 3: "outdoors", 4: "no_cooking"},
        "note": "Modifies solid fuel exposure — outdoor cooking reduces indoor air pollution even with solid fuel",
    },

    "separate_kitchen": {
        "label": "Separate Kitchen Room",
        "description": "Household has separate room used as kitchen",
        "file": "HR",
        "variable": "hv242",
        "category": "Indoor Air Quality",
        "coverage_pct": 37.2,
        "population": "households",
        "measurement": "binary",
    },

    # ─── MOSQUITO NET COVERAGE ────────────────────────────────────
    "household_has_net": {
        "label": "Household Has Mosquito Bed Net",
        "description": "Household has at least one mosquito bed net",
        "file": "HR",
        "variable": "hv227",
        "category": "Malaria Prevention",
        "coverage_pct": 100.0,
        "population": "households",
        "measurement": "binary",
    },

    "children_slept_under_net": {
        "label": "Under-5 Children Slept Under Net",
        "description": "Children under 5 slept under mosquito bed net last night",
        "file": "HR",
        "variable": "hv228",
        "category": "Malaria Prevention",
        "coverage_pct": 42.1,
        "population": "households",
        "measurement": "categorical",
        "note": "Household-level — complements child-level ITN in KR",
    },

    "number_of_nets": {
        "label": "Number of Bed Nets in Household",
        "description": "Number of mosquito bed nets in household",
        "file": "HR",
        "variable": "hml1",
        "category": "Malaria Prevention",
        "coverage_pct": 100.0,
        "population": "households",
        "measurement": "continuous",
    },

    # ─── ASSETS & FOOD PRODUCTION ─────────────────────────────────
    "owns_agricultural_land": {
        "label": "Agricultural Land Ownership",
        "description": "Household owns land usable for agriculture",
        "file": "HR",
        "variable": "hv244",
        "category": "Food Security",
        "coverage_pct": 100.0,
        "population": "households",
        "measurement": "binary",
        "note": "Links to food production and dietary diversity — important in rural zones",
    },

    "owns_livestock": {
        "label": "Livestock Ownership",
        "description": "Household owns livestock, herds or farm animals",
        "file": "HR",
        "variable": "hv246",
        "category": "Food Security",
        "coverage_pct": 100.0,
        "population": "households",
        "measurement": "binary",
        "note": "Animal source food access — links to child protein intake and anaemia",
    },

    "has_bank_account": {
        "label": "Household Bank Account",
        "description": "Any member of the household has a bank account",
        "file": "HR",
        "variable": "hv247",
        "category": "Financial Inclusion",
        "coverage_pct": 100.0,
        "population": "households",
        "measurement": "binary",
    },

    "mobile_financial_transactions": {
        "label": "Mobile Money Use",
        "description": "Mobile phone used for financial transactions",
        "file": "HR",
        "variable": "hv263",
        "category": "Financial Inclusion",
        "coverage_pct": 100.0,
        "population": "households",
        "measurement": "binary",
    },

    # ─── LIGHTING ────────────────────────────────────────────────
    "light_source": {
        "label": "Type of Light Source",
        "description": "Type of lighting used in the home",
        "file": "HR",
        "variable": "hv262",
        "category": "Living Conditions",
        "coverage_pct": 100.0,
        "population": "households",
        "measurement": "categorical",
        "note": "Electricity access proxy — links to food storage, healthcare access at night",
    },

    # ─── TOILET SHARING ──────────────────────────────────────────
    "toilet_shared": {
        "label": "Shared Toilet Facility",
        "description": "Share toilet with other households",
        "file": "HR",
        "variable": "hv225",
        "category": "WASH",
        "coverage_pct": 77.4,
        "population": "households",
        "measurement": "binary",
        "note": "Shared toilets increase disease transmission even with improved facilities",
    },

    "toilet_location": {
        "label": "Toilet Location",
        "description": "Location of toilet facility relative to dwelling",
        "file": "HR",
        "variable": "hv238a",
        "category": "WASH",
        "coverage_pct": 77.4,
        "population": "households",
        "measurement": "categorical",
    },
}

# New categories from HR
HR_NEW_CATEGORIES = {
    "Food Security": [
        "food_insecurity_worry",
        "food_insecurity_unable_healthy",
        "food_insecurity_skipped_meal",
        "food_insecurity_hungry",
        "food_insecurity_no_eat_day",
        "food_insecurity_moderate",
        "food_insecurity_severe",
        "owns_agricultural_land",
        "owns_livestock",
    ],
    "Indoor Air Quality": [
        "indoor_smoking",
        "cooking_indoor_outdoor",
        "separate_kitchen",
    ],
    "Financial Inclusion": [
        "has_bank_account",
        "mobile_financial_transactions",
    ],
    "Living Conditions": [
        "light_source",
    ],
}

if __name__ == "__main__":
    print(f"HR-specific outcome additions: {len(HR_OUTCOME_ADDITIONS)}")
    print()
    for key, val in HR_OUTCOME_ADDITIONS.items():
        print(f"  {val['label']} ({val['coverage_pct']}% coverage) — {val['file']}:{val['variable']}")
