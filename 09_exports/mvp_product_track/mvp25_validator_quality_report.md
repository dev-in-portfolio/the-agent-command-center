# MVP-25

- AUTHENTICATED_FEEDBACK_REVIEW_INBOX_READY
- PASS_WITH_OWNER_SCOPED_READ_ONLY_FEEDBACK_REVIEW
- FEEDBACK_LIST_READ_API_READY
- FEEDBACK_DETAIL_READ_API_READY
- OWNER_SCOPED_RLS_READS
- READ_ONLY_REVIEW_WORKFLOW
- SERVICE_ROLE_NOT_USED
- UPDATE_DELETE_EXECUTE_BLOCKED
- NOT_READY_FOR_REAL_AUTOMATION
- NEXT_STEP_BUILD_FEEDBACK_SYNTHESIS_AND_PRODUCT_DECISION_WORKFLOW

## Direct Supabase Fetch Regression Fix

- MVP-25 direct validator now fails on executable browser/dashboard Supabase fetches.
- MVP-25 direct validator now blocks fetch/axios/XMLHttpRequest access to supabase.co.
- MVP-25 direct validator now blocks createClient and supabase.createClient in dashboard/browser runtime.
- Safety-label text does not suppress executable Supabase scanning.
- E2E validator now requires the direct validator to contain Supabase executable-pattern checks.
