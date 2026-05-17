const { createClient } = require("@supabase/supabase-js");

function getFeedbackReadClient(bearerToken) {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_ANON_KEY;

  if (!url || !key) {
    throw new Error("Missing Supabase configuration");
  }

  if (!bearerToken) {
    throw new Error("Missing user bearer token for feedback read");
  }

  return createClient(url, key, {
    global: {
      headers: {
        Authorization: `Bearer ${bearerToken}`
      }
    }
  });
}

async function listFeedbackPackets(bearerToken) {
  try {
    const client = getFeedbackReadClient(bearerToken);
    const { data, error } = await client
      .from("external_feedback_packets")
      .select("*")
      .order("created_at", { ascending: false });

    if (error) {
      console.error("List feedback read error", error);
      return { success: false, status: 500, error: "FEEDBACK_LIST_ERROR" };
    }
    return { success: true, data: data };
  } catch (err) {
    console.error("List feedback unexpected error", err);
    return { success: false, status: 500, error: "FEEDBACK_LIST_ERROR" };
  }
}

async function getFeedbackPacket(bearerToken, feedbackId) {
  try {
    if (!feedbackId) {
      return { success: false, status: 400, error: "MISSING_FEEDBACK_ID" };
    }
    const client = getFeedbackReadClient(bearerToken);
    const { data, error } = await client
      .from("external_feedback_packets")
      .select("*")
      .eq("id", feedbackId)
      .single();

    if (error) {
      console.error("Get feedback read error", error);
      return { success: false, status: 404, error: "FEEDBACK_NOT_FOUND" };
    }
    return { success: true, data: data };
  } catch (err) {
    console.error("Get feedback unexpected error", err);
    return { success: false, status: 500, error: "FEEDBACK_GET_ERROR" };
  }
}

module.exports = {
  listFeedbackPackets,
  getFeedbackPacket
};
