#!/usr/bin/env node
/*
 * Fetch GA4 portfolio metrics for zonted.com/metrics/.
 * Uses the existing GA4 service account config from the OpenClaw GA4 skill.
 */
const fs = require('fs');
const path = require('path');
const { createRequire } = require('module');

const GA4_SKILL_DIR = '/Users/psy/.openclaw/workspace/skills/ga4-analytics/scripts';
const skillRequire = createRequire(path.join(GA4_SKILL_DIR, 'package.json'));
const dotenv = skillRequire('dotenv');
const { BetaAnalyticsDataClient } = skillRequire('@google-analytics/data');

dotenv.config({ path: path.join(GA4_SKILL_DIR, '..', '.env') });

const PROPERTIES = [
  { key: 'tabiji', name: 'Tabiji', domain: 'tabiji.ai', id: '524076952', color: '#2a7a2a' },
  { key: 'veracityapi', name: 'VeracityAPI', domain: 'veracityapi.com', id: '537020430', color: '#336699' },
  { key: 'palmaura', name: 'Palmaura', domain: 'palmaura.app', id: '538073800', color: '#8a5a20' },
  { key: 'zonted', name: 'Zonted', domain: 'zonted.com', id: '532496138', color: '#6f4aa8' },
];

function fmtDate(d) {
  return d.toISOString().slice(0, 10).replace(/-/g, '');
}

function labelFromYmd(s) {
  const d = new Date(`${s.slice(0, 4)}-${s.slice(4, 6)}-${s.slice(6, 8)}T12:00:00`);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

async function run() {
  const keyPath = path.join(process.env.HOME || '/Users/psy', '.secrets', 'ga4-private-key.pem');
  const key = fs.existsSync(keyPath)
    ? fs.readFileSync(keyPath, 'utf8').trim()
    : (process.env.GA4_PRIVATE_KEY || '').replace(/\\n/g, '\n');

  if (!process.env.GA4_CLIENT_EMAIL || !key) {
    throw new Error('Missing GA4_CLIENT_EMAIL or private key');
  }

  const client = new BetaAnalyticsDataClient({
    credentials: { client_email: process.env.GA4_CLIENT_EMAIL, private_key: key },
  });

  const end = new Date();
  end.setHours(12, 0, 0, 0);
  const start = new Date(end);
  start.setDate(start.getDate() - 89);
  const ymds = [];
  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) ymds.push(fmtDate(d));

  const output = {
    updatedIso: new Date().toISOString(),
    updatedLabel: new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }),
    rangeLabel: 'Last 90 days',
    labels: ymds.map(labelFromYmd),
    properties: [],
  };

  for (const property of PROPERTIES) {
    const [daily] = await client.runReport({
      property: `properties/${property.id}`,
      dateRanges: [{ startDate: '89daysAgo', endDate: 'today' }],
      dimensions: [{ name: 'date' }],
      metrics: [{ name: 'sessions' }],
      orderBys: [{ dimension: { dimensionName: 'date' } }],
    });

    const byDate = Object.fromEntries(ymds.map((d) => [d, 0]));
    for (const row of daily.rows || []) {
      byDate[row.dimensionValues[0].value] = Number(row.metricValues[0].value || 0);
    }

    const [aggregate] = await client.runReport({
      property: `properties/${property.id}`,
      dateRanges: [{ startDate: '89daysAgo', endDate: 'today' }],
      metrics: [
        { name: 'sessions' },
        { name: 'activeUsers' },
        { name: 'screenPageViews' },
        { name: 'averageSessionDuration' },
        { name: 'engagementRate' },
      ],
    });
    const totals = aggregate.rows?.[0]?.metricValues?.map((v) => Number(v.value || 0)) || [0, 0, 0, 0, 0];

    const [sources] = await client.runReport({
      property: `properties/${property.id}`,
      dateRanges: [{ startDate: '89daysAgo', endDate: 'today' }],
      dimensions: [{ name: 'sessionSourceMedium' }],
      metrics: [{ name: 'sessions' }],
      orderBys: [{ metric: { metricName: 'sessions' }, desc: true }],
      limit: 5,
    });

    output.properties.push({
      ...property,
      totals: {
        sessions: totals[0],
        users: totals[1],
        views: totals[2],
        avgDuration: totals[3],
        engagementRate: totals[4],
      },
      series: ymds.map((d) => byDate[d]),
      sources: (sources.rows || []).map((row) => ({
        sourceMedium: row.dimensionValues[0].value || '(not set)',
        sessions: Number(row.metricValues[0].value || 0),
      })),
    });
  }

  output.properties.sort((a, b) => b.totals.sessions - a.totals.sessions);
  process.stdout.write(JSON.stringify(output, null, 2));
}

run().catch((err) => {
  console.error(err && err.stack ? err.stack : String(err));
  process.exit(1);
});
