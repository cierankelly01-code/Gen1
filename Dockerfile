# Genex UK website: static build served by nginx.
# PREVIEW=1 (default) adds noindex + a "preview for review" note and blocks crawlers.
# Set the build arg PREVIEW=0 in Coolify when Genex approve the site for go-live.
FROM python:3.12-alpine AS build
WORKDIR /app
COPY site/ ./site/
ARG PREVIEW=1
RUN cd site && python build.py \
 && if [ "$PREVIEW" = "1" ]; then python make_preview.py && mv /app/preview /app/out; \
    else mkdir -p /app/out && cp -r *.html robots.txt sitemap.xml llms.txt assets /app/out/ && rm -rf /app/out/assets/img/src; fi

FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/out /usr/share/nginx/html
EXPOSE 80
