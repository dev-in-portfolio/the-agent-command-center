# Original Phase 5 — Request State Machine

## Status
PLANNING_ONLY

## Purpose
Define the conceptual request state machine for the interactive operator workflow system. States and transitions are display-only — no execution, mutation, or persistence occurs.

## Allowed States

| State | Description | Display Behavior |
|-------|-------------|------------------|
| draft | Initial state after request concept is created | Shows draft label, edit allowed in mock |
| needs_review | Request marked as needing review | Shows needs_review badge |
| review_ready | Request is ready for conceptual review | Shows review_ready badge, approval gate displayed |
| changes_requested | Review indicated changes needed | Shows changes_requested badge |
| approved_for_future_phase | Conceptually approved for future implementation | Shows approved badge, no execution |
| rejected | Request rejected during review | Shows rejected badge, no further transitions |
| cancelled | Request cancelled by operator | Shows cancelled badge, terminal |
| expired | Request expired without action | Shows expired badge, terminal |
| archived | Request archived for reference | Shows archived badge, read-only |

## Forbidden States

| State | Reason |
|-------|--------|
| executing | No execution in Phase 5 |
| deployed | No deployment in Phase 5 |
| merged | No merge in Phase 5 |
| pushed | No push in Phase 5 |
| pr_created | No PR creation in Phase 5 |
| mutation_completed | No mutation in Phase 5 |

These forbidden states must never appear in any Phase 5 display model or prototype.

## Transition Table

| From | To | Condition | Notes |
|------|----|-----------|-------|
| draft | needs_review | Operator marks needs review | Display only |
| draft | cancelled | Operator cancels | Terminal |
| needs_review | review_ready | Operator confirms review ready | Display only |
| needs_review | changes_requested | Changes requested during review | Display only |
| needs_review | rejected | Rejected during review | Terminal |
| needs_review | cancelled | Operator cancels | Terminal |
| review_ready | approved_for_future_phase | Display approval gate passed | No execution |
| review_ready | changes_requested | Review requests changes | Display only |
| review_ready | rejected | Rejected during final review | Terminal |
| review_ready | cancelled | Operator cancels | Terminal |
| changes_requested | draft | Operator revises request | Display only |
| changes_requested | cancelled | Operator cancels | Terminal |
| approved_for_future_phase | archived | Archived after review | Terminal |
| approved_for_future_phase | expired | No action taken | Terminal |
| rejected | archived | Archived for reference | Terminal |
| cancelled | archived | Archived for reference | Terminal |
| expired | archived | Archived for reference | Terminal |

## Forbidden Transitions

| From | To | Reason |
|------|----|--------|
| any | executing | Phase 5 does not enable execution |
| any | deployed | Phase 5 does not enable deployment |
| any | merged | Phase 5 does not enable merge |
| any | pushed | Phase 5 does not enable push |
| any | pr_created | Phase 5 does not enable PR creation |
| any | mutation_completed | Phase 5 does not enable mutation |

## State Machine Rules
1. All states are display-only
2. No state transition triggers any external system call
3. No state transition triggers any execution, mutation, deploy, merge, push, or PR
4. No state is persisted without future storage dependency
5. Forbidden states must never appear in any Phase 5 display
6. Transitions to forbidden states must never be represented even as disabled options
