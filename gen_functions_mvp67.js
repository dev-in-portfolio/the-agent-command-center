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

const enterprisePilotRoomSnapshotInner = `
    if (event.httpMethod === 'POST') {
        const body = JSON.parse(event.body || '{}');
        const { actor } = body;
        
        const { data, error } = await supabase.rpc('create_enterprise_pilot_snapshot', {
            p_actor: actor || 'pilot_viewer'
        });
        if (error) throw error;
        
        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({ success: true, snapshot_id: data })
        };
    } else {
        const { data, error } = await supabase.from('enterprise_pilot_snapshots')
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

const enterprisePilotRoomPackageInner = `
    const [roles, criteria, risks, decisions] = await Promise.all([
      supabase.from('enterprise_pilot_stakeholder_roles').select('*').order('sort_order', { ascending: true }),
      supabase.from('enterprise_pilot_success_criteria').select('*'),
      supabase.from('enterprise_pilot_risk_register').select('*'),
      supabase.from('enterprise_pilot_decision_log').select('*').order('created_at', { ascending: false })
    ]);

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        roles: roles.data,
        criteria: criteria.data,
        risks: risks.data,
        decisions: decisions.data
      })
    };
`;

const createEnterprisePilotNoteInner = `
    const body = JSON.parse(event.body);
    const { snapshot_id, reviewer_role, note_body, actor, note_type } = body;

    const { data, error } = await supabase.rpc('create_enterprise_pilot_note', {
      p_snapshot_id: snapshot_id,
      p_reviewer_role: reviewer_role,
      p_note_body: note_body,
      p_actor: actor || 'pilot_viewer',
      p_note_type: note_type || 'review_note'
    });

    if (error) throw error;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true, note_id: data })
    };
`;

const createEnterprisePilotDecisionInner = `
    const body = JSON.parse(event.body);
    const { snapshot_id, decision_status, decision_summary, actor, decision_type } = body;

    const { data, error } = await supabase.rpc('create_enterprise_pilot_decision', {
      p_snapshot_id: snapshot_id,
      p_decision_status: decision_status,
      p_decision_summary: decision_summary,
      p_actor: actor || 'decision_maker',
      p_decision_type: decision_type || 'pilot_decision'
    });

    if (error) throw error;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true, decision_id: data })
    };
`;

const exportEnterprisePilotReportInner = `
    const body = JSON.parse(event.body);
    const { snapshot_id, actor } = body;

    const { data, error } = await supabase.rpc('export_enterprise_pilot_report', {
      p_snapshot_id: snapshot_id,
      p_actor: actor || 'pilot_viewer'
    });

    if (error) throw error;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true, report: data })
    };
`;


const files = {
    'enterprise-pilot-room-snapshot.js': { code: enterprisePilotRoomSnapshotInner, method: 'POST' },
    'enterprise-pilot-room-package.js': { code: enterprisePilotRoomPackageInner, method: 'GET' },
    'create-enterprise-pilot-note.js': { code: createEnterprisePilotNoteInner },
    'create-enterprise-pilot-decision.js': { code: createEnterprisePilotDecisionInner },
    'export-enterprise-pilot-report.js': { code: exportEnterprisePilotReportInner }
};

for (const [name, config] of Object.entries(files)) {
    const filePath = path.join(functionsDir, name);
    fs.writeFileSync(filePath, baseContent(name, config.code, config.method));
    console.log('Created ' + filePath);
}
