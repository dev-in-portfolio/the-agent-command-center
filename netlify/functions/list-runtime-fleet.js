
const { createClient } = require('@supabase/supabase-js');

exports.handler = async (event) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers, body: '' };
  }

  if (event.httpMethod !== 'GET') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  }

  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!supabaseUrl || !supabaseKey) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: 'Server configuration error' })
    };
  }

  const supabase = createClient(supabaseUrl, supabaseKey);

  try {
    
    const [limits, stages, cohorts, circuitBreakers, rollups, events, coverage] = await Promise.all([
      supabase.from('runtime_fleet_limits').select('*'),
      supabase.from('runtime_fleet_stages').select('*').order('stage_cap', { ascending: true }),
      supabase.from('runtime_fleet_cohorts').select('*').order('created_at', { ascending: false }),
      supabase.from('runtime_fleet_circuit_breakers').select('*').order('created_at', { ascending: false }),
      supabase.from('runtime_fleet_health_rollups').select('*').order('created_at', { ascending: false }).limit(10),
      supabase.from('runtime_fleet_events').select('*').order('created_at', { ascending: false }).limit(20),
      supabase.from('runtime_fleet_department_coverage').select('*, runtime_departments(*)').order('created_at', { ascending: false })
    ]);

    let active_count = 0;
    if (cohorts.data) {
        active_count = cohorts.data.reduce((acc, c) => {
            return c.cohort_status === 'active' ? acc + c.activated_agent_count : acc;
        }, 0);
    }

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        limits: limits.data,
        stages: stages.data,
        current_cap: 47979,
        active_count: active_count,
        cohorts: cohorts.data,
        circuit_breakers: circuitBreakers.data,
        rollups: rollups.data,
        events: events.data,
        department_coverage: coverage.data
      })
    };

  } catch (err) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: err.message })
    };
  }
};
