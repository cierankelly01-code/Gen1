-- Genex UK website: concern attachments, and an email to Genex for every new quote request and concern.
-- Run once in Supabase > SQL Editor, AFTER setup.sql. Safe to re-run.
-- If setup.sql is ever run again, run this file again straight after it (setup.sql puts back older, looser insert rules).
-- Run it BEFORE the live site takes real enquiries: on its first run, every row already in the tables
-- is treated as a test from the preview and is marked "never emailed".
-- The email itself is sent by the Edge Function in supabase/functions/notify-enquiries (see its README).
--
-- Part A is plain Postgres and is tested on every push (supabase/tests). Parts B and C use Supabase's
-- file store, scheduler and outbound-request extensions and have only been checked by reading.

-- ===========================================================================
-- >>> PART A: columns, rules and functions
-- ===========================================================================

-- A1. Concern attachments: up to five file paths per report
alter table public.concerns add column if not exists files text[];
alter table public.concerns drop constraint if exists concerns_files_sane;
alter table public.concerns add constraint concerns_files_sane check (
  coalesce(array_length(files, 1), 0) <= 5
  and coalesce(char_length(array_to_string(files, ',')), 0) <= 1000
);

-- A2. Bookkeeping for the notification email, on both tables.
--     Rows that arrived before this existed (test enquiries from the preview) are marked, not emailed.
do $$
declare t text;
begin
  foreach t in array array['rfqs', 'concerns'] loop
    if not exists (select 1 from information_schema.columns
                   where table_schema = 'public' and table_name = t and column_name = 'notified_at') then
      execute format('alter table public.%I add column notified_at timestamptz, add column notify_claimed_at timestamptz, '
                  || 'add column notify_attempts integer not null default 0, add column notify_error text', t);
      execute format('update public.%I set notified_at = now(), notify_error = %L', t,
                     'arrived before email notifications were switched on; never emailed');
    end if;
  end loop;
end $$;

--     The email provider's id for the sent message, so a bounce can be traced later
alter table public.rfqs add column if not exists notify_provider_id text;
alter table public.concerns add column if not exists notify_provider_id text;

--     Size limits the first setup missed. A huge value would make an email the provider refuses for ever.
alter table public.concerns drop constraint if exists concerns_email_len;
alter table public.concerns add constraint concerns_email_len
  check (coalesce(char_length(email), 0) <= 320) not valid;
alter table public.rfqs drop constraint if exists rfqs_arrays_sane;
alter table public.rfqs add constraint rfqs_arrays_sane check (
  coalesce(char_length(array_to_string(stages, ',')), 0) <= 500
  and coalesce(char_length(array_to_string(files, ',')), 0) <= 2500) not valid;

-- A3. The public key still can only INSERT, and now cannot pre-mark its own row as "already emailed"
drop policy if exists "website can submit rfqs" on public.rfqs;
create policy "website can submit rfqs"
  on public.rfqs for insert to anon
  with check (status = 'new' and char_length(email) between 3 and 320
              and notified_at is null and notify_claimed_at is null and notify_attempts = 0
              and notify_error is null and notify_provider_id is null);

drop policy if exists "website can submit concerns" on public.concerns;
create policy "website can submit concerns"
  on public.concerns for insert to anon
  with check (status = 'new'
              and notified_at is null and notify_claimed_at is null and notify_attempts = 0
              and notify_error is null and notify_provider_id is null);

--     The website cannot choose a row's id or back-date it: both are set here for the public key.
--     (Runs as the caller, so current_user is the role the request came in as.)
create or replace function public.stamp_enquiry()
returns trigger language plpgsql set search_path = '' as $$
begin
  if current_user = 'anon' then
    new.id := gen_random_uuid();
    new.created_at := now();
  end if;
  return new;
end $$;
drop trigger if exists stamp_enquiry on public.concerns;
create trigger stamp_enquiry before insert on public.concerns
  for each row execute function public.stamp_enquiry();
drop trigger if exists stamp_enquiry on public.rfqs;
create trigger stamp_enquiry before insert on public.rfqs
  for each row execute function public.stamp_enquiry();

--     A form with 60 rows still waiting to be emailed refuses new ones, so the visitor sees
--     "couldn't send, call us" instead of a thank-you for a report nobody will read for days.
--     To clear junk by hand:  delete from public.concerns where notified_at is null and <what marks the junk>;
create or replace function public.refuse_when_enquiry_queue_full()
returns trigger language plpgsql security definer set search_path = '' as $$
declare waiting integer;
begin
  execute format('select count(*) from public.%I where notified_at is null', tg_table_name) into waiting;
  if waiting >= 60 then
    raise exception 'too many enquiries are waiting to be emailed' using errcode = '53400';
  end if;
  return new;
end $$;
drop trigger if exists refuse_when_enquiry_queue_full on public.concerns;
create trigger refuse_when_enquiry_queue_full before insert on public.concerns
  for each row execute function public.refuse_when_enquiry_queue_full();
drop trigger if exists refuse_when_enquiry_queue_full on public.rfqs;
create trigger refuse_when_enquiry_queue_full before insert on public.rfqs
  for each row execute function public.refuse_when_enquiry_queue_full();

-- A4. Hands the notifier the rows that still need an email: never-tried rows first, then oldest,
--     so a row that keeps failing can never hold back the ones behind it.
--     A claimed row is left alone for 5 minutes (an hour after six failed tries), so two runs
--     never email the same row. daily_cap (per form) stops a flood of junk rows becoming a flood of emails.
create or replace function public.claim_enquiry_notifications(
  max_rows integer default 10, dry_run boolean default false, daily_cap integer default 60)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare
  result jsonb := '[]'::jsonb;
  room_c integer;   -- how many concerns may still go today (the cap is per form,
  room_q integer;   -- so junk sent to one form cannot hold back the other)
  r record;
begin
  select least(max_rows, daily_cap - count(*)) into room_c from public.concerns
   where notified_at > now() - interval '24 hours' and notify_error is null;
  select least(max_rows, daily_cap - count(*)) into room_q from public.rfqs
   where notified_at > now() - interval '24 hours' and notify_error is null;

  if dry_run then   -- look, don't touch: a dry run must not use up tries or hold rows back
    select coalesce(jsonb_agg(s.item), '[]'::jsonb) into result from (
      (select jsonb_build_object('table', 'concerns', 'row', to_jsonb(c)) as item
         from public.concerns c where c.notified_at is null order by c.created_at limit greatest(room_c, 0))
      union all
      (select jsonb_build_object('table', 'rfqs', 'row', to_jsonb(q))
         from public.rfqs q where q.notified_at is null order by q.created_at limit greatest(room_q, 0))
    ) s;
    return result;
  end if;

  if room_c > 0 then
    for r in
      update public.concerns c
         set notify_claimed_at = now(), notify_attempts = c.notify_attempts + 1
       where c.id in (
         select x.id from public.concerns x
          where x.notified_at is null
            and (x.notify_claimed_at is null or x.notify_claimed_at < now() -
                 case when x.notify_attempts < 6 then interval '5 minutes' else interval '1 hour' end)
          order by x.notify_attempts, x.created_at limit room_c for update skip locked)
      returning to_jsonb(c) as j
    loop
      result := result || jsonb_build_object('table', 'concerns', 'row', r.j);
    end loop;
  end if;

  if room_q > 0 then
    for r in
      update public.rfqs q
         set notify_claimed_at = now(), notify_attempts = q.notify_attempts + 1
       where q.id in (
         select x.id from public.rfqs x
          where x.notified_at is null
            and (x.notify_claimed_at is null or x.notify_claimed_at < now() -
                 case when x.notify_attempts < 6 then interval '5 minutes' else interval '1 hour' end)
          order by x.notify_attempts, x.created_at limit room_q for update skip locked)
      returning to_jsonb(q) as j
    loop
      result := result || jsonb_build_object('table', 'rfqs', 'row', r.j);
    end loop;
  end if;
  return result;
end $$;

-- A5. What the uptime monitor reads: how many rows are waiting, and how many have waited too long
create or replace function public.enquiry_notification_health()
returns jsonb language sql stable security definer set search_path = '' as $$
  select jsonb_build_object(
    'pending', count(*),
    'stale', count(*) filter (where p.created_at < now() - interval '15 minutes'),
    'oldest_minutes', coalesce(floor(extract(epoch from now() - min(p.created_at)) / 60), 0))
  from (select created_at from public.concerns where notified_at is null
        union all
        select created_at from public.rfqs where notified_at is null) p;
$$;

-- A6. Wakes the notifier. The address and the shared secret live in Supabase Vault (never in this repo).
--     With no Vault entries yet it does nothing, and rows simply wait.
create or replace function public.poke_enquiry_notifier()
returns void language plpgsql security definer set search_path = '' as $$
declare u text; s text;
begin
  select decrypted_secret into u from vault.decrypted_secrets where name = 'notify_enquiries_url';
  select decrypted_secret into s from vault.decrypted_secrets where name = 'notify_enquiries_secret';
  if u is null or s is null then return; end if;
  perform net.http_post(
    url := u,
    body := '{}'::jsonb,
    headers := jsonb_build_object('Content-Type', 'application/json', 'x-notify-secret', s),
    timeout_milliseconds := 60000);
end $$;

create or replace function public.poke_enquiry_notifier_trigger()
returns trigger language plpgsql security definer set search_path = '' as $$
begin
  begin
    perform public.poke_enquiry_notifier();
  exception when others then
    null;   -- a failed wake-up must never block an enquiry; the five-minute sweep sends it
  end;
  return null;
end $$;

drop trigger if exists poke_enquiry_notifier on public.concerns;
create trigger poke_enquiry_notifier after insert on public.concerns
  for each statement execute function public.poke_enquiry_notifier_trigger();
drop trigger if exists poke_enquiry_notifier on public.rfqs;
create trigger poke_enquiry_notifier after insert on public.rfqs
  for each statement execute function public.poke_enquiry_notifier_trigger();

-- A7. Only the server-side key may call these. The website's public key cannot.
revoke all on function public.claim_enquiry_notifications(integer, boolean, integer) from public, anon, authenticated;
revoke all on function public.enquiry_notification_health() from public, anon, authenticated;
revoke all on function public.poke_enquiry_notifier() from public, anon, authenticated;
revoke all on function public.poke_enquiry_notifier_trigger() from public, anon, authenticated;
revoke all on function public.refuse_when_enquiry_queue_full() from public, anon, authenticated;
revoke all on function public.stamp_enquiry() from public, anon, authenticated;
grant execute on function public.claim_enquiry_notifications(integer, boolean, integer) to service_role;
grant execute on function public.enquiry_notification_health() to service_role;
-- <<< PART A

-- ===========================================================================
-- PART B: private file store for concern attachments (Supabase Storage)
-- ===========================================================================
insert into storage.buckets (id, name, public, file_size_limit)
values ('concern-files', 'concern-files', false, 20971520)
on conflict (id) do update set public = false, file_size_limit = 20971520;

-- Photos and office documents only, one random folder per report, no overwriting.
-- No select/update/delete policy for anon: files can't be listed, read or replaced with the public key.
drop policy if exists "website can upload concern files" on storage.objects;
create policy "website can upload concern files"
  on storage.objects for insert to anon
  with check (
    bucket_id = 'concern-files'
    and (storage.foldername(name))[1] ~ '^[0-9a-z-]{8,36}$'
    and array_length(storage.foldername(name), 1) = 1
    and lower(storage.extension(name)) in ('jpg','jpeg','png','webp','heic','heif','pdf','doc','docx','xls','xlsx')
    and char_length(name) <= 200
  );

-- ===========================================================================
-- PART C: outbound requests and the five-minute sweep (pg_net, pg_cron)
-- ===========================================================================
create extension if not exists pg_net;
create extension if not exists pg_cron;
select cron.schedule('notify-enquiries-sweep', '*/5 * * * *', $$select public.poke_enquiry_notifier()$$);

-- After the Edge Function is deployed, store its address and secret ONCE (values are not kept in this repo):
--   select vault.create_secret('https://<project-ref>.supabase.co/functions/v1/notify-enquiries', 'notify_enquiries_url');
--   select vault.create_secret('<the same value as the function secret NOTIFY_SECRET>', 'notify_enquiries_secret');
-- Check:  select jobname, schedule from cron.job;   select public.enquiry_notification_health();
