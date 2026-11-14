# AI — RotaHalcón
Owner: Role 3. API keys go in `.env` (git-ignored).

## Status
| Piece | Status |
|---|---|
| `POST /preguntar` — grounded assistant, **template mode** (EN/ES, no invented numbers, cites sources). Also the LLM fallback (plan B) | ✅ working with mock data |
| **Local LLM mode (Ollama, `asistente_ollama.py`)** — free, offline, no key. Default. Same grounding rules, JSON-schema output, auto-fallback to templates | ✅ code ready |
| Claude API mode (`asistente_llm.py`) — optional, paid | ✅ code ready, off by default |
| Uncertainty (bootstrap → `resiliencia.rango`) | ⏳ |
| Satellite ↔ sensor calibration (linear vs. random forest) | ⏳ |
| NDVI bare-soil detection | ⏳ optional |
| Glossary texts · AI-use declaration | ⏳ |

## Local AI (Ollama) — free
```bash
brew install ollama && brew services start ollama
ollama pull qwen2.5:3b        # ~2 GB, once
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
