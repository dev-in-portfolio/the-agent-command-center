# 47,250-Worker Architecture Blueprint v0.1

## Status
Static design layer only. No workers activated. No live orchestration. No task execution. No API access. No credential access. No deployment access. No production access.

## Purpose
Define the full 47,250-worker template structure for the Agent Command Center without activating workers or connecting external systems.

This is a fixed design-capacity target of 47,250 worker templates. This number represents planned role-template capacity only. It does not mean workers are active, hired, routed, executing tasks, connected to APIs, allowed to use credentials, allowed to deploy, or allowed to touch production.

## Core Doctrine
Workers are not live agents yet. Workers are named role templates, capability profiles, routing targets, permission boundaries, validation targets, and audit objects.

A worker template may describe what a future worker could do, but it must not perform work, call tools, call APIs, read credentials, access secrets, deploy code, or touch production.

## Workforce Structure
- Command Center: the top-level authority and coordination layer.
- Division: a major functional domain grouping multiple departments.
- Department: a focused operating unit within a division.
- Team: a smaller working cluster inside a department.
- Role Family: a reusable template class for similar worker responsibilities.
- Worker Role: a named responsibility profile inside a role family.
- Worker Instance Template: a static record of one future instance derived from a role family.

## Worker Count Target
Target design capacity: 47,250 worker templates.

This target is a static architecture count, not an activation count.

The 47,250-worker design should be organized into reusable role families, departments, teams, and worker-instance templates so the system can eventually support large-scale routing, auditing, validation, and permission management without requiring live worker activation.

## Capacity Model
| Phase | Capacity | Meaning |
| --- | ---: | --- |
| Phase 1 | 500 worker templates | Planning and design only; no activation. |
| Phase 2 | 5,000 worker templates | Planning and design only; no activation. |
| Phase 3 | 25,000 worker templates | Planning and design only; no activation. |
| Phase 4 | 47,250 worker templates | Final static architecture target; still not activation. |

## Major Divisions
### Command and Governance
- purpose: Define direction, guard scope, and coordinate command-level oversight.
- example departments: Command Desk, Scope Office, Policy Office
- example worker roles: Command Router, Scope Guardian, Priority Governor
- permission ceiling: T1
- output types: command briefs, scope rulings, governance logs
- escalation requirements: Escalate any ambiguity affecting scope, authority, or safety.
- safety restrictions: No live task routing., No production access., No self-activation.
- suggested percentage of the 47,250-worker design capacity: 3.1746%
- approximate future worker-template allocation: 1500

### Intake and Interpretation
- purpose: Capture incoming work, normalize requests, and map intent into structured records.
- example departments: Intake Desk, Interpretation Desk, Normalization Desk
- example worker roles: Intake Parser, Intent Interpreter, Request Normalizer
- permission ceiling: T1
- output types: structured intake records, intent summaries, classification notes
- escalation requirements: Escalate missing context, contradictory instructions, or unsafe requests.
- safety restrictions: No direct execution., No credential access., No live routing.
- suggested percentage of the 47,250-worker design capacity: 5.2910%
- approximate future worker-template allocation: 2500

### Planning and Strategy
- purpose: Convert requirements into staged plans, sequences, and strategic options.
- example departments: Planning Office, Strategy Office, Sequencing Office
- example worker roles: Plan Architect, Strategy Synthesizer, Milestone Mapper
- permission ceiling: T1
- output types: plans, roadmaps, decision memos
- escalation requirements: Escalate when tradeoffs change scope, schedule, or risk exposure.
- safety restrictions: No deployment action., No production execution., No API calls.
- suggested percentage of the 47,250-worker design capacity: 6.3492%
- approximate future worker-template allocation: 3000

### Research and Knowledge
- purpose: Collect, organize, and synthesize knowledge into static reference material.
- example departments: Research Desk, Knowledge Desk, Synthesis Desk
- example worker roles: Research Synthesizer, Knowledge Curator, Evidence Mapper
- permission ceiling: T1
- output types: research notes, knowledge briefs, evidence summaries
- escalation requirements: Escalate when source quality, freshness, or reliability is uncertain.
- safety restrictions: No network access., No live system interaction., No secrets.
- suggested percentage of the 47,250-worker design capacity: 9.5238%
- approximate future worker-template allocation: 4500

### Engineering and Build
- purpose: Design code changes, build artifacts, and implementation plans without live execution.
- example departments: Build Office, Implementation Office, Architecture Office
- example worker roles: Code Reviewer, UI Builder, API Boundary Auditor
- permission ceiling: T1
- output types: design specs, patch plans, implementation outlines
- escalation requirements: Escalate changes affecting runtime, deployment, or protected baselines.
- safety restrictions: No live builds., No production touch., No protected baseline mutation.
- suggested percentage of the 47,250-worker design capacity: 12.6984%
- approximate future worker-template allocation: 6000

### QA and Validation
- purpose: Check correctness, regressions, and conformance against static requirements.
- example departments: Validation Desk, Regression Desk, Test Design Desk
- example worker roles: Regression Checker, Validator Writer, Test Matrix Auditor
- permission ceiling: T1
- output types: test plans, validation reports, regression notes
- escalation requirements: Escalate when a defect might affect safety, data integrity, or production risk.
- safety restrictions: No live test execution., No production execution., No API access.
- suggested percentage of the 47,250-worker design capacity: 10.5820%
- approximate future worker-template allocation: 5000

### Documentation and Reporting
- purpose: Produce clear records, reports, and user-facing documentation.
- example departments: Docs Office, Reporting Office, Release Notes Office
- example worker roles: Documentation Formatter, Release Note Curator, Report Assembler
- permission ceiling: T1
- output types: documentation, reports, summaries
- escalation requirements: Escalate when wording could imply activation, authority, or capability that does not exist.
- safety restrictions: No runtime claims., No live worker claims., No secrets.
- suggested percentage of the 47,250-worker design capacity: 7.4074%
- approximate future worker-template allocation: 3500

### Security and Safety
- purpose: Define defensive boundaries, restrictions, and safety checks for the worker blueprint.
- example departments: Safety Office, Boundary Office, Threat Office
- example worker roles: Policy Sentinel, Boundary Auditor, Safety Gatekeeper
- permission ceiling: T1
- output types: safety rules, risk notes, boundary assessments
- escalation requirements: Escalate any condition that could expose secrets, credentials, or production systems.
- safety restrictions: No live access., No credential handling., No secret handling.
- suggested percentage of the 47,250-worker design capacity: 8.4656%
- approximate future worker-template allocation: 4000

### Deployment and Operations
- purpose: Plan operational readiness, release gating, and non-executing deployment support.
- example departments: Operations Office, Release Office, Readiness Office
- example worker roles: Deployment Planner, Rollback Strategist, Operations Curator
- permission ceiling: T1
- output types: readiness plans, rollback notes, operations checklists
- escalation requirements: Escalate any request involving deployment, runtime drift, or production activation.
- safety restrictions: No deployment execution., No live routing., No production approval bypass.
- suggested percentage of the 47,250-worker design capacity: 6.8783%
- approximate future worker-template allocation: 3250

### Business and Product
- purpose: Frame product intent, business goals, and user value in static planning form.
- example departments: Product Office, Business Office, Research Ops
- example worker roles: Product Strategist, Business Analyst, Value Mapper
- permission ceiling: T1
- output types: product briefs, business cases, roadmap inputs
- escalation requirements: Escalate if business objectives conflict with safety, compliance, or capacity limits.
- safety restrictions: No live customer action., No credential use., No production access.
- suggested percentage of the 47,250-worker design capacity: 5.2910%
- approximate future worker-template allocation: 2500

### Creative and Media
- purpose: Develop static creative direction, media concepts, and presentation assets.
- example departments: Creative Studio, Media Studio, Brand Studio
- example worker roles: Creative Concept Builder, Media Layout Designer, Brand Voice Curator
- permission ceiling: T1
- output types: creative briefs, media concepts, presentation assets
- escalation requirements: Escalate when a creative request crosses into live publishing or rights-sensitive use.
- safety restrictions: No live publishing., No protected asset mutation., No production touch.
- suggested percentage of the 47,250-worker design capacity: 5.8201%
- approximate future worker-template allocation: 2750

### Data and Analytics
- purpose: Describe measurement, reporting, and analytic structure without live query access.
- example departments: Analytics Office, Metrics Office, Modeling Office
- example worker roles: Data Analyst, Metric Curator, Insight Synthesizer
- permission ceiling: T1
- output types: analytics plans, metric definitions, trend summaries
- escalation requirements: Escalate any request that implies direct data access, credentialed access, or production telemetry use.
- safety restrictions: No direct database access., No secrets., No live API access.
- suggested percentage of the 47,250-worker design capacity: 7.4074%
- approximate future worker-template allocation: 3500

### User Support and Personalization
- purpose: Draft support patterns, personalization logic, and user assistance guidance.
- example departments: Support Desk, Personalization Desk, Experience Desk
- example worker roles: Support Triage Analyst, Personalization Mapper, Help Flow Curator
- permission ceiling: T1
- output types: support scripts, help articles, personalization guides
- escalation requirements: Escalate when a support response would require live account, credential, or production access.
- safety restrictions: No account access., No credential access., No production execution.
- suggested percentage of the 47,250-worker design capacity: 4.2328%
- approximate future worker-template allocation: 2000

### Compliance and Audit
- purpose: Track policy, compliance, and audit-ready records for the static worker system.
- example departments: Compliance Office, Audit Office, Controls Office
- example worker roles: Compliance Checker, Audit Trail Curator, Control Mapper
- permission ceiling: T1
- output types: compliance notes, audit records, controls mapping
- escalation requirements: Escalate any policy exception, audit failure, or control gap.
- safety restrictions: No live access., No production access., No unauthorized exceptions.
- suggested percentage of the 47,250-worker design capacity: 4.7619%
- approximate future worker-template allocation: 2250

### Experimental Systems Lab
- purpose: Prototype future static structures and sandboxed conceptual variants without activation.
- example departments: Lab Office, Prototype Office, Exploration Office
- example worker roles: Experimental Concept Mapper, Prototype Planner, Variant Curator
- permission ceiling: T1
- output types: prototype specs, experiment notes, variant proposals
- escalation requirements: Escalate any experiment that could be mistaken for live execution or deployment.
- safety restrictions: No live test execution., No production pathway., No self-activation.
- suggested percentage of the 47,250-worker design capacity: 2.1164%
- approximate future worker-template allocation: 1000

## Worker Role Template
Standard worker role object fields:
- worker_role_id
- worker_display_name
- division
- department
- team
- role_family
- role_type
- primary_purpose
- allowed_inputs
- allowed_outputs
- forbidden_actions
- required_context
- required_approvals
- permission_tier
- activation_tier
- audit_level
- escalation_target
- validator_requirements
- failure_mode
- rollback_behavior
- status

## Permission Tiers
| Tier | Name | Live | API | Credentials | Deploy | Production | Future Defined |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T0 | Design-only worker | false | false | false | false | false | false |
| T1 | Local planning worker | false | false | false | false | false | false |
| T2 | Local file drafting worker | false | false | false | false | false | true |
| T3 | Local validation worker | false | false | false | false | false | true |
| T4 | Sandbox execution worker | false | false | false | false | false | true |
| T5 | Supervised tool-use worker | false | false | false | false | false | true |
| T6 | Supervised API-preview worker | false | false | false | false | false | true |
| T7 | Supervised production-candidate worker | false | false | false | false | false | true |
| T8 | Production pilot worker | false | false | false | false | false | true |
| T9 | Locked live worker | false | false | false | false | false | true |

## Activation Tiers
| Tier | Name | Active Worker | Live Routing | Human Approval |
| --- | --- | --- | --- | --- |
| A0 | Not created | false | false | false |
| A1 | Static role template | false | false | false |
| A2 | Registered role template | false | false | true |
| A3 | Simulated dry-run worker | false | false | true |
| A4 | Sandbox worker candidate | false | false | true |
| A5 | Supervised pilot candidate | false | false | true |
| A6 | Human-approved pilot worker | false | false | true |
| A7 | Production-readiness reviewed | false | false | true |
| A8 | Production pilot approved | false | false | true |
| A9 | Live activation approved | false | false | true |

## Audit Levels
| Level | Name | Required For v0.1 |
| --- | --- | --- |
| L0 | Design note only | false |
| L1 | Basic role record | true |
| L2 | Structured capability record | true |
| L3 | Validation-required role record | true |
| L4 | Approval-required role record | false |
| L5 | Full audit trail required | false |

## Worker Status Values
- STATIC_DESIGN_ONLY
- REGISTERED_TEMPLATE_ONLY
- SIMULATION_READY_NOT_ACTIVE
- SANDBOX_CANDIDATE_NOT_ACTIVE
- PILOT_CANDIDATE_NOT_ACTIVE
- BLOCKED_PENDING_APPROVAL
- RETIRED_TEMPLATE

## Starter Worker Role Families
The starter set includes 150 static role families, distributed evenly across the 15 divisions.

### Command Router
- role family id: DIV-01-RF-01
- division: Command and Governance
- department: Command Desk
- purpose: Routes command intent into static governance records.
- allowed outputs: command briefs, governance logs
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Policy Office
- status: STATIC_DESIGN_ONLY

### Scope Guardian
- role family id: DIV-01-RF-02
- division: Command and Governance
- department: Command Desk
- purpose: Protects the scope boundary of the architecture.
- allowed outputs: command briefs, governance logs
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Policy Office
- status: STATIC_DESIGN_ONLY

### Priority Governor
- role family id: DIV-01-RF-03
- division: Command and Governance
- department: Command Desk
- purpose: Ranks work by declared importance and urgency.
- allowed outputs: command briefs, governance logs
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Policy Office
- status: STATIC_DESIGN_ONLY

### Authority Ledger Keeper
- role family id: DIV-01-RF-04
- division: Command and Governance
- department: Command Desk
- purpose: Records authority boundaries and ownership.
- allowed outputs: command briefs, governance logs
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Policy Office
- status: STATIC_DESIGN_ONLY

### Oversight Coordinator
- role family id: DIV-01-RF-05
- division: Command and Governance
- department: Command Desk
- purpose: Coordinates non-executing oversight artifacts.
- allowed outputs: command briefs, governance logs
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L3
- escalation target: Policy Office
- status: STATIC_DESIGN_ONLY

### Policy Sentinel
- role family id: DIV-01-RF-06
- division: Command and Governance
- department: Command Desk
- purpose: Flags policy drift and authority mismatch.
- allowed outputs: command briefs, governance logs
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L1
- escalation target: Policy Office
- status: STATIC_DESIGN_ONLY

### Dispatch Curator
- role family id: DIV-01-RF-07
- division: Command and Governance
- department: Command Desk
- purpose: Curates dispatch rules without routing live work.
- allowed outputs: command briefs, governance logs
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Policy Office
- status: STATIC_DESIGN_ONLY

### Directive Archivist
- role family id: DIV-01-RF-08
- division: Command and Governance
- department: Command Desk
- purpose: Archives command directives as static references.
- allowed outputs: command briefs, governance logs
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Policy Office
- status: STATIC_DESIGN_ONLY

### Consensus Recorder
- role family id: DIV-01-RF-09
- division: Command and Governance
- department: Command Desk
- purpose: Captures agreed decisions for governance review.
- allowed outputs: command briefs, governance logs
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Policy Office
- status: STATIC_DESIGN_ONLY

### Drift Watcher
- role family id: DIV-01-RF-10
- division: Command and Governance
- department: Command Desk
- purpose: Detects divergence between scope and blueprint.
- allowed outputs: command briefs, governance logs
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Policy Office
- status: STATIC_DESIGN_ONLY

### Intake Parser
- role family id: DIV-02-RF-01
- division: Intake and Interpretation
- department: Intake Desk
- purpose: Converts raw requests into structured intake records.
- allowed outputs: structured intake records, classification notes
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Normalization Desk
- status: STATIC_DESIGN_ONLY

### Intent Interpreter
- role family id: DIV-02-RF-02
- division: Intake and Interpretation
- department: Intake Desk
- purpose: Maps human wording to normalized intent.
- allowed outputs: structured intake records, classification notes
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Normalization Desk
- status: STATIC_DESIGN_ONLY

### Request Normalizer
- role family id: DIV-02-RF-03
- division: Intake and Interpretation
- department: Intake Desk
- purpose: Standardizes request fields and phrasing.
- allowed outputs: structured intake records, classification notes
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Normalization Desk
- status: STATIC_DESIGN_ONLY

### Context Collector
- role family id: DIV-02-RF-04
- division: Intake and Interpretation
- department: Intake Desk
- purpose: Collects required context fields for planning.
- allowed outputs: structured intake records, classification notes
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Normalization Desk
- status: STATIC_DESIGN_ONLY

### Clarification Drafter
- role family id: DIV-02-RF-05
- division: Intake and Interpretation
- department: Intake Desk
- purpose: Drafts clarification questions for missing context.
- allowed outputs: structured intake records, classification notes
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L3
- escalation target: Normalization Desk
- status: STATIC_DESIGN_ONLY

### Signal Classifier
- role family id: DIV-02-RF-06
- division: Intake and Interpretation
- department: Intake Desk
- purpose: Classifies request signals into static categories.
- allowed outputs: structured intake records, classification notes
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L1
- escalation target: Normalization Desk
- status: STATIC_DESIGN_ONLY

### Input Sanitizer
- role family id: DIV-02-RF-07
- division: Intake and Interpretation
- department: Intake Desk
- purpose: Normalizes input without executing it.
- allowed outputs: structured intake records, classification notes
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Normalization Desk
- status: STATIC_DESIGN_ONLY

### Brief Extractor
- role family id: DIV-02-RF-08
- division: Intake and Interpretation
- department: Intake Desk
- purpose: Extracts high-signal summary notes.
- allowed outputs: structured intake records, classification notes
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Normalization Desk
- status: STATIC_DESIGN_ONLY

### Scope Tagger
- role family id: DIV-02-RF-09
- division: Intake and Interpretation
- department: Intake Desk
- purpose: Tags requests by scope class and boundary.
- allowed outputs: structured intake records, classification notes
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Normalization Desk
- status: STATIC_DESIGN_ONLY

### Intake Auditor
- role family id: DIV-02-RF-10
- division: Intake and Interpretation
- department: Intake Desk
- purpose: Audits intake completeness and safety notes.
- allowed outputs: structured intake records, classification notes
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Normalization Desk
- status: STATIC_DESIGN_ONLY

### Plan Architect
- role family id: DIV-03-RF-01
- division: Planning and Strategy
- department: Planning Office
- purpose: Builds staged static plans from requirements.
- allowed outputs: plans, decision memos
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Sequencing Office
- status: STATIC_DESIGN_ONLY

### Strategy Synthesizer
- role family id: DIV-03-RF-02
- division: Planning and Strategy
- department: Planning Office
- purpose: Synthesizes strategic options and tradeoffs.
- allowed outputs: plans, decision memos
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Sequencing Office
- status: STATIC_DESIGN_ONLY

### Milestone Mapper
- role family id: DIV-03-RF-03
- division: Planning and Strategy
- department: Planning Office
- purpose: Maps milestones and dependencies.
- allowed outputs: plans, decision memos
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Sequencing Office
- status: STATIC_DESIGN_ONLY

### Sequence Planner
- role family id: DIV-03-RF-04
- division: Planning and Strategy
- department: Planning Office
- purpose: Orders tasks into a rational static sequence.
- allowed outputs: plans, decision memos
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Sequencing Office
- status: STATIC_DESIGN_ONLY

### Tradeoff Curator
- role family id: DIV-03-RF-05
- division: Planning and Strategy
- department: Planning Office
- purpose: Records tradeoff choices for review.
- allowed outputs: plans, decision memos
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L3
- escalation target: Sequencing Office
- status: STATIC_DESIGN_ONLY

### Roadmap Editor
- role family id: DIV-03-RF-06
- division: Planning and Strategy
- department: Planning Office
- purpose: Edits roadmap structure without execution.
- allowed outputs: plans, decision memos
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L1
- escalation target: Sequencing Office
- status: STATIC_DESIGN_ONLY

### Scenario Builder
- role family id: DIV-03-RF-07
- division: Planning and Strategy
- department: Planning Office
- purpose: Frames alternative future scenarios.
- allowed outputs: plans, decision memos
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Sequencing Office
- status: STATIC_DESIGN_ONLY

### Decision Memo Writer
- role family id: DIV-03-RF-08
- division: Planning and Strategy
- department: Planning Office
- purpose: Writes decision memos for future approval.
- allowed outputs: plans, decision memos
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Sequencing Office
- status: STATIC_DESIGN_ONLY

### Constraint Mapper
- role family id: DIV-03-RF-09
- division: Planning and Strategy
- department: Planning Office
- purpose: Maps constraints to planning boundaries.
- allowed outputs: plans, decision memos
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Sequencing Office
- status: STATIC_DESIGN_ONLY

### Execution-Free Planner
- role family id: DIV-03-RF-10
- division: Planning and Strategy
- department: Planning Office
- purpose: Plans only, never activates work.
- allowed outputs: plans, decision memos
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Sequencing Office
- status: STATIC_DESIGN_ONLY

### Research Synthesizer
- role family id: DIV-04-RF-01
- division: Research and Knowledge
- department: Research Desk
- purpose: Synthesizes evidence into static research notes.
- allowed outputs: research notes, evidence summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Synthesis Desk
- status: STATIC_DESIGN_ONLY

### Knowledge Curator
- role family id: DIV-04-RF-02
- division: Research and Knowledge
- department: Research Desk
- purpose: Curates durable reference material.
- allowed outputs: research notes, evidence summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Synthesis Desk
- status: STATIC_DESIGN_ONLY

### Evidence Mapper
- role family id: DIV-04-RF-03
- division: Research and Knowledge
- department: Research Desk
- purpose: Maps evidence to claims and caveats.
- allowed outputs: research notes, evidence summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Synthesis Desk
- status: STATIC_DESIGN_ONLY

### Source Evaluator
- role family id: DIV-04-RF-04
- division: Research and Knowledge
- department: Research Desk
- purpose: Evaluates source quality and freshness.
- allowed outputs: research notes, evidence summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Synthesis Desk
- status: STATIC_DESIGN_ONLY

### Citation Builder
- role family id: DIV-04-RF-05
- division: Research and Knowledge
- department: Research Desk
- purpose: Builds citation-ready references.
- allowed outputs: research notes, evidence summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L3
- escalation target: Synthesis Desk
- status: STATIC_DESIGN_ONLY

### Archive Indexer
- role family id: DIV-04-RF-06
- division: Research and Knowledge
- department: Research Desk
- purpose: Indexes archived knowledge records.
- allowed outputs: research notes, evidence summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L1
- escalation target: Synthesis Desk
- status: STATIC_DESIGN_ONLY

### Insight Summarizer
- role family id: DIV-04-RF-07
- division: Research and Knowledge
- department: Research Desk
- purpose: Summarizes findings for planning use.
- allowed outputs: research notes, evidence summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Synthesis Desk
- status: STATIC_DESIGN_ONLY

### Reference Librarian
- role family id: DIV-04-RF-08
- division: Research and Knowledge
- department: Research Desk
- purpose: Organizes knowledge by topic and stability.
- allowed outputs: research notes, evidence summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Synthesis Desk
- status: STATIC_DESIGN_ONLY

### Pattern Finder
- role family id: DIV-04-RF-09
- division: Research and Knowledge
- department: Research Desk
- purpose: Identifies stable patterns across notes.
- allowed outputs: research notes, evidence summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Synthesis Desk
- status: STATIC_DESIGN_ONLY

### Knowledge Auditor
- role family id: DIV-04-RF-10
- division: Research and Knowledge
- department: Research Desk
- purpose: Audits the consistency of knowledge records.
- allowed outputs: research notes, evidence summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Synthesis Desk
- status: STATIC_DESIGN_ONLY

### Code Reviewer
- role family id: DIV-05-RF-01
- division: Engineering and Build
- department: Build Office
- purpose: Reviews code design without changing runtime state.
- allowed outputs: design specs, implementation outlines
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Architecture Office
- status: STATIC_DESIGN_ONLY

### UI Builder
- role family id: DIV-05-RF-02
- division: Engineering and Build
- department: Build Office
- purpose: Drafts user interface build specifications.
- allowed outputs: design specs, implementation outlines
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Architecture Office
- status: STATIC_DESIGN_ONLY

### API Boundary Auditor
- role family id: DIV-05-RF-03
- division: Engineering and Build
- department: Build Office
- purpose: Audits interface boundaries and contracts.
- allowed outputs: design specs, implementation outlines
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Architecture Office
- status: STATIC_DESIGN_ONLY

### Module Planner
- role family id: DIV-05-RF-04
- division: Engineering and Build
- department: Build Office
- purpose: Plans module decomposition and ownership.
- allowed outputs: design specs, implementation outlines
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Architecture Office
- status: STATIC_DESIGN_ONLY

### Patch Designer
- role family id: DIV-05-RF-05
- division: Engineering and Build
- department: Build Office
- purpose: Designs static patch outlines.
- allowed outputs: design specs, implementation outlines
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L3
- escalation target: Architecture Office
- status: STATIC_DESIGN_ONLY

### Architecture Mapper
- role family id: DIV-05-RF-06
- division: Engineering and Build
- department: Build Office
- purpose: Maps system architecture for future build work.
- allowed outputs: design specs, implementation outlines
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L1
- escalation target: Architecture Office
- status: STATIC_DESIGN_ONLY

### Component Curator
- role family id: DIV-05-RF-07
- division: Engineering and Build
- department: Build Office
- purpose: Curates component responsibilities.
- allowed outputs: design specs, implementation outlines
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Architecture Office
- status: STATIC_DESIGN_ONLY

### Interface Designer
- role family id: DIV-05-RF-08
- division: Engineering and Build
- department: Build Office
- purpose: Defines interaction surfaces and edges.
- allowed outputs: design specs, implementation outlines
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Architecture Office
- status: STATIC_DESIGN_ONLY

### Build Blueprint Writer
- role family id: DIV-05-RF-09
- division: Engineering and Build
- department: Build Office
- purpose: Writes build blueprints, not builds.
- allowed outputs: design specs, implementation outlines
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Architecture Office
- status: STATIC_DESIGN_ONLY

### Dependency Cartographer
- role family id: DIV-05-RF-10
- division: Engineering and Build
- department: Build Office
- purpose: Maps internal dependencies and coupling.
- allowed outputs: design specs, implementation outlines
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Architecture Office
- status: STATIC_DESIGN_ONLY

### Regression Checker
- role family id: DIV-06-RF-01
- division: QA and Validation
- department: Validation Desk
- purpose: Checks regression risk in static form.
- allowed outputs: test plans, regression notes
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Test Design Desk
- status: STATIC_DESIGN_ONLY

### Validator Writer
- role family id: DIV-06-RF-02
- division: QA and Validation
- department: Validation Desk
- purpose: Writes validation criteria and checks.
- allowed outputs: test plans, regression notes
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Test Design Desk
- status: STATIC_DESIGN_ONLY

### Test Matrix Auditor
- role family id: DIV-06-RF-03
- division: QA and Validation
- department: Validation Desk
- purpose: Audits test coverage and matrix gaps.
- allowed outputs: test plans, regression notes
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Test Design Desk
- status: STATIC_DESIGN_ONLY

### Assertion Planner
- role family id: DIV-06-RF-04
- division: QA and Validation
- department: Validation Desk
- purpose: Plans assertions and expected results.
- allowed outputs: test plans, regression notes
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Test Design Desk
- status: STATIC_DESIGN_ONLY

### Quality Gate Keeper
- role family id: DIV-06-RF-05
- division: QA and Validation
- department: Validation Desk
- purpose: Defines quality gates without enforcing live execution.
- allowed outputs: test plans, regression notes
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L3
- escalation target: Test Design Desk
- status: STATIC_DESIGN_ONLY

### Case Designer
- role family id: DIV-06-RF-06
- division: QA and Validation
- department: Validation Desk
- purpose: Designs test cases and edge cases.
- allowed outputs: test plans, regression notes
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L1
- escalation target: Test Design Desk
- status: STATIC_DESIGN_ONLY

### Failure Analyst
- role family id: DIV-06-RF-07
- division: QA and Validation
- department: Validation Desk
- purpose: Analyzes failure modes and rollback needs.
- allowed outputs: test plans, regression notes
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Test Design Desk
- status: STATIC_DESIGN_ONLY

### Coverage Mapper
- role family id: DIV-06-RF-08
- division: QA and Validation
- department: Validation Desk
- purpose: Maps coverage to requirements and risk.
- allowed outputs: test plans, regression notes
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Test Design Desk
- status: STATIC_DESIGN_ONLY

### Verification Curator
- role family id: DIV-06-RF-09
- division: QA and Validation
- department: Validation Desk
- purpose: Curates verification steps and evidence.
- allowed outputs: test plans, regression notes
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Test Design Desk
- status: STATIC_DESIGN_ONLY

### Defect Pattern Tracker
- role family id: DIV-06-RF-10
- division: QA and Validation
- department: Validation Desk
- purpose: Tracks defect patterns for static remediation.
- allowed outputs: test plans, regression notes
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Test Design Desk
- status: STATIC_DESIGN_ONLY

### Documentation Formatter
- role family id: DIV-07-RF-01
- division: Documentation and Reporting
- department: Docs Office
- purpose: Formats documentation into consistent records.
- allowed outputs: documentation, summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Release Notes Office
- status: STATIC_DESIGN_ONLY

### Report Assembler
- role family id: DIV-07-RF-02
- division: Documentation and Reporting
- department: Docs Office
- purpose: Assembles structured reports from static inputs.
- allowed outputs: documentation, summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Release Notes Office
- status: STATIC_DESIGN_ONLY

### Release Note Curator
- role family id: DIV-07-RF-03
- division: Documentation and Reporting
- department: Docs Office
- purpose: Curates release notes without release action.
- allowed outputs: documentation, summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Release Notes Office
- status: STATIC_DESIGN_ONLY

### Narrative Editor
- role family id: DIV-07-RF-04
- division: Documentation and Reporting
- department: Docs Office
- purpose: Edits narrative clarity and structure.
- allowed outputs: documentation, summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Release Notes Office
- status: STATIC_DESIGN_ONLY

### Brief Writer
- role family id: DIV-07-RF-05
- division: Documentation and Reporting
- department: Docs Office
- purpose: Writes concise briefings for review.
- allowed outputs: documentation, summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L3
- escalation target: Release Notes Office
- status: STATIC_DESIGN_ONLY

### Record Keeper
- role family id: DIV-07-RF-06
- division: Documentation and Reporting
- department: Docs Office
- purpose: Maintains durable documentation records.
- allowed outputs: documentation, summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L1
- escalation target: Release Notes Office
- status: STATIC_DESIGN_ONLY

### Summary Producer
- role family id: DIV-07-RF-07
- division: Documentation and Reporting
- department: Docs Office
- purpose: Produces readable summary artifacts.
- allowed outputs: documentation, summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Release Notes Office
- status: STATIC_DESIGN_ONLY

### Explainer
- role family id: DIV-07-RF-08
- division: Documentation and Reporting
- department: Docs Office
- purpose: Explains static system concepts plainly.
- allowed outputs: documentation, summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Release Notes Office
- status: STATIC_DESIGN_ONLY

### Reference Publisher
- role family id: DIV-07-RF-09
- division: Documentation and Reporting
- department: Docs Office
- purpose: Prepares reference material for later use.
- allowed outputs: documentation, summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Release Notes Office
- status: STATIC_DESIGN_ONLY

### Archive Formatter
- role family id: DIV-07-RF-10
- division: Documentation and Reporting
- department: Docs Office
- purpose: Normalizes archive-ready document output.
- allowed outputs: documentation, summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Release Notes Office
- status: STATIC_DESIGN_ONLY

### Boundary Auditor
- role family id: DIV-08-RF-01
- division: Security and Safety
- department: Safety Office
- purpose: Audits safety boundaries and permission ceilings.
- allowed outputs: safety rules, boundary assessments
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Threat Office
- status: STATIC_DESIGN_ONLY

### Safety Gatekeeper
- role family id: DIV-08-RF-02
- division: Security and Safety
- department: Safety Office
- purpose: Prevents unsafe escalation into live systems.
- allowed outputs: safety rules, boundary assessments
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Threat Office
- status: STATIC_DESIGN_ONLY

### Threat Modeler
- role family id: DIV-08-RF-03
- division: Security and Safety
- department: Safety Office
- purpose: Models threat scenarios in static form.
- allowed outputs: safety rules, boundary assessments
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Threat Office
- status: STATIC_DESIGN_ONLY

### Risk Sentinel
- role family id: DIV-08-RF-04
- division: Security and Safety
- department: Safety Office
- purpose: Watches for risk and unsafe drift.
- allowed outputs: safety rules, boundary assessments
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Threat Office
- status: STATIC_DESIGN_ONLY

### Policy Enforcer
- role family id: DIV-08-RF-05
- division: Security and Safety
- department: Safety Office
- purpose: Describes policy enforcement boundaries.
- allowed outputs: safety rules, boundary assessments
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L3
- escalation target: Threat Office
- status: STATIC_DESIGN_ONLY

### Shield Curator
- role family id: DIV-08-RF-06
- division: Security and Safety
- department: Safety Office
- purpose: Curates defensive safety measures.
- allowed outputs: safety rules, boundary assessments
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L1
- escalation target: Threat Office
- status: STATIC_DESIGN_ONLY

### Guardrail Designer
- role family id: DIV-08-RF-07
- division: Security and Safety
- department: Safety Office
- purpose: Designs guardrails and stop conditions.
- allowed outputs: safety rules, boundary assessments
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Threat Office
- status: STATIC_DESIGN_ONLY

### Security Reviewer
- role family id: DIV-08-RF-08
- division: Security and Safety
- department: Safety Office
- purpose: Reviews security posture and red lines.
- allowed outputs: safety rules, boundary assessments
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Threat Office
- status: STATIC_DESIGN_ONLY

### Privilege Auditor
- role family id: DIV-08-RF-09
- division: Security and Safety
- department: Safety Office
- purpose: Audits privilege boundaries and non-access.
- allowed outputs: safety rules, boundary assessments
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Threat Office
- status: STATIC_DESIGN_ONLY

### Safety Assertion Writer
- role family id: DIV-08-RF-10
- division: Security and Safety
- department: Safety Office
- purpose: Writes explicit safety assertions.
- allowed outputs: safety rules, boundary assessments
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Threat Office
- status: STATIC_DESIGN_ONLY

### Deployment Planner
- role family id: DIV-09-RF-01
- division: Deployment and Operations
- department: Operations Office
- purpose: Plans deployment stages without deploying.
- allowed outputs: readiness plans, operations checklists
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Readiness Office
- status: STATIC_DESIGN_ONLY

### Rollback Strategist
- role family id: DIV-09-RF-02
- division: Deployment and Operations
- department: Operations Office
- purpose: Plans rollback paths and containment.
- allowed outputs: readiness plans, operations checklists
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Readiness Office
- status: STATIC_DESIGN_ONLY

### Operations Curator
- role family id: DIV-09-RF-03
- division: Deployment and Operations
- department: Operations Office
- purpose: Curates operations runbooks and readiness notes.
- allowed outputs: readiness plans, operations checklists
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Readiness Office
- status: STATIC_DESIGN_ONLY

### Readiness Checker
- role family id: DIV-09-RF-04
- division: Deployment and Operations
- department: Operations Office
- purpose: Checks readiness criteria in static form.
- allowed outputs: readiness plans, operations checklists
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Readiness Office
- status: STATIC_DESIGN_ONLY

### Runbook Writer
- role family id: DIV-09-RF-05
- division: Deployment and Operations
- department: Operations Office
- purpose: Writes operational runbooks and references.
- allowed outputs: readiness plans, operations checklists
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L3
- escalation target: Readiness Office
- status: STATIC_DESIGN_ONLY

### Stability Analyst
- role family id: DIV-09-RF-06
- division: Deployment and Operations
- department: Operations Office
- purpose: Analyzes operational stability patterns.
- allowed outputs: readiness plans, operations checklists
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L1
- escalation target: Readiness Office
- status: STATIC_DESIGN_ONLY

### Incident Mapper
- role family id: DIV-09-RF-07
- division: Deployment and Operations
- department: Operations Office
- purpose: Maps incident classes to response ideas.
- allowed outputs: readiness plans, operations checklists
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Readiness Office
- status: STATIC_DESIGN_ONLY

### Control Desk Planner
- role family id: DIV-09-RF-08
- division: Deployment and Operations
- department: Operations Office
- purpose: Plans control desk procedures.
- allowed outputs: readiness plans, operations checklists
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Readiness Office
- status: STATIC_DESIGN_ONLY

### Change Window Curator
- role family id: DIV-09-RF-09
- division: Deployment and Operations
- department: Operations Office
- purpose: Curates change-window rules and checks.
- allowed outputs: readiness plans, operations checklists
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Readiness Office
- status: STATIC_DESIGN_ONLY

### Continuity Planner
- role family id: DIV-09-RF-10
- division: Deployment and Operations
- department: Operations Office
- purpose: Plans continuity and recovery records.
- allowed outputs: readiness plans, operations checklists
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Readiness Office
- status: STATIC_DESIGN_ONLY

### Product Strategist
- role family id: DIV-10-RF-01
- division: Business and Product
- department: Product Office
- purpose: Shapes product intent into static strategy.
- allowed outputs: product briefs, roadmap inputs
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Research Ops
- status: STATIC_DESIGN_ONLY

### Business Analyst
- role family id: DIV-10-RF-02
- division: Business and Product
- department: Product Office
- purpose: Analyzes business goals and constraints.
- allowed outputs: product briefs, roadmap inputs
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Research Ops
- status: STATIC_DESIGN_ONLY

### Value Mapper
- role family id: DIV-10-RF-03
- division: Business and Product
- department: Product Office
- purpose: Maps value statements to outcomes.
- allowed outputs: product briefs, roadmap inputs
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Research Ops
- status: STATIC_DESIGN_ONLY

### Market Curator
- role family id: DIV-10-RF-04
- division: Business and Product
- department: Product Office
- purpose: Curates market context and positioning.
- allowed outputs: product briefs, roadmap inputs
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Research Ops
- status: STATIC_DESIGN_ONLY

### Opportunity Finder
- role family id: DIV-10-RF-05
- division: Business and Product
- department: Product Office
- purpose: Finds opportunity themes for planning.
- allowed outputs: product briefs, roadmap inputs
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L3
- escalation target: Research Ops
- status: STATIC_DESIGN_ONLY

### Portfolio Planner
- role family id: DIV-10-RF-06
- division: Business and Product
- department: Product Office
- purpose: Plans product portfolio structure.
- allowed outputs: product briefs, roadmap inputs
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L1
- escalation target: Research Ops
- status: STATIC_DESIGN_ONLY

### Outcome Writer
- role family id: DIV-10-RF-07
- division: Business and Product
- department: Product Office
- purpose: Writes outcome-focused product briefs.
- allowed outputs: product briefs, roadmap inputs
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Research Ops
- status: STATIC_DESIGN_ONLY

### Segment Analyst
- role family id: DIV-10-RF-08
- division: Business and Product
- department: Product Office
- purpose: Analyzes audience segments in static form.
- allowed outputs: product briefs, roadmap inputs
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Research Ops
- status: STATIC_DESIGN_ONLY

### Demand Mapper
- role family id: DIV-10-RF-09
- division: Business and Product
- department: Product Office
- purpose: Maps demand signals to backlog themes.
- allowed outputs: product briefs, roadmap inputs
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Research Ops
- status: STATIC_DESIGN_ONLY

### Business Review Curator
- role family id: DIV-10-RF-10
- division: Business and Product
- department: Product Office
- purpose: Curates review-ready business notes.
- allowed outputs: product briefs, roadmap inputs
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Research Ops
- status: STATIC_DESIGN_ONLY

### Creative Concept Builder
- role family id: DIV-11-RF-01
- division: Creative and Media
- department: Creative Studio
- purpose: Builds static creative concepts and directions.
- allowed outputs: creative briefs, presentation assets
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Brand Studio
- status: STATIC_DESIGN_ONLY

### Media Layout Designer
- role family id: DIV-11-RF-02
- division: Creative and Media
- department: Creative Studio
- purpose: Designs presentation and media layouts.
- allowed outputs: creative briefs, presentation assets
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Brand Studio
- status: STATIC_DESIGN_ONLY

### Brand Voice Curator
- role family id: DIV-11-RF-03
- division: Creative and Media
- department: Creative Studio
- purpose: Curates voice and tone references.
- allowed outputs: creative briefs, presentation assets
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Brand Studio
- status: STATIC_DESIGN_ONLY

### Visual Storyboarder
- role family id: DIV-11-RF-04
- division: Creative and Media
- department: Creative Studio
- purpose: Builds visual storyboards for later use.
- allowed outputs: creative briefs, presentation assets
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Brand Studio
- status: STATIC_DESIGN_ONLY

### Art Direction Planner
- role family id: DIV-11-RF-05
- division: Creative and Media
- department: Creative Studio
- purpose: Plans art direction without publishing.
- allowed outputs: creative briefs, presentation assets
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L3
- escalation target: Brand Studio
- status: STATIC_DESIGN_ONLY

### Concept Renderer
- role family id: DIV-11-RF-06
- division: Creative and Media
- department: Creative Studio
- purpose: Renders concept descriptions into notes.
- allowed outputs: creative briefs, presentation assets
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L1
- escalation target: Brand Studio
- status: STATIC_DESIGN_ONLY

### Presentation Designer
- role family id: DIV-11-RF-07
- division: Creative and Media
- department: Creative Studio
- purpose: Designs presentation structure and sequencing.
- allowed outputs: creative briefs, presentation assets
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Brand Studio
- status: STATIC_DESIGN_ONLY

### Creative Brief Writer
- role family id: DIV-11-RF-08
- division: Creative and Media
- department: Creative Studio
- purpose: Writes creative briefs for review.
- allowed outputs: creative briefs, presentation assets
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Brand Studio
- status: STATIC_DESIGN_ONLY

### Story Arc Curator
- role family id: DIV-11-RF-09
- division: Creative and Media
- department: Creative Studio
- purpose: Curates narrative arc options.
- allowed outputs: creative briefs, presentation assets
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Brand Studio
- status: STATIC_DESIGN_ONLY

### Media Concept Auditor
- role family id: DIV-11-RF-10
- division: Creative and Media
- department: Creative Studio
- purpose: Audits media concepts for static fit.
- allowed outputs: creative briefs, presentation assets
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Brand Studio
- status: STATIC_DESIGN_ONLY

### Data Analyst
- role family id: DIV-12-RF-01
- division: Data and Analytics
- department: Analytics Office
- purpose: Analyzes data structure in static planning form.
- allowed outputs: analytics plans, trend summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Modeling Office
- status: STATIC_DESIGN_ONLY

### Metric Curator
- role family id: DIV-12-RF-02
- division: Data and Analytics
- department: Analytics Office
- purpose: Curates metrics and definitions.
- allowed outputs: analytics plans, trend summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Modeling Office
- status: STATIC_DESIGN_ONLY

### Insight Synthesizer
- role family id: DIV-12-RF-03
- division: Data and Analytics
- department: Analytics Office
- purpose: Synthesizes analytic insights for review.
- allowed outputs: analytics plans, trend summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Modeling Office
- status: STATIC_DESIGN_ONLY

### Trend Mapper
- role family id: DIV-12-RF-04
- division: Data and Analytics
- department: Analytics Office
- purpose: Maps trends to static observations.
- allowed outputs: analytics plans, trend summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Modeling Office
- status: STATIC_DESIGN_ONLY

### Forecast Planner
- role family id: DIV-12-RF-05
- division: Data and Analytics
- department: Analytics Office
- purpose: Plans forecast structure without live queries.
- allowed outputs: analytics plans, trend summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L3
- escalation target: Modeling Office
- status: STATIC_DESIGN_ONLY

### Signal Analyst
- role family id: DIV-12-RF-06
- division: Data and Analytics
- department: Analytics Office
- purpose: Analyzes signals and metric relationships.
- allowed outputs: analytics plans, trend summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L1
- escalation target: Modeling Office
- status: STATIC_DESIGN_ONLY

### Model Curator
- role family id: DIV-12-RF-07
- division: Data and Analytics
- department: Analytics Office
- purpose: Curates model concepts and assumptions.
- allowed outputs: analytics plans, trend summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Modeling Office
- status: STATIC_DESIGN_ONLY

### Measure Designer
- role family id: DIV-12-RF-08
- division: Data and Analytics
- department: Analytics Office
- purpose: Designs measurement definitions and scope.
- allowed outputs: analytics plans, trend summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Modeling Office
- status: STATIC_DESIGN_ONLY

### Report Analyst
- role family id: DIV-12-RF-09
- division: Data and Analytics
- department: Analytics Office
- purpose: Analyzes report structure and outputs.
- allowed outputs: analytics plans, trend summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Modeling Office
- status: STATIC_DESIGN_ONLY

### Analytics Auditor
- role family id: DIV-12-RF-10
- division: Data and Analytics
- department: Analytics Office
- purpose: Audits analytics assumptions and notes.
- allowed outputs: analytics plans, trend summaries
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Modeling Office
- status: STATIC_DESIGN_ONLY

### Support Triage Analyst
- role family id: DIV-13-RF-01
- division: User Support and Personalization
- department: Support Desk
- purpose: Triage support patterns and escalation notes.
- allowed outputs: support scripts, personalization guides
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Experience Desk
- status: STATIC_DESIGN_ONLY

### Personalization Mapper
- role family id: DIV-13-RF-02
- division: User Support and Personalization
- department: Support Desk
- purpose: Maps personalization logic into static records.
- allowed outputs: support scripts, personalization guides
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Experience Desk
- status: STATIC_DESIGN_ONLY

### Help Flow Curator
- role family id: DIV-13-RF-03
- division: User Support and Personalization
- department: Support Desk
- purpose: Curates support flows and help steps.
- allowed outputs: support scripts, personalization guides
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Experience Desk
- status: STATIC_DESIGN_ONLY

### Response Drafting Assistant
- role family id: DIV-13-RF-04
- division: User Support and Personalization
- department: Support Desk
- purpose: Drafts responses for human review.
- allowed outputs: support scripts, personalization guides
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Experience Desk
- status: STATIC_DESIGN_ONLY

### Experience Guide
- role family id: DIV-13-RF-05
- division: User Support and Personalization
- department: Support Desk
- purpose: Guides experience choices in static form.
- allowed outputs: support scripts, personalization guides
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L3
- escalation target: Experience Desk
- status: STATIC_DESIGN_ONLY

### Service Pattern Writer
- role family id: DIV-13-RF-06
- division: User Support and Personalization
- department: Support Desk
- purpose: Writes support pattern references.
- allowed outputs: support scripts, personalization guides
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L1
- escalation target: Experience Desk
- status: STATIC_DESIGN_ONLY

### Care Plan Curator
- role family id: DIV-13-RF-07
- division: User Support and Personalization
- department: Support Desk
- purpose: Curates user care and support plans.
- allowed outputs: support scripts, personalization guides
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Experience Desk
- status: STATIC_DESIGN_ONLY

### Assist Flow Designer
- role family id: DIV-13-RF-08
- division: User Support and Personalization
- department: Support Desk
- purpose: Designs assistance flow structure.
- allowed outputs: support scripts, personalization guides
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Experience Desk
- status: STATIC_DESIGN_ONLY

### Resolution Mapper
- role family id: DIV-13-RF-09
- division: User Support and Personalization
- department: Support Desk
- purpose: Maps resolution paths without live action.
- allowed outputs: support scripts, personalization guides
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Experience Desk
- status: STATIC_DESIGN_ONLY

### Support Knowledge Builder
- role family id: DIV-13-RF-10
- division: User Support and Personalization
- department: Support Desk
- purpose: Builds support knowledge references.
- allowed outputs: support scripts, personalization guides
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Experience Desk
- status: STATIC_DESIGN_ONLY

### Compliance Checker
- role family id: DIV-14-RF-01
- division: Compliance and Audit
- department: Compliance Office
- purpose: Checks policy alignment in static form.
- allowed outputs: compliance notes, controls mapping
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Controls Office
- status: STATIC_DESIGN_ONLY

### Audit Trail Curator
- role family id: DIV-14-RF-02
- division: Compliance and Audit
- department: Compliance Office
- purpose: Curates audit trail requirements and records.
- allowed outputs: compliance notes, controls mapping
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Controls Office
- status: STATIC_DESIGN_ONLY

### Control Mapper
- role family id: DIV-14-RF-03
- division: Compliance and Audit
- department: Compliance Office
- purpose: Maps controls to policy and evidence.
- allowed outputs: compliance notes, controls mapping
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Controls Office
- status: STATIC_DESIGN_ONLY

### Assurance Writer
- role family id: DIV-14-RF-04
- division: Compliance and Audit
- department: Compliance Office
- purpose: Writes assurance notes and exceptions.
- allowed outputs: compliance notes, controls mapping
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Controls Office
- status: STATIC_DESIGN_ONLY

### Evidence Keeper
- role family id: DIV-14-RF-05
- division: Compliance and Audit
- department: Compliance Office
- purpose: Keeps audit evidence references.
- allowed outputs: compliance notes, controls mapping
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L3
- escalation target: Controls Office
- status: STATIC_DESIGN_ONLY

### Policy Reviewer
- role family id: DIV-14-RF-06
- division: Compliance and Audit
- department: Compliance Office
- purpose: Reviews policy consistency and limits.
- allowed outputs: compliance notes, controls mapping
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L1
- escalation target: Controls Office
- status: STATIC_DESIGN_ONLY

### Trace Recorder
- role family id: DIV-14-RF-07
- division: Compliance and Audit
- department: Compliance Office
- purpose: Records traceability notes for audits.
- allowed outputs: compliance notes, controls mapping
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Controls Office
- status: STATIC_DESIGN_ONLY

### Governance Analyst
- role family id: DIV-14-RF-08
- division: Compliance and Audit
- department: Compliance Office
- purpose: Analyzes governance boundaries and records.
- allowed outputs: compliance notes, controls mapping
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Controls Office
- status: STATIC_DESIGN_ONLY

### Registry Auditor
- role family id: DIV-14-RF-09
- division: Compliance and Audit
- department: Compliance Office
- purpose: Audits registry accuracy and completeness.
- allowed outputs: compliance notes, controls mapping
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Controls Office
- status: STATIC_DESIGN_ONLY

### Exception Tracker
- role family id: DIV-14-RF-10
- division: Compliance and Audit
- department: Compliance Office
- purpose: Tracks exceptions for formal review.
- allowed outputs: compliance notes, controls mapping
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Controls Office
- status: STATIC_DESIGN_ONLY

### Experimental Concept Mapper
- role family id: DIV-15-RF-01
- division: Experimental Systems Lab
- department: Lab Office
- purpose: Maps novel concepts into static proposals.
- allowed outputs: prototype specs, variant proposals
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Exploration Office
- status: STATIC_DESIGN_ONLY

### Prototype Planner
- role family id: DIV-15-RF-02
- division: Experimental Systems Lab
- department: Lab Office
- purpose: Plans prototype directions without execution.
- allowed outputs: prototype specs, variant proposals
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Exploration Office
- status: STATIC_DESIGN_ONLY

### Variant Curator
- role family id: DIV-15-RF-03
- division: Experimental Systems Lab
- department: Lab Office
- purpose: Curates non-live variant ideas.
- allowed outputs: prototype specs, variant proposals
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Exploration Office
- status: STATIC_DESIGN_ONLY

### Lab Scenario Builder
- role family id: DIV-15-RF-04
- division: Experimental Systems Lab
- department: Lab Office
- purpose: Builds scenario sketches for research.
- allowed outputs: prototype specs, variant proposals
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Exploration Office
- status: STATIC_DESIGN_ONLY

### Exploration Mapper
- role family id: DIV-15-RF-05
- division: Experimental Systems Lab
- department: Lab Office
- purpose: Maps exploratory paths and unknowns.
- allowed outputs: prototype specs, variant proposals
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L3
- escalation target: Exploration Office
- status: STATIC_DESIGN_ONLY

### Trial Designer
- role family id: DIV-15-RF-06
- division: Experimental Systems Lab
- department: Lab Office
- purpose: Designs trials without live activation.
- allowed outputs: prototype specs, variant proposals
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L1
- escalation target: Exploration Office
- status: STATIC_DESIGN_ONLY

### Concept Auditor
- role family id: DIV-15-RF-07
- division: Experimental Systems Lab
- department: Lab Office
- purpose: Audits concept fit and safety.
- allowed outputs: prototype specs, variant proposals
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L2
- escalation target: Exploration Office
- status: STATIC_DESIGN_ONLY

### Prototype Blueprint Writer
- role family id: DIV-15-RF-08
- division: Experimental Systems Lab
- department: Lab Office
- purpose: Writes prototype blueprints, not prototypes.
- allowed outputs: prototype specs, variant proposals
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L3
- escalation target: Exploration Office
- status: STATIC_DESIGN_ONLY

### Model Variant Planner
- role family id: DIV-15-RF-09
- division: Experimental Systems Lab
- department: Lab Office
- purpose: Plans model variants for static review.
- allowed outputs: prototype specs, variant proposals
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T0
- default activation tier: A1
- audit level: L1
- escalation target: Exploration Office
- status: STATIC_DESIGN_ONLY

### Innovation Recorder
- role family id: DIV-15-RF-10
- division: Experimental Systems Lab
- department: Lab Office
- purpose: Records experimental observations and caveats.
- allowed outputs: prototype specs, variant proposals
- forbidden actions: activate_live_worker, route_live_task, call_api, use_credentials, read_secrets, read_environment_variables, deploy, execute_production, modify_protected_baseline, modify_devinization_overlay
- default permission tier: T1
- default activation tier: A1
- audit level: L2
- escalation target: Exploration Office
- status: STATIC_DESIGN_ONLY

## Worker Instance Scaling Logic
One role family can expand into many worker instance templates by cloning the same static record pattern with different instance identifiers, allocation labels, or future responsibility slices.

Example:
- one role family = Validator Writer
- one department = QA and Validation
- one team = Runtime Validator Team
- future worker instances = Validator Writer 001 through Validator Writer 250

This v0.1 blueprint does not create 47,250 individual worker records yet. It creates the architecture and taxonomy needed to support that full target capacity.

## Routing Doctrine
Future tasks would be routed only through static eligibility checks, never by activating workers in v0.1.

Routing checks:
- command classification
- required context
- division matching
- department matching
- team matching
- role-family matching
- permission ceiling check
- activation tier check
- human approval requirement
- validator requirement
- audit logging requirement
- escalation path

## Safety Rules
- No worker is live by default.
- No worker can self-activate.
- No worker can raise its own permission tier.
- No worker can bypass approval gates.
- No worker can call APIs.
- No worker can use credentials.
- No worker can read secrets.
- No worker can read environment variables.
- No worker can deploy.
- No worker can execute production.
- No worker can route live tasks.
- No worker can start other workers.
- No worker can mutate protected baseline files.
- No worker can modify Devinization overlays.
- No worker can write outside explicitly approved output directories.
- No worker can convert a design record into an execution record.

## Future Build Steps
1. Expand starter role families into 500 worker templates.
2. Create department-specific worker manifests.
3. Create worker permission matrix.
4. Create worker routing table.
5. Create worker audit schema.
6. Create worker readiness validator.
7. Create worker simulation bundle.
8. Create worker registry preview.
9. Create worker retirement and quarantine policy.
10. Create worker instance allocation map for the full 47,250-worker target.
11. Create runtime bridge only after static design validation passes.
