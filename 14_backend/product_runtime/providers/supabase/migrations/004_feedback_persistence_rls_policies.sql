-- MVP-22: Feedback Persistence RLS Policies
-- Enforce strict data ownership for imported feedback.

ALTER TABLE external_feedback_packets ENABLE ROW LEVEL SECURITY;

-- 1. SELECT Policy: Users see only their own imported feedback.
CREATE POLICY feedback_select_owner_only ON external_feedback_packets
    FOR SELECT
    USING (auth.uid() = owner_user_id);

-- 2. INSERT Policy: Users can only import feedback for themselves.
CREATE POLICY feedback_insert_owner_only ON external_feedback_packets
    FOR INSERT
    WITH CHECK (auth.uid() = owner_user_id);

-- 3. UPDATE/DELETE: FORBIDDEN (Immune to modification after import).
-- No policies created for UPDATE or DELETE means they remain blocked by default RLS behavior.

COMMENT ON POLICY feedback_select_owner_only ON external_feedback_packets IS 'Users are restricted to viewing their own feedback signal.';
COMMENT ON POLICY feedback_insert_owner_only ON external_feedback_packets IS 'Users can only insert feedback where they are the owner.';
