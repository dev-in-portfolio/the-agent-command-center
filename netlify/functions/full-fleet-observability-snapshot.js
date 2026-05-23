
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

  } catch (err) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: err.message })
    };
  }
};
