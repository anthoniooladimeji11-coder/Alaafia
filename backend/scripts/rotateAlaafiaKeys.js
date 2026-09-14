'use strict';

// Rotates every issued Alaafia API key. Written for the incident where
// 'alaafia-admin-2024' (the old admin-panel gate, unrelated to these keys
// but discovered alongside them) sat exposed in the public JS bundle for
// ~2.5 months (2026-06-07 to 2026-08-24) — any key issued in that window
// must be treated as potentially compromised, so we rotate all of them.
//
// Defaults to a dry run (lists affected records, sends nothing, writes
// nothing). Pass --execute to actually rotate keys and email new ones out.
//
// Usage:
//   node scripts/rotateAlaafiaKeys.js            # dry run
//   node scripts/rotateAlaafiaKeys.js --execute   # rotate + email

const crypto = require('crypto');
const { PrismaClient } = require('@prisma/client');
const { sendAPIKeyRotationEmail } = require('../src/utils/email');

const prisma = new PrismaClient();
const EXECUTE = process.argv.includes('--execute');

async function main() {
  const requests = await prisma.alaafiaAccess.findMany({
    where: { status: 'approved', apiKey: { not: null } },
    orderBy: { createdAt: 'asc' },
  });

  if (requests.length === 0) {
    console.log('No approved records with an issued API key. Nothing to rotate.');
    return;
  }

  console.log(`${EXECUTE ? 'EXECUTING' : 'DRY RUN'} — ${requests.length} key(s) to rotate:`);
  for (const r of requests) {
    console.log(`  ${r.id}  ${r.email}  (${r.organisation})`);
  }

  if (!EXECUTE) {
    console.log('\nDry run only — no keys changed, no emails sent. Re-run with --execute to apply.');
    return;
  }

  let ok = 0;
  let failed = 0;
  for (const r of requests) {
    const newApiKey = crypto.randomBytes(32).toString('hex');
    try {
      // Email first: the old key must stay live until the replacement has
      // actually been delivered, otherwise a failed send strands the holder
      // with no working key at all.
      await sendAPIKeyRotationEmail(r, newApiKey);
      await prisma.alaafiaAccess.update({
        where: { id: r.id },
        data:  { apiKey: newApiKey },
      });
      console.log(`  emailed + rotated: ${r.email}`);
      ok++;
    } catch (err) {
      console.error(`  FAILED for ${r.email} (id=${r.id}) — key NOT changed:`, err.message);
      failed++;
    }
  }

  console.log(`\nDone. ${ok} rotated and emailed, ${failed} failed.`);
  if (failed > 0) {
    console.log('Failures left the old key untouched — safe to re-run.');
  }
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect());
