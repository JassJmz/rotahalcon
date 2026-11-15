# RotaHalcón – web (Role 4)

Website and pitch animation. Everything user-facing is in English.

## What works
- `index.html` + `app.js`: the 8 sections (My field, My soil today, Compare, Your bad year, What if…?, Ask RotaHalcón, Glossary, Report) plus "How it works".
- **Live data**: the web calls the real backend (`API_URL` in `app.js`, currently `https://rotahalcon.onrender.com`):
  `POST /recomendar`, `GET /anio-malo` and `POST /preguntar`. The ranking is sorted here by `puntaje`.
- **Offline fallback**: if the API is unreachable the web uses `mock.json`, a saved *real* `/recomendar` response for the default Durango field, and shows an "OFFLINE SNAPSHOT" banner. "Your bad year" is then read from the per-year `anios` list.
- Every visible data point carries a **NASA**, **SENSOR** or **FAO/INIFAP** tag; missing sources are shown as information gaps.
- `animacion/`: the 11-scene animation (HTML + SVG + GSAP). Click, → or Space = next, ← = back, F = fullscreen.
  - Act 2 is **data-driven**: `data.js` holds the real engine output (failed seasons per rotation, worst year, scores for two sets of priorities) and NASA POWER annual rainfall. Regenerate it with `python build_data.py` (from `animacion/`) whenever the engine or the example field changes. Never edit the numbers by hand.
  - Scene 8 picks its comparison from the data: the safest alternative if one beats the current rotation, otherwise the riskiest one, and says so in plain words.
  - `?autoplay=1` advances by itself, for screen-recording the 1080p MP4 backup.
  - `?scene=N&t=S` freezes scene N (0–10) at second S, for slide stills; add `&from=M` to preview the hand-off from scene M.
  - Elements carry over between scenes; loops and ambient particles turn off under `prefers-reduced-motion`.

## Report (Download PDF)
The *Report* section builds a one-page printable report (recommended rotation, current rotation, all rotations tested, worst year, information gaps, sensor and calibration status). "Download PDF" opens the browser's print dialog: choose *Save as PDF*. It follows the page language (`?lang=es`).

## Spanish version
Open `index.html?lang=es` (or press the ES/EN button, top right). `i18n.js` translates the page, and the backend's English sentences with rules (the engine only writes English); anything it does not recognise stays in English. Glossary and assistant answers come from the API already in Spanish (`idioma=es`). To add a sentence, add a rule in `R` or an entry in `D` inside `i18n.js`.

## Presenter view
Open `slides/es.html` (or `index.html`) and press **P**: a second window shows the script of the current slide (read from `docs/PITCH_SCRIPT*.md`), the next slide and a 4:00 timer with a budget per slide (green / amber / red). The timer starts when you leave the cover; its buttons or Space pause it, R resets it. Drag that window to the laptop screen and the deck to the projector. The browser may ask to allow pop-ups.

## Offline test
Open the web with `?api=http://localhost:1` (connection refused) or `?api=http://10.255.255.1` (never answers): it shows a saved real response with a "SAVED SNAPSHOT" banner. With the real API, if the free server takes more than 8 s to wake up, the same snapshot is shown and replaced by the live response when it arrives. The deck and the animation load only local files.

## How to run
```bash
python -m http.server 8080      # from this folder, then open http://localhost:8080/
```
(`fetch('mock.json')` needs a server. The animation alone also opens by double-click.)
The free Render server sleeps: the first request can take up to a minute.

## Still mock / pending
- Sensor reading and satellite calibration: the API still returns `"mock": true`; the web and animation scenes 4–5 say "demo" on screen. Firebase live reading needs the config from Role 1 (keep it out of git).
- Assistant: `/preguntar` on the backend is a stub; set `IA_URL` in `app.js` to Role 3's service when it is public.
- Glossary texts are provisional (`GLOSSARY` in `app.js`); Role 3 publishes the final ones at `GET /glosario`.
- Report PDF / `web/boleta/` from Role 1.
- Offline animation: `animacion/vendor/gsap.min.js` (GSAP 3.12.5) is included; the page falls back to it when the CDN is unreachable. The web also ships Tailwind 3.4.1 and Leaflet 1.9.4 in `web/vendor/`, and the deck has no external dependencies. Only the map tiles (OpenStreetMap) and the API need internet: offline, the map is blank (type the coordinates) and the web uses its saved real response.
