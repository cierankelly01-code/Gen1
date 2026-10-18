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

-- ---------------------------------------------------------------------------
-- Hardening (18 Oct 2026). Safe to re-run. The browser checks in site.js are
-- for convenience only; these are the rules that actually hold.
-- ---------------------------------------------------------------------------

-- Size limits on every field, so nobody can stuff megabytes into the table
alter table public.rfqs drop constraint if exists rfqs_sane_sizes;
alter table public.rfqs add constraint rfqs_sane_sizes check (
  char_length(name) between 1 and 120 and char_length(company) between 1 and 160
  and email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'
  and coalesce(char_length(phone), 0) <= 40 and coalesce(char_length(country), 0) <= 80
  and char_length(part) between 1 and 2000 and char_length(annual_volume) <= 80
  and coalesce(char_length(prototype_qty), 0) <= 80 and coalesce(char_length(material), 0) <= 200
  and coalesce(char_length(finish), 0) <= 200 and coalesce(char_length(ppap), 0) <= 40
  and coalesce(char_length(needed_by), 0) <= 80 and coalesce(char_length(notes), 0) <= 5000
  and coalesce(char_length(source), 0) <= 500
  and coalesce(array_length(stages, 1), 0) <= 10 and coalesce(array_length(files, 1), 0) <= 10
) not valid;  -- applies to new rows; old test rows don't block it

-- The public key can never read, change or delete RFQs (belt and braces: no policies exist for those)
revoke select, update, delete on table public.rfqs from anon;

-- Uploads: drawing/CAD types only, one random folder per submission, max 50 MB, no overwriting
update storage.buckets set public = false, file_size_limit = 52428800 where id = 'rfq-files';

drop policy if exists "website can upload rfq files" on storage.objects;
create policy "website can upload rfq files"
  on storage.objects for insert to anon
  with check (
    bucket_id = 'rfq-files'
    and (storage.foldername(name))[1] ~ '^[0-9a-z-]{8,36}$'
    and array_length(storage.foldername(name), 1) = 1
    and lower(storage.extension(name)) in ('step','stp','igs','iges','x_t','dxf','dwg','pdf','zip')
    and char_length(name) <= 200
  );
-- No select/update/delete policies for anon on storage.objects: uploaded drawings can't be listed,
-- downloaded or replaced with the public key. Genex staff read them with their own login.
