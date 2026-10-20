"""Website checks for the Genex site. Run from the repo root:  python tools/check_site.py

Fails (exit 1) if any of these break:
  1. every internal link, image, video and download on every page points at a real file
  2. every #anchor link lands on an element with that id
  3. every page has a title, a meta description, a canonical link and exactly one <h1>
  4. every JSON-LD block parses
  5. every sitemap URL exists
  6. the preview build (../preview, if present) is noindex and blocks all crawlers
  7. nothing private is tracked by git in this public repo
Standard library only, so it runs anywhere (CI included).
"""
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

REPO = Path(__file__).resolve().parent.parent
SITE = REPO / "site"
PREVIEW = REPO / "preview"
# Files that must never be tracked in this public repo (mirrors .gitignore; this is the second lock)
PRIVATE = [r"^brain/", r"^platform/", r"^outreach/", r"(^|/)genex-[^/]*\.html$", r"-BRIEF\.md$",
           r"(^|/)CLAUDE\.md$", r"(^|/)AGENTS\.md$", r"^WEBSITE-BENCHMARK\.md$", r"^PLATFORM-FOUNDATIONS\.md$",
           r"^SECURITY-POSTURE\.md$", r"\.env($|\.)", r"^preview/"]


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs, self.ids, self.jsonld, self.h1 = [], set(), [], 0
        self.title = self.desc = self.canonical = self.robots = None
        self._in_title = self._in_ld = False
        self._buf = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for key in ("href", "src", "poster", "data-src", "data-video"):
            if a.get(key):
                self.refs.append(a[key])
        if a.get("srcset"):
            self.refs += [s.strip().split(" ")[0] for s in a["srcset"].split(",")]
        if tag == "title":
            self._in_title, self._buf = True, ""
        if tag == "h1":
            self.h1 += 1
        if tag == "meta" and a.get("name") == "description":
            self.desc = a.get("content")
        if tag == "meta" and a.get("name") == "robots":
            self.robots = a.get("content")
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        if tag == "script" and a.get("type") == "application/ld+json":
            self._in_ld, self._buf = True, ""

    def handle_endtag(self, tag):
        if tag == "title" and self._in_title:
            self.title, self._in_title = self._buf.strip(), False
        if tag == "script" and self._in_ld:
            self.jsonld.append(self._buf)
            self._in_ld = False

    def handle_data(self, data):
        if self._in_title or self._in_ld:
            self._buf += data


def parse(path):
    p = Page()
    p.feed(path.read_text(encoding="utf-8"))
    return p


def main():
    errors = []
    pages = {f"/{f.name}": parse(f) for f in sorted(SITE.glob("*.html")) if not f.name.startswith("_")}
    pages["/"] = pages["/index.html"]

    for url, p in pages.items():
        if url == "/":
            continue
        name = url.lstrip("/")
        if not p.title:
            errors.append(f"{name}: missing <title>")
        if not p.desc:
            errors.append(f"{name}: missing meta description")
        if not p.canonical and name != "404.html":
            errors.append(f"{name}: missing canonical link")
        if p.h1 != 1:
            errors.append(f"{name}: has {p.h1} <h1> elements (want exactly 1)")
        for block in p.jsonld:
            try:
                json.loads(block)
            except json.JSONDecodeError as e:
                errors.append(f"{name}: JSON-LD does not parse ({e})")
        for ref in p.refs:
            parts = urlsplit(ref)
            if parts.scheme or ref.startswith(("//", "mailto:", "tel:", "data:")):
                continue
            path = unquote(parts.path) or url
            if not path.startswith("/"):
                path = "/" + path
            target = SITE / path.lstrip("/")
            if path == "/" or target.is_dir():
                target = target / "index.html"
            if not target.exists():
                errors.append(f"{name}: broken link {ref}")
                continue
            if parts.fragment and target.suffix == ".html":
                key = "/" + target.name
                if key in pages and parts.fragment not in pages[key].ids:
                    errors.append(f"{name}: anchor #{parts.fragment} missing on {target.name}")

    sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    for loc in re.findall(r"<loc>https://genexuk\.co\.uk(/[^<]*)</loc>", sitemap):
        f = SITE / (loc.lstrip("/") or "index.html")
        if not f.exists():
            errors.append(f"sitemap.xml: {loc} does not exist")

    if PREVIEW.exists():
        robots = (PREVIEW / "robots.txt").read_text(encoding="utf-8")
        if "Disallow: /" not in robots:
            errors.append("preview/robots.txt does not block crawlers")
        for f in PREVIEW.glob("*.html"):
            if "noindex" not in (parse(f).robots or ""):
                errors.append(f"preview/{f.name}: missing noindex")

    try:
        tracked = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True, check=True).stdout.splitlines()
        for f in tracked:
            if any(re.search(rx, f) for rx in PRIVATE):
                errors.append(f"PRIVATE FILE TRACKED IN PUBLIC REPO: {f}")
    except (OSError, subprocess.CalledProcessError):
        errors.append("could not run git ls-files")

    n_refs = sum(len(p.refs) for u, p in pages.items() if u != "/")
    if errors:
        print("\n".join(errors))
        print(f"\nFAILED: {len(errors)} problem(s) across {len(pages) - 1} pages")
        return 1
    print(f"OK: {len(pages) - 1} pages, {n_refs} links and assets, sitemap, JSON-LD and private-file guard all pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
