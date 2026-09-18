import { useState } from 'react';

// Holding page. The previous 1,871-line AlaafiaPage was a UI built entirely on
// the precomputed demo datasets, which were removed 2026-09-06 for systematic
// geographic misattribution (see REBUILD_ASSESSMENT_2026-09-06.md). Archived at
// _archive_demo_2026-09-06/frontend/AlaafiaPage.jsx.
//
// This page makes no data claims. It exists so the site builds and the
// access-request path stays reachable while the intelligence layer is rebuilt.

const API_BASE = import.meta.env.VITE_API_URL || '';

export default function AlaafiaPage() {
  const [form, setForm] = useState({ name: '', organisation: '', role: '', email: '', useCase: '' });
  const [state, setState] = useState('idle'); // idle | sending | sent | error

  const submit = async (e) => {
    e.preventDefault();
    setState('sending');
    try {
      const res = await fetch(`${API_BASE}/api/alaafia-access`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      setState(res.ok ? 'sent' : 'error');
    } catch {
      setState('error');
    }
  };

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  return (
    <div style={{
      minHeight: '100vh', background: '#0b0b0f', color: '#e8e8ea',
      fontFamily: 'Inter, system-ui, sans-serif',
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24,
    }}>
      <div style={{ maxWidth: 560, width: '100%' }}>
        <p style={{ letterSpacing: '0.18em', fontSize: 12, color: '#8a8a93', margin: 0 }}>
          POPULATION-HEALTH INTELLIGENCE
        </p>
        <h1 style={{ fontSize: 'clamp(40px, 9vw, 72px)', fontWeight: 800, margin: '8px 0 16px' }}>
          Àlááfìà
        </h1>
        <p style={{ fontSize: 17, lineHeight: 1.6, color: '#c4c4cc', marginTop: 0 }}>
          Àlááfìà is being rebuilt. The earlier public preview presented model
          output from a small sample as finished findings; it has been taken down
          while the data and methodology are reworked.
        </p>
        <p style={{ fontSize: 15, lineHeight: 1.6, color: '#9a9aa3' }}>
          If you're a researcher, funder, or government partner who wants to be
          contacted when the API opens, leave your details below.
        </p>

        {state === 'sent' ? (
          <p style={{ color: '#7ee0b8', fontSize: 15, marginTop: 24 }}>
            Thanks — we have your request and will be in touch.
          </p>
        ) : (
          <form onSubmit={submit} style={{ display: 'grid', gap: 10, marginTop: 24 }}>
            {[
              ['name', 'Name', 'text'],
              ['organisation', 'Organisation', 'text'],
              ['role', 'Role', 'text'],
              ['email', 'Email', 'email'],
            ].map(([k, label, type]) => (
              <input
                key={k} type={type} required placeholder={label}
                value={form[k]} onChange={set(k)}
                style={inputStyle}
              />
            ))}
            <textarea
              placeholder="What would you use it for? (optional)"
              value={form.useCase} onChange={set('useCase')} rows={3}
              style={{ ...inputStyle, resize: 'vertical' }}
            />
            <button type="submit" disabled={state === 'sending'} style={buttonStyle}>
              {state === 'sending' ? 'Sending…' : 'Request access'}
            </button>
            {state === 'error' && (
              <p style={{ color: '#e88', fontSize: 13, margin: 0 }}>
                Something went wrong. Try again, or email anthoniooladimeji11@gmail.com.
              </p>
            )}
          </form>
        )}
      </div>
    </div>
  );
}

const inputStyle = {
  background: '#15151b', border: '1px solid #2a2a33', borderRadius: 8,
  padding: '12px 14px', color: '#e8e8ea', fontSize: 15, fontFamily: 'inherit',
  width: '100%',
};

const buttonStyle = {
  background: '#e8e8ea', color: '#0b0b0f', border: 'none', borderRadius: 8,
  padding: '12px 18px', fontSize: 15, fontWeight: 600, cursor: 'pointer',
  marginTop: 4,
};
