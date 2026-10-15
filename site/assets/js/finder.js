/* Genex UK — "Can Genex make your part?" route finder + RFQ prefill.
   Rules mirror the pressing design guide: laser below ~2k/yr, stage tooling 2k–10k, progressive 10k+,
   pressing gauge 0.5–3.0 mm, laser to 25 mm. A first check only; an engineer confirms the route. */
(() => {
  const track = window.track || (() => {});
  const finder = document.querySelector('[data-finder]');
  if (finder) {
    const $ = sel => finder.querySelector(sel);
    const out = { box: $('[data-result]'), status: $('[data-r-status]'), route: $('[data-r-route]'), why: $('[data-r-why]'), tool: $('[data-r-tool]'), ppap: $('[data-r-ppap]'), notes: $('[data-r-notes]') };
    const MAT = {
      mild: null,
      hsla: 'High-strength steel needs larger bend radii (about 1.5–2× thickness) and allowance for springback.',
      structural: 'Check your S355 grade is rolled at this thickness. We can suggest an equivalent if not.',
      stainless: 'Stainless springs back more and wears tools faster. We allow for both in the tool design.',
      aluminium: 'Tell us the temper. It decides how tight the bends can be.'
    };
    const OPS = {
      fasteners: 'Nuts and studs can be inserted in the tool or in a separate cell.',
      welding: 'Projection, spot, MIG and TIG welding are done in-house.',
      coating: 'E-coat, zinc and powder coat are managed through our approved finishers on one part number.',
      assembly: 'Sub-assemblies are built, checked and packed for your line.'
    };
    const fmt = n => Number(n).toLocaleString('en-GB');

    const run = () => {
      const t = parseFloat($('#f-thk').value) || 0;
      const size = parseFloat($('#f-size').value) || 0;
      const v = parseFloat($('#f-vol').value) || 0;
      const mat = $('#f-material').value;
      const ops = [...finder.querySelectorAll('[name=ops]:checked')].map(i => i.value);
      let status = ['ok', 'Within our range'], route, why, tool, ppap = 'PPAP to the level you need';
      const notes = [];

      if (t > 25) {
        status = ['no', 'Outside our range']; route = 'Talk to us first';
        why = `${t} mm is beyond our 25 mm laser capacity. Send the drawing and we'll tell you straight whether we can help, or who can.`;
        tool = 'Depends on route'; ppap = 'Depends on route';
      } else if (t > 3) {
        status = ['warn', 'Laser and fabrication route']; route = 'Laser cut, fold and fabricate';
        why = `At ${t} mm the part is above our 3.0 mm pressing gauge, so we'd laser cut it (up to 25 mm), fold it and weld if needed.`;
        tool = 'No press tooling';
        if (v >= 10000) notes.push('At this volume, ask about jigged welding fixtures to keep the piece price down.');
      } else if (t < 0.5) {
        status = ['warn', 'Below our standard gauge']; route = 'Talk to us first';
        why = `${t} mm is thinner than our standard 0.5 mm. Send the drawing and we'll confirm.`;
        tool = 'Depends on route';
      } else if (v < 2000) {
        route = 'Laser cut and fold';
        why = `At ${fmt(v)} parts a year there's no tooling to pay for. Laser cutting and press-brake folding gives the lowest total cost.`;
        tool = 'No press tooling'; ppap = 'PPAP or first-article inspection';
        notes.push('If volumes grow, we can move the part onto production tooling later.');
      } else if (v < 10000) {
        route = 'Single-stage or compound tooling';
        why = `At ${fmt(v)} parts a year, simpler stage tools keep tooling cost down and still give a pressed-part price.`;
        tool = 'Typically 12–17 weeks';
      } else {
        route = 'Progressive tooling';
        why = `At ${fmt(v)} parts a year, a progressive tool gives the lowest piece price. It makes a finished part on every press stroke.`;
        tool = 'Typically 12–17 weeks';
        if (v < 20000) notes.push('Between 10,000 and 20,000 a year, stage tooling can also make sense. We will price both.');
      }
      const proto = parseFloat(($('#f-proto') || {}).value) || 0;
      if (proto > 0 && t <= 25 && route !== 'Laser cut and fold' && route !== 'Laser cut, fold and fabricate') notes.unshift(`Start with ${fmt(proto)} laser-cut prototypes. There's no tooling cost, and you decide on tooling when the design is frozen.`);
      if (size > 600 && t <= 25) notes.push("Large part: we'll confirm press and laser bed fit when we see the drawing.");
      if (MAT[mat] && t <= 25) notes.push(MAT[mat]);
      ops.forEach(o => notes.push(OPS[o]));

      out.status.className = 'pill-s ' + status[0]; out.status.textContent = status[1];
      out.route.textContent = route; out.why.textContent = why; out.tool.textContent = tool; out.ppap.textContent = ppap;
      out.notes.innerHTML = '';
      notes.forEach(n => { const li = document.createElement('li'); li.textContent = n; out.notes.append(li); });
      out.box.classList.remove('is-updating'); void out.box.offsetWidth; out.box.classList.add('is-updating');
      finder.dataset.route = route;
    };

    let debounce;
    finder.addEventListener('input', () => { clearTimeout(debounce); debounce = setTimeout(run, 120); });
    finder.addEventListener('change', run);
    finder.addEventListener('submit', () => {
      let r = finder.querySelector('[name=route]');
      if (!r) { r = document.createElement('input'); r.type = 'hidden'; r.name = 'route'; finder.append(r); }
      r.value = finder.dataset.route || '';
      track('finder_submit', { route: r.value, volume: $('#f-vol').value, thickness: $('#f-thk').value });
    });
    run();
  }

  /* RFQ page: prefill from the quick check (query string) */
  const rfq = document.querySelector('[data-rfq]');
  if (rfq && location.search) {
    const q = new URLSearchParams(location.search);
    const names = { mild: 'Mild steel (DC01–DC04)', hsla: 'High-strength steel (HC340LA–HC420LA)', structural: 'Structural steel (S355)', stainless: 'Stainless 304/316', aluminium: 'Aluminium 5xxx/6xxx' };
    const set = (name, val) => { const el = rfq.querySelector(`[name="${name}"]`); if (el && val && !el.value) el.value = val; };
    if (q.get('volume')) set('volume', Number(q.get('volume')).toLocaleString('en-GB'));
    if (q.get('protoqty')) set('protoqty', q.get('protoqty'));
    const mat = [names[q.get('material')] || '', q.get('thickness') ? q.get('thickness') + ' mm' : ''].filter(Boolean).join(', ');
    if (mat) set('material', mat);
    const bits = [];
    if (q.get('route')) bits.push('Route from quick check: ' + q.get('route'));
    if (q.get('size')) bits.push('Largest dimension: ' + q.get('size') + ' mm');
    const ops = q.getAll('ops'); if (ops.length) bits.push('Also needed: ' + ops.join(', '));
    if (bits.length) set('notes', bits.join('\n'));
    if (mat || bits.length) { const more = rfq.querySelector('details.more'); if (more) more.open = true; }
  }
})();
