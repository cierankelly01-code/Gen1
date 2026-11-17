# notify-enquiries (Supabase Edge Function)

Emails every new website **quote request** and **concern** to the right Genex mailbox, with the
attached files. Without it the forms only save to the database and nobody is told.

- A new row wakes the function straight away; a five-minute sweep catches anything that was missed.
- A row is marked as sent only after the email provider accepts it. A failure stays waiting and is retried.
- **Dry run by default.** Nothing is emailed unless `NOTIFY_MODE=live`.
- Files up to 20 MB in total are attached. Bigger sets (CAD) are sent as links that work for 7 days.
- No more than 60 emails per form in 24 hours, so junk rows can't flood a mailbox. The rest wait and show in health.
- A form with 60 rows still waiting refuses new ones, so the visitor sees "couldn't send, call us" instead of a
  thank-you for something nobody will read for days. Never-tried rows go ahead of rows that keep failing.
- There is no rate limit or bot check on the forms yet. A determined junk sender can fill a queue and close a
  form until the junk is deleted (SQL below). A bot check at the edge is the real fix.
- Recipients and keys are function secrets. Nothing private is in this repo.

| Secret | What |
|---|---|
| `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` | Provided by Supabase automatically |
| `NOTIFY_SECRET` | Random, 32+ characters. The database sends it as `x-notify-secret` |
| `NOTIFY_MODE` | `live` to send. Anything else, or unset, is a dry run |
| `RESEND_API_KEY` | Resend key with "sending access" only (live only) |
| `NOTIFY_FROM` | e.g. `Genex website <website@notify.genexuk.co.uk>`, on a domain verified in Resend |
| `CONCERN_TO` | Who gets concerns. Comma-separated for more than one. **Use two mailboxes**: a row counts as sent when the provider accepts it, so one renamed or full mailbox would swallow reports unseen |
| `RFQ_TO` | Who gets quote requests |
| `NOTIFY_HELP_CONTACT` | Optional. Named in the email when a file could not be included, e.g. `the website team on 01234 567890` |

## Switching it on

1. **Database:** run `supabase/notifications.sql` in the SQL Editor (after `setup.sql`).
2. **Email provider:** Resend account, add the sending domain, add the DNS records it shows, wait for
   "Verified". Create an API key with sending access only.
3. **Deploy:** `npx supabase functions deploy notify-enquiries --no-verify-jwt --project-ref <ref>`
4. **Secrets, dry run first:**
   `npx supabase secrets set --project-ref <ref> NOTIFY_SECRET=<random 64 hex> CONCERN_TO=<address> RFQ_TO=<address>`
5. **Tell the database where the function is** (SQL Editor, once; same secret as step 4):
   ```sql
   select vault.create_secret('https://<ref>.supabase.co/functions/v1/notify-enquiries', 'notify_enquiries_url');
   select vault.create_secret('<NOTIFY_SECRET>', 'notify_enquiries_secret');
   ```
6. **Watch a dry run:** send one test through each form. Edge Functions > notify-enquiries > Logs should
   show `notify.dry_run` with the right (masked) mailbox within five minutes.
7. **Go live:** `npx supabase secrets set --project-ref <ref> RESEND_API_KEY=re_... NOTIFY_FROM="Genex website <website@notify.genexuk.co.uk>" NOTIFY_MODE=live`.
   The waiting test rows go out on the next sweep. Confirm with Genex that both arrived, with the attachment.
8. **Uptime monitor:** point an outside monitor at `https://<ref>.supabase.co/functions/v1/notify-enquiries`
   (a plain GET). It answers 200 when healthy and 503 when anything has waited over 15 minutes, when it
   is in dry run, or when a setting is missing. The reply only says healthy or not; the counts are in the log.

## How you find out it has stopped

- The health address above goes 503. That is the alarm; without a monitor on it nobody is told.
- Function logs: `notify.sent`, `notify.failed` (with the reason), `notify.misconfigured`.
- In the database: `select id, created_at, notify_attempts, notify_error from concerns where notified_at is null;`
  (and the same for `rfqs`). To clear junk: `delete from concerns where notified_at is null and <what marks the junk>;`
- A bounce after the provider accepted the email is **not** detected. Each sent row keeps the provider's id
  (`notify_provider_id`) so it can be looked up in Resend. Check Resend's bounce list monthly.

## What is and isn't proven

`cd supabase && npm ci && npm test` runs the database rules for real (PGlite) and the function logic against
a fake email provider and file store. **Not proven until the first live test on the real project:** the
storage API calls, Vault, pg_net, pg_cron, and Resend accepting the domain. Step 6 and 7 are that test.

## To pause

`npx supabase secrets set --project-ref <ref> NOTIFY_MODE=dryrun`. Rows keep saving and wait; health goes 503.
