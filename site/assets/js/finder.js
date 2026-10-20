/* Genex UK — "Can Genex make your part?" route finder + RFQ prefill.
   Limits are Genex's own published figures: presswork up to 5 mm on presses to 200 t,
   folding up to 6 mm at 3 m (Amada HRB1003), laser cutting up to 25 mm.
   The volume break points are a first guide only; the team confirms the route from the drawing. */
(() => {
  const track = window.track || (() => {});
  const finder = document.querySelector('[data-finder]');
  if (finder) {
    const $ = sel => finder.querySelector(sel);
    const out = { box: $('[data-result]'), status: $('[data-r-status]'), route: $('[data-r-route]'), why: $('[data-r-why]'), tool: $('[data-r-tool]'), ppap: $('[data-r-ppap]'), notes: $('[data-r-notes]') };
    const LIMITS = { press: 5, fold: 6, foldLength: 3000, laser: 25, pressVolume: 5000, laserVolume: 1000 };
    const MAT = {
      mild: null,
      stainless: 'Stainless steel: tell us the grade and the finish you need. We TIG weld stainless in-house.',
      aluminium: 'Aluminium: tell us the grade and temper, as it decides how tight the bends can be.',
      other: 'Copper, brass and coated steels: send the spec and we will confirm the route.'
    };
    const OPS = {
      welding: 'Robotic and manual MIG, TIG, spot and projection welding are all done in-house.',
      fasteners: 'PEM, stud and nut inserting is done in-house, in the press or as a separate operation.',
      machining: 'Machined features are finished on our 5-axis machining centre.',
      coating: 'Coatings are managed through our approved finishers, on one order with us.',
      assembly: 'We can assemble, inspect and pack the finished product under one part number.'
    };
    const fmt = n => Number(n).toLocaleString('en-GB');

    const run = () => {
      const t = parseFloat($('#f-thk').value) || 0;
      const size = parseFloat($('#f-size').value) || 0;
      const v = parseFloat($('#f-vol').value) || 0;
      const mat = $('#f-material').value;
      const ops = [...finder.querySelectorAll('[name=ops]:checked')].map(i => i.value);
      let status = ['ok', 'Within our range'], route, why, tool = 'None needed', ppap = 'First-article inspection, or PPAP if you need it';
      const notes = [];

      if (t > LIMITS.laser) {
        status = ['no', 'Talk to us first']; route = 'Send us the drawing';
        why = `${t} mm is beyond our ${LIMITS.laser} mm laser capacity. Send the drawing and we will tell you straight whether we can help.`;
        tool = 'Depends on route'; ppap = 'Depends on route';
      } else if (t > LIMITS.fold) {
        status = ['warn', 'Cut and fabricate']; route = 'Laser cut, then weld or machine';
        why = `At ${t} mm we laser cut the profile (up to ${LIMITS.laser} mm) and weld or machine it. Folding goes up to ${LIMITS.fold} mm.`;
      } else if (v >= LIMITS.pressVolume && t <= LIMITS.press) {
        route = 'Pressing';
        why = `At ${fmt(v)} parts a year, pressing gives the lowest price per part. We run progression and single-action presswork on presses up to 200 tonnes.`;
        tool = 'A production tool, quoted separately';
        if (v < 20000) notes.push('At this volume we will price laser cut and fold as well, so you can compare.');
      } else if (v >= LIMITS.laserVolume && t <= LIMITS.press) {
        route = 'Laser cut and fold, then pressing as volumes grow';
        why = `At ${fmt(v)} parts a year, laser cutting and folding avoids tooling cost. If volumes rise, the part can move to presswork.`;
      } else {
        route = 'Laser cut and fold';
        why = `At ${fmt(v)} parts a year there is no tooling to pay for. Laser cutting and press-brake folding gives the lowest total cost.`;
      }
      if (t > 0 && t < 0.5) { status = ['warn', 'Check with us']; notes.unshift(`${t} mm is very thin. Send the drawing and we will confirm.`); }
      if (size > LIMITS.foldLength && t <= LIMITS.laser) { status = ['warn', 'Large part']; notes.push(`Our press brake folds up to ${LIMITS.foldLength / 1000} m long. Longer parts can often be fabricated; send the drawing.`); }
      else if (size > 600 && route === 'Pressing') notes.push('Large pressing: we will confirm press and tool fit from the drawing.');
      if (t <= LIMITS.fold && size <= LIMITS.foldLength && route !== 'Pressing') notes.push('Need a safe edge? Our hemming tool folds a closed edge in one hit.');
      if (MAT[mat] && t <= LIMITS.laser) notes.push(MAT[mat]);
      ops.forEach(o => notes.push(OPS[o]));

      /* What drives the cost on this route (guidance, not a price) */
      const DRIVERS = {
        press: ['The production tool, a one-off cost spread across every part', 'Material and thickness: most of the price per part at volume', 'Number of operations and inserted fasteners', 'Coating and packing'],
        laser: ['Cutting length and material thickness', 'Number of bends, and any hemmed edges', 'Welding, inserts and finishing after cutting', 'Batch size: set-up is shared across the batch'],
        fab: ['Plate thickness and cutting time', 'Weld length and process', 'Machining of thick sections', 'Finishing and handling of large parts']
      };
      const key = route === 'Pressing' ? 'press' : (t > LIMITS.fold ? 'fab' : 'laser');
      let drv = finder.querySelector('[data-r-drivers]');
      if (!drv) { drv = document.createElement('div'); drv.className = 'finder__drivers'; drv.setAttribute('data-r-drivers', ''); out.notes.after(drv); }
      drv.hidden = t > LIMITS.laser;
      drv.innerHTML = '<b>What drives the cost</b><ul></ul>';
      DRIVERS[key].forEach(d => { const li = document.createElement('li'); li.textContent = d; drv.querySelector('ul').append(li); });

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
    const names = { mild: 'Mild steel', stainless: 'Stainless steel', aluminium: 'Aluminium', other: 'Other (copper, brass or coated steel)' };
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
