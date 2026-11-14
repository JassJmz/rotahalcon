# RotaHalcón – web (Role 4)

Website and pitch animation. Everything user-facing is in English.

## What works
- `index.html` + `app.js`: the 8 sections (My field, My soil today, Compare, Your bad year, What if…?, Ask RotaHalcón, Glossary, Report) plus "How it works".
- Reads `mock.json`, which follows `docs/CONTRACT.md` exactly. A "DEMO DATA" banner shows while `API_URL` is empty.
- Every visible data point carries a **NASA**, **SENSOR** or **FAO/INIFAP** tag; missing sources are shown as information gaps.
- `animacion/`: the 11-scene animation (HTML + SVG + GSAP). Click, → or Space = next, ← = back, F = fullscreen.
  `animacion/index.html?autoplay=1` advances by itself, for screen-recording the 1080p MP4 backup.
  `animacion/index.html?scene=N&t=S` freezes scene N (0–10) at second S: use it for slide stills and frame-by-frame review.
  Add `&from=M` to preview the hand-off from scene M (e.g. `?scene=7&from=6&t=2`).
  Elements carry over between scenes: camera push into the soil (1→2) and pull out (2→3), the ESP32 travels (3→4),
  the SENSOR card stays (4→5), rainfall bars shrink into a strip above the year grid (6→7), and scene 8 reuses that grid.
  Scenes cross-fade, captions reveal word by word, loops and ambient particles turn off under `prefers-reduced-motion`.

## How to run
```bash
python -m http.server 8080      # from this folder, then open http://localhost:8080/
```
(`fetch('mock.json')` needs a server; opening the file directly will not work.)

## Switching to the real backend
Set `API_URL` at the top of `app.js` (the `── DATOS ──` block). The web then calls `POST /recomendar`, `GET /anio-malo` and `POST /preguntar`.

## Pending
- Firebase live soil reading (needs the config from Role 1; keep it out of git).
- Real glossary texts from Role 3 (`GLOSSARY` in `app.js`; current texts are provisional).
- Report PDF/`web/boleta/` from Role 1.
- Animation numbers marked "illustrative" (`── DATOS ──` in `animacion/anim.js`) are replaced with real engine output at H14.
- Fully offline animation: put `gsap.min.js` in `animacion/vendor/` (the page falls back to it when the CDN is unreachable).
- `mock.json` keys starting with `_mock` are mock-only and do not exist in the real API.
