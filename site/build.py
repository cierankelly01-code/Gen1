"""Tiny static build for the Genex UK site.

Each page in _src/pages/*.html starts with a JSON meta comment:
    <!--meta {"title": "...", "description": "...", "path": "/x.html", "nav": "capabilities"} -->
The page body is dropped into _src/partials/layout.html and written to the site root.
Run:  python build.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "_src"
NAV_KEYS = ["capabilities", "industries", "quality", "about", "contact"]


def strip_svg() -> str:
    """Progressive-die strip layout for the home page story (works with JS off)."""
    bg = "#191D22"
    xs = [100, 260, 420, 580, 740]
    out = []
    a = out.append
    a('<svg class="story__svg" viewBox="0 6 1000 352" role="img" aria-labelledby="strip-t strip-d">')
    a('<title id="strip-t">Progressive die strip layout</title>')
    a('<desc id="strip-d">A coil strip feeds through five press stations: pilot and pierce, notch, form, nut insert and cut-off. '
      'The finished bracket is then e-coated, inspected and packed.</desc>')
    # upper die / ram
    a('<g class="st-ram">')
    a(f'<rect x="20" y="18" width="800" height="46" fill="#242A31" stroke="#545B64"/>')
    a('<text class="st-fine" x="32" y="48" fill="#8C929A" font-family="IBM Plex Mono, monospace" font-size="17" letter-spacing=".06em">UPPER DIE · GX TOOLROOM</text>')
    for x in xs:
        a(f'<rect x="{x-14}" y="64" width="28" height="22" fill="#3B4149" stroke="#545B64"/>')
    a('</g>')
    # station labels + highlight brackets
    for i, x in enumerate(xs, start=1):
        a(f'<g class="st-station" data-station="{i}">')
        a(f'<text x="{x}" y="112" text-anchor="middle" fill="#AEB3BA" font-family="IBM Plex Mono, monospace" font-size="17">OP{i}0</text>')
        a('</g>')
        a(f'<g class="st-hl" data-hl="{i}"><path d="M{x-70} 128v-8h140v8M{x-70} 292v8h140v-8" fill="none" stroke="#FF6A63" stroke-width="2"/></g>')
    # feed arrow + strip
    a('<path d="M4 205h10" stroke="#7FA8E0" stroke-width="1.5"/><path d="M10 200l6 5-6 5" fill="none" stroke="#7FA8E0" stroke-width="1.5"/>')
    a('<rect x="20" y="130" width="800" height="150" fill="#2E353D" stroke="#8C929A" stroke-width="1"/>')
    a('<text class="st-fine" x="24" y="318" fill="#AEB3BA" font-family="IBM Plex Mono, monospace" font-size="17">COIL FEED → · DC01 · 2.0 MM</text>')
    for i, x in enumerate(xs, start=1):
        g = lambda op, body: a(f'<g class="st-feat" data-op="{op}">{body}</g>') if op <= i else None
        # OP10 pilot + pierce
        g(1, f'<circle cx="{x}" cy="142" r="5" fill="{bg}"/><circle cx="{x}" cy="268" r="5" fill="{bg}"/>'
             f'<circle cx="{x-26}" cy="180" r="7" fill="{bg}"/><circle cx="{x+26}" cy="180" r="7" fill="{bg}"/>'
             f'<rect x="{x-13}" y="234" width="26" height="10" rx="5" fill="{bg}"/>')
        # OP20 notch (material removed either side of the part, leaving carrier)
        g(2, f'<rect x="{x-80}" y="152" width="22" height="106" fill="{bg}"/><rect x="{x+58}" y="152" width="22" height="106" fill="{bg}"/>')
        # OP30 form — flanges + bend lines
        g(3, f'<rect x="{x-58}" y="152" width="116" height="106" fill="#9AA4AF" stroke="#D5DAE0" stroke-width="1"/>'
             f'<rect x="{x-58}" y="152" width="116" height="20" fill="#6E7883"/><rect x="{x-58}" y="238" width="116" height="20" fill="#6E7883"/>'
             f'<path d="M{x-58} 172h116M{x-58} 238h116" stroke="#E8ECF0" stroke-dasharray="5 4"/>'
             f'<circle cx="{x-26}" cy="180" r="7" fill="{bg}"/><circle cx="{x+26}" cy="180" r="7" fill="{bg}"/>'
             f'<rect x="{x-13}" y="234" width="26" height="10" rx="5" fill="{bg}"/>')
        # OP40 M6 nut insert
        g(4, f'<polygon points="{x+11},205 {x+5.5},214.5 {x-5.5},214.5 {x-11},205 {x-5.5},195.5 {x+5.5},195.5" fill="none" stroke="#7FA8E0" stroke-width="2"/>'
             f'<circle cx="{x}" cy="205" r="4.5" fill="{bg}" stroke="#7FA8E0"/>')
        # OP50 cut-off
        g(5, f'<rect x="{x-60}" y="146" width="120" height="6" fill="{bg}"/><rect x="{x-60}" y="258" width="120" height="6" fill="{bg}"/>')
    a('<path class="st-ghost" d="M872 150h96l-8 22v66l8 22h-96l8-22v-66z" fill="none" stroke="#545B64" stroke-dasharray="4 4"/>')
    a('<text x="920" y="210" text-anchor="middle" fill="#8C929A" font-family="IBM Plex Mono, monospace" font-size="15">OP60</text>')
    # OP60 — finished, e-coated part leaves the tool
    a('<g class="st-part-final" data-op="6">')
    a('<path d="M828 205h22" stroke="#7FA8E0" stroke-width="1.5"/><path d="M845 200l6 5-6 5" fill="none" stroke="#7FA8E0" stroke-width="1.5"/>')
    a('<path d="M872 150h96l-8 22v66l8 22h-96l8-22v-66z" fill="#0E1012" stroke="#AEB3BA"/>')
    a('<circle cx="894" cy="182" r="7" fill="#2E353D"/><circle cx="946" cy="182" r="7" fill="#2E353D"/>')
    a('<polygon points="931,212 925.5,221.5 914.5,221.5 909,212 914.5,202.5 925.5,202.5" fill="none" stroke="#7FA8E0" stroke-width="2"/>')
    a('<text x="920" y="296" text-anchor="middle" fill="#F3F1EC" font-family="IBM Plex Mono, monospace" font-size="16">OP60</text>')
    a('<text x="920" y="316" text-anchor="middle" fill="#AEB3BA" font-family="IBM Plex Mono, monospace" font-size="14">INSPECT · PACK</text>')
    a('<path d="M908 330l8 8 16-18" fill="none" stroke="#3DBA75" stroke-width="3"/>')
    a('</g>')
    a('</svg>')
    return "\n".join(out)


def build():
    layout = (SRC / "partials" / "layout.html").read_text(encoding="utf-8")
    snippets = {"strip_svg": strip_svg(), "cta": (SRC / "partials" / "cta.html").read_text(encoding="utf-8")}
    pages = sorted((SRC / "pages").glob("*.html"))
    for page in pages:
        raw = page.read_text(encoding="utf-8")
        m = re.match(r"\s*<!--meta\s*(\{.*?\})\s*-->", raw, re.S)
        if not m:
            raise SystemExit(f"{page.name}: missing <!--meta {{...}} --> header")
        meta = json.loads(m.group(1))
        body = raw[m.end():]
        schema = ""
        sm = re.search(r"<!--schema-->(.*?)<!--/schema-->", body, re.S)
        if sm:
            schema = sm.group(1).strip()
            body = body[:sm.start()] + body[sm.end():]
        for k, v in snippets.items():
            body = body.replace("{{" + k + "}}", v)
        html = layout
        repl = {
            "title": meta["title"],
            "description": meta["description"],
            "path": meta["path"],
            "schema": schema,
        }
        for key in NAV_KEYS:
            on = meta.get("nav") == key
            repl["nav_" + key] = (' aria-current="page"' if key == "contact" else ' data-current="true"') if on else ""
        for k, v in repl.items():
            html = html.replace("{{" + k + "}}", v)
        html = html.replace("{{content}}", body.strip())
        # mark this page's own link in the menus as the current page
        own = '<a href="%s"><strong>' % meta["path"]
        html = html.replace(own, own.replace('"><strong>', '" aria-current="page"><strong>'))
        out = ROOT / page.name
        out.write_text(html, encoding="utf-8")
        print(f"built {out.name}")


if __name__ == "__main__":
    build()
