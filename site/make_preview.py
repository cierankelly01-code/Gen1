"""Build a shareable preview of the site for client review.

Creates ../preview/ containing only the public files, with:
  - noindex on every page and a robots.txt that blocks all crawlers
    (so a demo with unconfirmed facts never reaches Google or AI search)
  - a slim "preview for review" note at the top of every page
Upload the ../preview folder to any static host (e.g. Netlify Drop, Vercel, GitHub Pages).
Run:  python build.py && python make_preview.py
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT.parent / "preview"
NOTE = ('<div style="background:#FFF4D6;color:#5A4300;font:600 13px/1.4 Barlow,system-ui,sans-serif;'
        'text-align:center;padding:8px 16px">Preview for Genex UK review. Not the live site; some details are still to be confirmed.</div>')

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()
shutil.copytree(ROOT / "assets", OUT / "assets", ignore=shutil.ignore_patterns("src"))
for f in ROOT.glob("*.html"):
    html = f.read_text(encoding="utf8")
    html = html.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex, nofollow">', 1)
    html = html.replace('<a class="skip" href="#main">Skip to content</a>', '<a class="skip" href="#main">Skip to content</a>\n' + NOTE, 1)
    (OUT / f.name).write_text(html, encoding="utf8")
(OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf8")
print(f"preview written to {OUT}")
