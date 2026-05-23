const fs = require('fs');
const path = require('path');

const functionsDir = path.join(__dirname, 'netlify', 'functions');

const baseContent = (name, innerCode, method = 'POST') => `
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

  if (event.httpMethod !== '${method}') {
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
    ${innerCode}
  } catch (err) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: err.message })
    };
  }
};
`;

const listFleetLoadTestsInner = `
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
`;

const startFleetLoadTestInner = `
    const body = JSON.parse(event.body);
    const { test_name, simulated_agent_count, simulated_department_count, actor, reason } = body;

    const { data, error } = await supabase.rpc('start_fleet_load_test', {
      p_test_name: test_name,
      p_simulated_agent_count: parseInt(simulated_agent_count, 10),
      p_simulated_department_count: parseInt(simulated_department_count, 10),
      p_actor: actor || 'system',
      p_reason: reason || 'Start load test'
    });

    if (error) throw error;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true, load_test_id: data })
    };
`;

const pauseFleetLoadTestInner = `
    const body = JSON.parse(event.body);
    const { load_test_id, actor, reason } = body;

    const { error } = await supabase.rpc('pause_fleet_load_test', {
      p_load_test_id: load_test_id,
      p_actor: actor || 'system',
      p_reason: reason || 'Pause load test'
    });

    if (error) throw error;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true })
    };
`;

const completeFleetLoadTestInner = `
    const body = JSON.parse(event.body);
    const { load_test_id, actor, reason } = body;

    const { error } = await supabase.rpc('complete_fleet_load_test', {
      p_load_test_id: load_test_id,
      p_actor: actor || 'system',
      p_reason: reason || 'Complete load test'
    });

    if (error) throw error;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true })
    };
`;

const simulateFleetFailureInner = `
    const body = JSON.parse(event.body);
    const { load_test_id, scenario_id, actor, details } = body;

    const { error } = await supabase.rpc('simulate_fleet_failure', {
      p_load_test_id: load_test_id,
      p_scenario_id: scenario_id,
      p_actor: actor || 'system',
      p_details: details || {}
    });

    if (error) throw error;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true })
    };
`;

const triggerRecoveryDrillInner = `
    const body = JSON.parse(event.body);
    const { load_test_id, scenario_id, actor, recovery_action } = body;

    const { data, error } = await supabase.rpc('trigger_recovery_drill', {
      p_load_test_id: load_test_id,
      p_scenario_id: scenario_id,
      p_actor: actor || 'system',
      p_recovery_action: recovery_action || 'Execute recovery protocol'
    });

    if (error) throw error;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true, drill_id: data })
    };
`;

const verifyRecoveryDrillInner = `
    const body = JSON.parse(event.body);
    const { drill_id, actor, reason } = body;

    const { error } = await supabase.rpc('verify_recovery_drill', {
      p_drill_id: drill_id,
      p_actor: actor || 'system',
      p_reason: reason || 'Verify safe state restored'
    });

    if (error) throw error;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true })
    };
`;

const fleetLoadTestRollupInner = `
    const { data, error } = await supabase.from('runtime_fleet_load_test_rollups')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(1);

    if (error) throw error;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ rollup: data && data.length > 0 ? data[0] : null })
    };
`;

const exportFleetLoadTestReportInner = `
    const body = JSON.parse(event.body);
    const { load_test_id, actor } = body;

    const { data, error } = await supabase.rpc('export_fleet_load_test_report', {
      p_load_test_id: load_test_id,
      p_actor: actor || 'system'
    });

    if (error) throw error;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true, report: data })
    };
`;

const files = {
    'list-fleet-load-tests.js': { code: listFleetLoadTestsInner, method: 'GET' },
    'start-fleet-load-test.js': { code: startFleetLoadTestInner },
    'pause-fleet-load-test.js': { code: pauseFleetLoadTestInner },
    'complete-fleet-load-test.js': { code: completeFleetLoadTestInner },
    'simulate-fleet-failure.js': { code: simulateFleetFailureInner },
    'trigger-recovery-drill.js': { code: triggerRecoveryDrillInner },
    'verify-recovery-drill.js': { code: verifyRecoveryDrillInner },
    'fleet-load-test-rollup.js': { code: fleetLoadTestRollupInner, method: 'GET' },
    'export-fleet-load-test-report.js': { code: exportFleetLoadTestReportInner }
};

for (const [name, config] of Object.entries(files)) {
    const filePath = path.join(functionsDir, name);
    fs.writeFileSync(filePath, baseContent(name, config.code, config.method));
    console.log('Created ' + filePath);
}
