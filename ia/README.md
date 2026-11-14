# AI — RotaHalcón
Owner: Role 3. API keys go in `.env` (git-ignored).

## Status
| Piece | Status |
|---|---|
| `POST /preguntar` — grounded assistant, **template mode** (EN/ES, no invented numbers, cites sources). Also the LLM fallback (plan B) | ✅ working with mock data |
| **Local LLM mode (Ollama `qwen2.5:7b`, or `qwen2.5:3b` for speed, `asistente_ollama.py`)** — free, offline, no key. Default. Labeled data summary + pre-computed comparisons, JSON-schema output, auto-fallback to templates | ✅ tested (7b: 5–30 s · 3b: 3–15 s) |
| **Hybrid routing** (`ROTAHALCON_HIBRIDO=true`): recognized questions → exact template answer; free-form → LLM | ✅ default |
| Claude API mode (`asistente_llm.py`) — optional, paid | ✅ code ready, off by default |
| Uncertainty (bootstrap → `resiliencia.rango`), `incertidumbre.py` + `POST /incertidumbre` | ✅ working — needs per-year results from backend (below) |
| Satellite ↔ sensor calibration — `calibracion.py`, `GET /calibracion`, `POST /calibrar`: NASA GWETTOP vs field moisture, **linear vs random forest** (leave-one-out MAE); difference mode with < 5 days | ✅ method working — **EXAMPLE data** until the moisture probe is added |
| NDVI bare-soil detection | ⏳ optional |
| Glossary EN/ES (10 terms) — `glosario.json` + `GET /glosario?idioma=en\|es` for the web tooltips | ✅ |
| AI-use declaration | ⏳ |

## Local AI (Ollama) — free
```bash
brew install ollama && brew services start ollama
ollama pull qwen2.5:7b        # ~4.7 GB, once (or qwen2.5:3b, ~2 GB, faster)
cp .env.example .env          # ROTAHALCON_PROVEEDOR=ollama (default)
```
`GET /salud` shows `"ollama": true` when it's running. If Ollama is off, answers fall back to templates (`"modo": "plantilla"`).
To use Claude instead (paid): set `ROTAHALCON_PROVEEDOR=claude` and `ANTHROPIC_API_KEY` in `.env` (git-ignored).

## Run
```bash
cd ia
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn api:app --reload --port 8001
```
Docs: http://localhost:8001/docs

## Try it
```bash
curl -s -X POST localhost:8001/preguntar -H "Content-Type: application/json" \
  -d '{"pregunta":"What should I plant?","idioma":"en"}'
```
Request: `{ "pregunta": str, "recomendacion": {…backend /recomendar output…}, "idioma": "en"|"es" }` — if `recomendacion` is missing, `mock_recomendacion.json` is used (illustrative numbers only).
Response: `{ "respuesta": str, "fuentes": [str], "modo": "ollama" | "llm" | "plantilla" }` (+ `motivo_plantilla` when it fell back).

## Uncertainty — what the backend must send (proposal for docs/CONTRACT.md)
Add an optional per-year list to each strategy in `/recomendar`:
```json
"anios": [ { "anio": 1981, "ok": true }, { "anio": 1982, "ok": false, "motivo": "frost in cycle 2" } ]
```
Then either `from incertidumbre import agregar_incertidumbre` (same repo, Python) or `POST /incertidumbre` with the whole recommendation. It fills
`resiliencia = { "anios_ok", "anios_total", "rango": [lo, hi], "metodo" }` (bootstrap, 2000 resamples, 5th–95th percentile, fixed seed).

## Calibration — how to plug in the real moisture probe
The current node measures N, P, K only. When a capacitive moisture probe is added, calibrate it in two points
(**dry air = 0 %**, **in water = 100 %**) so `humedad_pct` is relative wetness 0–100, comparable with NASA `GWETTOP` (0–1).
Then send the readings:
```json
POST /calibrar  { "lecturas": [ { "ts": 1794700000, "humedad_pct": 44.2 }, { "fecha": "2026-11-12", "humedad_pct": 47.0 } ] }
```
- **≥ 5 distinct days** that overlap NASA (NASA lags ~3 days) → `"modo": "regresion"`, both models compared, best one used.
- Fewer days → `"modo": "diferencia"` (sensor − latest NASA day).
- No readings → EXAMPLE data, always labeled `"datos": "ejemplo"` + `"aviso"`.

Backend can fill `/recomendar`'s `calibracion` with `from calibracion import calibrar` (same pattern as `agregar_incertidumbre`).
With the synthetic example (hypothetical field = 0.85 × satellite + 12), the linear model recovers slope 0.84 / intercept 12.0, MAE 1.45 vs random forest 1.49 — the method works.
