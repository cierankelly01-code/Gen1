# Genex UK website: static build served by nginx.
# Build variables (set in Coolify > Environment Variables, tick "Build Variable"):
#   PREVIEW            1 = noindex preview with banner (default), 0 = live site
#   SUPABASE_URL       e.g. https://abcd1234.supabase.co
#   SUPABASE_ANON_KEY  the project's anon / publishable key (safe in the browser; RLS allows insert only)
#   STATS_URL          optional: the Umami address, e.g. https://stats.example.com (must also be in security-headers.conf)
#   STATS_ID           optional: the website id Umami gives this site (not a secret)
#   SOURCE_COMMIT      set by Coolify to the commit being deployed; written to /version.txt so anyone can
#                      check which commit is live. Empty outside Coolify, and the file then says "unknown".
FROM python:3.15-alpine AS build
WORKDIR /app
COPY site/ ./site/
ARG PREVIEW=1
ARG SUPABASE_URL=""
ARG SUPABASE_ANON_KEY=""
# Visit statistics (Umami, no cookies). Leave both empty and the site counts nothing.
ARG STATS_URL=""
ARG STATS_ID=""
# The live site must never be built without a form backend: it would lose every enquiry.
RUN if [ "$PREVIEW" != "1" ] && { [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_ANON_KEY" ]; }; then \
      echo "ERROR: PREVIEW=0 needs SUPABASE_URL and SUPABASE_ANON_KEY set as build variables." >&2; exit 1; fi
# Statistics must never be able to break the site. A stray quote in either value would break config.js and
# with it the forms, and a stats address the browser's security policy doesn't allow would count nothing
# without anyone being told. So both are checked here and a bad value stops the build (the old site stays up).
COPY security-headers.conf /tmp/security-headers.conf
RUN if [ -n "$STATS_URL$STATS_ID" ]; then \
      echo "$STATS_URL" | grep -Eq '^https://[A-Za-z0-9.-]+$' || { echo "ERROR: STATS_URL must look like https://host with no path or trailing slash." >&2; exit 1; }; \
      echo "$STATS_ID" | grep -Eq '^[A-Za-z0-9-]+$' || { echo "ERROR: STATS_ID must be letters, digits and dashes only." >&2; exit 1; }; \
      grep -qF "$STATS_URL/script.js" /tmp/security-headers.conf && grep -qF "$STATS_URL/api/send" /tmp/security-headers.conf \
        || { echo "ERROR: STATS_URL is not allowed in security-headers.conf (script.js and api/send)." >&2; exit 1; }; \
    fi
RUN cd site && python build.py \
 && if [ "$PREVIEW" = "1" ]; then python make_preview.py && mv /app/preview /app/out && DEMO=true; \
    else mkdir -p /app/out && cp -r *.html robots.txt sitemap.xml llms.txt assets .well-known /app/out/ && rm -rf /app/out/assets/img/src && DEMO=false; fi \
 && if [ "$PREVIEW" = "1" ]; then STATS_URL=""; STATS_ID=""; fi \
 && printf "window.GENEX_CFG = { supabaseUrl: '%s', supabaseAnonKey: '%s', demo: %s, stats: { url: '%s', id: '%s' } };\n" "$SUPABASE_URL" "$SUPABASE_ANON_KEY" "$DEMO" "$STATS_URL" "$STATS_ID" > /app/out/assets/js/config.js

FROM nginx:1.29-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY security-headers.conf /etc/nginx/snippets/security-headers.conf
COPY --from=build /app/out /usr/share/nginx/html
# Which commit is this? Declared last, so a new commit never throws away the cached build above.
# Anything that is not a commit id (or nothing at all) is written as "unknown".
ARG SOURCE_COMMIT=""
RUN if echo "$SOURCE_COMMIT" | grep -Eqx '[0-9a-f]{7,40}'; then echo "$SOURCE_COMMIT"; else echo unknown; fi > /usr/share/nginx/html/version.txt
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD wget -qO- http://127.0.0.1/ >/dev/null || exit 1
