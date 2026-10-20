"""Genex v5 pages: deeper capability and sector pages, plus how-we-work, materials, case studies,
glossary and resources. Facts come only from what Genex has published (site, LinkedIn) or is on
the README confirm list. Rules of thumb are general industry guidance, flagged for engineer sign-off."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from gen_lib import *  # noqa: F401,F403  (page, sec, table, fig, cards, vbtn, service, parts_block, PARTS, HOME, CAP, BASE, ARROW, strip_tags)

made = []


def ul(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def ol_steps(items):
    return '<ol class="steps">' + "".join(f"<li><div><h3>{h}</h3><p>{p}</p></div></li>" for h, p in items) + "</ol>"


def related(links, heading="Related reading"):
    return sec("related", "Related", "Read next", heading, "",
               '<ul class="linklist">' + "".join(f'<li><a href="{u}">{n} →</a></li>' for n, u in links) + "</ul>")


def send_block(extra=""):
    return sec("quote", "What to send", "Get a price", "What to send for a quote",
               ul(["A 3D model (STEP) and a dimensioned drawing (PDF or DXF)",
                   "Material and thickness, and any equivalent grades you'd accept",
                   "Quantity per order and per year",
                   "Finish or coating, and any cosmetic faces",
                   "Critical tolerances, and the approval you need (first-article report or PPAP level)",
                   "When you need the first parts"] + ([extra] if extra else [])) +
               '<p>We reply within one working day. <a class="link" href="/rfq.html">Send your drawing</a>.</p>')


QUALITY = sec("quality", "Quality checks", "Quality", "How every part is checked",
              ul(["<strong>First-off inspection</strong> against the drawing before a batch runs",
                  "<strong>In-process checks</strong> against the control plan while it runs",
                  "<strong>Final inspection</strong> before packing, with material certificates held against the batch",
                  "<strong>Traceability</strong> from enquiry to delivery, with customer-specific reports if you need them",
                  "<strong>PPAP</strong> Levels 1 to 5 when your customer requires it"]) +
              '<p>Certified to ISO 9001 and ISO 14001, and re-audited by BSI in 2026 with zero non-conformances. <a class="link" href="/quality.html">More on quality</a>.</p>')

DIE = '''<figure class="media die3d" data-die>
          <div class="press__stage"><img src="/assets/img/f-progression.webp" width="1280" height="580" loading="lazy" alt="A progression tool running on a Genex press"></div>
          <figcaption>Live model: the strip indexes one pitch per stroke; pierce, notch, form, nut insert, cut-off. <button type="button" class="link vlink" data-die-pause aria-pressed="false" hidden>Pause</button></figcaption>
        </figure>'''

# ================= capability pages =================
made.append(page(
    "metal-pressings", "capabilities",
    "Metal Pressings up to 200 Tonnes, Walsall | Genex UK",
    "Pressed metal parts on mechanical presses up to 200 tonnes: progression, single-action and multi-stage presswork in mild steel, stainless, aluminium and coated steels up to 5 mm. Walsall, West Midlands.",
    [HOME, CAP, ("Metal pressings", "/metal-pressings.html")],
    "Metal pressings", "Metal pressings, from a few hundred to millions.",
    "Progression, single-action and multi-stage presswork on mechanical presses up to 200 tonnes, with inserting, welding, finishing and assembly on the same site.",
    "Genex makes pressed metal parts on mechanical presses up to 200 tonnes, in mild steel, stainless steel, aluminium and coated steels up to 5 mm thick, from a few hundred to millions of parts a year. Coil-fed progression tools handle long runs; single-action and multi-stage tools suit simpler or lower-volume parts. Production tools are maintained in Genex's own toolroom in Walsall.",
    [
        sec("capacity", "Capacity", "01 · Capacity", "What our press shop runs",
            "<p>Repeatable pressed components at medium to high volume, for customers in automotive, construction, defence, data centres and more. Production tools are maintained in our own toolroom, so a worn punch or a breakdown is dealt with on site, fast, and your parts keep coming.</p>",
            fig("chin-fong-200t.webp", 1000, 1500, "A Chin Fong 200 tonne mechanical press at Genex", "One of our 200 tonne Chin Fong mechanical presses.") + table("Presswork", [
                ("Press capacity", "Mechanical presses up to 200 tonnes"), ("Tool types run", "Progression (coil-fed), single action, multi-stage"),
                ("Material thickness", "Up to 5 mm"), ("Materials", "Mild steel, stainless steel, aluminium, coated steels (e.g. pre-galvanised)"),
                ("Volumes", "A few hundred to millions of parts a year"), ("In-press operations", "Pierce, notch, form, nut and stud insertion"),
                ("After pressing", "Projection and spot welding, robotic MIG, inserting, coating, assembly")])),
        sec("how", "How a pressing is made", "02 · Process", "How a progression tool makes your part",
            "<p>Steel coil feeds through the tool one pitch per press stroke. Each station does one job: pilot holes locate the strip, then the tool pierces, notches, forms and inserts, and the last station cuts the finished part free. A part drops out on every stroke, which is why pressing gives the lowest price per part at volume.</p>",
            DIE + "<div class=\"prose\"><p>Simpler parts, or lower volumes, run in <strong>single-action</strong> tools (one operation per stroke) or <strong>multi-stage</strong> tools, with the operator moving the part between stages. That keeps tooling cost down when a progression tool wouldn't pay back.</p></div>"),
        sec("types", "Tool types compared", "03 · Choosing", "Progression, single-action or multi-stage?", "",
            '<div class="table-wrap"><table class="spec-table"><thead><tr><th scope="col">Tool type</th><th scope="col">How it works</th><th scope="col">Best for</th></tr></thead><tbody>'
            '<tr><th scope="row">Progression</th><td>Coil-fed strip, several stations, a finished part every stroke</td><td>High volumes of settled designs</td></tr>'
            '<tr><th scope="row">Single action</th><td>One operation per stroke</td><td>Simple parts, blanks, lower volumes</td></tr>'
            '<tr><th scope="row">Multi-stage</th><td>Several separate operations, part moved between them</td><td>Medium volumes, larger or deeper parts</td></tr>'
            '</tbody></table></div>'),
        sec("when", "When pressing makes sense", "04 · Route", "When pressing makes sense",
            "<p>Pressing pays off once volumes reach several thousand parts a year and the design is settled, because the production tool is a one-off cost spread across every part. Below that, or while the design is still changing, laser cutting and folding is usually cheaper. Near the break point we price both, so you can compare. See <a class=\"link\" href=\"/pressing-vs-laser-cut-and-fold.html\">pressing vs laser cut and fold</a>.</p>"),
        sec("design", "Design tips", "05 · Design", "Design tips for pressed parts",
            ul(["Keep holes at least one material thickness across, and at least 1.5× thickness from an edge",
                "Keep holes away from bends (at least 2× thickness plus the bend radius), or they'll distort",
                "Use generous inside bend radii, especially in stainless, aluminium and high-strength steel",
                "Mark the burr side on the drawing if it matters for fit or handling",
                "Specify tight tolerances only where the function needs them: they drive tool cost",
                "Tell us if nuts or studs are needed: they can often go in during pressing"]) +
            '<p class="muted" style="font-size:var(--fs-small)">Starting guidelines, not limits. Tell us what a feature has to do and we\'ll tell you what\'s achievable. More in our <a class="link" href="/design-guide.html">design guide</a>.</p>'),
        sec("tooling", "Tooling", "06 · Tooling", "Production tooling",
            "<p>We arrange the production tool for your part and quote it separately from the piece price, so you can see exactly what you're paying for. Once it's running, we maintain it in our own toolroom, with preventative maintenance that extends tool life and keeps quality consistent from the first part to the millionth.</p>"),
        QUALITY,
        {"id": "examples", "toc": "Examples", "html": parts_block(["fuel", "door", "ceiling", "floor"], "Pressings we make")},
        send_block(),
    ],
    [("How thick can you press?", "Up to 5 mm, on mechanical presses up to 200 tonnes, depending on the material and the size of the part."),
     ("What volumes do you press?", "From a few hundred parts to millions a year. Coil-fed progression tools are used for the long runs."),
     ("Can nuts and studs go in during pressing?", "Yes. Nuts and studs can be inserted in the press tool, or as a separate operation in our PEM and projection welding cells."),
     ("Can I get prototypes before committing to tooling?", "Yes. Prototypes are usually laser cut and folded with no tooling cost, so you can prove the design before the production tool is made."),
     ("Which materials can you press?", "Mild steel, stainless steel, aluminium and coated steels such as pre-galvanised. Tell us the grade and we'll confirm."),
     ("Who maintains the press tools?", "We do, in our own toolroom in Walsall, with preventative maintenance and fast response if a tool needs attention."),
     ("Can you take over parts from another supplier?", "Yes. Send the drawing, volumes and details of the existing tooling, and we'll assess the best way to bring the part to Genex.")],
    service("Metal pressing", "Progression, single-action and multi-stage metal pressing up to 200 tonnes and 5 mm thick.", "metal-pressings")))

made.append(page(
    "laser-cutting-and-folding", "capabilities",
    "Laser Cutting & CNC Folding up to 6 mm × 3 m, Walsall | Genex UK",
    "Laser cutting up to 25 mm and CNC press-brake folding up to 6 mm thick at 3 metres on an Amada HRB1003 with offline programming and hemming. Mild steel, stainless, aluminium, copper and brass.",
    [HOME, CAP, ("Laser cutting & folding", "/laser-cutting-and-folding.html")],
    "Laser cutting &amp; folding", "Cut to 25 mm. Folded to 6 mm at 3 metres.",
    "Laser cutting and CNC folding for prototypes, low to medium volumes and parts too large or thick for a press, with hemmed safety edges in a single hit.",
    "Genex laser cuts sheet and plate up to 25 mm and folds up to 6 mm thick at 3 metres long on an Amada HRB1003 press brake, programmed offline from your 3D model, with automatic crowning, digital angle inspection and hemming, in mild steel, stainless steel, aluminium, copper and brass.",
    [
        sec("capacity", "Capacity", "01 · Capacity", "Cutting and folding envelope", "",
            table("Cutting &amp; folding", [("Laser cutting", "Up to 25 mm, depending on material"), ("Folding", "Up to 6 mm thick at 3 m long"),
                                            ("Press brake", "Amada HRB1003, installed April 2026"),
                                            ("Programming", "Offline, from your 3D model"), ("Accuracy", "Automatic crowning, digital angle inspection"),
                                            ("Hemming", "Closed safety edges in a single hit"), ("Materials", "Mild steel, stainless steel, aluminium, copper, brass"),
                                            ("Volumes", "One-off prototypes to repeat batches")])),
        sec("process", "From model to part", "02 · Process", "From your model to a finished part",
            "", ol_steps([("Your model", "We work from your STEP file or drawing and check it for manufacturability."),
                          ("Programmed offline", "The bend sequence is worked out on screen before any metal is cut, so problems are solved before set-up."),
                          ("Laser cut", "The flat blank is cut to profile, with holes and features."),
                          ("Folded", "The Amada folds each bend, with crowning keeping the angle true along the length."),
                          ("Checked", "Angles are inspected digitally and the part is checked against the drawing.")])),
        sec("amada", "Our Amada press brake", "03 · Investment", "The Amada HRB1003",
            "<p>Installed in April 2026, after our team trained on the offline programming with Amada UK. Programming offline means set-up time drops and the first part is right. Automatic crowning keeps the angle true along the full 3 metres, and digital inspection confirms it.</p>",
            fig("amada-delivery.webp", 800, 602, "The new Amada HRB1003 press brake being delivered to Genex", "Our Amada HRB1003 arriving in Walsall, April 2026.") + vbtn("amada-press-brake.mp4", "Our Amada HRB1003 press brake, from offline program to finished bend", "Watch it run (1 min 11)")),
        sec("hemming", "Hemmed edges", "04 · Safe edges", "Hemmed edges in one hit",
            "<p>A hemmed edge folds the sheet back on itself: no sharp edge, a stiffer panel, and no deburring operation. Read more in <a class=\"link\" href=\"/hemmed-edges.html\">hemmed edges explained</a>.</p>",
            vbtn("hemming-tool.mp4", "Hemming a safe, closed edge in a single hit", "Watch the hemming tool (33 sec)")),
        sec("design", "Design tips", "05 · Design", "Design tips for folded parts",
            ul(["Keep flanges at least 4× the material thickness long, so the press brake can grip them",
                "Add bend relief where a bend meets an edge, to stop tearing",
                "Keep holes and slots clear of bends (at least 2× thickness plus the bend radius)",
                "Use the same inside bend radius throughout where you can: fewer tool changes, lower cost",
                "Allow extra flat length for any hemmed edge",
                "Send a STEP file: we program the folding straight from it"]) +
            '<p class="muted" style="font-size:var(--fs-small)">Starting guidelines, not limits. See the <a class="link" href="/design-guide.html">design guide</a>.</p>'),
        QUALITY,
        {"id": "examples", "toc": "Examples", "html": parts_block(["panel", "mortuary"], "Cut and folded work")},
        send_block(),
    ],
    [("What's the thickest you can laser cut?", "Up to 25 mm, depending on the material."),
     ("How long and thick can you fold?", "Up to 6 mm thick at 3 metres long on our Amada HRB1003."),
     ("Do I need tooling for laser cut and folded parts?", "No. Laser cutting and folding works from your drawing, which makes it the usual route for prototypes and lower volumes."),
     ("Can you fold copper and brass?", "Yes, as well as mild steel, stainless steel and aluminium."),
     ("What file should I send?", "A 3D model (STEP) is best, because we program the press brake offline from it. A dimensioned PDF or DXF works too."),
     ("Can parts longer than 3 metres be made?", "Folding is limited to 3 metres, but longer parts can often be fabricated from sections. Send the drawing and we'll advise.")],
    service("Laser cutting and CNC folding", "Laser cutting up to 25 mm and press-brake folding up to 6 mm at 3 m, with hemming.", "laser-cutting-and-folding")))

made.append(page(
    "welding-and-fabrication", "capabilities",
    "Robotic & Manual Welding, Fabrication, Walsall | Genex UK",
    "Robotic MIG, manual MIG and TIG, spot and projection welding for fabrications and welded assemblies in mild steel, stainless and aluminium, from one-offs to jigged volume work. Walsall, UK.",
    [HOME, CAP, ("Welding & fabrication", "/welding-and-fabrication.html")],
    "Welding &amp; fabrication", "The right weld for the part.",
    "Robotic MIG for repeatable volume, skilled manual MIG and TIG for complex or cosmetic welds, and spot and projection welding for sheet assemblies and weld nuts.",
    "Genex welds fabrications and assemblies with robotic MIG, manual MIG and TIG, spot and projection welding, in mild steel, stainless steel and aluminium, from one-off parts to jigged high-volume work, alongside presswork, folding, finishing and assembly on the same site in Walsall.",
    [
        sec("processes", "Weld processes", "01 · Processes", "Four weld processes under one roof",
            "<p>Having the right process available lets engineers design for performance, quality and cost, not for the limits of one supplier's equipment.</p>",
            fig("f-mig.webp", 1280, 580, "Manual MIG welding a folded steel panel at Genex", "Manual MIG welding a fabricated panel.") +
            cards([("Robotic", "Robotic MIG", "Consistent, repeatable welds across high-volume assemblies."),
                   ("Manual", "MIG &amp; TIG", "Complex, specialist and cosmetic welds, including stainless."),
                   ("Resistance", "Spot welding", "Sheet-to-sheet joints for brackets and housings."),
                   ("Resistance", "Projection welding", "Weld nuts and studs, jigged and checked.")])),
        sec("choose", "Choosing a process", "02 · Choosing", "Which weld process suits your part?", "",
            '<div class="table-wrap"><table class="spec-table"><thead><tr><th scope="col">Process</th><th scope="col">Best for</th><th scope="col">Typical volume</th></tr></thead><tbody>'
            '<tr><th scope="row">Robotic MIG</th><td>Repeatable seam welds on steel assemblies</td><td>Medium to high, jigged</td></tr>'
            '<tr><th scope="row">Manual MIG</th><td>Fabrications, frames, guards, larger parts</td><td>One-off to medium</td></tr>'
            '<tr><th scope="row">TIG</th><td>Stainless, aluminium, cosmetic and food-safe welds</td><td>One-off to medium</td></tr>'
            '<tr><th scope="row">Spot</th><td>Joining overlapping sheets quickly, no filler</td><td>Medium to high</td></tr>'
            '<tr><th scope="row">Projection</th><td>Weld nuts and studs onto pressings</td><td>Medium to high, jigged</td></tr>'
            '</tbody></table></div>'),
        sec("quality-weld", "Weld quality", "03 · Quality", "Checked, not assumed",
            "<p>Weld quality is checked against your specification. On our robot-welded exhaust hangers, for example, penetration is measured by macro section and wire-form positions are held to a tight tolerance after welding. Weld nuts and studs are checked to your torque or push-out requirement.</p>",
            fig("f-spotweld.webp", 1280, 580, "Projection welding a nut onto a pressed bracket at Genex", "Projection welding a nut to a pressed bracket.")),
        sec("design", "Design tips", "04 · Design", "Design tips for welded assemblies",
            ul(["Leave room for the torch or electrode to reach every weld",
                "Show weld type and size with standard weld symbols on the drawing",
                "Tell us which faces are cosmetic, so welds and spatter stay off them",
                "For volume work, design parts to locate in a jig: it's what makes robotic welding repeatable",
                "Long or heavy welds on thin sheet can distort it: talk to us early about sequence and fixturing"])),
        QUALITY,
        {"id": "examples", "toc": "Examples", "html": parts_block(["exhaust", "roller", "panel"], "Welded work")},
        send_block("Weld specifications or approvals your customer requires"),
    ],
    [("Do you have robotic welding?", "Yes. Robotic MIG is used for repeatable, high-volume welded assemblies."),
     ("Can you TIG weld stainless steel?", "Yes. Manual TIG is used for stainless and cosmetic work, such as our polished stainless mortuary tables."),
     ("Can you weld nuts and studs to pressings?", "Yes, by projection welding in jigged cells, checked to your torque or push-out requirement."),
     ("Do you weld aluminium?", "Yes, with manual MIG and TIG."),
     ("Can you supply welded assemblies finished and painted?", "Yes. Coatings are managed through our approved finishing partners, so the assembly arrives finished.")],
    service("Welding and fabrication", "Robotic MIG, manual MIG and TIG, spot and projection welding.", "welding-and-fabrication")))

made.append(page(
    "cnc-machining", "capabilities",
    "5-Axis CNC Machining, Turning & Grinding, Walsall | Genex UK",
    "CNC machining on a Hurco 5-axis machining centre, plus turning and grinding, for machined components and post-press machining. Walsall, West Midlands.",
    [HOME, CAP, ("CNC machining", "/cnc-machining.html")],
    "CNC machining", "Complex parts, fewer set-ups.",
    "Machined and turned components, and post-press machining where a feature needs tighter tolerance than a press can hold.",
    "Genex machines components on a Hurco 5-axis machining centre installed in 2026, alongside turning and grinding, and uses machining to finish features on pressed and fabricated parts that need tighter tolerances than forming can hold.",
    [
        sec("five-axis", "5-axis machining", "01 · Investment", "A Hurco 5-axis machining centre",
            "<p>Installed in June 2026. Five axes mean complex geometry is machined in one set-up, with greater precision and shorter lead times, because the part isn't re-clamped between operations.</p>",
            fig("hurco-5axis.webp", 560, 470, "The Hurco VMi 5-axis CNC machining centre at Genex", "Our Hurco 5-axis machining centre.")),
        sec("services", "What we machine", "02 · Services", "What we machine",
            "", cards([("Milling", "5-axis CNC", "Complex parts in fewer set-ups."),
                       ("Turning", "Turned parts", "Bushes, spacers and turned features."),
                       ("Finishing", "Grinding", "Flatness and surface finish where it matters."),
                       ("Secondary", "Post-press machining", "Tight-tolerance features on pressed and fabricated parts.")])),
        sec("when", "When to machine", "03 · Route", "When machining is the right route",
            ul(["Features that need tighter tolerances than pressing or folding can hold",
                "Thick sections and solid parts that can't be formed from sheet",
                "Complex 3D shapes, pockets and threads",
                "Low volumes of parts that would otherwise need a dedicated tool"])),
        sec("design", "Design tips", "04 · Design", "Design tips for machined parts",
            ul(["Use standard thread sizes and hole diameters where you can",
                "Avoid deep, narrow pockets and sharp internal corners: cutters are round",
                "Only tolerance the features that need it; everything else to a general tolerance",
                "Tell us how the part locates in its assembly, so datums match its function"])),
        QUALITY,
        send_block(),
    ],
    [("What machining do you offer?", "5-axis CNC milling on a Hurco machining centre, plus turning and grinding."),
     ("Can you machine features on pressed parts?", "Yes. Holes, threads and faces that need tighter tolerances than a press can hold are finished by machining."),
     ("Can you supply machined parts on their own?", "Yes, as well as machined features within a larger assembly."),
     ("Why 5-axis?", "It machines complex geometry in a single set-up, which improves accuracy and shortens lead times.")],
    service("CNC machining", "5-axis CNC milling, turning and grinding.", "cnc-machining")))

made.append(page(
    "assembly-and-finishing", "capabilities",
    "Complete Assemblies, Inserting & Finishing, Walsall | Genex UK",
    "PEM, stud and nut inserting, bought-in components, tube manipulation, managed coatings and complete assemblies, inspected, packed and delivered on our own vehicles. One supplier, one part number.",
    [HOME, CAP, ("Assembly & finishing", "/assembly-and-finishing.html")],
    "Assembly &amp; finishing", "A finished assembly is worth more than a box of parts.",
    "Inserts, bought-in parts, tube work, coatings and assembly brought together by one supplier, then inspected, packed and delivered on our own vehicles.",
    "Genex turns pressed, folded, welded and machined parts into finished products: PEM, stud and nut inserting, tube manipulation, coatings managed through approved partners, assembly and customer-specified testing, then inspection, packing and delivery on its own 3.5 t and 7.5 t vehicles, under one part number.",
    [
        sec("assembly", "Complete assembly", "01 · Build", "One part number instead of many",
            "<p>When presswork, welding, fabrication, finishing and assembly are coordinated through one manufacturing partner, you buy, inspect and receive one thing. That means less supplier administration, less assembly work on your line and clearer accountability.</p>",
            fig("medical-sink.webp", 817, 937, "A stainless steel mortuary preparation table with built-in sink, supplied by Genex as a complete assembly", "A mortuary preparation table, supplied complete with sink, taps and drain.") +
            '<p><a class="link" href="/case-mortuary-table.html">Read the case study →</a></p>'),
        sec("bring", "What we bring together", "02 · Scope", "What we bring together",
            ul(["Our own pressed, laser-cut, folded, welded and machined parts",
                "Fasteners: PEM nuts, studs and standoffs, clinch nuts and weld nuts",
                "Bought-in components: fittings, plastics, rubber mounts, hardware",
                "Coatings and finishes through approved partners",
                "Customer-specified tests and checks",
                "Packing, labelling and documentation to your specification"])),
        sec("inserting", "Inserting", "03 · Inserting", "Inserting fasteners",
            "<p>PEM nuts, studs and standoffs, clinch nuts and weld nuts fitted by us, so fasteners arrive in the part rather than loose in a bag, and your line doesn't need to fit them.</p>"),
        sec("tube", "Tube manipulation", "04 · Tube", "Tube manipulation",
            "<p>Bent tube frames and wire-form assemblies in stainless and mild steel, welded to pressings and brackets where the design needs it.</p>",
            fig("f-tube.webp", 1280, 580, "Racks of bent stainless tube frames at Genex", "Bent stainless tube frames, racked for welding.")),
        sec("finishing", "Finishing", "05 · Protection", "Finishing, managed by us",
            "<p>E-coat, zinc and zinc-nickel plating, powder coating, passivation and more, through our approved, audited finishing partners. We manage the logistics, the specification and the inspection, so your parts arrive finished on one order. Not sure which finish? See <a class=\"link\" href=\"/metal-finishes-explained.html\">metal finishes explained</a>.</p>"),
        sec("delivery", "Delivery", "06 · Delivered", "Packed, traceable and delivered",
            "", cards([("Transport", "Our own vehicles", "A 3.5 tonne and a 7.5 tonne vehicle, so large orders arrive in one trip."),
                       ("Packing", "Racking &amp; crates", "Custom racks and crates protect parts from our door to your dock."),
                       ("Paperwork", "Traceable to the order", "Labels, reports and container tickets to suit your goods-in.")])),
        QUALITY,
        send_block("Bills of materials for any bought-in parts"),
    ],
    [("Can you supply a finished assembly?", "Yes. We bring our own parts together with inserts, bought-in components and finishing, then assemble, inspect and pack the finished product under one part number."),
     ("Do you do the coating yourselves?", "Coatings are applied by our approved, audited finishing partners and managed by us, so you deal with one supplier."),
     ("Do you deliver?", "Yes, on our own 3.5 tonne and 7.5 tonne vehicles, with racking and crates to protect your parts."),
     ("Can you source bought-in parts?", "Yes. Send the bill of materials and we'll source, check and fit them as part of the assembly.")],
    service("Assembly, inserting and finishing", "Complete assemblies with inserting, tube manipulation, managed coatings and delivery.", "assembly-and-finishing")))

# ================= sector pages =================
SEC = ("Sectors", "/industries.html")


def sector(slug, name, title, desc, h1, lead, answer, makes, needs, run, caps, parts, faqs, guides, img=None, img_alt="", img_cap="", core=True):
    caps_html = '<ul class="linklist">' + ''.join(f'<li><a href="/{s}.html">{n} →</a></li>' for s, n in caps) + '</ul>'
    lname = name.lower().replace('&', '&amp;')
    sections = [
        sec("make", "What we make", "01 · Products", f"What we make for {lname}", ul(makes), fig(*img, img_alt, img_cap) if img else ""),
        sec("needs", "What you need from a supplier", "02 · Requirements", "What you need from a supplier, and how we meet it", "", cards(needs)),
        sec("run", "How a project runs", "03 · Process", f"How a {lname} project runs with Genex", "", ol_steps(run)),
        sec("capabilities", "Capabilities used", "04 · Capabilities", "Capabilities we use", "", caps_html),
    ]
    if parts:
        sections.append({"id": "examples", "toc": "Examples", "html": parts_block(parts, "Examples")})
    sections.append(related(guides))
    return page(slug, "industries", title, desc, [HOME, SEC, (name, f"/{slug}.html")],
                ("Core sector · " if core else "Sector · ") + name.replace('&', '&amp;'), h1, lead, answer, sections, faqs, cta_label="Discuss your project")


RUN_STD = [("Enquiry and review", "Send the drawing, volumes and specification; we review manufacturability and flag cost risks."),
           ("Quote", "Route, piece price, any tooling and lead time, in writing."),
           ("First parts", "First-article inspection report, or PPAP to the level required."),
           ("Production", "Parts made to your schedule, with in-process and final checks."),
           ("Delivery", "Packed to your specification and delivered on our own vehicles.")]

made.append(sector("automotive", "Automotive", "Automotive Pressings & Welded Assemblies | Genex UK",
    "Pressings and welded assemblies for automotive OEMs and Tier 1s, to PPAP, in aluminium, stainless and coated steels. Walsall, West Midlands. Working towards IATF 16949.",
    "Automotive pressings and assemblies, to PPAP.",
    "We've supplied pressings and welded assemblies into automotive for decades, including parts for BMW and Land Rover programmes.",
    "Genex supplies automotive OEMs and Tier 1s with pressed brackets, reinforcements and welded sub-assemblies in aluminium, stainless and coated steels, with PPAP to the level the customer requires, robotic welding for repeatability, a 0 PPM defect record, and IATF 16949 in progress.",
    ["Brackets and reinforcements", "Robot-welded sub-assemblies such as exhaust hangers", "Large aluminium pressings such as door card brackets", "Fuel-system and under-body brackets with weld studs", "E-coated and zinc-nickel plated parts to OEM coating specifications"],
    [("Approval", "PPAP, Levels 1 to 5", "First-article inspection as standard; full PPAP to the level your customer asks for."),
     ("Quality", "0 PPM", "Our defect record, under ISO 9001, working towards IATF 16949."),
     ("Repeatability", "Robotic welding", "Consistent welds across high-volume assemblies."),
     ("Supply", "98%+ on time, in full", "Traceable from enquiry to delivery, delivered on our own vehicles.")],
    [("Feasibility", "Drawing, volumes and OEM specifications reviewed; material and process risks raised at quote stage."),
     ("Quote", "Piece price, tooling and timing, quoted separately so you can compare."),
     ("Launch", "Tooling arranged, first-off samples with a dimensional report."),
     ("PPAP", "Submission to the level your customer requires, with control plan and capability evidence."),
     ("Serial supply", "Parts to your call-offs, packed to line-side specification, with full traceability.")],
    [("metal-pressings", "Metal pressings"), ("welding-and-fabrication", "Welding & fabrication"), ("assembly-and-finishing", "Assembly & finishing")],
    ["fuel", "door", "exhaust"],
    [("Do you supply automotive Tier 1s?", "Yes. Automotive has been a core sector for decades, including parts for BMW and Land Rover programmes."),
     ("Are you IATF 16949 certified?", "We're working towards IATF 16949. Today our automotive work runs under ISO 9001 with the AIAG core tools: APQP, PPAP, FMEA, MSA and SPC."),
     ("Can you submit PPAP?", "Yes, Levels 1 to 5, as your customer requires."),
     ("Which coatings do automotive parts get?", "Commonly e-coat or zinc-nickel to the OEM specification, applied by our approved finishing partners and managed by us.")],
    [("Case study: robot-welded exhaust hanger", "/case-exhaust-hanger.html"), ("Metal finishes explained", "/metal-finishes-explained.html"), ("Pressing or laser cut and fold?", "/pressing-vs-laser-cut-and-fold.html")],
    img=("part-door-card-bracket.webp", 800, 600), img_alt="Pressed aluminium door card bracket made by Genex", img_cap="A large aluminium door card bracket, pressed in Walsall."))

made.append(sector("defence", "Defence", "Defence Metal Assemblies & Fabrication | Genex UK",
    "Documented, traceable metal pressings, fabrications and complete assemblies for defence, in aluminium, stainless steel and titanium. ISO 9001, ISO 14001, Cyber Essentials. Walsall, UK.",
    "Defence assemblies, documented and ready when needed.",
    "Defence is one of our major sectors. We make complete, ready-to-install metal assemblies with documented quality and full traceability.",
    "Genex supplies the defence sector with UK-made pressings, fabrications and complete assemblies in aluminium, stainless steel and titanium, with customer-specified coatings, full traceability, ISO 9001 and ISO 14001, and Cyber Essentials for secure handling of drawings.",
    ["Complete, ready-to-install metal assemblies", "Pressings and fabrications from one-offs to repeat production", "Parts in aluminium, stainless steel and titanium", "Customer-specified coatings, managed by us", "Kits and assemblies packed and labelled to your requirements"],
    [("Security", "Cyber Essentials", "Your drawings and data handled securely."),
     ("Traceability", "Order to delivery", "Every stage recorded against your order, with material certificates."),
     ("Sovereign supply", "Made in the UK", "Manufactured in Walsall, with fast reaction when requirements change."),
     ("Quality", "ISO 9001 &amp; 14001", "Re-audited by BSI in 2026 with zero non-conformances.")],
    RUN_STD,
    [("metal-pressings", "Metal pressings"), ("welding-and-fabrication", "Welding & fabrication"), ("cnc-machining", "CNC machining"), ("assembly-and-finishing", "Assembly & finishing")],
    [],
    [("Do you work in defence?", "Yes. Defence is one of our major sectors."),
     ("Which materials do you use for defence work?", "Aluminium, stainless steel and titanium, with customer-specified coatings."),
     ("How do you protect our drawings?", "We hold Cyber Essentials, and drawings are seen only by the Genex team and the approved partners who need them."),
     ("Can you handle one-off and low-volume work?", "Yes, from one-off parts to repeat production.")],
    [("How we work", "/how-we-work.html"), ("Quality and certificates", "/quality.html"), ("Materials", "/materials.html")],
    img=("f-multistage.webp", 1280, 580), img_alt="Multi-stage presswork at Genex", img_cap="Multi-stage presswork in our press shop."))

made.append(sector("construction", "Construction", "Construction Brackets, Fixings & Assemblies | Genex UK",
    "High-volume brackets, fixings and structural and modular metal assemblies for construction, with traceability for the golden thread. ISO 9001, ISO 14001. Walsall, UK.",
    "Construction brackets and assemblies, on time.",
    "High-volume brackets, fixings and modular assemblies for contractors and building-product makers, including when the last-minute order comes in.",
    "Genex makes high-volume pressed brackets and fixings and structural and modular metal assemblies for the construction sector, on presses up to 200 tonnes in material up to 5 mm, with ISO 14001, full traceability for the golden thread, and coated steels and finishes for site conditions.",
    ["Cable basket ceiling and wall brackets, in several lengths", "Fixings and brackets in pre-galvanised and coated steels", "Prefabricated frames and modular assemblies", "Raised-floor components"],
    [("Volume", "Up to 200 t presses", "High-volume pressings, from a few hundred to millions."),
     ("Golden thread", "Full traceability", "Material certificates and records from order to delivery."),
     ("Environment", "ISO 14001", "Environmental management, with eco-conscious coatings available."),
     ("Speed", "Quick turnaround", "Procured, produced and delivered fast when a site needs parts.")],
    RUN_STD,
    [("metal-pressings", "Metal pressings"), ("laser-cutting-and-folding", "Laser cutting & folding"), ("assembly-and-finishing", "Assembly & finishing")],
    ["ceiling", "floor"],
    [("What do you make for construction?", "High-volume brackets and fixings, such as cable basket ceiling and wall brackets, plus prefabricated frames and modular assemblies."),
     ("Can you support the golden thread?", "Yes. Every order is traceable, with material certificates and records from enquiry to delivery."),
     ("Which steels suit outdoor and site use?", "Pre-galvanised and coated steels are common for construction brackets; we can advise on the finish for your environment.")],
    [("Case study: raised-floor base plates", "/case-raised-floor-base-plates.html"), ("Metal finishes explained", "/metal-finishes-explained.html"), ("Materials", "/materials.html")],
    img=("part-ceiling-bracket.webp", 800, 600), img_alt="Pre-galvanised cable basket ceiling bracket made by Genex", img_cap="A pre-galvanised cable basket ceiling bracket."))

made.append(sector("data-centres", "Data centres", "Data Centre & Power Metalwork: Enclosures, Frames, Floors | Genex UK",
    "Raised-floor base plates, fabricated enclosures, frames and welded assemblies for data-centre, power-distribution and industrial-equipment builders. Walsall, UK.",
    "Metalwork for data centres and power.",
    "We already press the base plates that hold up raised data-centre floors, and make enclosures, frames and welded assemblies for equipment builders.",
    "Genex supplies data-centre, power-distribution and industrial-equipment builders with raised-floor base plates on progression tooling, fabricated enclosures, frames and welded assemblies, finished and ready for the next stage of production.",
    ["Raised-floor base plates, run on a progression press", "Fabricated enclosures and frames", "Welded assemblies and panels", "Brackets and cable-management parts"],
    [("Volume", "Progression presswork", "Repeat parts at the lowest price per part."),
     ("Fabrication", "Enclosures &amp; frames", "Laser cut, folded, welded and finished."),
     ("Supply chain", "Fewer hand-offs", "Pressing, fabrication, finishing and assembly from one supplier."),
     ("Delivery", "Our own vehicles", "Packed to protect finished panels and frames.")],
    RUN_STD,
    [("metal-pressings", "Metal pressings"), ("laser-cutting-and-folding", "Laser cutting & folding"), ("welding-and-fabrication", "Welding & fabrication")],
    ["floor", "ceiling"],
    [("Do you make parts for raised floors?", "Yes. We press raised-floor base plates on a progression press, for data centres and offices."),
     ("Can you make enclosures?", "Yes: laser cut, folded, welded and finished, as individual parts or complete assemblies.")],
    [("Case study: raised-floor base plates", "/case-raised-floor-base-plates.html"), ("Pressing or laser cut and fold?", "/pressing-vs-laser-cut-and-fold.html")],
    img=("part-floor-base-plates.webp", 800, 600), img_alt="Pressed raised-floor base plates made by Genex", img_cap="Raised-floor base plates, run on a progression press.", core=False))

made.append(sector("medical-and-catering", "Medical & catering", "Stainless Steel Medical & Catering Fabrication | Genex UK",
    "Food-safe and hygienic stainless steel assemblies for medical and catering, TIG welded and polished, built complete with sinks, taps and fittings. Walsall, UK.",
    "Stainless assemblies, built complete.",
    "Food-safe and hygienic stainless assemblies, TIG welded and polished, from mortuary preparation tables to sinks supplied with their fittings.",
    "Genex fabricates stainless steel assemblies for medical and catering use, laser cut, folded, TIG welded and polished to a mirror or brushed finish, and supplies them complete with sinks, taps, drains and fittings, ready to install.",
    ["Mortuary preparation tables with built-in sinks and drains", "Sinks and wash stations supplied with taps and fittings", "Food-safe stainless frames, panels and assemblies", "Catering equipment parts"],
    [("Hygiene", "Stainless steel", "Mirror or brushed finish, easy to clean."),
     ("Welding", "TIG", "Clean, cosmetic welds on stainless."),
     ("Complete", "Fittings included", "Sinks, taps and drains sourced and fitted."),
     ("Delivery", "Ready to install", "Inspected, packed and delivered on our own vehicles.")],
    RUN_STD,
    [("laser-cutting-and-folding", "Laser cutting & folding"), ("welding-and-fabrication", "Welding & fabrication"), ("assembly-and-finishing", "Assembly & finishing")],
    ["mortuary"],
    [("Do you make stainless steel medical equipment?", "Yes, such as mortuary preparation tables built complete with a sink and drain."),
     ("What finish can you give stainless steel?", "Mirror polish or a brushed finish, to suit the application."),
     ("Can you supply the fittings too?", "Yes. Sinks, taps, drains and fittings are sourced and fitted, so the product arrives ready to install.")],
    [("Case study: mortuary preparation table", "/case-mortuary-table.html"), ("Materials", "/materials.html"), ("Metal finishes explained", "/metal-finishes-explained.html")],
    img=("medical-sink.webp", 817, 937), img_alt="Stainless steel mortuary table with built-in sink made by Genex", img_cap="A mortuary preparation table, built complete.", core=False))

# ================= how we work =================
made.append(page("how-we-work", "about", "How We Work: From Drawing to Delivery | Genex UK",
    "How a project runs at Genex UK: enquiry and manufacturability review, quotation, first parts and PPAP, production with in-process checks, finishing and assembly, packing and delivery on our own vehicles.",
    [HOME, ("About", "/about.html"), ("How we work", "/how-we-work.html")],
    "How we work", "From your drawing to your door.",
    "What happens at each stage, what you receive, and how we check it, so you know exactly what working with Genex looks like.",
    "A Genex project runs in seven stages: enquiry, manufacturability review, quotation, first parts (inspection report or PPAP), production with in-process checks, finishing and assembly, then packing and delivery on Genex's own vehicles. Every stage is recorded against the order, so it's traceable from enquiry to delivery.",
    [
        sec("stages", "The seven stages", "01 · Stages", "The seven stages", "", ol_steps([
            ("Enquiry", "You send a drawing or 3D model, quantities, material and finish. We reply within one working day. NDA on request."),
            ("Manufacturability review", "We check the design against the route: features that add cost, material availability, tolerances that need special attention. Problems are raised now, not at first-off."),
            ("Quotation", "A written quote with the process route, piece price, any tooling quoted separately, and lead times. Where pressing and laser cut and fold are close, we price both."),
            ("First parts", "A first-article inspection report as standard, or a PPAP submission to the level your customer requires."),
            ("Production", "Parts made to your schedule, with first-off, in-process and final inspection against the control plan, and material certificates held against every batch."),
            ("Finishing and assembly", "Coatings managed through approved partners, inserts fitted, assemblies built and tested, all under one part number."),
            ("Packing and delivery", "Packed to your specification, labelled for your goods-in, and delivered on our own 3.5 t or 7.5 t vehicles.")])),
        sec("receive", "What you receive", "02 · Documents", "What you receive",
            "", cards([("At quote", "Written quotation", "Route, piece price, tooling and lead time."),
                       ("At first parts", "Inspection report", "Dimensional results against the drawing, or a full PPAP."),
                       ("Every batch", "Material certificates", "Held against the batch and available on request."),
                       ("Every delivery", "Delivery paperwork", "Labels, reports and container tickets to suit your system.")])),
        sec("if", "If something goes wrong", "03 · Problems", "If something goes wrong",
            "<p>Call us first, so we can contain it straight away. Problems are logged and investigated under our ISO 9001 system, with corrective action owned by a named person and dated containment. Anyone can also raise a quality or environmental concern directly with our Managing Director through our <a class=\"link\" href=\"/concern.html\">concern form</a>.</p>"),
        sec("start", "Starting", "04 · Start", "Starting a project",
            "<p>The quickest route is to <a class=\"link\" href=\"/rfq.html\">send your drawing</a> with quantities. If you're early in a design and want advice on the most cost-effective route, call <a class=\"link\" href=\"tel:+441922710050\">01922 710050</a>. Early manufacturing conversations save more money than late cost-reduction exercises.</p>"),
    ],
    [("How fast do you reply to an enquiry?", "Within one working day."),
     ("Do you sign NDAs?", "Yes. Tick the NDA option on the quote form and we'll send our mutual NDA before you share full drawings."),
     ("Can you help before the design is finished?", "Yes. Early advice on the route, materials and features usually saves the most cost.")],
    cta_label="Send a drawing"))

# ================= materials =================
made.append(page("materials", "capabilities", "Materials We Work With: Steel, Stainless, Aluminium | Genex UK",
    "The metals Genex presses, cuts, folds, welds and machines: mild steel, coated steels, stainless steel, aluminium, copper and brass, with typical uses, finishes and design notes for each.",
    [HOME, CAP, ("Materials", "/materials.html")],
    "Materials", "The right metal for the job.",
    "Mild steel, coated steels, stainless steel, aluminium, copper and brass: what each is good for, which processes suit it, and what to watch for.",
    "Genex works mainly in mild steel, stainless steel and aluminium, plus coated steels such as pre-galvanised, and copper and brass for folded parts. Mild steel is the lowest-cost, most formable choice; stainless resists corrosion and suits food and medical use; aluminium saves weight. The right choice depends on where the part lives and what it has to do.",
    [
        sec("compare", "At a glance", "01 · Compare", "Materials at a glance", "",
            '<div class="table-wrap"><table class="spec-table"><thead><tr><th scope="col">Material</th><th scope="col">Good for</th><th scope="col">Processes at Genex</th><th scope="col">Watch for</th></tr></thead><tbody>'
            '<tr><th scope="row">Mild steel</th><td>Brackets, panels, frames; lowest cost, easy to form and weld</td><td>Pressing, laser, folding, welding, machining</td><td>Needs a coating against corrosion</td></tr>'
            '<tr><th scope="row">Coated steel (pre-galvanised, pre-painted)</th><td>Construction and outdoor parts</td><td>Pressing, laser, folding</td><td>Cut edges and welds may need touching up</td></tr>'
            '<tr><th scope="row">Stainless steel</th><td>Corrosion resistance, food, catering, medical, cosmetic parts</td><td>Pressing, laser, folding, TIG welding, polishing</td><td>More springback; specify the surface finish</td></tr>'
            '<tr><th scope="row">Aluminium</th><td>Weight-critical parts</td><td>Pressing, laser, folding, MIG and TIG welding</td><td>Grade and temper decide how tight it can bend</td></tr>'
            '<tr><th scope="row">Copper and brass</th><td>Electrical and decorative parts</td><td>Laser cutting, folding</td><td>Tell us the grade; send the drawing to confirm</td></tr>'
            '<tr><th scope="row">Titanium</th><td>Specialist defence parts</td><td>Ask us</td><td>Discussed per project</td></tr>'
            '</tbody></table></div>'),
        sec("choose", "Choosing", "02 · Choosing", "How to choose",
            ul(["<strong>Where does it live?</strong> Indoors, outdoors, wet, food contact or clean room changes the answer.",
                "<strong>What does it carry?</strong> Strength and stiffness requirements decide grade and thickness.",
                "<strong>Does weight matter?</strong> Aluminium saves weight but costs more per kilo.",
                "<strong>Is it seen?</strong> Cosmetic parts may suit stainless or a powder coat.",
                "<strong>What does your customer specify?</strong> Automotive and defence drawings often name the grade."]) +
            "<p>If you'd accept an equivalent grade, say so on the RFQ: it avoids a re-quote if your first choice isn't available in your thickness.</p>"),
        sec("finish", "Finishes", "03 · Finishes", "Finishes for each material",
            "<p>Mild steel usually needs protection: e-coat, zinc or zinc-nickel plating, or powder coat. Stainless is often left bare, polished or passivated. Aluminium can be left bare or powder coated. See <a class=\"link\" href=\"/metal-finishes-explained.html\">metal finishes explained</a>.</p>"),
        related([("Design guide", "/design-guide.html"), ("Metal finishes explained", "/metal-finishes-explained.html"), ("Laser cutting & folding", "/laser-cutting-and-folding.html")]),
    ],
    [("Which materials does Genex work with?", "Mainly mild steel, stainless steel and aluminium, plus coated steels, copper and brass, and titanium for specialist defence work."),
     ("Can you suggest a material?", "Yes. Tell us what the part does and where it lives, and we'll suggest a grade and finish."),
     ("Do you supply material certificates?", "Yes. Material certificates are held against every batch.")],
    cta_label="Ask about materials"))

# ================= case studies =================
CASES = ("Projects", "/projects.html")


def case(slug, part_key, title, desc, h1, lead, answer, challenge, route, detail, result, faqs_extra=None, extra_fig=None):
    pid, img, name, _d, chip, sector_name = PARTS[part_key]
    route_html = '<ol class="case__route">' + ''.join(f'<li><b>{i + 1:02d}</b>{r}</li>' for i, r in enumerate(route)) + '</ol>'
    sections = [
        sec("part", "The part", "01 · The part", name, f"<p>{challenge}</p>",
            fig(img, 800, 600, f"{name} made by Genex", f"{name}. {chip}.")),
        sec("route", "Process route", "02 · Route", "How we make it", "", route_html),
        sec("detail", "Engineering detail", "03 · Detail", "The engineering detail", f"<p>{detail}</p>"),
        sec("result", "What the customer gets", "04 · Result", "What the customer gets", f"<p>{result}</p>"),
    ]
    if extra_fig:
        sections[0]["html"] = sections[0]["html"].replace("</article>", extra_fig + "</article>")
    sections.append(related([("All projects", "/projects.html"), ("Request a quote for a similar part", "/rfq.html")], "Read next"))
    art = {"@context": "https://schema.org", "@type": "Article", "headline": h1, "description": desc, "author": {"@id": f"{BASE}/#org"},
           "publisher": {"@id": f"{BASE}/#org"}, "image": f"{BASE}/assets/img/{img}", "inLanguage": "en-GB", "url": f"{BASE}/{slug}.html"}
    return page(slug, "about", title, desc, [HOME, CASES, (name, f"/{slug}.html")], f"Case study · {sector_name}", h1, lead, answer, sections, faqs_extra, art, cta_label="Quote a similar part")


made.append(case("case-mortuary-table", "mortuary",
    "Case Study: Stainless Mortuary Preparation Table | Genex UK",
    "How Genex laser cut, folded, TIG welded and mirror-polished a stainless steel mortuary preparation table, and supplied it complete with sink, taps and drain.",
    "A mortuary preparation table, built complete.",
    "Laser cut, folded, TIG welded, mirror polished and fitted with its sink, taps and drain: one finished product from one supplier.",
    "Genex made a stainless steel mortuary preparation table as a complete product: laser-cut and press-brake folded stainless, TIG welded and mirror polished, with the sink, taps and drain sourced and fitted, so the customer received a finished table ready to install.",
    "A purpose-built table for body preparation and cleaning in a mortuary. It needs a hygienic, easy-to-clean surface, a sink for cleaning, and a drain set in to remove waste fluids.",
    ["Laser cut from stainless sheet", "Folded on the press brake", "TIG welded", "Mirror polished", "Sink, taps and drain sourced and fitted", "Inspected, packed and delivered"],
    "Designed and built complete as a dedicated product. TIG welding keeps the welds clean on stainless, and the mirror polish leaves a surface that's easy to keep hygienic.",
    "One finished, ready-to-install product, instead of separate metalwork, plumbing parts and a fitting job: one order, one delivery and one point of accountability."))

made.append(case("case-exhaust-hanger", "exhaust",
    "Case Study: Robot-Welded Stainless Exhaust Hanger | Genex UK",
    "How Genex makes an automotive exhaust hanger from two stainless pressings and two wire forms, robot welded, with weld penetration checked by macro section.",
    "A robot-welded exhaust hanger.",
    "Two pressings and two wire forms, robot welded into one automotive assembly, with weld quality measured, not assumed.",
    "Genex makes an automotive exhaust hanger from two stainless steel pressings (1.5 mm) and two wire forms, robot welded into one assembly with clinch nuts fitted. Wire-form positions are held to a tight tolerance after welding, and weld penetration is checked by macro section.",
    "The bracket wraps around the exhaust and hangs it from the vehicle on rubber mounts. It's made from two pressed components welded together with two wire forms.",
    ["Single-action press, 100 t", "Robotic weld", "Clinch nut insert (rivet gun)", "Inspect and pack"],
    "The critical features are the positions of the wire forms after welding, held to a tight tolerance so the rubber mounts locate correctly on the vehicle, and weld quality, checked by macro penetration measurement.",
    "A complete, repeatable welded assembly delivered as one part number, with the evidence that every weld meets the specification."))

made.append(case("case-raised-floor-base-plates", "floor",
    "Case Study: Raised-Floor Base Plates on a Progression Press | Genex UK",
    "How Genex presses mild steel base plates for raised floors in data centres and offices on a progression press, the lowest-cost route for repeat volumes.",
    "Raised-floor base plates, pressed at volume.",
    "A repeat, high-volume part made in one pass on a progression press, the lowest-cost route once volumes are steady.",
    "Genex presses 3 mm mild steel base plates for raised-floor systems used in data centres and offices on a 100 tonne progression press, so each part is made complete in a single coil-fed pass at the lowest price per part.",
    "Base plates form part of an assembly that raises the floor so services can run underneath the working area. Typical uses are data centres and offices, where floors are laid in large areas and parts are needed in volume.",
    ["Progression press, 100 t"],
    "A progression tool makes the finished plate, with its raised centre boss and four fixing holes, from coil in one pass, so there is no handling between operations.",
    "Consistent parts at the lowest price per part, at the volumes large floor installations need."))

# ================= projects hub =================
proj_cards = ''.join(f'<li><a class="part" href="{u}"><img src="/assets/img/{PARTS[k][1]}" width="800" height="600" loading="lazy" alt="{PARTS[k][2]} made by Genex"><div class="part__body"><p class="label">{PARTS[k][5]}</p><h3>{PARTS[k][2]}</h3><p>{PARTS[k][3]}</p><span class="chip">{lbl}</span></div></a></li>'
                     for k, u, lbl in [("mortuary", "/case-mortuary-table.html", "Case study"), ("exhaust", "/case-exhaust-hanger.html", "Case study"), ("floor", "/case-raised-floor-base-plates.html", "Case study"),
                                       ("fuel", "/industries.html#p-fuel-filter", PARTS["fuel"][4]), ("door", "/industries.html#p-door-card", PARTS["door"][4]), ("ceiling", "/industries.html#p-ceiling", PARTS["ceiling"][4]),
                                       ("panel", "/industries.html#p-panel", PARTS["panel"][4]), ("roller", "/industries.html#p-roller", PARTS["roller"][4])])
made.append(page("projects", "about", "Projects & Case Studies | Genex UK",
    "Real parts Genex makes: case studies of a stainless mortuary table, a robot-welded exhaust hanger and raised-floor base plates, plus brackets, panels and rollers across automotive, construction, medical and machinery.",
    [HOME, CASES], "Projects", "Real parts. Real capability.",
    "Parts we make for customers across automotive, construction, data centres, medical and machinery, with the process route behind each.",
    "Genex's projects include a stainless mortuary preparation table built complete, a robot-welded automotive exhaust hanger, raised-floor base plates on a progression press, fuel filter and door card brackets, cable basket brackets, scanner-lane panels and a lawn mower roller. Customer names are left out for confidentiality.",
    [sec("all", "All projects", "Projects", "Parts we make", "<p>Photos of real parts we produce. Customer names and part numbers are left out for confidentiality.</p>",
         f'<ul class="parts parts--inline parts--projects">{proj_cards}</ul>')],
    None, cta_label="Quote a similar part"))

# ================= glossary =================
TERMS = [
    ("Progression tool", "A press tool with several stations that a coil-fed strip moves through one step per stroke, producing a finished part on every stroke. Also called a progressive die."),
    ("Single-action tool", "A press tool that does one operation per stroke, such as blanking or forming."),
    ("Multi-stage tooling", "A set of separate tools, with the part moved between them for each operation."),
    ("Blank", "The flat piece of metal cut to shape before it's formed or folded."),
    ("Pierce", "Punching a hole in sheet metal in a press tool."),
    ("Press brake", "A machine that folds sheet metal between a punch and a die. Genex's Amada HRB1003 folds up to 6 mm at 3 m."),
    ("Crowning", "Compensation on a press brake that keeps the bend angle constant along the full length of a long bend."),
    ("Springback", "The tendency of metal to open up slightly after bending; tools and programs allow for it."),
    ("Hem (hemmed edge)", "An edge folded back on itself to remove the sharp edge and stiffen the panel."),
    ("Bend relief", "A small cut where a bend meets an edge, to stop the material tearing."),
    ("PEM insert", "A self-clinching nut, stud or standoff pressed permanently into sheet metal."),
    ("Projection welding", "A resistance weld that joins a nut or stud to a sheet through small raised projections."),
    ("Spot welding", "A resistance weld joining overlapping sheets at points, without filler metal."),
    ("MIG welding", "Arc welding with a continuously fed wire, used manually or by robot."),
    ("TIG welding", "Arc welding with a tungsten electrode, used for clean, precise welds, especially on stainless and aluminium."),
    ("5-axis machining", "CNC machining where the cutter can approach the part from many angles, so complex shapes are made in one set-up."),
    ("E-coat", "Electrophoretic coating: an even, thin paint layer applied by electrical charge, common on automotive brackets."),
    ("Zinc-nickel plating", "A plated coating that gives steel higher corrosion resistance than plain zinc."),
    ("Powder coating", "A dry paint applied electrostatically and cured with heat, giving a thick, hard-wearing coloured finish."),
    ("Passivation", "A treatment that restores stainless steel's natural corrosion resistance after fabrication."),
    ("Pre-galvanised steel", "Steel coated with zinc before it's formed, common for construction brackets."),
    ("First-article inspection (FAI)", "A full check of the first parts against the drawing before production runs."),
    ("PPAP", "Production Part Approval Process: the automotive industry's evidence pack that a supplier's process makes good parts consistently. Levels 1 to 5 set how much is submitted."),
    ("APQP", "Advanced Product Quality Planning: the structured way automotive launches are planned."),
    ("Control plan", "The document that sets which features are checked, how and how often during production."),
    ("PPM", "Parts per million: a defect rate. Genex reports 0 PPM."),
    ("OTIF", "On time, in full: the share of orders delivered complete and on schedule. Genex reports 98%+."),
    ("ISO 9001", "The international standard for quality management systems."),
    ("ISO 14001", "The international standard for environmental management systems."),
    ("IATF 16949", "The automotive industry's quality management standard. Genex is working towards it."),
    ("Cyber Essentials", "A UK government-backed scheme that certifies basic cyber security controls."),
    ("Golden thread", "The construction industry's requirement for accurate, traceable information about a building and its components."),
]
gl = '<dl class="glossary">' + ''.join(f'<div id="{t.lower().split(" (")[0].replace(" ", "-")}"><dt>{t}</dt><dd>{d}</dd></div>' for t, d in TERMS) + '</dl>'
defined = {"@context": "https://schema.org", "@type": "DefinedTermSet", "name": "Sheet metal and pressings glossary", "url": f"{BASE}/glossary.html",
           "hasDefinedTerm": [{"@type": "DefinedTerm", "name": t, "description": d} for t, d in TERMS]}
made.append(page("glossary", "about", "Sheet Metal & Pressings Glossary | Genex UK",
    "Plain-English definitions of the terms used in metal pressing, sheet metal fabrication, welding, finishing and supplier quality: progression tools, hemming, PEM inserts, e-coat, PPAP, OTIF and more.",
    [HOME, ("Resources", "/resources.html"), ("Glossary", "/glossary.html")],
    "Glossary", "The words, in plain English.",
    "The terms you'll meet in pressing, fabrication, finishing and supplier quality, explained simply.",
    "This glossary explains the terms used in metal pressing, sheet metal fabrication, welding, finishing and supplier quality, from progression tools and hemmed edges to PPAP, PPM and OTIF, in plain English.",
    [sec("terms", "Terms", "A–Z", "Terms", "", gl)], None, defined, cta_label="Ask us a question"))

# ================= resources hub =================
res = lambda items: '<div class="res">' + ''.join(f'<a href="{u}"><span class="kind">{k}</span><h3>{h}</h3><p>{p}</p><span class="go">{g} →</span></a>' for k, h, p, u, g in items) + '</div>'
made.append(page("resources", "about", "Resources: Guides, Downloads & Documents | Genex UK",
    "Guides for engineers and buyers (pressing vs laser cut and fold, hemmed edges, metal finishes, materials, design rules), our capability pack, certificates, policies and a glossary.",
    [HOME, ("Resources", "/resources.html")],
    "Resources", "For engineers and buyers.",
    "Guides, downloads and documents to help you design better parts, choose the right route and approve us as a supplier.",
    "Genex publishes practical guides for engineers and buyers: choosing between pressing and laser cut and fold, hemmed edges, metal finishes, materials and design rules, plus a capability pack, certificates, policies and a glossary of trade terms.",
    [sec("guides", "Guides", "01 · Guides", "Guides", "", res([
        ("Route", "Pressing or laser cut and fold?", "When a press tool pays back.", "/pressing-vs-laser-cut-and-fold.html", "Read"),
        ("Design", "Design guide", "Design rules for holes, bends, materials and what to send.", "/design-guide.html", "Read"),
        ("Design", "Hemmed edges explained", "Safer, stiffer and no deburring.", "/hemmed-edges.html", "Read"),
        ("Finishing", "Metal finishes explained", "E-coat, zinc, powder coat or passivation?", "/metal-finishes-explained.html", "Read"),
        ("Materials", "Materials guide", "Steel, stainless, aluminium and more.", "/materials.html", "Read"),
        ("Reference", "Glossary", "The trade terms in plain English.", "/glossary.html", "Read")])),
     sec("downloads", "Downloads", "02 · Downloads", "Downloads and documents", "", res([
        ("PDF · 2 pages", "Capability pack", "Capabilities, accreditations and sectors for your supplier file.", "/assets/genex-capability-pack.pdf", "Download"),
        ("Quality", "Certificates", "ISO 9001, ISO 14001, Cyber Essentials, Achilles.", "/quality.html#certificates", "View"),
        ("Documents", "Policies and terms", "Policies, conditions of sale and purchase.", "/documents.html", "View")])),
     sec("work", "Our work", "03 · Work", "Our work", "", res([
        ("Projects", "Projects and case studies", "Real parts and how we make them.", "/projects.html", "View"),
        ("Process", "How we work", "From drawing to delivery, stage by stage.", "/how-we-work.html", "Read"),
        ("Video", "Inside Genex", "Our machines and people on film.", "/#film", "Watch")]))],
    None, cta_label="Send a drawing"))

print("generated", len(made), "pages:", ", ".join(made))
