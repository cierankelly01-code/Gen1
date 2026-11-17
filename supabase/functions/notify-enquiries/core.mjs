// Genex website: email every new quote request and concern to the right Genex mailbox.
// Pure logic with fetch injected, so the same code runs in the Edge Function (Deno) and under
// `node --test` with a fake database and a fake email provider (supabase/tests/notify.test.mjs).
//
// How it works: the database hands over rows that have not been emailed yet
// (public.claim_enquiry_notifications in supabase/notifications.sql). Each one is emailed through
// Resend and only then marked as sent. A row that fails stays unsent and is retried by the
// five-minute sweep. /health goes red when anything has been waiting more than 15 minutes.

const RESEND_URL = 'https://api.resend.com/emails';
export const ATTACH_LIMIT = 20 * 1024 * 1024; // attach files up to this total; above it, email links instead
export const LINK_DAYS = 7;
const RUN_BUDGET_MS = 40000;   // stop starting new rows after this, to answer inside the database's 60 s wait
const MAX_ROUNDS = 20;
const PATH_OK = /^[0-9a-z-]{8,36}\/[\w.\-]{1,120}$/;
const EMAIL_OK = /^[^@\s<>",;]+@[^@\s<>",;]+\.[^@\s<>",;]+$/;

export const TABLES = {
  concerns: { bucket: 'concern-files' },
  rfqs: { bucket: 'rfq-files' },
};

const KIND = {
  quality: 'Quality of a part or delivery',
  environmental: 'Environmental',
  safety: 'Health & safety',
  other: 'Something else',
};

const list = (v) => (v ?? '').split(',').map((s) => s.trim()).filter(Boolean);

/** Reads settings from the environment. `problems` names what is missing; nothing is sent while it is non-empty. */
export function readConfig(get) {
  const cfg = {
    supabaseUrl: (get('SUPABASE_URL') ?? '').replace(/\/$/, ''),
    serviceKey: get('SUPABASE_SERVICE_ROLE_KEY') ?? '',
    secret: get('NOTIFY_SECRET') ?? '',
    live: (get('NOTIFY_MODE') ?? '') === 'live',
    resendKey: get('RESEND_API_KEY') ?? '',
    from: get('NOTIFY_FROM') ?? '',
    to: { concerns: list(get('CONCERN_TO')), rfqs: list(get('RFQ_TO')) },
    help: get('NOTIFY_HELP_CONTACT') ?? '',
    problems: [],
  };
  if (!cfg.supabaseUrl) cfg.problems.push('SUPABASE_URL');
  if (!cfg.serviceKey) cfg.problems.push('SUPABASE_SERVICE_ROLE_KEY');
  if (cfg.secret.length < 32) cfg.problems.push('NOTIFY_SECRET (32 or more characters)');
  if (cfg.live) {
    if (!cfg.resendKey) cfg.problems.push('RESEND_API_KEY');
    if (!cfg.from) cfg.problems.push('NOTIFY_FROM');
    for (const [table, key] of [['concerns', 'CONCERN_TO'], ['rfqs', 'RFQ_TO']]) {
      if (!cfg.to[table].length || !cfg.to[table].every((a) => EMAIL_OK.test(a))) cfg.problems.push(key);
    }
  }
  return cfg;
}

/** Compares the caller's secret without leaking how much of it matched. */
export function secretMatches(given, expected) {
  if (!expected || expected.length < 32 || typeof given !== 'string') return false;
  let diff = given.length ^ expected.length;
  for (let i = 0; i < expected.length; i++) diff |= (given.charCodeAt(i % (given.length || 1)) || 0) ^ expected.charCodeAt(i);
  return diff === 0;
}

/** Every outbound call gets a time limit, so a service that hangs becomes an ordinary, recorded failure. */
const timed = (fetchImpl, ms) => (url, init = {}) => fetchImpl(url, { ...init, signal: AbortSignal.timeout(ms) });

/** Database access with the service key (server side only; never in the browser). */
export function database(cfg, rawFetch = fetch) {
  const fetchImpl = timed(rawFetch, 10000);
  const headers = { apikey: cfg.serviceKey, Authorization: `Bearer ${cfg.serviceKey}`, 'Content-Type': 'application/json' };
  return {
    async rpc(name, args = {}) {
      const res = await fetchImpl(`${cfg.supabaseUrl}/rest/v1/rpc/${name}`, { method: 'POST', headers, body: JSON.stringify(args) });
      if (!res.ok) throw new Error(`database ${name} ${res.status}`);
      return res.json();
    },
    async patch(table, id, body) {
      if (!TABLES[table]) throw new Error(`unknown table ${table}`);
      const res = await fetchImpl(`${cfg.supabaseUrl}/rest/v1/${table}?id=eq.${encodeURIComponent(id)}`, {
        method: 'PATCH', headers: { ...headers, Prefer: 'return=minimal' }, body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(`database update ${table} ${res.status}`);
    },
  };
}

/** File store access with the service key: sizes, contents and time-limited links. */
export function storage(cfg, rawFetch = fetch) {
  const fetchImpl = timed(rawFetch, 20000);
  const headers = { apikey: cfg.serviceKey, Authorization: `Bearer ${cfg.serviceKey}` };
  const base = `${cfg.supabaseUrl}/storage/v1`;
  const enc = (path) => path.split('/').map(encodeURIComponent).join('/');
  return {
    /** Returns { name: size } for one folder of a bucket. */
    async sizes(bucket, folder) {
      const res = await fetchImpl(`${base}/object/list/${bucket}`, {
        method: 'POST', headers: { ...headers, 'Content-Type': 'application/json' }, body: JSON.stringify({ prefix: folder, limit: 100 }),
      });
      if (!res.ok) throw new Error(`file list ${res.status}`);
      const out = {};
      for (const o of await res.json()) out[o.name] = Number(o?.metadata?.size);
      return out;
    },
    async download(bucket, path) {
      const res = await fetchImpl(`${base}/object/${bucket}/${enc(path)}`, { headers });
      if (!res.ok) throw new Error(`file download ${res.status}`);
      return new Uint8Array(await res.arrayBuffer());
    },
    async link(bucket, path, seconds) {
      const res = await fetchImpl(`${base}/object/sign/${bucket}/${enc(path)}`, {
        method: 'POST', headers: { ...headers, 'Content-Type': 'application/json' }, body: JSON.stringify({ expiresIn: seconds }),
      });
      if (!res.ok) throw new Error(`file link ${res.status}`);
      const { signedURL } = await res.json();
      if (!signedURL) throw new Error('file link missing');
      return `${base}${signedURL}`;
    },
  };
}

export function toBase64(bytes) {
  let out = '';
  for (let i = 0; i < bytes.length; i += 30000) out += btoa(String.fromCharCode(...bytes.subarray(i, i + 30000))); // 30000 is a multiple of 3
  return out;
}

/**
 * Works out how the files on a row reach the reader: attached (small enough), linked (too big to
 * attach), or named as not included (anything that went wrong). A file problem never stops the email.
 */
export async function gatherFiles(table, row, store, { contents = true } = {}) {
  const bucket = TABLES[table].bucket;
  const out = { attachments: [], links: [], missing: [] };
  const paths = Array.isArray(row.files) ? [...new Set(row.files.filter((p) => typeof p === 'string'))] : [];
  if (!paths.length) return out;
  const good = paths.filter((p) => PATH_OK.test(p));
  // The files column is typed by whoever posted the row. A path that isn't in our own format is
  // counted, never printed: its text must not appear in the email as if the system had written it.
  const invalid = paths.length - good.length;
  if (invalid) out.missing.push(`${invalid} file reference${invalid > 1 ? 's' : ''} that could not be read`);
  const name = (p) => p.slice(p.indexOf('/') + 1);
  let sizes = {};
  try {
    for (const folder of new Set(good.map((p) => p.slice(0, p.indexOf('/'))))) {
      const s = await store.sizes(bucket, folder);
      for (const [n, size] of Object.entries(s)) sizes[`${folder}/${n}`] = size;
    }
  } catch { sizes = {}; }
  const known = good.filter((p) => Number.isFinite(sizes[p]));
  for (const p of good) if (!Number.isFinite(sizes[p])) out.missing.push(name(p));
  const total = known.reduce((n, p) => n + sizes[p], 0);
  for (const p of known) {
    try {
      // A dry run only needs to know what it would do. Downloading every waiting file on every
      // five-minute sweep would burn through the file store's data allowance for nothing.
      if (!contents) (total <= ATTACH_LIMIT ? out.attachments : out.links).push({ filename: name(p) });
      else if (total <= ATTACH_LIMIT) out.attachments.push({ filename: name(p), content: toBase64(await store.download(bucket, p)) });
      else out.links.push({ filename: name(p), url: await store.link(bucket, p, LINK_DAYS * 86400) });
    } catch { out.missing.push(name(p)); }
  }
  return out;
}

const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const oneLine = (s, max = 150) => String(s ?? '').replace(/[\r\n\t]+/g, ' ').replace(/\s{2,}/g, ' ').trim().slice(0, max);
const when = (iso) => {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return 'unknown';
  return new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/London', dateStyle: 'medium', timeStyle: 'short' }).format(d) + ' (UK time)';
};

/** Turns [label, value] pairs and notes into matching plain-text and HTML bodies. Everything is escaped. */
function render(title, intro, fields, notes) {
  const shown = fields.filter(([, v]) => v !== null && v !== undefined && String(v).trim() !== '');
  const text = [title, '', ...intro, '', ...shown.map(([k, v]) => `${k}: ${v}`), '', ...notes.map((n) => n.text)].join('\n');
  const html = `<div style="font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.5;color:#111">`
    + `<h2 style="font-size:18px;margin:0 0 12px">${esc(title)}</h2>`
    + intro.map((p) => `<p style="margin:0 0 12px">${esc(p)}</p>`).join('')
    + `<table cellpadding="6" style="border-collapse:collapse">`
    + shown.map(([k, v]) => `<tr><td style="vertical-align:top;color:#555;white-space:nowrap">${esc(k)}</td><td style="white-space:pre-wrap">${esc(v)}</td></tr>`).join('')
    + `</table>`
    + notes.map((n) => `<p style="margin:12px 0 0;color:#555">${n.html ?? esc(n.text)}</p>`).join('')
    + `</div>`;
  return { text, html };
}

function fileNotes(files, cfg) {
  const notes = [];
  if (files.attachments.length) notes.push({ text: `${files.attachments.length} file(s) are attached to this email.` });
  if (files.links.length) {
    const ask = cfg.help ? `, ask ${cfg.help} for a new link` : ', the files are still stored and a new link can be made';
    notes.push({
      text: `Files too large to attach. These links work for ${LINK_DAYS} days; after that${ask}:\n` + files.links.map((l) => `${l.filename}: ${l.url}`).join('\n'),
      html: `Files too large to attach. These links work for ${LINK_DAYS} days; after that${esc(ask)}:<br>`
        + files.links.map((l) => `<a href="${esc(l.url)}">${esc(l.filename)}</a>`).join('<br>'),
    });
  }
  if (files.missing.length) {
    notes.push({ text: `These files were sent with it but could not be included in this email: ${files.missing.join(', ')}.${cfg.help ? ` Ask ${cfg.help} for them.` : ''}` });
  }
  return notes;
}

export function concernEmail(row, files, cfg) {
  const kind = KIND[row.kind] ?? 'Something else';
  const named = !row.anonymous && EMAIL_OK.test(row.email ?? '');
  const subject = oneLine(`Website concern: ${kind}${row.reference ? ` (ref ${row.reference})` : ''}`);
  const notes = [
    row.anonymous
      ? { text: 'Reported anonymously. No contact details were given, so there is nobody to reply to.' }
      : { text: named ? 'Replying to this email goes to the person who raised the concern.' : 'No usable email address was given.' },
    ...fileNotes(files, cfg),
    { text: 'Sent automatically by the genexuk.co.uk website. The site tells people the quality team aims to respond within 24 hours.' },
  ];
  const body = render('A concern was raised on the website', [], [
    ['Type', kind], ['Received', when(row.created_at)], ['Reference', row.reference], ['What happened', row.details],
    ['Name', row.anonymous ? null : row.name], ['Company', row.anonymous ? null : row.company],
    ['Email', row.anonymous ? null : row.email], ['Phone', row.anonymous ? null : row.phone],
  ], notes);
  return { subject, ...body, replyTo: named ? row.email : null, attachments: files.attachments };
}

export function rfqEmail(row, files, cfg) {
  const subject = oneLine(`Website quote request: ${row.company ?? 'no company given'} - ${row.part ?? ''}`);
  const notes = [
    ...(row.nda_requested ? [{ text: 'NDA requested: they asked for the mutual NDA before sharing full drawings.' }] : []),
    { text: EMAIL_OK.test(row.email ?? '') ? 'Replying to this email goes to the person who asked for the quote.' : 'No usable email address was given.' },
    ...fileNotes(files, cfg),
    { text: 'Sent automatically by the genexuk.co.uk website.' },
  ];
  const body = render('A quote was requested on the website', [], [
    ['Received', when(row.created_at)], ['Name', row.name], ['Company', row.company], ['Email', row.email], ['Phone', row.phone],
    ['Country', row.country], ['Part', row.part], ['Annual volume', row.annual_volume], ['Prototype quantity', row.prototype_qty],
    ['Material', row.material], ['Finish', row.finish], ['Stages wanted', Array.isArray(row.stages) ? row.stages.join(', ') : null],
    ['PPAP', row.ppap], ['Needed by', row.needed_by], ['Notes', row.notes],
  ], notes);
  return { subject, ...body, replyTo: EMAIL_OK.test(row.email ?? '') ? row.email : null, attachments: files.attachments };
}

/** Sends one email through Resend. The idempotency key stops a retry from sending the same row twice. */
export function resendSender({ apiKey, from, fetchImpl: rawFetch = fetch }) {
  const fetchImpl = timed(rawFetch, 30000);
  return async ({ to, subject, text, html, replyTo, attachments, idempotencyKey }) => {
    const res = await fetchImpl(RESEND_URL, {
      method: 'POST',
      headers: { Authorization: `Bearer ${apiKey}`, 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey },
      body: JSON.stringify({
        from, to, subject, text, html,
        ...(replyTo ? { reply_to: replyTo } : {}),
        ...(attachments?.length ? { attachments } : {}),
      }),
    });
    const body = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(`email provider ${res.status}: ${oneLine(body?.message ?? 'no detail', 200)}`);
    return body?.id ?? '';
  };
}

const mask = (a) => String(a).replace(/^(.).*(@.*)$/, '$1***$2');

/**
 * One run: claim what is waiting, email each row, mark it sent. Returns a summary.
 * `ok` is false when the settings are incomplete or any row failed, so the caller can answer with an error.
 */
export async function runNotifications({ cfg, db, store, send, log = console.log, now = () => new Date() }) {
  const summary = { ok: true, mode: cfg.live ? 'live' : 'dry run', sent: 0, wouldSend: 0, failed: 0 };
  if (cfg.problems.length) {
    log(JSON.stringify({ event: 'notify.misconfigured', missing: cfg.problems }));
    return { ...summary, ok: false, misconfigured: true };
  }
  // Live runs claim one row per form at a time, inside a time budget. A run that hangs or is
  // killed has then only used up a try on the row it was working on, not on a whole batch.
  const deadline = now().getTime() + RUN_BUDGET_MS;
  for (let round = 0; round < MAX_ROUNDS; round++) {
    if (now().getTime() > deadline) break;   // the rest are untouched; the next sweep takes them
    const items = await db.rpc('claim_enquiry_notifications', { max_rows: cfg.live ? 1 : 10, dry_run: !cfg.live });
    if (!Array.isArray(items) || !items.length) break;
    for (const { table, row } of items) {
      if (!TABLES[table] || !row?.id) continue;
      try {
        const files = await gatherFiles(table, row, store, { contents: cfg.live });
        const mail = table === 'concerns' ? concernEmail(row, files, cfg) : rfqEmail(row, files, cfg);
        if (!cfg.live) {
          summary.wouldSend++;
          log(JSON.stringify({ event: 'notify.dry_run', table, id: row.id, to: cfg.to[table].map(mask), subject: mail.subject, attached: files.attachments.length, linked: files.links.length, notIncluded: files.missing.length }));
          continue;
        }
        const providerId = await send({ ...mail, to: cfg.to[table], idempotencyKey: `${table}-${row.id}` });
        // the provider's id stays on the row, so a later bounce can be traced after the logs have gone
        await db.patch(table, row.id, { notified_at: now().toISOString(), notify_error: null, notify_provider_id: providerId || null });
        summary.sent++;
        log(JSON.stringify({ event: 'notify.sent', table, id: row.id, providerId, attached: files.attachments.length, linked: files.links.length, notIncluded: files.missing.length }));
      } catch (e) {
        summary.failed++; summary.ok = false;
        const message = oneLine(e?.message ?? 'unknown error', 300);
        log(JSON.stringify({ event: 'notify.failed', table, id: row.id, error: message }));
        try { await db.patch(table, row.id, { notify_error: message }); } catch { /* the row stays unsent and is retried */ }
      }
    }
    if (!cfg.live) break;   // a dry run reads the same rows every time, so one look is enough
  }
  return summary;
}

/** For an outside uptime monitor: healthy only when live, fully set up, and nothing has waited over 15 minutes. */
export async function health({ cfg, db }) {
  const out = { ok: false, mode: cfg.live ? 'live' : 'dry run', pending: null, stale: null };
  if (cfg.problems.some((p) => p.startsWith('SUPABASE'))) return out;
  const h = await db.rpc('enquiry_notification_health');
  out.pending = Number(h?.pending ?? 0); out.stale = Number(h?.stale ?? 0);
  out.ok = cfg.live && cfg.problems.length === 0 && out.stale === 0;
  return out;
}
