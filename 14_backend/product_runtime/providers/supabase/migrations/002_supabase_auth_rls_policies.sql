-- MVP-4 Supabase Auth + RLS policy scaffold.
-- RLS is required before production writes.
-- auth.uid() binding is required before production writes.
-- Service role must never be exposed to browser code.
-- Production migrations are scaffolded only and must be applied manually after review.

alter table if exists app_users enable row level security;
alter table if exists app_roles enable row level security;
alter table if exists requests enable row level security;
alter table if exists request_lifecycle_events enable row level security;
alter table if exists approvals enable row level security;
alter table if exists audit_events enable row level security;
alter table if exists dry_run_results enable row level security;
alter table if exists no_go_flags enable row level security;

drop policy if exists "app_users_select_own" on app_users;
create policy "app_users_select_own" on app_users
  for select
  using (auth.uid() = id);

drop policy if exists "requests_select_own" on requests;
create policy "requests_select_own" on requests
  for select
  using (auth.uid() = actor_id);

drop policy if exists "requests_insert_own" on requests;
create policy "requests_insert_own" on requests
  for insert
  with check (auth.uid() = actor_id);

drop policy if exists "request_lifecycle_events_select_own" on request_lifecycle_events;
create policy "request_lifecycle_events_select_own" on request_lifecycle_events
  for select
  using (
    exists (
      select 1
      from requests
      where requests.id = request_lifecycle_events.request_id
        and requests.actor_id = auth.uid()
    )
  );

drop policy if exists "dry_run_results_select_own" on dry_run_results;
create policy "dry_run_results_select_own" on dry_run_results
  for select
  using (
    exists (
      select 1
      from requests
      where requests.id = dry_run_results.request_id
        and requests.actor_id = auth.uid()
    )
  );

-- approvals, audit_events, and no_go_flags remain restricted until role policies are manually reviewed.
-- No anonymous write policy is added.
-- No broad public write policy is added.
-- No service role browser exposure is allowed.
