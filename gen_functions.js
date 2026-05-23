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

const listRuntimeFleetInner = `
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
`;

const unlockStageInner = `
    const body = JSON.parse(event.body);
    const { stage_id, actor, reason } = body;

    const { error } = await supabase.rpc('unlock_runtime_fleet_stage', {
      p_stage_id: stage_id,
      p_actor: actor || 'system',
      p_reason: reason || 'Manual unlock'
    });

    if (error) throw error;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true })
    };
`;

const activateCohortInner = `
    const body = JSON.parse(event.body);
    const { department_id, requested_agent_count, actor, reason } = body;

    const { data, error } = await supabase.rpc('activate_runtime_fleet_cohort', {
      p_department_id: department_id,
      p_requested_agent_count: parseInt(requested_agent_count, 10),
      p_actor: actor || 'system',
      p_reason: reason || 'Activate cohort'
    });

    if (error) throw error;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true, cohort_id: data })
    };
`;

const deactivateCohortInner = `
    const body = JSON.parse(event.body);
    const { cohort_id, actor, reason } = body;

    const { error } = await supabase.rpc('deactivate_runtime_fleet_cohort', {
      p_cohort_id: cohort_id,
      p_actor: actor || 'system',
      p_reason: reason || 'Deactivate cohort'
    });

    if (error) throw error;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true })
    };
`;

const activateApprovedInner = `
    const body = JSON.parse(event.body);
    const { department_id, requested_agent_count, actor, reason } = body;

    const { data, error } = await supabase.rpc('activate_approved_department_fleet_cohort', {
      p_department_id: department_id,
      p_requested_agent_count: parseInt(requested_agent_count, 10),
      p_actor: actor || 'system',
      p_reason: reason || 'Activate approved cohort'
    });

    if (error) throw error;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true, cohort_id: data })
    };
`;

const deactivateApprovedInner = `
    const body = JSON.parse(event.body);
    const { department_id, actor, reason } = body;

    const { error } = await supabase.rpc('deactivate_approved_department_fleet_cohort', {
      p_department_id: department_id,
      p_actor: actor || 'system',
      p_reason: reason || 'Deactivate approved cohort'
    });

    if (error) throw error;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true })
    };
`;

const heartbeatInner = `
    const body = JSON.parse(event.body);
    const { actor } = body;

    const { error } = await supabase.from('runtime_fleet_events').insert({
        actor: actor || 'system',
        event_type: 'heartbeat',
        event_summary: 'Fleet heartbeat received',
        event_payload: {}
    });

    if (error) throw error;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true })
    };
`;

const createReadinessNoteInner = `
    const body = JSON.parse(event.body);
    const { actor, note } = body;

    const { error } = await supabase.from('runtime_fleet_events').insert({
        actor: actor || 'system',
        event_type: 'readiness_note',
        event_summary: 'Fleet readiness note: ' + note,
        event_payload: { note }
    });

    if (error) throw error;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true })
    };
`;

const circuitBreakerInner = `
    const body = JSON.parse(event.body);
    const { action, breaker_name, breaker_id, reason, actor } = body;

    if (action === 'trigger') {
        const { error } = await supabase.rpc('trigger_runtime_fleet_circuit_breaker', {
            p_breaker_name: breaker_name,
            p_trigger_reason: reason,
            p_actor: actor || 'system'
        });
        if (error) throw error;
    } else if (action === 'clear') {
        const { error } = await supabase.rpc('clear_runtime_fleet_circuit_breaker', {
            p_breaker_id: breaker_id,
            p_reason: reason,
            p_actor: actor || 'system'
        });
        if (error) throw error;
    }

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true })
    };
`;

const rollupInner = `
    const { data, error } = await supabase.from('runtime_fleet_health_rollups')
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

const killSwitchInner = `
    const body = JSON.parse(event.body);
    const { actor, reason } = body;

    const { error } = await supabase.rpc('runtime_fleet_kill_switch', {
      p_actor: actor || 'system',
      p_reason: reason || 'Manual kill switch activation'
    });

    if (error) throw error;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true })
    };
`;

const files = {
    'list-runtime-fleet.js': { code: listRuntimeFleetInner, method: 'GET' },
    'unlock-runtime-fleet-stage.js': { code: unlockStageInner },
    'activate-runtime-fleet-cohort.js': { code: activateCohortInner },
    'deactivate-runtime-fleet-cohort.js': { code: deactivateCohortInner },
    'activate-approved-department-fleet-cohort.js': { code: activateApprovedInner },
    'deactivate-approved-department-fleet-cohort.js': { code: deactivateApprovedInner },
    'runtime-fleet-heartbeat.js': { code: heartbeatInner },
    'create-runtime-fleet-readiness-note.js': { code: createReadinessNoteInner },
    'runtime-fleet-circuit-breaker.js': { code: circuitBreakerInner },
    'runtime-fleet-rollup.js': { code: rollupInner, method: 'GET' },
    'runtime-fleet-kill-switch.js': { code: killSwitchInner }
};

for (const [name, config] of Object.entries(files)) {
    const filePath = path.join(functionsDir, name);
    fs.writeFileSync(filePath, baseContent(name, config.code, config.method));
    console.log('Created ' + filePath);
}

