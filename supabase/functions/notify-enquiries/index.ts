// Supabase Edge Function: email each new website quote request and concern to Genex.
//   POST  with header x-notify-secret: sends whatever is waiting. Called by the database
//         (on every new row, and every five minutes as a sweep). Not for browsers.
//   GET   health for an uptime monitor: 200 when healthy, 503 when something is stuck or not set up.
// Deploy with --no-verify-jwt: the function checks its own secret. Setup: README.md next to this file.
import { database, health, readConfig, resendSender, runNotifications, secretMatches, storage } from './core.mjs';

Deno.serve(async (req: Request) => {
  const cfg = readConfig((k: string) => Deno.env.get(k));
  try {
    if (req.method === 'GET') {
      const h = await health({ cfg, db: database(cfg) });
      if (!h.ok) console.log(JSON.stringify({ event: 'notify.unhealthy', ...h, missing: cfg.problems }));
      // Anyone can call this, so it says only healthy or not. The counts are in the function log.
      return Response.json({ ok: h.ok }, { status: h.ok ? 200 : 503, headers: { 'Cache-Control': 'no-store' } });
    }
    if (req.method !== 'POST') return new Response('Method not allowed', { status: 405 });
    if (!secretMatches(req.headers.get('x-notify-secret') ?? '', cfg.secret)) return new Response('Unauthorized', { status: 401 });
    const summary = await runNotifications({
      cfg,
      db: database(cfg),
      store: storage(cfg),
      send: resendSender({ apiKey: cfg.resendKey, from: cfg.from }),
    });
    // A failed send or missing setting is an HTTP error on purpose, so run history and monitors see it.
    return Response.json(summary, { status: summary.ok ? 200 : 500 });
  } catch (e) {
    console.error(JSON.stringify({ event: 'notify.error', error: (e as Error).message }));
    return Response.json({ ok: false, error: 'notification run failed, see function logs' }, { status: req.method === 'GET' ? 503 : 500 });
  }
});
