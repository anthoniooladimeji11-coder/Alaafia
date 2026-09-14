'use strict';

const { Resend } = require('resend');

// Lazy-init: key is not available at dev boot until the user adds it to .env
function getResend() {
  if (!process.env.RESEND_API_KEY) {
    throw new Error('RESEND_API_KEY is not set — add it to backend/.env');
  }
  return new Resend(process.env.RESEND_API_KEY);
}

const ADMIN_EMAIL = process.env.ALAAFIA_ADMIN_EMAIL || 'anthoniooladimeji11@gmail.com';
const FROM_EMAIL  = process.env.ALAAFIA_FROM_EMAIL  || 'onboarding@resend.dev';
const ADMIN_URL   = process.env.ALAAFIA_ADMIN_URL   || 'https://iyawo.org/alaafia-admin';
const DOCS_URL    = process.env.ALAAFIA_DOCS_URL    || 'https://iyawo.org/alaafia';
const API_URL     = process.env.ALAAFIA_API_URL     || 'https://api.iyawo.org';

async function sendAccessRequestNotification(request) {
  const resend = getResend();
  const { name, organisation, role, email, useCase, createdAt, id } = request;
  const timestamp = new Date(createdAt).toLocaleString('en-GB', { timeZone: 'Africa/Lagos' });

  await resend.emails.send({
    from:    FROM_EMAIL,
    to:      ADMIN_EMAIL,
    subject: `New Àlááfíà Access Request — ${name} from ${organisation}`,
    html: `
<div style="font-family:sans-serif;max-width:600px;margin:0 auto;color:#1a1a1a;">
  <h2 style="color:#1d4ed8;">New Àlááfíà API Access Request</h2>
  <table style="width:100%;border-collapse:collapse;">
    <tr><td style="padding:8px 0;font-weight:600;width:140px;">Name</td><td style="padding:8px 0;">${name}</td></tr>
    <tr><td style="padding:8px 0;font-weight:600;">Organisation</td><td style="padding:8px 0;">${organisation}</td></tr>
    <tr><td style="padding:8px 0;font-weight:600;">Role</td><td style="padding:8px 0;">${role}</td></tr>
    <tr><td style="padding:8px 0;font-weight:600;">Email</td><td style="padding:8px 0;">${email}</td></tr>
    <tr><td style="padding:8px 0;font-weight:600;">Use Case</td><td style="padding:8px 0;">${useCase || '(not provided)'}</td></tr>
    <tr><td style="padding:8px 0;font-weight:600;">Submitted</td><td style="padding:8px 0;">${timestamp} (WAT)</td></tr>
    <tr><td style="padding:8px 0;font-weight:600;">Request ID</td><td style="padding:8px 0;font-family:monospace;font-size:12px;">${id}</td></tr>
  </table>
  <div style="margin-top:24px;">
    <a href="${ADMIN_URL}"
       style="background:#1d4ed8;color:#fff;padding:12px 24px;text-decoration:none;border-radius:6px;font-weight:600;">
      Review &amp; Approve
    </a>
  </div>
  <p style="margin-top:24px;font-size:12px;color:#6b7280;">
    This email was sent automatically by the Àlááfíà platform.
  </p>
</div>`,
  });
}

async function sendAPIKeyEmail(request, apiKey) {
  const resend = getResend();
  const { name, email, organisation } = request;
  const curlExample = `curl -X POST ${API_URL}/api/alaafia/analyse \\
  -H "Authorization: Bearer ${apiKey}" \\
  -H "Content-Type: application/json" \\
  -d '{
    "geography_type": "state",
    "geography_value": "Lagos",
    "outcome": "stunting"
  }'`;

  await resend.emails.send({
    from:    FROM_EMAIL,
    to:      email,
    subject: 'Your Àlááfíà API Access — Welcome',
    html: `
<div style="font-family:sans-serif;max-width:620px;margin:0 auto;color:#1a1a1a;">
  <h2 style="color:#1d4ed8;">Welcome to the Àlááfíà API, ${name}</h2>
  <p>Your access request from <strong>${organisation}</strong> has been approved.
     Below is your API key — keep it private and do not share it publicly.</p>

  <h3 style="margin-top:28px;">Your API Key</h3>
  <div style="background:#f1f5f9;border:1px solid #e2e8f0;border-radius:6px;padding:16px;font-family:monospace;font-size:14px;word-break:break-all;">
    ${apiKey}
  </div>

  <h3 style="margin-top:28px;">Example Request</h3>
  <pre style="background:#0f172a;color:#e2e8f0;padding:16px;border-radius:6px;font-size:12px;overflow-x:auto;white-space:pre-wrap;">${curlExample}</pre>

  <h3 style="margin-top:28px;">Documentation</h3>
  <p>Full API documentation, available outcomes, and geographic parameters are at:</p>
  <a href="${DOCS_URL}" style="color:#1d4ed8;">${DOCS_URL.replace(/^https?:\/\//, '')}</a>

  <p style="margin-top:32px;font-size:13px;color:#6b7280;">
    If you have questions, reply to this email or contact us at
    <a href="mailto:${ADMIN_EMAIL}" style="color:#1d4ed8;">${ADMIN_EMAIL}</a>.
  </p>
  <p style="font-size:12px;color:#9ca3af;">Àlááfíà · Population-health intelligence for Nigerian primary care</p>
</div>`,
  });
}

async function sendAPIKeyRotationEmail(request, newApiKey) {
  const resend = getResend();
  const { name, email, organisation } = request;
  const curlExample = `curl -X POST ${API_URL}/api/alaafia/analyse \\
  -H "Authorization: Bearer ${newApiKey}" \\
  -H "Content-Type: application/json" \\
  -d '{
    "geography_type": "state",
    "geography_value": "Lagos",
    "outcome": "stunting"
  }'`;

  await resend.emails.send({
    from:    FROM_EMAIL,
    to:      email,
    subject: 'Action required: your Àlááfíà API key has been rotated',
    html: `
<div style="font-family:sans-serif;max-width:620px;margin:0 auto;color:#1a1a1a;">
  <h2 style="color:#1d4ed8;">Your Àlááfíà API key has changed, ${name}</h2>
  <p>As a security precaution, we rotated every issued Àlááfíà API key for
     <strong>${organisation}</strong>. Your previous key has been deactivated
     and will no longer work — please switch to the new key below.</p>

  <h3 style="margin-top:28px;">Your New API Key</h3>
  <div style="background:#f1f5f9;border:1px solid #e2e8f0;border-radius:6px;padding:16px;font-family:monospace;font-size:14px;word-break:break-all;">
    ${newApiKey}
  </div>

  <h3 style="margin-top:28px;">Example Request</h3>
  <pre style="background:#0f172a;color:#e2e8f0;padding:16px;border-radius:6px;font-size:12px;overflow-x:auto;white-space:pre-wrap;">${curlExample}</pre>

  <p style="margin-top:28px;font-size:13px;color:#6b7280;">
    If you have questions, reply to this email or contact us at
    <a href="mailto:${ADMIN_EMAIL}" style="color:#1d4ed8;">${ADMIN_EMAIL}</a>.
  </p>
  <p style="font-size:12px;color:#9ca3af;">Àlááfíà · Population-health intelligence for Nigerian primary care</p>
</div>`,
  });
}

module.exports = { sendAccessRequestNotification, sendAPIKeyEmail, sendAPIKeyRotationEmail };
