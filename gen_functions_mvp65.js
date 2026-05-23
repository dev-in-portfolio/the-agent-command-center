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

const fullFleetObservabilitySnapshotInner = `
    if (event.httpMethod === 'POST') {
        const body = JSON.parse(event.body || '{}');
        const { actor } = body;
        
        const { data, error } = await supabase.rpc('create_full_fleet_observability_snapshot', {
            p_actor: actor || 'system_observer'
        });
        if (error) throw error;
        
        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({ success: true, snapshot_id: data })
        };
    } else {
        const { data, error } = await supabase.from('runtime_observability_snapshots')
            .select('*')
            .order('created_at', { ascending: false })
            .limit(1);
        if (error) throw error;
        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({ snapshot: data && data.length > 0 ? data[0] : null })
        };
    }
`;

const fullFleetObservabilityEventsInner = `
    const [events, notes, flags] = await Promise.all([
      supabase.from('runtime_observability_events').select('*').order('created_at', { ascending: false }).limit(50),
      supabase.from('runtime_observability_notes').select('*').order('created_at', { ascending: false }).limit(20),
      supabase.from('runtime_observability_state_flags').select('*').order('created_at', { ascending: false })
    ]);

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        events: events.data,
        notes: notes.data,
        flags: flags.data
      })
    };
`;

const createObservabilityNoteInner = `
    const body = JSON.parse(event.body);
    const { snapshot_id, note_body, actor, note_type } = body;

    const { data, error } = await supabase.rpc('create_observability_note', {
      p_snapshot_id: snapshot_id,
      p_note_body: note_body,
      p_actor: actor || 'operator',
      p_note_type: note_type || 'operator_note'
    });

    if (error) throw error;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true, note_id: data })
    };
`;

const exportObservabilityReportInner = `
    const body = JSON.parse(event.body);
    const { snapshot_id, actor } = body;

    const { data, error } = await supabase.rpc('export_observability_report', {
      p_snapshot_id: snapshot_id,
      p_actor: actor || 'operator'
    });

    if (error) throw error;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true, report: data })
    };
`;


const files = {
    'full-fleet-observability-snapshot.js': { code: fullFleetObservabilitySnapshotInner, method: 'POST' }, // Changed to POST here, but the inner code handles GET as well. We'll use a custom wrapper below for dual-method.
    'full-fleet-observability-events.js': { code: fullFleetObservabilityEventsInner, method: 'GET' },
    'create-observability-note.js': { code: createObservabilityNoteInner },
    'export-observability-report.js': { code: exportObservabilityReportInner }
};

// Custom generation for snapshot to allow GET and POST
const snapshotCode = `
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

  if (event.httpMethod !== 'GET' && event.httpMethod !== 'POST') {
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
    ${fullFleetObservabilitySnapshotInner}
  } catch (err) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: err.message })
    };
  }
};
`;

fs.writeFileSync(path.join(functionsDir, 'full-fleet-observability-snapshot.js'), snapshotCode);
console.log('Created ' + path.join(functionsDir, 'full-fleet-observability-snapshot.js'));


for (const [name, config] of Object.entries(files)) {
    if (name === 'full-fleet-observability-snapshot.js') continue;
    const filePath = path.join(functionsDir, name);
    fs.writeFileSync(filePath, baseContent(name, config.code, config.method));
    console.log('Created ' + filePath);
}
