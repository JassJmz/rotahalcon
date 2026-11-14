// RotaHalcón web – reads docs/CONTRACT.md formats. Uses mock.json until the API is ready.

// ── DATOS ──
const API_URL = 'https://rotahalcon.onrender.com';   // backend (Role 2). '' = always use mock.json. Local: 'http://localhost:8000'
// Assistant, calibration and glossary (Role 3). Same Render URL as the backend by default.
// For a local demo with Ollama open the page with ?ia=http://localhost:8001 (or set it here).
const IA_URL = new URLSearchParams(location.search).get('ia') || '';   // '' = use API_URL
const DEFAULT_POINT = { lat: 24.02, lon: -104.65 };   // Durango
const CROPS = {                // contract ids -> English display
  frijol:  { en: 'Beans',   icon: '🫘' },
  maiz:    { en: 'Corn',    icon: '🌽' },
  avena:   { en: 'Oats',    icon: '🌾' },
  sorgo:   { en: 'Sorghum', icon: '🌱' },
  alfalfa: { en: 'Alfalfa', icon: '🌿' },
};
const SOIL_FIELDS = [   // sensor field -> label, unit
  ['humedad_pct', 'Moisture', '%'], ['temp_c', 'Soil temp', '°C'], ['ph', 'pH', ''], ['ce_uScm', 'Salinity (EC)', 'µS/cm'],
  ['n_mgkg', 'Nitrogen (N)', 'mg/kg'], ['p_mgkg', 'Phosphorus (P)', 'mg/kg'], ['k_mgkg', 'Potassium (K)', 'mg/kg'],
];
// Fields whose meaning Role 1 has verified on the real sensor. Empty until they confirm: a real reading still shows
// every field, but marked UNVERIFIED, so we never present an unconfirmed variable as measured.
const CONFIRMED_FIELDS = [];
const CALIB_CONFIRMED = false;   // calibration stays 'example data' until Role 1 confirms the moisture reading
const PRIOS = [['agua', 'Water'], ['suelo', 'Soil'], ['ingreso', 'Income'], ['riesgo', 'Risk']];
const GLOSSARY = {   // provisional – Role 3 provides final texts
  'Evapotranspiration': 'Water that leaves the field as evaporation from soil plus transpiration from plants.',
  'NDVI': 'A satellite index of how green and vigorous vegetation is.',
  'Moisture anomaly': 'How far soil moisture is from its normal value for that time of year.',
  'Frost': 'Air temperature at or below 0 °C that can damage crops.',
  'Water balance': 'Water coming in (rain, irrigation) minus water going out (evapotranspiration, runoff).',
};
// ── FIN DATOS ──

const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const cname = id => (CROPS[id] ? CROPS[id].en : id);
const state = { lat: DEFAULT_POINT.lat, lon: DEFAULT_POINT.lon, suelo: 'franco', prev: ['maiz', 'maiz'],   // example farmer: maize every cycle (clearest real case, Role 2)
  prio: { agua: .4, suelo: .3, ingreso: .2, riesgo: .1 }, esc: { lluvia_pct: 0, temp_c: 0 } };
let MOCK = null, DATA = null, USING_MOCK = false;   // USING_MOCK: API unreachable, showing the offline snapshot

function srcTag(s) {
  const u = s.toUpperCase();
  if (u.startsWith('NASA')) return 'NASA';
  if (u.startsWith('SENSOR')) return 'SENSOR';
  if (u.startsWith('FAO') || u.startsWith('INIFAP')) return 'FAO';
  return 'GAP';
}
const tag = t => `<span class="tag tag-${t}">${t === 'FAO' ? 'FAO/INIFAP' : t}</span>`;

/* ---------- data layer ---------- */
async function recomendar() {
  const body = { lat: state.lat, lon: state.lon, suelo: state.suelo, cultivos_previos: state.prev, prioridades: state.prio, escenario: state.esc };
  if (API_URL) {
    try {
      const r = await fetch(API_URL + '/recomendar', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      if (!r.ok) throw new Error('API ' + r.status);
      const j = await r.json(); USING_MOCK = false; return j;
    } catch (e) { console.warn('API unavailable, using the offline snapshot:', e.message); }
  }
  USING_MOCK = true;
  return mockRecomendar();
}
function mockRecomendar() {   // offline snapshot of a real response; re-ranking only if an entry carries _mock helpers
  const d = JSON.parse(JSON.stringify(MOCK));
  const w = state.prio, s = state.esc;
  d.estrategias.forEach(e => {
    if (!e._mock) return;
    const m = e._mock, base = PRIOS.reduce((a, [k]) => a + (w[k] || 0) * m.sub[k], 0);
    const hit = m.vuln * (Math.max(0, -s.lluvia_pct) * .5 + s.temp_c * 4);
    e.puntaje = Math.max(0, Math.round(base - hit));
    const lost = Math.round(m.vuln * (Math.max(0, -s.lluvia_pct) * .15 + s.temp_c * 1.5));
    e.resiliencia.anios_ok = Math.max(0, e.resiliencia.anios_ok - lost);
    e.resiliencia.rango = e.resiliencia.rango.map(x => Math.max(0, x - lost));
    const ratio = e.resiliencia.anios_ok / e.resiliencia.anios_total;
    e.semaforo = ratio >= .88 ? 'verde' : ratio >= .75 ? 'amarillo' : 'rojo';
  });
  d.estrategias.sort((a, b) => b.puntaje - a.puntaje);
  return d;
}
async function anioMalo(year) {
  if (API_URL && !USING_MOCK) {
    try {
      const q = `anio=${year}&lat=${state.lat}&lon=${state.lon}&suelo=${state.suelo}&cultivos_previos=${state.prev.join(',')}&lluvia_pct=${state.esc.lluvia_pct}&temp_c=${state.esc.temp_c}`;
      const r = await fetch(`${API_URL}/anio-malo?${q}`);
      if (!r.ok) throw new Error('API ' + r.status);
      return await r.json();
    } catch (e) { console.warn('anio-malo unavailable, deriving it from the per-year results:', e.message); }
  }
  // offline: read that season from the per-year results (anios) already in the recommendation
  return { estrategias: DATA.estrategias.map(e => { const a = (e.anios || []).find(x => x.anio == year) || {};
    return { id: e.id, semaforo: a.ok ? 'verde' : 'rojo', peor_anio: { anio: +year, motivo: a.ok ? 'no failure in this season' : (a.motivo || 'failed') },
      porque: a.ok ? 'This rotation would have held in that season.' : 'This rotation would have failed in that season.' }; }) };
}
async function preguntar(pregunta) {
  const base = IA_URL || API_URL;
  if (base && (!USING_MOCK || IA_URL)) {     // recomendacion = the /recomendar response being shown, so the answer is about this field
    const r = await fetch(base + '/preguntar', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ pregunta, recomendacion: DATA }) });
    if (!r.ok) throw new Error('API ' + r.status);
    return r.json();
  }
  return MOCK._mock_chat.default;
}

/* ---------- 1. field ---------- */
function initField() {
  const opts = Object.entries(CROPS).map(([k, v]) => `<option value="${k}">${v.icon} ${v.en}</option>`).join('');
  $('prev1').innerHTML = opts; $('prev2').innerHTML = opts;
  $('prev1').value = state.prev[0]; $('prev2').value = state.prev[1];
  $('lat').value = state.lat; $('lon').value = state.lon;
  const map = L.map('map').setView([state.lat, state.lon], 9);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18, attribution: '© OpenStreetMap' }).addTo(map);
  const mk = L.marker([state.lat, state.lon]).addTo(map);
  const set = (la, lo) => { state.lat = +(+la).toFixed(4); state.lon = +(+lo).toFixed(4); $('lat').value = state.lat; $('lon').value = state.lon; mk.setLatLng([state.lat, state.lon]); };
  map.on('click', e => set(e.latlng.lat, e.latlng.lng));
  ['lat', 'lon'].forEach(i => $(i).addEventListener('change', () => { set($('lat').value, $('lon').value); map.setView([state.lat, state.lon]); }));
  $('suelo').addEventListener('change', () => state.suelo = $('suelo').value);
  $('prev1').addEventListener('change', () => state.prev[0] = $('prev1').value);
  $('prev2').addEventListener('change', () => state.prev[1] = $('prev2').value);
  $('runBtn').addEventListener('click', async () => { await refresh(); $('compare').scrollIntoView(); });
}

/* ---------- 2. soil ---------- */
function renderSoil(s) {
  const zeros = !!s.mock && /zeros/.test(s.motivo_mock || '');   // probe not in soil / RS485 silent: do not show 0% and pH 0 as readings
  $('soilGrid').innerHTML = SOIL_FIELDS.map(([k, label, unit]) => `
    <div class="card p-4"><div class="flex justify-between items-start"><span class="text-sm text-slate-400">${label}</span>${(s.mock || CONFIRMED_FIELDS.includes(k)) ? tag(s.fuente || 'SENSOR') : '<span class="tag tag-GAP">UNVERIFIED</span>'}</div>
    <div class="text-3xl font-bold mt-2">${zeros ? '—' : (s[k] ?? '—')}<span class="text-base font-normal text-slate-400 ml-1">${unit}</span></div></div>`).join('');
  $('soilTime').textContent = (s.ts ? '· last reading: ' + new Date(s.ts * 1000).toISOString().replace('T', ' ').slice(0, 16) + ' UTC' : '') + (s.mock ? (zeros ? ' · node connected, probe returns zeros (not in soil or RS485 silent): no reading shown' : ' · demo reading (node not connected yet)') : '');
}

/* ---------- 3. compare ---------- */
function renderCompare(d) {
  $('cards').innerHTML = d.estrategias.map(e => {
    const r = e.resiliencia, pct = Math.round(r.anios_ok / r.anios_total * 100);
    const list = (arr, cls) => (arr && arr.length) ? arr.map(x => `<li class="${cls || ''}">${esc(x)}</li>`).join('') : '<li class="text-slate-500">None</li>';
    return `<article class="card p-5">
      <div class="flex items-center justify-between gap-2 mb-3">
        <div class="flex items-center gap-2 flex-wrap">
          ${e.ciclos.map((c, i) => `<span class="rounded-lg bg-navy px-2.5 py-1 text-sm">${i + 1}· ${CROPS[c]?.icon || ''} ${esc(cname(c))}</span>`).join('')}
        </div>
        <span class="light ${e.semaforo}" title="${e.semaforo}"></span>
      </div>
      ${e.es_actual ? '<span class="text-xs font-semibold text-gold uppercase tracking-wide">Your current rotation</span>' : '<span class="text-xs font-semibold text-slate-400 uppercase tracking-wide">Alternative</span>'}
      <div class="mt-1"><span class="text-3xl font-extrabold">Works in ${r.anios_ok} of ${r.anios_total} years</span> <span class="text-slate-400">(range ${r.rango[0]}–${r.rango[1]})</span> ${tag('NASA')}</div>
      <div class="h-2 rounded bg-navy mt-2 overflow-hidden"><div class="h-full ${e.semaforo === 'verde' ? 'bg-green-500' : e.semaforo === 'amarillo' ? 'bg-yellow-500' : 'bg-red-500'}" style="width:${pct}%"></div></div>
      <p class="mt-3 text-sm"><b class="text-gold">Worst year ${e.peor_anio.anio}:</b> ${esc(e.peor_anio.motivo)} ${tag('NASA')}</p>
      <p class="mt-2 text-sm text-slate-300"><b class="text-gold">Why:</b> ${esc(e.porque)}</p>
      <div class="grid sm:grid-cols-3 gap-3 mt-3 text-xs">
        <div><b class="text-green-400">Benefits</b><ul class="list-disc pl-4 mt-1 space-y-0.5">${list(e.beneficios)}</ul></div>
        <div><b class="text-amber-300">Information gaps</b><ul class="list-disc pl-4 mt-1 space-y-0.5">${list(e.huecos)}</ul></div>
        <div><b class="text-red-300">Check with an agronomist</b><ul class="list-disc pl-4 mt-1 space-y-0.5">${list(e.riesgos)}</ul></div>
      </div>
      <div class="flex flex-wrap gap-1.5 mt-3 items-center"><span class="text-xs text-slate-500">Sources:</span>${(e.fuentes || []).map(f => `<span class="text-xs text-slate-300">${tag(srcTag(f))} ${esc(f)}</span>`).join('')}</div>
    </article>`;
  }).join('');
  renderCalib(d.calibracion, !!(d.sensor && d.sensor.mock));
  renderReport(d);
}

// Calibration card. Source: GET /calibracion (Role 3 service) when reachable, else the calibracion block of /recomendar.
// While the moisture probe is not connected the numbers are EXAMPLE data, and the card says so.
function renderCalib(c, example) {
  if (!c) { $('calib').innerHTML = ''; return; }
  const ex = !CALIB_CONFIRMED || example || c.datos === 'ejemplo';
  const err = c.error === null || c.error === undefined ? '' : `± ${c.error}, `;
  $('calib').innerHTML = `${ex ? '<span class="tag tag-GAP mr-2">EXAMPLE DATA · NEXT MODULE</span>' : ''}<b class="text-gold">Satellite corrected by the ground:</b> ${tag('NASA')} satellite says ${c.satelite_pct}% moisture · ${tag('SENSOR')} your field measures ${c.sensor_pct}% → adjustment ${c.ajuste > 0 ? '+' : ''}${c.ajuste} pts (${err}${esc(c.modelo)} model).`
    + (ex ? '<div class="text-xs text-slate-400 mt-1">Illustrative until the AGRISENSE moisture probe is connected.</div>' : '');
}
async function loadSensor() {     // GET /sensor: latest reading from Firebase, or an example reading with mock: true
  if (!API_URL || USING_MOCK) return;
  try { const r = await fetch(API_URL + '/sensor'); if (r.ok) renderSoil(await r.json()); } catch (e) { /* keep the sensor block from /recomendar */ }
}
async function loadCalib() {
  const base = IA_URL || API_URL;
  if (!base || (USING_MOCK && !IA_URL)) return;
  try { const r = await fetch(base + '/calibracion'); if (r.ok) renderCalib(await r.json(), false); } catch (e) { /* keep the card from /recomendar */ }
}

/* ---------- 4. bad year ---------- */
async function initBadYear() {
  const years = (DATA.estrategias[0].anios || []).map(a => a.anio), worst = DATA.estrategias[0].peor_anio.anio;
  if (!years.length) years.push(worst);
  $('yearSel').innerHTML = years.map(y => `<option${y === worst ? ' selected' : ''}>${y}</option>`).join('');
  const draw = async () => {
    const out = await anioMalo($('yearSel').value);
    const base = DATA.estrategias;
    $('yearOut').innerHTML = out.estrategias.map(o => {
      const e = base.find(b => b.id === o.id) || { ciclos: [] };
      return `<div class="rounded-xl bg-navy p-4"><div class="flex justify-between items-center"><span class="text-sm">${e.ciclos.map(c => (CROPS[c]?.icon || '') + ' ' + cname(c)).join(' → ')}</span><span class="light ${o.semaforo}"></span></div>
        <p class="text-xs text-slate-400 mt-2">${esc(o.peor_anio.motivo)} ${tag('NASA')}</p><p class="text-sm mt-1">${esc(o.porque)}</p></div>`;
    }).join('');
  };
  $('yearSel').addEventListener('change', draw);
  await draw();
}

/* ---------- 5. what if ---------- */
function initWhatIf() {
  $('prioBox').innerHTML = PRIOS.map(([k, label]) => `<label class="text-sm text-slate-300 block">${label} <b id="p_${k}v" class="float-right text-white">${Math.round(state.prio[k] * 100)}%</b><input id="p_${k}" type="range" min="0" max="100" value="${Math.round(state.prio[k] * 100)}">${k === 'ingreso' ? '<span class="tag tag-GAP mt-1">INFORMATION GAP</span> <span class="text-xs text-slate-400">We don\'t know seed cost or crop price in your area yet, so this slider has no sourced data behind it.</span>' : ''}</label>`).join('');
  const sync = () => {
    PRIOS.forEach(([k]) => $('p_' + k + 'v').textContent = $('p_' + k).value + '%');
    const sum = PRIOS.reduce((a, [k]) => a + +$('p_' + k).value, 0) || 1;
    PRIOS.forEach(([k]) => state.prio[k] = +$('p_' + k).value / sum);   // normalized to 1 for the API
    state.esc.lluvia_pct = +$('rain').value; state.esc.temp_c = +$('temp').value;
    $('rainV').textContent = (state.esc.lluvia_pct > 0 ? '+' : '') + state.esc.lluvia_pct + '%';
    $('tempV').textContent = '+' + state.esc.temp_c.toFixed(1) + ' °C';
    refresh();
  };
  [...PRIOS.map(([k]) => 'p_' + k), 'rain', 'temp'].forEach(i => $(i).addEventListener('input', sync));
  const preset = (r, t) => { $('rain').value = r; $('temp').value = t; sync(); };
  $('preset1').onclick = () => preset(-20, 0); $('preset2').onclick = () => preset(0, 1.5); $('preset0').onclick = () => preset(0, 0);
}
function renderRank(d) {
  const ranked = [...d.estrategias].sort((a, b) => b.puntaje - a.puntaje);   // the API returns a fixed order: rank here
  const max = Math.max(...ranked.map(e => e.puntaje), 1);
  $('rank').innerHTML = ranked.map((e, i) => `
    <div class="rounded-xl bg-navy p-3"><div class="flex justify-between text-sm"><span><b class="text-gold">#${i + 1}</b> ${e.ciclos.map(c => CROPS[c]?.icon || '').join(' ')} ${e.es_actual ? '<span class="text-xs text-slate-400">(current)</span>' : ''}</span><span class="font-bold">${e.puntaje}</span></div>
    <div class="h-2 rounded bg-navy2 mt-1.5 overflow-hidden"><div class="h-full ${e.semaforo === 'verde' ? 'bg-green-500' : e.semaforo === 'amarillo' ? 'bg-yellow-500' : 'bg-red-500'}" style="width:${e.puntaje / max * 100}%;transition:width .4s"></div></div>
    <div class="text-xs text-slate-400 mt-1">Works in ${e.resiliencia.anios_ok} of ${e.resiliencia.anios_total} years ${tag('NASA')}</div></div>`).join('');
}

/* ---------- 6. chat ---------- */
function addMsg(who, html) {
  const mine = who === 'me';
  $('chat').insertAdjacentHTML('beforeend', `<div class="${mine ? 'text-right' : ''}"><div class="inline-block max-w-[85%] text-left rounded-2xl px-4 py-2.5 text-sm ${mine ? 'bg-gold text-navy' : 'bg-navy'}">${html}</div></div>`);
  $('chat').scrollTop = 1e9;
}
function initChat() {
  addMsg('bot', 'Hi! Ask me about your rotations. I only answer with NASA data, your SENSOR readings and FAO/INIFAP references.');
  $('chatForm').addEventListener('submit', async ev => {
    ev.preventDefault();
    const q = $('chatIn').value.trim(); if (!q) return;
    $('chatIn').value = ''; addMsg('me', esc(q));
    try {
      const a = await preguntar(q);
      addMsg('bot', `${esc(a.respuesta)}<div class="mt-2 flex flex-wrap gap-1.5">${(a.fuentes || []).map(f => `${tag(srcTag(f))}<span class="text-xs text-slate-400 mr-2">${esc(f)}</span>`).join('')}</div>`);
    } catch (e) { addMsg('bot', 'The assistant is not available right now: ' + esc(e.message)); }
  });
}

/* ---------- 7. glossary ---------- */
async function initGlossary() {
  draw(GLOSSARY);
  const base = IA_URL || API_URL; if (!base) return;
  try {
    const r = await fetch(base + '/glosario?idioma=en'); if (!r.ok) return;
    const j = await r.json(); if (!Array.isArray(j) || !j.length) return;
    draw(Object.fromEntries(j.map(t => [t.termino, t.largo || t.corto])));
  } catch (e) { /* keep the provisional texts */ }
  function draw(map) {
    $('gloss').innerHTML = Object.entries(map).map(([t, d]) => `<span class="term" tabindex="0" data-def="${esc(d)}">${esc(t)}</span>`).join('');
  }
}

/* ---------- 8. report ---------- */
function reportText(d) {
  const best = [...d.estrategias].sort((a, b) => b.puntaje - a.puntaje)[0], cur = d.estrategias.find(e => e.es_actual);
  const fmt = e => e.ciclos.map(cname).join(' → ');
  return `RotaHalcón\nTop score for your priorities: ${fmt(best)} (${best.semaforo}) works in ${best.resiliencia.anios_ok} of ${best.resiliencia.anios_total} years.\n` +
    (cur ? `Your current rotation: ${fmt(cur)} works in ${cur.resiliencia.anios_ok} of ${cur.resiliencia.anios_total} years. Worst year ${cur.peor_anio.anio}.\n` : '') +
    'Decision support tool — does not replace an agronomist.' + (USING_MOCK ? '\n(offline snapshot)' : '');
}
function renderReport(d) {
  $('reportPreview').innerHTML = `<pre class="whitespace-pre-wrap font-sans">${esc(reportText(d))}</pre>`;
  $('waBtn').onclick = () => window.open('https://wa.me/?text=' + encodeURIComponent(reportText(d)), '_blank', 'noopener');
}

/* ---------- boot ---------- */
async function refresh() {
  try {
    DATA = await recomendar();
    $('demoBanner').style.display = USING_MOCK ? '' : 'none';
    renderCompare(DATA); renderRank(DATA);
    renderSoil(DATA.sensor || {});
    loadSensor();
    loadCalib();
  } catch (e) { $('cards').innerHTML = `<div class="card p-5 text-red-300">Could not load recommendations (${esc(e.message)}). Showing nothing instead of guessing.</div>`; }
}
(async function init() {
  try { MOCK = await (await fetch('mock.json')).json(); }
  catch (e) { if (!API_URL) { $('cards').innerHTML = '<div class="card p-5 text-red-300">mock.json could not be loaded. Serve this folder with a local web server (python -m http.server).</div>'; return; } }
  $('cards').innerHTML = '<div class="card p-5 text-slate-300">Loading real engine results… the free server can take up to a minute to wake up.</div>';
  initField(); initGlossary(); initChat(); initWhatIf();
  await refresh();
  await initBadYear();
})();
