# MVP-40 — Reviewer Response Schema Proposal

## Status
READINESS_ONLY — Schema proposed for future implementation. No capture enabled.

## Proposed Response Categories
1. Feature Request — New capability or enhancement suggested by reviewer
2. Bug Report — Issue or defect identified during demo
3. Usability Feedback — Comments on user experience and interface
4. Documentation Note — Missing or unclear documentation
5. General Comment — Other feedback not fitting above categories

## Proposed Response Fields
- reviewer_name (text, optional)
- response_category (enum from categories above)
- response_text (text, required)
- response_timestamp (datetime, auto)
- demo_session_id (uuid, reference)
- reviewer_packet_id (uuid, reference)
- operator_notes (text, optional, operator-only)

## Status
Schema is a readiness proposal only. No intake endpoint exists. No capture is enabled.
