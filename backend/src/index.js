'use strict';

require('dotenv').config();

const express = require('express');
const compression = require('compression');
const cors = require('cors');
const morgan = require('morgan');
const { PrismaClient } = require('@prisma/client');

const alaafiaAccessRouter = require('./routes/alaafiaAccess');

// ─── Initialise ───────────────────────────────────────────
const app = express();
// Behind a proxy (Railway/Render/etc.): trust the first hop so req.ip is the
// real client IP. Harmless locally.
app.set('trust proxy', 1);
const prisma = new PrismaClient();
const PORT = process.env.PORT || 4000;

// ─── Middleware ───────────────────────────────────────────
app.use(compression());

// Comma-separated CORS_ORIGINS in .env overrides the default list. During the
// transition the Àlááfìà pages may still be served from iyawo.org.
const corsOrigins = (process.env.CORS_ORIGINS ||
  'http://localhost:5173,http://localhost:3000,https://iyawo.org,https://www.iyawo.org')
  .split(',').map(s => s.trim()).filter(Boolean);

app.use(cors({
  origin: corsOrigins,
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));
app.use(morgan(process.env.NODE_ENV === 'production' ? 'combined' : 'dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// ─── Routes ───────────────────────────────────────────────
//
// The population-health data routes (/api/alaafia/precomputed*, /analyse,
// /job, /cached) were torn down 2026-09-06 — the precomputed datasets they
// served carried systematic geographic misattribution and the live pipeline
// route never ran in production. See REBUILD_ASSESSMENT_2026-09-06.md.
// Archived code: _archive_demo_2026-09-06/.

// API-access request + approval workflow (unchanged, works)
app.use('/api/alaafia-access', alaafiaAccessRouter);

// Health check
app.get('/api/health', (_req, res) => {
  res.json({
    status: 'ok',
    service: 'alaafia-api',
    timestamp: new Date().toISOString(),
  });
});

// ─── 404 handler ─────────────────────────────────────────
app.use((_req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

// ─── Global error handler ─────────────────────────────────
// eslint-disable-next-line no-unused-vars
app.use((err, _req, res, _next) => {
  console.error(err);
  res.status(500).json({ error: 'Internal server error' });
});

// ─── Start ────────────────────────────────────────────────
app.listen(PORT, async () => {
  console.log(`[alaafia] Server running on http://localhost:${PORT}`);
  try {
    await prisma.$connect();
    console.log('[alaafia] Prisma connected to database successfully');
  } catch (err) {
    console.error('[alaafia] Prisma failed to connect to database:', err.message);
  }

  // Keep-alive ping every 4 minutes to prevent cold starts on free tiers
  if (process.env.BACKEND_URL) {
    setInterval(async () => {
      try {
        await fetch(process.env.BACKEND_URL + '/api/health');
        console.log('[alaafia] keep-alive ping sent');
      } catch (e) {
        console.log('[alaafia] keep-alive failed:', e.message);
      }
    }, 4 * 60 * 1000);
  }
});

// Graceful shutdown
const shutdown = async (signal) => {
  console.log(`[alaafia] ${signal} received — shutting down`);
  await prisma.$disconnect();
  process.exit(0);
};
process.on('SIGINT', () => shutdown('SIGINT'));
process.on('SIGTERM', () => shutdown('SIGTERM'));
