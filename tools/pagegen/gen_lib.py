"""Shared building blocks for the Genex page generators (from gen_v4)."""
import json
import sys
from pathlib import Path

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
ARROW = '<svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M3 10h13m-5-5 5 5-5 5" stroke="currentColor" stroke-width="1.6"/></svg>'
BASE = "https://genexuk.co.uk"

PARTS = {
    "fuel": ("p-fuel-filter", "part-fuel-pump-bracket.webp", "Fuel filter bracket", "Pressed, stud-welded and e-coated, holding two fuel pumps.", "Steel · 1.5 mm", "Automotive"),
    "door": ("p-door-card", "part-door-card-bracket.webp", "Door card bracket", "About 350 × 350 mm in aluminium, with clinched nuts.", "Aluminium · 1.5 mm", "Automotive"),
    "exhaust": ("p-exhaust", "part-exhaust-hanger.webp", "Exhaust hanger", "Two pressings and two wire forms, robot-welded into one assembly.", "Stainless · 1.5 mm", "Automotive"),
    "ceiling": ("p-ceiling", "part-ceiling-bracket.webp", "Cable basket ceiling bracket", "High-volume pressing in ceiling and wall-mount versions.", "Pre-galv · 3 mm", "Construction"),
    "floor": ("p-floor", "part-floor-base-plates.webp", "Raised-floor base plates", "For raised floors in data centres and offices, run on a progression press.", "Mild steel · 3 mm", "Data centres"),
    "mortuary": ("p-mortuary", "part-mortuary-table.webp", "Mortuary preparation table", "Built complete, with sink and drain, in polished stainless.", "Stainless · mirror polish", "Medical"),
    "panel": ("p-panel", "part-access-panel.webp", "Scanner-lane access panels", "Laser-cut, folded and welded panels in a range of sizes.", "Mild steel · 1.5 mm", "Airport security"),
    "roller": ("p-roller", "part-rear-roller.webp", "Lawn mower rear roller", "Flat sheet rolled, seam-welded and pressed into a roller.", "Mild steel · 1.5 mm", "Machinery"),
}


def parts_block(keys, heading="Parts we make this way"):
    lis = []
    for k in keys:
        pid, img, name, desc, chip, sector = PARTS[k]
        lis.append(f'<li><a class="part" href="/industries.html#{pid}"><img src="/assets/img/{img}" width="800" height="600" loading="lazy" alt="{name} made by Genex"><div class="part__body"><p class="label">{sector}</p><h3>{name}</h3><p>{desc}</p><span class="chip">{chip}</span></div></a></li>')
    return f'''      <article class="block" id="examples">
        <p class="label">Examples</p>
        <h2>{heading}</h2>
        <ul class="parts parts--inline">{''.join(lis)}</ul>
      </article>
'''


def faq_html(faqs):
    items = ''.join(f'<details class="qa"{" open" if i == 0 else ""}><summary>{q}<span class="pm" aria-hidden="true"></span></summary><div class="qa__a"><p>{a}</p></div></details>' for i, (q, a) in enumerate(faqs))
    return f'''      <article class="block" id="faq">
        <p class="label">Questions</p>
        <h2>Frequently asked questions</h2>
        <div class="faq__list">{items}</div>
      </article>
'''


def strip_tags(s):
    import re
    return re.sub(r"<[^>]+>", "", s)


def page(slug, nav, title, desc, crumbs, kicker, h1, lead, answer, sections, faqs=None, schema_extra=None, side=None, cta_label="Quote my part", cta_href="/rfq.html"):
    crumb_ld = [{"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(crumbs)]
    blocks = [json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": crumb_ld}, ensure_ascii=False)]
    if faqs:
        blocks.append(json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in faqs]}, ensure_ascii=False))
    if schema_extra:
        blocks.append(json.dumps(schema_extra, ensure_ascii=False))
    schema = "\n".join(f'<script type="application/ld+json">\n{b}\n</script>' for b in blocks)
    esc = lambda t: t.replace('&amp;', '&').replace('&', '&amp;')
    crumb_html = ''.join(f'<li><a href="{u}">{esc(n)}</a></li>' for n, u in crumbs[:-1]) + f'<li aria-current="page">{esc(crumbs[-1][0])}</li>'
    toc_items = [(s["id"], s["toc"]) for s in sections] + ([("faq", "Questions")] if faqs else [])
    toc = ''.join(f'<li><a href="#{i}"><span>{n + 1:02d}</span>{t}</a></li>' for n, (i, t) in enumerate(toc_items))
    side = side or ('<div class="side-card" style="margin-top:var(--s-6)"><h2>Send us a drawing</h2>'
                    '<p class="muted" style="font-size:var(--fs-small);margin-bottom:var(--s-4)">STEP, DXF or PDF with your quantities. We reply within one working day.</p>'
                    f'<a class="btn btn--sm" href="/rfq.html">Request a quote</a></div>')
    body = ''.join(s["html"] for s in sections) + (faq_html(faqs) if faqs else '')
    meta = json.dumps({"title": title, "description": desc, "path": f"/{slug}.html", "nav": nav}, ensure_ascii=False)
    html = f'''<!--meta {meta} -->
<!--schema-->
{schema}
<!--/schema-->

<section class="phero">
  <div class="wrap">
    <nav aria-label="Breadcrumb" class="crumbs"><ol>{crumb_html}</ol></nav>
    <div class="phero__grid">
      <div class="phero__t">
        <p class="label label--line">{kicker}</p>
        <h1 class="display">{h1}</h1>
      </div>
      <div class="phero__d">
        <p class="lead">{lead}</p>
        <a class="btn" href="{cta_href}">{cta_label} {ARROW}</a>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap split">
    <aside class="split__side">
      <div class="sticky">
        <p class="label" style="margin-bottom:var(--s-4)">On this page</p>
        <ol class="toc">{toc}</ol>
        {side}
      </div>
    </aside>
    <div class="split__main">
      <div class="answer answer--lead"><p><b>In short:</b> {answer}</p></div>
{body}    </div>
  </div>
</section>

{{{{cta}}}}
'''
    (OUT / f"{slug}.html").write_text(html, encoding="utf-8")
    return slug


def sec(id, toc, label, h2, prose="", extra=""):
    p = f'<div class="prose">{prose}</div>' if prose else ''
    return {"id": id, "toc": toc, "html": f'''      <article class="block" id="{id}">
        <p class="label">{label}</p>
        <h2>{h2}</h2>
        {p}{extra}
      </article>
'''}


def table(caption, rows):
    r = ''.join(f'<tr><th scope="row">{a}</th><td>{b}</td></tr>' for a, b in rows)
    return f'<div class="table-wrap"><table class="spec-table"><caption>{caption}</caption><tbody>{r}</tbody></table></div>'


def fig(img, w, h, alt, cap):
    return f'<figure class="media"><img src="/assets/img/{img}" width="{w}" height="{h}" loading="lazy" alt="{alt}"><figcaption>{cap}</figcaption></figure>'


def cards(items):
    return '<div class="cards">' + ''.join(f'<div class="card"><span class="label">{l}</span><h3>{h}</h3><p>{p}</p></div>' for l, h, p in items) + '</div>'


def vbtn(src, title, label):
    return f'<p><button class="link vlink" type="button" data-video="/assets/video/{src}" data-title="{title}">{label} →</button></p>'


def service(name, desc, slug):
    return {"@context": "https://schema.org", "@type": "Service", "name": name, "serviceType": name, "description": desc,
            "provider": {"@id": f"{BASE}/#org"}, "areaServed": "GB", "url": f"{BASE}/{slug}.html"}


made = []
CAP = ("Capabilities", "/capabilities.html")
HOME = ("Home", "/")
