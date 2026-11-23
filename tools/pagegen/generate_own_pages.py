"""Own page for every capability and sector (Michael Beese, 18 Nov 2026).

Writes ONLY the eleven pages below. generate.py is not run for this: four of its pages have been
hand-edited since and running it would overwrite them. The small helpers are copied from
generate.py for that reason (importing it would run it).

Every fact here is already on the site (industries.html, capabilities.html, assembly-and-finishing.html,
metal-finishes-explained.html) or is Michael's own wording. Nothing new is claimed.

Run from the repo root:  python tools/pagegen/generate_own_pages.py   then   cd site && python build.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gen_lib import page, sec, fig, cards, service, parts_block, HOME, CAP  # noqa: E402

SEC = ("Sectors", "/industries.html")


def ul(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def ol_steps(items):
    return '<ol class="steps">' + "".join(f"<li><div><h3>{h}</h3><p>{p}</p></div></li>" for h, p in items) + "</ol>"


def linklist(links):
    return '<ul class="linklist">' + "".join(f'<li><a href="{u}">{n} →</a></li>' for n, u in links) + "</ul>"


def related(links, heading="Related reading"):
    return sec("related", "Related", "Read next", heading, "", linklist(links))


def send_block(extra=""):
    return sec("quote", "What to send", "Get a price", "What to send for a quote",
               ul(["A 3D model (STEP) and a dimensioned drawing (PDF or DXF)",
                   "Material and thickness, and any equivalent grades you'd accept",
                   "Quantity per order and per year",
                   "Finish or coating, and any cosmetic faces",
                   "Critical tolerances, and the approval you need (first-article report or PPAP level)",
                   "When you need the first parts"] + ([extra] if extra else [])) +
               '<p><a class="link" href="/rfq.html">Send your drawing for a quote</a>.</p>')


QUALITY = sec("quality", "Quality checks", "Quality", "How every part is checked",
              ul(["<strong>First-off inspection</strong> against the drawing before a batch runs",
                  "<strong>In-process checks</strong> against the control plan while it runs",
                  "<strong>Final inspection</strong> before packing, with material certificates held against the batch",
                  "<strong>Traceability</strong> from enquiry to delivery, with customer-specific reports if you need them",
                  "<strong>PPAP</strong> Levels 1 to 5 when your customer requires it"]) +
              '<p>Certified to ISO 9001 and ISO 14001, and re-audited by BSI in 2026 with zero non-conformances. <a class="link" href="/quality.html">More on quality</a>.</p>')

RUN_STD = [("Enquiry and review", "Send the drawing, volumes and specification; we review manufacturability and flag cost risks."),
           ("Quote", "Route, piece price, any tooling and lead time, in writing."),
           ("First parts", "First-article inspection report, or PPAP to the level required."),
           ("Production", "Parts made to your schedule, with in-process and final checks."),
           ("Delivery", "Packed to your specification and delivered on our own vehicles.")]

ONE_SUPPLIER = ("Supply chain", "Fewer hand-offs", "Presswork, welding, folding, finishing and assembly from one supplier.")
OWN_VEHICLES = ("Delivery", "Our own vehicles", "Packed to your specification and delivered on our own vehicles.")


def sector(slug, name, title, desc, h1, lead, answer, makes, needs, caps, parts, faqs, guides, img=None, core=True, make_h2=None):
    """Same six blocks, in the same order, as the existing sector pages."""
    lname = name.lower().replace('&', '&amp;')
    art = "an" if lname[0] in "aeiou" else "a"
    sections = [
        sec("make", "What we make", "01 · Products", make_h2 or f"What we make for {lname}", ul(makes), fig(*img) if img else ""),
        sec("needs", "What you need from a supplier", "02 · Requirements", "What you need from a supplier, and how we meet it", "", cards(needs)),
        sec("run", "How a project runs", "03 · Process", f"How {art} {lname} project runs with Genex", "", ol_steps(RUN_STD)),
        sec("capabilities", "Capabilities used", "04 · Capabilities", "Capabilities we use", "", linklist(caps)),
    ]
    if parts:
        sections.append({"id": "examples", "toc": "Examples", "html": parts_block(parts, "Examples")})
    sections.append(related(guides))
    return page(slug, "industries", title, desc, [HOME, SEC, (name, f"/{slug}.html")],
                ("Core sector · " if core else "Sector · ") + name.replace('&', '&amp;'), h1, lead, answer, sections, faqs,
                cta_label="Discuss your project")


PRESS = ("Metal pressings", "/metal-pressings.html")
LASER = ("Laser cutting &amp; folding", "/laser-cutting-and-folding.html")
WELD = ("Welding &amp; fabrication", "/welding-and-fabrication.html")
CNC = ("CNC machining", "/cnc-machining.html")
ASSY = ("Inserting &amp; assembly", "/assembly-and-finishing.html")
FINISH = ("Finishing &amp; coating", "/finishing-and-coating.html")
TUBE = ("Tube manipulation", "/tube-manipulation.html")
DELIVER = ("Packing &amp; delivery", "/packing-and-delivery.html")

made = []

# ================= capability pages =================

made.append(page(
    "finishing-and-coating", "capabilities",
    "Metal Finishing & Coating, Managed on One Order | Genex UK",
    "E-coat, zinc and zinc-nickel plating, powder coating and passivation through approved, audited finishing partners, managed by Genex so your parts arrive finished on one order.",
    [HOME, CAP, ("Finishing & coating", "/finishing-and-coating.html")],
    "Finishing &amp; coating",
    "Your parts arrive finished, on one order.",
    "E-coat, plating, powder coat and more through our approved finishers, managed by us on one order.",
    "Genex supplies parts finished: e-coat, zinc and zinc-nickel plating, powder coating, passivation and more, applied by approved, audited finishing partners. Genex manages the logistics, the specification and the inspection, so you deal with one supplier.",
    [
        sec("finishes", "Finishes we manage", "01 · Protection", "Finishes we manage",
            "<p>E-coat, zinc and zinc-nickel plating, powder coating, passivation and more, through our approved, audited finishing partners.</p>",
            cards([("Coating", "E-coat", "An even, thin corrosion-resistant coat that reaches into recesses. Common on automotive brackets."),
                   ("Plating", "Zinc &amp; zinc-nickel", "Plating that protects steel sacrificially."),
                   ("Coating", "Powder coat", "A thicker, coloured, hard-wearing finish for visible parts."),
                   ("Treatment", "Passivation", "Helps stainless steel resist corrosion.")]) +
            fig("d-finishing.webp", 800, 600, "Black e-coated pressed steel bracket", "An e-coated bracket, finished to customer specification.")),
        sec("managed", "Managed by us", "02 · One order", "Finishing, managed by us",
            "<p>Coatings are applied by our approved, audited finishing partners and managed by us. We manage the logistics, the specification and the inspection, so your parts arrive finished on one order and you deal with one supplier.</p>"),
        sec("choose", "Choosing a finish", "03 · Materials", "Which finish for which material",
            ul(["<strong>Mild steel</strong> usually needs protection: e-coat, zinc or zinc-nickel plating, or powder coat.",
                "<strong>Stainless steel</strong> is often left bare, polished or passivated.",
                "<strong>Aluminium</strong> can be left bare or powder coated."]) +
            '<p>Not sure which finish? See <a class="link" href="/metal-finishes-explained.html">metal finishes explained</a>.</p>'),
        {"id": "examples", "toc": "Examples", "html": parts_block(["fuel", "panel", "roller", "mortuary"], "Parts we make")},
        QUALITY,
        send_block("The coating specification, if your customer sets one"),
        related([("Metal finishes explained", "/metal-finishes-explained.html"), ("Materials", "/materials.html"), ASSY]),
    ],
    [("Do you do the coating yourselves?", "Coatings are applied by our approved, audited finishing partners and managed by us, so you deal with one supplier."),
     ("Which finish is best for automotive brackets?", "E-coat and zinc-nickel are common on automotive brackets."),
     ("Do stainless steel parts need a finish?", "Often not, but passivation after fabrication helps stainless resist corrosion, and polishing gives a cosmetic finish.")],
    service("Finishing and coating", "E-coat, plating, powder coating and passivation through approved finishing partners, managed by Genex on one order.", "finishing-and-coating")))

made.append(page(
    "tube-manipulation", "capabilities",
    "Tube Manipulation: Bent & Welded Tube Assemblies | Genex UK",
    "Bent and welded tube frames and assemblies in stainless and mild steel, welded to pressings and brackets where the design needs it. Walsall, West Midlands.",
    [HOME, CAP, ("Tube manipulation", "/tube-manipulation.html")],
    "Tube manipulation",
    "Bent and welded tube, built into the assembly.",
    "Bent and welded tube frames and assemblies in stainless and mild steel.",
    "Genex makes bent tube frames and assemblies in stainless and mild steel, welded to pressings and brackets where the design needs it, then finished, inspected and packed with the rest of the order.",
    [
        sec("tube", "What we do", "01 · Tube", "Tube frames and assemblies",
            "<p>Bent tube frames and wire-form assemblies in stainless and mild steel, welded to pressings and brackets where the design needs it.</p>",
            fig("f-tube2.webp", 1280, 580, "Racks of bent stainless tube frames at Genex", "Bent stainless tube frames, racked for welding.")),
        sec("assembly", "Into the assembly", "02 · Build", "From bent tube to a finished assembly",
            "<p>Tube frames are welded to pressings and brackets where the design needs it, finished through our approved partners, then inspected and packed complete under one part number.</p>",
            linklist([WELD, FINISH, ASSY])),
        sec("products", "Where it started", "03 · Our own products", "Our own boot racks started here",
            "<p>Our classic-car boot racks, made in stainless and aluminium, started here.</p>"),
        QUALITY,
        send_block("Tube diameter, wall thickness and bend radii"),
        related([("Welding &amp; fabrication", "/welding-and-fabrication.html"), ("Medical &amp; catering", "/medical-and-catering.html"), ("Materials", "/materials.html")]),
    ],
    [("Which materials do you work in?", "Tube frames and assemblies are made in stainless and mild steel."),
     ("Can you weld tube to other parts?", "Yes. Tube frames are welded to pressings and brackets where the design needs it."),
     ("Can you supply the finished assembly?", "Yes. We bring our own parts together with inserts, bought-in components and finishing, then assemble, inspect and pack the finished product under one part number.")],
    service("Tube manipulation", "Bent and welded tube frames and assemblies in stainless and mild steel.", "tube-manipulation")))

made.append(page(
    "packing-and-delivery", "capabilities",
    "Packed and Delivered by Us: Our Own Transport Fleet | Genex UK",
    "Packed and delivered by us. Our own 3.5 and 7.5 tonne vehicles, custom racking and crates, and labels and paperwork to suit your goods-in.",
    [HOME, CAP, ("Packing & delivery", "/packing-and-delivery.html")],
    "Packing &amp; delivery",
    "Packed and delivered by us.",
    # Michael's own sentence (email, 18 Nov 2026). Keep word for word.
    "Dedicated Genex UK transport fleet ensure your goods are delivered safely.",
    "Genex packs orders to the customer's specification and delivers on its own 3.5 tonne and 7.5 tonne vehicles, with custom racking and crates, and labels, reports and container tickets to suit your goods-in.",
    [
        sec("fleet", "Our own vehicles", "01 · Transport", "Our own vehicles", "",
            cards([("Transport", "Our own vehicles", "A 3.5 tonne and a 7.5 tonne vehicle, so large orders arrive in one trip."),
                   ("Packing", "Racking &amp; crates", "Custom racks and crates protect parts from our door to your dock."),
                   ("Paperwork", "Traceable to the order", "Labels, reports and container tickets to suit your goods-in.")])),
        sec("packing", "Packing", "02 · Packing", "Packed to your specification",
            "<p>Parts are given a final inspection, then packed to your specification with your labels and a delivery note. Custom racks and crates protect them from our door to your dock.</p>"),
        sec("trace", "Traceability", "03 · Paperwork", "Traceable from enquiry to delivery",
            "<p>Every order is recorded from the moment the enquiry arrives, through purchasing and production, to delivery. We can produce customer-specific reports and container tickets so your goods-in is quick.</p>"),
        QUALITY,
        related([("How we work", "/how-we-work.html"), ASSY, ("Quality &amp; accreditations", "/quality.html")]),
    ],
    [("Do you deliver?", "Yes, on our own 3.5 tonne and 7.5 tonne vehicles, with racking and crates to protect your parts."),
     ("Can you label and document deliveries to our system?", "Yes. We can produce customer-specific labels, reports and container tickets to suit your goods-in.")],
    service("Packing and delivery", "Orders packed to specification and delivered on Genex's own vehicles.", "packing-and-delivery")))

# ================= sector pages =================

made.append(sector(
    "rail", "Rail", "Rail Pressings & Welded Assemblies | Genex UK",
    "Pressings and welded assemblies (robotic MIG, manual MIG and TIG), with full finishing, for rolling-stock and rail-infrastructure suppliers. Walsall, UK.",
    "Pressings and welded assemblies for rail.",
    "Pressings plus welded assemblies, robotic MIG and manual MIG and TIG, with full finishing, for rolling-stock and rail-infrastructure suppliers who want a shorter vendor list.",
    "Genex offers rolling-stock and rail-infrastructure suppliers pressings and welded assemblies (robotic MIG, manual MIG and TIG), finished through approved partners and packed complete.",
    ["Pressings", "Welded assemblies: robotic MIG, and manual MIG and TIG", "Welded assemblies, finished and packed complete"],
    [("Welding", "Robotic MIG, manual MIG and TIG", "Verified, repeatable processes."),
     ("Finishing", "Full finishing", "Through our approved finishing partners, managed by us on one order."),
     ("Supply chain", "A shorter vendor list", "Presswork, welding, finishing and assembly from one supplier."),
     OWN_VEHICLES],
    [PRESS, WELD, FINISH], [],
    [("What do you offer rail suppliers?", "Pressings and welded assemblies (robotic MIG, manual MIG and TIG), with full finishing, packed complete."),
     ("Can you supply assemblies finished?", "Yes. Coatings are applied by our approved, audited finishing partners and managed by us, so you deal with one supplier.")],
    [("How we work", "/how-we-work.html"), ("Quality &amp; accreditations", "/quality.html")],
    img=("f-mig.webp", 1280, 580, "A welder MIG welding a folded steel panel at Genex", "MIG welding a folded steel panel."), core=False,
    make_h2="What we offer rail suppliers"))

made.append(sector(
    "aerospace-and-space", "Aerospace & space", "Aerospace & Space: Precision Fabrication | Genex UK",
    "Precision fabrication and complete assemblies for aerospace and space, with each job's manufacturing and documentation needs reviewed at enquiry. Listed on the Midlands Space Cluster.",
    "Precision fabrication for aerospace and space.",
    "Precision fabrication and complete assemblies, with each job's manufacturing and documentation needs reviewed at enquiry.",
    "Genex supplies precision fabrication and complete assemblies for aerospace and space, reviews each job's manufacturing and documentation needs at enquiry, and is listed on the Midlands Space Cluster.",
    ["Precision fabrication", "Complete assemblies", "Advanced alloys and specialist coatings through approved partners"],
    [("Review", "Reviewed at enquiry", "Each job's manufacturing and documentation needs are reviewed at enquiry."),
     ("Network", "Midlands Space Cluster", "Genex is listed on the Midlands Space Cluster, which supports regional firms moving into the space sector."),
     ONE_SUPPLIER,
     OWN_VEHICLES],
    [LASER, WELD], [],
    [("Is Genex part of the Midlands Space Cluster?", "Genex is listed on the Midlands Space Cluster, which supports regional firms moving into the space sector."),
     ("How do you handle documentation?", "Each job's manufacturing and documentation needs are reviewed at enquiry.")],
    [("Quality &amp; accreditations", "/quality.html"), ("Materials", "/materials.html")],
    img=("f-laserfold.webp", 1280, 580, "A laser-cut panel after folding at Genex", "A laser-cut panel after folding.")))

made.append(sector(
    "security", "Security", "Panels for Security Equipment & Scanner Lanes | Genex UK",
    "Laser-cut, folded and welded panels for security equipment, including scanner-lane access panels for airport security lanes. Walsall, UK.",
    "Panels for security equipment.",
    "Laser-cut, folded and welded panels for security equipment, including the scanner-lane access panels we make for airport security lanes.",
    "Genex makes laser-cut, folded and welded panels for security equipment in mild steel, including scanner-lane access panels for airport security lanes in a range of sizes, with undercoat and powder topcoat through approved finishing partners.",
    ["Laser-cut, folded and welded panels", "Scanner-lane access panels, in a range of sizes, that finish the framework of security scanner lanes in airports"],
    [("Fabrication", "Cut, folded and welded", "Mild steel, laser cut, folded and welded."),
     ("Finish", "Undercoat and powder topcoat", "Through our approved finishing partners."),
     ("Range", "A range of sizes", "Access panels made in a range of sizes to finish the installation."),
     OWN_VEHICLES],
    [LASER, WELD, FINISH], ["panel"],
    [("What do you make for security equipment?", "Laser-cut, folded and welded panels, including scanner-lane access panels for airport security lanes."),
     ("How are the panels finished?", "With an undercoat and powder topcoat, through our approved finishing partners.")],
    [("Pressing or laser cut and fold?", "/pressing-vs-laser-cut-and-fold.html"), ("Metal finishes explained", "/metal-finishes-explained.html")],
    img=("part-access-panel.webp", 800, 600, "Powder-coated steel scanner-lane access panel made by Genex", "A scanner-lane access panel, powder coated.")))

made.append(sector(
    "machinery", "Machinery, food & packaging", "Machinery, Food & Packaging Metalwork | Genex UK",
    "Machine frames, guards, brackets, panels and sub-assemblies for machine builders, including food-processing and packaging equipment. Walsall, UK.",
    "Metalwork for machine builders.",
    "Machine frames, guards, brackets, panels and sub-assemblies for machine builders, including food-processing and packaging equipment that has to be strong and easy to clean.",
    "Genex supplies machine builders, including makers of food-processing and packaging equipment, with frames, guards, brackets, panels and sub-assemblies, formed, welded and finished by one supplier.",
    ["Machine frames and guards", "Brackets and panels", "Sub-assemblies, including for food-processing and packaging equipment that has to be strong and easy to clean"],
    [("Fabrication", "Formed, welded and finished", "Formed, welded and finished components."),
     ONE_SUPPLIER,
     ("Finish", "E-coat", "The lawn mower rear roller is e-coated by our approved coating partner."),
     OWN_VEHICLES],
    [LASER, WELD, FINISH], ["roller"],
    [("What do you make for machine builders?", "Machine frames, guards, brackets, panels and sub-assemblies, including for food-processing and packaging equipment.")],
    [("How we work", "/how-we-work.html"), ("Metal finishes explained", "/metal-finishes-explained.html")],
    img=("part-rear-roller.webp", 800, 600, "Black e-coated rolled steel lawn mower rear roller", "A lawn mower rear roller: rolled, seam-welded and e-coated."), core=False))

made.append(sector(
    "automation", "Automation & intralogistics", "Automation & Intralogistics Metalwork | Genex UK",
    "Conveyor frames, machine guards, safety gates, fabricated bases and support structures for automation and intralogistics. Walsall, UK.",
    "Frames, guards and structures for automation.",
    "Conveyor frames, machine guards, safety gates, fabricated bases and support structures that have to arrive right first time, because the installation date is already fixed.",
    "Genex supplies automation and intralogistics firms with conveyor frames, machine guards, safety gates, fabricated bases and support structures, with presswork, welding, folding, finishing and assembly from one supplier.",
    ["Conveyor frames", "Machine guards and safety gates", "Fabricated bases and support structures"],
    [ONE_SUPPLIER,
     ("Approval", "First parts checked", "First-article inspection report, or PPAP to the level required."),
     ("Finishing", "Managed by us", "Through our approved finishing partners, on one order."),
     OWN_VEHICLES],
    [LASER, WELD, FINISH], [],
    [("What do you make for automation?", "Conveyor frames, machine guards, safety gates, fabricated bases and support structures.")],
    [("How we work", "/how-we-work.html"), ("Pressing or laser cut and fold?", "/pressing-vs-laser-cut-and-fold.html")],
    img=("f-laserfold.webp", 1280, 580, "A laser-cut panel after folding at Genex", "A laser-cut panel after folding."), core=False))

made.append(sector(
    "agriculture", "Agriculture & off-highway", "Agricultural & Off-Highway Metalwork | Genex UK",
    "Rollers, brackets, guards and welded assemblies for agricultural and off-highway equipment, in coated steels. Walsall, UK.",
    "Metalwork for agriculture and off-highway.",
    "Rollers, brackets, guards and welded assemblies for agricultural and off-highway equipment, in coated steels.",
    "Genex supplies makers of agricultural and off-highway equipment with rollers, brackets, guards and welded assemblies in coated steels, formed, welded and finished by one supplier.",
    ["Rollers", "Brackets and guards", "Welded assemblies, in coated steels"],
    [("Fabrication", "Formed, welded and finished", "Formed, welded and finished components."),
     ONE_SUPPLIER,
     ("Finishing", "Managed by us", "Through our approved finishing partners, on one order."),
     OWN_VEHICLES],
    [PRESS, WELD, FINISH], [],
    [("Do you make parts for agricultural equipment?", "Yes. Rollers, brackets, guards and welded assemblies for agricultural and off-highway equipment, in coated steels.")],
    [("How we work", "/how-we-work.html"), ("Metal finishes explained", "/metal-finishes-explained.html")],
    img=("f-mig.webp", 1280, 580, "A welder MIG welding a folded steel panel at Genex", "MIG welding a folded steel panel."), core=False))

made.append(sector(
    "electrical-hardware", "Electrical hardware", "Electrical Hardware: Brackets, Fixings & Enclosure Parts | Genex UK",
    "Brackets, fixings and enclosure parts for electrical installations, including the cable-basket brackets used in commercial buildings. Walsall, UK.",
    "Brackets and fixings for electrical installations.",
    "Brackets, fixings and enclosure parts for electrical installations, including the cable-basket brackets used in commercial buildings.",
    "Genex makes brackets and fixings for electrical installations, including pressed pre-galvanised cable-basket brackets in ceiling and wall-mount versions and different lengths.",
    ["Brackets and fixings for electrical installations", "Cable-basket brackets in ceiling and wall-mount versions, in different lengths to suit the job"],
    [("Volume", "High-volume pressing", "The cable basket ceiling bracket is a high-volume production part."),
     ("Material", "Pre-galvanised steel", "Our cable basket ceiling bracket is pre-galvanised steel, 3 mm."),
     ONE_SUPPLIER,
     OWN_VEHICLES],
    [PRESS], ["ceiling"],
    [("Do you make cable-basket brackets?", "Yes. A pre-galvanised ceiling bracket and a wall-mount version, in different lengths to suit the job."),
     ("Which materials do you press?", "Mild steel, stainless steel, aluminium and coated steels such as pre-galvanised.")],
    [("Construction", "/construction.html"), ("Materials", "/materials.html")],
    img=("part-ceiling-bracket.webp", 800, 600, "Pre-galvanised steel ceiling bracket for hanging electrical cable basket", "A pre-galvanised cable basket ceiling bracket."), core=False))

made.append(sector(
    "aftermarket", "Aftermarket", "Aftermarket, Consumer & Architectural Metalwork | Genex UK",
    "Aftermarket accessories, consumer goods and architectural metalwork, including Genex's own classic-car boot racks in stainless and aluminium. Walsall, UK.",
    "Aftermarket, consumer and architectural metalwork.",
    "Aftermarket accessories, consumer goods and architectural metalwork, including our own classic-car boot racks in stainless and aluminium.",
    "Genex makes aftermarket accessories, consumer goods and architectural metalwork, including its own classic-car boot racks in stainless and aluminium.",
    ["Our own classic-car boot racks, in stainless and aluminium", "Aftermarket accessories, consumer goods and architectural metalwork"],
    [("Materials", "Stainless and aluminium", "Our own boot racks are made in stainless and aluminium."),
     ("Finish", "Cosmetic finishes", "Polishing gives a cosmetic finish. Powder coating gives a coloured, hard-wearing finish for visible parts."),
     ONE_SUPPLIER,
     OWN_VEHICLES],
    [TUBE, WELD, FINISH], [],
    [("Do you make a product of your own?", "Yes. Our own classic-car boot racks are made in stainless and aluminium."),
     ("Can you supply a finished product?", "Yes. We bring our own parts together with inserts, bought-in components and finishing, then assemble, inspect and pack the finished product under one part number.")],
    [("Metal finishes explained", "/metal-finishes-explained.html"), ("Materials", "/materials.html")]))

print("wrote", len(made), "pages:", ", ".join(made))
