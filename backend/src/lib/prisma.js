'use strict';

// Shared Prisma client for the Àlááfìà API.
//
// Plain client, on purpose. The Ìyàwó copy of this file carries an RLS
// Phase-A extension (AsyncLocalStorage + a transaction-local GUC on every
// query); none of the Àlááfìà routes need it, and it depends on Ìyàwó-only
// middleware, so it is deliberately left out here.
//
// DATABASE_URL currently points at Ìyàwó's Postgres (the `alaafia_access`
// table lives there — see backend/prisma/schema.prisma and the README).

const { PrismaClient } = require('@prisma/client');

module.exports = new PrismaClient();
