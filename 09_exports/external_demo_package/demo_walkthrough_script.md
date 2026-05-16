# Demo Walkthrough Script

## 1. Context (0:00 - 0:30)
"This is The Agent Command Center. It is a safety-first control layer for agentic workflows. We separate request intake from execution to ensure every action is reviewable and secure."

## 2. Security Surface (0:30 - 1:30)
"Our dashboard shows live system status. Notice the 'Safety Boundary'—tokens are handled in memory only, and no secrets like the Service Role are ever exposed to the browser. All API calls proxy through Netlify Functions to enforce these rules."

## 3. The Operator Workspace (1:30 - 3:00)
"We'll load a real request list using a test user token. The operator can open any request to see its full detail. The Activity Feed provides a unified timeline of lifecycle events and operator notes, all enforced by Supabase Row Level Security."

## 4. Controlled Mutations (3:00 - 4:00)
"Operators can add notes to the timeline, but notice what's missing: the 'Approve' and 'Execute' buttons are intentionally blocked. We focus on getting the intake and review experience right before enabling automated execution."

## 5. Summary (4:00 - 5:00)
"The system has progressed through multiple verified phases, from local persistence to a production-ready Supabase backend. Our next steps focus on persistent sessions and controlled approval execution."
