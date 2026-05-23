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

const enterprisePilotPacketInner = `
    if (event.httpMethod === 'POST') {
        const body = JSON.parse(event.body || '{}');
        const { actor } = body;
        
        const { data, error } = await supabase.rpc('create_enterprise_pilot_packet', {
            p_actor: actor || 'pilot_packet_exporter'
        });
        if (error) throw error;
        
        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({ success: true, packet_id: data })
        };
    } else {
        const { data, error } = await supabase.from('enterprise_pilot_packets')
            .select('*, sections:enterprise_pilot_packet_sections(*), notes:enterprise_pilot_packet_review_notes(*)')
            .order('created_at', { ascending: false })
            .limit(1);
            
        if (error) throw error;
        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({ packet: data && data.length > 0 ? data[0] : null })
        };
    }
`;

const exportEnterprisePilotPacketInner = `
    const body = JSON.parse(event.body);
    const { packet_id, export_format, actor } = body;

    const { data, error } = await supabase.rpc('export_enterprise_pilot_packet', {
      p_packet_id: packet_id,
      p_export_format: export_format || 'json',
      p_actor: actor || 'pilot_packet_exporter'
    });

    if (error) throw error;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true, export_data: data })
    };
`;

const createPilotPacketReviewNoteInner = `
    const body = JSON.parse(event.body);
    const { packet_id, reviewer_role, note_body, actor } = body;

    const { data, error } = await supabase.rpc('create_pilot_packet_review_note', {
      p_packet_id: packet_id,
      p_reviewer_role: reviewer_role,
      p_note_body: note_body,
      p_actor: actor || 'pilot_reviewer'
    });

    if (error) throw error;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true, note_id: data })
    };
`;


const files = {
    'enterprise-pilot-packet.js': { code: enterprisePilotPacketInner, method: 'POST' },
    'export-enterprise-pilot-packet.js': { code: exportEnterprisePilotPacketInner },
    'create-pilot-packet-review-note.js': { code: createPilotPacketReviewNoteInner }
};

for (const [name, config] of Object.entries(files)) {
    const filePath = path.join(functionsDir, name);
    fs.writeFileSync(filePath, baseContent(name, config.code, config.method));
    console.log('Created ' + filePath);
}
