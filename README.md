# Àlááfìà

Population-health intelligence for Nigerian primary care. **Currently between
versions** — the first preview was torn down on 2026-09-06 (see below) and the
real product is being rebuilt.

Extracted from the Ìyàwó monorepo on 2026-09-06. Ìyàwó (the CHEW clinical
decision-support tool) is a separate product; Àlááfìà is the intended paid
intelligence layer on top of Ìyàwó's de-identified encounter stream.

**Read first:** `REBUILD_ASSESSMENT_2026-09-06.md` (what this is for, what to
keep, the rebuild direction) and `AUDIT_2026-09-06.md` (defect-level detail).

---

## State of the repo (2026-09-06)

### Live / working
```
alaafia/
├── backend/                     Node/Express — the access-request API only
│   └── src/
│       ├── index.js             mounts /api/alaafia-access  (+ /api/health)
│       ├── routes/alaafiaAccess.js   request → ADMIN approves → API key issued
│       ├── middleware/apiKeyAuth.js  Bearer-key check (currently unwired — no route uses it)
│       ├── middleware/auth.js        Ìyàwó ADMIN-JWT check for the admin routes
│       ├── lib/prisma.js            plain PrismaClient
│       └── utils/email.js           Resend — access-request notice / key / rotation
│   ├── prisma/schema.prisma     AlaafiaAccess model only (see "Database")
│   └── scripts/rotateAlaafiaKeys.js
├── frontend/                    Vite + React
│   └── src/
│       ├── AlaafiaPage.jsx      holding page + the access-request form (no data claims)
│       └── AlaafiaAdminPage.jsx access-request review
```

### Reference only — NOT a runnable product
```
├── agents/  utils/  scripts/  models/   the epicause_ng causal pipeline
```
Kept for the domain assets it contains (the 178-outcome DHS variable map, the
tokeniser mappings, the geography lookup, the merge recipes). Do **not** treat
it as live — see `REBUILD_ASSESSMENT_2026-09-06.md` §3–4. It has no dependency
manifest, no data, and 40+ hardcoded laptop paths.

### Archived 2026-09-06 (`_archive_demo_2026-09-06/`)
- `alaafia_precomputed*.json` — the three precomputed datasets. Removed for
  systematic geographic misattribution (44% of zone / 59% of state entries
  named the wrong zone), n=2–3 per finding, and a keyword-based quality grade.
- `routes/alaafia.js` — `/precomputed`, `/precomputed-states`, `/analyse`
  (never ran in prod; had an auth'd code-injection hole), `/job`, `/cached`.
- `frontend/AlaafiaPage.jsx` — the 1,871-line UI built on the above.

---

## Quick start

```bash
cd backend && cp .env.example .env   # fill DATABASE_URL, JWT_SECRET, RESEND_API_KEY
npm install && npx prisma generate && npm run dev     # :4000

cd frontend && npm install && npm run dev             # :5173, proxies /api → :4000
```

---

## Database

Àlááfìà **shares Ìyàwó's Postgres database.** The only table it uses is
`alaafia_access` (API-access requests + issued keys — no clinical data, no
foreign keys to Ìyàwó tables; 3 rows today, all internal test data).

- That table is **owned by the Ìyàwó repo**, which holds its migration history
  and runs `prisma migrate deploy` on deploy.
- This repo ships `backend/prisma/schema.prisma` **only so `prisma generate`
  types the client.** Do **not** run `prisma migrate` from here.
- `JWT_SECRET` must match Ìyàwó's — the admin routes verify an Ìyàwó ADMIN
  token, and `AlaafiaAdminPage.jsx` reads it from `localStorage['iyawo_token']`
  (same-origin assumption inherited from the monorepo — resolve in the rebuild).

Before real users: hash the API keys, rate-limit the public POST, move admin
auth off the shared Ìyàwó JWT (`AUDIT_2026-09-06.md` #2, #10).

---

## History

- **2026-09-06** — extracted from Ìyàwó; full audit; demo layer torn down;
  rebuild direction set. The live `iyawo.org/alaafia` still serves the old data
  from the Ìyàwó repo until the planned redirect to this GitHub repo lands.
