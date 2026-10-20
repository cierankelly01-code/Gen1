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

# Preview links get forwarded to people nobody is there to guide. Enquiries sent from a preview aren't
# being read yet, so the quote form says so instead of promising an engineer's reply.
RFQ_SWAPS = [
    ('<span>Reply within one working day</span><span>Files seen', '<span>Files seen'),
    ('<span>Reply within one working day</span><span>Or call',
     '<span>Preview: this form is for trying out and isn\'t monitored yet</span>'),
    ('<h2>Thanks. Your drawing is with our engineers.</h2>',
     '<h2>Thanks. That\'s how sending a drawing will work.</h2>'),
    ('<p class="muted">You\'ll get a reply within one working day. If it\'s urgent, call',
     '<p class="muted">This is a preview, so nobody is reading enquiries from it yet. For a real quote, email '
     '<a class="link" href="mailto:sales@genexuk.co.uk">sales@genexuk.co.uk</a> or call'),
]

CONCERN_SWAPS = [
    ('<span>Read by our Managing Director</span><span>Anonymous if you prefer</span>',
     '<span>Preview: this form is for trying out and is not monitored yet</span>'),
    ('<p class="muted">Your report has gone to our Managing Director.',
     '<p class="muted">This is a preview, so nobody is reading reports from it yet. On the live site, this goes to our Managing Director.'),
]

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()
shutil.copytree(ROOT / "assets", OUT / "assets", ignore=shutil.ignore_patterns("src"))
for f in ROOT.glob("*.html"):
    if f.name.startswith("_"):
        continue
    html = f.read_text(encoding="utf8")
    html = html.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex, nofollow">', 1)
    html = html.replace('<a class="skip" href="#main">Skip to content</a>', '<a class="skip" href="#main">Skip to content</a>\n' + NOTE, 1)
    if f.name == "rfq.html":
        for old, new in RFQ_SWAPS:
            assert old in html, f"rfq.html changed; update RFQ_SWAPS in make_preview.py: {old[:40]}"
            html = html.replace(old, new, 1)
    if f.name == "concern.html":
        for old, new in CONCERN_SWAPS:
            assert old in html, f"concern.html changed; update CONCERN_SWAPS in make_preview.py: {old[:40]}"
            html = html.replace(old, new, 1)
    (OUT / f.name).write_text(html, encoding="utf8")
(OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf8")
print(f"preview written to {OUT}")
