function getFeedbackReadClient(bearerToken) {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_ANON_KEY;

  if (!url || !key) {
    throw new Error("Missing Supabase configuration");
  }

  if (!bearerToken) {
    throw new Error("Missing user bearer token for feedback read");
  }

  return {
    url,
    key,
    bearerToken
  };
}

async function runFeedbackReadQuery(client, query) {
  const response = await fetch(query.url, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${client.bearerToken}`,
      apikey: client.key,
      Accept: "application/json"
    }
  });

  if (!response.ok) {
    return {
      success: false,
      status: response.status,
      error: "SUPABASE_READ_FAILED"
    };
  }

  const data = await response.json();
  return { success: true, data };
}

async function listFeedbackPackets(bearerToken) {
  try {
    const client = getFeedbackReadClient(bearerToken);
    const query = new URL("/rest/v1/external_feedback_packets", client.url);
    query.searchParams.set("select", "*");
    query.searchParams.set("order", "created_at.desc");
    return await runFeedbackReadQuery(client, query);
  } catch (err) {
    return { success: false, status: 500, error: "FEEDBACK_LIST_ERROR" };
  }
}

async function getFeedbackPacket(bearerToken, feedbackId) {
  try {
    if (!feedbackId) {
      return { success: false, status: 400, error: "MISSING_FEEDBACK_ID" };
    }
    const client = getFeedbackReadClient(bearerToken);
    const query = new URL("/rest/v1/external_feedback_packets", client.url);
    query.searchParams.set("select", "*");
    query.searchParams.set("id", `eq.${feedbackId}`);
    query.searchParams.set("limit", "1");
    const result = await runFeedbackReadQuery(client, query);

    if (!result.success) {
      return { success: false, status: 404, error: "FEEDBACK_NOT_FOUND" };
    }
    const row = Array.isArray(result.data) ? result.data[0] : result.data;
    if (!row) {
      return { success: false, status: 404, error: "FEEDBACK_NOT_FOUND" };
    }
    return { success: true, data: row };
  } catch (err) {
    return { success: false, status: 500, error: "FEEDBACK_GET_ERROR" };
  }
}

module.exports = {
  listFeedbackPackets,
  getFeedbackPacket
};
