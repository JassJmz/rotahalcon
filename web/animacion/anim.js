// RotaHawk pitch animation – 11 scenes (HTML + SVG + GSAP)
// Controls: click / → / Space = next · ← = back · F = fullscreen · Home = restart
// ?autoplay=1        advances by itself (screen-record the 1080p MP4 backup)
// ?short=1            ~30 s version: soil, cloud, calibration, every rotation, worst year, assistant (no closing logo). Plays by itself (add &autoplay=0 to click through).
//                     With short=1, start/end are positions 0-5 inside that sequence (the slides play 0..5).
// ?start=N&end=M      plays only scenes N..M; going past the ends tells the parent page (slide deck) to move on
// ?delay=1500          waits that many ms before the first scene (record.mjs uses it)
// ?scene=N&t=SECONDS freezes scene N (0-10) at time t: for slide stills and frame-by-frame review
'use strict';

// ── DATOS ──  Act 2 is driven by data.js: real engine output (POST /recomendar) + NASA POWER annual rainfall.
// Regenerate it with:  python build_data.py   (never edit numbers here by hand).
// Sensor reading and calibration are still mock until the AGRISENSE node is live; those scenes say so on screen.
const D = window.ROTA_DATA;
const ICON = { frijol: '🫘', maiz: '🌽', avena: '🌾', sorgo: '🌱', alfalfa: '🌿' };
const NAME = { frijol: 'beans', maiz: 'maize', avena: 'oats', sorgo: 'sorghum', alfalfa: 'alfalfa' };
const SEM = { verde: '#22c55e', amarillo: '#eab308', rojo: '#ef4444' };
const ROWS = [...D.estrategias].sort((a, b) => b.es_actual - a.es_actual);      // current rotation first
const Y0 = D.years[0], YEARS = D.years.length;
const FAILS = ROWS.map(e => e.fails.length);                                    // failed seasons per rotation
const ROW_LABELS = ROWS.map((e, i) => e.es_actual ? 'Current' : 'Alt ' + i);
const ROW_CROPS = ROWS.map(e => e.ciclos.map(c => ICON[c] || '🌱').join(''));
const rainPct = (m => { const x = /rain ([+-]?\d+)% vs normal/.exec(m || ''); return x ? +x[1] : null; })(ROWS[0].peor_anio.motivo);
const WORST_YEAR = { year: ROWS[0].peor_anio.anio, why: rainPct === null ? 'the hardest season on record' : `rainfall ${Math.abs(rainPct)}% ${rainPct < 0 ? 'below' : 'above'} normal` };
// Role 1: the sensor must be shown as measuring moisture, and calibrated against NASA, ONLY after they verify it. Until then
// scene 5 stays on demo values even if a real reading arrives. Set to true when Role 1 confirms.
const CALIB_CONFIRMED = false;
const SENSOR_MOCK = !D.sensor || !!D.sensor.mock;
const CALIB_LIVE = CALIB_CONFIRMED && !SENSOR_MOCK && D.calibracion_datos === 'sensor';
const SAT_PCT = D.calibracion.satelite_pct, SENSOR_PCT = CALIB_CONFIRMED ? D.sensor.humedad_pct : D.calibracion.sensor_pct, ADJUST = D.calibracion.ajuste;
const RAIN = D.rain_mm;                                                         // mm per year, NASA POWER PRECTOTCORR
const DURATIONS = [3, 6, 4, 4, 8, 6, 10, 6, 5, 6, 3];   // seconds per scene (storyboard C2), used by ?autoplay=1
// ── FIN DATOS ──

const NS = 'http://www.w3.org/2000/svg';
const C = { navy: '#0B1F3A', navy2: '#102a4c', navy3: '#1b3a66', gold: '#D4AF37', goldL: '#f1d27a', green: '#22c55e', yellow: '#eab308', red: '#ef4444', blue: '#3b82f6', blueL: '#93c5fd', white: '#e8eef7', mute: '#94a3b8' };
const E = { out: 'expo.out', out3: 'power3.out', in: 'power2.in', io: 'power3.inOut', sine: 'sine.inOut', pop: 'back.out(1.5)' };
const REDUCE = matchMedia('(prefers-reduced-motion: reduce)').matches;
const LOOP = REDUCE ? 0 : -1;                       // ambient loops are off under reduced motion
const Q = new URLSearchParams(location.search);
const stage = document.getElementById('stage');

// ── IDIOMA ──  ?lang=es shows the whole animation in Spanish. English is the default (international page).
const LANG = Q.get('lang') === 'es' ? 'es' : 'en';
const ES = {
  'ACT 1 · FROM SOIL TO CLOUD': 'ACTO 1 · DEL SUELO A LA NUBE', 'ACT 2 · ROTAHAWK': 'ACTO 2 · ROTAHAWK', 'ROTAHAWK': 'ROTAHAWK',
  'A field in Durango': 'Un campo en Durango', 'NPK soil sensor · indicative reading': 'Sensor de suelo NPK · lectura indicativa',
  'Read every 60 s': 'Lectura cada 60 s', 'Live, from this field': 'En vivo, desde este campo',
  'Satellite sees km. We see your field.': 'El satélite ve kilómetros. Nosotros vemos tu campo.',
  'Every rotation, every year': 'Cada rotación, cada año', 'The worst year, not the average': 'El peor año, no el promedio',
  'Your priorities, your ranking': 'Tus prioridades, tu ranking', 'Explained. Sourced. In your pocket.': 'Explicado. Con fuentes. En tu bolsillo.',
  'Smart Crop Rotation for Climate Resilience': 'Rotación inteligente de cultivos para la resiliencia climática',
  'Team Halcones Dorados · ITSRLL · NASA Space Apps 2026': 'Equipo Halcones Dorados · ITSRLL · NASA Space Apps 2026',
  'EC': 'CE', 'NPK probes': 'Sondas NPK', 'in the soil': 'en el suelo', 'Calibrated': 'Calibrado',
  'ONE SATELLITE PIXEL ≈ SEVERAL KM': 'UN PÍXEL DE SATÉLITE ≈ VARIOS KM', 'NASA POWER · rainfall per year': 'NASA POWER · lluvia por año', 'rainfall': 'lluvia',
  'NASA POWER · PRECTOTCORR annual sum · Durango': 'NASA POWER · PRECTOTCORR suma anual · Durango',
  'Engine output: FAO water and frost rules on NASA POWER data': 'Resultado del motor: reglas FAO de agua y helada sobre datos NASA POWER',
  'Engine output on NASA POWER data': 'Resultado del motor sobre datos NASA POWER', 'Engine output for both sets of priorities': 'Resultado del motor para ambas prioridades',
  'Numbers from the engine; wording illustrative': 'Números del motor; redacción ilustrativa',
  'Demo sensor and calibration values': 'Valores de ejemplo del sensor y la calibración', 'Live sensor readings': 'Lecturas del sensor en vivo',
  'Reading received': 'Lectura recibida', 'Current': 'Actual', 'Water': 'Agua', 'Soil': 'Suelo', 'Income*': 'Ingreso*', 'Risk': 'Riesgo',
  '* Income: no sourced seed cost or crop price yet (information gap)': '* Ingreso: aún no hay costo de semilla ni precio con fuente (hueco de información)',
  'EXAMPLE · NEXT MODULE': 'EJEMPLO · PRÓXIMO MÓDULO', 'EXAMPLE DATA': 'DATOS DE EJEMPLO', 'LIVE': 'EN VIVO', 'SAFER': 'MÁS SEGURA', 'RISKIER': 'MÁS RIESGOSA', 'SAME RISK': 'MISMO RIESGO',
  'RotaHawk report': 'Reporte RotaHawk', 'Decision support only': 'Solo apoyo a la decisión',
  'Every answer cites its source, and says when one is missing.': 'Cada respuesta cita su fuente y dice cuándo falta una.',
  'the hardest season on record': 'la temporada más difícil del registro',
};
const ES_CROP = { beans: 'frijol', corn: 'maíz', maize: 'maíz', oats: 'avena', sorghum: 'sorgo', alfalfa: 'alfalfa' }, ES_LIGHT = { red: 'roja', yellow: 'amarilla', green: 'verde' };
const ES_RULES = [   // dynamic sentences: [pattern, replacement]
  [/^(\d+) years of real NASA climate$/, '$1 años de clima real de la NASA'], [/^Moisture ([\d.]+)%$/, 'Humedad $1%'],
  [/^\+(\d+) pts adjustment$/, '+$1 pts de ajuste'], [/^Worst year (\d+)$/, 'Peor año $1'],
  [/^rainfall (\d+)% (below|above) normal$/, (m, n, d) => 'lluvia ' + n + '% ' + (d === 'below' ? 'por debajo' : 'por encima') + ' de lo normal'],
  [/^Why is my current rotation (\w+)\?$/, (m, c) => '¿Por qué mi rotación actual está en ' + (ES_LIGHT[c] === 'roja' ? 'rojo' : ES_LIGHT[c] === 'verde' ? 'verde' : 'amarillo') + '?'],
  [/^It would have failed (\d+) of (\d+) seasons:$/, 'Habría fallado $1 de $2 temporadas:'], [/^(\d+) by drought, (\d+) by frost\.$/, '$1 por sequía, $2 por helada.'],
  [/^Works in (\d+) of (\d+) years$/, 'Funciona en $1 de $2 años'], [/^Alt (\d+)$/, 'Alt $1'],
  [/^Alt (\d+) \((\w+) first\)$/, (m, n, c) => 'Alt ' + n + ' (' + (ES_CROP[c] || c) + ' primero)'],
  [/^(✗|✓)  (.+): (crop failed|held)$/, (m, i, w, r) => i + '  ' + T(w) + ': ' + (r === 'held' ? 'aguantó' : 'el cultivo falló')],
  [/^Current rotation$/, 'Rotación actual'],
  [/^(.+) fails (\d+) of (\d+) seasons\. Yours fails (\d+)\.$/, (m, w, a, y, b) => T(w) + ' falla ' + a + ' de ' + y + ' temporadas. La tuya falla ' + b + '.'],
  [/^No alternative is safer in a drought here: the best also fails (\d+) of (\d+), and (\w+) first fails (\d+)\.$/, (m, a, y, c, b) => 'Ninguna alternativa es más segura en sequía aquí: la mejor también falla ' + a + ' de ' + y + ', y ' + (ES_CROP[c] || c) + ' primero falla ' + b + '.'],
  [/^Every alternative is riskier here: (\w+) first fails (\d+) of (\d+)\. Yours fails (\d+)\.$/, (m, c, a, y, b) => 'Todas las alternativas son más riesgosas aquí: ' + (ES_CROP[c] || c) + ' primero falla ' + a + ' de ' + y + '. La tuya falla ' + b + '.'],
];
function T(str) {
  if (LANG !== 'es' || typeof str !== 'string') return str;
  if (ES[str] !== undefined) return ES[str];
  for (const [re, to] of ES_RULES) if (re.test(str)) return str.replace(re, to);
  return str;
}
// ── FIN IDIOMA ──

/* ---------- helpers ---------- */
function el(tag, attrs, parent) {
  const e = document.createElementNS(NS, tag);
  for (const k in (attrs || {})) e.setAttribute(k, attrs[k]);
  (parent || stage).appendChild(e); return e;
}
function txt(parent, x, y, s, size, fill, anchor, weight, extra) {
  const t = el('text', Object.assign({ x, y, 'font-size': size || 28, fill: fill || C.white, 'text-anchor': anchor || 'middle', 'font-weight': weight || 600, style: 'font-variant-numeric:tabular-nums' }, extra || {}), parent);
  t.textContent = T(s); return t;
}
function grp(parent, x, y) { const g = el('g', {}, parent); gsap.set(g, { x: x || 0, y: y || 0 }); return g; }
function rng(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function chip(parent, x, y, label, bg, fg, size) {
  label = T(label); size = size || 22; const w = label.length * size * .62 + 28, g = grp(parent, x, y);
  el('rect', { x: -w / 2, y: -size, width: w, height: size * 2, rx: size * .55, fill: bg }, g);
  txt(g, 0, size * .36, label, size, fg, 'middle', 800); return g;
}
function countTo(obj, key, to, node, fmt, dur, ease, tl, at) {
  tl.to(obj, { [key]: to, duration: dur, ease: ease || E.out3, onUpdate: () => node.textContent = fmt(obj[key]) }, at);
}
function burst(parent, x, y, n, col, dist, tl, at) {     // radial particle burst
  const r = rng(x + y);
  for (let i = 0; i < n; i++) {
    const a = i / n * Math.PI * 2 + r() * .4, d = dist * (.6 + r() * .6);
    const p = el('circle', { cx: x, cy: y, r: 3 + r() * 3, fill: col, opacity: 0 }, parent);
    tl.fromTo(p, { opacity: 1 }, { opacity: 0, x: Math.cos(a) * d, y: Math.sin(a) * d, duration: .8 + r() * .3, ease: E.out3, immediateRender: false }, at);
  }
}

/* ---------- data shared by scenes 6, 7 and 8 (so the same years line up across them) ---------- */
const WI = WORST_YEAR.year - Y0;                         // column of the worst year
const ALTS = ROWS.map((_, i) => i).filter(i => !ROWS[i].es_actual);
const BEST = ALTS.reduce((a, b) => FAILS[b] < FAILS[a] || (FAILS[b] === FAILS[a] && ROWS[b].puntaje > ROWS[a].puntaje) ? b : a);   // most resilient alternative
const RISKY = ALTS.reduce((a, b) => FAILS[b] > FAILS[a] ? b : a);                 // least resilient alternative
const SAFER = FAILS[BEST] < FAILS[0];                    // does any alternative fail in fewer seasons than the current rotation?
const RAINH = (() => { const m = Math.max(...RAIN); return RAIN.map(v => v / m); })();   // rainfall per year, normalised 0..1
const FAILSETS = ROWS.map(e => new Set(e.fails.map(y => y - Y0)));                // failed columns per row
const GRID = { x0: 380, cw: 860 / YEARS, h: 92, y: r => 120 + r * 130 };
function gridRow(g, r, final) {                          // one rotation row: label, crops, counter and one cell per year
  const rg = grp(g, 0, GRID.y(r));
  const lab = txt(rg, 44, 34, ROW_LABELS[r], 28, r === 0 ? C.gold : C.white, 'start', 800), crops = txt(rg, 44, 72, ROW_CROPS[r], 28, C.white, 'start', 500);
  const cnt = txt(rg, 350, 54, (final ? FAILS[r] : 0) + ' / ' + YEARS, 24, final && r === 0 ? C.red : C.mute, 'end', 700), cells = [];
  for (let i = 0; i < YEARS; i++) { const bad = FAILSETS[r].has(i);
    cells.push({ c: el('rect', { x: GRID.x0 + i * GRID.cw + 1, y: 0, width: GRID.cw - 2, height: GRID.h, rx: 3, fill: final && bad ? C.red : C.green, opacity: final ? (bad ? 1 : .4) : 0 }, rg), bad, i }); }
  return { rg, lab, crops, cnt, cells };
}

/* ---------- static layers ---------- */
const defs = el('defs');
defs.innerHTML = `
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#07152b"/><stop offset=".55" stop-color="#27456f"/><stop offset="1" stop-color="#e8a05a"/></linearGradient>
  <linearGradient id="cloudG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4f8ff"/><stop offset="1" stop-color="#b9cbe6"/></linearGradient>
  <linearGradient id="soilG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6b4429"/><stop offset="1" stop-color="#2f1c0e"/></linearGradient>
  <radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".45"/></radialGradient>
  <pattern id="dots" width="40" height="40" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="#ffffff" opacity=".07"/></pattern>
  <filter id="glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>`;
el('rect', { width: 1280, height: 720, fill: C.navy });
el('rect', { width: 1280, height: 720, fill: 'url(#dots)' });
const host = el('g');            // scene layers are created inside this group, one per scene
const ambient = el('g', { opacity: .5, 'pointer-events': 'none' });
el('rect', { width: 1280, height: 720, fill: 'url(#vig)', 'pointer-events': 'none' });
const hud = el('g');
const tagTxt = txt(hud, 44, 56, '', 20, C.gold, 'start', 700, { 'letter-spacing': '2' });
const capTxt = txt(hud, 640, 668, '', 42, C.gold, 'middle', 700);
const capLine = el('rect', { x: 560, y: 694, width: 160, height: 3, rx: 1.5, fill: C.gold, opacity: 0 }, hud);
const noteTxt = txt(hud, 1236, 700, '', 14, C.mute, 'end', 500);
el('rect', { x: 0, y: 714, width: 1280, height: 6, fill: '#ffffff12' }, hud);
const progress = el('rect', { x: 0, y: 714, width: 0, height: 6, fill: C.gold }, hud);

if (!REDUCE) {        // ambient gold dust, very subtle, shared by every scene
  const r = rng(99);
  for (let i = 0; i < 24; i++) {
    const p = el('circle', { cx: r() * 1280, cy: 100 + r() * 560, r: 1.2 + r() * 2, fill: C.goldL, opacity: .25 + r() * .5 }, ambient);
    gsap.to(p, { y: -60 - r() * 120, x: (r() - .5) * 60, opacity: 0, duration: 6 + r() * 6, repeat: -1, delay: -r() * 8, ease: 'none' });
  }
}

/* ---------- scenes ---------- */
const SCENES = [];

// 1 ── A field in Durango (3 s)
SCENES.push({ act: 'ACT 1 · FROM SOIL TO CLOUD', cap: 'A field in Durango', build(g) {
  el('rect', { width: 1280, height: 720, fill: 'url(#sky)' }, g);
  const rr = rng(2), stars = [];
  for (let i = 0; i < 46; i++) stars.push(el('circle', { cx: rr() * 1280, cy: rr() * 280, r: .8 + rr() * 1.6, fill: '#fff', opacity: .35 + rr() * .6 }, g));
  const halo = el('circle', { cx: 900, cy: 600, r: 130, fill: '#ffd36b', opacity: .16 }, g);
  const sun = el('circle', { cx: 900, cy: 600, r: 66, fill: '#ffd36b', filter: 'url(#glow)' }, g);
  el('path', { d: 'M0 440 Q180 340 400 410 T800 390 T1280 420 V470 H0Z', fill: '#1b3d63' }, g);
  el('path', { d: 'M0 450 Q260 390 520 435 T1040 420 T1280 440 V480 H0Z', fill: '#1f5148' }, g);
  el('rect', { x: 0, y: 440, width: 1280, height: 280, fill: 'url(#soilG)' }, g);
  el('rect', { x: 0, y: 440, width: 1280, height: 12, fill: '#4c8f3f' }, g);
  [0, 1, 2, 3].forEach(i => el('rect', { x: 0, y: 520 + i * 55, width: 1280, height: 2, fill: '#00000030' }, g));
  const rs = rng(8), crops = [];
  for (let i = 0; i < 46; i++) { const x = rs() * 1280; if (Math.abs(x - 640) > 70) crops.push(el('path', { d: `M${x} 442 l-5 -24 M${x} 442 l5 -24 M${x} 442 v-28`, stroke: '#7ccf64', 'stroke-width': 3, 'stroke-linecap': 'round', fill: 'none' }, g)); }
  const n = grp(g, 640, -240);
  el('rect', { x: -52, y: -134, width: 104, height: 96, rx: 14, fill: C.navy2, stroke: C.gold, 'stroke-width': 4 }, n);
  el('rect', { x: -40, y: -122, width: 80, height: 26, rx: 6, fill: '#0b1a30' }, n);
  txt(n, 0, -103, 'ROTAHAWK', 15, C.gold, 'middle', 800);
  const led = el('circle', { cx: 34, cy: -62, r: 6, fill: C.green }, n);
  el('rect', { x: -26, y: -38, width: 10, height: 108, rx: 3, fill: C.goldL }, n); el('rect', { x: 16, y: -38, width: 10, height: 108, rx: 3, fill: C.goldL }, n);
  const tl = gsap.timeline();
  tl.to(stars, { opacity: 0, duration: 2.6, stagger: .02, ease: 'none' }, 0)
    .to([sun, halo], { attr: { cy: 380 }, duration: 3, ease: 'power2.out' }, 0)
    .to(crops, { y: -4, duration: .6, stagger: .02, ease: E.out3 }, .4)
    .to(n, { y: 362, duration: .8, ease: 'power2.in' }, .2)            // gravity fall: the one place ease-in is physical
    .to(n, { y: 402, duration: .55, ease: E.out3 }, 1.0)                // probes push into the soil
    .to(led, { opacity: .2, duration: .25, repeat: LOOP ? 7 : 1, yoyo: true, ease: E.sine }, 1.5);
  gsap.to(halo, { attr: { r: 160 }, opacity: .07, duration: 2, repeat: LOOP, yoyo: true, ease: E.sine });
  burst(g, 640, 440, 12, '#c9a37a', 90, tl, 1.0);
  return tl;
} });

// 2 ── Inside the soil (6 s)
SCENES.push({ act: 'ACT 1 · FROM SOIL TO CLOUD', cap: 'NPK soil sensor · indicative reading', build(g) {
  el('rect', { width: 1280, height: 720, fill: '#34210f' }, g);
  const z = el('g', {}, g), r = rng(3), grains = [];
  for (let i = 0; i < 64; i++) {
    const cx = r() * 1280, cy = 90 + r() * 520, rad = 14 + r() * 24, gg = el('g', { opacity: 0 }, z);
    el('circle', { cx, cy, r: rad, fill: ['#5a3a22', '#6b4429', '#47301c'][i % 3] }, gg);
    el('circle', { cx: cx - rad * .3, cy: cy - rad * .3, r: rad * .35, fill: '#ffffff', opacity: .07 }, gg); grains.push(gg);
  }
  const drops = []; for (let i = 0; i < 16; i++) drops.push(el('ellipse', { cx: r() * 1280, cy: 110 + r() * 480, rx: 7, ry: 10, fill: C.blue, opacity: 0 }, z));
  const ionEls = [], ions = [['N', '#4ade80'], ['P', '#f59e0b'], ['K', '#c084fc']];
  ions.forEach(([l, col]) => { for (let i = 0; i < 5; i++) { const gi = grp(z, 160 + r() * 960, 130 + r() * 430); gi.setAttribute('opacity', 0); el('circle', { r: 15, fill: col }, gi); txt(gi, 0, 6, l, 17, C.navy, 'middle', 800); ionEls.push(gi); } });
  [560, 720].forEach(x => { el('rect', { x: x - 7, y: 40, width: 14, height: 600, rx: 7, fill: C.goldL, filter: 'url(#glow)' }, z); });
  const pulses = [0, 1, 2].map(() => el('circle', { cx: 640, cy: 340, r: 10, fill: 'none', stroke: C.gold, 'stroke-width': 4, opacity: 0 }, z));
  const labels = ['N', 'P', 'K'], chips = labels.map((l, i) => { const c = chip(g, 640 + (i - 1) * 120, 110, l, '#ffffff14', C.white, 22); c.setAttribute('opacity', 0); return c; });
  const tl = gsap.timeline();
  tl.from(z, { scale: .45, svgOrigin: '640 340', duration: 1.5, ease: E.out }, 0)
    .to(grains, { opacity: 1, duration: .5, stagger: .01 }, 0)
    .to(drops, { opacity: .9, duration: .5, stagger: .03 }, .3)
    .to(ionEls, { opacity: 1, duration: .5, stagger: .04 }, .6)
    .to(chips, { opacity: 1, y: '+=0', duration: .4, stagger: .08, ease: E.out3 }, 1.2);
  chips.forEach((c, i) => tl.fromTo(c.children[0], { fill: '#ffffff14' }, { fill: C.gold, duration: .2, yoyo: true, repeat: 1 }, 2 + i * .45));
  ionEls.forEach(e => gsap.to(e, { x: '+=' + gsap.utils.random(-34, 34), y: '+=' + gsap.utils.random(-34, 34), duration: gsap.utils.random(1.3, 2.4), repeat: LOOP, yoyo: true, ease: E.sine }));
  pulses.forEach((p, i) => gsap.fromTo(p, { attr: { r: 10 }, opacity: .9 }, { attr: { r: 240 }, opacity: 0, duration: 1.8, repeat: LOOP, delay: 1.2 + i * .6, ease: 'power1.out' }));
  return tl;
} });

// 3 ── Probe → MAX485 → ESP32 (4 s)
SCENES.push({ act: 'ACT 1 · FROM SOIL TO CLOUD', cap: 'Read every 60 s', build(g) {
  const probe = grp(g, 140, 360);
  el('rect', { x: -22, y: -56, width: 10, height: 112, rx: 3, fill: C.goldL }, probe); el('rect', { x: 12, y: -56, width: 10, height: 112, rx: 3, fill: C.goldL }, probe);
  txt(probe, 0, 96, 'NPK probes', 20, C.white); txt(probe, 0, 120, 'in the soil', 16, C.mute, 'middle', 500);
  const cab1 = el('path', { d: 'M170 360 H470', stroke: C.gold, 'stroke-width': 5, fill: 'none', 'stroke-linecap': 'round', pathLength: 1, 'stroke-dasharray': 1, 'stroke-dashoffset': 1 }, g);
  const max = grp(g, 580, 360);
  el('rect', { x: -110, y: -64, width: 220, height: 128, rx: 14, fill: C.navy2, stroke: C.gold, 'stroke-width': 3 }, max);
  for (let i = 0; i < 6; i++) { el('rect', { x: -88 + i * 32, y: -76, width: 12, height: 12, fill: '#8aa0c2' }, max); el('rect', { x: -88 + i * 32, y: 64, width: 12, height: 12, fill: '#8aa0c2' }, max); }
  txt(max, 0, -4, 'MAX485', 32, C.gold, 'middle', 800); txt(max, 0, 30, 'RS485 · Modbus RTU', 18, C.white, 'middle', 500);
  const cab2 = el('path', { d: 'M690 360 H900', stroke: C.gold, 'stroke-width': 5, fill: 'none', 'stroke-linecap': 'round', pathLength: 1, 'stroke-dasharray': 1, 'stroke-dashoffset': 1 }, g);
  const esp = grp(g, 1020, 360);
  const board = el('rect', { x: -130, y: -84, width: 260, height: 168, rx: 14, fill: C.navy2, stroke: '#4b6a99', 'stroke-width': 3 }, esp);
  for (let i = 0; i < 7; i++) { el('rect', { x: -110 + i * 36, y: -96, width: 14, height: 12, fill: '#8aa0c2' }, esp); el('rect', { x: -110 + i * 36, y: 84, width: 14, height: 12, fill: '#8aa0c2' }, esp); }
  el('rect', { x: 60, y: -70, width: 56, height: 34, rx: 4, fill: 'none', stroke: '#4b6a99', 'stroke-width': 2 }, esp);
  txt(esp, 0, 14, 'ESP32', 42, C.white, 'middle', 800); txt(esp, 0, 52, 'UART → WiFi', 18, C.mute, 'middle', 600);
  const ring = el('circle', { cx: 1170, cy: 230, r: 34, fill: 'none', stroke: '#ffffff22', 'stroke-width': 6 }, g);
  const sweep = el('circle', { cx: 1170, cy: 230, r: 34, fill: 'none', stroke: C.gold, 'stroke-width': 6, 'stroke-linecap': 'round', pathLength: 1, 'stroke-dasharray': 1, 'stroke-dashoffset': 1, transform: 'rotate(-90 1170 230)' }, g);
  txt(g, 1170, 238, '60 s', 18, C.white, 'middle', 700);
  const pk = [0, 1, 2].map(() => el('circle', { cx: 170, cy: 360, r: 9, fill: C.goldL, filter: 'url(#glow)', opacity: 0 }, g));
  const tl = gsap.timeline();
  tl.from([probe, max, esp], { opacity: 0, y: '+=24', duration: .6, stagger: .12, ease: E.out3 }, 0)
    .to(cab1, { strokeDashoffset: 0, duration: .5, ease: E.io }, .4).to(cab2, { strokeDashoffset: 0, duration: .4, ease: E.io }, .7);
  pk.forEach((p, i) => { const t0 = 1 + i * .45; tl.set(p, { opacity: 1, attr: { cx: 170 } }, t0).to(p, { attr: { cx: 470 }, duration: .6, ease: 'none' }, t0).to(p, { attr: { cx: 690 }, duration: .35, ease: 'none' }, t0 + .6).to(p, { attr: { cx: 900 }, duration: .5, ease: 'none' }, t0 + .95).to(p, { opacity: 0, duration: .15 }, t0 + 1.45); });
  tl.fromTo(board, { attr: { stroke: '#4b6a99' } }, { attr: { stroke: C.gold }, duration: .4, yoyo: true, repeat: LOOP ? 3 : 1 }, 2.2)
    .to(sweep, { strokeDashoffset: 0, duration: 1.6, ease: 'none' }, 1.8);
  return tl;
} });

// 4 ── Wi-Fi → Firebase → SENSOR card (4 s)
SCENES.push({ act: 'ACT 1 · FROM SOIL TO CLOUD', cap: 'Live, from this field', note: SENSOR_MOCK ? 'Demo sensor reading' : '', build(g, from) {
  const d = from === 2 ? .6 : 0;     // coming from scene 3, the ESP32 travels here first
  const esp = grp(g, 170, 520);
  el('rect', { x: -90, y: -52, width: 180, height: 104, rx: 14, fill: C.navy2, stroke: C.gold, 'stroke-width': 3 }, esp); txt(esp, 0, 12, 'ESP32', 32, C.white, 'middle', 800);
  const arcs = [0, 1, 2].map(i => el('path', { d: `M${290 + i * 36} ${520 - 26 - i * 22} Q${330 + i * 44} 520 ${290 + i * 36} ${520 + 26 + i * 22}`, stroke: C.gold, 'stroke-width': 5, fill: 'none', 'stroke-linecap': 'round', opacity: 0 }, g));
  const cloud = grp(g, 800, 210);
  [[-70, 22, 56], [10, -24, 72], [92, 14, 56]].forEach(([x, y, rr]) => el('circle', { cx: x, cy: y, r: rr, fill: 'url(#cloudG)' }, cloud));
  el('rect', { x: -70, y: 14, width: 162, height: 64, rx: 20, fill: 'url(#cloudG)' }, cloud);
  txt(cloud, 10, 40, 'Firebase', 34, C.navy, 'middle', 800);
  const line = el('path', { d: 'M440 470 L690 290', stroke: C.gold, 'stroke-width': 3, 'stroke-dasharray': '8 10', fill: 'none', opacity: 0 }, g);
  const pk = [0, 1, 2].map(() => el('circle', { cx: 440, cy: 470, r: 7, fill: C.goldL, opacity: 0, filter: 'url(#glow)' }, g));
  const card = grp(g, 810, 420);      // 420 wide, centered at x=1020 (scene 5 keeps this card in place)
  el('rect', { width: 420, height: 140, rx: 18, fill: C.navy2, stroke: C.gold, 'stroke-width': 3 }, card);
  el('rect', { x: 20, y: 18, width: 96, height: 30, rx: 8, fill: C.gold }, card); txt(card, 68, 39, 'SENSOR', 17, C.navy, 'middle', 800);
  if (SENSOR_MOCK) { const lab = T('EXAMPLE DATA'), wl = lab.length * 15 * .62 + 28; chip(card, 128 + wl / 2, 33, 'EXAMPLE DATA', '#7c2d12', '#fed7aa', 15); }   // not a real reading yet: say so on the card
  const REAL = !SENSOR_MOCK && !CALIB_CONFIRMED;     // real reading, variable mapping not verified yet
  const val = txt(card, 28, 106, REAL ? 'Reading received' : 'Moisture 0.0%', 38, C.white, 'start', 800);
  if (!REAL) {                                   // never let the number spill out of the card, whatever the value or the language
    val.textContent = T('Moisture ' + Math.max(SENSOR_PCT, 100).toFixed(1) + '%');
    const wmax = val.getComputedTextLength();
    if (wmax > 364) val.setAttribute('font-size', (38 * 364 / wmax).toFixed(1));
    val.textContent = T('Moisture 0.0%');
  }
  if (REAL && D.sensor.ts) txt(card, 28, 130, new Date(D.sensor.ts * 1000).toISOString().slice(11, 16) + ' UTC', 18, C.mute, 'start', 600);
  const o = { v: 0 }, tl = gsap.timeline();
  tl.from(esp, from === 2 ? { x: 1020, y: 360, scale: 1.44, transformOrigin: '50% 50%', duration: .9, ease: E.io } : { opacity: 0, x: -30, duration: .5, ease: E.out3 }, 0)
    .to(arcs, { opacity: 1, duration: .3, stagger: .15 }, .3 + d)
    .to(line, { opacity: 1, duration: .3 }, .6 + d)
    .from(cloud, { opacity: 0, y: '+=30', scale: .9, svgOrigin: '800 210', duration: .7, ease: E.out }, .7)
    .from(card, { opacity: 0, y: '+=40', duration: .6, ease: E.out3 }, 1.9);
  pk.forEach((p, i) => tl.set(p, { opacity: 1, attr: { cx: 440, cy: 470 } }, 1 + i * .3).to(p, { attr: { cx: 690, cy: 290 }, duration: .7, ease: 'none' }, 1 + i * .3).to(p, { opacity: 0, duration: .1 }, 1.7 + i * .3));
  if (!REAL) countTo(o, 'v', SENSOR_PCT, val, v => T('Moisture ' + v.toFixed(1) + '%'), 1.2, E.out3, tl, 2.2);
  gsap.to(arcs, { opacity: .2, duration: .6, stagger: .15, repeat: LOOP, yoyo: true, ease: E.sine, delay: 1.2 });
  gsap.to(cloud, { y: '-=8', duration: 2.2, repeat: LOOP, yoyo: true, ease: E.sine, delay: 1.5 });
  return tl;
} });

// 5 ── Satellite sees km; we see your field (8 s)
SCENES.push({ act: 'ACT 1 · FROM SOIL TO CLOUD', cap: 'Satellite sees km. We see your field.', note: CALIB_LIVE ? 'Live sensor readings' : 'Demo sensor and calibration values', build(g, from) {
  const px = el('rect', { x: 340, y: 240, width: 600, height: 340, fill: '#3b82f61f', stroke: C.blue, 'stroke-width': 3, 'stroke-dasharray': '14 10', opacity: 0 }, g);
  const gridL = [1, 2].flatMap(i => [el('line', { x1: 340 + i * 200, x2: 340 + i * 200, y1: 240, y2: 580, stroke: C.blue, 'stroke-width': 1, opacity: 0 }, g), el('line', { x1: 340, x2: 940, y1: 240 + i * 113, y2: 240 + i * 113, stroke: C.blue, 'stroke-width': 1, opacity: 0 }, g)]);
  const pxl = txt(g, 640, 224, 'ONE SATELLITE PIXEL ≈ SEVERAL KM', 20, C.blueL, 'middle', 700, { 'letter-spacing': '2', opacity: 0 });
  const field = grp(g, 640, 410);
  el('rect', { x: -22, y: -15, width: 44, height: 30, fill: C.gold }, field); el('circle', { r: 5, fill: C.navy }, field);
  const fring = el('circle', { cx: 640, cy: 410, r: 24, fill: 'none', stroke: C.gold, 'stroke-width': 3, opacity: 0 }, g);
  const beam = el('path', { d: 'M620 150 L340 240 L940 240 L660 150 Z', fill: '#3b82f61c', opacity: 0 }, g);
  const sat = grp(g, 640, -110);
  el('rect', { x: -26, y: -18, width: 52, height: 36, rx: 6, fill: '#cbd5e1' }, sat);
  [-1, 1].forEach(s => { el('rect', { x: s < 0 ? -112 : 36, y: -11, width: 76, height: 22, fill: '#2563eb' }, sat); [1, 2].forEach(k => el('line', { x1: (s < 0 ? -112 : 36) + k * 25, x2: (s < 0 ? -112 : 36) + k * 25, y1: -11, y2: 11, stroke: '#93c5fd', 'stroke-width': 1 }, sat)); });
  el('circle', { cy: 28, r: 8, fill: '#94a3b8' }, sat);
  const mk = (label, bg, fg, x) => { const c = grp(g, x, 520); c.setAttribute('opacity', 0); el('rect', { x: -140, y: -44, width: 280, height: 88, rx: 16, fill: bg }, c); txt(c, 0, 13, label, 38, fg, 'middle', 800); return c; };
  const a = mk('NASA ' + SAT_PCT + '%', C.blue, '#fff', -200), b = mk('SENSOR ' + Math.round(SENSOR_PCT) + '%', C.gold, C.navy, 1480);
  if (from === 3) gsap.set(b, { x: 1020, y: 490, opacity: 1 });     // the SENSOR card stays on screen from scene 4
  const ok = grp(g, 640, 520); ok.setAttribute('opacity', 0);
  el('rect', { x: -190, y: -50, width: 380, height: 100, rx: 18, fill: C.green }, ok);
  const chk = el('path', { d: 'M-150 2 l18 18 l34 -38', stroke: '#05290f', 'stroke-width': 8, fill: 'none', 'stroke-linecap': 'round', 'stroke-linejoin': 'round', pathLength: 1, 'stroke-dasharray': 1, 'stroke-dashoffset': 1 }, ok);
  txt(ok, 24, 14, 'Calibrated', 44, '#05290f', 'middle', 800);
  const adj = txt(g, 640, 598, '+' + ADJUST + ' pts adjustment', 22, C.green, 'middle', 700, { opacity: 0 });
  // Label follows the data: LIVE once /calibracion reports real sensor readings, EXAMPLE otherwise (regenerate data.js to switch).
  if (CALIB_LIVE) chip(g, 1140, 62, 'LIVE', C.green, '#05290f', 21); else chip(g, 1090, 62, 'EXAMPLE · NEXT MODULE', C.gold, C.navy, 21);
  const tl = gsap.timeline();
  tl.to(sat, { y: 110, duration: 1.3, ease: E.out }, 0).to(beam, { opacity: 1, duration: .5 }, 1)
    .to(px, { opacity: 1, duration: .5 }, 1.2).to(gridL, { opacity: .25, duration: .5, stagger: .05 }, 1.4).to(pxl, { opacity: 1, duration: .5 }, 1.5)
    .from(field, { opacity: 0, scale: .6, transformOrigin: '50% 50%', duration: .5, ease: E.pop }, 2.1).to(fring, { opacity: 1, duration: .2 }, 2.3)
    .fromTo(fring, { attr: { r: 24 } }, { attr: { r: 60 }, opacity: 0, duration: 1, ease: E.out3, repeat: LOOP ? 2 : 0 }, 2.3)
    .set([a, b], { opacity: 1 }, 3.2)
    .to(a, { x: 480, duration: 1.3, ease: E.io }, 3.2).to(b, { x: 800, y: 520, duration: 1.3, ease: E.io }, 3.2)
    .to([a, b], { x: 640, duration: .3, ease: 'power3.in' }, 4.6)
    .to([a, b], { opacity: 0, duration: .1 }, 4.9)
    .fromTo(ok, { opacity: 0, scale: .8, svgOrigin: '640 520' }, { opacity: 1, scale: 1, duration: .5, ease: E.pop }, 4.9)
    .to(chk, { strokeDashoffset: 0, duration: .45, ease: E.out3 }, 5.2).to(adj, { opacity: 1, duration: .5 }, 5.5);
  burst(g, 640, 520, 16, C.goldL, 150, tl, 4.9);
  gsap.to(sat, { y: '-=6', duration: 2, repeat: LOOP, yoyo: true, ease: E.sine, delay: 2 });
  return tl;
} });

// 6 ── Every year of NASA rainfall (6 s)
SCENES.push({ act: 'ACT 2 · ROTAHAWK', cap: YEARS + ' years of real NASA climate', note: 'NASA POWER · PRECTOTCORR annual sum · Durango', build(g) {
  const w = 1120 / YEARS, bars = RAINH.map((v, i) => { const h = v * 300; return el('rect', { x: 80 + i * w + 2, y: 600 - h, width: w - 4, height: h, rx: 3, fill: C.blue, opacity: .5 }, g); });
  el('line', { x1: 70, x2: 1210, y1: 602, y2: 602, stroke: '#ffffff44', 'stroke-width': 2 }, g);
  txt(g, 80, 636, String(Y0), 20, C.mute, 'start', 600); txt(g, 1200, 636, String(Y0 + YEARS - 1), 20, C.mute, 'end', 600);
  txt(g, 1200, 192, 'NASA POWER · rainfall per year', 20, C.blueL, 'end', 600);
  const yr = txt(g, 1200, 150, String(Y0), 92, C.gold, 'end', 800), scan = el('rect', { x: 78, y: 280, width: 3, height: 330, fill: C.goldL, opacity: 0 }, g);
  const o = { y: Y0 }, tl = gsap.timeline(), D = 4.2;
  tl.from(bars, { attr: { height: 0, y: 600 }, duration: .6, stagger: .09, ease: E.out3 }, 0)
    .to(scan, { opacity: .8, duration: .2 }, 0).to(scan, { x: 1120, duration: D, ease: 'none' }, 0).to(scan, { opacity: 0, duration: .3 }, D)
    .to(o, { y: Y0 + YEARS - 1, duration: D, ease: 'none', onUpdate: () => yr.textContent = Math.round(o.y) }, 0);
  bars.forEach((b, i) => tl.to(b, { opacity: .95, duration: .25 }, .1 + i * (D / YEARS)));
  return tl;
} });

// 7 ── Every rotation, every year (10 s)
SCENES.push({ act: 'ACT 2 · ROTAHAWK', cap: 'Every rotation, every year', note: 'Engine output: FAO water and frost rules on NASA POWER data', build(g, from) {
  const tl = gsap.timeline(), cnt = FAILS.map(() => 0), STEP = .16, T0 = from === 5 ? 1.1 : .25, bw = 1120 / YEARS;
  // the rainfall bars of the previous scene shrink into a strip above the grid, so each year keeps its column
  const strip = RAINH.map((v, i) => el('rect', { x: GRID.x0 + i * GRID.cw + 1, y: 108 - v * 44, width: GRID.cw - 2, height: v * 44, rx: 2, fill: C.blue, opacity: .85 }, g));
  const sl = txt(g, 350, 104, 'rainfall', 16, C.blueL, 'end', 600);
  if (from === 5) strip.forEach((b, i) => tl.from(b, { attr: { x: 80 + i * bw + 2, y: 600 - RAINH[i] * 300, width: bw - 4, height: RAINH[i] * 300 }, duration: .9, ease: E.io }, i * .004));
  else tl.from(strip, { opacity: 0, duration: .4, stagger: .005 }, 0);
  const rows = FAILS.map((_, r) => gridRow(g, r, false));
  tl.from([sl, ...rows.flatMap(x => [x.lab, x.crops, x.cnt])], { opacity: 0, x: -20, duration: .5, stagger: .03, ease: E.out3 }, from === 5 ? .5 : 0);
  const scan = el('rect', { x: GRID.x0, y: 60, width: 3, height: 560, fill: C.goldL, opacity: 0 }, g);
  tl.to(scan, { opacity: .9, duration: .2 }, T0).to(scan, { x: 860, duration: STEP * YEARS, ease: 'none' }, T0).to(scan, { opacity: 0, duration: .3 }, T0 + STEP * YEARS);
  for (let i = 0; i < YEARS; i++) {
    const t = T0 + .05 + i * STEP;
    rows.forEach((row, r) => {
      const { c, bad } = row.cells[i];
      tl.fromTo(c, { opacity: 0, scaleY: .6, transformOrigin: '50% 50%', transformBox: 'fill-box' }, { opacity: bad ? 1 : .4, scaleY: 1, duration: .3, ease: E.out3 }, t);
      if (bad) {
        tl.to(c, { attr: { fill: C.red }, duration: .15 }, t + .1).fromTo(c, { scaleX: 1.5 }, { scaleX: 1, duration: .3, ease: E.out3, immediateRender: false }, t + .1);
        tl.call(() => { cnt[r]++; row.cnt.textContent = cnt[r] + ' / ' + YEARS; if (r === 0) row.cnt.setAttribute('fill', C.red); }, null, t + .1);
      }
    });
  }
  tl.call(() => rows.forEach((row, r) => row.cnt.textContent = FAILS[r] + ' / ' + YEARS), null, T0 + YEARS * STEP + .4);
  return tl;
} });

// 8 ── The worst year, not the average (6 s): the same grid, narrowed to two rows, then to one year.
// The comparison is chosen from the data: the safest alternative if one beats the current rotation, otherwise the riskiest.
SCENES.push({ act: 'ACT 2 · ROTAHAWK', cap: 'The worst year, not the average', note: 'Engine output on NASA POWER data', build(g, from) {
  const other = SAFER ? BEST : RISKY, rel = FAILS[other] < FAILS[0] ? 'SAFER' : FAILS[other] > FAILS[0] ? 'RISKIER' : 'SAME RISK';
  const relCol = rel === 'SAFER' ? C.green : rel === 'RISKIER' ? C.red : C.yellow;
  const tl = gsap.timeline(), rows = FAILS.map((_, r) => gridRow(g, r, true)), cur = rows[0], cmp = rows[other];
  if (from !== 6) tl.from(rows.map(x => x.rg), { opacity: 0, duration: .5, stagger: .06, ease: E.out3 }, 0);
  const others = rows.filter((_, r) => r !== 0 && r !== other).map(x => x.rg);
  const tag = chip(cmp.rg, 190, 16, rel, relCol, rel === 'RISKIER' ? '#fff' : '#05290f', 15); tag.setAttribute('opacity', 0);
  const bx = GRID.x0 + WI * GRID.cw;
  const dim = [cur, cmp].flatMap(x => x.cells.filter(c => c.i !== WI).map(c => c.c));
  const band = el('rect', { x: bx - 5, y: 136, width: GRID.cw + 10, height: 270, rx: 6, fill: '#D4AF3718', stroke: C.gold, 'stroke-width': 3, opacity: 0, filter: 'url(#glow)' }, g);
  const yl = txt(g, Math.min(bx + GRID.cw / 2, 1200), 122, String(WORST_YEAR.year), 32, C.gold, 'middle', 800, { opacity: 0 });
  const ax = [txt(g, GRID.x0, 430, String(Y0), 16, C.mute, 'start', 600, { opacity: 0 }), txt(g, GRID.x0 + 860, 430, String(Y0 + YEARS - 1), 16, C.mute, 'end', 600, { opacity: 0 })];
  const pill = grp(g, 640, 486);
  el('rect', { x: -340, y: -44, width: 680, height: 86, rx: 43, fill: '#D4AF3722', stroke: C.gold, 'stroke-width': 3 }, pill);
  txt(pill, 0, -4, 'Worst year ' + WORST_YEAR.year, 34, C.gold, 'middle', 800); txt(pill, 0, 26, WORST_YEAR.why, 20, C.white, 'middle', 500);
  const who = r => r === 0 ? 'Current rotation' : ROW_LABELS[r] + ' (' + NAME[ROWS[r].ciclos[0]] + ' first)';
  const verdictOf = r => FAILSETS[r].has(WI) ? ['✗  ' + who(r) + ': crop failed', C.red] : ['✓  ' + who(r) + ': held', C.green];
  const v0 = verdictOf(0), v1 = verdictOf(other);
  const res = [txt(g, 400, 572, v0[0], 23, v0[1], 'middle', 700, { opacity: 0 }), txt(g, 880, 572, v1[0], 23, v1[1], 'middle', 700, { opacity: 0 })];
  const say = SAFER ? `${who(BEST)} fails ${FAILS[BEST]} of ${YEARS} seasons. Yours fails ${FAILS[0]}.`
    : FAILS[BEST] === FAILS[0] ? `No alternative is safer in a drought here: the best also fails ${FAILS[0]} of ${YEARS}, and ${NAME[ROWS[RISKY].ciclos[0]]} first fails ${FAILS[RISKY]}.`
    : `Every alternative is riskier here: ${NAME[ROWS[RISKY].ciclos[0]]} first fails ${FAILS[RISKY]} of ${YEARS}. Yours fails ${FAILS[0]}.`;
  const verdict = txt(g, 640, 610, say, 20, C.white, 'middle', 600, { opacity: 0 });
  const cw_ = cur.cells[WI].c, cb = cmp.cells[WI].c;
  tl.to(others, { opacity: 0, duration: .4, ease: 'power2.out' }, .4)
    .to(cur.rg, { y: 150, duration: .8, ease: E.io }, .7).to(cmp.rg, { y: 300, duration: .8, ease: E.io }, .7)
    .to(tag, { opacity: 1, duration: .4 }, 1.4).to(ax, { opacity: 1, duration: .4 }, 1.4)
    .to(cur.cnt, { attr: { 'font-size': 46, y: 74, fill: C.red }, duration: .6, ease: E.out3 }, 1.5)
    .to(cmp.cnt, { attr: { 'font-size': 46, y: 74, fill: relCol }, duration: .6, ease: E.out3 }, 1.6)
    .to(dim, { opacity: .12, duration: .6, ease: 'power2.out' }, 2.4)
    .to(band, { opacity: 1, duration: .4 }, 2.6).from(band, { scaleY: .7, transformOrigin: '50% 50%', transformBox: 'fill-box', duration: .6, ease: E.out }, 2.6)
    .to(yl, { opacity: 1, duration: .4 }, 2.8).to(cb, { opacity: 1, duration: .3 }, 2.8)
    .fromTo(cw_, { scaleY: 1.3 }, { scaleY: 1, duration: .5, ease: E.out3, transformOrigin: '50% 50%', transformBox: 'fill-box', immediateRender: false }, 2.8)
    .from(pill, { opacity: 0, y: '+=24', duration: .6, ease: E.out3 }, 3.3)
    .to(res, { opacity: 1, duration: .4, stagger: .2 }, 3.9).to(verdict, { opacity: 1, duration: .5 }, 4.5);
  return tl;
} });

// 9 ── Your priorities, your ranking (5 s): real engine output for two sets of priorities.
// The engine can propose different alternatives for different priorities, so rows are matched by their crops:
// rotations in both rankings slide to their new place, the ones that drop out fade away, new ones fade in.
SCENES.push({ act: 'ACT 2 · ROTAHAWK', cap: 'Your priorities, your ranking', note: 'Engine output for both sets of priorities', build(g) {
  const keys = ['agua', 'suelo', 'ingreso', 'riesgo'], names = ['Water', 'Soil', 'Income*', 'Risk'], pa = D.request.prioridades, pb = D.prioridades_b, kx = v => 230 + v * 300;
  const knobs = names.map((n, i) => { const y = 210 + i * 80; txt(g, 70, y + 8, n, 28, C.white, 'start', 700); el('rect', { x: 230, y: y - 2, width: 300, height: 8, rx: 4, fill: '#ffffff2e' }, g);
    return el('circle', { cx: kx(pa[keys[i]]), cy: y + 2, r: 16, fill: C.gold, filter: 'url(#glow)' }, g); });
  const key = e => e.ciclos.join('-'), byScore = (x, y) => y.puntaje - x.puntaje, yAt = k => 140 + k * 106;
  const A = [...ROWS].sort(byScore), B = [...D.ranking_b].sort(byScore);
  const all = [...A, ...B.filter(b => !A.some(a => key(a) === key(b)))];          // union of both rankings
  const rows = all.map(e => {
    const ia = A.findIndex(a => key(a) === key(e)), ib = B.findIndex(b => key(b) === key(e)), a = A[ia], b = B[ib], first = a || b;
    const r = grp(g, 660, yAt(ia >= 0 ? ia : ib)); if (ia < 0) r.setAttribute('opacity', 0);
    const box = el('rect', { width: 560, height: 90, rx: 16, fill: C.navy2, stroke: SEM[first.semaforo], 'stroke-width': 3 }, r);
    txt(r, 22, 58, e.ciclos.map(c => ICON[c] || '🌱').join(''), 30, C.white, 'start', 500);
    if (e.es_actual) txt(r, 140, 34, 'Current', 17, C.gold, 'start', 700);
    const bar = el('rect', { x: 140, y: 48, width: first.puntaje * 3, height: 14, rx: 7, fill: SEM[first.semaforo] }, r), v = txt(r, 536, 60, String(first.puntaje), 34, C.white, 'end', 800);
    return { r, box, bar, v, a, b, ib };
  });
  txt(g, 70, 560, '* Income: no sourced seed cost or crop price yet (information gap)', 16, C.mute, 'start', 500);
  const tl = gsap.timeline(), o = { w: 0 }, T = 2.3;
  tl.from(rows.filter(x => x.a).map(x => x.r), { opacity: 0, x: '+=40', duration: .5, stagger: .08, ease: E.out3 }, 0);
  knobs.forEach((k, i) => tl.to(k, { attr: { cx: kx(pb[keys[i]]) }, duration: 1, ease: E.io }, 1 + i * .06));
  rows.forEach(x => {
    if (x.a && x.b) tl.to(x.r, { y: yAt(x.ib), duration: .9, ease: E.io }, T).to(x.bar, { attr: { width: x.b.puntaje * 3, fill: SEM[x.b.semaforo] }, duration: .9, ease: E.io }, T).to(x.box, { attr: { stroke: SEM[x.b.semaforo] }, duration: .9 }, T);
    else if (x.a) tl.to(x.r, { opacity: 0, x: '+=40', duration: .45, ease: 'power2.in' }, T);          // dropped from the new ranking
    else tl.fromTo(x.r, { opacity: 0, x: 700 }, { opacity: 1, x: 660, duration: .6, ease: E.out3 }, T + .45);   // new in the ranking
  });
  tl.to(o, { w: 1, duration: .9, ease: E.io, onUpdate: () => rows.forEach(x => { if (x.a && x.b) x.v.textContent = Math.round(x.a.puntaje + (x.b.puntaje - x.a.puntaje) * o.w); }) }, T);
  return tl;
} });

// 10 ── Explained. Sourced. In your pocket. (6 s)
SCENES.push({ act: 'ACT 2 · ROTAHAWK', cap: 'Explained. Sourced. In your pocket.', note: 'Numbers from the engine; wording illustrative', build(g) {
  const cur = ROWS[0], top = [...ROWS].sort((x, y) => y.puntaje - x.puntaje)[0], light = { verde: 'green', amarillo: 'yellow', rojo: 'red' };
  const bub = grp(g, 60, 150);
  el('rect', { width: 650, height: 210, rx: 24, fill: C.navy2, stroke: '#4b6a99', 'stroke-width': 3 }, bub);
  txt(bub, 30, 58, 'Why is my current rotation ' + light[cur.semaforo] + '?', 24, C.mute, 'start', 600);
  const l1 = T(`It would have failed ${cur.fails.length} of ${YEARS} seasons:`), l2 = T(`${cur.by_drought} by drought, ${cur.by_frost} by frost.`);
  const a1 = txt(bub, 30, 114, '', 29, C.white, 'start', 600), a2 = txt(bub, 30, 156, '', 29, C.white, 'start', 600);
  const tags = [['NASA', C.blue, '#fff', 60], ['SENSOR', C.gold, C.navy, 210], ['FAO / INIFAP', '#15803d', '#fff', 380]].map(([l, bg, fg, x]) => { const w = l.length * 15 + 40, t = grp(g, x, 420); el('rect', { width: w, height: 46, rx: 12, fill: bg }, t); txt(t, w / 2, 31, l, 22, fg, 'middle', 800); t.setAttribute('opacity', 0); return t; });
  const note = txt(g, 60, 500, 'Every answer cites its source, and says when one is missing.', 22, C.mute, 'start', 500, { opacity: 0 });
  const ph = grp(g, 1340, 110);
  el('rect', { width: 300, height: 500, rx: 38, fill: '#0f172a', stroke: '#64748b', 'stroke-width': 4 }, ph); el('rect', { x: 18, y: 52, width: 264, height: 400, rx: 16, fill: '#0b141a' }, ph); el('rect', { x: 110, y: 18, width: 80, height: 10, rx: 5, fill: '#1e293b' }, ph);
  const msg = grp(ph, 0, 0); msg.setAttribute('opacity', 0);
  el('rect', { x: 34, y: 96, width: 232, height: 210, rx: 14, fill: '#005c4b' }, msg);
  txt(msg, 150, 132, 'RotaHawk report', 18, '#fff', 'middle', 800); el('circle', { cx: 66, cy: 176, r: 10, fill: SEM[top.semaforo] }, msg);
  txt(msg, 86, 184, top.ciclos.map(c => ICON[c] || '🌱').join(' → '), 22, '#fff', 'start', 600);
  txt(msg, 50, 232, `Works in ${top.resiliencia.anios_ok} of ${top.resiliencia.anios_total} years`, 17, '#fff', 'start', 500); txt(msg, 50, 262, 'Decision support only', 15, '#a7f3d0', 'start', 500);
  const o = { n: 0 }, tl = gsap.timeline();
  tl.from(bub, { opacity: 0, y: '+=24', duration: .5, ease: E.out3 }, 0)
    .to(o, { n: l1.length + l2.length, duration: 1.5, ease: 'none', onUpdate: () => { const n = Math.round(o.n); a1.textContent = l1.slice(0, n); a2.textContent = l2.slice(0, Math.max(0, n - l1.length)); } }, .5)
    .to(tags, { opacity: 1, duration: .01, stagger: .25 }, 2.1).from(tags, { y: '+=14', scale: .85, transformOrigin: '0 50%', duration: .4, stagger: .25, ease: E.pop }, 2.1)
    .to(note, { opacity: 1, duration: .5 }, 2.9)
    .to(ph, { x: 900, duration: 1, ease: E.out }, 3.2).fromTo(msg, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: .5, ease: E.out3 }, 3.9);
  return tl;
} });

// 11 ── Logo and tagline (3 s)
SCENES.push({ act: 'ROTAHAWK', cap: 'Smart Crop Rotation for Climate Resilience', build(g) {
  const logo = grp(g, 640, 250);
  const ring = el('circle', { r: 110, fill: 'none', stroke: C.gold, 'stroke-width': 6, pathLength: 1, 'stroke-dasharray': 1, 'stroke-dashoffset': 1, transform: 'rotate(-90)' }, logo);
  const bird = el('path', { d: 'M-72 22 L0 -74 L72 22 L32 10 L0 64 L-32 10 Z', fill: C.gold, opacity: 0 }, logo);
  const name = txt(g, 640, 472, '', 104, C.gold, 'middle', 800);
  name.innerHTML = 'RotaHawk'.split('').map(ch => `<tspan fill-opacity="0">${ch}</tspan>`).join('');
  const sub = txt(g, 640, 540, 'Team Halcones Dorados · ITSRLL · NASA Space Apps 2026', 26, C.mute, 'middle', 500, { opacity: 0 });
  const tl = gsap.timeline();
  tl.to(ring, { strokeDashoffset: 0, duration: 1.1, ease: E.io }, 0).to(bird, { opacity: 1, duration: .5, ease: E.out3 }, .7)
    .from(bird, { scale: .85, transformOrigin: '50% 50%', transformBox: 'fill-box', duration: .6, ease: E.out }, .7)
    .to(name.querySelectorAll('tspan'), { attr: { 'fill-opacity': 1 }, duration: .3, stagger: .05, ease: E.out3 }, .5)
    .to(sub, { opacity: 1, duration: .6 }, 1.4);
  burst(g, 640, 250, 18, C.goldL, 200, tl, .9);
  gsap.to(ring, { attr: { 'stroke-width': 9 }, duration: 1.6, repeat: LOOP, yoyo: true, ease: E.sine, delay: 1.5 });
  return tl;
} });

/* ---------- controller ---------- */
const SHORT = Q.get('short') === '1';
const SEQ = SHORT ? [1, 3, 4, 6, 7, 9] : SCENES.map((_, i) => i);      // the closing logo scene (10) is left out of the live version                 // scene indexes played, in order
const SPEED = { 1: 1.2, 3: 1.0, 4: 1.2, 6: 1.4, 7: 1.05, 9: 1.1, 10: 1 };                  // short version (~35 s): play some scenes a bit faster
const AUTO = SHORT ? Q.get('autoplay') !== '0' : !!Q.get('autoplay'), HOLD = SHORT ? 0.8 : 0;   // seconds to hold a finished scene
const START = Math.max(0, +(Q.get('start') || 0)), END = Math.min(SEQ.length - 1, Q.get('end') !== null ? +Q.get('end') : SEQ.length - 1);
let cur = -1, live = null, master = null, timer = null;
function step(d) {                       // click / arrows: next or previous scene inside the range, else hand over to the deck
  const n = SEQ.indexOf(cur) + d;
  if (n > END) { if (parent !== window) parent.postMessage({ rota: 'next' }, '*'); else document.title = 'ANIM_DONE'; return; }   // ANIM_DONE: used by record.mjs
  if (n < START) { parent !== window && parent.postMessage({ rota: 'prev' }, '*'); return; }
  go(SEQ[n]);
}

function setCaption(s) {
  s = T(s); const words = s.split(' ');
  capTxt.innerHTML = words.map(w => `<tspan fill-opacity="0">${w.replace(/&/g, '&amp;')} </tspan>`).join('');
  const sp = capTxt.querySelectorAll('tspan');
  gsap.killTweensOf([sp, capLine]);
  gsap.to(sp, { attr: { 'fill-opacity': 1 }, duration: .45, stagger: .05, delay: .25, ease: E.out3 });
  gsap.fromTo(capTxt, { y: 12 }, { y: 0, duration: .6, delay: .25, ease: E.out3 });
  gsap.fromTo(capLine, { opacity: 0, scaleX: .2, svgOrigin: '640 695' }, { opacity: .9, scaleX: 1, duration: .6, delay: .5, ease: E.out3 });
}

// Camera moves for specific scene pairs; every other pair cross-fades.
const EXITS = {
  '0>1': { scale: 3.2, svgOrigin: '640 470', duration: .7, ease: 'power2.in' },   // push in to the probe tips → inside the soil
  '1>2': { scale: .12, svgOrigin: '140 360', duration: .6, ease: E.io },           // pull out: the soil shrinks into the probe icon
};

function go(n, instant, fromOverride) {
  n = Math.max(0, Math.min(SCENES.length - 1, n));
  clearTimeout(timer);
  const from = fromOverride !== undefined ? fromOverride : cur, old = live, S = SCENES[n];
  cur = n;
  // A fresh layer per scene: the camera moves in EXITS scale the outgoing layer, so a layer is never reused.
  const g = el('g', { opacity: instant ? 1 : 0 }, host);
  tagTxt.textContent = T(S.act); noteTxt.textContent = T(S.note || '');
  gsap.to(progress, { attr: { width: (n + 1) / SCENES.length * 1280 }, duration: instant ? 0 : .5, ease: E.out3 });
  if (old) {
    const drop = () => { old.ctx.revert(); old.g.remove(); };
    gsap.killTweensOf(old.g);
    if (instant) drop();
    else gsap.to(old.g, Object.assign({ opacity: 0, duration: .3, ease: 'power2.in', onComplete: drop }, REDUCE ? {} : EXITS[from + '>' + n] || {}));
  }
  if (!instant) gsap.to(g, { opacity: 1, duration: .45, ease: 'power2.out' });
  const ctx = gsap.context(() => { master = S.build(g, from); });
  live = { g, ctx };
  setCaption(S.cap);
  if (SHORT && master) master.timeScale(SPEED[n] || 1);
  if (AUTO && !instant) {
    if (SHORT && master) master.eventCallback('onComplete', () => { timer = setTimeout(() => step(1), HOLD * 1000); });
    else if (SEQ.indexOf(n) < END) timer = setTimeout(() => step(1), DURATIONS[n] * 1000);
  }
}

document.getElementById('wrap').addEventListener('click', () => step(1));
document.addEventListener('keydown', e => {
  if (['ArrowRight', ' ', 'PageDown', 'Enter'].includes(e.key)) { e.preventDefault(); step(1); }
  else if (['ArrowLeft', 'PageUp', 'Backspace'].includes(e.key)) { e.preventDefault(); step(-1); }
  else if (e.key === 'Home') go(SEQ[START]);
  else if (e.key.toLowerCase() === 'f') (document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen()).catch(() => {});
});

if (Q.get('scene') !== null) {            // freeze a scene at time t (stills / review)
  go(+Q.get('scene'), true, Q.get('from') !== null ? +Q.get('from') : -1);   // &from=N previews the hand-off from scene N
  const t = +(Q.get('t') || 0);
  gsap.globalTimeline.pause();
  if (master) master.seek(t, false);
  capTxt.querySelectorAll('tspan').forEach(s => s.setAttribute('fill-opacity', 1));
  capTxt.setAttribute('transform', 'translate(0 0)'); capLine.setAttribute('opacity', .9);
} else { const D0 = +(Q.get('delay') || 0); if (D0) setTimeout(() => go(SEQ[START]), D0); else go(SEQ[START]); }   // ?delay=ms: wait before the first scene (used when recording)
