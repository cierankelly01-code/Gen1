/* Genex UK — real-time 3D progressive die (interim hero until real footage lands).
   A coil strip indexes one pitch per press stroke. Every station works on every stroke:
   OP10 pilot & pierce · OP20 notch · OP30 form · OP40 nut insert · OP50 cut-off → part drops to the tote (OP60).
   Loaded lazily by site.js; if WebGL or this module fails, the SVG strip stays in place. */
import * as THREE from '../vendor/three.module.min.js';
import { RoomEnvironment } from '../vendor/RoomEnvironment.js';

const P = 1.4;            // strip pitch
const T = 0.06;           // material thickness
const STATIONS = [-2.8, -1.4, 0, 1.4, 2.8];   // OP10..OP50 x-positions
const TOTE_X = 4.75;
const STROKE = { down: 0.34, dwell: 0.10, up: 0.32, index: 0.42 };
const CYCLE = STROKE.down + STROKE.dwell + STROKE.up + STROKE.index;
const RAM_TRAVEL = 0.42;
const ease = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;

export function start(figure, hooks = {}) {
  const stage = figure.querySelector('.press__stage');
  const fill = !!hooks.fill;   // full-bleed hero background mode
  const canvas = document.createElement('canvas');
  canvas.className = 'press__canvas';
  canvas.setAttribute('aria-hidden', 'true');

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, powerPreference: 'high-performance' });
  } catch (e) { return null; }
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 1.75));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  const scene = new THREE.Scene();
  const BG = fill ? '#0A1C33' : '#14171B';
  scene.background = new THREE.Color(BG);
  scene.fog = new THREE.Fog(BG, fill ? 22 : 13, fill ? 42 : 22);
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(renderer), 0.04).texture;

  const camera = new THREE.PerspectiveCamera(28, 16 / 9, 0.1, 60);
  const camBase = fill ? new THREE.Vector3(2.4, 9.6, 17.5) : new THREE.Vector3(0.6, 8.6, 9.2);
  const look = fill ? new THREE.Vector3(-3.7, -0.6, 0) : new THREE.Vector3(1.25, -0.6, 0.1);
  const lookTarget = look.clone();

  // ---- lights
  scene.add(new THREE.HemisphereLight('#dfe6ee', '#1a1d21', 0.55));
  const key = new THREE.DirectionalLight('#ffffff', 2.1);
  key.position.set(-2, 9, 4);
  key.castShadow = true;
  key.shadow.mapSize.set(1024, 1024);
  Object.assign(key.shadow.camera, { left: -7, right: 7, top: 4, bottom: -4, near: 1, far: 20 });
  key.shadow.bias = -0.0004;
  scene.add(key);
  const rim = new THREE.DirectionalLight('#7FA8E0', 1.1);
  rim.position.set(5, 3, -6);
  scene.add(rim);

  // ---- materials
  const M = {
    strip: new THREE.MeshStandardMaterial({ color: '#aeb6bf', metalness: 0.9, roughness: 0.36 }),
    part: new THREE.MeshStandardMaterial({ color: '#eef2f5', metalness: 0.96, roughness: 0.18 }),
    die: new THREE.MeshStandardMaterial({ color: '#3a414a', metalness: 0.7, roughness: 0.45 }),
    dieDark: new THREE.MeshStandardMaterial({ color: '#1e2227', metalness: 0.5, roughness: 0.6 }),
    punch: new THREE.MeshStandardMaterial({ color: '#8f99a3', metalness: 0.9, roughness: 0.35 }),
    hole: new THREE.MeshBasicMaterial({ color: '#0a0c0e' }),
    nut: new THREE.MeshStandardMaterial({ color: '#c7b27a', metalness: 0.95, roughness: 0.28 }),
    hot: new THREE.MeshBasicMaterial({ color: '#FF6A63' }),
    tote: new THREE.MeshStandardMaterial({ color: '#2a3a52', metalness: 0.2, roughness: 0.7 }),
  };
  if (fill) {   // hero: moodier, more realistic steel
    M.die.color.set('#232b35'); M.die.metalness = 0.85; M.die.roughness = 0.32;
    M.dieDark.color.set('#161c24'); M.dieDark.metalness = 0.7; M.dieDark.roughness = 0.4;
    M.strip.color.set('#c9d1db'); M.strip.metalness = 1; M.strip.roughness = 0.22;
    M.part.color.set('#eef3f8'); M.part.metalness = 1; M.part.roughness = 0.16;
    M.punch.color.set('#a9b4c0'); M.punch.metalness = 1; M.punch.roughness = 0.25;
    renderer.toneMappingExposure = 1.2;
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(60, 40), new THREE.MeshStandardMaterial({ color: '#0b1a2e', metalness: 0.3, roughness: 0.8 }));
    floor.rotation.x = -Math.PI / 2; floor.position.y = -1.05; floor.receiveShadow = true; scene.add(floor);
  }
  const box = (w, h, d, m) => { const g = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m); g.castShadow = true; g.receiveShadow = true; return g; };

  // ---- die set
  const lower = box(7.6, 0.5, 2.6, M.die); lower.position.set(0, -0.25 - T / 2, 0); scene.add(lower);
  const bolster = box(9.4, 0.5, 3.4, M.dieDark); bolster.position.set(0.4, -0.75 - T / 2, 0); scene.add(bolster);
  const ram = new THREE.Group(); scene.add(ram);
  const upper = box(7.6, 0.4, 1.4, M.die); upper.position.set(0, 2.15, -0.5); ram.add(upper);
  const upperPlate = box(8.2, 0.22, 1.8, M.dieDark); upperPlate.position.set(0, 2.46, -0.5); ram.add(upperPlate);
  STATIONS.forEach((x, i) => {
    // slim punches set to the back of each station so the parts stay in view
    [-0.18, 0.18].forEach(dx => { const punch = box(0.16, 1.5, 0.22, M.punch); punch.position.set(x + dx, 1.2, -0.42); ram.add(punch); });
  });
  [-3.5, 3.5].forEach(x => [-1.05, 1.05].forEach(z => {
    const pin = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 2.6, 16), M.punch);
    pin.position.set(x, 1.0, z); pin.castShadow = true; scene.add(pin);
  }));
  // station highlight bars (focus indicator) on the lower die front face
  const hot = STATIONS.concat([TOTE_X]).map(x => {
    const b = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.04, 0.02), M.hot);
    b.position.set(x, -0.08, 1.32); b.visible = false; scene.add(b); return b;
  });
  hot[5].position.set(TOTE_X, -0.95, 0.95);

  // tote
  const tote = new THREE.Group(); tote.position.set(TOTE_X, -1.6, 0); scene.add(tote);
  const toteBase = box(1.5, 0.08, 1.7, M.tote); tote.add(toteBase);
  [[0, 0.3, 0.85, 1.5, 0.6, 0.06], [0, 0.3, -0.85, 1.5, 0.6, 0.06], [0.75, 0.3, 0, 0.06, 0.6, 1.7], [-0.75, 0.3, 0, 0.06, 0.6, 1.7]]
    .forEach(([x, y, z, w, h, d]) => { const s = box(w, h, d, M.tote); s.position.set(x, y, z); tote.add(s); });
  const chute = box(1.2, 0.04, 1.3, M.punch); chute.position.set(3.9, -0.62, 0); chute.rotation.z = -0.55; scene.add(chute);

  // ---- strip slots
  const geo = {
    rail: new THREE.BoxGeometry(P + 0.002, T, 0.2),
    web: new THREE.BoxGeometry(P - 0.002, T, 1.2),
    centre: new THREE.BoxGeometry(0.6, T, 1.1),
    flange: new THREE.BoxGeometry(0.22, T, 1.1),
    tab: new THREE.BoxGeometry(0.16, T, 0.1),
    pilot: new THREE.CylinderGeometry(0.06, 0.06, T + 0.004, 18),
    hole: new THREE.CylinderGeometry(0.075, 0.075, T + 0.004, 20),
    nut: new THREE.CylinderGeometry(0.11, 0.11, 0.1, 6),
  };
  const mesh = (g, m) => { const o = new THREE.Mesh(g, m); o.castShadow = true; o.receiveShadow = true; return o; };

  function makeSlot(s) {
    const g = new THREE.Group();
    const carrier = new THREE.Group(); g.add(carrier);
    [-0.7, 0.7].forEach(z => {
      const r = mesh(geo.rail, M.strip); r.position.z = z; carrier.add(r);
      const p = mesh(geo.pilot, M.hole); p.position.set(0, 0, z); carrier.add(p);
    });
    const web = mesh(geo.web, M.strip); carrier.add(web);
    const part = new THREE.Group(); g.add(part); part.visible = false;
    const centre = mesh(geo.centre, M.part); part.add(centre);
    const fl = [-1, 1].map(side => {
      const hinge = new THREE.Group(); hinge.position.x = side * 0.3; part.add(hinge);
      const f = mesh(geo.flange, M.part); f.position.x = side * 0.11; hinge.add(f);
      return { hinge, side };
    });
    const holes = [[0, -0.3], [0, 0.3]].map(([x, z]) => { const h = mesh(geo.hole, M.hole); h.position.set(x, 0, z); h.visible = false; return h; });
    holes.forEach(h => g.add(h));
    const tabs = [-0.6, 0.6].map(z => { const t = mesh(geo.tab, M.part); t.position.z = z; t.visible = false; carrier.add(t); return t; });
    const nut = mesh(geo.nut, M.nut); nut.position.y = T / 2 + 0.05; nut.visible = false; part.add(nut);
    scene.add(g);
    return { g, carrier, web, part, holes, fl, tabs, nut, s, ops: 0, bend: 0 };
  }
  const slots = [];
  for (let s = -4; s <= 4; s++) slots.push(makeSlot(s));
  const slotX = (s, shift) => STATIONS[0] + (s + shift) * P;

  // apply the operation of station k (0..4) to the slot sitting under it
  const falling = [];
  function applyOp(slot, k) {
    if (slot.ops !== k) return;           // a slot under station k has already had k operations
    slot.ops = k + 1;
    if (k === 0) slot.holes.forEach(h => h.visible = true);
    if (k === 1) {                        // notch: web becomes part + carrier tabs; holes now belong to the part
      slot.web.visible = false; slot.part.visible = true; slot.tabs.forEach(t => t.visible = true);
      slot.holes.forEach(h => slot.part.add(h));
    }
    if (k === 2) slot.bend = 1;
    if (k === 3) slot.nut.visible = true;
    if (k === 4) {                        // cut-off: part leaves the carrier and drops down the chute
      slot.tabs.forEach(t => t.visible = false);
      const part = slot.part, x0 = slot.g.position.x;
      slot.g.remove(part); scene.add(part); part.position.set(x0, 0, 0);
      falling.push({ part, x0, t: 0 });
    }
  }
  // pre-roll so the strip starts full
  slots.forEach(sl => { for (let k = 0; k < sl.s && k < 4; k++) applyOp(sl, k); });
  // empty carrier skeleton already past the cut-off station
  for (let s = 5; s <= 7; s++) { const sk = makeSlot(s); sk.web.visible = false; sk.part.visible = false; sk.ops = 5; slots.push(sk); }

  const pile = [];
  function landInTote(part) {
    scene.remove(part);
    part.position.set((Math.random() - 0.5) * 0.9, 0.12 + pile.length * 0.03, (Math.random() - 0.5) * 1.0);
    part.rotation.set((Math.random() - 0.5) * 0.4, Math.random() * Math.PI, (Math.random() - 0.5) * 0.4);
    tote.add(part); pile.push(part);
    if (pile.length > 14) { tote.remove(pile.shift()); pile.forEach((q, i) => q.position.y = 0.12 + i * 0.03); }
  }

  // ---- loop state
  let t0 = performance.now(), clock = 0, cycleStart = 0, running = true, visible = true, raf = 0;
  let stroked = false, focus = 0, autoFocus = true, focusHold = 0, strokes = 0;
  const mouse = { x: 0, y: 0, tx: 0, ty: 0 };

  function setFocus(i, user) {
    focus = i;
    hot.forEach((b, j) => b.visible = !fill && j === i);
    if (!fill) lookTarget.set(i < 5 ? STATIONS[i] * 0.2 + 1.25 : 2.2, -0.6, 0.1);
    if (user) { autoFocus = false; focusHold = clock + 9; }
    hooks.onFocus && hooks.onFocus(i);
  }
  if (fill) lookTarget.copy(look);
  setFocus(0);

  function resize() {
    const w = stage.clientWidth, h = fill ? stage.clientHeight : Math.round(w * 0.5);
    renderer.setSize(w, h, false);
    canvas.style.height = fill ? '100%' : h + 'px';
    camera.aspect = w / h;
    camera.fov = w < 520 ? 38 : 30;
    camera.updateProjectionMatrix();
  }

  function frame(now) {
    raf = 0;
    if (!running || !visible) return;
    const dt = Math.min(0.05, (now - t0) / 1000); t0 = now; clock += dt;
    let ph = clock - cycleStart;
    if (ph >= CYCLE) {
      cycleStart = clock; ph = 0; stroked = false;
      slots.forEach(sl => { sl.s += 1; });
      // retire carrier skeleton far right, feed a new blank in at the left
      for (let i = slots.length - 1; i >= 0; i--) if (slots[i].s > 7) { scene.remove(slots[i].g); slots.splice(i, 1); }
      const minS = Math.min(...slots.map(s => s.s));
      if (minS > -4) slots.push(makeSlot(minS - 1));
      if (autoFocus || clock > focusHold) { autoFocus = true; setFocus((focus + 1) % 6); }
    }
    // ram motion
    let ramY, shift = 0;
    if (ph < STROKE.down) ramY = -RAM_TRAVEL * ease(ph / STROKE.down);
    else if (ph < STROKE.down + STROKE.dwell) ramY = -RAM_TRAVEL;
    else if (ph < STROKE.down + STROKE.dwell + STROKE.up) ramY = -RAM_TRAVEL * (1 - ease((ph - STROKE.down - STROKE.dwell) / STROKE.up));
    else { ramY = 0; shift = ease((ph - STROKE.down - STROKE.dwell - STROKE.up) / STROKE.index); }
    ram.position.y = ramY;
    if (!stroked && ph >= STROKE.down) {
      stroked = true; strokes++;
      slots.forEach(sl => { if (sl.s >= 0 && sl.s <= 4) applyOp(sl, sl.s); });
      hooks.onStroke && hooks.onStroke(strokes);
    }
    // slots ride the strip
    for (const sl of slots) {
      sl.g.position.x = slotX(sl.s, shift);
      if (sl.s === 2 && sl.ops === 2 && ph < STROKE.down) sl.bend = ease(ph / STROKE.down);   // forming as the ram closes
      sl.fl.forEach(({ hinge, side }) => hinge.rotation.z = side * sl.bend * (Math.PI / 2));
      sl.g.visible = sl.g.position.x < 7.4 && sl.g.position.x > -9.5;
    }
    // cut-off parts fall to the tote
    for (let i = falling.length - 1; i >= 0; i--) {
      const f = falling[i];
      f.t += dt;
      const k = Math.min(1, f.t / 0.75);
      f.part.position.set(f.x0 + ease(k) * (TOTE_X - f.x0), -k * k * 1.45, 0);
      f.part.rotation.set(0, k * 0.9, -k * 1.1);
      if (k >= 1) { falling.splice(i, 1); landInTote(f.part); }
    }
    // camera: slow drift + pointer parallax + focus pan
    mouse.x += (mouse.tx - mouse.x) * 0.05; mouse.y += (mouse.ty - mouse.y) * 0.05;
    look.lerp(lookTarget, 0.04);
    camera.position.set(camBase.x + mouse.x * 1.2 + Math.sin(clock * 0.15) * 0.3, camBase.y - mouse.y * 0.6, camBase.z);
    camera.lookAt(look);
    renderer.render(scene, camera);
    raf = requestAnimationFrame(frame);
  }
  const kick = () => { if (!raf && running && visible) { t0 = performance.now(); raf = requestAnimationFrame(frame); } };

  stage.prepend(canvas);
  resize();
  addEventListener('resize', resize);
  if (matchMedia('(hover: hover)').matches) {
    figure.addEventListener('pointermove', e => {
      const r = figure.getBoundingClientRect();
      mouse.tx = (e.clientX - r.left) / r.width - 0.5; mouse.ty = (e.clientY - r.top) / r.height - 0.5;
    });
    figure.addEventListener('pointerleave', () => { mouse.tx = 0; mouse.ty = 0; });
  }
  new IntersectionObserver(es => { visible = es[0].isIntersecting; kick(); }, { threshold: 0.05 }).observe(figure);
  document.addEventListener('visibilitychange', () => { visible = !document.hidden; kick(); });
  // render one frame, then reveal (crossfade from the SVG)
  renderer.render(scene, camera);
  requestAnimationFrame(() => figure.classList.add(fill ? 'is-3d' : 'press--3d'));
  kick();

  return {
    focus: i => setFocus(i, true),
    pause() { running = false; },
    resume() { running = true; kick(); },
  };
}
