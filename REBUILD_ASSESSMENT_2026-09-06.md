# Àlááfìa — end-to-end assessment and rebuild direction

**Date:** 2026-09-06
**Context:** extracted from the Ìyàwó monorepo today; founder's call is to tear the demo layer down to the studs and rebuild with more data. This document is the "beginning to end" read of what exists, what the project is actually for, and what a real version needs.
**Companion docs:** `AUDIT_2026-09-06.md` (the defect-level detail), `project_iyawo_alaafia_revenue_strategy.md` (founder's strategy notes, in Claude memory).

---

## 1. What was torn down today

Removed from the served path (archived, not deleted, in `_archive_demo_2026-09-06/`):

| Removed | Why |
|---|---|
| `alaafia_precomputed.json`, `_states.json`, `_v2_backup.json` | 44% of zone entries / 59% of state entries misattributed causal claims to the wrong geography; every finding rested on 2–3 simulated records; "Grade A" was a keyword count. Not fixable by editing. |
| `backend/src/routes/alaafia.js` (`/precomputed`, `/precomputed-states`, `/analyse`, `/job`, `/cached`) | Served the above, or (for `/analyse`) never ran in production and carried an authenticated code-injection hole. |
| `frontend/src/AlaafiaPage.jsx` (1,871 lines) | A UI built entirely to display the removed datasets. Replaced with an honest holding page + the access-request form. |

**Kept, because it works and is real:**
- `alaafia_access` request → admin-approve → API-key workflow (`routes/alaafiaAccess.js`, `middleware/apiKeyAuth.js`, `utils/email.js`). 3 rows in the DB, all internal test data.
- The Python pipeline source (`agents/`, `utils/`, `scripts/`) — as **reference**, not as a runnable product. See §4.
- The extraction scaffold (backend/frontend shells, README).

The live site at `iyawo.org/alaafia` still serves the old data from the **Ìyàwó** repo's copy — this teardown is in the `alaafia` repo only, per your call. The planned redirect (`iyawo.org/alaafia` → GitHub) is what removes it from the live site.

---

## 2. The aim — and the problem to resolve first

From the strategy notes: Àlááfìa is **the revenue engine**. Ìyàwó runs free at PHCs (grant-funded, the clinical anchor and data-acquisition layer); Àlááfìa is the paid intelligence layer on top of the de-identified encounter stream. Target buyers: Gates, Global Fund, PMI, Malaria Consortium, CHAI, Society for Family Health, and government M&E budgets. Strongest wedge: **program-evaluation-as-a-service + real-time surveillance / early-warning**. Framing: *"Nigeria's primary-health-care intelligence layer — from the CHEW's tablet to the mother's phone to the ministry's dashboard."*

**There are two different Àlááfìas in play, and the rebuild has to pick a lane (or sequence them):**

| | **A — Survey causal reasoning** (what got built) | **B — Live-stream operational intelligence** (the revenue vision) |
|---|---|---|
| Data | NDHS 2024 / MICS 2021 public microdata — a fixed, 2-year-old snapshot | Ìyàwó's live de-identified encounter stream + LMIS/HMIS/geospatial |
| Question | "What causes stunting in zone X?" (retrospective, academic) | "Is program Y working? Where is the malaria spike this week? Which PHC is stocking out?" (operational, current) |
| Buyer | researchers, papers | funders' M&E lines, state health boards — people with budgets *today* |
| Method | causal DAGs over cross-sectional survey data | evaluation designs (ITS, diff-in-diff, matched controls), surveillance signals, benchmarking — grounded by a live panel |
| Moat | none — anyone can download DHS | the live stream. Nobody else has continuous CHEW-level encounter data for Nigerian PHCs |
| Blocker | none (data is public) | Ìyàwó needs real encounter volume (≈0 today); Oyo PHC Board data-sharing + commercial-use consent; the separate analytics store |

The current codebase is **entirely A**. The money is in **B**. A is a reasonable *research demo* and a way to have something to show while B's prerequisites mature — but it should be labelled as research, not sold as the product, and it should not block on the same standard as B.

**Recommendation:** the rebuilt Àlááfìa is **B**, with A retained as a clearly-labelled research track that reuses B's data infrastructure. The 3-agent causal idea survives — but as the strategy notes already say, "continuously grounded by live data," i.e. inside B, not as n=3 survey narration.

---

## 3. What the current work actually is (honest read)

The build arc (from git history): EDA of all 6 DHS file types → a real 39,050-record merge → a 178-outcome variable map → a tokeniser → local LLMs (Llama 3.1 8B + N-ATLAS) → a 3-agent "propose / critique / judge" loop → an equity layer → precompute scripts.

The **data engineering half is genuine work**. The **reasoning half does not do what it claims:**

- **No causal inference happens.** `run_pipeline()` is three `ollama run` shell-outs. The model gets one woman's `|`-joined tag string plus a hardcoded priors paragraph and writes a "X causes Y via Z" sentence. There is no DAG estimation, no confounder adjustment, no effect size, no counterfactual, no uncertainty from data. The `stats` block next to each result (real, n≈9,000) creates an impression of rigour the pathway doesn't have.
- **n = 1–3.** Each zone/outcome finding is the single highest-"scored" pathway out of ~15 runs on 3 fixed-seed records per wealth group. States: 2–3 records total. Re-running doesn't resample.
- **The quality grade is a rhetoric detector.** `validation_framework.py` scores four dimensions by substring match — "via", "zone", "south", confounder names — all of which the prompt forces into the output. 17 of 18 zone findings scored "A" while their own 3 records disagreed with each other. The backwards claim *"improved sanitation causes stunting"* would still score A.
- **Conclusions are hardcoded, then narrated.** `equity_interrogation.py` ships `WEALTH_ANAEMIA` numbers and a prompt that states *"This means SE anaemia is NOT primarily a poverty problem"* with `"poverty_explains_disparity": false` pre-filled, and asks the model to elaborate. `highest_impact_intervention_zone` is `max()` over a hardcoded dict, string-injected into the "AI" response.
- **Cross-zone misattribution is structural.** The equity layer is *designed* to feed the model all six zones' data and ask it to compare — so its prose names other zones, and `precompute.py` files that prose under one geography's key. That is why Sokoto's page describes North-Central women.
- **It is not reproducible.** No `requirements.txt`. No data or model weights in the repo. 40+ hardcoded `/Users/theoneglobal/...` paths. Three merge scripts that overwrite the same parquet in place in an undocumented order. Two different "stunting %" formulas in the same codebase.

The methodology-defence work that was already done — `natlas_role.md`, `validation_framework` "v2", the expert-rating form — was the right instinct pointed at the wrong target. The expert-rating form (`utils/expert_validation_form.md`) is actually a sound instrument (Nigerian epidemiologists, Cohen's Kappa ≥ 0.60, ≥30 records × 2 raters) that **was built and never run.**

---

## 4. What to keep, what to discard

### Keep — real assets, carry into the rebuild
| Asset | Value |
|---|---|
| `utils/outcome_map.py` (+ `_KR/_HR/_GR/_CR/_complete`) | 178 health outcomes mapped to exact DHS variables, coverage %, value codes, binary definitions across all 5 file types. Weeks of codebook work. This is the domain layer. |
| `utils/tokeniser.py` variable→concept mappings | The DHS-code→semantic-label logic (fuel, water, sanitation, parity, ANC, IPV, dietary diversity, husband factors…) is reusable regardless of what consumes it. Needs the bare-`except` cleanup and a "missing ≠ negative" fix. |
| `utils/nigeria_geography.py` | Correct 37-state / 6-zone map. Keep as-is. |
| `scripts/merge_*.py` *recipes* | Which DHS files, which variables, which join keys, which cluster-level aggregations. Rewrite as one idempotent pipeline, but the knowledge of *what to merge* is the hard part and it's here. |
| The 3-agent concept | Propose → critique → adjudicate is a fine pattern — for turning a **computed** result into a policy narrative, or for hypothesis generation that a stats layer then tests. Not for generating findings from n=3. |
| `expert_validation_form.md` | Good instrument. Actually run it against whatever the rebuild produces. |
| `alaafia_access` system | Works. Needs key hashing + rate limiting (audit #2, #10) before real users. |
| The name, brand, the "intelligence layer" framing | Fine. |

### Discard — dead ends
- The precompute-to-static-JSON-served-as-live architecture.
- `validation_framework.py`'s keyword scorer (keep the *four dimensions* as a human rubric — it's the expert form's rubric — drop the automated scoring).
- Hardcoded `NIGERIA_PRIORS` / `ZONE_PROFILES` / `WEALTH_ANAEMIA` in three files. Priors come from the data layer at runtime or not at all.
- `ollama` shell-out with ANSI-stripping and regex JSON extraction. If an LLM is in the loop, call a real API with structured/tool output.
- `exec(open(...).read())` module loading.
- n=1–3 sampling; fixed-seed "resampling"; `pathway[:40]` consistency; `max(quality_score)` as "dominant".
- Serving three JSON files with different schemas.

---

## 5. "Add more data" — what that means concretely

### If the rebuild is A (survey causal, research track)
- **Full NDHS 2024**, all modules, with **survey weights** (`v005`, cluster, strata) — none of the current code applies weights, so even the `stats` are unweighted and biased.
- **MICS 2021** — currently *claimed on the site* ("31,103 MICS 2021 children") but **not used by any script**. Either wire it in or drop the claim.
- **NDHS 2018** (already explored in git history) for trend/temporal analysis.
- **NNHS** (National Nutrition and Health Survey) — annual, more current than DHS for stunting/wasting.
- **DHIS2 / HMIS** aggregates — monthly facility data, the bridge toward "current".
- Geospatial (already partially present via the GC file): malaria surfaces, travel time, conflict (ACLED), climate.

### If the rebuild is B (live-stream operational intelligence — the revenue product)
- **Ìyàwó's encounter stream** — the actual asset. Via a **one-directional scheduled ETL into a separate analytics store** (hard constraint: never the live clinical DB; free-text `notes` never leaves Ìyàwó; aggregate-first, minimum cell size). This does not exist yet and Ìyàwó has ≈0 real encounters today ("clean build").
- **LMIS / stock data** (state medical stores, or Ìyàwó's own prescription vs. formulary signal) for stockout intelligence.
- **Facility registry** (the Nigeria MFL / Oyo PHC Board's 264-PHC list) for benchmarking denominators.
- **Program calendars** — when and where each funder's intervention rolled out — the exposure variable for evaluation-as-a-service.
- DHIS2 for the district-level backdrop.

The order matters: **B's data doesn't exist until Ìyàwó scales.** "Add more data" for B is mostly "get Ìyàwó deployed and accumulating encounters, and sign the Oyo PHC Board data-sharing agreement."

---

## 6. Rebuild architecture (for B, the revenue product)

```
  Ìyàwó clinical DB (Supabase)
        │  one-directional scheduled ETL — aggregates only, no notes, min cell size
        ▼
  Àlááfìa analytics store  ◄──── external feeds: DHIS2, LMIS, MFL, program calendars,
  (separate DB / warehouse)       geospatial, NDHS/MICS as historical baseline
        │
        ▼
  Analysis layer (the actual product logic)
   ├─ Surveillance:     anomaly detection on encounter/RDT/referral rates by area+week
   ├─ Program eval:     ITS / diff-in-diff / matched controls against program calendars
   ├─ Supply:           predicted vs. actual consumption, stockout risk
   ├─ Benchmarking:     facility quality percentiles on referral appropriateness, outcomes
   └─ Causal (track A):  DAG proposal → **estimation on real data** → narrative
        │  every output carries: n, CI, method, date, cell-suppression note
        ▼
  Narrative layer (LLM, real API, tool output)
   turns a computed result + its numbers into policy-legible text. Never generates the finding.
        │
        ▼
  Delivery
   ├─ API (keys hashed + rate-limited; the current access workflow, hardened)
   ├─ Dashboards (funder / state-health-board views)
   └─ Scheduled reports (the "evaluation-as-a-service" deliverable)
```

Non-negotiables baked in from the start (all in the strategy notes, all expensive to retrofit):
- Separate analytics store; one-directional ETL; **never** the live clinical DB.
- Aggregate-first, never record-level; enforced minimum cell size with suppression.
- Free-text `notes` never leaves Ìyàwó.
- Commercial/secondary use has an explicit consent basis, visible in Ìyàwó's consent flow, with IRB cover — distinct from "no names stored."
- Data-sharing / ownership agreement with the Oyo State PHC Board **before** anything derived is sold.

---

## 7. Prerequisites & sequencing

Àlááfìa-B cannot really start until:
1. **Ìyàwó is deployed and accumulating encounters** at enough PHCs for area×week cells to clear a minimum size. Today: not yet.
2. **Oyo State PHC Board data-sharing agreement** signed, covering commercial use and data ownership.
3. **Commercial-use consent basis** added to Ìyàwó's consent flow + IRB cover.
4. **The separate analytics store + ETL** is built (this *can* start now — it's infrastructure, needs no live volume to design).
5. A decision on **which lane leads** (§2) and who owns Àlááfìa day-to-day.

The strategy notes put real Àlááfìa revenue **12–24 months out**, gated on Ìyàwó adoption, and say the build starts "when it's time" — not now. Nothing in this assessment contradicts that. The useful work available *today* is: (a) this teardown, (b) preserving the reference assets in §4, (c) designing the analytics store + ETL contract, (d) the redirect so the live site stops overclaiming.

---

## 8. Concrete next steps

**Now (this session or soon):**
- [x] Tear down the demo data + routes + page (done — `_archive_demo_2026-09-06/`).
- [ ] Land the `iyawo.org/alaafia` → GitHub redirect (Phase 2 of the extraction) so the live site stops serving the old data.
- [ ] Decide: does the `alaafia` repo also absorb the `epicause_ng` local checkout (data/outputs/venv) or stay code-only?
- [ ] Salvage-organise: move `utils/outcome_map*.py`, `nigeria_geography.py`, the tokeniser mappings, and the merge recipes into a clearly-labelled `reference/` or `research/` tree so they're not mistaken for a live product.

**Near term (infrastructure, no live volume needed):**
- [ ] Write the ETL contract: exactly which Ìyàwó aggregates cross the boundary, at what grain, with what suppression rule. Review against the hard constraints.
- [ ] Stand up the analytics store (separate project/DB).
- [ ] Harden the access system: hash API keys, add rate limiting, move admin auth off the shared Ìyàwó JWT.

**Gated on Ìyàwó scale + the PHC Board agreement:**
- [ ] Build the surveillance and program-evaluation layers against real accumulating data.
- [ ] Run the expert-validation instrument against real outputs before anything is published or sold.

---

*Prepared after a full read of the pipeline, the extracted code, the database, and the datasets. The teardown is done in the `alaafia` repo working tree, uncommitted, for your review.*
