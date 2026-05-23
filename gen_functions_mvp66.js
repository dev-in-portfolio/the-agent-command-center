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

  if (event.httpMethod !== '${method}' && event.httpMethod !== 'GET') {
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

const executiveControlRoomSnapshotInner = `
    if (event.httpMethod === 'POST') {
        const body = JSON.parse(event.body || '{}');
        const { mode, actor } = body;
        
        const { data, error } = await supabase.rpc('create_executive_control_room_snapshot', {
            p_mode: mode || 'executive',
            p_actor: actor || 'executive_viewer'
        });
        if (error) throw error;
        
        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({ success: true, snapshot_id: data })
        };
    } else {
        const { mode } = event.queryStringParameters || {};
        let query = supabase.from('runtime_executive_control_room_snapshots')
            .select('*')
            .order('created_at', { ascending: false });
            
        if (mode) {
            query = query.eq('selected_mode', mode);
        }
        
        const { data, error } = await query.limit(1);
        
        if (error) throw error;
        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({ snapshot: data && data.length > 0 ? data[0] : null })
        };
    }
`;

const executiveControlRoomModeInner = `
    const { mode } = event.queryStringParameters || { mode: 'executive' };
    
    const { data, error } = await supabase.from('runtime_executive_review_questions')
        .select('*')
        .eq('reviewer_mode', mode)
        .eq('enabled', true)
        .order('sort_order', { ascending: true });

    if (error) throw error;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        mode: mode,
        questions: data
      })
    };
`;

const createExecutiveControlRoomNoteInner = `
    const body = JSON.parse(event.body);
    const { snapshot_id, reviewer_mode, note_body, actor, note_type } = body;

    const { data, error } = await supabase.rpc('create_executive_control_room_note', {
      p_snapshot_id: snapshot_id,
      p_reviewer_mode: reviewer_mode || 'executive',
      p_note_body: note_body,
      p_actor: actor || 'operator',
      p_note_type: note_type || 'review_note'
    });

    if (error) throw error;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true, note_id: data })
    };
`;

const exportExecutiveControlRoomReportInner = `
    const body = JSON.parse(event.body);
    const { snapshot_id, actor } = body;

    const { data, error } = await supabase.rpc('export_executive_control_room_report', {
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
    'executive-control-room-snapshot.js': { code: executiveControlRoomSnapshotInner, method: 'POST' },
    'executive-control-room-mode.js': { code: executiveControlRoomModeInner, method: 'GET' },
    'create-executive-control-room-note.js': { code: createExecutiveControlRoomNoteInner },
    'export-executive-control-room-report.js': { code: exportExecutiveControlRoomReportInner }
};

for (const [name, config] of Object.entries(files)) {
    const filePath = path.join(functionsDir, name);
    fs.writeFileSync(filePath, baseContent(name, config.code, config.method));
    console.log('Created ' + filePath);
}
