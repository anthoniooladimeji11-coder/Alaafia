import { useState, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || '';

// Auth is enforced server-side: /api/alaafia-access requires a valid ADMIN JWT
// (verifyToken + requireRole('ADMIN')). This page is gated on the ADMIN token
// the operator obtains by signing into the Ìyàwó app (same origin, so the token
// in localStorage is shared). No secret is embedded in this bundle.
function getAuth() {
  const token = localStorage.getItem('iyawo_token') || '';
  let role = null;
  try {
    role = JSON.parse(localStorage.getItem('iyawo_user') || 'null')?.role ?? null;
  } catch {
    role = null;
  }
  return { token, role };
}

const STATUS_COLORS = {
  pending:  { bg: '#fef9c3', text: '#854d0e' },
  approved: { bg: '#dcfce7', text: '#166534' },
  rejected: { bg: '#fee2e2', text: '#991b1b' },
};

function StatusBadge({ status }) {
  const c = STATUS_COLORS[status] || { bg: '#f1f5f9', text: '#475569' };
  return (
    <span style={{
      background: c.bg, color: c.text,
      padding: '2px 10px', borderRadius: 12,
      fontSize: 12, fontWeight: 600, textTransform: 'capitalize',
    }}>
      {status}
    </span>
  );
}

export default function AlaafiaAdminPage() {
  const [{ token, role }] = useState(getAuth);
  const isAdmin = !!token && role === 'ADMIN';

  const [requests, setRequests] = useState([]);
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState('');
  const [busy,     setBusy]     = useState({});   // { [id]: true } while a request is in-flight

  async function fetchRequests() {
    setLoading(true);
    setError('');
    try {
      // ADMIN-JWT protected server-side. The token comes from the operator's
      // Ìyàwó admin session (localStorage, same origin). A non-ADMIN or missing
      // token is rejected by the backend with 401/403.
      const res = await fetch(`${API_BASE}/api/alaafia-access`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.error || `HTTP ${res.status}`);
      }
      const data = await res.json();
      setRequests(data.requests || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (isAdmin) fetchRequests();
  }, [isAdmin]);

  async function updateStatus(id, status) {
    setBusy(b => ({ ...b, [id]: true }));
    setError('');
    try {
      const res = await fetch(`${API_BASE}/api/alaafia-access/${id}`, {
        method:  'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ status }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.error || `HTTP ${res.status}`);
      }
      const data = await res.json();
      setRequests(prev => prev.map(r => r.id === id ? data.record : r));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(b => ({ ...b, [id]: false }));
    }
  }

  if (!isAdmin) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f8fafc' }}>
        <div style={{
          background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12,
          padding: '40px 48px', maxWidth: 420, width: '100%', boxShadow: '0 4px 24px rgba(0,0,0,0.07)',
        }}>
          <h2 style={{ margin: '0 0 8px', fontSize: 22, fontWeight: 700, color: '#1d4ed8' }}>Àlááfíà Admin</h2>
          <p style={{ margin: '0 0 8px', color: '#64748b', fontSize: 14, lineHeight: 1.6 }}>
            Administrator sign-in required. Sign in to Ìyàwó with an ADMIN account, then reopen this page.
          </p>
          <p style={{ margin: 0, color: '#94a3b8', fontSize: 13, lineHeight: 1.6 }}>
            Access to research access-requests is restricted to administrators and is enforced on the server.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', padding: '48px 24px', fontFamily: 'sans-serif' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 32 }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 26, fontWeight: 800, color: '#1e293b' }}>Àlááfíà Access Requests</h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: 14 }}>
            {requests.length} total — {requests.filter(r => r.status === 'pending').length} pending
          </p>
        </div>
        <button onClick={fetchRequests} disabled={loading} style={{
          background: loading ? '#e2e8f0' : '#1d4ed8', color: loading ? '#94a3b8' : '#fff',
          border: 'none', borderRadius: 8, padding: '9px 20px', fontSize: 14, fontWeight: 600, cursor: loading ? 'default' : 'pointer',
        }}>
          {loading ? 'Loading…' : 'Refresh'}
        </button>
      </div>

      {error && (
        <div style={{ background: '#fee2e2', border: '1px solid #fca5a5', borderRadius: 8, padding: '12px 16px', marginBottom: 24, color: '#991b1b', fontSize: 14 }}>
          {error}
        </div>
      )}

      {loading && !requests.length ? (
        <p style={{ color: '#64748b', textAlign: 'center', padding: 60 }}>Loading requests…</p>
      ) : requests.length === 0 ? (
        <p style={{ color: '#64748b', textAlign: 'center', padding: 60 }}>No access requests yet.</p>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
            <thead>
              <tr style={{ background: '#f1f5f9', color: '#475569' }}>
                {['Name', 'Organisation', 'Role', 'Email', 'Status', 'Submitted', 'Actions'].map(h => (
                  <th key={h} style={{ padding: '10px 14px', textAlign: 'left', fontWeight: 600, whiteSpace: 'nowrap' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {requests.map((r, i) => (
                <tr key={r.id} style={{ background: i % 2 === 0 ? '#fff' : '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                  <td style={{ padding: '12px 14px', fontWeight: 600 }}>{r.name}</td>
                  <td style={{ padding: '12px 14px' }}>{r.organisation}</td>
                  <td style={{ padding: '12px 14px', color: '#64748b' }}>{r.role}</td>
                  <td style={{ padding: '12px 14px' }}>
                    <a href={`mailto:${r.email}`} style={{ color: '#1d4ed8', textDecoration: 'none' }}>{r.email}</a>
                  </td>
                  <td style={{ padding: '12px 14px' }}><StatusBadge status={r.status} /></td>
                  <td style={{ padding: '12px 14px', color: '#64748b', whiteSpace: 'nowrap' }}>
                    {new Date(r.createdAt).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}
                  </td>
                  <td style={{ padding: '12px 14px', whiteSpace: 'nowrap' }}>
                    {r.status === 'pending' && (
                      <>
                        <button
                          onClick={() => updateStatus(r.id, 'approved')}
                          disabled={!!busy[r.id]}
                          style={{
                            background: busy[r.id] ? '#e2e8f0' : '#16a34a', color: busy[r.id] ? '#94a3b8' : '#fff',
                            border: 'none', borderRadius: 6, padding: '6px 14px', fontSize: 13,
                            fontWeight: 600, cursor: busy[r.id] ? 'default' : 'pointer', marginRight: 8,
                          }}
                        >
                          {busy[r.id] ? '…' : 'Approve'}
                        </button>
                        <button
                          onClick={() => updateStatus(r.id, 'rejected')}
                          disabled={!!busy[r.id]}
                          style={{
                            background: busy[r.id] ? '#e2e8f0' : '#dc2626', color: busy[r.id] ? '#94a3b8' : '#fff',
                            border: 'none', borderRadius: 6, padding: '6px 14px', fontSize: 13,
                            fontWeight: 600, cursor: busy[r.id] ? 'default' : 'pointer',
                          }}
                        >
                          {busy[r.id] ? '…' : 'Reject'}
                        </button>
                      </>
                    )}
                    {r.status === 'approved' && (
                      <span style={{ color: '#16a34a', fontSize: 13 }}>
                        ✓ Approved {r.approvedAt ? `· ${new Date(r.approvedAt).toLocaleDateString('en-GB')}` : ''}
                      </span>
                    )}
                    {r.status === 'rejected' && (
                      <button
                        onClick={() => updateStatus(r.id, 'pending')}
                        disabled={!!busy[r.id]}
                        style={{
                          background: 'transparent', color: '#64748b',
                          border: '1px solid #e2e8f0', borderRadius: 6, padding: '5px 12px',
                          fontSize: 12, cursor: busy[r.id] ? 'default' : 'pointer',
                        }}
                      >
                        Reopen
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {requests.some(r => r.useCase) && (
            <details style={{ marginTop: 32 }}>
              <summary style={{ cursor: 'pointer', fontWeight: 600, color: '#475569', fontSize: 14 }}>
                Use case details
              </summary>
              <div style={{ marginTop: 16, display: 'grid', gap: 12 }}>
                {requests.filter(r => r.useCase).map(r => (
                  <div key={r.id} style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 8, padding: 16 }}>
                    <p style={{ margin: '0 0 4px', fontWeight: 600, color: '#1e293b' }}>{r.name} — {r.organisation}</p>
                    <p style={{ margin: 0, color: '#475569', fontSize: 13 }}>{r.useCase}</p>
                  </div>
                ))}
              </div>
            </details>
          )}
        </div>
      )}
    </div>
  );
}
