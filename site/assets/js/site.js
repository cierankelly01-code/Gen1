/* Genex UK — site behaviour. Progressive enhancement only: every page works without this file. */
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Analytics hook — swap the body for GA4 / Plausible without touching call sites */
  window.track = (name, props = {}) => { (window.dataLayer = window.dataLayer || []).push({ event: name, ...props }); };
  document.addEventListener('click', e => {
    const a = e.target.closest('a[href*="rfq"], a[href^="tel:"], a[href^="mailto:"]');
    if (a) track('cta_click', { href: a.getAttribute('href'), where: a.closest('section,header,footer')?.className.split(' ')[0] || 'page' });
  });

  /* Year */
  document.querySelectorAll('[data-year]').forEach(el => el.textContent = new Date().getFullYear());

  /* Sticky header state */
  const header = document.querySelector('.header');
  if (header) {
    const onScroll = () => header.classList.toggle('is-stuck', scrollY > 40);
    onScroll(); addEventListener('scroll', onScroll, { passive: true });
  }

  /* Close the mobile menu on link tap / Escape */
  const toggle = document.querySelector('.nav-toggle');
  if (toggle) {
    toggle.addEventListener('click', e => { if (e.target.closest('.nav-panel a')) toggle.open = false; });
    addEventListener('keydown', e => { if (e.key === 'Escape' && toggle.open) { toggle.open = false; toggle.querySelector('summary').focus(); } });
    toggle.addEventListener('toggle', () => document.documentElement.style.overflow = toggle.open ? 'hidden' : '');
  }

  /* Mega menus: hover on desktop, click/keyboard everywhere */
  const mms = [...document.querySelectorAll('.has-mm')];
  const closeAll = except => mms.forEach(li => { if (li !== except) { li.classList.remove('is-open'); li.querySelector('.mm-btn').setAttribute('aria-expanded', 'false'); } });
  mms.forEach(li => {
    const btn = li.querySelector('.mm-btn');
    btn.addEventListener('click', () => { const open = !li.classList.contains('is-open'); closeAll(li); li.classList.toggle('is-open', open); btn.setAttribute('aria-expanded', String(open)); });
    li.addEventListener('mouseenter', () => btn.setAttribute('aria-expanded', 'true'));
    li.addEventListener('mouseleave', () => { if (!li.classList.contains('is-open')) btn.setAttribute('aria-expanded', 'false'); });
  });
  document.addEventListener('click', e => { if (!e.target.closest('.has-mm')) closeAll(); });
  addEventListener('keydown', e => { if (e.key === 'Escape') { const open = document.querySelector('.has-mm.is-open .mm-btn'); closeAll(); open && open.focus(); } });

  /* Hero headline rise */
  const hero = document.querySelector('.hero');
  if (hero) requestAnimationFrame(() => requestAnimationFrame(() => hero.classList.add('is-ready')));

  /* Reveal system */
  const io = new IntersectionObserver(entries => entries.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
  }), { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
  document.querySelectorAll('[data-reveal]').forEach(el => { el.style.setProperty('--d', el.dataset.revealDelay || 0); io.observe(el); });

  /* Showstopper: the hero runs a progressive die — one station per stroke, on a loop */
  const press = document.querySelector('[data-press]');
  if (press) {
    const feats = [...press.querySelectorAll('.st-feat, .st-part-final')];
    const stations = [...press.querySelectorAll('[data-station]')];
    const hls = [...press.querySelectorAll('[data-hl]')];
    const pips = [...press.querySelectorAll('.pip')];
    const descs = [...press.querySelectorAll('[data-desc]')];
    const stage = press.querySelector('.press__stage');
    const svg = press.querySelector('.story__svg');
    const strokeEl = press.querySelector('[data-stroke]');
    const XS = [100, 260, 420, 580, 740, 920];
    let step = -1, strokes = 0, hitTimer, loopTimer, resumeTimer, visible = true, hovering = false, userHold = false, paused = false;
    let mode = 'svg', ctl = null;   // 'svg' | '3d' | 'video'

    const pan = () => {
      if (!svg || innerWidth > 700) { if (svg) svg.style.transform = ''; return; }
      const w = svg.getBoundingClientRect().width, view = stage.clientWidth;
      const x = XS[Math.max(0, step - 1)] / 1000 * w;
      const max = w - view + 32;
      svg.style.transform = `translateX(${-Math.min(max, Math.max(0, x - view / 2))}px)`;
    };
    /* pips + description only (used by every mode) */
    const setUI = s => {
      pips.forEach((pp, i) => { pp.classList.toggle('is-on', i + 1 === s); pp.classList.toggle('is-done', mode === 'svg' && i + 1 < s); pp.setAttribute('aria-pressed', String(i + 1 === s)); });
      descs.forEach(d => d.classList.toggle('is-on', +d.dataset.desc === Math.max(1, s)));
    };
    const countStroke = () => { strokes++; if (strokeEl) strokeEl.textContent = String(strokes).padStart(4, '0'); };
    const set = s => {
      step = s;
      feats.forEach(f => f.classList.toggle('is-shown', +f.dataset.op <= s));
      stations.forEach(st => st.classList.toggle('is-active', +st.dataset.station === s));
      hls.forEach(h => h.classList.toggle('is-active', +h.dataset.hl === s));
      setUI(s);
      if (s >= 1 && s <= 5 && !reduce && mode !== 'video') {
        countStroke();
        press.dataset.hit = '1'; clearTimeout(hitTimer); hitTimer = setTimeout(() => press.dataset.hit = '0', 200);
      }
      pan();
    };
    const running = () => mode !== '3d' && !reduce && !paused && visible && !hovering && !userHold && !document.hidden;
    const tick = () => {
      clearTimeout(loopTimer);
      if (!running()) return;
      const next = step >= 6 ? 0 : step + 1;
      set(next);
      loopTimer = setTimeout(tick, next === 6 ? 3200 : next === 0 ? 450 : 1350);
    };
    const resume = () => { clearTimeout(loopTimer); loopTimer = setTimeout(tick, 900); };

    pips.forEach((pp, i) => pp.addEventListener('click', () => {
      userHold = true; clearTimeout(loopTimer); clearTimeout(resumeTimer);
      press.querySelector('[data-descs]')?.setAttribute('aria-live', 'polite');
      if (mode === '3d') { ctl.focus(i); track('press_step', { op: i + 1, mode }); return; }
      set(i + 1); track('press_step', { op: i + 1, mode });
      resumeTimer = setTimeout(() => { userHold = false; resume(); }, 9000);
    }));
    if (matchMedia('(hover: hover)').matches) {
      press.addEventListener('mouseenter', () => { hovering = true; clearTimeout(loopTimer); });
      press.addEventListener('mouseleave', () => { hovering = false; resume(); });
    }
    new IntersectionObserver(es => { visible = es[0].isIntersecting; visible ? resume() : clearTimeout(loopTimer); }, { threshold: 0.2 }).observe(press);
    document.addEventListener('visibilitychange', () => document.hidden ? clearTimeout(loopTimer) : resume());
    addEventListener('resize', pan);

    const pauseBtn = press.querySelector('[data-pause]');
    if (pauseBtn) {
      if (reduce) pauseBtn.hidden = true;
      pauseBtn.addEventListener('click', () => {
        paused = !paused;
        pauseBtn.textContent = paused ? 'Play' : 'Pause';
        pauseBtn.setAttribute('aria-pressed', String(paused));
        if (mode === '3d') { paused ? ctl.pause() : ctl.resume(); return; }
        paused ? clearTimeout(loopTimer) : resume();
      });
    }
    if (reduce) set(6); else { set(0); loopTimer = setTimeout(tick, 1100); }

    /* Upgrade path: real footage (data-video) → real-time 3D → SVG strip (already running) */
    const saveData = navigator.connection && navigator.connection.saveData;
    const canGL = () => { try { return !!document.createElement('canvas').getContext('webgl2'); } catch (e) { return false; } };
    const boot3d = () => {
      if (reduce || saveData || innerWidth < 640 || !canGL()) return;
      const go = () => import('/assets/js/press3d.js').then(m => {
        ctl = m.start(press, { onFocus: i => setUI(i + 1), onStroke: countStroke });
        if (!ctl) return;
        mode = '3d'; clearTimeout(loopTimer);
        if (paused) ctl.pause();
        track('press_mode', { mode: '3d' });
      }).catch(() => { /* stay on the SVG strip */ });
      ('requestIdleCallback' in window) ? requestIdleCallback(go, { timeout: 2500 }) : setTimeout(go, 1200);
    };
    const videoSrc = press.dataset.video;
    if (videoSrc && !reduce && !saveData) {
      const v = document.createElement('video');
      Object.assign(v, { muted: true, loop: true, playsInline: true, autoplay: true, preload: 'metadata' });
      v.className = 'press__video'; v.setAttribute('aria-hidden', 'true');
      if (press.dataset.poster) v.poster = press.dataset.poster;
      v.addEventListener('playing', () => { mode = 'video'; press.classList.add('press--video'); track('press_mode', { mode: 'video' }); }, { once: true });
      v.addEventListener('error', () => { v.remove(); boot3d(); }, { once: true });
      v.src = videoSrc;
      stage.prepend(v);
      if (pauseBtn) pauseBtn.addEventListener('click', () => { if (mode === 'video') paused ? v.pause() : v.play(); });
    } else {
      boot3d();
    }
  }

  /* v2 hero: real footage (data-video) → full-bleed 3D die (desktop) → still image */
  const hero2 = document.querySelector('[data-hero]');
  if (hero2) {
    const media = hero2.querySelector('.hero2__media');
    const live = hero2.querySelector('[data-live]');
    const pauseBtn2 = hero2.querySelector('[data-hero-pause]');
    const saveData2 = navigator.connection && navigator.connection.saveData;
    let ctl2 = null, paused2 = false, vid = null;
    const showLive = () => { if (live) live.hidden = false; };
    const boot3d2 = () => {
      if (reduce || saveData2 || innerWidth < 900) return;
      try { if (!document.createElement('canvas').getContext('webgl2')) return; } catch (e) { return; }
      const go = () => import('/assets/js/press3d.js').then(m => {
        ctl2 = m.start(hero2, { fill: true });
        if (ctl2) { showLive('Live: progressive tool, 5 stations'); track('press_mode', { mode: '3d-hero' }); }
      }).catch(() => {});
      ('requestIdleCallback' in window) ? requestIdleCallback(go, { timeout: 2500 }) : setTimeout(go, 1200);
    };
    if (hero2.dataset.video && !reduce && !saveData2) {
      vid = document.createElement('video');
      Object.assign(vid, { muted: true, loop: true, playsInline: true, autoplay: true, preload: 'metadata' });
      if (hero2.dataset.poster) vid.poster = hero2.dataset.poster;
      vid.addEventListener('playing', () => { hero2.classList.add('is-video'); showLive('Filmed at Genex, Walsall'); }, { once: true });
      vid.addEventListener('error', () => { vid.remove(); vid = null; boot3d2(); }, { once: true });
      vid.src = hero2.dataset.video;
      media.prepend(vid);
    } else boot3d2();
    pauseBtn2 && pauseBtn2.addEventListener('click', () => {
      paused2 = !paused2;
      pauseBtn2.textContent = paused2 ? 'Play' : 'Pause'; pauseBtn2.setAttribute('aria-pressed', String(paused2));
      if (ctl2) paused2 ? ctl2.pause() : ctl2.resume();
      if (vid) paused2 ? vid.pause() : vid.play();
    });
  }


  /* Film band: the reel only downloads and plays while it's on screen (and never under reduced motion / data saver) */
  document.querySelectorAll('[data-autoplay]').forEach(fig => {
    const v = fig.querySelector('video');
    if (!v || reduce || (navigator.connection && navigator.connection.saveData)) return;
    new IntersectionObserver(es => {
      if (es[0].isIntersecting) {
        if (!v.src) { v.src = v.dataset.src; v.addEventListener('playing', () => fig.classList.add('is-playing'), { once: true }); }
        v.play().catch(() => {});
      } else v.pause();
    }, { threshold: 0.35 }).observe(fig);
  });

  /* Video cards open in a modal player with sound and controls */
  const vmodal = document.querySelector('[data-vmodal]');
  if (vmodal && typeof vmodal.showModal === 'function') {
    const mv = vmodal.querySelector('video');
    const close = () => { mv.pause(); vmodal.close(); };
    document.querySelectorAll('button[data-video]').forEach(b => b.addEventListener('click', () => {
      mv.src = b.dataset.video; vmodal.querySelector('[data-vmodal-title]').textContent = b.dataset.title || '';
      vmodal.showModal(); mv.play().catch(() => {}); track('video_open', { src: b.dataset.video });
    }));
    vmodal.querySelector('[data-vmodal-close]').addEventListener('click', close);
    vmodal.addEventListener('click', e => { if (e.target === vmodal) close(); });
    vmodal.addEventListener('close', () => mv.pause());
  } else {
    document.querySelectorAll('button[data-video]').forEach(b => b.addEventListener('click', () => { location.href = b.dataset.video; }));
  }

  /* Concern form: quality or environmental concerns go to the MD's inbox (Supabase 'concerns' table) */
  const cform = document.querySelector('[data-concern]');
  if (cform) {
    const check = f => {
      const i = f.querySelector('input, select, textarea'); if (!i) return true;
      /* the database counts trimmed text, so the browser check must too */
      if (i.name === 'details') i.setCustomValidity(i.value.trim().length < 10 ? 'Tell us a little more' : '');
      const ok = i.disabled || i.checkValidity(); f.classList.toggle('is-invalid', !ok); i.setAttribute('aria-invalid', String(!ok)); return ok;
    };
    cform.querySelectorAll('.field').forEach(f => f.querySelector('input, select, textarea')?.addEventListener('blur', () => check(f)));
    cform.setAttribute('novalidate', '');
    cform.addEventListener('submit', async e => {
      e.preventDefault();
      const bad = [...cform.querySelectorAll('.field')].filter(f => !check(f));
      if (bad.length) { bad[0].querySelector('input, select, textarea').focus(); return; }
      const btn = cform.querySelector('[type=submit]'); btn.setAttribute('aria-busy', 'true');
      try {
        const cfg = window.GENEX_CFG || {}, fd = new FormData(cform);
        const spam = !!(fd.get('website_url') || '').toString().trim();   /* bots get the success screen; nothing is sent */
        if (!spam && cfg.supabaseUrl && cfg.supabaseAnonKey) {
          const val = k => (fd.get(k) || '').toString().trim() || null;
          const anon = fd.get('anonymous') !== null;   /* anonymous reports never carry contact details */
          const res = await fetch(cfg.supabaseUrl.replace(/\/$/, '') + '/rest/v1/concerns', {
            method: 'POST',
            headers: { apikey: cfg.supabaseAnonKey, Authorization: 'Bearer ' + cfg.supabaseAnonKey, 'Content-Type': 'application/json', Prefer: 'return=minimal' },
            body: JSON.stringify({ kind: val('kind'), details: val('details'), reference: val('reference'), name: anon ? null : val('name'), company: anon ? null : val('company'), email: anon ? null : val('email'), phone: anon ? null : val('phone'), anonymous: anon, source: location.href, status: 'new' })
          });
          if (!res.ok) throw new Error('insert ' + res.status);
        } else if (!spam) await new Promise(r => setTimeout(r, 700));   /* demo mode: no backend configured */
        track('concern_submit', { kind: fd.get('kind') });
        cform.hidden = true;
        const ok = document.querySelector('[data-concern-ok]'); ok.classList.add('is-shown'); ok.setAttribute('tabindex', '-1'); ok.focus();
      } catch (err) {
        btn.removeAttribute('aria-busy'); cform.querySelector('[data-neterr]').hidden = false;
      }
    });
    /* "Report anonymously" makes the contact fields optional */
    const anon = cform.querySelector('[name=anonymous]');
    /* anonymous: contact fields are switched off (disabled fields aren't validated or sent) */
    anon && anon.addEventListener('change', () => cform.querySelectorAll('[data-contact] .field').forEach(f => {
      const i = f.querySelector('input'); i.disabled = anon.checked; f.classList.toggle('is-off', anon.checked);
      if (anon.checked) { f.classList.remove('is-invalid'); i.removeAttribute('aria-invalid'); }
    }));
  }

  /* Supabase: upload drawings to the private 'rfq-files' bucket, then insert the RFQ row.
     The anon key can only INSERT (see supabase/setup.sql); it cannot read anything back. */
  async function submitToSupabase(form, cfg) {
    const base = cfg.supabaseUrl.replace(/\/$/, '');
    const auth = { apikey: cfg.supabaseAnonKey, Authorization: 'Bearer ' + cfg.supabaseAnonKey };
    const fd = new FormData(form);
    if ((fd.get('website_url') || '').toString().trim()) return;   /* spam trap filled: drop silently */
    const files = fd.getAll('files').filter(f => f && f.name && f.size);
    /* Mirrors the server-side rules in supabase/setup.sql (the server is the real gate) */
    const ALLOWED = /\.(step|stp|igs|iges|x_t|dxf|dwg|pdf|zip)$/i;
    if (files.length > 10) throw new Error('too many files');
    for (const f of files) {
      if (!ALLOWED.test(f.name) || f.size > 52428800) throw new Error('file type or size: ' + f.name);
    }
    const folder = (crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(36));
    const paths = [];
    for (const file of files) {
      const safe = file.name.replace(/[^\w.\-]+/g, '_').slice(-120);
      const path = `${folder}/${safe}`;
      const up = await fetch(`${base}/storage/v1/object/rfq-files/${path}`, {
        method: 'POST', headers: { ...auth, 'x-upsert': 'false', 'Content-Type': file.type || 'application/octet-stream' }, body: file
      });
      if (!up.ok) throw new Error('upload ' + up.status);
      paths.push(path);
    }
    const val = k => (fd.get(k) || '').toString().trim() || null;
    const row = {
      name: val('name'), company: val('company'), email: val('email'), phone: val('phone'), country: val('country'),
      part: val('part'), annual_volume: val('volume'), prototype_qty: val('protoqty'), material: val('material'),
      finish: val('finish'), stages: fd.getAll('stage').map(String), ppap: val('ppap'), needed_by: val('sop'),
      notes: val('notes'), nda_requested: fd.get('nda') !== null, files: paths, source: location.href, status: 'new'
    };
    const res = await fetch(`${base}/rest/v1/rfqs`, {
      method: 'POST', headers: { ...auth, 'Content-Type': 'application/json', Prefer: 'return=minimal' }, body: JSON.stringify(row)
    });
    if (!res.ok) throw new Error('insert ' + res.status);
  }

  /* RFQ form: drop zone, on-blur validation, designed states */
  const form = document.querySelector('[data-rfq]');
  if (form) {
    const drop = form.querySelector('.drop');
    const fileInput = drop?.querySelector('input[type=file]');
    const list = form.querySelector('[data-files]');
    const fmt = b => b > 1048576 ? (b / 1048576).toFixed(1) + ' MB' : Math.max(1, Math.round(b / 1024)) + ' KB';
    const renderFiles = () => {
      list.innerHTML = '';
      [...fileInput.files].forEach(f => {
        const li = document.createElement('li');
        li.innerHTML = '<span></span><span></span>';
        li.children[0].textContent = f.name; li.children[1].textContent = fmt(f.size);
        list.append(li);
      });
    };
    if (drop && fileInput) {
      ['dragenter', 'dragover'].forEach(t => drop.addEventListener(t, () => drop.classList.add('is-over')));
      ['dragleave', 'drop'].forEach(t => drop.addEventListener(t, () => drop.classList.remove('is-over')));
      fileInput.addEventListener('change', renderFiles);
    }

    const validate = field => {
      const input = field.querySelector('input, select, textarea');
      if (!input) return true;
      const ok = input.checkValidity();
      field.classList.toggle('is-invalid', !ok);
      input.setAttribute('aria-invalid', String(!ok));
      return ok;
    };
    form.querySelectorAll('.field').forEach(f => {
      const input = f.querySelector('input, select, textarea');
      input?.addEventListener('blur', () => validate(f));
      input?.addEventListener('input', () => f.classList.contains('is-invalid') && validate(f));
    });

    form.setAttribute('novalidate', '');
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const fields = [...form.querySelectorAll('.field')];
      const bad = fields.filter(f => !validate(f));
      if (bad.length) { bad[0].querySelector('input, select, textarea').focus(); track('rfq_error', { count: bad.length }); return; }
      const btn = form.querySelector('[type=submit]');
      btn.setAttribute('aria-busy', 'true');
      try {
        /* DEMO: no backend yet. In production this POSTs multipart to the RFQ endpoint,
           which files the lead into the Genex dashboard and emails sales@. */
        const cfg = window.GENEX_CFG || {};
        if (cfg.supabaseUrl && cfg.supabaseAnonKey) {
          await submitToSupabase(form, cfg);
        } else if (form.dataset.endpoint) {
          const res = await fetch(form.dataset.endpoint, { method: 'POST', body: new FormData(form) });
          if (!res.ok) throw new Error(res.status);
        } else {
          await new Promise(r => setTimeout(r, 900));   /* demo mode: no backend configured */
        }
        track('rfq_submit', { stages: [...form.querySelectorAll('[name=stage]:checked')].map(i => i.value).join(',') });
        form.hidden = true;
        const ok = document.querySelector('[data-success]');
        ok.classList.add('is-shown'); ok.setAttribute('tabindex', '-1'); ok.focus();
      } catch (err) {
        btn.removeAttribute('aria-busy');
        const msg = form.querySelector('[data-neterr]'); msg.hidden = false;
      }
    });
  }
})();
