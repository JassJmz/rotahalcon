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

## Modules
| File | What it does |
|---|---|
| `main.py` | FastAPI app (endpoints above) |
| `nasa_power.py` | Downloads NASA POWER daily climate → `data/nasa_power/` (CSV + metadata + chart). `load_daily()` reads it offline for the engine. Standard library only. See [`data/README.md`](../data/README.md) |

| `crops.py` | Validates the crop table (`data/crops/`): **refuses any value without a source**. Builds `crops.json`. `load_crops()` for the engine |

```bash
python backend/nasa_power.py            # download (needs internet)
python backend/nasa_power.py --offline  # rebuild from saved CSV
python backend/crops.py                 # validate crop table + rebuild crops.json
```

## Next
- Rules engine (H8) + 45-year simulation 1981–2025 (H10)
