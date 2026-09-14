'use strict';

const prisma = require('../lib/prisma');

/**
 * Validates Bearer API key from Authorization header against AlaafiaAccess table.
 * Attaches the approved record to req.alaafiaUser on success.
 * Only approved records with a non-null apiKey are accepted.
 */
async function apiKeyAuth(req, res, next) {
  const authHeader = req.headers['authorization'] || '';
  const match = authHeader.match(/^Bearer\s+(.+)$/i);

  if (!match) {
    return res.status(401).json({ error: 'Missing or malformed Authorization header. Expected: Bearer <api_key>' });
  }

  const key = match[1].trim();

  try {
    const record = await prisma.alaafiaAccess.findUnique({
      where: { apiKey: key },
    });

    if (!record || record.status !== 'approved') {
      return res.status(401).json({ error: 'Invalid or inactive API key' });
    }

    req.alaafiaUser = record;
    return next();
  } catch (err) {
    return next(err);
  }
}

module.exports = apiKeyAuth;
