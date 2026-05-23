
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
    
    const [loadTests, scenarios, drills, events, rollups, reports] = await Promise.all([
      supabase.from('runtime_fleet_load_tests').select('*').order('created_at', { ascending: false }),
      supabase.from('runtime_fleet_failure_scenarios').select('*').order('scenario_id', { ascending: true }),
      supabase.from('runtime_fleet_recovery_drills').select('*').order('created_at', { ascending: false }),
      supabase.from('runtime_fleet_load_test_events').select('*').order('created_at', { ascending: false }).limit(50),
      supabase.from('runtime_fleet_load_test_rollups').select('*').order('created_at', { ascending: false }).limit(10),
      supabase.from('runtime_fleet_load_test_reports').select('*').order('generated_at', { ascending: false }).limit(10)
    ]);

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        load_tests: loadTests.data,
        scenarios: scenarios.data,
        drills: drills.data,
        events: events.data,
        rollups: rollups.data,
        reports: reports.data
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
