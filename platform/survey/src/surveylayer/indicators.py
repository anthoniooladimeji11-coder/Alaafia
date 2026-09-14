"""The starter indicator set.

28 indicators across every domain in the vision (§7). All IDs verified
against the DHS API. Extend freely — `domain` and `unit` are ours;
everything else the API supplies.

Tuple: (dhs_id, slug, domain, unit, populace)
  unit    — "pct" (percent), "rate_1000" (deaths per 1,000), "prev_pct"
  populace— who the denominator is: children / women / household / persons
"""

from __future__ import annotations

INDICATORS: list[tuple[str, str, str, str, str]] = [
    # --- child nutrition -----------------------------------------------
    ("CN_NUTS_C_HA2", "child_stunting",        "nutrition",   "pct",       "children"),
    ("CN_NUTS_C_WH2", "child_wasting",         "nutrition",   "pct",       "children"),
    ("CN_NUTS_C_WA2", "child_underweight",     "nutrition",   "pct",       "children"),
    ("CN_ANMC_C_ANY", "child_anaemia_any",     "anaemia",     "pct",       "children"),
    ("CN_IYCB_C_EXB", "excl_breastfeeding",    "nutrition",   "pct",       "children"),
    # --- child health / immunisation ---------------------------------
    ("CH_VACC_C_BAS", "fully_vaccinated",      "immunisation","pct",       "children"),
    ("CH_VACC_C_NON", "zero_dose",             "immunisation","pct",       "children"),
    ("CH_VACC_C_PT3", "pentavalent3",          "immunisation","pct",       "children"),
    ("CH_VACC_C_MSL", "measles1",              "immunisation","pct",       "children"),
    ("CH_DIAT_C_ORT", "diarrhoea_ors_rhf",     "child_health","pct",       "children"),
    # --- child mortality --------------------------------------------
    ("CM_ECMR_C_NNR", "neonatal_mortality",    "mortality",   "rate_1000", "children"),
    ("CM_ECMR_C_IMR", "infant_mortality",      "mortality",   "rate_1000", "children"),
    ("CM_ECMR_C_U5M", "under5_mortality",      "mortality",   "rate_1000", "children"),
    # --- maternal / reproductive ----------------------------------
    ("RH_ANCN_W_N4P", "anc4",                  "maternal",    "pct",       "women"),
    ("FP_CUSA_W_MOD", "mcpr_all_women",        "family_plan", "pct",       "women"),
    ("FP_NADA_W_UNT", "unmet_need_fp",         "family_plan", "pct",       "women"),
    # --- malaria ---------------------------------------------------
    ("ML_NETP_H_IT2", "itn_access",            "malaria",     "pct",       "household"),
    ("ML_PMAL_C_RDT", "malaria_rdt_prev",      "malaria",     "prev_pct",  "children"),
    ("ML_FEVT_C_ADV", "fever_care_sought",     "malaria",     "pct",       "children"),
    ("ML_IPTP_W_3SP", "iptp3",                 "malaria",     "pct",       "women"),
    # --- WASH ----------------------------------------------------
    ("WS_SRCE_P_IMP", "improved_water",        "wash",        "pct",       "persons"),
    ("WS_TLET_P_IMP", "improved_sanitation",   "wash",        "pct",       "persons"),
    ("WS_TLET_P_NFC", "open_defecation",       "wash",        "pct",       "persons"),
    # --- women's status / assets -------------------------------
    ("ED_LITR_W_LIT", "women_literate",        "education",   "pct",       "women"),
    ("AN_NUTS_W_THN", "women_thin_bmi",        "nutrition",   "pct",       "women"),
    ("AN_ANEM_W_ANY", "women_anaemia_any",     "anaemia",     "pct",       "women"),
    ("HC_ELEC_H_ELC", "household_electricity", "living_std",  "pct",       "household"),
]

IDS = [i[0] for i in INDICATORS]
META = {i[0]: {"slug": i[1], "domain": i[2], "unit": i[3], "populace": i[4]}
        for i in INDICATORS}
