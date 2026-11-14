# AI — RotaHalcón
Owner: Role 3. API keys go in `.env` (git-ignored).

## Status
| Piece | Status |
|---|---|
| `POST /preguntar` — grounded assistant, **template mode** (EN/ES, no invented numbers, cites sources). Also the LLM fallback (plan B) | ✅ working with mock data |
| LLM mode for the assistant | ⏳ next |
| Uncertainty (bootstrap → `resiliencia.rango`) | ⏳ |
| Satellite ↔ sensor calibration (linear vs. random forest) | ⏳ |
| NDVI bare-soil detection | ⏳ optional |
| Glossary texts · AI-use declaration | ⏳ |

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
Response: `{ "respuesta": str, "fuentes": [str], "modo": "plantilla" }`.
