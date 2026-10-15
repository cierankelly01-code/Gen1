-- Genex UK: quote requests (run once in Supabase > SQL Editor)
-- Website visitors (anon key) can only INSERT. Nobody can read rows or files with the public key.

create table if not exists public.rfqs (
  id             uuid primary key default gen_random_uuid(),
  created_at     timestamptz not null default now(),
  status         text not null default 'new',
  name           text not null,
  company        text not null,
  email          text not null,
  phone          text,
  country        text,
  part           text not null,
  annual_volume  text not null,
  prototype_qty  text,
  material       text,
  finish         text,
  stages         text[],
  ppap           text,
  needed_by      text,
  notes          text,
  nda_requested  boolean not null default false,
  files          text[],
  source         text
);

alter table public.rfqs enable row level security;

grant insert on table public.rfqs to anon;

drop policy if exists "website can submit rfqs" on public.rfqs;
create policy "website can submit rfqs"
  on public.rfqs for insert to anon
  with check (status = 'new' and char_length(email) between 3 and 320);

-- Private bucket for uploaded drawings (50 MB per file)
insert into storage.buckets (id, name, public, file_size_limit)
values ('rfq-files', 'rfq-files', false, 52428800)
on conflict (id) do nothing;

drop policy if exists "website can upload rfq files" on storage.objects;
create policy "website can upload rfq files"
  on storage.objects for insert to anon
  with check (bucket_id = 'rfq-files');
