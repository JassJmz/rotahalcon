"""Needs `pip install segno` (QR code on slide 7; the generated files are committed, so only rebuilding needs it).
Builds slides/index.html (English) and slides/es.html (Spanish) from ONE template, so both stay in sync.
Run from web/slides/:   python build_slides.py
Numbers (45 seasons, 23 vs 9, worst year...) are filled in the browser from ../animacion/data.js, never typed here."""
import io, os

HERE = os.path.dirname(os.path.abspath(__file__))

SITE = 'https://jassjmz.github.io/rotahalcon/'
# ── TEXTOS ──
T = {
 'en': {
  'lang': 'en', 'title': 'RotaHawk · Pitch', 'hint': '← → / click: move · F: fullscreen · P: presenter view · Ctrl+P: export PDF', 'anim': 'animation',
  'event': 'NASA SPACE APPS CHALLENGE 2026 · FIELD SHIFT',
  'tag': 'Smart Crop Rotation for Climate Resilience',
  'sub': 'We test every crop rotation against <b>45 years of real NASA climate</b>, so a farmer can see which one survives a bad year.',
  'team': 'Team <b>Halcones Dorados</b> · Mecatrónica, ITSRLL · Durango',
  'p_eye': 'THE PROBLEM', 'p_title': 'Every season is a bet on the weather',
  'p_body1': '<b class="gold">Don José</b> <span class="mute">(an example farmer)</span> grows maize in Durango. Each cycle he chooses what to plant <b>without knowing how it would do in a bad year.</b>',
  'p_body2': 'One bad year can cost him the harvest, the water and the health of his soil.',
  'p_body3': 'NASA climate data is free, but it covers kilometers, not his field, and it is hard to read.',
  'p_chart': 'Rainfall per year · Durango · <span class="yrs">1981–2025</span>', 'p_red': 'red = year his maize would have failed',
  'p_big': 'of <span class="yn">45</span> seasons', 'p_big2': 'his maize would have failed',
  'p_worst': 'Worst year <b class="gold wy">1997</b>: <span class="wm">rainfall 56% below normal</span>',
  'p_src': 'Source: RotaHawk engine on NASA POWER (PRECTOTCORR) and FAO crop-water rules.',
  'd_eye': 'LIVE DEMO', 'd_title': 'From a pin on the map to a decision',
  'd1': 'Mark the field', 'd2': 'Read the soil', 'd3': 'Compare rotations', 'd4': 'Pick a bad year', 'd5': 'Ask and adjust',
  'd_cur': 'Current rotation', 'd_alt': 'Best alternative', 'd_of': 'of', 'd_seasons': 'seasons fail',
  'd_node': 'Our prototype node, on the table', 'img1': 'Prototype node: outside', 'img2': 'Prototype node: inside', 'd_node2': 'ESP32 · NPK sensor over RS485 · Firebase', 'd_btn': 'Open the web app →',
  'd_back': 'Backup: if the network fails, the web runs a saved real response and the animation video plays.',
  'i_eye': 'IMPACT AND VALIDITY', 'i_title': 'A tool that says how sure it is',
  'i1h': 'Real data', 'i1b': 'Daily NASA POWER data since 1981: rain, minimum temperature and root-zone soil moisture, <span class="yn">45</span> full seasons, with FAO crop-water and frost rules.',
  'i2h': 'Honest', 'i2b': 'A range, not one number: the best option works in <b class="gold"><span class="bo">36</span> of <span class="yn">45</span> seasons, range <span class="rg">31–40</span></b>. Calibration against the field sensor: next module, example data today. Every answer cites its source.',
  'i3h': 'Open', 'i3b': 'Open source: any region can plug in its own crops and climate.',
  'i_know': 'What we say we do not know', 'k1': 'Seed cost and crop price in Durango', 'k2': 'Local sowing dates (INIFAP)', 'k3': 'Soil-sensor calibration: next module, shown as example data',
  'i_disc': 'Decision support tool: it does not replace an agronomist. Data: NASA LaRC POWER Project (NASA Earth Science/Applied Science Program).',
  'qr_cap': 'Scan to open the web app', 'team_h': 'The team', 'r_t': 'Data and backend', 'r_j': 'AI and repository', 'r_e': 'Web, animation and pitch', 'r_n': 'Hardware', 'c_title': 'Smart Crop Rotation for Climate Resilience', 'c_code': 'Code: github.com/JassJmz/rotahalcon', 'c_lic': 'MIT (code) · CC BY 4.0 (docs, images, animation)',
  'c_live': '<a href="https://jassjmz.github.io/rotahalcon/" style="color:#f1d27a;font-weight:700;text-decoration:none;word-break:break-all">https://jassjmz.github.io/rotahalcon/</a>',
  'c_cred': 'Credits', 'c_cred_b': 'AGRISENSE sensor node, pre-existing hardware shared with permission: Alberto Ortega, Gabriel Jahir Landa, Lizzeth Avalos, Cecilia Reyes, Angel Moreno.',
  'c_disc': 'Not affiliated with or endorsed by NASA.', 'c_ai': 'AI use', 'c_ai_b': 'AI tools helped with code, the assistant and the animation. Details in <b>docs/AI_USE.md</b>. Not affiliated with or endorsed by NASA.',
  'q': '',
  'wm_fmt': "'rainfall ' + Math.abs(+rain[1]) + '% ' + (+rain[1] < 0 ? 'below' : 'above') + ' normal'",
  'langq': '',
  'titles': ['Cover', 'The problem', 'Animation', 'The result', 'Live prototype', 'Impact and validity', 'Close'], 'script': 'PITCH_SCRIPT.md', 'pv': ['Presenter', 'Slide', 'Next', 'Total', 'This slide', 'Start / pause', 'Reset', 'budget', 'No notes for this slide'],
  'ph1': 'HOW IT WORKS · FROM SOIL TO ANSWER',
  'r_eye': 'THE RESULT', 'r_title': 'Same weather, two rotations',
  'r_cap': 'Maize after maize: <b class="red cf">23</b> bad seasons out of <span class="yn">45</span>. Bean–bean–sorghum: <b class="green bf">9</b>.',
  'r_chat': 'Asked how much he will earn per hectare, the assistant answers <i>“I don’t have that data.”</i> We have no sourced prices for Durango, so it never invents a number.',
  'l_eye': 'LIVE · OUR PROTOTYPE', 'l_title': 'The node reads the soil, right now', 'l_card': 'Soil reading', 'l_unit': 'mg/kg',
  'lt': {'wait': 'Waiting for the reading…', 'zero': 'Node connected: the probe is not reading soil yet.', 'demo': 'Demo reading: the node is not connected.', 'ok': 'Last reading {s} s ago', 'err': 'No connection to the server.', 'unv': 'UNVERIFIED'}, 'ph2': 'HOW IT WORKS · THE SYSTEM', 'print1': 'Soil and sensor', 'print2': 'Satellite vs sensor', 'print3': 'Every rotation, every year', 'print4': 'The worst year', 'print5': 'The assistant cites its sources', 'print6': 'RotaHawk',
 },
 'es': {
  'lang': 'es', 'title': 'RotaHawk · Presentación', 'hint': '← → / clic: mover · F: pantalla completa · P: vista del presentador · Ctrl+P: exportar a PDF', 'anim': 'animación',
  'event': 'NASA SPACE APPS CHALLENGE 2026 · FIELD SHIFT',
  'tag': 'Rotación inteligente de cultivos para la resiliencia climática',
  'sub': 'Probamos cada rotación de cultivos con <b>45 años de clima real de la NASA</b>, para que el agricultor vea cuál aguanta un año malo.',
  'team': 'Equipo <b>Halcones Dorados</b> · Mecatrónica, ITSRLL · Durango',
  'p_eye': 'EL PROBLEMA', 'p_title': 'Cada temporada es una apuesta al clima',
  'p_body1': '<b class="gold">Don José</b> <span class="mute">(un agricultor de ejemplo)</span> siembra maíz en Durango. Cada ciclo elige qué sembrar <b>sin saber cómo le iría en un año malo.</b>',
  'p_body2': 'Un solo año malo le puede costar la cosecha, el agua y la salud de su suelo.',
  'p_body3': 'Los datos del clima de la NASA son gratuitos, pero cubren kilómetros, no su parcela, y son difíciles de interpretar.',
  'p_chart': 'Lluvia por año · Durango · <span class="yrs">1981–2025</span>', 'p_red': 'rojo = año en que su maíz habría fallado',
  'p_big': 'de <span class="yn">45</span> temporadas', 'p_big2': 'su maíz habría fallado',
  'p_worst': 'Peor año <b class="gold wy">1997</b>: <span class="wm">lluvia 56% por debajo de lo normal</span>',
  'p_src': 'Fuente: motor de RotaHawk sobre NASA POWER (PRECTOTCORR) y reglas de agua de cultivos de la FAO.',
  'd_eye': 'DEMOSTRACIÓN EN VIVO', 'd_title': 'De un punto en el mapa a una decisión',
  'd1': 'Marcar la parcela', 'd2': 'Leer el suelo', 'd3': 'Comparar rotaciones', 'd4': 'Elegir un año malo', 'd5': 'Preguntar y ajustar',
  'd_cur': 'Rotación actual', 'd_alt': 'Mejor alternativa', 'd_of': 'de', 'd_seasons': 'temporadas fallan',
  'd_node': 'Nuestro nodo prototipo, sobre la mesa', 'img1': 'Nodo prototipo: por fuera', 'img2': 'Nodo prototipo: por dentro', 'd_node2': 'ESP32 · sensor NPK por RS485 · Firebase', 'd_btn': 'Abrir la web →',
  'd_back': 'Respaldo: si falla la red, la web usa una respuesta real guardada y se reproduce el video de la animación.',
  'i_eye': 'IMPACTO Y VALIDEZ', 'i_title': 'Una herramienta que dice qué tan segura está',
  'i1h': 'Datos reales', 'i1b': 'Datos diarios de NASA POWER desde 1981: lluvia, temperatura mínima y humedad del suelo, <span class="yn">45</span> temporadas completas, con reglas de agua y helada de la FAO.',
  'i2h': 'Honesta', 'i2b': 'Un rango, no un solo número: la mejor opción funciona en <b class="gold"><span class="bo">36</span> de <span class="yn">45</span> temporadas, rango <span class="rg">31–40</span></b>. Calibración con el sensor de campo: próximo módulo, hoy con datos de ejemplo. Cada respuesta cita su fuente.',
  'i3h': 'Abierta', 'i3b': 'Código abierto: cualquier región puede conectar sus propios cultivos y su clima.',
  'i_know': 'Lo que decimos que no sabemos', 'k1': 'Costo de semilla y precio del cultivo en Durango', 'k2': 'Fechas locales de siembra (INIFAP)', 'k3': 'Calibración con el sensor de suelo: próximo módulo, mostrada como datos de ejemplo',
  'i_disc': 'Herramienta de apoyo a la decisión: no sustituye a un agrónomo. Datos: NASA LaRC POWER Project (NASA Earth Science/Applied Science Program).',
  'qr_cap': 'Escanea para abrir la web', 'team_h': 'El equipo', 'r_t': 'Datos y backend', 'r_j': 'IA y repositorio', 'r_e': 'Web, animación y pitch', 'r_n': 'Hardware', 'c_title': 'Rotación inteligente de cultivos para la resiliencia climática', 'c_code': 'Código: github.com/JassJmz/rotahalcon', 'c_lic': 'MIT (código) · CC BY 4.0 (documentos, imágenes y animación)',
  'c_live': '<a href="https://jassjmz.github.io/rotahalcon/" style="color:#f1d27a;font-weight:700;text-decoration:none;word-break:break-all">https://jassjmz.github.io/rotahalcon/</a>',
  'c_cred': 'Créditos', 'c_cred_b': 'Nodo sensor AGRISENSE, hardware preexistente compartido con permiso: Alberto Ortega, Gabriel Jahir Landa, Lizzeth Avalos, Cecilia Reyes, Angel Moreno.',
  'c_disc': 'Sin afiliación ni respaldo de la NASA.', 'c_ai': 'Uso de IA', 'c_ai_b': 'Usamos herramientas de IA en el código, el asistente y la animación. Detalles en <b>docs/AI_USE.md</b>. Sin afiliación ni respaldo de la NASA.',
  'q': '&lang=es',
  'wm_fmt': "'lluvia ' + Math.abs(+rain[1]) + '% ' + (+rain[1] < 0 ? 'por debajo' : 'por encima') + ' de lo normal'",
  'langq': '&lang=es',
  'titles': ['Portada', 'El problema', 'Animación', 'El resultado', 'Prototipo en vivo', 'Impacto y validez', 'Cierre'], 'script': 'PITCH_SCRIPT_ES.md', 'pv': ['Presentador', 'Slide', 'Siguiente', 'Total', 'Esta slide', 'Iniciar / pausar', 'Reiniciar', 'tiempo', 'Sin notas para esta slide'],
  'ph1': 'CÓMO FUNCIONA · DEL SUELO A LA RESPUESTA',
  'r_eye': 'EL RESULTADO', 'r_title': 'El mismo clima, dos rotaciones',
  'r_cap': 'Maíz tras maíz: <b class="red cf">23</b> temporadas malas de <span class="yn">45</span>. Frijol–frijol–sorgo: <b class="green bf">9</b>.',
  'r_chat': 'Al preguntarle cuánto ganará por hectárea, el asistente responde <i>«No tengo ese dato».</i> No tenemos precios con fuente para Durango, así que nunca inventa un número.',
  'l_eye': 'EN VIVO · NUESTRO PROTOTIPO', 'l_title': 'El nodo lee el suelo, ahora mismo', 'l_card': 'Lectura del suelo', 'l_unit': 'mg/kg',
  'lt': {'wait': 'Esperando la lectura…', 'zero': 'Nodo conectado: la sonda aún no lee suelo.', 'demo': 'Lectura de ejemplo: el nodo no está conectado.', 'ok': 'Última lectura hace {s} s', 'err': 'Sin conexión con el servidor.', 'unv': 'SIN VERIFICAR'}, 'ph2': 'CÓMO FUNCIONA · EL SISTEMA', 'print1': 'Suelo y sensor', 'print2': 'Satélite contra sensor', 'print3': 'Cada rotación, cada año', 'print4': 'El peor año', 'print5': 'El asistente cita sus fuentes', 'print6': 'RotaHawk',
 },
}
# ── FIN TEXTOS ──

TEMPLATE = r'''<!doctype html>
<html lang="{{lang}}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{title}}</title>
<style>
  :root{--navy:#0B1F3A;--navy2:#102a4c;--navy3:#16345e;--gold:#D4AF37;--goldL:#f1d27a;--ink:#eef3fb;--mute:#9fb0c8;--green:#22c55e;--yellow:#eab308;--red:#ef4444;--blue:#3b82f6;--line:rgba(255,255,255,.09)}
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;background:#040a14;color:var(--ink);font-family:"Segoe UI",system-ui,-apple-system,Roboto,sans-serif;overflow:hidden}
  #stage{position:fixed;inset:0;display:flex;align-items:center;justify-content:center}
  .slide{position:absolute;width:1280px;height:720px;display:none;overflow:hidden;
    background:radial-gradient(900px 500px at 85% -10%,rgba(212,175,55,.12),transparent 60%),radial-gradient(700px 500px at -10% 110%,rgba(59,130,246,.10),transparent 60%),linear-gradient(160deg,#0d2547,#081528)}
  .slide.on{display:block}
  .pad{position:absolute;inset:0;padding:64px 80px}
  .eyebrow{font-size:15px;font-weight:800;letter-spacing:3.5px;color:var(--gold);margin:0 0 14px}
  h1{font-size:96px;line-height:1;margin:0;font-weight:800;letter-spacing:-1px}
  h2{font-size:46px;line-height:1.1;margin:0 0 24px;font-weight:800;letter-spacing:-.5px}
  p{font-size:26px;line-height:1.45;margin:0 0 16px;color:#d6e0ee}
  .gold{color:var(--gold)}.mute{color:var(--mute)}.red{color:var(--red)}.green{color:var(--green)}
  .card{background:linear-gradient(180deg,rgba(255,255,255,.045),rgba(255,255,255,.015));border:1px solid var(--line);border-radius:22px;padding:26px 30px;box-shadow:0 18px 40px rgba(0,0,0,.28)}
  .tag{display:inline-block;font-size:13px;font-weight:800;padding:3px 9px;border-radius:7px;vertical-align:middle;margin-left:8px;letter-spacing:.6px}
  .NASA{background:var(--blue);color:#fff}.SENSOR{background:var(--gold);color:var(--navy)}.FAO{background:#15803d;color:#fff}
  .foot{position:absolute;left:80px;right:80px;bottom:26px;font-size:15px;color:#7f93b0;display:flex;justify-content:space-between;align-items:center}
  .foot .brand{display:flex;align-items:center;gap:8px;font-weight:700;color:#9fb0c8}
  .light{width:16px;height:16px;border-radius:50%;display:inline-block;box-shadow:0 0 12px currentColor}
  .chip{display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,.07);border:1px solid var(--line);border-radius:999px;padding:8px 16px;font-size:20px;color:#dbe6f5}
  iframe{position:absolute;inset:0;width:100%;height:100%;border:0;background:#0B1F3A}
  .btn{display:inline-block;background:var(--gold);color:var(--navy);font-weight:800;font-size:24px;border-radius:14px;padding:14px 28px;text-decoration:none;box-shadow:0 10px 24px rgba(212,175,55,.25)}
  #hint{position:fixed;left:12px;bottom:8px;font-size:12px;color:#5b6b85;transition:opacity 1s}
  .pillar{position:relative}
  .ico{width:54px;height:54px;border-radius:16px;background:rgba(212,175,55,.14);display:flex;align-items:center;justify-content:center;margin-bottom:14px}
  .big{font-size:96px;font-weight:800;line-height:.95;letter-spacing:-2px}
  .steps{display:flex;gap:0;align-items:flex-start;margin:0 0 30px}
  .step{flex:1;text-align:center;position:relative}
  .step .c{width:76px;height:76px;border-radius:50%;margin:0 auto 12px;background:var(--navy3);border:2px solid rgba(212,175,55,.55);display:flex;align-items:center;justify-content:center;position:relative;z-index:1}
  .step span{font-size:20px;font-weight:600;color:#dbe6f5}
  .step:not(:last-child)::after{content:"";position:absolute;top:37px;left:calc(50% + 44px);right:calc(-50% + 44px);height:2px;background:linear-gradient(90deg,var(--gold),rgba(212,175,55,.2))}
  .slide[data-n="6"] h2{margin-bottom:16px}
  .slide[data-n="6"] .chip{font-size:17px;padding:6px 13px}
  .slide[data-n="6"] .card{padding:18px 22px}
  .slide[data-n="6"] .ico{width:44px;height:44px;margin-bottom:8px}
  .printgrid{display:none}
  body.print{overflow:visible;height:auto;background:#fff}
  body.print #stage{position:static;display:block}
  body.print .slide{display:block;position:relative;transform:none!important;page-break-after:always;break-after:page}
  body.print #hint{display:none}
  body.print .anim{display:none}
  body.print .printgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:22px;position:absolute;inset:0;padding:40px;align-content:center;gap:24px 22px}
  .pg{background:#0B1F3A;border:1px solid var(--line);border-radius:14px;overflow:hidden}
  .pg .fr{position:relative;width:100%;aspect-ratio:16/9;overflow:hidden}
  .pg iframe{position:absolute;left:0;top:0;width:1280px;height:720px;transform-origin:0 0;transform:scale(.3)}
  .pg b{display:block;padding:12px 16px;font-size:22px;color:#dbe6f5}
  @page{size:1280px 720px;margin:0}
</style>
</head>
<body>
<div id="stage">

<!-- 1 · Cover -->
<section class="slide" data-n="1">
  <svg viewBox="0 0 1280 720" width="1280" height="720" style="position:absolute;inset:0" aria-hidden="true">
    <defs>
      <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#050d1c"/><stop offset=".55" stop-color="#1b3a66"/><stop offset=".82" stop-color="#d79a52"/><stop offset="1" stop-color="#f2c777"/></linearGradient>
      <linearGradient id="soil" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6e4629"/><stop offset="1" stop-color="#22140a"/></linearGradient>
      <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#081528" stop-opacity=".96"/><stop offset=".55" stop-color="#081528" stop-opacity=".78"/><stop offset="1" stop-color="#081528" stop-opacity="0"/></linearGradient>
      <filter id="gl" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    </defs>
    <rect width="1280" height="720" fill="url(#sky)"/>
    <g fill="#fff"><circle cx="120" cy="60" r="1.6"/><circle cx="260" cy="130" r="1.2"/><circle cx="420" cy="50" r="1.8"/><circle cx="580" cy="110" r="1.2"/><circle cx="700" cy="40" r="1.6"/><circle cx="820" cy="150" r="1.2"/><circle cx="930" cy="70" r="1.8"/><circle cx="1050" cy="120" r="1.2"/><circle cx="1180" cy="40" r="1.6"/><circle cx="340" cy="210" r="1"/><circle cx="1230" cy="200" r="1.2"/></g>
    <circle cx="1010" cy="470" r="150" fill="#ffd36b" opacity=".16"/><circle cx="1010" cy="470" r="66" fill="#ffe09a" filter="url(#gl)"/>
    <path d="M0 470 Q220 380 470 450 T930 430 T1280 460 V520 H0Z" fill="#183a63"/>
    <path d="M0 490 Q300 430 620 482 T1280 470 V540 H0Z" fill="#1e5a4c"/>
    <rect x="0" y="515" width="1280" height="14" fill="#4c9a43"/>
    <g stroke="#7ccf64" stroke-width="3" stroke-linecap="round" fill="none"><path d="M610 515l-4-20M610 515l4-20M610 515v-24"/><path d="M660 515l-4-20M660 515l4-20M660 515v-24"/><path d="M1130 515l-4-20M1130 515l4-20M1130 515v-24"/><path d="M1180 515l-4-20M1180 515l4-20M1180 515v-24"/><path d="M1230 515l-4-20M1230 515l4-20M1230 515v-24"/><path d="M730 515l-4-20M730 515l4-20M730 515v-24"/></g>
    <rect x="0" y="529" width="1280" height="191" fill="url(#soil)"/>
    <g stroke="#00000033" stroke-width="2"><path d="M0 590H1280"/><path d="M0 650H1280"/></g>
    <g fill="#8a5d3a" opacity=".6"><circle cx="640" cy="560" r="9"/><circle cx="700" cy="620" r="12"/><circle cx="780" cy="570" r="8"/><circle cx="1100" cy="600" r="11"/><circle cx="1190" cy="670" r="9"/><circle cx="1000" cy="680" r="7"/><circle cx="660" cy="690" r="8"/></g>
    <g fill="#38bdf8" opacity=".85"><ellipse cx="760" cy="600" rx="4" ry="6"/><ellipse cx="1060" cy="570" rx="4" ry="6"/><ellipse cx="860" cy="680" rx="4" ry="6"/></g>
    <!-- sensor node -->
    <g>
      <rect x="880" y="425" width="86" height="76" rx="12" fill="#102a4c" stroke="#D4AF37" stroke-width="4"/>
      <rect x="892" y="437" width="62" height="22" rx="5" fill="#081528"/><text x="923" y="453" font-size="12" font-weight="800" fill="#D4AF37" text-anchor="middle">AGRISENSE</text>
      <circle cx="948" cy="478" r="5" fill="#22c55e"/>
      <rect x="899" y="501" width="9" height="112" rx="3" fill="#f1d27a"/><rect x="938" y="501" width="9" height="112" rx="3" fill="#f1d27a"/>
      <path d="M923 405q-22-14-44-6M923 405q22-14 44-6M923 385q-36-22-70-8M923 385q36-22 70-8" stroke="#f1d27a" stroke-width="3" fill="none" stroke-linecap="round" opacity=".9"/>
    </g>
    <!-- satellite and its km-wide pixel -->
    <path d="M1090 168L860 520H1230Z" fill="#3b82f6" opacity=".12"/>
    <rect x="860" y="505" width="370" height="24" fill="none" stroke="#93c5fd" stroke-width="2" stroke-dasharray="8 6" opacity=".8"/>
    <g transform="translate(1090 150)"><rect x="-22" y="-16" width="44" height="32" rx="6" fill="#cbd5e1"/><rect x="-96" y="-9" width="66" height="18" fill="#2563eb"/><rect x="30" y="-9" width="66" height="18" fill="#2563eb"/><circle cy="25" r="7" fill="#94a3b8"/></g>
    <rect width="800" height="720" fill="url(#fade)"/>
  </svg>
  <div class="pad" style="padding-top:150px">
    <p class="eyebrow">{{event}}</p>
    <h1>Rota<span class="gold">Hawk</span></h1>
    <p style="font-size:34px;line-height:1.2;margin:14px 0 22px;color:#fff;font-weight:600;max-width:640px">{{tag}}</p>
    <p style="font-size:24px;max-width:640px;color:#c5d3e6">{{sub}}</p>
    <p class="mute" style="font-size:20px;margin-top:34px">{{team}}</p>
  </div>
</section>

<!-- 2 · Problem -->
<section class="slide" data-n="2">
  <div class="pad">
    <div style="display:grid;grid-template-columns:5fr 6fr;gap:46px;align-items:center;height:100%;padding-bottom:30px">
      <div>
        <p class="eyebrow">{{p_eye}}</p>
        <h2>{{p_title}}</h2>
        <p>{{p_body1}}</p>
        <p style="font-size:22px">{{p_body2}}</p>
        <p class="mute" style="font-size:20px">{{p_body3}}</p>
      </div>
      <div class="card">
        <p class="mute" style="font-size:18px;margin:0 0 6px">{{p_chart}} <span class="tag NASA">NASA</span></p>
        <svg id="bars" viewBox="0 0 560 150" width="100%" style="display:block"></svg>
        <p class="mute" style="font-size:15px;margin:4px 0 14px"><span class="red">▲</span> {{p_red}}</p>
        <div style="display:flex;align-items:baseline;gap:14px"><span class="big red cf">23</span><span style="font-size:30px;color:#fff;font-weight:600">{{p_big}}</span></div>
        <p style="margin:6px 0 10px;font-size:24px">{{p_big2}}</p>
        <p class="mute" style="font-size:19px;margin:0">{{p_worst}}</p>
      </div>
    </div>
  </div>
  <div class="foot"><span>{{p_src}}</span><span class="brand">RotaHawk · 2 / 7</span></div>
</section>

<!-- 3 · Animation (30 s, plays by itself) -->
<section class="slide" data-n="3" data-src="../animacion/index.html?short=1&start=0&end=6{{q}}">
  <div class="printgrid">
    <p class="eyebrow" style="grid-column:1/-1;margin:0">{{ph1}}</p>
    <div class="pg"><div class="fr"><iframe tabindex="-1" src="../animacion/index.html?scene=1&t=3{{q}}"></iframe></div><b>{{print1}}</b></div>
    <div class="pg"><div class="fr"><iframe tabindex="-1" src="../animacion/index.html?scene=4&t=7{{q}}"></iframe></div><b>{{print2}}</b></div>
    <div class="pg"><div class="fr"><iframe tabindex="-1" src="../animacion/index.html?scene=6&from=5&t=9{{q}}"></iframe></div><b>{{print3}}</b></div>
    <div class="pg"><div class="fr"><iframe tabindex="-1" src="../animacion/index.html?scene=7&from=6&t=5.5{{q}}"></iframe></div><b>{{print4}}</b></div>
    <div class="pg"><div class="fr"><iframe tabindex="-1" src="../animacion/index.html?scene=9&t=5{{q}}"></iframe></div><b>{{print5}}</b></div>
    <div class="pg"><div class="fr"><iframe tabindex="-1" src="../animacion/index.html?scene=10&t=2.4{{q}}"></iframe></div><b>{{print6}}</b></div>
  </div>
</section>

<!-- 4 · The result: real screenshots of the web -->
<section class="slide" data-n="4">
  <div class="pad" style="padding-top:44px">
    <p class="eyebrow">{{r_eye}}</p>
    <h2 style="font-size:40px;margin-bottom:16px">{{r_title}}</h2>
    <img src="img/shot-compare-{{lang}}.webp" alt="" style="width:1080px;display:block;border-radius:16px">
    <p style="font-size:30px;margin:12px 0 14px;color:#fff;font-weight:700;line-height:1.25">{{r_cap}}</p>
    <div style="display:flex;gap:26px;align-items:center">
      <img src="img/shot-chat-{{lang}}.webp" alt="" style="width:520px;display:block;border-radius:16px;flex:none">
      <p style="font-size:21px;margin:0;color:#cfdbea">{{r_chat}}</p>
    </div>
  </div>
  <div class="foot"><span>{{p_src}}</span><span class="brand">RotaHawk · 4 / 7</span></div>
</section>

<!-- 5 · Live prototype: the node's soil reading, read from the API every few seconds -->
<section class="slide" data-n="5">
  <div class="pad" style="padding-top:44px">
    <p class="eyebrow">{{l_eye}}</p>
    <h2 style="font-size:40px;margin-bottom:20px">{{l_title}}</h2>
    <div style="display:grid;grid-template-columns:1fr 1.1fr;gap:28px;align-items:stretch">
      <div class="card" style="padding:16px 20px;text-align:center">
        <div style="display:flex;justify-content:center;align-items:flex-end;gap:14px">
          <img src="img/node-exterior.webp" alt="{{img1}}" style="height:300px;width:auto;display:block;border-radius:12px;background:#fff">
          <img src="img/node-interior.webp" alt="{{img2}}" style="height:300px;width:auto;display:block;border-radius:12px;background:#fff">
        </div>
        <p class="mute" style="font-size:16px;margin:10px 0 0">{{d_node}} · {{d_node2}}</p>
      </div>
      <div class="card" style="padding:18px 22px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px"><p style="font-size:22px;margin:0;color:#fff;font-weight:700">{{l_card}}</p><span id="live-tag" class="tag SENSOR" style="margin:0">SENSOR</span></div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px">
          <div style="background:rgba(255,255,255,.05);border-radius:14px;padding:12px 8px;text-align:center"><div class="mute" style="font-size:20px;font-weight:700">N</div><div id="live-n" style="font-size:54px;font-weight:800;line-height:1.1">—</div><div class="mute" style="font-size:15px">{{l_unit}}</div></div>
          <div style="background:rgba(255,255,255,.05);border-radius:14px;padding:12px 8px;text-align:center"><div class="mute" style="font-size:20px;font-weight:700">P</div><div id="live-p" style="font-size:54px;font-weight:800;line-height:1.1">—</div><div class="mute" style="font-size:15px">{{l_unit}}</div></div>
          <div style="background:rgba(255,255,255,.05);border-radius:14px;padding:12px 8px;text-align:center"><div class="mute" style="font-size:20px;font-weight:700">K</div><div id="live-k" style="font-size:54px;font-weight:800;line-height:1.1">—</div><div class="mute" style="font-size:15px">{{l_unit}}</div></div>
        </div>
        <p id="live-status" class="mute" style="font-size:18px;margin:14px 0 0"><span id="live-dot" class="light" style="background:#64748b;color:#64748b;width:12px;height:12px;margin-right:6px"></span><span id="live-text"></span></p>
      </div>
    </div>
  </div>
  <div class="foot"><span>{{d_back}}</span><span class="brand">RotaHawk · 5 / 7</span></div>
</section>

<!-- 6 · Impact and validity -->
<section class="slide" data-n="6">
  <div class="pad">
    <p class="eyebrow">{{i_eye}}</p>
    <h2>{{i_title}}</h2>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px">
      <div class="card pillar"><div class="ico"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/></svg></div><p class="gold" style="font-size:30px;font-weight:800;margin:0 0 8px">{{i1h}}</p><p style="font-size:18px;line-height:1.4;margin:0">{{i1b}} <span class="tag NASA">NASA</span><span class="tag FAO">FAO</span></p></div>
      <div class="card pillar"><div class="ico"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="1.8" stroke-linecap="round"><path d="M12 3v18M5 8l7-5 7 5M5 16l7 5 7-5" opacity="0"/><path d="M4 12h16M4 12l3-3M4 12l3 3M20 12l-3-3M20 12l-3 3"/></svg></div><p class="gold" style="font-size:30px;font-weight:800;margin:0 0 8px">{{i2h}}</p><p style="font-size:18px;line-height:1.4;margin:0">{{i2b}}</p></div>
      <div class="card pillar"><div class="ico"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M8 7l-5 5 5 5M16 7l5 5-5 5M14 4l-4 16"/></svg></div><p class="gold" style="font-size:30px;font-weight:800;margin:0 0 8px">{{i3h}}</p><p style="font-size:18px;line-height:1.4;margin:0">{{i3b}}</p></div>
    </div>
    <p class="mute" style="font-size:18px;margin:30px 0 10px;letter-spacing:1px;font-weight:700">{{i_know}}</p>
    <div style="display:flex;flex-wrap:wrap;gap:12px"><span class="chip">{{k1}}</span><span class="chip">{{k2}}</span><span class="chip">{{k3}}</span></div>
  </div>
  <div class="foot"><span>{{i_disc}}</span><span class="brand">RotaHawk · 6 / 7</span></div>
</section>

<!-- 7 · Close -->
<section class="slide" data-n="7">
  <div class="pad" style="padding-top:44px;padding-bottom:0">
    <div style="display:grid;grid-template-columns:1.25fr 1fr;gap:36px;align-items:center">
      <div style="display:flex;gap:20px;align-items:center">
        <svg width="84" height="84" viewBox="-60 -60 120 120" style="flex:none"><circle r="52" fill="none" stroke="#D4AF37" stroke-width="5"/><path d="M-34 12L0 -38L34 12L16 5L0 32L-16 5Z" fill="#D4AF37"/></svg>
        <div>
          <h2 style="font-size:36px;line-height:1.12;margin:0 0 8px">{{c_title}}</h2>
          <p style="font-size:22px;color:#fff;font-weight:700;margin:0 0 2px">Halcones Dorados · ITSRLL</p>
          <p class="mute" style="font-size:14px;margin:0">{{c_code}} · {{c_lic}}</p>
        </div>
      </div>
      <div class="card" style="display:flex;align-items:center;gap:18px;padding:14px 18px">
        <div style="background:#fff;border-radius:12px;padding:8px;line-height:0;flex:none">{{qr_svg}}</div>
        <div><p style="font-size:19px;margin:0 0 4px;color:#fff;font-weight:700">{{qr_cap}}</p><p class="mute" style="font-size:17px;margin:0">{{c_live}}</p></div>
      </div>
    </div>
    <p class="eyebrow" style="margin:22px 0 10px">{{team_h}}</p>
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:22px">
      <figure style="margin:0"><img src="img/team-tania.webp" alt="Tania" style="width:100%;height:292px;object-fit:cover;object-position:top;border-radius:16px;display:block;border:1px solid rgba(255,255,255,.12)"><figcaption style="margin-top:8px"><b style="font-size:22px;color:#fff">Tania</b><br><span class="mute" style="font-size:15px">{{r_t}}</span></figcaption></figure>
      <figure style="margin:0"><img src="img/team-jassiel.webp" alt="Jassiel" style="width:100%;height:292px;object-fit:cover;object-position:top;border-radius:16px;display:block;border:1px solid rgba(255,255,255,.12)"><figcaption style="margin-top:8px"><b style="font-size:22px;color:#fff">Jassiel</b><br><span class="mute" style="font-size:15px">{{r_j}}</span></figcaption></figure>
      <figure style="margin:0"><img src="img/team-esmeralda.webp" alt="Esmeralda" style="width:100%;height:292px;object-fit:cover;object-position:top;border-radius:16px;display:block;border:1px solid rgba(255,255,255,.12)"><figcaption style="margin-top:8px"><b style="font-size:22px;color:#fff">Esmeralda</b><br><span class="mute" style="font-size:15px">{{r_e}}</span></figcaption></figure>
      <figure style="margin:0"><img src="img/team-jean.webp" alt="Jean" style="width:100%;height:292px;object-fit:cover;object-position:top;border-radius:16px;display:block;border:1px solid rgba(255,255,255,.12)"><figcaption style="margin-top:8px"><b style="font-size:22px;color:#fff">Jean</b><br><span class="mute" style="font-size:15px">{{r_n}}</span></figcaption></figure>
    </div>
  </div>
  <div class="foot"><span>{{c_disc}}</span><span class="brand">RotaHawk · 7 / 7</span></div>
</section>

</div>
<div id="hint">{{hint}}</div>

<script src="../animacion/data.js"></script>
<script>
(function () {
  const PRINT = /[?&]print=1/.test(location.search);
  if (PRINT) document.body.classList.add('print');
  // numbers come from the same engine output as the animation (animacion/data.js): never typed by hand
  const D = window.ROTA_DATA;
  if (D) {
    const rows = [...D.estrategias].sort((a, b) => b.es_actual - a.es_actual), cur = rows[0];
    const alts = rows.filter(r => !r.es_actual), best = alts.reduce((a, b) => b.fails.length < a.fails.length ? b : a);
    const yn = D.years.length, rain = /rain ([+-]?\d+)% vs normal/.exec(cur.peor_anio.motivo);
    const set = (cls, v) => document.querySelectorAll('.' + cls).forEach(e => e.textContent = v);
    set('cf', cur.fails.length); set('bf', best.fails.length); set('yn', yn);
    set('yrs', D.years[0] + '–' + D.years[yn - 1]); set('wy', cur.peor_anio.anio);
    if (rain) set('wm', {{wm_fmt}});
    set('rg', best.resiliencia.rango[0] + '–' + best.resiliencia.rango[1]); set('bo', best.resiliencia.anios_ok);
    // slide 2 chart: rainfall per year, years the current rotation fails marked in red
    const svg = document.getElementById('bars'), w = 560 / yn, mx = Math.max(...D.rain_mm), fails = new Set(cur.fails);
    svg.innerHTML = D.years.map((y, i) => { const h = D.rain_mm[i] / mx * 120, bad = fails.has(y);
      return '<rect x="' + (i * w + 1.5) + '" y="' + (128 - h) + '" width="' + (w - 3) + '" height="' + h + '" rx="2" fill="' + (bad ? '#ef4444' : '#3b82f6') + '" opacity="' + (bad ? 1 : .55) + '"/>'
        + (bad ? '<path d="M' + (i * w + w / 2) + ' 136l-4.5 8h9z" fill="#ef4444"/>' : ''); }).join('')
      + '<line x1="0" x2="560" y1="130" y2="130" stroke="#ffffff30"/>';
  }
  const slides = [...document.querySelectorAll('.slide')];
  let i = Math.max(0, Math.min(slides.length - 1, (+location.hash.slice(1) || 1) - 1));
  function fit() { const k = Math.min(innerWidth / 1280, innerHeight / 720); slides.forEach(s => s.style.transform = 'scale(' + k + ')'); }
  function show(n) {
    const prevI = i;
    i = Math.max(0, Math.min(slides.length - 1, n));
    slides.forEach((s, k) => {
      s.classList.toggle('on', k === i);
      const src = s.dataset.src;
      if (src && !PRINT) {
        let fr = s.querySelector('iframe.anim');
        if (k === i) { if (!fr) { fr = document.createElement('iframe'); fr.className = 'anim'; fr.title = '{{anim}}'; fr.allow = 'fullscreen'; s.appendChild(fr); } fr.src = src; setTimeout(() => fr.focus(), 50); }
        else if (fr) fr.remove();
      }
    });
    history.replaceState(null, '', '#' + (i + 1));
    if (typeof livePoll === 'function') livePoll(i === 4);
    if (typeof total === 'function') { if (prevI !== i) { if (prevI === 0 && !running && acc === 0 && !PRINT) { t0 = Date.now(); running = true; } slideT0 = total(); } renderPresenter(); }
  }
  document.querySelectorAll('.pg iframe').forEach(f => { const k = f.parentElement.clientWidth / 1280; if (k) f.style.transform = 'scale(' + k + ')'; });
  setTimeout(() => { const h = document.getElementById('hint'); if (h) h.style.opacity = 0; }, 5000);
  // ── presenter view (key P): script of each slide, next slide, 4-minute timer with a budget per slide ──
  const NOTES = {{notes_json}}, TITLES = {{titles_json}}, PV = {{pv_json}}, BUDGET = [10, 45, 35, 50, 40, 45, 15], LT = {{lt_json}}, API = (new URLSearchParams(location.search).get('api') ?? 'https://rotahalcon.onrender.com'), SENSOR_CONFIRMED = false;   // SENSOR_CONFIRMED: set true when Role 1 confirms which register is N, P and K
  let pw = null, t0 = 0, acc = 0, running = false, slideT0 = 0;
  const total = () => acc + (running ? (Date.now() - t0) / 1000 : 0), fmt = x => { x = Math.max(0, Math.round(x)); return Math.floor(x / 60) + ':' + String(x % 60).padStart(2, '0'); };
  function toggleTimer() { if (running) { acc = total(); running = false; } else { t0 = Date.now(); running = true; } renderPresenter(); }
  function resetTimer() { acc = 0; running = false; slideT0 = 0; renderPresenter(); }
  function renderPresenter() {
    if (!pw || pw.closed) return;
    const d = pw.document, T = total(), S = T - slideT0, B = BUDGET[i], over = S - B, tot = T > 240;
    const set = (id, v) => { const e = d.getElementById(id); if (e) e.innerHTML = v; };
    set('pv-slide', (i + 1) + ' / 7 · ' + TITLES[i]);
    set('pv-next', i < 6 ? (i + 2) + ' · ' + TITLES[i + 1] : '—');
    set('pv-total', fmt(T)); set('pv-slidet', fmt(S) + ' <small>/ ' + fmt(B) + '</small>');
    set('pv-notes', NOTES[i + 1] || PV[8]);
    const tc = d.getElementById('pv-total'), sc = d.getElementById('pv-slidet');
    if (tc) tc.style.color = tot ? '#ef4444' : T > 210 ? '#eab308' : '#22c55e';
    if (sc) sc.style.color = over > 10 ? '#ef4444' : over > 0 ? '#eab308' : '#22c55e';
    const bar = d.getElementById('pv-bar'); if (bar) bar.style.width = Math.min(100, S / B * 100) + '%';
    const b2 = d.getElementById('pv-run'); if (b2) b2.textContent = running ? '⏸' : '▶';
  }
  function openPresenter() {
    if (pw && !pw.closed) { pw.focus(); return; }
    pw = window.open('', 'rota-presenter', 'width=560,height=780');
    if (!pw) { alert('Allow pop-ups for this page to open the presenter view.'); return; }
    pw.document.write('<!doctype html><meta charset="utf-8"><title>' + PV[0] + ' · RotaHawk</title><style>body{margin:0;background:#081528;color:#eef3fb;font-family:Segoe UI,system-ui,sans-serif;padding:18px 22px}small{font-size:.5em;color:#9fb0c8;font-weight:600}.row{display:flex;gap:14px;align-items:stretch}.box{flex:1;background:#102a4c;border:1px solid #ffffff18;border-radius:14px;padding:10px 14px}.l{font-size:12px;letter-spacing:2px;color:#D4AF37;font-weight:800;text-transform:uppercase}.t{font-size:44px;font-weight:800;font-variant-numeric:tabular-nums}#pv-bar{height:6px;background:#D4AF37;border-radius:3px;width:0;transition:width .3s}#pv-notes{font-size:23px;line-height:1.5;margin-top:14px;color:#e6edf8}button{font-size:20px;border:0;border-radius:10px;padding:10px 16px;background:#D4AF37;color:#081528;font-weight:800;cursor:pointer;margin-right:8px}</style>'
      + '<div class="l">' + PV[1] + '</div><div id="pv-slide" style="font-size:24px;font-weight:700;margin-bottom:6px"></div>'
      + '<div class="l" style="margin-top:6px">' + PV[2] + '</div><div id="pv-next" style="font-size:18px;color:#9fb0c8;margin-bottom:12px"></div>'
      + '<div class="row"><div class="box"><div class="l">' + PV[3] + '</div><div class="t" id="pv-total">0:00</div></div><div class="box"><div class="l">' + PV[4] + '</div><div class="t" id="pv-slidet">0:00</div></div></div>'
      + '<div style="margin:10px 0 12px;background:#ffffff18;border-radius:3px"><div id="pv-bar"></div></div>'
      + '<button onclick="opener.__deck.show(opener.__deck.cur()-1)">◀</button><button onclick="opener.__deck.show(opener.__deck.cur()+1)">▶</button><button id="pv-run" onclick="opener.__deck.toggle()" title="' + PV[5] + '">▶</button><button onclick="opener.__deck.reset()" title="' + PV[6] + '">↺</button>'
      + '<div id="pv-notes"></div>'
      + '<script>onkeydown=function(e){var D=opener.__deck;if(e.key==="ArrowRight"||e.key==="PageDown"){D.show(D.cur()+1)}else if(e.key==="ArrowLeft"||e.key==="PageUp"){D.show(D.cur()-1)}else if(e.key===" "){e.preventDefault();D.toggle()}else if(e.key==="r"||e.key==="R"){D.reset()}}<\/script>');
    pw.document.close(); renderPresenter();
  }
  // live soil reading on slide 5 (only polled while that slide is on screen)
  let liveTimer = null;
  async function pollSensor() {
    const $ = id => document.getElementById(id), dot = $('live-dot'), txt = $('live-text'), tag = $('live-tag');
    const paint = (col, msg) => { dot.style.background = col; dot.style.color = col; txt.textContent = msg; };
    try {
      const r = await fetch(API + '/sensor', { cache: 'no-store' }); if (!r.ok) throw new Error(r.status);
      const s = await r.json(), vals = [s.n_mgkg, s.p_mgkg, s.k_mgkg], zero = vals.every(v => !v);
      if (s.mock) { ['n', 'p', 'k'].forEach(k => $('live-' + k).textContent = '—'); paint(zero ? '#eab308' : '#64748b', zero ? LT.zero : LT.demo); tag.textContent = 'SENSOR'; tag.className = 'tag SENSOR'; return; }
      ['n', 'p', 'k'].forEach((k, i) => $('live-' + k).textContent = Math.round(vals[i] * 10) / 10);
      tag.textContent = SENSOR_CONFIRMED ? 'SENSOR' : LT.unv; tag.className = SENSOR_CONFIRMED ? 'tag SENSOR' : 'tag';
      if (!SENSOR_CONFIRMED) tag.style.cssText = 'margin:0;background:#7c2d12;color:#fed7aa';
      paint('#22c55e', LT.ok.replace('{s}', Math.round(s.edad_s || 0)));
    } catch (e) { paint('#ef4444', LT.err); }
  }
  function livePoll(on) { clearInterval(liveTimer); if (on && !PRINT) { pollSensor(); liveTimer = setInterval(pollSensor, 4000); } }
  window.__deck = { show: n => show(n), cur: () => i, toggle: toggleTimer, reset: resetTimer };
  setInterval(renderPresenter, 250);
  addEventListener('resize', fit); if (!PRINT) { fit(); show(i); } else { slides.forEach(s => s.classList.add('on')); }
  addEventListener('message', e => { if (e.data && e.data.rota === 'next') show(i + 1); if (e.data && e.data.rota === 'prev') show(i - 1); });
  addEventListener('keydown', e => {
    if (['ArrowRight', 'PageDown', ' ', 'Enter'].includes(e.key)) { e.preventDefault(); show(i + 1); }
    else if (['ArrowLeft', 'PageUp', 'Backspace'].includes(e.key)) { e.preventDefault(); show(i - 1); }
    else if (e.key === 'p' || e.key === 'P') openPresenter();
    else if (e.key === 'f' || e.key === 'F') (document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen()).catch(() => {});
  });
  addEventListener('click', e => { if (PRINT || e.target.closest('a,iframe')) return; show(i + 1); });
})();
</script>
</body>
</html>
'''

import json, re
def read_notes(md):
    """{slide number: text} from '**N · title (time)**' blocks of the pitch script."""
    txt = io.open(os.path.join(HERE, '..', '..', 'docs', md), encoding='utf-8').read()
    notes = {}
    for m in re.finditer(r'\*\*(\d) · [^\n]*\*\*\n(.*?)(?=\n\*\*\d ·|\n## |\Z)', txt, re.S):
        body = m.group(2).strip().replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        notes[int(m.group(1))] = re.sub(r'\[([^\]]+)\]', r'<i style="color:#D4AF37">[\1]</i>', body.replace('\n\n', '<br><br>').replace('\n', '<br>'))
    return notes

def make_qr(url, size=230):
    try:
        import segno
    except ImportError:
        print('WARNING: segno is not installed; slide 7 gets no QR (pip install segno)')
        return ''
    qr = segno.make(url, error='m')
    w, h = qr.symbol_size(scale=1, border=1)
    svg = qr.svg_inline(scale=1, border=1, dark='#0B1F3A', light='#ffffff')
    # segno gives a 1-pixel-per-module size and no viewBox: add the viewBox and size it here (crisp at any zoom, also in the PDF)
    return svg.replace('<svg ', '<svg viewBox="0 0 %d %d" width="%d" height="%d" shape-rendering="crispEdges" ' % (w, h, size, size), 1)

for lang, d in T.items():
    d = dict(d)
    d['qr_svg'] = make_qr(SITE, 150)
    d['lt_json'] = json.dumps(d['lt'], ensure_ascii=False)
    d['notes_json'] = json.dumps(read_notes(d['script']), ensure_ascii=False).replace('</', '<\\/')
    d['titles_json'] = json.dumps(d['titles'], ensure_ascii=False)
    d['pv_json'] = json.dumps(d['pv'], ensure_ascii=False)
    out = TEMPLATE
    for k, v in d.items():
        if isinstance(v, str):
            out = out.replace('{{' + k + '}}', v)
    assert '{{' not in out, [x for x in out.split('{{')[1:2]]
    name = 'index.html' if lang == 'en' else 'es.html'
    io.open(os.path.join(HERE, name), 'w', encoding='utf-8', newline='\n').write(out)
    print('wrote', name)
