# External Demo Package — After MVP-50

## Purpose
This package provides materials for demonstrating and reviewing The Agent Command Center's controlled command-center readiness architecture. The system is a read-only production-visible dashboard that documents the readiness architecture. Runtime activation has not started.

## Live Site
https://the-agent-command-center-dashboard.netlify.app/

## Package Contents
- executive_demo_one_pager.md — One-page executive summary
- guided_demo_walkthrough_script.md — 10-15 minute guided demo script
- stakeholder_pitch_outline.md — Pitch outlines for different audiences
- demo_talk_track.md — Multi-audience talk tracks
- demo_click_path.md — Exact live site navigation path
- architecture_layer_map.md — Readiness layer architecture map
- safety_boundary_brief.md — Disabled capabilities documentation
- validator_confidence_brief.md — Validation and testing confidence
- release_readiness_summary.md — Readiness verdict and scoring
- runtime_activation_separation_memo.md — Runtime activation as separate phase
- stakeholder_faq.md — Frequently asked questions (15+ entries)
- demo_screenshot_capture_list.md — Screenshots to capture
- demo_readiness_checklist.md — Pre-demo verification checklist
- external_reviewer_notes_template.md — Structured reviewer notes template
- demo_package_manifest.json — Machine-readable package metadata

## Recommended Demo Order
1. Start with executive_demo_one_pager.md for context
2. Follow demo_click_path.md through the live site
3. Use guided_demo_walkthrough_script.md during the walkthrough
4. Reference architecture_layer_map.md for technical depth
5. End with safety_boundary_brief.md and release_readiness_summary.md

## Safety Note
This system is a read-only readiness dashboard. Real execution, public writes, automation, alert sending, rollback execution, and incident mutation remain disabled. The dashboard proves its disabled status through explicit markers, including `NOT_READY_FOR_REAL_AUTOMATION`.

## Runtime Activation Note
Runtime activation is explicitly separated. It has not started. A separate planning phase is required before any runtime enablement. See runtime_activation_separation_memo.md for details.

## Next Step Recommendation
1. Review and merge the demo package branch
2. Use the package to create a stakeholder-facing presentation or guided screen-share script
3. Schedule demos with reviewers
4. Collect feedback using external_reviewer_notes_template.md
5. Plan runtime activation separately — do not begin until explicitly approved
