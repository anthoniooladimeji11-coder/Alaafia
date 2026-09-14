'use strict';

const express    = require('express');
const { spawn }  = require('child_process');
const fs         = require('fs');
const path       = require('path');
const crypto     = require('crypto');
const apiKeyAuth = require('../middleware/apiKeyAuth');

const router = express.Router();

// The causal pipeline (agents/, utils/, scripts/) now lives in this same repo,
// one level above backend/. Override with PIPELINE_PATH if it is checked out
// elsewhere. Historically this was hardcoded to a laptop path; the /analyse
// route only works where the Python pipeline + its deps are actually present.
const PIPELINE_PATH = process.env.PIPELINE_PATH || path.resolve(__dirname, '../../..');
const RESULTS_STORE = process.env.ALAAFIA_RESULTS_STORE || `${PIPELINE_PATH}/outputs/results_store.json`;
const JOBS_STORE = process.env.ALAAFIA_JOBS_STORE || '/tmp/alaafia_jobs.json';

const STATE_MAP = {
  1:'Sokoto', 2:'Zamfara', 3:'Katsina', 4:'Jigawa',
  5:'Yobe', 6:'Borno', 7:'Adamawa', 8:'Gombe', 9:'Bauchi',
  10:'Kano', 11:'Kaduna', 12:'Kebbi', 13:'Niger', 14:'FCT Abuja',
  15:'Nasarawa', 16:'Plateau', 17:'Taraba', 18:'Benue',
  19:'Kogi', 20:'Kwara', 21:'Oyo', 22:'Osun', 23:'Ekiti',
  24:'Ondo', 25:'Edo', 26:'Anambra', 27:'Enugu', 28:'Ebonyi',
  29:'Cross River', 30:'Akwa Ibom', 31:'Abia', 32:'Imo',
  33:'Rivers', 34:'Bayelsa', 35:'Delta', 36:'Lagos', 37:'Ogun',
};

const ZONE_MAP = {
  NC: 'North Central', NE: 'North East', NW: 'North West',
  SE: 'South East', SS: 'South South', SW: 'South West',
};

function readJSON(file) {
  try {
    if (fs.existsSync(file)) return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch(e) {}
  return {};
}

function writeJSON(file, data) {
  fs.writeFileSync(file, JSON.stringify(data, null, 2));
}

function cacheKey(geoType, geoValue, outcome) {
  return crypto.createHash('md5')
    .update(`${geoType}:${geoValue}:${outcome}`.toLowerCase())
    .digest('hex').slice(0, 12);
}

function runPipelineAsync(jobId, geoType, geoValue, outcome) {
  const jobs = readJSON(JOBS_STORE);
  jobs[jobId] = { status: 'running', started: new Date().toISOString() };
  writeJSON(JOBS_STORE, jobs);

  const stateNamesJson = JSON.stringify(
    Object.fromEntries(Object.entries(STATE_MAP).map(([k,v]) => [v, parseInt(k)]))
  );

  const script = `
import sys, json
sys.path.append('${PIPELINE_PATH}')
import pandas as pd
from utils.tokeniser import tokenise_record
from utils.data_filter import load_merged_data, filter_by_geography, get_geography_stats
from agents.causal_agents import run_pipeline
from agents.equity_interrogation import run_equity_interrogation

df = load_merged_data()
geo_type = '${geoType}'
geo_value = '${geoValue}'
outcome = '${outcome}'
state_names = ${stateNamesJson}

state_code = None
zone = None
if geo_type == 'state':
    state_code = state_names.get(geo_value)
elif geo_type == 'zone':
    zone = geo_value

records = filter_by_geography(df, zone=zone, state_code=state_code, outcome=outcome, sample_n=3)
if len(records) == 0:
    print(json.dumps({"error": "no_records_found"}))
    sys.exit(0)

stats = get_geography_stats(df, zone=zone, state_code=state_code)
results = []

for _, row in records.iterrows():
    token = tokenise_record(row)
    result = run_pipeline(token, outcome, zone=zone or geo_value, verbose=False)
    if 'final_pathway' in result.get('final', {}):
        equity = run_equity_interrogation(result)
        results.append({
            'pathway': result['final'].get('final_pathway', ''),
            'policy': result['final'].get('policy_implication', ''),
            'equity': result['final'].get('equity_flag', ''),
            'confidence': result['final'].get('pathway_confidence', 0),
            'quality_grade': result.get('quality', {}).get('quality_grade', ''),
            'quality_score': result.get('quality', {}).get('overall_quality', 0),
            'equity_driver': equity.get('equity_interrogation', {}).get('disparity_primary_driver', ''),
            'beyond_poverty': equity.get('wealth_analysis', {}).get('beyond_poverty_factor', ''),
        })

if not results:
    print(json.dumps({"error": "no_results"}))
    sys.exit(0)

best = max(results, key=lambda r: r.get('quality_score', 0))
print(json.dumps({
    "geography_type": geo_type,
    "geography_value": geo_value,
    "outcome": outcome,
    "stats": stats,
    "result": best,
    "n_records_analysed": len(records),
}))
`;

  const python = spawn('python3', ['-c', script], {
    env: { ...process.env, PYTHONPATH: PIPELINE_PATH },
    detached: false,
  });

  let stdout = '';
  let stderr = '';

  python.stdout.on('data', d => { stdout += d.toString(); });
  python.stderr.on('data', d => { stderr += d.toString(); });

  python.on('close', (code) => {
    const jobs = readJSON(JOBS_STORE);
    if (code !== 0) {
      jobs[jobId] = { status: 'failed', error: stderr.slice(-300), finished: new Date().toISOString() };
      writeJSON(JOBS_STORE, jobs);
      return;
    }
    try {
      const lines = stdout.trim().split('\n');
      const jsonLine = lines.reverse().find(l => l.trim().startsWith('{'));
      const result = JSON.parse(jsonLine);

      if (result.error) {
        jobs[jobId] = { status: 'failed', error: result.error, finished: new Date().toISOString() };
      } else {
        // Cache the result
        const store = readJSON(RESULTS_STORE);
        const key = cacheKey(geoType, geoValue, outcome);
        store[key] = { geography_type: geoType, geography_value: geoValue, outcome, ...result, cached_at: new Date().toISOString() };
        writeJSON(RESULTS_STORE, store);

        jobs[jobId] = { status: 'complete', result, finished: new Date().toISOString() };
      }
    } catch(e) {
      jobs[jobId] = { status: 'failed', error: `Parse error: ${e.message}`, finished: new Date().toISOString() };
    }
    writeJSON(JOBS_STORE, jobs);
    console.log(`[alaafia] job ${jobId} complete`);
  });
}

// ── GET /api/alaafia/outcomes ─────────────────────────────
router.get('/outcomes', (_req, res) => {
  res.json({
    outcomes: ['anaemia','stunting','wasting','underweight','antenatal_care','facility_delivery','contraceptive_use','hiv_testing','child_vaccination','food_insecurity'],
    zones: Object.entries(ZONE_MAP).map(([code, name]) => ({ code, name })),
    states: Object.entries(STATE_MAP).map(([code, name]) => ({ code: parseInt(code), name })),
  });
});

// ── GET /api/alaafia/cached ───────────────────────────────
router.get('/cached', (_req, res) => {
  const store = readJSON(RESULTS_STORE);
  res.json({ total: Object.keys(store).length, results: Object.values(store) });
});

// ── POST /api/alaafia/analyse ─────────────────────────────
// Protected: requires a valid approved API key via Authorization: Bearer <key>
// Returns job ID immediately — pipeline runs in background
router.post('/analyse', apiKeyAuth, (req, res) => {
  const { geography_type, geography_value, outcome } = req.body;

  if (!geography_type || !geography_value || !outcome) {
    return res.status(400).json({ error: 'geography_type, geography_value, and outcome are required' });
  }

  // Check cache first — return instantly
  const store = readJSON(RESULTS_STORE);
  const key = cacheKey(geography_type, geography_value, outcome);
  if (store[key]) {
    console.log(`[alaafia] cache hit: ${geography_value}/${outcome}`);
    return res.json({ source: 'cache', status: 'complete', ...store[key] });
  }

  // Start async job
  const jobId = crypto.randomUUID();
  console.log(`[alaafia] starting job ${jobId}: ${geography_value}/${outcome}`);
  runPipelineAsync(jobId, geography_type, geography_value, outcome);

  res.json({
    source: 'live',
    status: 'running',
    job_id: jobId,
    message: 'Pipeline started. Poll /api/alaafia/job/:id for results.',
    estimated_seconds: 180,
  });
});

// ── GET /api/alaafia/job/:id ──────────────────────────────
// Poll this to check job status
router.get('/job/:id', (req, res) => {
  const jobs = readJSON(JOBS_STORE);
  const job = jobs[req.params.id];
  if (!job) return res.status(404).json({ error: 'job not found' });
  res.json(job);
});

// ── GET /api/alaafia/precomputed ─────────────────────────────
router.get('/precomputed', (_req, res) => {
  const filePath = path.join(__dirname, '../data/alaafia_precomputed.json');
  const data = readJSON(filePath);
  if (!Object.keys(data).length) return res.status(404).json({ error: 'Precomputed data unavailable' });
  res.json(data);
});

// ── GET /api/alaafia/precomputed-states ──────────────────────
router.get('/precomputed-states', (_req, res) => {
  const filePath = path.join(__dirname, '../data/alaafia_precomputed_states.json');
  const data = readJSON(filePath);
  if (!Object.keys(data).length) return res.status(404).json({ error: 'Precomputed states data unavailable' });
  res.json(data);
});

module.exports = router;
