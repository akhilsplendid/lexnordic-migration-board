create table if not exists public.matters (
  id uuid primary key default gen_random_uuid(),
  matter_number text not null unique,
  title text not null,
  case_type text not null default 'work_permit_appeal',
  status text not null default 'intake',
  jurisdiction text not null default 'SE',
  permit_type text not null default 'work_permit',
  applicant_alias text,
  employer_name text,
  decision_date date,
  appeal_deadline date,
  band_room_id uuid,
  qdrant_collection text,
  summary text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint matters_case_type_check check (
    case_type in ('work_permit_appeal', 'migration_risk_review', 'source_research')
  ),
  constraint matters_status_check check (
    status in ('intake', 'triage', 'evidence', 'drafting', 'review', 'approved', 'archived')
  )
);

create table if not exists public.matter_documents (
  id uuid primary key default gen_random_uuid(),
  matter_id uuid not null references public.matters(id) on delete cascade,
  document_type text not null,
  source_kind text not null default 'uploaded',
  storage_bucket text not null,
  storage_path text not null unique,
  filename text not null,
  content_type text,
  size_bytes bigint,
  sha256 text,
  extracted_text_status text not null default 'pending',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint matter_documents_document_type_check check (
    document_type in (
      'decision',
      'employment_contract',
      'salary_evidence',
      'insurance_evidence',
      'identity',
      'appeal_draft',
      'other'
    )
  ),
  constraint matter_documents_source_kind_check check (
    source_kind in ('uploaded', 'generated', 'official_source', 'case_law', 'secondary_source')
  ),
  constraint matter_documents_extracted_status_check check (
    extracted_text_status in ('pending', 'processing', 'complete', 'failed', 'not_applicable')
  )
);

create table if not exists public.agent_runs (
  id uuid primary key default gen_random_uuid(),
  matter_id uuid references public.matters(id) on delete cascade,
  band_room_id uuid,
  band_agent_id uuid,
  agent_role text not null,
  status text not null default 'queued',
  model_provider text,
  model_name text,
  input jsonb not null default '{}'::jsonb,
  output jsonb not null default '{}'::jsonb,
  citations jsonb not null default '[]'::jsonb,
  error_message text,
  started_at timestamptz,
  completed_at timestamptz,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint agent_runs_agent_role_check check (
    agent_role in (
      'intake',
      'conflict_kyc',
      'decision_parser',
      'evidence',
      'legal_source',
      'risk',
      'appeal_packet',
      'partner_review'
    )
  ),
  constraint agent_runs_status_check check (
    status in ('queued', 'running', 'blocked', 'completed', 'failed', 'needs_review')
  ),
  constraint agent_runs_model_provider_check check (
    model_provider is null or model_provider in ('aiml', 'featherless', 'manual')
  )
);

create table if not exists public.evidence_items (
  id uuid primary key default gen_random_uuid(),
  matter_id uuid not null references public.matters(id) on delete cascade,
  label text not null,
  description text,
  status text not null default 'needed',
  priority integer not null default 3,
  source_document_id uuid references public.matter_documents(id) on delete set null,
  requested_by_agent_run_id uuid references public.agent_runs(id) on delete set null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint evidence_items_status_check check (
    status in ('needed', 'requested', 'received', 'reviewed', 'waived', 'missing')
  ),
  constraint evidence_items_priority_check check (priority between 1 and 5)
);

create table if not exists public.legal_source_refs (
  id uuid primary key default gen_random_uuid(),
  matter_id uuid references public.matters(id) on delete cascade,
  agent_run_id uuid references public.agent_runs(id) on delete set null,
  qdrant_point_id text,
  source_type text not null,
  title text not null,
  citation text,
  url text,
  retrieved_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb,
  constraint legal_source_refs_source_type_check check (
    source_type in ('official_rule', 'mig_case', 'statute', 'guidance', 'secondary_context')
  )
);

create table if not exists public.packet_versions (
  id uuid primary key default gen_random_uuid(),
  matter_id uuid not null references public.matters(id) on delete cascade,
  version_no integer not null,
  status text not null default 'draft',
  created_by_agent_run_id uuid references public.agent_runs(id) on delete set null,
  packet jsonb not null default '{}'::jsonb,
  source_bundle jsonb not null default '[]'::jsonb,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (matter_id, version_no),
  constraint packet_versions_status_check check (
    status in ('draft', 'ready_for_review', 'approved', 'returned', 'archived')
  )
);

create table if not exists public.review_decisions (
  id uuid primary key default gen_random_uuid(),
  matter_id uuid not null references public.matters(id) on delete cascade,
  packet_version_id uuid references public.packet_versions(id) on delete cascade,
  reviewer_role text not null default 'partner_review',
  decision text not null,
  notes text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  constraint review_decisions_decision_check check (
    decision in ('approve', 'return', 'block', 'needs_expert_review')
  )
);

create table if not exists public.matter_deadlines (
  id uuid primary key default gen_random_uuid(),
  matter_id uuid not null references public.matters(id) on delete cascade,
  deadline_type text not null,
  due_at timestamptz not null,
  status text not null default 'open',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint matter_deadlines_status_check check (
    status in ('open', 'satisfied', 'missed', 'cancelled')
  )
);

create table if not exists public.audit_events (
  id uuid primary key default gen_random_uuid(),
  matter_id uuid references public.matters(id) on delete cascade,
  actor_type text not null,
  actor_id text,
  event_type text not null,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  constraint audit_events_actor_type_check check (
    actor_type in ('system', 'user', 'band_agent', 'provider', 'script')
  )
);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

revoke all on function public.set_updated_at() from public, anon, authenticated;

drop trigger if exists matters_set_updated_at on public.matters;
create trigger matters_set_updated_at
before update on public.matters
for each row execute function public.set_updated_at();

drop trigger if exists matter_documents_set_updated_at on public.matter_documents;
create trigger matter_documents_set_updated_at
before update on public.matter_documents
for each row execute function public.set_updated_at();

drop trigger if exists agent_runs_set_updated_at on public.agent_runs;
create trigger agent_runs_set_updated_at
before update on public.agent_runs
for each row execute function public.set_updated_at();

drop trigger if exists evidence_items_set_updated_at on public.evidence_items;
create trigger evidence_items_set_updated_at
before update on public.evidence_items
for each row execute function public.set_updated_at();

drop trigger if exists packet_versions_set_updated_at on public.packet_versions;
create trigger packet_versions_set_updated_at
before update on public.packet_versions
for each row execute function public.set_updated_at();

drop trigger if exists matter_deadlines_set_updated_at on public.matter_deadlines;
create trigger matter_deadlines_set_updated_at
before update on public.matter_deadlines
for each row execute function public.set_updated_at();

alter table public.matters enable row level security;
alter table public.matter_documents enable row level security;
alter table public.agent_runs enable row level security;
alter table public.evidence_items enable row level security;
alter table public.legal_source_refs enable row level security;
alter table public.packet_versions enable row level security;
alter table public.review_decisions enable row level security;
alter table public.matter_deadlines enable row level security;
alter table public.audit_events enable row level security;

grant usage on schema public to service_role;
grant select, insert, update, delete on table
  public.matters,
  public.matter_documents,
  public.agent_runs,
  public.evidence_items,
  public.legal_source_refs,
  public.packet_versions,
  public.review_decisions,
  public.matter_deadlines,
  public.audit_events
to service_role;

create index if not exists idx_matters_status on public.matters(status);
create index if not exists idx_matters_case_type on public.matters(case_type);
create index if not exists idx_matter_documents_matter on public.matter_documents(matter_id);
create index if not exists idx_matter_documents_type on public.matter_documents(document_type);
create index if not exists idx_agent_runs_matter on public.agent_runs(matter_id);
create index if not exists idx_agent_runs_role_status on public.agent_runs(agent_role, status);
create index if not exists idx_agent_runs_created_at on public.agent_runs(created_at desc);
create index if not exists idx_evidence_items_matter_status on public.evidence_items(matter_id, status);
create index if not exists idx_legal_source_refs_matter on public.legal_source_refs(matter_id);
create index if not exists idx_legal_source_refs_type on public.legal_source_refs(source_type);
create index if not exists idx_packet_versions_matter on public.packet_versions(matter_id);
create index if not exists idx_review_decisions_matter on public.review_decisions(matter_id);
create index if not exists idx_matter_deadlines_matter_due on public.matter_deadlines(matter_id, due_at);
create index if not exists idx_audit_events_matter_created on public.audit_events(matter_id, created_at desc);
create index if not exists idx_audit_events_type_created on public.audit_events(event_type, created_at desc);
