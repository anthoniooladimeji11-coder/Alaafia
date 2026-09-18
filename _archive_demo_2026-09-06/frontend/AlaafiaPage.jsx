import { useState, useEffect, useRef } from 'react';

/* ----------------------------------------------------------------
   UTILITIES
---------------------------------------------------------------- */
const fadeUp = (visible, delay = 0) => ({
  opacity:    visible ? 1 : 0,
  transform:  visible ? 'translateY(0)' : 'translateY(32px)',
  transition: `opacity 0.75s ease ${delay}s, transform 0.75s ease ${delay}s`,
});

function useInView(threshold = 0.12) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setVisible(true); }, { threshold });
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);
  return [ref, visible];
}

/* ----------------------------------------------------------------
   DATA  (unchanged)
---------------------------------------------------------------- */
const ZONES = {
  NC: { name: 'North Central', stunting: 52.1, anaemia: 40.1, wasting: 33.0, sanitation: 24.8, water: 33.6, color: '#DC2626', x: 310, y: 280 },
  NE: { name: 'North East',    stunting: 52.1, anaemia: 41.9, wasting: 34.8, sanitation: 36.6, water: 34.6, color: '#EA580C', x: 430, y: 200 },
  NW: { name: 'North West',    stunting: 35.5, anaemia: 36.0, wasting: 20.8, sanitation:  3.4, water: 29.5, color: '#F59E0B', x: 190, y: 190 },
  SE: { name: 'South East',    stunting: 19.3, anaemia: 55.4, wasting: 15.3, sanitation:  2.7, water: 14.5, color: '#7C3AED', x: 390, y: 380 },
  SS: { name: 'South South',   stunting: 20.0, anaemia: 46.9, wasting: 18.1, sanitation:  5.9, water: 16.8, color: '#2563EB', x: 310, y: 420 },
  SW: { name: 'South West',    stunting: 21.2, anaemia: 41.1, wasting: 21.8, sanitation:  1.2, water:  5.4, color: '#0F6E56', x: 200, y: 370 },
};

const OUTCOMES = [
  { id: 'stunting', label: 'Child Stunting', unit: '%' },
  { id: 'anaemia',  label: 'Maternal Anaemia', unit: '%' },
  { id: 'wasting',  label: 'Child Wasting', unit: '%' },
];

const PRECOMPUTED = {
  NC: {
    stunting: {
      pathway: 'Poor sanitation → environmental enteropathy → nutrient malabsorption → stunting',
      policy: 'Prioritise pit latrine construction and open defecation elimination in North Central LGAs',
      equity: 'NC stunting driven by differential sanitation exposure, not solid fuel — same exposure produces worse stunting than SW due to lower baseline maternal nutrition',
      confidence: 0.82,
    },
    anaemia: {
      pathway: 'High parity → maternal nutritional depletion → iron deficiency → anaemia',
      policy: 'Integrate periconceptional iron supplementation with family planning services in NC facilities',
      equity: 'NC anaemia lower than SE despite worse WASH — parity and ANC attendance are primary drivers here',
      confidence: 0.74,
    },
    wasting: {
      pathway: 'Unimproved water → diarrhoeal disease → acute nutrient loss → wasting',
      policy: 'Emergency borehole and water treatment programme targeting 33.6% unimproved water clusters',
      equity: 'NC wasting 33% — second highest nationally — driven by acute water contamination pathway distinct from chronic stunting',
      confidence: 0.79,
    },
  },
  NE: {
    stunting: {
      pathway: 'Poor sanitation (36.6%) → environmental enteropathy → chronic nutrient malabsorption → stunting',
      policy: 'Northeast requires largest sanitation investment nationally — 36.6% poor sanitation drives 52.1% stunting',
      equity: 'NE has worst sanitation of all zones — explains why stunting equals NC despite similar wealth. Not a poverty story.',
      confidence: 0.85,
    },
    anaemia: {
      pathway: 'No ANC + high malaria burden → undetected iron deficiency + haemolysis → anaemia',
      policy: 'Mobile ANC outreach to security-compromised LGAs combined with ITN distribution',
      equity: 'NE anaemia (41.9%) reflects healthcare access collapse, not dietary factors alone',
      confidence: 0.71,
    },
    wasting: {
      pathway: 'Unimproved water (34.6%) → diarrhoea → acute wasting → exacerbated by conflict-related food insecurity',
      policy: 'Emergency water trucking and therapeutic feeding centre expansion in displacement camps',
      equity: 'NE wasting highest in Nigeria at 34.8% — conflict multiplies the water-wasting pathway',
      confidence: 0.88,
    },
  },
  NW: {
    stunting: {
      pathway: 'Unimproved water → waterborne infection → stunting — partially mitigated by better sanitation (3.4%)',
      policy: 'Water quality improvement would close remaining stunting gap — sanitation already relatively strong',
      equity: 'NW stunting (35.5%) lower than NC/NE despite similar poverty — better sanitation explains the gap',
      confidence: 0.80,
    },
    anaemia: {
      pathway: 'Low dietary iron diversity + high parity → maternal iron depletion → anaemia',
      policy: 'NW improved most 2018-2024 (23pp reduction) — replicate successful LGA-level interventions',
      equity: 'NW anaemia improved most dramatically 2018-2024 — identifying what worked here is the research priority',
      confidence: 0.76,
    },
    wasting: {
      pathway: 'Moderate malaria burden + suboptimal ANC → maternal anaemia → low birthweight → wasting',
      policy: 'ITN coverage expansion and ANC attendance incentive programme',
      equity: 'NW wasting (20.8%) lower than NC/NE — sanitation advantage partially protects children',
      confidence: 0.72,
    },
  },
  SE: {
    stunting: {
      pathway: 'Dietary diversity deficit → micronutrient deficiency → stunting — not sanitation driven',
      policy: 'Dietary diversification programme and school feeding — sanitation already strong (2.7%)',
      equity: 'SE stunting lowest (19.3%) despite highest anaemia (55.4%) — two separate causal structures operating simultaneously',
      confidence: 0.78,
    },
    anaemia: {
      pathway: 'Structural food environment → low dietary iron → iron deficiency anaemia — persists across wealth quintiles',
      policy: 'SE anaemia requires food environment intervention, not poverty targeting — richest women still 48.7% anaemic',
      equity: 'SE anaemia is NOT a poverty problem — richest SE women (48.7%) are more anaemic than poorest SW women (34.4%)',
      confidence: 0.83,
    },
    wasting: {
      pathway: 'Moderate malaria exposure → episodic haemolysis → acute nutritional depletion → wasting',
      policy: 'Malaria prevention and early treatment — WASH infrastructure already strong',
      equity: 'SE wasting (15.3%) lowest — WASH advantage clear. Remaining burden is malaria-driven.',
      confidence: 0.75,
    },
  },
  SS: {
    stunting: {
      pathway: 'Oil pollution → food insecurity + dietary contamination → stunting — unique pathway not captured by standard WASH indicators',
      policy: 'Environmental remediation and alternative livelihood support in Delta communities',
      equity: 'SS stunting (20%) similar to SE despite worse sanitation — oil pollution pathway partially explains divergence',
      confidence: 0.68,
    },
    anaemia: {
      pathway: 'High parity + environmental contaminant exposure → compounded nutritional depletion → anaemia',
      policy: 'Reproductive health integration with environmental health screening in SS facilities',
      equity: 'SS anaemia (46.9%) second highest — parity and environmental exposure interact uniquely here',
      confidence: 0.70,
    },
    wasting: {
      pathway: 'Unimproved water (16.8%) → diarrhoea → wasting — amplified by fish-dependent diets during contamination events',
      policy: 'Water treatment investment and emergency dietary support during pollution events',
      equity: 'SS wasting (18.1%) moderate — water pathway dominant but pollution amplifies seasonally',
      confidence: 0.73,
    },
  },
  SW: {
    stunting: {
      pathway: 'Dietary diversity access → adequate micronutrient intake → protected growth — best WASH in Nigeria (1.2% poor sanitation)',
      policy: 'SW is the benchmark — document what works here and replicate in Northern zones',
      equity: 'SW stunting lowest (21.2%) — WASH and education advantages combine. Model zone for intervention design.',
      confidence: 0.85,
    },
    anaemia: {
      pathway: 'Urban food environment → dietary iron access → anaemia — despite best WASH, urban dietary patterns create gaps',
      policy: 'Urban dietary iron fortification and nutrition labelling programme for Lagos, Ibadan, Abeokuta',
      equity: 'SW anaemia (41.1%) moderate despite best structural conditions — urban dietary transition driving hidden burden',
      confidence: 0.77,
    },
    wasting: {
      pathway: 'Residual malaria exposure + urban food insecurity → episodic wasting — largely controlled compared to North',
      policy: 'Urban malaria control and social protection for food-insecure urban households',
      equity: 'SW wasting (21.8%) unexpectedly higher than SE — urban poverty creates hidden acute malnutrition burden',
      confidence: 0.74,
    },
  },
};

const STATE_CODE_MAP = {
  'Sokoto':1,'Zamfara':2,'Katsina':3,'Jigawa':4,
  'Yobe':5,'Borno':6,'Adamawa':7,'Gombe':8,'Bauchi':9,
  'Kano':10,'Kaduna':11,'Kebbi':12,'Niger':13,'FCT Abuja':14,
  'Nasarawa':15,'Plateau':16,'Taraba':17,'Benue':18,
  'Kogi':19,'Kwara':20,'Oyo':21,'Osun':22,'Ekiti':23,
  'Ondo':24,'Edo':25,'Anambra':26,'Enugu':27,'Ebonyi':28,
  'Cross River':29,'Akwa Ibom':30,'Abia':31,'Imo':32,
  'Rivers':33,'Bayelsa':34,'Delta':35,'Lagos':36,'Ogun':37,
};

const STATE_ZONES = {
  NC: ['Niger','FCT Abuja','Nasarawa','Plateau','Benue','Kogi','Kwara'],
  NE: ['Yobe','Borno','Adamawa','Gombe','Bauchi','Taraba'],
  NW: ['Sokoto','Zamfara','Katsina','Jigawa','Kano','Kaduna','Kebbi'],
  SE: ['Anambra','Enugu','Ebonyi','Abia','Imo'],
  SS: ['Edo','Cross River','Akwa Ibom','Rivers','Bayelsa','Delta'],
  SW: ['Oyo','Osun','Ekiti','Ondo','Lagos','Ogun'],
};

/* ----------------------------------------------------------------
   REQUEST ACCESS MODAL
---------------------------------------------------------------- */
const API_BASE = import.meta.env.VITE_API_URL || '';

function RequestAccessModal({ open, onClose }) {
  const [form, setForm]           = useState({ name: '', org: '', role: '', email: '' });
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setSubmitError('');
    try {
      const res = await fetch(`${API_BASE}/api/alaafia-access`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({
          name:         form.name,
          organisation: form.org,
          role:         form.role,
          email:        form.email,
        }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || 'Submission failed. Please try again.');
      }
      setSubmitted(true);
    } catch (err) {
      setSubmitError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    onClose();
    setTimeout(() => {
      setSubmitted(false);
      setSubmitError('');
      setForm({ name: '', org: '', role: '', email: '' });
    }, 400);
  };

  const inputStyle = {
    width: '100%', boxSizing: 'border-box',
    background: '#F8F8F6', border: '1px solid rgba(0,0,0,0.1)',
    borderRadius: 10, padding: '13px 16px',
    fontSize: 15, color: '#111827', outline: 'none',
    fontFamily: 'Inter, system-ui',
    transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
  };

  return (
    <div
      onClick={handleClose}
      style={{
        position: 'fixed', inset: 0, zIndex: 9000,
        background: 'rgba(5,10,6,0.82)',
        backdropFilter: 'blur(24px)', WebkitBackdropFilter: 'blur(24px)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        padding: '20px',
        opacity: open ? 1 : 0,
        pointerEvents: open ? 'all' : 'none',
        transition: 'opacity 0.3s ease',
      }}
    >
      <div
        onClick={e => e.stopPropagation()}
        style={{
          background: 'white', borderRadius: 24,
          padding: 'clamp(28px,4vw,48px)',
          width: '100%', maxWidth: 480,
          boxShadow: '0 40px 100px rgba(0,0,0,0.5)',
          transform: open ? 'scale(1) translateY(0)' : 'scale(0.94) translateY(24px)',
          transition: 'transform 0.35s cubic-bezier(0.34,1.4,0.64,1)',
        }}
      >
        {submitted ? (
          <div style={{ textAlign: 'center', padding: '24px 0' }}>
            <div style={{
              width: 64, height: 64, borderRadius: '50%',
              background: 'rgba(15,110,86,0.1)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              margin: '0 auto 20px',
            }}>
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
                <path d="M5 12l5 5L20 7" stroke="#0F6E56" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <h3 style={{
              fontFamily: '"Bricolage Grotesque", system-ui', fontWeight: 800,
              fontSize: 24, color: '#111827', margin: '0 0 10px', letterSpacing: '-0.03em',
            }}>Request received.</h3>
            <p style={{ fontSize: 15, color: '#6B7280', lineHeight: 1.7, margin: '0 0 28px' }}>
              We'll review your request and follow up at the email provided. Thank you for your interest in Àlááfíà.
            </p>
            <button onClick={handleClose} style={{
              background: '#050A06', color: 'white', border: 'none',
              borderRadius: 100, padding: '12px 32px',
              fontSize: 15, fontWeight: 600, cursor: 'pointer',
              fontFamily: '"Bricolage Grotesque", system-ui',
              transition: 'opacity 0.2s ease',
            }}>Close</button>
          </div>
        ) : (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
              <div>
                <p style={{ fontSize: 11, fontWeight: 700, color: '#F59E0B', textTransform: 'uppercase',
                  letterSpacing: '0.15em', margin: '0 0 6px' }}>FREE FOR RESEARCHERS &amp; POLICYMAKERS</p>
                <h2 style={{ fontFamily: '"Bricolage Grotesque", system-ui', fontWeight: 800,
                  fontSize: 26, color: '#111827', margin: 0, letterSpacing: '-0.03em' }}>
                  Get Access to Àlááfíà
                </h2>
              </div>
              <button onClick={handleClose} style={{
                background: 'rgba(0,0,0,0.06)', border: 'none', borderRadius: '50%',
                width: 36, height: 36, cursor: 'pointer', display: 'flex',
                alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                transition: 'background 0.2s ease',
              }}
              onMouseEnter={e => e.currentTarget.style.background='rgba(0,0,0,0.12)'}
              onMouseLeave={e => e.currentTarget.style.background='rgba(0,0,0,0.06)'}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                  <path d="M18 6L6 18M6 6l12 12" stroke="#374151" strokeWidth="2.5" strokeLinecap="round"/>
                </svg>
              </button>
            </div>

            {/* What you get */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8, marginBottom: 20 }}>
              {[
                {
                  icon: (
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
                      <circle cx="12" cy="12" r="9" stroke="#0F6E56" strokeWidth="1.8"/>
                      <path d="M12 3c0 0-4 5-4 9s4 9 4 9" stroke="#0F6E56" strokeWidth="1.8" strokeLinecap="round"/>
                      <path d="M12 3c0 0 4 5 4 9s-4 9-4 9" stroke="#0F6E56" strokeWidth="1.8" strokeLinecap="round"/>
                      <path d="M3 12h18" stroke="#0F6E56" strokeWidth="1.8" strokeLinecap="round"/>
                    </svg>
                  ),
                  title: 'Zone explorer',
                  desc: 'Click any zone to see its causal health pathway.',
                },
                {
                  icon: (
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
                      <path d="M3 20h18M7 20V10M12 20V4M17 20V14" stroke="#0F6E56" strokeWidth="1.8" strokeLinecap="round"/>
                    </svg>
                  ),
                  title: 'Equity analysis',
                  desc: 'See why identical exposures drive different outcomes.',
                },
                {
                  icon: (
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
                      <path d="M8 6L2 12l6 6M16 6l6 6-6 6" stroke="#0F6E56" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  ),
                  title: 'API access',
                  desc: 'Integrate causal intelligence into your pipeline.',
                },
              ].map(({ icon, title, desc }) => (
                <div key={title} style={{
                  background: '#F8F8F6', border: '1px solid rgba(0,0,0,0.07)',
                  borderRadius: 10, padding: '12px 10px',
                }}>
                  <div style={{
                    width: 28, height: 28, borderRadius: 7,
                    background: 'rgba(15,110,86,0.08)', border: '1px solid rgba(15,110,86,0.14)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    marginBottom: 9, flexShrink: 0,
                  }}>{icon}</div>
                  <div style={{ fontSize: 12, fontWeight: 700, color: '#111827',
                    fontFamily: '"Bricolage Grotesque", system-ui',
                    letterSpacing: '-0.01em', marginBottom: 4, lineHeight: 1.25,
                    whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {title}
                  </div>
                  <div style={{ fontSize: 11, color: '#6B7280', lineHeight: 1.5,
                    fontFamily: 'Inter, system-ui' }}>
                    {desc}
                  </div>
                </div>
              ))}
            </div>

            <form onSubmit={handleSubmit}>
              <div style={{ display: 'grid', gap: 14 }}>
                <div>
                  <label style={{ display: 'block', fontSize: 11, fontWeight: 700, color: '#374151',
                    textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 6 }}>Name</label>
                  <input
                    required
                    placeholder="Full name"
                    value={form.name}
                    onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                    style={inputStyle}
                    onFocus={e => { e.target.style.borderColor='#0F6E56'; e.target.style.boxShadow='0 0 0 3px rgba(15,110,86,0.1)'; }}
                    onBlur={e => { e.target.style.borderColor='rgba(0,0,0,0.1)'; e.target.style.boxShadow='none'; }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: 11, fontWeight: 700, color: '#374151',
                    textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 6 }}>Organisation</label>
                  <input
                    required
                    placeholder="Institution or organisation"
                    value={form.org}
                    onChange={e => setForm(f => ({ ...f, org: e.target.value }))}
                    style={inputStyle}
                    onFocus={e => { e.target.style.borderColor='#0F6E56'; e.target.style.boxShadow='0 0 0 3px rgba(15,110,86,0.1)'; }}
                    onBlur={e => { e.target.style.borderColor='rgba(0,0,0,0.1)'; e.target.style.boxShadow='none'; }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: 11, fontWeight: 700, color: '#374151',
                    textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 6 }}>Role</label>
                  <select
                    required
                    value={form.role}
                    onChange={e => setForm(f => ({ ...f, role: e.target.value }))}
                    style={{ ...inputStyle, appearance: 'none', backgroundImage: 'url("data:image/svg+xml,%3Csvg width=\'12\' height=\'8\' viewBox=\'0 0 12 8\' fill=\'none\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cpath d=\'M1 1l5 5 5-5\' stroke=\'%236B7280\' stroke-width=\'1.5\' stroke-linecap=\'round\'/%3E%3C/svg%3E")', backgroundRepeat: 'no-repeat', backgroundPosition: 'right 16px center', color: form.role ? '#111827' : '#9CA3AF' }}
                    onFocus={e => { e.target.style.borderColor='#0F6E56'; e.target.style.boxShadow='0 0 0 3px rgba(15,110,86,0.1)'; }}
                    onBlur={e => { e.target.style.borderColor='rgba(0,0,0,0.1)'; e.target.style.boxShadow='none'; }}
                  >
                    <option value="" disabled>Select your role</option>
                    <option value="government">Government</option>
                    <option value="researcher">Researcher</option>
                    <option value="health-startup">Health Startup</option>
                    <option value="ngo">NGO</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: 11, fontWeight: 700, color: '#374151',
                    textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 6 }}>Email</label>
                  <input
                    required
                    type="email"
                    placeholder="you@organisation.org"
                    value={form.email}
                    onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
                    style={inputStyle}
                    onFocus={e => { e.target.style.borderColor='#0F6E56'; e.target.style.boxShadow='0 0 0 3px rgba(15,110,86,0.1)'; }}
                    onBlur={e => { e.target.style.borderColor='rgba(0,0,0,0.1)'; e.target.style.boxShadow='none'; }}
                  />
                </div>
              </div>

              {submitError && (
                <p style={{ marginTop: 16, marginBottom: 0, fontSize: 13,
                  color: '#DC2626', textAlign: 'center', fontFamily: 'Inter, system-ui' }}>
                  {submitError}
                </p>
              )}
              <button
                type="submit"
                disabled={submitting}
                style={{
                  width: '100%', marginTop: 24,
                  background: submitting ? '#D97706' : '#F59E0B',
                  color: '#111827', border: 'none', borderRadius: 12,
                  padding: '15px', fontSize: 15, fontWeight: 700,
                  cursor: submitting ? 'wait' : 'pointer',
                  fontFamily: '"Bricolage Grotesque", system-ui',
                  transition: 'background 0.2s ease, transform 0.15s ease',
                  letterSpacing: '-0.01em',
                }}
                onMouseEnter={e => { if (!submitting) e.currentTarget.style.transform='translateY(-1px)'; }}
                onMouseLeave={e => { e.currentTarget.style.transform='translateY(0)'; }}
              >
                {submitting ? 'Sending…' : 'Submit Request'}
              </button>
              <p style={{ textAlign: 'center', fontSize: 12, color: '#9CA3AF', marginTop: 12 }}>
                Your data will never be shared or sold.
              </p>
            </form>
          </>
        )}
      </div>
    </div>
  );
}

/* ----------------------------------------------------------------
   SECTION 1 — HERO  (cinematic, dark, full viewport)
---------------------------------------------------------------- */
function HeroSection({ onRequestAccess }) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => { const t = setTimeout(() => setMounted(true), 60); return () => clearTimeout(t); }, []);

  return (
    <section style={{
      position: 'relative', minHeight: '85vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      overflow: 'hidden', background: '#050A06',
    }}>
      <style>{`
        @keyframes al-orb-a {
          0%,100% { transform:translate(0,0) scale(1); }
          33%      { transform:translate(120px,-80px) scale(1.15); }
          66%      { transform:translate(-60px,60px) scale(0.9); }
        }
        @keyframes al-orb-b {
          0%,100% { transform:translate(0,0) scale(1); }
          33%      { transform:translate(-100px,70px) scale(1.1); }
          66%      { transform:translate(80px,-90px) scale(1.2); }
        }
        @keyframes al-orb-c {
          0%,100% { transform:translate(0,0); }
          50%      { transform:translate(40px,-120px); }
        }
        @keyframes al-particles {
          from { background-position: 0 0; }
          to   { background-position: 80px 80px; }
        }
        @keyframes al-fade-title {
          from { opacity:0; transform:translateY(40px) skewY(1.5deg); }
          to   { opacity:1; transform:translateY(0) skewY(0deg); }
        }
        @keyframes al-fade-sub {
          from { opacity:0; transform:translateY(20px); }
          to   { opacity:1; transform:translateY(0); }
        }
        @keyframes al-chevron {
          0%,100% { transform:translateX(-50%) translateY(0); }
          50%      { transform:translateX(-50%) translateY(9px); }
        }
        .al-hero-title {
          font-family: "Bricolage Grotesque", system-ui;
          font-weight: 800;
          font-size: clamp(80px,12vw,160px);
          line-height: 0.9;
          letter-spacing: 0.07em;
          color: white;
          margin: 0;
          opacity: 0;
          animation: al-fade-title 1s cubic-bezier(0.22,1,0.36,1) 0.15s forwards;
        }
        .al-hero-sub {
          opacity: 0;
          animation: al-fade-sub 0.9s ease 0.55s forwards;
        }
        .al-hero-stats {
          opacity: 0;
          animation: al-fade-sub 0.9s ease 0.75s forwards;
        }
        .al-hero-btns {
          opacity: 0;
          animation: al-fade-sub 0.9s ease 0.95s forwards;
        }
        .al-btn-primary {
          background: #F59E0B; color: #050A06; border: none;
          border-radius: 100px; padding: 0 36px; height: 54px;
          font-size: 15px; font-weight: 700; cursor: pointer;
          font-family: "Bricolage Grotesque", system-ui;
          letter-spacing: -0.01em;
          box-shadow: 0 0 0 0 rgba(245,158,11,0);
          transition: transform 0.25s ease, box-shadow 0.25s ease;
          white-space: nowrap;
        }
        .al-btn-primary:hover {
          transform: translateY(-3px);
          box-shadow: 0 12px 40px rgba(245,158,11,0.45);
        }
        .al-btn-primary:active { transform: scale(0.97); }
        .al-btn-ghost {
          background: transparent; border: 1px solid rgba(255,255,255,0.18);
          color: rgba(255,255,255,0.75); border-radius: 100px;
          padding: 0 28px; height: 54px;
          font-size: 15px; font-weight: 500; cursor: pointer;
          font-family: "Bricolage Grotesque", system-ui;
          display: inline-flex; align-items: center; gap: 8px;
          text-decoration: none;
          transition: border-color 0.25s ease, color 0.25s ease, transform 0.25s ease;
          white-space: nowrap;
        }
        .al-btn-ghost:hover {
          border-color: rgba(255,255,255,0.5);
          color: white;
          transform: translateY(-2px);
        }
      `}</style>

      {/* Gradient orbs */}
      <div style={{ position:'absolute', inset:0, pointerEvents:'none', overflow:'hidden' }}>
        {/* Amber orb */}
        <div style={{
          position:'absolute', top:'15%', right:'18%',
          width:600, height:600, borderRadius:'50%',
          background:'radial-gradient(circle, rgba(245,158,11,0.14) 0%, transparent 70%)',
          animation:'al-orb-a 18s ease-in-out infinite',
        }} />
        {/* Green orb */}
        <div style={{
          position:'absolute', bottom:'10%', left:'10%',
          width:800, height:800, borderRadius:'50%',
          background:'radial-gradient(circle, rgba(15,110,86,0.12) 0%, transparent 65%)',
          animation:'al-orb-b 22s ease-in-out infinite',
        }} />
        {/* Small accent orb */}
        <div style={{
          position:'absolute', top:'40%', left:'40%',
          width:300, height:300, borderRadius:'50%',
          background:'radial-gradient(circle, rgba(124,58,237,0.08) 0%, transparent 70%)',
          animation:'al-orb-c 14s ease-in-out infinite',
        }} />
        {/* Particle dot grid */}
        <div style={{
          position:'absolute', inset:0,
          backgroundImage:'radial-gradient(circle, rgba(255,255,255,0.12) 1px, transparent 1px)',
          backgroundSize:'40px 40px',
          animation:'al-particles 12s linear infinite',
          opacity:0.4,
        }} />
        {/* Vignette */}
        <div style={{
          position:'absolute', inset:0,
          background:'radial-gradient(ellipse at 50% 50%, transparent 40%, rgba(5,10,6,0.7) 100%)',
        }} />
      </div>

      {/* Content */}
      <div style={{
        position:'relative', zIndex:1, width:'100%',
        maxWidth:1200, margin:'0 auto',
        padding:'clamp(64px,6vw,88px) clamp(24px,5vw,64px) clamp(36px,3.5vw,52px)',
        textAlign:'center',
      }}>
        {/* Kicker */}
        <p className="al-hero-sub" style={{
          fontSize: 11, fontWeight: 700, color: '#F59E0B',
          textTransform: 'uppercase', letterSpacing: '0.18em',
          margin: '0 0 16px',
          fontFamily: 'Inter, system-ui',
        }}>
          Powered by N-ATLAS &nbsp;·&nbsp; Nigeria&rsquo;s National AI
        </p>

        {/* Big headline */}
        <h1 className="al-hero-title">Àlááfíà</h1>

        {/* Subtitle */}
        <p className="al-hero-sub" style={{
          fontSize: 'clamp(16px,1.8vw,20px)', fontWeight: 400,
          color: 'rgba(255,255,255,0.52)', lineHeight: 1.7,
          maxWidth: 560, margin: '14px auto 0',
          fontFamily: 'Inter, system-ui',
        }}>
          Nigeria&rsquo;s first causal population health intelligence platform.
        </p>

        {/* Stats */}
        <div className="al-hero-stats" style={{
          display: 'flex', justifyContent: 'center', gap: 'clamp(24px,4vw,48px)',
          marginTop: 32, flexWrap: 'wrap',
        }}>
          {[
            { n: '39,050', label: 'NDHS 2024 women' },
            { n: '31,103', label: 'MICS 2021 children' },
            { n: '6',      label: 'Geopolitical zones' },
          ].map(({ n, label }) => (
            <div key={label} style={{ textAlign: 'center' }}>
              <div style={{
                fontFamily: '"Bricolage Grotesque", system-ui', fontWeight: 800,
                fontSize: 'clamp(32px,4vw,52px)', color: '#F59E0B',
                lineHeight: 1, letterSpacing: '-0.04em',
              }}>{n}</div>
              <div style={{
                fontSize: 11, fontWeight: 600, color: 'rgba(255,255,255,0.35)',
                textTransform: 'uppercase', letterSpacing: '0.12em', marginTop: 8,
                fontFamily: 'Inter, system-ui',
              }}>{label}</div>
            </div>
          ))}
        </div>

        {/* Buttons */}
        <div className="al-hero-btns" style={{
          display: 'flex', justifyContent: 'center', gap: 14,
          marginTop: 28, flexWrap: 'wrap',
        }}>
          <button className="al-btn-primary" onClick={onRequestAccess}>
            Request Access
          </button>
          <a
            href="https://github.com/anthoniooladimeji11-coder/Alaafia"
            target="_blank" rel="noopener noreferrer"
            className="al-btn-ghost"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
            </svg>
            View on GitHub
          </a>
        </div>
      </div>

      {/* Scroll chevron */}
      <div style={{
        position:'absolute', bottom:36, left:'50%',
        animation:'al-chevron 2.4s ease-in-out infinite',
        opacity:0.3,
      }}>
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
          <path d="M6 9l6 6 6-6" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </div>
    </section>
  );
}

/* ----------------------------------------------------------------
   SECTION 2 — INTERACTIVE NIGERIA MAP  (premium dark dashboard)
---------------------------------------------------------------- */
function NigeriaZonePath({ zone, data, isSelected, isHovered, onSelect, onHover, outcome, liveValue }) {
  const value    = liveValue ?? data[outcome];
  const maxVal   = outcome === 'anaemia' ? 60 : outcome === 'stunting' ? 55 : 38;
  const intensity = Math.min(value / maxVal, 1);

  const baseColor  = isSelected ? data.color : `rgba(15,110,86,${0.15 + intensity * 0.55})`;
  const stroke     = isSelected ? data.color : isHovered ? 'rgba(255,255,255,0.45)' : 'rgba(255,255,255,0.1)';
  const r          = isSelected ? 44 : isHovered ? 39 : 33;

  return (
    <g
      style={{
        cursor: 'pointer',
        filter: isSelected
          ? `drop-shadow(0 0 14px ${data.color}) drop-shadow(0 0 28px ${data.color}60)`
          : isHovered
          ? 'drop-shadow(0 0 8px rgba(255,255,255,0.25))'
          : 'none',
      }}
      onClick={() => onSelect(zone)}
      onMouseEnter={() => onHover(zone)}
      onMouseLeave={() => onHover(null)}
    >
      {isSelected && (
        <circle cx={data.x} cy={data.y} r={r + 12}
          fill="none" stroke={data.color} strokeWidth={0.8} opacity={0.25}
          style={{ transformBox:'fill-box', transformOrigin:'center', animation:'al-spin 10s linear infinite' }}
        />
      )}
      <circle
        cx={data.x} cy={data.y} r={r}
        fill={baseColor}
        stroke={stroke}
        strokeWidth={isSelected ? 2 : 1}
        style={{ transition:'r 0.25s ease, fill 0.25s ease, stroke 0.25s ease' }}
      />
      <text x={data.x} y={data.y - 2} textAnchor="middle"
        style={{ fontSize:13, fontWeight:800, fill:'white', fontFamily:'"Bricolage Grotesque",system-ui', pointerEvents:'none' }}>
        {zone}
      </text>
      <text x={data.x} y={data.y + 14} textAnchor="middle"
        style={{ fontSize:10, fill:'rgba(255,255,255,0.6)', fontFamily:'Inter,system-ui', pointerEvents:'none' }}>
        {value}%
      </text>
    </g>
  );
}

function CausalExplorer({
  selectedZone, setSelectedZone,
  selectedOutcome, setSelectedOutcome,
  liveData, dataLoading,
  geoMode, setGeoMode,
  selectedState, setSelectedState,
  statesData, statesLoading,
}) {
  const [ref, visible] = useInView();
  const [hoveredZone, setHoveredZone] = useState(null);
  const [animating,   setAnimating]   = useState(false);

  // Zone-mode result
  const liveEntry = liveData?.[`${selectedZone}:${selectedOutcome}`];
  const zoneResult = liveEntry
    ? {
        pathway:    liveEntry.dominant_pathway.pathway,
        policy:     liveEntry.dominant_pathway.policy,
        equity:     liveEntry.dominant_pathway.equity_flag,
        confidence: liveEntry.dominant_pathway.confidence,
      }
    : PRECOMPUTED[selectedZone]?.[selectedOutcome];
  const zoneData = ZONES[selectedZone];

  // State-mode result
  const stateCode  = selectedState ? STATE_CODE_MAP[selectedState] : null;
  const stateEntry = (stateCode && statesData) ? statesData[`state_${stateCode}:${selectedOutcome}`] : null;
  const stateResult = stateEntry
    ? {
        pathway:    stateEntry.dominant_pathway.pathway,
        policy:     stateEntry.dominant_pathway.policy,
        equity:     stateEntry.dominant_pathway.equity_flag,
        confidence: stateEntry.dominant_pathway.confidence,
      }
    : null;
  const stateZoneCode = stateEntry?.zone;
  const stateZoneData = ZONES[stateZoneCode] || zoneData;

  const result     = geoMode === 'zone' ? zoneResult : stateResult;
  const activeZone = geoMode === 'zone' ? zoneData : stateZoneData;
  const activeColor = activeZone?.color || '#F59E0B';

  const handleZoneSelect = (zone) => {
    if (zone === selectedZone) return;
    setAnimating(true);
    setTimeout(() => { setSelectedZone(zone); setAnimating(false); }, 200);
  };

  const handleOutcomeSelect = (outcome) => {
    if (outcome === selectedOutcome) return;
    setAnimating(true);
    setTimeout(() => { setSelectedOutcome(outcome); setAnimating(false); }, 200);
  };

  const handleStateSelect = (state) => {
    if (state === selectedState) return;
    setAnimating(true);
    setTimeout(() => { setSelectedState(state); setAnimating(false); }, 200);
  };

  const hexToRgb = (hex) => hex.slice(1).match(/../g).map(h => parseInt(h, 16)).join(',');

  return (
    <section ref={ref} style={{ background:'#050A06', padding:'clamp(40px,5vw,80px) clamp(24px,4vw,56px)' }}>
      <style>{`
        @keyframes al-spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }
        .al-outcome-btn {
          padding: 10px 26px; border-radius: 100px; border: 1px solid;
          font-size: 13px; font-weight: 600; cursor: pointer;
          font-family: "Bricolage Grotesque", system-ui;
          transition: all 0.2s ease; letter-spacing: 0.01em;
        }
        .al-outcome-btn:hover { transform: translateY(-1px); }
        .al-zone-pill {
          padding: 6px 16px; border-radius: 100px; border: 1px solid;
          font-size: 12px; font-weight: 700; cursor: pointer;
          font-family: "Bricolage Grotesque", system-ui;
          transition: all 0.2s ease; letter-spacing: 0.02em;
        }
        .al-zone-pill:hover { transform: translateY(-1px); }
        .al-result-card {
          border-radius: 14px; padding: 16px;
          transition: transform 0.2s ease;
        }
        .al-geo-btn {
          padding: 8px 22px; border-radius: 100px; border: 1px solid;
          font-size: 12px; font-weight: 700; cursor: pointer;
          font-family: "Bricolage Grotesque", system-ui;
          transition: all 0.2s ease; letter-spacing: 0.04em;
          text-transform: uppercase;
        }
        .al-geo-btn:hover { transform: translateY(-1px); }
      `}</style>
      <div style={{ maxWidth:1200, margin:'0 auto' }}>

        {/* Header */}
        <div style={{ textAlign:'center', marginBottom:'clamp(28px,3.5vw,44px)', ...fadeUp(visible) }}>
          <p style={{ fontSize:11, fontWeight:700, color:'#F59E0B', textTransform:'uppercase',
            letterSpacing:'0.18em', marginBottom:14, fontFamily:'Inter,system-ui' }}>
            INTERACTIVE EXPLORER
          </p>
          <h2 style={{ fontFamily:'"Bricolage Grotesque", system-ui', fontWeight:800,
            fontSize:'clamp(36px,5vw,64px)', color:'white',
            letterSpacing:'-0.04em', margin:'0 0 20px', lineHeight:1.05 }}>
            Click a zone. See the causal pathway.
          </h2>
          <p style={{ fontSize:17, color:'rgba(255,255,255,0.4)', lineHeight:1.8,
            maxWidth:480, margin:'0 auto', fontFamily:'Inter,system-ui' }}>
            Real findings · NDHS 2024 · 39,050 Nigerian women · Powered by Llama 3.1 + N-ATLAS
          </p>
          {dataLoading && (
            <p style={{ fontSize:11, color:'rgba(255,255,255,0.2)', marginTop:10,
              fontFamily:'Inter,system-ui', letterSpacing:'0.05em' }}>
              Loading live results…
            </p>
          )}
        </div>

        {/* Outcome selector */}
        <div style={{ display:'flex', justifyContent:'center', gap:10, marginBottom:16,
          flexWrap:'wrap', ...fadeUp(visible, 0.1) }}>
          {OUTCOMES.map(({ id, label }) => (
            <button key={id} className="al-outcome-btn" onClick={() => handleOutcomeSelect(id)} style={{
              borderColor:  selectedOutcome === id ? '#F59E0B' : 'rgba(255,255,255,0.1)',
              background:   selectedOutcome === id ? 'rgba(245,158,11,0.12)' : 'transparent',
              color:        selectedOutcome === id ? '#F59E0B' : 'rgba(255,255,255,0.45)',
            }}>{label}</button>
          ))}
        </div>

        {/* Geography level toggle */}
        <div style={{ display:'flex', justifyContent:'center', gap:8, marginBottom:36, ...fadeUp(visible, 0.13) }}>
          {[['zone','By Zone'],['state','By State']].map(([mode, label]) => (
            <button key={mode} className="al-geo-btn" onClick={() => setGeoMode(mode)} style={{
              borderColor: geoMode === mode ? 'rgba(255,255,255,0.45)' : 'rgba(255,255,255,0.1)',
              background:  geoMode === mode ? 'rgba(255,255,255,0.1)'  : 'transparent',
              color:       geoMode === mode ? 'white'                   : 'rgba(255,255,255,0.38)',
            }}>{label}</button>
          ))}
        </div>

        {/* Map + Panel */}
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(300px, 1fr))',
          gap:'clamp(24px,3vw,40px)', alignItems:'start', ...fadeUp(visible, 0.15) }}>

          {/* Left column — zone map OR state grid */}
          <div>
            <p style={{ fontSize:11, fontWeight:600, color:'rgba(255,255,255,0.22)',
              textTransform:'uppercase', letterSpacing:'0.12em', marginBottom:18,
              textAlign:'center', fontFamily:'Inter,system-ui' }}>
              {geoMode === 'zone'
                ? `Nigeria · Six Geopolitical Zones · ${OUTCOMES.find(o=>o.id===selectedOutcome)?.label}`
                : `Nigeria · 37 States · ${OUTCOMES.find(o=>o.id===selectedOutcome)?.label}`}
            </p>

            {geoMode === 'zone' ? (
              <>
                <div style={{ background:'rgba(255,255,255,0.02)', border:'1px solid rgba(255,255,255,0.06)',
                  borderRadius:20, padding:'12px 4px', overflow:'hidden' }}>
                  <svg viewBox="80 140 440 360" style={{ width:'100%', maxHeight:380 }}>
                    {Object.entries(ZONES).map(([zone, data]) =>
                      Object.entries(ZONES).map(([zone2, data2]) => {
                        if (zone >= zone2) return null;
                        const dist = Math.sqrt((data.x-data2.x)**2+(data.y-data2.y)**2);
                        if (dist > 160) return null;
                        return (
                          <line key={`${zone}-${zone2}`}
                            x1={data.x} y1={data.y} x2={data2.x} y2={data2.y}
                            stroke="rgba(255,255,255,0.04)" strokeWidth={1} />
                        );
                      })
                    )}
                    {Object.entries(ZONES).map(([zone, data]) => (
                      <NigeriaZonePath key={zone} zone={zone} data={data}
                        isSelected={selectedZone===zone} isHovered={hoveredZone===zone}
                        onSelect={handleZoneSelect} onHover={setHoveredZone}
                        outcome={selectedOutcome}
                        liveValue={liveData?.[`${zone}:${selectedOutcome}`]?.stats?.[`${selectedOutcome}_prevalence_pct`]}
                      />
                    ))}
                  </svg>
                </div>
                <div style={{ display:'flex', justifyContent:'center', gap:16, marginTop:16, flexWrap:'wrap' }}>
                  {[['Low', 0.15],['Medium', 0.38],['High', 0.62],['Severe', 0.85]].map(([l, a]) => (
                    <div key={l} style={{ display:'flex', alignItems:'center', gap:6 }}>
                      <div style={{ width:8, height:8, borderRadius:'50%', background:`rgba(15,110,86,${a})` }} />
                      <span style={{ fontSize:11, color:'rgba(255,255,255,0.3)',
                        fontFamily:'Inter,system-ui', letterSpacing:'0.05em' }}>{l}</span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div style={{ background:'rgba(255,255,255,0.02)', border:'1px solid rgba(255,255,255,0.06)',
                borderRadius:20, padding:'16px 20px', maxHeight:380, overflowY:'auto' }}>
                {statesLoading ? (
                  <p style={{ textAlign:'center', color:'rgba(255,255,255,0.3)', fontSize:13,
                    fontFamily:'Inter,system-ui', margin:'24px 0' }}>Loading state data…</p>
                ) : (
                  Object.entries(STATE_ZONES).map(([zCode, states]) => (
                    <div key={zCode} style={{ marginBottom:16 }}>
                      <div style={{ fontSize:10, fontWeight:700, color:ZONES[zCode]?.color || '#F59E0B',
                        textTransform:'uppercase', letterSpacing:'0.14em', marginBottom:8,
                        fontFamily:'Inter,system-ui' }}>
                        {zCode} · {ZONES[zCode]?.name}
                      </div>
                      <div style={{ display:'flex', flexWrap:'wrap', gap:6 }}>
                        {states.map(state => (
                          <button key={state} className="al-zone-pill"
                            onClick={() => handleStateSelect(state)} style={{
                              borderColor: selectedState===state
                                ? ZONES[zCode]?.color || '#F59E0B'
                                : 'rgba(255,255,255,0.1)',
                              background: selectedState===state
                                ? `rgba(${hexToRgb(ZONES[zCode]?.color || '#F59E0B')},0.15)`
                                : 'transparent',
                              color: selectedState===state
                                ? ZONES[zCode]?.color || '#F59E0B'
                                : 'rgba(255,255,255,0.35)',
                            }}>{state}</button>
                        ))}
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>

          {/* Result panel */}
          <div>
            {/* Zone header */}
            {geoMode === 'zone' && (
              <div style={{ display:'flex', alignItems:'center', gap:14, marginBottom:24,
                background:'rgba(255,255,255,0.03)', border:'1px solid rgba(255,255,255,0.07)',
                borderRadius:16, padding:'16px 20px' }}>
                <div style={{ width:44, height:44, borderRadius:12,
                  background:`rgba(${hexToRgb(zoneData.color)},0.15)`,
                  border:`1px solid rgba(${hexToRgb(zoneData.color)},0.3)`,
                  display:'flex', alignItems:'center', justifyContent:'center',
                  fontSize:13, fontWeight:800, color:zoneData.color,
                  fontFamily:'"Bricolage Grotesque", system-ui', flexShrink:0 }}>
                  {selectedZone}
                </div>
                <div style={{ flex:1 }}>
                  <div style={{ fontSize:17, fontWeight:800, color:'white',
                    fontFamily:'"Bricolage Grotesque", system-ui', letterSpacing:'-0.02em' }}>
                    {zoneData.name}
                  </div>
                  <div style={{ fontSize:12, color:'rgba(255,255,255,0.38)', marginTop:2,
                    fontFamily:'Inter,system-ui', letterSpacing:'0.03em' }}>
                    {OUTCOMES.find(o=>o.id===selectedOutcome)?.label}
                  </div>
                </div>
                <div style={{ textAlign:'right' }}>
                  <div style={{ fontSize:34, fontWeight:800, color:zoneData.color,
                    fontFamily:'"Bricolage Grotesque", system-ui', lineHeight:1, letterSpacing:'-0.04em' }}>
                    {zoneData[selectedOutcome]}%
                  </div>
                  <div style={{ fontSize:10, color:'rgba(255,255,255,0.25)',
                    textTransform:'uppercase', letterSpacing:'0.1em', marginTop:2,
                    fontFamily:'Inter,system-ui' }}>prevalence</div>
                </div>
              </div>
            )}

            {/* State header */}
            {geoMode === 'state' && selectedState && (
              <div style={{ display:'flex', alignItems:'center', gap:14, marginBottom:24,
                background:'rgba(255,255,255,0.03)', border:'1px solid rgba(255,255,255,0.07)',
                borderRadius:16, padding:'16px 20px' }}>
                <div style={{ width:44, height:44, borderRadius:12,
                  background:`rgba(${hexToRgb(activeColor)},0.15)`,
                  border:`1px solid rgba(${hexToRgb(activeColor)},0.3)`,
                  display:'flex', alignItems:'center', justifyContent:'center',
                  fontSize:13, fontWeight:800, color:activeColor,
                  fontFamily:'"Bricolage Grotesque", system-ui', flexShrink:0 }}>
                  {stateZoneCode || '—'}
                </div>
                <div style={{ flex:1 }}>
                  <div style={{ fontSize:17, fontWeight:800, color:'white',
                    fontFamily:'"Bricolage Grotesque", system-ui', letterSpacing:'-0.02em' }}>
                    {selectedState}
                  </div>
                  <div style={{ fontSize:12, color:'rgba(255,255,255,0.38)', marginTop:2,
                    fontFamily:'Inter,system-ui', letterSpacing:'0.03em' }}>
                    {OUTCOMES.find(o=>o.id===selectedOutcome)?.label}
                  </div>
                </div>
                <div style={{ textAlign:'right' }}>
                  <div style={{ fontSize:34, fontWeight:800, color:activeColor,
                    fontFamily:'"Bricolage Grotesque", system-ui', lineHeight:1, letterSpacing:'-0.04em' }}>
                    {(selectedOutcome === 'anaemia'
                      ? stateEntry?.stats?.anaemia_prevalence_pct
                      : selectedOutcome === 'stunting'
                      ? stateEntry?.stats?.stunting_prevalence_pct
                      : stateEntry?.stats?.wasting_prevalence_pct
                    ) ?? '—'}%
                  </div>
                  <div style={{ fontSize:10, color:'rgba(255,255,255,0.25)',
                    textTransform:'uppercase', letterSpacing:'0.1em', marginTop:2,
                    fontFamily:'Inter,system-ui' }}>prevalence</div>
                </div>
              </div>
            )}

            {/* State placeholder */}
            {geoMode === 'state' && !selectedState && (
              <div style={{ display:'flex', alignItems:'center', justifyContent:'center',
                background:'rgba(255,255,255,0.02)', border:'1px solid rgba(255,255,255,0.05)',
                borderRadius:16, padding:'40px 20px', marginBottom:24 }}>
                <p style={{ fontSize:14, color:'rgba(255,255,255,0.25)', fontFamily:'Inter,system-ui',
                  margin:0, textAlign:'center' }}>
                  Select a state above to see its causal pathway
                </p>
              </div>
            )}

            {/* Confidence bar */}
            {result && (
              <div style={{ marginBottom:20, padding:'14px 18px',
                background:'rgba(255,255,255,0.02)', border:'1px solid rgba(255,255,255,0.06)',
                borderRadius:12 }}>
                <div style={{ display:'flex', justifyContent:'space-between', marginBottom:8 }}>
                  <span style={{ fontSize:11, fontWeight:600, color:'rgba(255,255,255,0.28)',
                    textTransform:'uppercase', letterSpacing:'0.12em', fontFamily:'Inter,system-ui' }}>
                    Pathway confidence
                  </span>
                  <span style={{ fontSize:12, fontWeight:700, color:'#4ADE80',
                    fontFamily:'"Bricolage Grotesque",system-ui' }}>
                    {Math.round(result.confidence * 100)}%
                  </span>
                </div>
                <div style={{ height:3, background:'rgba(255,255,255,0.06)', borderRadius:2, overflow:'hidden' }}>
                  <div style={{ width:`${result.confidence*100}%`, height:'100%',
                    background:'linear-gradient(90deg, #0F6E56, #4ADE80)',
                    borderRadius:2, transition:'width 0.7s cubic-bezier(0.25,1,0.5,1)' }} />
                </div>
              </div>
            )}

            {result && (
              <div style={{
                opacity: animating ? 0 : 1, transform: animating ? 'translateY(8px)' : 'translateY(0)',
                transition:'opacity 0.2s ease, transform 0.2s ease',
              }}>
                {/* Causal pathway */}
                <div className="al-result-card" style={{
                  background:'rgba(255,255,255,0.03)', border:'1px solid rgba(255,255,255,0.07)',
                  marginBottom:12,
                }}>
                  <p style={{ fontSize:11, fontWeight:700, color:'rgba(255,255,255,0.28)',
                    textTransform:'uppercase', letterSpacing:'0.14em', margin:'0 0 12px',
                    fontFamily:'Inter,system-ui' }}>Causal Pathway</p>
                  <div style={{ fontSize:14, color:'rgba(255,255,255,0.82)', lineHeight:1.7,
                    fontFamily:'Inter,system-ui' }}>
                    {result.pathway.split('→').map((step, i, arr) => (
                      <span key={i}>
                        <span style={{
                          color: i===arr.length-1 ? activeColor : 'rgba(255,255,255,0.82)',
                          fontWeight: i===arr.length-1 ? 700 : 400,
                        }}>{step.trim()}</span>
                        {i < arr.length-1 && (
                          <span style={{ color:'#F59E0B', margin:'0 7px', opacity:0.8 }}>→</span>
                        )}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Policy */}
                <div className="al-result-card" style={{
                  background:'rgba(15,110,86,0.1)', border:'1px solid rgba(15,110,86,0.2)',
                  marginBottom:12,
                }}>
                  <p style={{ fontSize:11, fontWeight:700, color:'#4ADE80',
                    textTransform:'uppercase', letterSpacing:'0.14em', margin:'0 0 12px',
                    fontFamily:'Inter,system-ui' }}>Policy Intervention</p>
                  <p style={{ fontSize:14, color:'rgba(255,255,255,0.78)', lineHeight:1.7, margin:0,
                    fontFamily:'Inter,system-ui' }}>{result.policy}</p>
                </div>

                {/* Equity */}
                <div className="al-result-card" style={{
                  background:`rgba(${hexToRgb(activeColor)},0.08)`,
                  border:`1px solid rgba(${hexToRgb(activeColor)},0.2)`,
                }}>
                  <p style={{ fontSize:11, fontWeight:700, color:activeColor,
                    textTransform:'uppercase', letterSpacing:'0.14em', margin:'0 0 12px',
                    fontFamily:'Inter,system-ui' }}>Equity Flag</p>
                  <p style={{ fontSize:14, color:'rgba(255,255,255,0.72)', lineHeight:1.7, margin:0,
                    fontFamily:'Inter,system-ui' }}>{result.equity}</p>
                </div>
              </div>
            )}

            {/* Zone pills — zone mode only */}
            {geoMode === 'zone' && (
              <div style={{ display:'flex', gap:8, flexWrap:'wrap', marginTop:20 }}>
                {Object.entries(ZONES).map(([zone, data]) => (
                  <button key={zone} className="al-zone-pill" onClick={() => handleZoneSelect(zone)} style={{
                    borderColor: selectedZone===zone ? data.color : 'rgba(255,255,255,0.08)',
                    background:  selectedZone===zone ? `rgba(${hexToRgb(data.color)},0.12)` : 'transparent',
                    color:       selectedZone===zone ? data.color : 'rgba(255,255,255,0.32)',
                  }}>{zone}</button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

/* ----------------------------------------------------------------
   CAUSAL DAG SECTION
---------------------------------------------------------------- */
function CausalDAGSection({ selectedZone, selectedOutcome, liveData, geoMode, selectedState, statesData }) {
  const [ref, visible] = useInView();

  const isZoneMode = !geoMode || geoMode === 'zone';

  if (isZoneMode && (!selectedZone || !selectedOutcome)) return null;
  if (!isZoneMode && (!selectedState || !selectedOutcome)) return null;

  let result, zoneData, activeLabel, uid;

  if (isZoneMode) {
    const liveEntry = liveData?.[`${selectedZone}:${selectedOutcome}`];
    result = liveEntry
      ? {
          pathway:    liveEntry.dominant_pathway.pathway,
          policy:     liveEntry.dominant_pathway.policy,
          equity:     liveEntry.dominant_pathway.equity_flag,
          confidence: liveEntry.dominant_pathway.confidence,
        }
      : PRECOMPUTED[selectedZone]?.[selectedOutcome];
    zoneData    = ZONES[selectedZone];
    activeLabel = zoneData?.name;
    uid         = `${selectedZone}-${selectedOutcome}`;
  } else {
    const stateCode  = STATE_CODE_MAP[selectedState];
    const stateEntry = (stateCode && statesData) ? statesData[`state_${stateCode}:${selectedOutcome}`] : null;
    result = stateEntry
      ? {
          pathway:    stateEntry.dominant_pathway.pathway,
          policy:     stateEntry.dominant_pathway.policy,
          equity:     stateEntry.dominant_pathway.equity_flag,
          confidence: stateEntry.dominant_pathway.confidence,
        }
      : null;
    const stateZoneCode = stateEntry?.zone;
    zoneData    = ZONES[stateZoneCode] || ZONES['SW'];
    activeLabel = selectedState;
    uid         = `state-${(selectedState || '').replace(/\s+/g, '-')}-${selectedOutcome}`;
  }

  if (!result || !zoneData) return null;

  const hexToRgb = (hex) =>
    hex.replace('#', '').match(/../g).map(h => parseInt(h, 16)).join(',');

  const dagNodes = result.pathway
    .split('→')
    .map((s, i, arr) => ({
      label: s.trim().replace(/\s*—.*$/, '').trim(),
      kind:  i === 0 ? 'exposure' : i === arr.length - 1 ? 'outcome' : 'mediator',
    }));

  const n      = dagNodes.length;
  const NODE_W = 190;
  const GAP_X  = 72;
  const CARD_H = 108;
  const yMid   = CARD_H / 2;
  const totalW = n * NODE_W + (n - 1) * GAP_X;

  const paletteFor = (kind) => {
    if (kind === 'exposure') return { accent: '#DC2626', bg: 'rgba(220,38,38,0.05)', border: 'rgba(220,38,38,0.18)' };
    if (kind === 'outcome')  return { accent: zoneData.color, bg: `rgba(${hexToRgb(zoneData.color)},0.07)`, border: `rgba(${hexToRgb(zoneData.color)},0.25)` };
    return { accent: '#0F6E56', bg: 'rgba(15,110,86,0.05)', border: 'rgba(15,110,86,0.18)' };
  };

  const zRgb = zoneData.color.replace('#', '').match(/../g).map(h => parseInt(h, 16));
  const sRgb = [0xDC, 0x26, 0x26];
  const mixGrad = (t) => {
    const out = sRgb.map((v, idx) => Math.round(v + (zRgb[idx] - v) * Math.max(0, Math.min(1, t))));
    return `#${out.map(v => Math.max(0, Math.min(255, v)).toString(16).padStart(2, '0')).join('')}`;
  };

  return (
    <section ref={ref} style={{
      background: '#F8F7F4',
      padding: 'clamp(36px,4.5vw,60px) clamp(24px,4vw,56px)',
      borderTop: '1px solid #E5E1D8',
    }}>
      <div style={{ maxWidth: 1200, margin: '0 auto', ...fadeUp(visible) }}>

        {/* Header */}
        <div style={{ marginBottom: 28 }}>
          <p style={{
            fontSize: 11, fontWeight: 700, color: '#0F6E56',
            textTransform: 'uppercase', letterSpacing: '0.18em',
            margin: '0 0 10px', fontFamily: 'Inter,system-ui',
          }}>
            CAUSAL DAG · {activeLabel} · {OUTCOMES.find(o => o.id === selectedOutcome)?.label}
          </p>
          <h3 style={{
            fontFamily: '"Bricolage Grotesque", system-ui', fontWeight: 800,
            fontSize: 'clamp(22px,2.8vw,36px)', color: '#1C1F1D',
            letterSpacing: '-0.03em', margin: '0 0 8px', lineHeight: 1.1,
          }}>
            Pathway visualised — step by step
          </h3>
          <p style={{
            fontSize: 14, color: '#4A524D', fontFamily: 'Inter,system-ui',
            margin: 0, lineHeight: 1.6, maxWidth: 560,
          }}>
            Each node is a causal link identified by Àlááfíà for{' '}
            <strong style={{ color: '#1C1F1D' }}>{activeLabel}</strong>.
            Gradient follows pathway direction from exposure to outcome.
          </p>
        </div>

        {/* Legend */}
        <div style={{ display: 'flex', gap: 20, marginBottom: 28, flexWrap: 'wrap' }}>
          {['exposure', 'mediator', 'outcome'].map(kind => {
            const p = paletteFor(kind);
            return (
              <div key={kind} style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                <div style={{ width: 9, height: 9, borderRadius: '50%', background: p.accent }} />
                <span style={{ fontSize: 11, color: '#4A524D', fontFamily: 'Inter,system-ui',
                  textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: 600 }}>
                  {kind}
                </span>
              </div>
            );
          })}
        </div>

        {/* DAG — horizontally scrollable on narrow viewports */}
        <div style={{ overflowX: 'auto', paddingBottom: 12 }}>
          <div style={{ position: 'relative', width: totalW, height: CARD_H, margin: '0 auto' }}>

            {/* Node cards */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: `repeat(${n}, ${NODE_W}px)`,
              columnGap: GAP_X,
              height: CARD_H,
              position: 'relative', zIndex: 2,
            }}>
              {dagNodes.map((node, i) => {
                const p = paletteFor(node.kind);
                return (
                  <div key={i} style={{
                    height: CARD_H, boxSizing: 'border-box',
                    background: p.bg, borderRadius: 16, padding: '14px 16px',
                    border: `1px solid ${p.border}`, borderTop: `3px solid ${p.accent}`,
                    boxShadow: '0 3px 14px rgba(28,31,29,0.07)',
                    display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
                  }}>
                    <div style={{ fontSize: 9, fontWeight: 700, color: p.accent,
                      textTransform: 'uppercase', letterSpacing: '0.14em', fontFamily: 'Inter,system-ui' }}>
                      {node.kind} · {String(i + 1).padStart(2, '0')}/{String(n).padStart(2, '0')}
                    </div>
                    <div style={{ fontFamily: '"Bricolage Grotesque", system-ui',
                      fontWeight: 800, fontSize: 13, lineHeight: 1.3,
                      color: '#1C1F1D', letterSpacing: '-0.01em' }}>
                      {node.label}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* SVG arrow layer */}
            <svg
              width={totalW} height={CARD_H}
              viewBox={`0 0 ${totalW} ${CARD_H}`}
              style={{ position: 'absolute', left: 0, top: 0, zIndex: 1, pointerEvents: 'none' }}
            >
              <defs>
                {Array.from({ length: n - 1 }, (_, i) => (
                  <linearGradient key={i} id={`dag-lg-${uid}-${i}`} x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0" stopColor={mixGrad(i / (n - 1))} />
                    <stop offset="1" stopColor={mixGrad((i + 1) / (n - 1))} />
                  </linearGradient>
                ))}
                <marker id={`dag-arr-${uid}`} viewBox="0 0 10 10" refX="8" refY="5"
                  markerWidth="5" markerHeight="5" orient="auto-start-reverse">
                  <path d="M0,0 L10,5 L0,10 z" fill={zoneData.color} />
                </marker>
              </defs>
              {Array.from({ length: n - 1 }, (_, i) => {
                const x1   = (i + 1) * NODE_W + i * GAP_X;
                const x2   = x1 + GAP_X;
                const path = `M ${x1} ${yMid} C ${x1 + 22} ${yMid - 16}, ${x2 - 22} ${yMid + 16}, ${x2} ${yMid}`;
                return (
                  <g key={i}>
                    <path d={path} stroke={`url(#dag-lg-${uid}-${i})`}
                      strokeWidth="2.5" fill="none" strokeLinecap="round"
                      markerEnd={i === n - 2 ? `url(#dag-arr-${uid})` : undefined}
                    />
                    <circle r="3" fill={mixGrad((i + 0.5) / (n - 1))}>
                      <animateMotion dur={`${2.6 + i * 0.35}s`} repeatCount="indefinite" path={path} />
                    </circle>
                  </g>
                );
              })}
            </svg>
          </div>
        </div>

        {/* Confidence strip */}
        <div style={{
          marginTop: 28, display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap',
          padding: '14px 20px', background: 'white', borderRadius: 14, border: '1px solid #E5E1D8',
        }}>
          <span style={{ fontSize: 11, fontWeight: 700, color: '#7A8079',
            textTransform: 'uppercase', letterSpacing: '0.14em',
            fontFamily: 'Inter,system-ui', flexShrink: 0 }}>
            Pathway confidence
          </span>
          <div style={{ flex: 1, minWidth: 100, maxWidth: 220,
            height: 5, background: '#F1EFEA', borderRadius: 3, overflow: 'hidden' }}>
            <div style={{
              width: `${result.confidence * 100}%`, height: '100%',
              background: `linear-gradient(90deg, #DC2626, ${zoneData.color})`,
              borderRadius: 3, transition: 'width 0.8s cubic-bezier(0.25,1,0.5,1)',
            }} />
          </div>
          <span style={{ fontFamily: '"Bricolage Grotesque", system-ui', fontWeight: 800,
            fontSize: 20, color: '#1C1F1D', letterSpacing: '-0.02em', flexShrink: 0 }}>
            {Math.round(result.confidence * 100)}%
          </span>
          <span style={{ fontSize: 13, color: '#7A8079', fontFamily: 'Inter,system-ui' }}>
            {result.confidence >= 0.8 ? 'High confidence — strong epidemiological evidence' :
             result.confidence >= 0.7 ? 'Moderate confidence — robust, some causal uncertainty' :
             'Exploratory — pathway plausible, evidence limited'}
          </span>
        </div>
      </div>
    </section>
  );
}

/* ----------------------------------------------------------------
   SECTION 3 — THE INVERSION FINDING
---------------------------------------------------------------- */
function InversionFinding() {
  const [ref, visible] = useInView();
  return (
    <section ref={ref} style={{ background:'#F8F8F6', padding:'clamp(40px,5vw,80px) clamp(24px,4vw,56px)' }}>
      <div style={{ maxWidth:1100, margin:'0 auto' }}>

        <div style={{ textAlign:'center', marginBottom:'clamp(28px,3.5vw,44px)', ...fadeUp(visible) }}>
          <p style={{ fontSize:11, fontWeight:700, color:'#DC2626', textTransform:'uppercase',
            letterSpacing:'0.18em', marginBottom:14, fontFamily:'Inter,system-ui' }}>KEY FINDING</p>
          <h2 style={{ fontFamily:'"Bricolage Grotesque", system-ui', fontWeight:800,
            fontSize:'clamp(36px,5vw,64px)', color:'#111827',
            letterSpacing:'-0.04em', margin:'0 0 20px', lineHeight:1.05 }}>
            Two crises. Two geographies.{' '}
            <span style={{ color:'#0F6E56' }}>One country.</span>
          </h2>
          <p style={{ fontSize:17, color:'#6B7280', lineHeight:1.8,
            maxWidth:540, margin:'0 auto', fontFamily:'Inter,system-ui' }}>
            Nigeria&rsquo;s stunting crisis and anaemia crisis are geographically inverted —
            with completely different causal structures. Standard regression missed this.
            Àlááfíà found it.
          </p>
        </div>

        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(300px, 1fr))',
          gap:20, ...fadeUp(visible, 0.12) }}>

          {/* Stunting */}
          <div style={{ background:'white', borderRadius:20, padding:32,
            border:'1px solid rgba(0,0,0,0.06)',
            borderTop:'3px solid #DC2626',
            boxShadow:'0 2px 8px rgba(0,0,0,0.04)',
            transition:'box-shadow 0.3s ease, transform 0.3s ease',
          }}
          onMouseEnter={e => { e.currentTarget.style.transform='translateY(-5px)'; e.currentTarget.style.boxShadow='0 20px 48px rgba(0,0,0,0.09)'; }}
          onMouseLeave={e => { e.currentTarget.style.transform='translateY(0)'; e.currentTarget.style.boxShadow='0 2px 8px rgba(0,0,0,0.04)'; }}>
            <p style={{ fontSize:11, fontWeight:700, color:'#DC2626', textTransform:'uppercase',
              letterSpacing:'0.15em', margin:'0 0 20px', fontFamily:'Inter,system-ui' }}>
              Child Stunting Burden
            </p>
            {[
              { zone:'North Central', val:52.1, color:'#DC2626' },
              { zone:'North East',    val:52.1, color:'#DC2626' },
              { zone:'North West',    val:35.5, color:'#EA580C' },
              { zone:'South East',    val:19.3, color:'#16A34A' },
              { zone:'South South',   val:20.0, color:'#16A34A' },
              { zone:'South West',    val:21.2, color:'#16A34A' },
            ].map(({ zone, val, color }) => (
              <div key={zone} style={{ marginBottom:14 }}>
                <div style={{ display:'flex', justifyContent:'space-between', marginBottom:5 }}>
                  <span style={{ fontSize:13, color:'#374151', fontWeight:500,
                    fontFamily:'Inter,system-ui' }}>{zone}</span>
                  <span style={{ fontSize:13, fontWeight:700, color,
                    fontFamily:'"Bricolage Grotesque",system-ui' }}>{val}%</span>
                </div>
                <div style={{ height:4, background:'#F3F4F6', borderRadius:2, overflow:'hidden' }}>
                  <div style={{ width:`${val/55*100}%`, height:'100%', background:color,
                    borderRadius:2, transition:'width 0.9s cubic-bezier(0.25,1,0.5,1)' }} />
                </div>
              </div>
            ))}
            <div style={{ marginTop:20, padding:'14px 16px',
              background:'#F9FAFB', borderRadius:12, border:'1px solid rgba(0,0,0,0.05)',
              fontSize:13, color:'#374151', lineHeight:1.65, fontFamily:'Inter,system-ui' }}>
              <strong style={{ color:'#111827' }}>Primary driver:</strong> Sanitation — not solid fuel.
              North West&rsquo;s better sanitation (3.4%) explains why its stunting is
              35.5% vs North East&rsquo;s 52.1%.
            </div>
          </div>

          {/* Anaemia */}
          <div style={{ background:'white', borderRadius:20, padding:32,
            border:'1px solid rgba(0,0,0,0.06)',
            borderTop:'3px solid #7C3AED',
            boxShadow:'0 2px 8px rgba(0,0,0,0.04)',
            transition:'box-shadow 0.3s ease, transform 0.3s ease',
          }}
          onMouseEnter={e => { e.currentTarget.style.transform='translateY(-5px)'; e.currentTarget.style.boxShadow='0 20px 48px rgba(0,0,0,0.09)'; }}
          onMouseLeave={e => { e.currentTarget.style.transform='translateY(0)'; e.currentTarget.style.boxShadow='0 2px 8px rgba(0,0,0,0.04)'; }}>
            <p style={{ fontSize:11, fontWeight:700, color:'#7C3AED', textTransform:'uppercase',
              letterSpacing:'0.15em', margin:'0 0 20px', fontFamily:'Inter,system-ui' }}>
              Maternal Anaemia Burden
            </p>
            {[
              { zone:'South East',    val:55.4, color:'#7C3AED' },
              { zone:'South South',   val:46.9, color:'#9333EA' },
              { zone:'South West',    val:41.1, color:'#A855F7' },
              { zone:'North East',    val:41.9, color:'#C084FC' },
              { zone:'North Central', val:40.1, color:'#C084FC' },
              { zone:'North West',    val:36.0, color:'#16A34A' },
            ].map(({ zone, val, color }) => (
              <div key={zone} style={{ marginBottom:14 }}>
                <div style={{ display:'flex', justifyContent:'space-between', marginBottom:5 }}>
                  <span style={{ fontSize:13, color:'#374151', fontWeight:500,
                    fontFamily:'Inter,system-ui' }}>{zone}</span>
                  <span style={{ fontSize:13, fontWeight:700, color,
                    fontFamily:'"Bricolage Grotesque",system-ui' }}>{val}%</span>
                </div>
                <div style={{ height:4, background:'#F3F4F6', borderRadius:2, overflow:'hidden' }}>
                  <div style={{ width:`${val/60*100}%`, height:'100%', background:color,
                    borderRadius:2, transition:'width 0.9s cubic-bezier(0.25,1,0.5,1)' }} />
                </div>
              </div>
            ))}
            <div style={{ marginTop:20, padding:'14px 16px',
              background:'#F9FAFB', borderRadius:12, border:'1px solid rgba(0,0,0,0.05)',
              fontSize:13, color:'#374151', lineHeight:1.65, fontFamily:'Inter,system-ui' }}>
              <strong style={{ color:'#111827' }}>Counterintuitive:</strong> South East has the{' '}
              <em>best</em> WASH but the <em>worst</em> anaemia. This is a food environment problem,
              not a poverty problem.
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ----------------------------------------------------------------
   SECTION 4 — HOW IT WORKS
---------------------------------------------------------------- */
function HowItWorks() {
  const [ref, visible] = useInView();
  const AGENTS = [
    {
      num:'1', model:'Llama 3.1 8B', role:'DAG Proposer',
      color:'#2563EB',
      desc:'Reads the population token and proposes the most plausible causal pathway from structural exposures to health outcome, grounded in Nigerian epidemiological literature.',
      icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="#2563EB" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/></svg>,
    },
    {
      num:'2', model:'Llama 3.1 8B', role:'DAG Critic',
      color:'#DC2626',
      desc:'Adversarially challenges every proposed causal edge — testing for reverse causation, unmeasured confounding, missing mediators, and whether the evidence applies to Nigeria specifically.',
      icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9" stroke="#DC2626" strokeWidth="1.8"/><path d="M9 9l6 6M15 9l-6 6" stroke="#DC2626" strokeWidth="2" strokeLinecap="round"/></svg>,
    },
    {
      num:'3', model:'N-ATLAS', role:'DAG Judge',
      color:'#0F6E56',
      desc:"Nigeria's national AI arbitrates the debate. Grounds the final pathway in Nigerian cultural and social context across all six geopolitical zones. Produces the policy implication.",
      icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M9 12l2.5 2.5L15 9" stroke="#0F6E56" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><circle cx="12" cy="12" r="9" stroke="#0F6E56" strokeWidth="1.8"/></svg>,
    },
  ];

  const hexToRgb = (hex) => hex.slice(1).match(/../g).map(h => parseInt(h, 16)).join(',');

  return (
    <section ref={ref} style={{ background:'#050A06', padding:'clamp(40px,5vw,80px) clamp(24px,4vw,56px)' }}>
      <div style={{ maxWidth:1100, margin:'0 auto' }}>

        <div style={{ textAlign:'center', marginBottom:'clamp(28px,3.5vw,44px)', ...fadeUp(visible) }}>
          <p style={{ fontSize:11, fontWeight:700, color:'#F59E0B', textTransform:'uppercase',
            letterSpacing:'0.18em', marginBottom:14, fontFamily:'Inter,system-ui' }}>
            THE ARCHITECTURE
          </p>
          <h2 style={{ fontFamily:'"Bricolage Grotesque", system-ui', fontWeight:800,
            fontSize:'clamp(36px,5vw,64px)', color:'white',
            letterSpacing:'-0.04em', margin:'0 0 20px', lineHeight:1.05 }}>
            Three AI agents. One Nigerian health question.
          </h2>
          <p style={{ fontSize:17, color:'rgba(255,255,255,0.38)', lineHeight:1.8,
            maxWidth:480, margin:'0 auto', fontFamily:'Inter,system-ui' }}>
            Every population record passes through a structured adversarial debate before
            a causal pathway is accepted. No single model decides alone.
          </p>
        </div>

        {/* Token example */}
        <div style={{ background:'rgba(255,255,255,0.025)', border:'1px solid rgba(255,255,255,0.07)',
          borderRadius:16, padding:'16px 20px', marginBottom:32, ...fadeUp(visible, 0.08) }}>
          <p style={{ fontSize:11, fontWeight:600, color:'rgba(255,255,255,0.28)',
            textTransform:'uppercase', letterSpacing:'0.12em', margin:'0 0 14px',
            fontFamily:'Inter,system-ui' }}>
            Population Token · Real NDHS 2024 Record
          </p>
          <div style={{ fontSize:12, color:'#4ADE80', fontFamily:'monospace',
            lineHeight:1.8, display:'flex', flexWrap:'wrap', gap:6 }}>
            {['STRATUM:zone_north_east','STRATUM:poorest','STRATUM:rural',
              'STRATUM:education_no_education','EXPOSURE:cooking_solid_fuel',
              'EXPOSURE:unimproved_water','EXPOSURE:health_facility_far',
              'EXPOSURE:high_malaria_burden','MEDIATOR:high_parity',
              'MEDIATOR:no_anc','OUTCOME:anaemia_moderate','EQUITY:zone_north_east'].map(t => (
              <span key={t} style={{ background:'rgba(74,222,128,0.06)',
                border:'1px solid rgba(74,222,128,0.12)', borderRadius:4,
                padding:'2px 8px', whiteSpace:'nowrap' }}>{t}</span>
            ))}
          </div>
        </div>

        {/* Agent cards */}
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(280px, 1fr))',
          gap:16, marginBottom:32 }}>
          {AGENTS.map(({ num, model, role, color, desc, icon }, i) => (
            <div key={num} style={{
              background:'rgba(255,255,255,0.025)', border:'1px solid rgba(255,255,255,0.07)',
              borderRadius:20, padding:28,
              transition:'transform 0.25s ease, border-color 0.25s ease',
              ...fadeUp(visible, 0.1 + i * 0.1),
            }}
            onMouseEnter={e => { e.currentTarget.style.transform='translateY(-4px)'; e.currentTarget.style.borderColor='rgba(255,255,255,0.14)'; }}
            onMouseLeave={e => { e.currentTarget.style.transform='translateY(0)'; e.currentTarget.style.borderColor='rgba(255,255,255,0.07)'; }}>
              <div style={{ display:'flex', alignItems:'center', gap:12, marginBottom:16 }}>
                <div style={{ width:40, height:40, borderRadius:12,
                  background:`rgba(${hexToRgb(color)},0.1)`,
                  border:`1px solid rgba(${hexToRgb(color)},0.2)`,
                  display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0 }}>
                  {icon}
                </div>
                <div style={{ flex:1 }}>
                  <div style={{ fontSize:11, fontWeight:600, color:'rgba(255,255,255,0.28)',
                    textTransform:'uppercase', letterSpacing:'0.1em', fontFamily:'Inter,system-ui' }}>
                    Agent {num}
                  </div>
                  <div style={{ fontSize:15, fontWeight:700, color:'white',
                    fontFamily:'"Bricolage Grotesque", system-ui', letterSpacing:'-0.01em' }}>
                    {role}
                  </div>
                </div>
                <div style={{ background:`rgba(${hexToRgb(color)},0.12)`,
                  border:`1px solid rgba(${hexToRgb(color)},0.2)`,
                  borderRadius:8, padding:'4px 10px', flexShrink:0 }}>
                  <span style={{ fontSize:11, fontWeight:600, color, fontFamily:'Inter,system-ui' }}>
                    {model}
                  </span>
                </div>
              </div>
              <p style={{ fontSize:14, color:'rgba(255,255,255,0.52)', lineHeight:1.75,
                margin:0, fontFamily:'Inter,system-ui' }}>{desc}</p>
            </div>
          ))}
        </div>

        {/* Data sources */}
        <div style={{ display:'flex', flexWrap:'wrap', gap:10, justifyContent:'center',
          ...fadeUp(visible, 0.4) }}>
          {[
            { label:'NDHS 2024',   sub:'39,050 women · Nigeria' },
            { label:'MICS 2021',   sub:'31,103 children · Nigeria' },
            { label:'Llama 3.1 8B',sub:'Meta · Open source · Local' },
            { label:'N-ATLAS',     sub:'NCAIR/NITDA · Nigeria National LLM' },
            { label:'Open source', sub:'github.com/Alaafia' },
          ].map(({ label, sub }) => (
            <div key={label} style={{
              background:'rgba(255,255,255,0.025)', border:'1px solid rgba(255,255,255,0.07)',
              borderRadius:12, padding:'12px 20px', textAlign:'center',
              transition:'border-color 0.2s ease',
            }}
            onMouseEnter={e => e.currentTarget.style.borderColor='rgba(255,255,255,0.15)'}
            onMouseLeave={e => e.currentTarget.style.borderColor='rgba(255,255,255,0.07)'}>
              <div style={{ fontSize:14, fontWeight:700, color:'white',
                fontFamily:'"Bricolage Grotesque", system-ui', letterSpacing:'-0.01em' }}>
                {label}
              </div>
              <div style={{ fontSize:11, color:'rgba(255,255,255,0.28)', marginTop:4,
                fontFamily:'Inter,system-ui' }}>{sub}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ----------------------------------------------------------------
   SECTION 5 — WHO USES ÀLÁÁFÍÀ
---------------------------------------------------------------- */
function WhoUsesIt() {
  const [ref, visible] = useInView();
  const USERS = [
    {
      icon:'🏛️', title:'Federal & State Government',
      desc:'FMOH, NCDC, and State Health Commissioners get zone-specific causal maps and intervention rankings — not regression tables. Àlááfíà tells them which structural node to target for maximum health impact.',
    },
    {
      icon:'🔬', title:'Researchers & PhD Students',
      desc:"Àlááfíà accelerates causal discovery from DHS/MICS data. What would take months of manual causal analysis now runs in hours — with full reproducibility and open source code.",
    },
    {
      icon:'🏥', title:'Health Startups & NGOs',
      desc:"Zone-specific causal intelligence for programme design. Build interventions grounded in what actually drives outcomes in each zone — not generic assumptions imported from other settings.",
    },
    {
      icon:'🌍', title:'UNICEF, WHO, Gates Foundation',
      desc:"MICS runs in 120+ countries. Àlááfíà's architecture is replicable on any MICS dataset. The same causal intelligence tool that works for Nigeria works for Ghana, Ethiopia, Bangladesh.",
    },
  ];

  return (
    <section ref={ref} style={{ background:'#F8F8F6', padding:'clamp(40px,5vw,80px) clamp(24px,4vw,56px)' }}>
      <div style={{ maxWidth:1100, margin:'0 auto' }}>

        <div style={{ textAlign:'center', marginBottom:'clamp(28px,3.5vw,44px)', ...fadeUp(visible) }}>
          <p style={{ fontSize:11, fontWeight:700, color:'#0F6E56', textTransform:'uppercase',
            letterSpacing:'0.18em', marginBottom:14, fontFamily:'Inter,system-ui' }}>WHO IT SERVES</p>
          <h2 style={{ fontFamily:'"Bricolage Grotesque", system-ui', fontWeight:800,
            fontSize:'clamp(36px,5vw,64px)', color:'#111827',
            letterSpacing:'-0.04em', margin:0, lineHeight:1.05 }}>
            Built for everyone who needs to know why.
          </h2>
        </div>

        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(260px, 1fr))', gap:16 }}>
          {USERS.map(({ icon, title, desc }, i) => (
            <div key={title} style={{
              background:'white', borderRadius:20, padding:32,
              border:'1px solid rgba(0,0,0,0.06)',
              borderTop:'2px solid #0F6E56',
              boxShadow:'0 1px 4px rgba(0,0,0,0.04)',
              transition:'transform 0.3s ease, box-shadow 0.3s ease',
              cursor:'default', ...fadeUp(visible, 0.08 + i * 0.08),
            }}
            onMouseEnter={e => { e.currentTarget.style.transform='translateY(-6px)'; e.currentTarget.style.boxShadow='0 24px 56px rgba(0,0,0,0.1)'; }}
            onMouseLeave={e => { e.currentTarget.style.transform='translateY(0)'; e.currentTarget.style.boxShadow='0 1px 4px rgba(0,0,0,0.04)'; }}>
              <div style={{ fontSize:30, marginBottom:18 }}>{icon}</div>
              <h3 style={{ fontFamily:'"Bricolage Grotesque", system-ui', fontWeight:800,
                fontSize:18, color:'#111827', margin:'0 0 12px', letterSpacing:'-0.02em' }}>
                {title}
              </h3>
              <p style={{ fontSize:15, color:'#6B7280', lineHeight:1.8, margin:0,
                fontFamily:'Inter,system-ui' }}>{desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ----------------------------------------------------------------
   SECTION 6 — CTA
---------------------------------------------------------------- */
function CTASection({ onNavigate, onRequestAccess }) {
  const [ref, visible] = useInView();
  return (
    <section ref={ref} style={{
      background:'#050A06', padding:'clamp(40px,5vw,80px) clamp(24px,4vw,56px)',
      textAlign:'center', position:'relative', overflow:'hidden',
    }}>
      {/* Background orbs */}
      <div style={{ position:'absolute', inset:0, pointerEvents:'none' }}>
        <div style={{ position:'absolute', top:'30%', left:'50%', transform:'translate(-50%,-50%)',
          width:700, height:400, borderRadius:'50%',
          background:'radial-gradient(ellipse, rgba(245,158,11,0.07) 0%, transparent 70%)' }} />
        <div style={{ position:'absolute', bottom:'10%', right:'15%', width:400, height:400,
          borderRadius:'50%', background:'radial-gradient(circle, rgba(15,110,86,0.08) 0%, transparent 70%)' }} />
      </div>

      <div style={{ position:'relative', zIndex:1, maxWidth:680, margin:'0 auto', ...fadeUp(visible) }}>
        <p style={{ fontSize:11, fontWeight:700, color:'rgba(255,255,255,0.3)',
          textTransform:'uppercase', letterSpacing:'0.18em', margin:'0 0 14px',
          fontFamily:'Inter,system-ui' }}>🇳🇬 &nbsp; Open Science</p>
        <h2 style={{ fontFamily:'"Bricolage Grotesque", system-ui', fontWeight:800,
          fontSize:'clamp(36px,5vw,64px)', color:'white',
          letterSpacing:'-0.04em', lineHeight:1.05, margin:'0 0 24px' }}>
          Nigeria deserves causal intelligence,{' '}
          <span style={{ color:'#F59E0B' }}>not more correlations.</span>
        </h2>
        <p style={{ fontSize:17, color:'rgba(255,255,255,0.45)', lineHeight:1.8,
          margin:'0 0 32px', fontFamily:'Inter,system-ui' }}>
          Àlááfíà is open source, locally run, and built for every researcher,
          policymaker, and health innovator working to improve Nigerian health outcomes.
        </p>
        <div style={{ display:'flex', gap:14, justifyContent:'center', flexWrap:'wrap' }}>
          <button onClick={onRequestAccess} style={{
            background:'#F59E0B', color:'#050A06', border:'none',
            borderRadius:100, padding:'0 40px', height:56,
            fontSize:16, fontWeight:700, cursor:'pointer',
            fontFamily:'"Bricolage Grotesque", system-ui',
            boxShadow:'0 0 40px rgba(245,158,11,0.3)',
            transition:'transform 0.25s ease, box-shadow 0.25s ease',
            letterSpacing:'-0.01em',
          }}
          onMouseEnter={e => { e.currentTarget.style.transform='translateY(-3px)'; e.currentTarget.style.boxShadow='0 16px 48px rgba(245,158,11,0.45)'; }}
          onMouseLeave={e => { e.currentTarget.style.transform='translateY(0)'; e.currentTarget.style.boxShadow='0 0 40px rgba(245,158,11,0.3)'; }}>
            Request Access
          </button>
          <a href="https://github.com/anthoniooladimeji11-coder/Alaafia"
            target="_blank" rel="noopener noreferrer"
            style={{
              background:'transparent', color:'rgba(255,255,255,0.7)',
              border:'1px solid rgba(255,255,255,0.15)', borderRadius:100,
              padding:'0 32px', height:56, fontSize:15, fontWeight:500,
              cursor:'pointer', fontFamily:'Inter, system-ui',
              textDecoration:'none', display:'inline-flex', alignItems:'center', gap:8,
              transition:'border-color 0.25s ease, color 0.25s ease, transform 0.25s ease',
            }}
            onMouseEnter={e => { e.currentTarget.style.borderColor='rgba(255,255,255,0.4)'; e.currentTarget.style.color='white'; e.currentTarget.style.transform='translateY(-2px)'; }}
            onMouseLeave={e => { e.currentTarget.style.borderColor='rgba(255,255,255,0.15)'; e.currentTarget.style.color='rgba(255,255,255,0.7)'; e.currentTarget.style.transform='translateY(0)'; }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
            </svg>
            View on GitHub
          </a>
          <button onClick={() => onNavigate('contact')} style={{
            background:'transparent', color:'rgba(255,255,255,0.55)',
            border:'1px solid rgba(255,255,255,0.1)', borderRadius:100,
            padding:'0 28px', height:56, fontSize:15, fontWeight:400,
            cursor:'pointer', fontFamily:'Inter, system-ui',
            transition:'border-color 0.25s ease, color 0.25s ease',
          }}
          onMouseEnter={e => { e.currentTarget.style.borderColor='rgba(255,255,255,0.3)'; e.currentTarget.style.color='rgba(255,255,255,0.85)'; }}
          onMouseLeave={e => { e.currentTarget.style.borderColor='rgba(255,255,255,0.1)'; e.currentTarget.style.color='rgba(255,255,255,0.55)'; }}>
            Partner with Ìyàwó
          </button>
        </div>
        <p style={{ fontSize:12, color:'rgba(255,255,255,0.2)', marginTop:28,
          fontFamily:'Inter,system-ui', letterSpacing:'0.04em' }}>
          Built by Anthonio Oladimeji &nbsp;·&nbsp; University of Ibadan &nbsp;·&nbsp; Open science
        </p>
      </div>
    </section>
  );
}

/* ----------------------------------------------------------------
   PAGE
---------------------------------------------------------------- */
export default function AlaafiaPage({ onNavigate }) {
  const [modalOpen,       setModalOpen]       = useState(false);
  const [selectedZone,    setSelectedZone]    = useState('SE');
  const [selectedOutcome, setSelectedOutcome] = useState('anaemia');
  const [liveData,        setLiveData]        = useState(null);
  const [dataLoading,     setDataLoading]     = useState(true);
  const [geoMode,         setGeoMode]         = useState('zone');
  const [selectedState,   setSelectedState]   = useState(null);
  const [statesData,      setStatesData]      = useState(null);
  const [statesLoading,   setStatesLoading]   = useState(false);

  useEffect(() => {
    fetch(`${API_BASE}/api/alaafia/precomputed`)
      .then(r => r.ok ? r.json() : Promise.reject())
      .then(d => { setLiveData(d); setDataLoading(false); })
      .catch(() => setDataLoading(false));
  }, []);

  useEffect(() => {
    if (geoMode !== 'state' || statesData !== null || statesLoading) return;
    setStatesLoading(true);
    fetch(`${API_BASE}/api/alaafia/precomputed-states`)
      .then(r => r.ok ? r.json() : Promise.reject())
      .then(d => { setStatesData(d); setStatesLoading(false); })
      .catch(() => setStatesLoading(false));
  }, [geoMode, statesData, statesLoading]);

  const openModal  = () => setModalOpen(true);
  const closeModal = () => setModalOpen(false);

  return (
    <>
      <HeroSection onRequestAccess={openModal} />
      <CausalExplorer
        selectedZone={selectedZone}       setSelectedZone={setSelectedZone}
        selectedOutcome={selectedOutcome} setSelectedOutcome={setSelectedOutcome}
        liveData={liveData}              dataLoading={dataLoading}
        geoMode={geoMode}               setGeoMode={setGeoMode}
        selectedState={selectedState}   setSelectedState={setSelectedState}
        statesData={statesData}         statesLoading={statesLoading}
      />
      <CausalDAGSection
        selectedZone={selectedZone} selectedOutcome={selectedOutcome} liveData={liveData}
        geoMode={geoMode} selectedState={selectedState} statesData={statesData}
      />
      <InversionFinding />
      <HowItWorks />
      <WhoUsesIt />
      <CTASection        onNavigate={onNavigate} onRequestAccess={openModal} />
      <RequestAccessModal open={modalOpen} onClose={closeModal} />
    </>
  );
}
