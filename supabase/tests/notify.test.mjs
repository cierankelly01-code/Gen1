// Tests for the website's enquiry notifications. Run: cd supabase && npm ci && npm test
// The SQL runs for real in PGlite (Postgres compiled to WebAssembly) with a small stand-in for
// Supabase's storage schema. Not covered here, and only provable on the real project: the storage
// HTTP API, Supabase Vault, pg_net, pg_cron and Resend itself.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { PGlite } from '@electric-sql/pglite';
import {
  ATTACH_LIMIT, concernEmail, database, gatherFiles, health, readConfig, resendSender, rfqEmail,
  runNotifications, secretMatches, storage, toBase64,
} from '../functions/notify-enquiries/core.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const SETUP = readFileSync(join(here, '..', 'setup.sql'), 'utf8');
const NOTIFY = readFileSync(join(here, '..', 'notifications.sql'), 'utf8');
const NOTIFY_AB = NOTIFY.slice(0, NOTIFY.indexOf('-- PART C:'));
assert.ok(NOTIFY_AB.length > 1000 && NOTIFY_AB.length < NOTIFY.length, 'PART C marker not found in notifications.sql');

const PRELUDE = `
  create role anon nologin; create role authenticated nologin; create role service_role nologin bypassrls;
  grant usage on schema public to anon, authenticated, service_role;
  alter default privileges in schema public grant all on tables to service_role;
  alter default privileges in schema public grant execute on functions to anon, authenticated, service_role;
  create schema storage; grant usage on schema storage to anon, service_role;
  create table storage.buckets (id text primary key, name text, public boolean, file_size_limit bigint);
  create table storage.objects (bucket_id text, name text);
  alter table storage.objects enable row level security;
  grant insert on storage.objects to anon;
  create function storage.foldername(n text) returns text[] language sql immutable as
    $f$ select (string_to_array(n, '/'))[1:array_length(string_to_array(n, '/'), 1) - 1] $f$;
  create function storage.extension(n text) returns text language sql immutable as
    $f$ select reverse(split_part(reverse(n), '.', 1)) $f$;
`;

async function freshDb({ before } = {}) {
  const pg = new PGlite();
  await pg.exec(PRELUDE);
  await pg.exec(SETUP);
  if (before) await before(pg);
  await pg.exec(NOTIFY_AB);
  return pg;
}
const as = async (pg, role, fn) => { await pg.exec(`set role ${role}`); try { return await fn(); } finally { await pg.exec('reset role'); } };
const CONCERN = `insert into public.concerns (kind, details, anonymous, name, email, status) values ('quality', 'A bracket arrived bent', false, 'Pat Example', 'pat@example.com', 'new')`;
const RFQ = `insert into public.rfqs (name, company, email, part, annual_volume, status) values ('Sam Example', 'Example Ltd', 'sam@example.com', 'Bracket', '5000', 'new')`;

/** The same two calls the Edge Function makes, pointed at PGlite instead of PostgREST. */
const pgDb = (pg) => ({
  async rpc(name, args = {}) {
    if (name === 'claim_enquiry_notifications') {
      const r = await pg.query('select public.claim_enquiry_notifications($1, $2) as j', [args.max_rows ?? 10, args.dry_run ?? false]);
      return r.rows[0].j;
    }
    if (name === 'enquiry_notification_health') return (await pg.query('select public.enquiry_notification_health() as j')).rows[0].j;
    throw new Error('unexpected rpc ' + name);
  },
  async patch(table, id, body) {
    const keys = Object.keys(body);
    await pg.query(`update public.${table} set ${keys.map((k, i) => `${k} = $${i + 2}`).join(', ')} where id = $1`, [id, ...keys.map((k) => body[k])]);
  },
});
const liveCfg = (over = {}) => ({ ...readConfig((k) => ({
  SUPABASE_URL: 'https://proj.supabase.co', SUPABASE_SERVICE_ROLE_KEY: 'service', NOTIFY_SECRET: 's'.repeat(40), NOTIFY_MODE: 'live',
  RESEND_API_KEY: 're_test', NOTIFY_FROM: 'Genex website <website@notify.example.com>', CONCERN_TO: 'quality@example.com', RFQ_TO: 'sales@example.com',
}[k])), ...over });
const noFiles = { sizes: async () => ({}), download: async () => new Uint8Array(), link: async () => '' };
const quiet = () => {};

// ---------------------------------------------------------------- database rules

test('the public key can submit a concern, with or without files, and read nothing back', async () => {
  const pg = await freshDb();
  await as(pg, 'anon', async () => {
    await pg.exec(CONCERN);
    await pg.exec(`insert into public.concerns (kind, details, anonymous, files, status) values ('safety', 'Oil on the yard floor', true, array['0b9a3f6e-aaaa-bbbb-cccc-1234567890ab/1-photo.jpg'], 'new')`);
    await assert.rejects(pg.query('select * from public.concerns'), /permission denied/);
    await assert.rejects(pg.query('select public.claim_enquiry_notifications()'), /permission denied/);
    await assert.rejects(pg.query('select public.enquiry_notification_health()'), /permission denied/);
    await assert.rejects(pg.query('select public.poke_enquiry_notifier()'), /permission denied/);
  });
  assert.equal((await pg.query('select count(*)::int n from public.concerns')).rows[0].n, 2);
});

test('the public key cannot mark its own row as already emailed, or attach more than five files', async () => {
  const pg = await freshDb();
  await as(pg, 'anon', async () => {
    await assert.rejects(pg.exec(`insert into public.concerns (kind, details, anonymous, status, notified_at) values ('other', 'Hide this one please', true, 'new', now())`), /row-level security/);
    await assert.rejects(pg.exec(`insert into public.rfqs (name, company, email, part, annual_volume, status, notify_attempts) values ('a', 'b', 'a@b.co', 'p', '1', 'new', 99)`), /row-level security/);
    await assert.rejects(pg.exec(`insert into public.concerns (kind, details, anonymous, status, files) values ('other', 'Too many files here', true, 'new', array['a','b','c','d','e','f'])`), /concerns_files_sane/);
  });
});

test('the public key cannot back-date a row, choose its id, or send values too big to ever email', async () => {
  const pg = await freshDb();
  await as(pg, 'anon', async () => {
    await pg.exec(`insert into public.concerns (id, created_at, kind, details, anonymous, status) values ('00000000-0000-0000-0000-000000000001', '2025-01-03 09:00+00', 'safety', 'Back-dated to look ignored', true, 'new')`);
    await assert.rejects(pg.exec(`insert into public.concerns (kind, details, anonymous, name, email, status) values ('other', 'Very long email address', false, 'A', 'a@b.' || repeat('c', 400), 'new')`), /concerns_email_len/);
    await assert.rejects(pg.exec(`insert into public.rfqs (name, company, email, part, annual_volume, status, stages) values ('a', 'b', 'a@b.co', 'p', '1', 'new', array[repeat('x', 600)])`), /rfqs_arrays_sane/);
    await assert.rejects(pg.exec(`insert into public.concerns (kind, details, anonymous, status, notify_provider_id) values ('other', 'Pre-filled provider id', true, 'new', 'fake')`), /row-level security/);
  });
  const row = (await pg.query(`select id::text, created_at > now() - interval '1 minute' as fresh from public.concerns`)).rows[0];
  assert.notEqual(row.id, '00000000-0000-0000-0000-000000000001'); assert.equal(row.fresh, true);
});

test('a form with 60 rows waiting refuses the next one out loud; the other form is unaffected', async () => {
  const pg = await freshDb();
  await pg.exec(`insert into public.concerns (kind, details, anonymous, status) select 'other', 'waiting row ' || g, true, 'new' from generate_series(1, 60) g`);
  await as(pg, 'anon', async () => {
    await assert.rejects(pg.exec(CONCERN), /too many enquiries are waiting/);
    await pg.exec(RFQ);
  });
  assert.equal((await pg.query('select count(*)::int n from public.concerns')).rows[0].n, 60);
  assert.equal((await pg.query('select count(*)::int n from public.rfqs')).rows[0].n, 1);
});

test('rows that can never be sent do not hold back the ones behind them', async () => {
  const pg = await freshDb();
  await pg.exec(`insert into public.rfqs (name, company, email, part, annual_volume, status, created_at)
                 select 'Junk', 'Junk Ltd', 'junk@example.com', 'junk part', '1', 'new', now() - interval '2 hours' from generate_series(1, 50)`);
  await pg.exec(RFQ);   // the real one arrives last
  const sent = [];
  const send = async (m) => { if (m.subject.includes('Junk Ltd')) throw new Error('email provider 422: refused'); sent.push(m); return 'ok'; };
  for (let run = 0; run < 3; run++) await runNotifications({ cfg: liveCfg(), db: pgDb(pg), store: noFiles, send, log: quiet });
  assert.equal(sent.length, 1, 'the real quote request went out within three sweeps');
  // and a row that has already failed goes behind a brand-new one
  await pg.exec(RFQ);
  await pg.exec(`update public.rfqs set notify_claimed_at = now() - interval '2 hours' where notified_at is null and notify_attempts > 0`);
  await runNotifications({ cfg: liveCfg(), db: pgDb(pg), store: noFiles, send, log: quiet });
  assert.equal(sent.length, 2);
});

test('a live run stops starting new rows when its time is up, leaving them untouched for the next sweep', async () => {
  const pg = await freshDb();
  await pg.exec(`insert into public.concerns (kind, details, anonymous, status) select 'other', 'slow day row ' || g, true, 'new' from generate_series(1, 5) g`);
  let t = Date.parse('2026-11-17T12:00:00Z');
  const send = async () => { t += 45000; return 'ok'; };   // each send takes 45 seconds
  const s = await runNotifications({ cfg: liveCfg(), db: pgDb(pg), store: noFiles, send, log: quiet, now: () => new Date(t) });
  assert.equal(s.sent, 1);
  const left = (await pg.query('select count(*)::int n, sum(notify_attempts)::int tries from public.concerns where notified_at is null')).rows[0];
  assert.deepEqual(left, { n: 4, tries: 0 });
});

test('a new enquiry still saves when the wake-up call cannot be made', async () => {
  // PGlite has no pg_net or Vault, so the wake-up fails inside the trigger. The insert must not.
  const pg = await freshDb();
  await as(pg, 'anon', () => pg.exec(RFQ));
  assert.equal((await pg.query('select count(*)::int n from public.rfqs where notified_at is null')).rows[0].n, 1);
});

test('rows from before notifications existed are marked, never emailed, and a re-run touches nothing new', async () => {
  const pg = await freshDb({ before: (p) => p.exec(CONCERN + ';' + RFQ) });
  const old = (await pg.query(`select notified_at, notify_error from public.concerns`)).rows[0];
  assert.ok(old.notified_at); assert.match(old.notify_error, /never emailed/);
  assert.deepEqual(await pgDb(pg).rpc('claim_enquiry_notifications'), []);
  await pg.exec(CONCERN);
  await pg.exec(NOTIFY_AB);   // running the file a second time must not swallow the waiting row
  assert.equal((await pgDb(pg).rpc('claim_enquiry_notifications')).length, 1);
});

test('a row is claimed once, retried after five minutes, and a dry run changes nothing', async () => {
  const pg = await freshDb();
  await pg.exec(CONCERN + ';' + RFQ);
  const db = pgDb(pg);
  assert.equal((await db.rpc('claim_enquiry_notifications', { dry_run: true })).length, 2);
  assert.equal((await pg.query('select sum(notify_attempts)::int n from public.concerns')).rows[0].n, 0);
  const first = await db.rpc('claim_enquiry_notifications');
  assert.deepEqual(first.map((i) => i.table).sort(), ['concerns', 'rfqs']);
  assert.deepEqual(await db.rpc('claim_enquiry_notifications'), []);
  await pg.exec(`update public.concerns set notify_claimed_at = now() - interval '6 minutes'`);
  const again = await db.rpc('claim_enquiry_notifications');
  assert.equal(again.length, 1); assert.equal(again[0].row.notify_attempts, 2);
  await pg.exec(`update public.concerns set notify_attempts = 6, notify_claimed_at = now() - interval '30 minutes'`);
  assert.deepEqual(await db.rpc('claim_enquiry_notifications'), [], 'after six tries it waits an hour');
});

test('the daily cap stops a flood of rows becoming a flood of emails, and health shows them waiting', async () => {
  const pg = await freshDb();
  await pg.exec(`insert into public.concerns (kind, details, anonymous, status, notified_at)
                 select 'other', 'sent earlier today ' || g, true, 'new', now() - interval '1 hour' from generate_series(1, 60) g`);
  await pg.exec(`insert into public.concerns (kind, details, anonymous, status, created_at) values ('other', 'one more arrives', true, 'new', now() - interval '20 minutes')`);
  assert.deepEqual(await pgDb(pg).rpc('claim_enquiry_notifications'), []);
  assert.deepEqual(await pgDb(pg).rpc('claim_enquiry_notifications', { dry_run: true }), [], 'the cap holds in a dry run too');
  const h = await pgDb(pg).rpc('enquiry_notification_health');
  assert.equal(h.pending, 1); assert.equal(h.stale, 1); assert.ok(h.oldest_minutes >= 19);
  // the cap is per form: junk on the concern form must not hold back a quote request
  await pg.exec(RFQ);
  const claimed = await pgDb(pg).rpc('claim_enquiry_notifications');
  assert.deepEqual(claimed.map((i) => i.table), ['rfqs']);
});

test('concern uploads: photos and documents in one random folder only', async () => {
  const pg = await freshDb({ before: null });
  const put = (bucket, name) => as(pg, 'anon', () => pg.query('insert into storage.objects (bucket_id, name) values ($1, $2)', [bucket, name]));
  await put('concern-files', '0b9a3f6e-aaaa-bbbb-cccc-1234567890ab/1-photo.JPG');
  await put('concern-files', 'mhl2k3j4/2-report.docx');
  await assert.rejects(put('concern-files', '0b9a3f6e-aaaa-bbbb-cccc-1234567890ab/run.exe'), /row-level security/);
  await assert.rejects(put('concern-files', '0b9a3f6e-aaaa-bbbb-cccc-1234567890ab/drawings.zip'), /row-level security/);
  await assert.rejects(put('concern-files', 'photo.jpg'), /row-level security/);
  await assert.rejects(put('concern-files', 'a/b/photo.jpg'), /row-level security/);
  await assert.rejects(put('some-other-bucket', '0b9a3f6e-aaaa-bbbb-cccc-1234567890ab/photo.jpg'), /row-level security/);
  await assert.rejects(as(pg, 'anon', () => pg.query('select name from storage.objects')), /permission denied/);
  await assert.rejects(as(pg, 'anon', () => pg.query('delete from storage.objects')), /permission denied/);
  assert.equal((await pg.query('select count(*)::int n from storage.objects')).rows[0].n, 2);
  assert.equal((await pg.query(`select public, file_size_limit::int s from storage.buckets where id = 'concern-files'`)).rows[0].public, false);
});

// ---------------------------------------------------------------- a whole run, database to email

test('live: each waiting row is emailed once to the right mailbox and then marked sent', async () => {
  const pg = await freshDb(); await pg.exec(CONCERN + ';' + RFQ);
  const sent = [];
  const send = async (m) => { sent.push(m); return 'id-' + sent.length; };
  const s1 = await runNotifications({ cfg: liveCfg(), db: pgDb(pg), store: noFiles, send, log: quiet });
  assert.deepEqual({ ok: s1.ok, sent: s1.sent, failed: s1.failed }, { ok: true, sent: 2, failed: 0 });
  const concern = sent.find((m) => m.subject.startsWith('Website concern'));
  assert.deepEqual(concern.to, ['quality@example.com']); assert.equal(concern.replyTo, 'pat@example.com');
  assert.match(concern.idempotencyKey, /^concerns-[0-9a-f-]{36}$/);
  assert.deepEqual(sent.find((m) => m.subject.startsWith('Website quote request')).to, ['sales@example.com']);
  const s2 = await runNotifications({ cfg: liveCfg(), db: pgDb(pg), store: noFiles, send, log: quiet });
  assert.equal(s2.sent, 0); assert.equal(sent.length, 2);
  assert.equal((await pgDb(pg).rpc('enquiry_notification_health')).pending, 0);
  assert.match((await pg.query('select notify_provider_id from public.concerns')).rows[0].notify_provider_id, /^id-\d$/);
});

test('a failed send is reported, leaves the row waiting with the reason, and goes out on the retry', async () => {
  const pg = await freshDb(); await pg.exec(CONCERN);
  let up = false; const sent = [];
  const send = async (m) => { if (!up) throw new Error('email provider 500: down'); sent.push(m); return 'ok'; };
  const s1 = await runNotifications({ cfg: liveCfg(), db: pgDb(pg), store: noFiles, send, log: quiet });
  assert.deepEqual({ ok: s1.ok, sent: s1.sent, failed: s1.failed }, { ok: false, sent: 0, failed: 1 });
  const row = (await pg.query('select notified_at, notify_error from public.concerns')).rows[0];
  assert.equal(row.notified_at, null); assert.match(row.notify_error, /email provider 500/);
  up = true;
  await pg.exec(`update public.concerns set notify_claimed_at = now() - interval '6 minutes'`);
  const s2 = await runNotifications({ cfg: liveCfg(), db: pgDb(pg), store: noFiles, send, log: quiet });
  assert.equal(s2.sent, 1); assert.equal(sent.length, 1);
  const after = (await pg.query('select notified_at, notify_error from public.concerns')).rows[0];
  assert.ok(after.notified_at); assert.equal(after.notify_error, null);
});

test('dry run sends nothing and leaves rows waiting; incomplete settings send nothing and say so', async () => {
  const pg = await freshDb(); await pg.exec(CONCERN);
  await pg.exec(`insert into public.concerns (kind, details, anonymous, status, files) values ('other', 'this one has a photo', true, 'new', array['${F}/1-photo.jpg'])`);
  let calls = 0; const send = async () => { calls++; return 'x'; };
  const sizesOnly = { sizes: async () => ({ '1-photo.jpg': 5000 }), download: async () => { throw new Error('a dry run must not download'); }, link: async () => { throw new Error('no links in a dry run'); } };
  const logged = [];
  const withFile = await runNotifications({ cfg: liveCfg({ live: false }), db: pgDb(pg), store: sizesOnly, send, log: (l) => logged.push(JSON.parse(l)) });
  assert.equal(withFile.wouldSend, 2); assert.equal(withFile.failed, 0);
  assert.deepEqual(logged.map((l) => [l.event, l.attached, l.notIncluded]).sort(), [['notify.dry_run', 0, 0], ['notify.dry_run', 1, 0]]);
  await pg.exec(`delete from public.concerns where files is not null`);
  const dry = await runNotifications({ cfg: liveCfg({ live: false }), db: pgDb(pg), store: noFiles, send, log: quiet });
  assert.deepEqual({ ok: dry.ok, sent: dry.sent, wouldSend: dry.wouldSend, mode: dry.mode }, { ok: true, sent: 0, wouldSend: 1, mode: 'dry run' });
  const bad = readConfig((k) => ({ SUPABASE_URL: 'https://p.supabase.co', SUPABASE_SERVICE_ROLE_KEY: 'k', NOTIFY_SECRET: 's'.repeat(40), NOTIFY_MODE: 'live' }[k]));
  assert.deepEqual(bad.problems, ['RESEND_API_KEY', 'NOTIFY_FROM', 'CONCERN_TO', 'RFQ_TO']);
  const mis = await runNotifications({ cfg: bad, db: pgDb(pg), store: noFiles, send, log: quiet });
  assert.equal(mis.ok, false); assert.equal(mis.misconfigured, true);
  assert.equal(calls, 0);
  assert.equal((await pgDb(pg).rpc('enquiry_notification_health')).pending, 1);
});

test('health is only green when live, set up, and nothing has waited over 15 minutes', async () => {
  const pg = await freshDb();
  assert.equal((await health({ cfg: liveCfg(), db: pgDb(pg) })).ok, true);
  assert.equal((await health({ cfg: liveCfg({ live: false }), db: pgDb(pg) })).ok, false, 'dry run is not healthy');
  assert.equal((await health({ cfg: liveCfg({ problems: ['RESEND_API_KEY'] }), db: pgDb(pg) })).ok, false);
  await pg.exec(`insert into public.concerns (kind, details, anonymous, status, created_at) values ('other', 'stuck for a while', true, 'new', now() - interval '16 minutes')`);
  const h = await health({ cfg: liveCfg(), db: pgDb(pg) });
  assert.deepEqual({ ok: h.ok, pending: h.pending, stale: h.stale }, { ok: false, pending: 1, stale: 1 });
});

// ---------------------------------------------------------------- files

const fakeStore = (sizes, { failDownload } = {}) => ({
  async sizes(bucket, folder) { return Object.fromEntries(Object.entries(sizes).filter(([p]) => p.startsWith(folder + '/')).map(([p, s]) => [p.slice(folder.length + 1), s])); },
  async download(bucket, path) { if (failDownload === path) throw new Error('nope'); return new TextEncoder().encode('file:' + path); },
  async link(bucket, path, seconds) { return `https://proj.supabase.co/storage/v1/object/sign/${bucket}/${path}?token=t&s=${seconds}`; },
});
const F = 'aaaaaaaa-1111-2222-3333-444444444444';

test('small files are attached; a set over 20 MB is linked instead; problems are named, never dropped silently', async () => {
  const row = { files: [`${F}/1-photo.jpg`, `${F}/2-report.pdf`] };
  const small = await gatherFiles('concerns', row, fakeStore({ [`${F}/1-photo.jpg`]: 1000, [`${F}/2-report.pdf`]: 2000 }));
  assert.deepEqual(small.attachments.map((a) => a.filename), ['1-photo.jpg', '2-report.pdf']);
  assert.equal(Buffer.from(small.attachments[0].content, 'base64').toString(), `file:${F}/1-photo.jpg`);
  const big = await gatherFiles('rfqs', row, fakeStore({ [`${F}/1-photo.jpg`]: ATTACH_LIMIT, [`${F}/2-report.pdf`]: 1 }));
  assert.equal(big.attachments.length, 0); assert.equal(big.links.length, 2); assert.match(big.links[0].url, /rfq-files.*s=604800/);
  const odd = await gatherFiles('concerns', { files: [`${F}/1-photo.jpg`, `${F}/gone.pdf`, '../../etc/passwd', `${F}/2-report.pdf`] },
    fakeStore({ [`${F}/1-photo.jpg`]: 10, [`${F}/2-report.pdf`]: 10 }, { failDownload: `${F}/2-report.pdf` }));
  assert.deepEqual(odd.attachments.map((a) => a.filename), ['1-photo.jpg']);
  assert.deepEqual(odd.missing.sort(), ['1 file reference that could not be read', '2-report.pdf', 'gone.pdf'].sort());
  // text typed into the files column is never echoed into the email, and a repeated path is only attached once
  const typed = await gatherFiles('rfqs', { files: ['drawing.pdf - blocked, download from https://evil.example/x', `${F}/1-photo.jpg`, `${F}/1-photo.jpg`] }, fakeStore({ [`${F}/1-photo.jpg`]: 10 }));
  assert.equal(typed.attachments.length, 1);
  assert.ok(!JSON.stringify(typed).includes('evil.example'));
  // a dry run works out what it would do without downloading or linking anything
  const noTouch = { sizes: fakeStore({ [`${F}/1-photo.jpg`]: 1000, [`${F}/2-report.pdf`]: 2000 }).sizes,
    download: async () => { throw new Error('a dry run must not download'); }, link: async () => { throw new Error('a dry run must not make links'); } };
  const dry = await gatherFiles('concerns', row, noTouch, { contents: false });
  assert.deepEqual(dry, { attachments: [{ filename: '1-photo.jpg' }, { filename: '2-report.pdf' }], links: [], missing: [] });
  const down = await gatherFiles('concerns', row, { sizes: async () => { throw new Error('store down'); } });
  assert.deepEqual(down.missing, ['1-photo.jpg', '2-report.pdf']);
  assert.deepEqual(await gatherFiles('concerns', { files: null }, fakeStore({})), { attachments: [], links: [], missing: [] });
});

test('base64 matches Node for sizes around the chunk boundary', () => {
  for (const n of [0, 1, 2, 3, 29999, 30000, 30001, 90001]) {
    const b = Uint8Array.from({ length: n }, (_, i) => (i * 31) % 256);
    assert.equal(toBase64(b), Buffer.from(b).toString('base64'), `length ${n}`);
  }
});

// ---------------------------------------------------------------- the emails

test('concern email: escaped, single-line subject, reply goes to the reporter, files explained', () => {
  const cfg = liveCfg({ help: 'the website team' });
  const row = { id: 'x', kind: 'quality', details: '<script>alert(1)</script>\nSecond line', reference: 'PO 123\r\nBcc: evil@example.com',
    anonymous: false, name: 'Pat <b>', email: 'pat@example.com', company: 'Example & Sons', created_at: '2026-11-17T12:00:00Z' };
  const m = concernEmail(row, { attachments: [{ filename: '1-photo.jpg', content: 'AA==' }], links: [], missing: ['2-big.pdf'] }, cfg);
  assert.equal(m.subject, 'Website concern: Quality of a part or delivery (ref PO 123 Bcc: evil@example.com)');
  assert.ok(!/[\r\n]/.test(m.subject));
  assert.ok(!m.html.includes('<script>')); assert.ok(m.html.includes('&lt;script&gt;alert(1)&lt;/script&gt;'));
  assert.ok(m.html.includes('Example &amp; Sons'));
  assert.equal(m.replyTo, 'pat@example.com');
  assert.match(m.text, /17 Nov 2026, 12:00 \(UK time\)/);
  assert.match(m.text, /1 file\(s\) are attached/); assert.match(m.text, /could not be included in this email: 2-big\.pdf\. Ask the website team/);
  assert.match(m.text, /aims to respond within 24 hours/);
});

test('anonymous concern: no contact details, no reply address, and it says so', () => {
  const m = concernEmail({ kind: 'environmental', details: 'Smell of solvent by the gate', anonymous: true, name: 'should not show', email: 'x@y.co', phone: '123', created_at: '2026-07-01T09:30:00Z' },
    { attachments: [], links: [], missing: [] }, liveCfg());
  assert.equal(m.replyTo, null);
  assert.ok(!m.text.includes('should not show') && !m.text.includes('x@y.co') && !m.text.includes('123'));
  assert.match(m.text, /Reported anonymously/); assert.match(m.text, /10:30 \(UK time\)/, 'summer time is handled');
});

test('quote email: all the fields, the NDA flag, links when drawings are too big, a bad reply address is not used', () => {
  const row = { name: 'Sam', company: 'Example Ltd', email: 'not-an-email', part: 'Bracket, 3 mm mild steel', annual_volume: '5000', stages: ['press', 'weld'], nda_requested: true, created_at: '2026-11-17T12:00:00Z' };
  const m = rfqEmail(row, { attachments: [], links: [{ filename: '1-part.step', url: 'https://proj.supabase.co/storage/v1/object/sign/rfq-files/a/1-part.step?token=t' }], missing: [] }, liveCfg());
  assert.equal(m.subject, 'Website quote request: Example Ltd - Bracket, 3 mm mild steel');
  assert.equal(m.replyTo, null); assert.match(m.text, /No usable email address/);
  assert.match(m.text, /NDA requested/); assert.match(m.text, /Stages wanted: press, weld/);
  assert.match(m.text, /These links work for 7 days/); assert.ok(m.html.includes('<a href="https://proj.supabase.co/storage/v1/object/sign/rfq-files/a/1-part.step?token=t">1-part.step</a>'));
});

// ---------------------------------------------------------------- plumbing

test('the secret check accepts only the exact secret', () => {
  const s = 'k'.repeat(40);
  assert.equal(secretMatches(s, s), true);
  for (const bad of ['', 'k'.repeat(39), 'k'.repeat(41), 'x' + 'k'.repeat(39), null, undefined]) assert.equal(secretMatches(bad, s), false);
  assert.equal(secretMatches('short', 'short'), false, 'a short secret is never accepted');
  assert.equal(secretMatches('', ''), false);
});

test('requests to the email provider, database and file store have the right shape', async () => {
  const calls = [];
  const fake = (reply) => async (url, init = {}) => { calls.push({ url, ...init }); return { ok: true, status: 200, json: async () => reply, arrayBuffer: async () => new Uint8Array([1, 2]).buffer }; };
  const id = await resendSender({ apiKey: 're_k', from: 'Genex <w@n.example.com>', fetchImpl: fake({ id: 'em_1' }) })(
    { to: ['q@example.com'], subject: 's', text: 't', html: '<p>h</p>', replyTo: 'pat@example.com', attachments: [{ filename: 'a.jpg', content: 'AA==' }], idempotencyKey: 'concerns-1' });
  assert.equal(id, 'em_1');
  assert.equal(calls[0].url, 'https://api.resend.com/emails'); assert.equal(calls[0].headers['Idempotency-Key'], 'concerns-1');
  assert.deepEqual(JSON.parse(calls[0].body), { from: 'Genex <w@n.example.com>', to: ['q@example.com'], subject: 's', text: 't', html: '<p>h</p>', reply_to: 'pat@example.com', attachments: [{ filename: 'a.jpg', content: 'AA==' }] });
  await assert.rejects(resendSender({ apiKey: 'k', from: 'f', fetchImpl: async () => ({ ok: false, status: 403, json: async () => ({ message: 'domain not verified' }) }) })(
    { to: ['q@example.com'], subject: 's', text: 't', html: 'h', idempotencyKey: 'k' }), /email provider 403: domain not verified/);

  const cfg = liveCfg();
  await database(cfg, fake([])).rpc('claim_enquiry_notifications', { max_rows: 10, dry_run: false });
  assert.equal(calls.at(-1).url, 'https://proj.supabase.co/rest/v1/rpc/claim_enquiry_notifications'); assert.equal(calls.at(-1).headers.Authorization, 'Bearer service');
  await database(cfg, fake({})).patch('concerns', 'abc', { notify_error: null });
  assert.equal(calls.at(-1).url, 'https://proj.supabase.co/rest/v1/concerns?id=eq.abc'); assert.equal(calls.at(-1).method, 'PATCH');
  await assert.rejects(database(cfg, fake({})).patch('users', 'abc', {}), /unknown table/);
  assert.deepEqual(await storage(cfg, fake([{ name: '1-a.jpg', metadata: { size: 12 } }])).sizes('concern-files', F), { '1-a.jpg': 12 });
  assert.equal(calls.at(-1).url, 'https://proj.supabase.co/storage/v1/object/list/concern-files'); assert.deepEqual(JSON.parse(calls.at(-1).body), { prefix: F, limit: 100 });
  assert.equal(await storage(cfg, fake({ signedURL: '/object/sign/rfq-files/a/b.pdf?token=t' })).link('rfq-files', 'a/b.pdf', 60), 'https://proj.supabase.co/storage/v1/object/sign/rfq-files/a/b.pdf?token=t');
  assert.deepEqual([...await storage(cfg, fake({})).download('rfq-files', 'a/b c.pdf')], [1, 2]);
  assert.equal(calls.at(-1).url, 'https://proj.supabase.co/storage/v1/object/rfq-files/a/b%20c.pdf');
});
