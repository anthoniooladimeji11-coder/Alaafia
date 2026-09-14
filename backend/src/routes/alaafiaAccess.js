'use strict';

const crypto  = require('crypto');
const express = require('express');
const prisma  = require('../lib/prisma');
const { verifyToken, requireRole } = require('../middleware/auth');
const { sendAccessRequestNotification, sendAPIKeyEmail } = require('../utils/email');

const router = express.Router();

// POST /api/alaafia-access — public, saves request to DB, emails admin
router.post('/', async (req, res, next) => {
  try {
    const { name, organisation, role, email, useCase } = req.body;

    if (!name || !organisation || !role || !email) {
      return res.status(400).json({ error: 'name, organisation, role, and email are required' });
    }

    const record = await prisma.alaafiaAccess.create({
      data: {
        name:         name.trim(),
        organisation: organisation.trim(),
        role:         role.trim(),
        email:        email.trim().toLowerCase(),
        useCase:      useCase?.trim() || null,
        status:       'pending',
      },
    });

    // Fire-and-forget — email failure must not block the HTTP response
    sendAccessRequestNotification(record).catch(err =>
      console.error(`[alaafia-access] notification email failed id=${record.id}:`, err.message)
    );

    return res.status(201).json({ success: true, id: record.id });
  } catch (err) { next(err); }
});

// GET /api/alaafia-access — ADMIN only, returns all requests ordered newest first
router.get('/', verifyToken, requireRole('ADMIN'), async (req, res, next) => {
  try {
    const requests = await prisma.alaafiaAccess.findMany({
      orderBy: { createdAt: 'desc' },
    });
    return res.json({ requests });
  } catch (err) { next(err); }
});

// PATCH /api/alaafia-access/:id — ADMIN only, updates status; generates key on approval
router.patch('/:id', verifyToken, requireRole('ADMIN'), async (req, res, next) => {
  try {
    const { id } = req.params;
    const { status } = req.body;

    if (!['approved', 'rejected', 'pending'].includes(status)) {
      return res.status(400).json({ error: 'status must be approved, rejected, or pending' });
    }

    const updateData = { status };

    if (status === 'approved') {
      // Only generate a new key if one doesn't already exist for this record
      const existing = await prisma.alaafiaAccess.findUnique({ where: { id } });
      if (!existing) return res.status(404).json({ error: 'Request not found' });

      if (!existing.apiKey) {
        updateData.apiKey     = crypto.randomBytes(32).toString('hex');
        updateData.approvedAt = new Date();
      }
    }

    const record = await prisma.alaafiaAccess.update({
      where: { id },
      data:  updateData,
    });

    if (status === 'approved' && updateData.apiKey) {
      sendAPIKeyEmail(record, record.apiKey).catch(err =>
        console.error(`[alaafia-access] API key email failed id=${record.id}:`, err.message)
      );
    }

    return res.json({ success: true, record });
  } catch (err) {
    if (err.code === 'P2025') {
      return res.status(404).json({ error: 'Request not found' });
    }
    next(err);
  }
});

module.exports = router;
