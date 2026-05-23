
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

  if (event.httpMethod !== 'GET' && event.httpMethod !== 'GET') {
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

  } catch (err) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: err.message })
    };
  }
};
