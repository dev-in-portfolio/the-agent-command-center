# MVP-21 — Feedback Schema Review Report

## Status
DEFINED

## Verdict
PASS

## Proposed Schema
- **Table:** `external_feedback_packets`
- **Fields:** id, owner_user_id, reviewer_persona, context, ratings (clarity, confidence, demo, pitch), text (strongest, confusing, blockers, trust), suggested_next_step, would_share, timestamps.
- **Constraints:** `owner_user_id` NOT NULL, references `auth.users(id)`.

## Result
The proposed schema captures all required feedback signal while maintaining strict data ownership.
