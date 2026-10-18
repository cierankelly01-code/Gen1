# Genex UK website: static build served by nginx.
# Build variables (set in Coolify > Environment Variables, tick "Build Variable"):
#   PREVIEW            1 = noindex preview with banner (default), 0 = live site
#   SUPABASE_URL       e.g. https://abcd1234.supabase.co
#   SUPABASE_ANON_KEY  the project's anon / publishable key (safe in the browser; RLS allows insert only)
FROM python:3.12-alpine AS build
WORKDIR /app
COPY site/ ./site/
ARG PREVIEW=1
ARG SUPABASE_URL=""
ARG SUPABASE_ANON_KEY=""
RUN cd site && python build.py \
 && if [ "$PREVIEW" = "1" ]; then python make_preview.py && mv /app/preview /app/out; \
    else mkdir -p /app/out && cp -r *.html robots.txt sitemap.xml llms.txt assets /app/out/ && rm -rf /app/out/assets/img/src; fi \
 && printf "window.GENEX_CFG = { supabaseUrl: '%s', supabaseAnonKey: '%s' };\n" "$SUPABASE_URL" "$SUPABASE_ANON_KEY" > /app/out/assets/js/config.js

FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY security-headers.conf /etc/nginx/snippets/security-headers.conf
COPY --from=build /app/out /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD wget -qO- http://127.0.0.1/ >/dev/null || exit 1
