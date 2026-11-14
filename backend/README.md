# RotaHalcón — Backend (FastAPI)

Owner: Rol 2 (NASA data & engine). API format: see `docs/CONTRACT.md` (A4).

## Status
| Endpoint | Status |
|---|---|
| `GET /` | ✅ health check |
| `POST /recomendar` | ✅ **MOCK** — contract format, current rotation + 3 alternatives |
| `GET /anio-malo?anio=2011&lat=..&lon=..` | ✅ **MOCK** — same format, single year |
| `POST /preguntar` | ✅ **MOCK** stub only. The real assistant is `ia/api.py` (Rol 3), port 8001 |

⚠️ All numbers are **illustrative mock values**, not agronomic results. Every mock text is tagged `MOCK`.

## Run locally
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Interactive docs: http://localhost:8000/docs

## Quick test
```bash
curl -X POST http://localhost:8000/recomendar -H "Content-Type: application/json" -d "{\"cultivos_previos\":[\"frijol\",\"frijol\"]}"
```

## Next
- NASA POWER daily climate 1981→today (Durango) → `data/` CSV
- Crop table with FAO / INIFAP source per value
- Rules engine + 40-year simulation
