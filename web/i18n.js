// RotaHalcón web: Spanish version. Open the page with ?lang=es (or use the ES/EN button, top right). English is the default.
// The backend only writes English, so its sentences are translated here with rules; anything unknown stays in English.
// Glossary and assistant answers are requested in Spanish from the API (idioma=es).
(function () {
  'use strict';
  const LANG = new URLSearchParams(location.search).get('lang') === 'es' ? 'es' : 'en';
  window.LANG = LANG;

  // language button
  const btn = document.getElementById('langBtn');
  if (btn) {
    const u = new URL(location.href); u.searchParams.set('lang', LANG === 'es' ? 'en' : 'es');
    btn.href = u.toString(); btn.textContent = LANG === 'es' ? 'EN' : 'ES'; btn.title = LANG === 'es' ? 'English' : 'Español';
  }
  if (LANG !== 'es') { window.I18N = { lang: 'en', tr: s => s }; return; }

  // ── TEXTOS ──  exact strings (after trimming)
  const D = {
    'My field': 'Mi parcela', 'My soil today': 'Mi suelo hoy', 'Compare': 'Comparar', 'Your bad year': 'Tu año malo', 'What if…?': '¿Y si…?',
    'Ask RotaHalcón': 'Pregunta a RotaHalcón', 'Glossary': 'Glosario', 'Report': 'Reporte', 'How it works': 'Cómo funciona',
    'Rotation as': 'La rotación como', 'climate insurance': 'seguro contra el clima',
    'We test every crop rotation against 45 years (1981–2025) of real NASA climate, correct it with a sensor in your field, and tell you which one holds up best in a bad year, not on average.':
      'Probamos cada rotación de cultivos con 45 años (1981–2025) de clima real de la NASA, la corregimos con un sensor en tu parcela y te decimos cuál aguanta mejor un año malo, no el promedio.',
    '⚠ SAVED SNAPSHOT · the live server is unreachable or still waking up; showing a saved real response': '⚠ RESPUESTA GUARDADA · el servidor en vivo no responde o aún está despertando; se muestra una respuesta real guardada',
    '1 · My field': '1 · Mi parcela', 'Drop a pin on your field, pick the soil and the last 2 crops you planted.': 'Marca tu parcela en el mapa, elige el suelo y los últimos 2 cultivos que sembraste.',
    'Latitude': 'Latitud', 'Longitude': 'Longitud', 'Soil type': 'Tipo de suelo', 'Loam': 'Franco', 'Sandy': 'Arenoso', 'Clay': 'Arcilloso',
    'Crop, 2 cycles ago': 'Cultivo de hace 2 ciclos', 'Crop, last cycle': 'Cultivo del último ciclo', 'Test my rotations →': 'Probar mis rotaciones →',
    '2 · My soil today': '2 · Mi suelo hoy', 'Live reading from the AGRISENSE node in your field.': 'Lectura en vivo del nodo AGRISENSE en tu parcela.',
    '3 · Compare': '3 · Comparar', 'Your current rotation and 3 alternatives, each simulated over 3 cycles in every year since 1981.': 'Tu rotación actual y 3 alternativas, cada una simulada en 3 ciclos en cada año desde 1981.',
    '4 · Your bad year': '4 · Tu año malo', 'Pick a year you remember. See what each rotation would have done.': 'Elige un año que recuerdes. Mira qué habría hecho cada rotación.', 'Year': 'Año',
    '5 · What if…?': '5 · ¿Y si…?', 'Change your priorities or the climate. The ranking re-orders live.': 'Cambia tus prioridades o el clima. El ranking se reordena en vivo.',
    'Priorities': 'Prioridades', 'Scenario': 'Escenario', 'Rainfall': 'Lluvia', 'Temperature': 'Temperatura', 'Rain −20%': 'Lluvia −20%', 'Reset': 'Restablecer', 'Live ranking': 'Ranking en vivo',
    'Water': 'Agua', 'Soil': 'Suelo', 'Income': 'Ingreso', 'Risk': 'Riesgo', 'INFORMATION GAP': 'HUECO DE INFORMACIÓN',
    "We don't know seed cost or crop price in your area yet, so this slider has no sourced data behind it.": 'Aún no conocemos el costo de semilla ni el precio del cultivo en tu zona, así que este control no tiene datos con fuente.',
    '6 · Ask RotaHalcón': '6 · Pregunta a RotaHalcón', 'An assistant that does not make things up: every answer cites NASA, SENSOR or FAO/INIFAP, and says when a source is missing.': 'Un asistente que no inventa: cada respuesta cita NASA, SENSOR o FAO/INIFAP y dice cuándo falta una fuente.',
    'Ask': 'Preguntar', '7 · Glossary': '7 · Glosario', 'Hover or tap a term.': 'Pasa el cursor o toca un término.',
    '8 · Report': '8 · Reporte', 'A one-page summary you can download or send by WhatsApp.': 'Un resumen de una página que puedes descargar o enviar por WhatsApp.',
    'Share on WhatsApp': 'Compartir por WhatsApp', 'Download PDF': 'Descargar PDF', 'Rotation report': 'Reporte de rotación', 'Field': 'Parcela', 'Previous crops': 'Cultivos previos',
    'Recommended rotation (highest score for your priorities)': 'Rotación recomendada (mayor puntaje para tus prioridades)', 'All rotations tested': 'Todas las rotaciones probadas',
    'Rotation': 'Rotación', 'Failed seasons': 'Temporadas con fallo', 'Score': 'Puntaje', 'Traffic light': 'Semáforo', 'Green': 'Verde', 'Yellow': 'Amarillo', 'Red': 'Rojo',
    'Soil reading:': 'Lectura del suelo:', 'Satellite calibration:': 'Calibración con el satélite:', 'Example data (next module)': 'Datos de ejemplo (próximo módulo)',
    'No real sensor reading yet: example data': 'Aún no hay lectura real del sensor: datos de ejemplo', 'AGRISENSE reading received; the variables are still being verified': 'Lectura de AGRISENSE recibida; las variables aún se están verificando',
    'Not affiliated with or endorsed by NASA.': 'Sin afiliación ni respaldo de la NASA.',
    'Data: NASA POWER · FAO · INIFAP references · github.com/JassJmz/rotahalcon · jassjmz.github.io/rotahalcon': 'Datos: NASA POWER · referencias FAO · INIFAP · github.com/JassJmz/rotahalcon · jassjmz.github.io/rotahalcon', 'Download PDF (coming)': 'Descargar PDF (próximamente)', 'Coming soon': 'Próximamente',
    'Decision support tool — does not replace an agronomist.': 'Herramienta de apoyo a la decisión: no sustituye a un agrónomo.',
    'Click the animation or press → to move through the story.': 'Haz clic en la animación o pulsa → para avanzar por la historia.',
    '▶ Watch the 30-second animation full screen': '▶ Ver la animación de 30 segundos en pantalla completa', 'On a phone, rotate it sideways for a bigger picture.': 'En el celular, gíralo de lado para verla más grande.',
    'Data: NASA POWER · AGRISENSE node (Alberto Ortega, Gabriel Jahir Landa, Lizzeth Avalos, Cecilia Reyes, Angel Moreno) · FAO / INIFAP references. Open source: github.com/JassJmz/rotahalcon · Built with the help of AI tools (see project page). Not affiliated with or endorsed by NASA.':
      'Datos: NASA POWER · nodo AGRISENSE (Alberto Ortega, Gabriel Jahir Landa, Lizzeth Avalos, Cecilia Reyes, Angel Moreno) · referencias FAO / INIFAP. Código abierto: github.com/JassJmz/rotahalcon · Hecho con ayuda de herramientas de IA (ver página del proyecto). Sin afiliación ni respaldo de la NASA.',
    'Why is my current rotation red?': '¿Por qué mi rotación actual está en rojo?', 'How RotaHalcón works': 'Cómo funciona RotaHalcón',
    // soil card
    'Moisture': 'Humedad', 'Soil temperature': 'Temperatura del suelo', 'Salinity (EC)': 'Salinidad (CE)', 'Nitrogen (N)': 'Nitrógeno (N)', 'Phosphorus (P)': 'Fósforo (P)', 'Potassium (K)': 'Potasio (K)', 'UNVERIFIED': 'SIN VERIFICAR',
    // compare cards
    'Your current rotation': 'Tu rotación actual', 'Alternative': 'Alternativa', 'Why:': 'Por qué:', 'Benefits': 'Beneficios', 'Information gaps': 'Huecos de información', 'Check with an agronomist': 'Revisar con un agrónomo', 'Sources:': 'Fuentes:', 'None': 'Ninguno',
    'EXAMPLE DATA · NEXT MODULE': 'DATOS DE EJEMPLO · PRÓXIMO MÓDULO', 'Satellite corrected by the ground:': 'Satélite corregido con la tierra:',
    'Illustrative until the AGRISENSE moisture probe is connected.': 'Ilustrativo hasta que se conecte la sonda de humedad de AGRISENSE.', '(current)': '(actual)',
    // chat / loading
    'Hi! Ask me about your rotations. I only answer with NASA data, your SENSOR readings and FAO/INIFAP references.': '¡Hola! Pregúntame sobre tus rotaciones. Solo respondo con datos de la NASA, tus lecturas del SENSOR y referencias de FAO/INIFAP.',
    'The assistant is offline right now. In the live system the answer comes from POST /preguntar, using only NASA data, the SENSOR reading and FAO/INIFAP references.': 'El asistente está desconectado en este momento. En el sistema en vivo la respuesta viene de POST /preguntar, con solo datos de la NASA, la lectura del SENSOR y referencias de FAO/INIFAP.',
    'Loading real engine results… the free server can take up to a minute to wake up.': 'Cargando los resultados reales del motor… el servidor gratuito puede tardar hasta un minuto en despertar.',
    // engine gaps (data/crops/gaps.csv and engine.py)
    'Climate data is from the example field in Durango, not from your exact location.': 'Los datos del clima son de la parcela de ejemplo en Durango, no de tu ubicación exacta.',
    'No live soil N reading from the field sensor yet: the soil score does not use N.': 'Aún no hay lectura en vivo de N del suelo con el sensor de campo: el puntaje de suelo no usa N.',
    'Rainfed sowing dates for Durango (INIFAP Campo Experimental Valle del Guadiana) were not found online': 'No encontramos en línea las fechas de siembra de temporal para Durango (INIFAP, Campo Experimental Valle del Guadiana)',
    'FAO cycle lengths are global ranges; local varieties (e.g. Pinto Saltillo bean) may differ': 'Las duraciones de ciclo de la FAO son rangos globales; las variedades locales (p. ej. frijol Pinto Saltillo) pueden diferir',
    'No sourced seed cost or crop price for Durango': 'No hay costo de semilla ni precio del cultivo con fuente para Durango',
    'Alfalfa is not listed in FAO frost Table 4.5': 'La alfalfa no aparece en la Tabla 4.5 de helada de la FAO',
    'FAO gives one value for barley/oats/wheat': 'La FAO da un solo valor para cebada/avena/trigo', 'FAO gives one value for sorghum/millet': 'La FAO da un solo valor para sorgo/mijo',
    'Oats is not listed in FAO-56 Table 24 (seasonal Ky)': 'La avena no aparece en la Tabla 24 de FAO-56 (Ky estacional)',
    'Enough water in every simulated season (NASA rain + soil moisture).': 'Agua suficiente en todas las temporadas simuladas (lluvia NASA + humedad del suelo).',
    'Soil N comes from a field sensor (indicative). NOM-021 classes are for lab analysis (method AS-08) of small-grain cereals: confirm with a soil lab.':
      'El N del suelo viene de un sensor de campo (indicativo). Las clases NOM-021 son para análisis de laboratorio (método AS-08) de cereales de grano pequeño: confírmalo con un laboratorio de suelos.',
    'no failure in this season': 'sin falla en esta temporada', 'This rotation would have held in that season.': 'Esta rotación habría aguantado esa temporada.', 'This rotation would have failed in that season.': 'Esta rotación habría fallado esa temporada.',
    // provisional glossary (offline fallback)
    'Evapotranspiration': 'Evapotranspiración', 'NDVI': 'NDVI', 'Moisture anomaly': 'Anomalía de humedad', 'Frost': 'Helada', 'Water balance': 'Balance hídrico',
    'Water that leaves the field as evaporation from soil plus transpiration from plants.': 'Agua que sale del campo por evaporación del suelo más transpiración de las plantas.',
    'A satellite index of how green and vigorous vegetation is.': 'Un índice satelital de qué tan verde y vigorosa está la vegetación.',
    'How far soil moisture is from its normal value for that time of year.': 'Qué tan lejos está la humedad del suelo de su valor normal para esa época del año.',
    'Air temperature at or below 0 °C that can damage crops.': 'Temperatura del aire de 0 °C o menos que puede dañar los cultivos.',
    'Water coming in (rain, irrigation) minus water going out (evapotranspiration, runoff).': 'Agua que entra (lluvia, riego) menos agua que sale (evapotranspiración, escurrimiento).',
  };
  const FAM = { Fabaceae: 'Fabáceas', Poaceae: 'Poáceas', Asteraceae: 'Asteráceas', Solanaceae: 'Solanáceas', Brassicaceae: 'Brasicáceas' };
  const NCLS = { 'VERY LOW': 'MUY BAJO', LOW: 'BAJO', MEDIUM: 'MEDIO', HIGH: 'ALTO', 'VERY HIGH': 'MUY ALTO' };
  const MON = { January: 'enero', February: 'febrero', March: 'marzo', April: 'abril', May: 'mayo', June: 'junio', July: 'julio', August: 'agosto', September: 'septiembre', October: 'octubre', November: 'noviembre', December: 'diciembre' };
  const CROPS = [[/\bBeans?\b/g, 'Frijol'], [/\bbeans?\b/g, 'frijol'], [/\bCorn\b/g, 'Maíz'], [/\bMaize\b/g, 'Maíz'], [/\bmaize\b/g, 'maíz'], [/\bSorghum\b/g, 'Sorgo'], [/\bsorghum\b/g, 'sorgo'], [/\bOats\b/g, 'Avena'], [/\boats\b/g, 'avena']];
  const loss = (m, l) => (l ? ', pérdida de rendimiento esperada ' + l + '%' : '');
  const R = [   // sentence rules, applied in order to every line
    [/Would have failed (\d+) of (\d+) seasons \((\d+)–(\d+)\): (\d+) by drought, (\d+) by frost\./g, 'Habría fallado $1 de $2 temporadas ($3–$4): $5 por sequía, $6 por helada.'],
    [/It would have failed (\d+) of (\d+) seasons:/g, 'Habría fallado $1 de $2 temporadas:'],
    [/([A-Za-z]+) is a legume: it fixes nitrogen from the air \(FAO\)\./g, '$1 es una leguminosa: fija nitrógeno del aire (FAO).'],
    [/Alternates plant families \((.+?)\)\./g, (m, f) => 'Alterna familias de plantas (' + f.split(' / ').map(x => FAM[x] || x).join(' / ') + ').'],
    [/Your soil N reads ([A-Z ]+) \(([\d.]+) mg\/kg, SENSOR; NOM-021 class\): the legume in this rotation adds nitrogen\./g, (m, c, n) => 'El N de tu suelo es ' + (NCLS[c.trim()] || c) + ' (' + n + ' mg/kg, SENSOR; clase NOM-021): la leguminosa de esta rotación aporta nitrógeno.'],
    [/Your soil N reads ([A-Z ]+) \(([\d.]+) mg\/kg, SENSOR\) and this rotation has no legume: review fertilization with an agronomist\./g, (m, c, n) => 'El N de tu suelo es ' + (NCLS[c.trim()] || c) + ' (' + n + ' mg/kg, SENSOR) y esta rotación no tiene leguminosa: revisa la fertilización con un agrónomo.'],
    [/Frost hit ([A-Za-z]+) in (\d+) of (\d+) seasons \(NASA T2M_MIN\): check the sowing date with an agronomist\./g, 'La helada afectó a $1 en $2 de $3 temporadas (NASA T2M_MIN): revisa la fecha de siembra con un agrónomo.'],
    [/([A-Za-z]+) lacked water in (\d+) of (\d+) seasons: review with an agronomist\./g, '$1 tuvo falta de agua en $2 de $3 temporadas: revísalo con un agrónomo.'],
    [/Repeats the ([A-Za-z]+) family in consecutive cycles: review pests and diseases with an agronomist\./g, (m, f) => 'Repite la familia ' + (FAM[f] || f) + ' en ciclos consecutivos: revisa plagas y enfermedades con un agrónomo.'],
    [/Assumes rainfed sowing on (\d+) ([A-Za-z]+) and FAO global crop values: confirm with INIFAP or an agronomist\./g, (m, d, mo) => 'Supone siembra de temporal el ' + d + ' de ' + (MON[mo] || mo) + ' y valores globales de cultivos de la FAO: confirma con INIFAP o un agrónomo.'],
    [/drought: ([A-Za-z]+) got (\d+)% of the water it needs(?:, expected yield loss (\d+)%)? \(rain ([+\-−]?\d+)% vs normal\)/g, (m, c, w, l, r) => 'sequía: ' + c + ' recibió ' + w + '% del agua que necesita' + loss(m, l) + ' (lluvia ' + r + '% vs lo normal)'],
    [/frost (-?[\d.]+) °C on (\d+ [A-Za-z]+) during ([A-Za-z]+) ([A-Za-z ]+)/g, 'helada de $1 °C el $2 durante $3 $4'],
    [/no failure \(([A-Za-z]+): rain ([+\-−]?\d+)% vs normal\)/g, 'sin falla ($1: lluvia $2% vs lo normal)'],
    [/In (\d+), (\d+) of (\d+) cycles would fail/g, 'En $1, $2 de $3 ciclos fallarían'],
    [/\(current\)/g, '(actual)'], [/^Sources: /g, 'Fuentes: '], [/^(\d+) of (\d+)$/g, '$1 de $2'], [/^Rotation report · (.+)$/g, 'Reporte de rotación · $1'], [/^Soil type$/g, 'Tipo de suelo'],
    [/Works in (\d+) of (\d+) years/g, 'Funciona en $1 de $2 años'], [/\(range (\d+–\d+)\)/g, '(rango $1)'], [/Worst year (\d+):/g, 'Peor año $1:'],
    [/satellite says ([\d.]+)% moisture ·/g, 'el satélite dice $1% de humedad ·'],
    [/your field measures ([\d.]+)% → adjustment ([+\-−]?[\d.]+) pts \((.*?)\)\./g, 'tu parcela mide $1% → ajuste $2 pts ($3).'],
    [/\(((?:± [\d.]+, )?)(\w+) model\)/g, '($1modelo $2)'],
    [/^· last reading: (.+) UTC/g, '· última lectura: $1 UTC'], [/ · node connected, probe returns zeros \(not in soil or RS485 silent\): no reading shown/g, ' · nodo conectado, la sonda devuelve ceros (fuera del suelo o RS485 sin responder): sin lectura'],
    [/ · demo reading \(node not connected yet\)/g, ' · lectura de ejemplo (nodo aún no conectado)'],
    [/^Top score for your priorities: (.+) \((\w+)\) works in (\d+) of (\d+) years\.$/g, 'Mayor puntaje para tus prioridades: $1 ($2) funciona en $3 de $4 años.'],
    [/^Your current rotation: (.+) works in (\d+) of (\d+) years\. Worst year (\d+)\.$/g, 'Tu rotación actual: $1 funciona en $2 de $3 años. Peor año $4.'],
    [/\(offline snapshot\)/g, '(respuesta guardada)'], [/^The assistant is not available right now: /g, 'El asistente no está disponible en este momento: '],
    [/^Could not load recommendations \((.*)\)\. Showing nothing instead of guessing\./g, 'No se pudieron cargar las recomendaciones ($1). No mostramos nada antes que adivinar.'],
  ];
  // ── FIN TEXTOS ──

  function tr(str) {
    if (typeof str !== 'string' || !str.trim()) return str;
    const lead = str.match(/^\s*/)[0], tail = str.match(/\s*$/)[0], core = str.trim();
    if (D[core] !== undefined) return lead + D[core] + tail;
    const lines = core.split('\n').map(line => {
      const t = line.trim(); if (D[t] !== undefined) return D[t];
      let out = line; for (const [re, to] of R) out = out.replace(re, to);
      for (const [re, to] of CROPS) out = out.replace(re, to);
      return out;
    });
    return lead + lines.join('\n') + tail;
  }
  window.I18N = { lang: 'es', tr };

  document.documentElement.lang = 'es';
  document.title = 'RotaHalcón · La rotación como seguro contra el clima';
  document.querySelectorAll('[placeholder],[title]').forEach(e => ['placeholder', 'title'].forEach(a => { const v = e.getAttribute(a); if (v && a !== 'title' || (v && e.id !== 'langBtn')) e.setAttribute(a, tr(v)); }));

  function walk(root) {
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, { acceptNode: n => (n.parentElement && /^(SCRIPT|STYLE|TEXTAREA)$/.test(n.parentElement.tagName)) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT });
    const nodes = []; while (w.nextNode()) nodes.push(w.currentNode);
    nodes.forEach(n => { const t = tr(n.data); if (t !== n.data) n.data = t; });
  }
  walk(document.body);
  new MutationObserver(ms => ms.forEach(m => {
    if (m.type === 'characterData') { const t = tr(m.target.data); if (t !== m.target.data) m.target.data = t; }
    else m.addedNodes.forEach(n => { if (n.nodeType === 3) { const t = tr(n.data); if (t !== n.data) n.data = t; } else if (n.nodeType === 1) { walk(n); ['placeholder', 'title'].forEach(a => { const v = n.getAttribute && n.getAttribute(a); if (v) n.setAttribute(a, tr(v)); }); } });
  })).observe(document.body, { childList: true, subtree: true, characterData: true });
})();
