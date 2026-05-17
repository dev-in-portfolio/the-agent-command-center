-- MVP-22: Feedback Persistence Schema
-- Table for storing imported reviewer feedback packets.

CREATE TABLE IF NOT EXISTS external_feedback_packets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_user_id UUID NOT NULL REFERENCES auth.users(id),
    reviewer_persona TEXT NOT NULL,
    reviewer_context TEXT,
    clarity_rating INTEGER CHECK (clarity_rating >= 1 AND clarity_rating <= 5),
    confidence_rating INTEGER CHECK (confidence_rating >= 1 AND confidence_rating <= 5),
    demo_readiness_rating INTEGER CHECK (demo_readiness_rating >= 1 AND demo_readiness_rating <= 5),
    pitchability_rating INTEGER CHECK (pitchability_rating >= 1 AND pitchability_rating <= 5),
    strongest_parts TEXT,
    confusing_parts TEXT,
    blockers TEXT,
    trust_concerns TEXT,
    suggested_next_step TEXT,
    would_share BOOLEAN,
    raw_packet JSONB NOT NULL DEFAULT '{}'::jsonB,
    source TEXT NOT NULL DEFAULT 'manual_import',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_feedback_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_feedback_timestamp_trigger
    BEFORE UPDATE ON external_feedback_packets
    FOR EACH ROW
    EXECUTE PROCEDURE update_feedback_timestamp();

COMMENT ON TABLE external_feedback_packets IS 'Controlled authenticated storage for external reviewer signal.';
