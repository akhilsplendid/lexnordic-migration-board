alter table public.matters
  add column if not exists user_id uuid references auth.users(id) on delete cascade;

create table if not exists public.consultation_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  matter_id uuid references public.matters(id) on delete set null,
  title text not null default 'New consultation',
  query text not null default '',
  route_id text,
  route_label text,
  readiness_score integer,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint consultation_sessions_readiness_check check (
    readiness_score is null or readiness_score between 0 and 100
  )
);

create table if not exists public.chat_messages (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references public.consultation_sessions(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null,
  content text not null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  constraint chat_messages_role_check check (role in ('user', 'assistant', 'system'))
);

drop trigger if exists consultation_sessions_set_updated_at on public.consultation_sessions;
create trigger consultation_sessions_set_updated_at
before update on public.consultation_sessions
for each row execute function public.set_updated_at();

alter table public.consultation_sessions enable row level security;
alter table public.chat_messages enable row level security;

create index if not exists idx_matters_user_updated
  on public.matters(user_id, updated_at desc)
  where user_id is not null;
create index if not exists idx_consultation_sessions_user_updated
  on public.consultation_sessions(user_id, updated_at desc);
create index if not exists idx_consultation_sessions_matter
  on public.consultation_sessions(matter_id);
create index if not exists idx_chat_messages_session_created
  on public.chat_messages(session_id, created_at asc);
create index if not exists idx_chat_messages_user_created
  on public.chat_messages(user_id, created_at desc);

revoke all on table
  public.matters,
  public.matter_documents,
  public.agent_runs,
  public.evidence_items,
  public.legal_source_refs,
  public.packet_versions,
  public.review_decisions,
  public.matter_deadlines,
  public.audit_events,
  public.consultation_sessions,
  public.chat_messages
from anon;

revoke all on table
  public.matters,
  public.matter_documents,
  public.agent_runs,
  public.evidence_items,
  public.legal_source_refs,
  public.packet_versions,
  public.review_decisions,
  public.matter_deadlines,
  public.audit_events,
  public.consultation_sessions,
  public.chat_messages
from authenticated;

revoke all on table
  public.matters,
  public.matter_documents,
  public.agent_runs,
  public.evidence_items,
  public.legal_source_refs,
  public.packet_versions,
  public.review_decisions,
  public.matter_deadlines,
  public.audit_events,
  public.consultation_sessions,
  public.chat_messages
from service_role;

grant select, insert, update, delete on table
  public.matters,
  public.matter_documents,
  public.agent_runs,
  public.evidence_items,
  public.legal_source_refs,
  public.packet_versions,
  public.review_decisions,
  public.matter_deadlines,
  public.audit_events,
  public.consultation_sessions,
  public.chat_messages
to authenticated;

grant select, insert, update, delete on table
  public.matters,
  public.matter_documents,
  public.agent_runs,
  public.evidence_items,
  public.legal_source_refs,
  public.packet_versions,
  public.review_decisions,
  public.matter_deadlines,
  public.audit_events,
  public.consultation_sessions,
  public.chat_messages
to service_role;

drop policy if exists "matters_select_owner" on public.matters;
create policy "matters_select_owner"
on public.matters for select
to authenticated
using ((select auth.uid()) = user_id);

drop policy if exists "matters_insert_owner" on public.matters;
create policy "matters_insert_owner"
on public.matters for insert
to authenticated
with check ((select auth.uid()) = user_id);

drop policy if exists "matters_update_owner" on public.matters;
create policy "matters_update_owner"
on public.matters for update
to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);

drop policy if exists "matters_delete_owner" on public.matters;
create policy "matters_delete_owner"
on public.matters for delete
to authenticated
using ((select auth.uid()) = user_id);

drop policy if exists "consultation_sessions_select_owner" on public.consultation_sessions;
create policy "consultation_sessions_select_owner"
on public.consultation_sessions for select
to authenticated
using ((select auth.uid()) = user_id);

drop policy if exists "consultation_sessions_insert_owner" on public.consultation_sessions;
create policy "consultation_sessions_insert_owner"
on public.consultation_sessions for insert
to authenticated
with check ((select auth.uid()) = user_id);

drop policy if exists "consultation_sessions_update_owner" on public.consultation_sessions;
create policy "consultation_sessions_update_owner"
on public.consultation_sessions for update
to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);

drop policy if exists "consultation_sessions_delete_owner" on public.consultation_sessions;
create policy "consultation_sessions_delete_owner"
on public.consultation_sessions for delete
to authenticated
using ((select auth.uid()) = user_id);

drop policy if exists "chat_messages_select_owner" on public.chat_messages;
create policy "chat_messages_select_owner"
on public.chat_messages for select
to authenticated
using ((select auth.uid()) = user_id);

drop policy if exists "chat_messages_insert_owner" on public.chat_messages;
create policy "chat_messages_insert_owner"
on public.chat_messages for insert
to authenticated
with check (
  (select auth.uid()) = user_id
  and exists (
    select 1
    from public.consultation_sessions s
    where s.id = chat_messages.session_id
      and s.user_id = (select auth.uid())
  )
);

drop policy if exists "chat_messages_update_owner" on public.chat_messages;
create policy "chat_messages_update_owner"
on public.chat_messages for update
to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);

drop policy if exists "chat_messages_delete_owner" on public.chat_messages;
create policy "chat_messages_delete_owner"
on public.chat_messages for delete
to authenticated
using ((select auth.uid()) = user_id);

drop policy if exists "matter_documents_select_owner" on public.matter_documents;
create policy "matter_documents_select_owner"
on public.matter_documents for select
to authenticated
using (
  exists (
    select 1 from public.matters m
    where m.id = matter_documents.matter_id
      and m.user_id = (select auth.uid())
  )
);

drop policy if exists "evidence_items_select_owner" on public.evidence_items;
create policy "evidence_items_select_owner"
on public.evidence_items for select
to authenticated
using (
  exists (
    select 1 from public.matters m
    where m.id = evidence_items.matter_id
      and m.user_id = (select auth.uid())
  )
);

drop policy if exists "agent_runs_select_owner" on public.agent_runs;
create policy "agent_runs_select_owner"
on public.agent_runs for select
to authenticated
using (
  matter_id is not null
  and exists (
    select 1 from public.matters m
    where m.id = agent_runs.matter_id
      and m.user_id = (select auth.uid())
  )
);

drop policy if exists "legal_source_refs_select_owner" on public.legal_source_refs;
create policy "legal_source_refs_select_owner"
on public.legal_source_refs for select
to authenticated
using (
  matter_id is not null
  and exists (
    select 1 from public.matters m
    where m.id = legal_source_refs.matter_id
      and m.user_id = (select auth.uid())
  )
);

drop policy if exists "packet_versions_select_owner" on public.packet_versions;
create policy "packet_versions_select_owner"
on public.packet_versions for select
to authenticated
using (
  exists (
    select 1 from public.matters m
    where m.id = packet_versions.matter_id
      and m.user_id = (select auth.uid())
  )
);

drop policy if exists "review_decisions_select_owner" on public.review_decisions;
create policy "review_decisions_select_owner"
on public.review_decisions for select
to authenticated
using (
  exists (
    select 1 from public.matters m
    where m.id = review_decisions.matter_id
      and m.user_id = (select auth.uid())
  )
);

drop policy if exists "matter_deadlines_select_owner" on public.matter_deadlines;
create policy "matter_deadlines_select_owner"
on public.matter_deadlines for select
to authenticated
using (
  exists (
    select 1 from public.matters m
    where m.id = matter_deadlines.matter_id
      and m.user_id = (select auth.uid())
  )
);

drop policy if exists "audit_events_select_owner" on public.audit_events;
create policy "audit_events_select_owner"
on public.audit_events for select
to authenticated
using (
  matter_id is not null
  and exists (
    select 1 from public.matters m
    where m.id = audit_events.matter_id
      and m.user_id = (select auth.uid())
  )
);
