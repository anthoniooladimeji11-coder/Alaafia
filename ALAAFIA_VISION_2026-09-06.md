# Àlááfìa — vision & strategy

**Created:** 2026-09-06 · **Revised:** 2026-09-07
**Companion to:** `REBUILD_ASSESSMENT_2026-09-06.md` (audit, teardown), `AUDIT_2026-09-06.md` (defects), `platform/geo/README.md` (the geography spine, built), `content/PLAYBOOK.md` (the Sep 2026 → Jan 2027 content run).

**What changed in the 2026-09-07 revision:** the earlier draft assumed grant money would fund the build and that "data-layer SaaS" was the first revenue. Both are wrong. This revision keeps the data universe, domains, and technical spine intact, and rewrites the market case, the revenue order, and the honest risks. It adds a stress test, a straight answer on why it matters, and the strategic call the founder has to make.

---

## 0. Where the build actually is (2026-09-07)

Real progress, not slideware:

- **Geography spine — done.** `platform/geo/`: 37 states / 774 LGAs / 5,872 wards / 745,191 settlements / 41,778 health facilities, one P-code scheme, name resolver, DHS crosswalk (37/37 states). 35 tests. This is Phase 0, step 1 of §7 — the piece everything else keys to.
- **Content run — planned.** `content/PLAYBOOK.md`: 42 posts, 9 Sep → 29 Jan, phased. Design kit: 3 looks, published canvas.
- **Not built yet:** the survey ingest, the small-area models, any product surface, any revenue.
- **Target:** something public and credible by **Jan 2027**.

---

## 1. The reframe (unchanged, tightened)

Àlááfìa is:

> **The subnational health-intelligence layer for Nigeria** — public surveys + satellite + (later) routine and Ìyàwó data, fused onto one geography, modelled down to LGA and ward with stated uncertainty, checked against the official state figures.

Its users are **organisations** — the government, the big implementers, the funders, and the consultancies that serve them. That is the category. It is not a consumer product (see §8 for the everyday-user question). "Orgs are slow and cynical" is true and it is still the category.

What could make it defensible:
1. **The geography spine.** Getting 40 messy sources onto one Nigerian admin hierarchy is weeks of unglamorous work everyone needs — *but it's built on public data and took ~a day; it's table stakes, not a moat* (see §4).
2. **Model-based small-area estimation done transparently** — every number with a credible interval, reproducible, calibrated. The method is public; the *discipline* is the differentiator.
3. **The Ìyàwó stream, later** — continuous CHEW-level data. The only real moat, and it doesn't exist yet.

---

## 2. The market — real, and smaller/harder than the first draft said

Nigeria takes more global-health money than any country in Africa:

| Flow | Order of magnitude |
|---|---|
| Global Fund Nigeria (malaria + HIV + TB, per cycle) | ~$0.9B |
| US PMI Nigeria | ~$75M / yr |
| World Bank health (IMPACT, ANRIN, others) | $1B+ active |
| Gates Foundation Nigeria | 9 figures / yr |
| GAVI, big INGOs (Malaria Consortium, CHAI, SFH, …), state health budgets, NHIA | collectively $B+ |

**Measurement / M&E is ~5–10% of a programme budget**, spent today on one-off consultant evaluations ($80k–$600k), 12–24 months late, on data scraped together once and discarded. That gap is real and every person in Nigerian public health knows it.

**But** — and the first draft glossed all of this:

- **Buyers often don't control the M&E spend.** Donors prescribe the framework (mandatory coverage surveys, LQAS, SMART). Redirecting money to a subscription needs donor sign-off, which is slow.
- **You replace a slice of the consultant, not the consultant.** They also do qualitative work, stakeholder management, capacity-building, the funder-required report. Realistically you compete for $50–100k of a $300k engagement, not all of it.
- **The buyer is often the party being evaluated.** An implementer purchasing an "independent" evaluation that finds no effect has an incentive problem. Independence sells to the donor and worries the person with the card.
- **Funders distrust "modelled."** WHO / Global Fund have wanted *measured* coverage for disbursement decisions. Getting SAE accepted as a basis for money moving is a multi-year institutional fight.
- **Procurement will grind a 2-year-old company** with no track record and possibly no local registration. RFPs, framework agreements, 6–18 month cycles.
- **The customer base is contracting.** 2025–26 gutted global-health funding. Selling measurement while programmes get cancelled is hard.

**Honest market shape:** capturing a sliver — a few dozen paying relationships — is still a multi-$M recurring business inside a $100M+ measurement spend. But the ARR math in the first draft ("mid-seven to eight figures in a couple of years") was fantasy given the sales cycles and the climate. It's a **services-margin business (~30–50%), not software margins**, for years.

---

## 3. Revenue — rethought, in the right order, no grants assumed

The first draft's mistake: treating "data-layer SaaS" as the first money. It isn't. Subscriptions come *after* trust is built. The real order:

### #1 — Bespoke analysis (first cash, H1 2027)
Someone writing a Global Fund proposal, a board deck, a programme design needs *"stunting by ward in these 6 states, with a wealth-quintile cut, this month."* Today they wait weeks for a consultant. You run it off the engine in days.
- **Who:** implementers, consultancies (Dalberg, Palladium, local firms), funder country offices, universities, journalists.
- **Price:** ~$5k–30k per piece. **2–3 a month funds a small team.**
- **Needs:** only the engine working + the geography spine + SAE for a handful of indicators. No product polish.
- **Lead-gen:** the content run. That is the content run's job.

### #2 — One anchor deployment (the reference, H1 2027)
Oyo State PHC Board (door already open via Ìyàwó) or one implementer. Build the targeting/surveillance dashboard they'd actually use for their PHCs. Get paid, get a case study.
- **Price:** ~$20k–80k.
- **Value:** one real reference beats ten pitches. It also defines the product roadmap from a real user, not a guess.

### #3 — Recurring access (after #1 and #2 prove it)
API / seat access to the estimates for the orgs that keep coming back.
- **Price:** ~$15k–60k / org / yr.
- **Reality:** this is the "SaaS" line, but it only closes once #1 and #2 have built trust and word of mouth. Do not plan revenue on it in year one.

### #4 — Evaluation-as-a-service (latest, needs the routine-data layer)
Continuous before/after + comparison analysis, quarterly brief. The big contracts.
- **Price:** ~$60k–200k / programme / yr.
- **Needs:** programme rollout data (georeferenced, from the partner) + routine data (DHIS2) or the Ìyàwó panel. And the causal claims must survive a hostile reviewer — Nigeria's spatial confounding (conflict, other programmes saturating the same LGAs) makes DiD/matched-comparison fragile. This is the hardest one to do *credibly*, which is the whole brand.

### Later / conditional
Targeting-and-allocation, surveillance-and-early-warning, commodity intelligence, facility benchmarking, diligence-verification — all real, all need either routine-data access or Ìyàwó volume, all documented in the earlier draft's table (kept below for reference, not as a near-term plan).

<details><summary>Full revenue-line menu (reference only — not the near-term plan)</summary>

| # | Product | Who pays | Rough economics | Needs |
|---|---|---|---|---|
| A | Data-layer access / API | INGOs, consultancies, donor offices, universities | $15k–60k/org/yr | Tier 1+3 data, spine, SAE |
| B | Evaluation-as-a-service | Global Fund PRs, PMI, GAVI, foundations | $60k–200k/programme/yr | programme geographies, routine data, Ìyàwó panel |
| C | Targeting & allocation | NPHCDA, states, campaign implementers | $30k–150k/engagement | denominators, access data, modelling |
| D | Surveillance & early warning | NCDC, state epi units, WHO Nigeria | $100k–500k/yr | IDSR/DHIS2 feed, Ìyàwó edge |
| E | Commodity / supply-chain intelligence | NPSCMP, state medical stores, GHSC | $50k–250k/yr | NHLMIS or Ìyàwó prescription signal |
| F | Facility benchmarking (PBF) | states, NHIA, NPHCDA | $20k–80k/state/yr | HFR + DHIS2 + Ìyàwó outcomes |
| G | Diligence / impact verification | DFIs, impact funds, RBF verifiers | $25k–100k/engagement | the asset + eval methods |
| H | Custom research / white-label | anyone above | $15k–100k/piece | analyst time |

</details>

**The near-term plan is #1 + #2. Everything else follows or it doesn't.**

---

## 4. The honest risks (the stress test)

Beyond §2's market risks:

- **The moat is mostly not there yet.** The spine is public-data table stakes. SAE is published methods + open-source packages. **This already exists commercially** — Fraym sells African subnational estimates to USAID/Gates; also Zenysis, Atlas AI, Dalberg Data Insights, eHealth Africa, Macro-Eyes. Universities (Southampton/Utazi, JHU) do it for co-authorship, which funders often prefer because it's cheap and publishable. The *only* real moat is Ìyàwó's stream, which is contingent, unbuilt, and single-state.
- **Routine-data quality.** Nigerian DHIS2/NHMIS is incomplete, late, and gamed. Nowcasting and evaluation built on it inherit that. The "current" edge may not be trustworthy for years.
- **Existential coupling.** Àlááfìa's story is welded to Ìyàwó's, and Ìyàwó is pre-patient, pre-IRB, safety-critical, unshipped. If Ìyàwó stalls, Àlááfìa is a geospatial-analytics startup with no distribution.
- **Focus.** Founder is running Ìyàwó (safety-critical) + Àlááfìa + SAFARI + grant applications. This is the biggest risk. Àlááfìa cannot be a parallel full build; it has to be sequenced.
- **Capability gap.** Credible SAE is not junior work. Needs a real statistician / geostatistician, plus a Nigeria BD person with funder relationships. Expensive senior hires for a pre-revenue company.
- **DHS commercial-use terms** for selling derived products — unresolved. Confirm before selling *access* (not before building).

---

## 5. Does it matter? — three straight answers

**In the world — yes, unambiguously.** Every year someone decides which ~200 of 774 LGAs get the malaria campaign, the extra midwives, the vaccine push. That targeting runs on state-level or stale data. Better targeting of the *same* budget = more lives saved per naira. Nigeria has ~30% of global malaria deaths and the most zero-dose children on earth. Getting "where" right is among the highest-leverage moves in that system.

**Commercially — yes, but hard.** It attaches to a budget line (M&E) that exists *regardless of the funding climate*. You're a faster, cheaper, checkable vendor for spend already committed — not a new ask. That's why it can survive a drought. It is not, on current evidence, a venture-scale rocket; it's a real, services-shaped business that could become more if the moat (Ìyàwó) materialises.

**For the founder strategically:** it's the data asset that, fused with Ìyàwó's encounter stream, becomes uncatchable. Standalone and near-term it's modest. Whether it deserves to be the *main* focus is the open question — see §9.

---

## 6. The data universe *(unchanged — still the plan)*

See the earlier draft's Tiers 1–5. In brief:
- **Tier 1 — survey microdata** (free, ~2-week registration): NDHS 1990/1999/2003/2008/2013/2018/2023–24; MICS 1999/2007/2011/2016–17/2021; NMIS 2010/2015/2021; NAIIS 2018; NLSS 2003–04/2009–10/2018–19/2022–23; GHS-Panel waves 1–5. **Register now.** GPS/geospatial-covariate files are a separate DHS request — essential for SAE.
- **Tier 2 — routine** (partnership/scraping): NHMIS/DHIS2, NHLMIS, IDSR/SORMAS, HFR, programme MIS, WUENIC, IHME GBD.
- **Tier 3 — geospatial** (public, ready): GRID3, WorldPop, Malaria Atlas, CHIRPS/ERA5/MODIS/VIIRS, Meta RWI, ACLED, building footprints.
- **Tier 4 — economic/financing:** NBS, BudgIT, IATI/PEPFAR/Global Fund geographies.
- **Tier 5 — the moat:** Ìyàwó, via one-directional ETL to a separate analytics store, aggregate-only, min cell size, `notes` never crossing.

## 7. Domains *(unchanged)*

Every measurable domain of Nigerian primary health + determinants: child health & survival, maternal & reproductive, full nutrition, infectious disease (malaria, TB, HIV cascade, NTDs, outbreaks), NCDs & injury, WASH, health-system readiness, determinants & equity, climate–health. See the earlier draft's table. The point stands: a buyer working on *any* of these gets a defensible subnational number with uncertainty, a trend, an equity cut.

## 8. Technical spine *(unchanged)*

`INGEST → RESOLVE (the spine, done) → MODEL (SAE · nowcasting · evaluation · surveillance) → NARRATE (Claude, numbers attached, never generates the finding) → DELIVER (dashboards · API · briefs · alerts)`. Trust infrastructure — reproducible, sourced, dated, uncertainty-bearing, cell-suppressed — is the feature. Hard constraints from the strategy notes unchanged (separate store, one-directional ETL, never the live clinical DB, consent + IRB, Oyo data agreement before selling anything Ìyàwó-derived).

---

## 9. The everyday-user product — wanted, currently out of scope

The founder wants Àlááfìa to *also* be something ordinary Nigerians use directly — and to make revenue directly from them, not wait for a sponsor. Explored 2026-09-07, then parked as out of current scope:

- **Channel:** WhatsApp + USSD (not an app).
- **Free tier (public good + sensor + brand):** basic symptom triage ("go now / today / home care"), outbreak/campaign/seasonal alerts for your ward, find-a-working-clinic (powered by the facility layer).
- **Direct-revenue mechanics considered:** airtime micro-plan (₦100–300/mo VAS billing); verified pharmacy/PPMV network with a vendor take-rate; a health wallet (save/receive/spend at verified vendors, diaspora top-ups, transaction fees + float); parametric micro-insurance **priced per ward by the data engine**; manufacturer-funded scratch-code guidance; diaspora "care package"; SME staff plans.
- **Why it's not a distraction:** it's the sensor network (live symptom/demand/outbreak signal by ward, un-copyable) and the "greatness demo" that unlocks the org deals and any funding.
- **Why it's parked:** can't be built before Jan 2027 alongside the engine; the wallet/insurance pieces are a fintech/insurtech licensing path (CBN/NAICOM + licensed partner); paid triage sharpens the clinical-liability weight (physician protocol, IRB). Design and narrative can start now; the build is a 2027+ track.

**Current scope = the intelligence layer (§1–§8). The everyday product is a documented future track, not this year's work.**

---

## 10. Phased path *(tightened)*

- **Phase 0 — public-data platform.** Spine (✅) → ingest Tier 1 + Tier 3 → LGA-level estimates for ~30 indicators with CIs, calibrated. **This is what "out by Jan 2027" means.** Enables revenue #1 (bespoke) and #2 (anchor).
- **Phase 1 — SAE depth.** Ward-level where defensible, 50–100 indicators across the domains. Enables targeting work.
- **Phase 2 — the current layer.** DHIS2/NHMIS partnership *or* Ìyàwó ETL → nowcasting + surveillance edge. Enables #4 and the later lines.
- **Phase 3 — the service layer.** Evaluation engine, allocation simulator, benchmarking.
- **Cross-cutting, start now:** DHS/MICS microdata registration; the Oyo data agreement + commercial-use consent + IRB; the statistician + BD hires; keep the content run pointed at making #1/#2 possible by March.

---

## 11. What carries over from the old work *(unchanged)*

The 178-outcome DHS variable map, the tokeniser's code→concept mappings, `nigeria_geography.py`, the merge recipes, the 3-agent concept (repositioned as *narrate/hypothesise*, never *generate*), the access-request system (hardened), the name. Everything else in `_archive_demo_2026-09-06/` is reference.

---

## 12. The strategic call

**Is Àlááfìa your main focus, or a capability inside the Ìyàwó story until Ìyàwó has traction and data?**

The honest test, decidable by ~March 2027:
- If **bespoke revenue (#1) + one anchor (#2)** materialise in H1 2027 → it's a real standalone thing, lean in.
- If they don't → it's the second option: a research capability and a feature of the Ìyàwó narrative, kept warm, not resourced as a company.

Don't decide now. Aim the build and the content run at making #1 and #2 *possible* by March, so the call gets made on evidence rather than hope.

---

*Short version: Àlááfìa turns a six-figure one-off health survey into a standing, checkable, ward-level picture — sold first as bespoke analysis, proven with one anchor deployment, and only then as a subscription. The problem is real, the method is real, the standalone business is not yet — and the everyday-user product the founder wants is a documented 2027+ track, not this year's build.*
