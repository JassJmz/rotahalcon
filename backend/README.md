# RotaHalcón — Backend (FastAPI)

Owner: Role 2 (NASA data & engine). API format: [`docs/CONTRACT.md`](../docs/CONTRACT.md) (A4).

## Status
| Endpoint | Status |
|---|---|
| `GET /` | ✅ health check (years, crops, soils available) |
| `POST /recomendar` | ✅ **REAL** — current rotation + 3 alternatives, simulated on NASA climate 1981–2025 |
| `GET /anio-malo?anio=2011&lat=..&lon=..` | ✅ **REAL** — same 4 strategies replayed in one past year |
| `POST /preguntar` | stub only — the real assistant is `ia/api.py` (Role 3), port 8001 |

Still **mock**: `sensor` (until Hardware/Firebase, flagged `"mock": true`) and `calibracion` (until Role 3).

## Run locally
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Interactive docs: http://localhost:8000/docs

```bash
curl -X POST http://localhost:8000/recomendar -H "Content-Type: application/json" -d "{\"cultivos_previos\":[\"frijol\",\"frijol\"]}"
curl "http://localhost:8000/anio-malo?anio=2011&cultivos_previos=maiz,frijol&lluvia_pct=-20"
```

**Accepted values** — crops: `frijol`, `maiz` (or `maíz`), `avena`, `sorgo`, `alfalfa` · soils: `arenoso`, `franco_arenoso`, `franco`, `franco_limoso`, `arcilloso`.
`/anio-malo` also accepts `suelo`, `cultivos_previos` (comma separated), `lluvia_pct`, `temp_c`.

## How the engine works (`engine.py`)

For **every crop in every past season (1981–2025)** the engine asks two questions with real NASA data:

**1 · Water.** Did the crop get the water it needs?
```
supply = effective rain in the crop window      FAO TM3 ch.4 formula on NASA PRECTOTCORR
       + water stored in the root zone at sowing FAO-56 soil water (Table 19) × root depth (Table 22)
                                                 × how wet NASA GWETROOT says the soil was that year
need   = FAO seasonal crop water need            FAO TM3 Table 14
yield loss = Ky × (1 − supply / need)            FAO-33 via FAO-56 Table 24
```
A season **fails by drought** when the expected yield loss is **≥ 50 %**.

**2 · Frost.** Did NASA `T2M_MIN` reach the FAO critical damage temperature for the crop stage (germination / flowering / fruiting, FAO frost Table 4.5)?

**Rotation** = 3 cycles, one rainfed crop per year, repeated. Its resilience is the expected number of failed seasons over 45 years (it does not depend on which cycle falls in which year). `rango` is a 90 % Wilson interval (Role 3 may replace it with the bootstrap).

**Score (`puntaje`, 0–100)** = weighted with the user's priorities:
| Priority | Score | Data |
|---|---|---|
| `agua` | average share of the water need that was covered | NASA + FAO |
| `suelo` | 50 % share of legumes (fix N) + 50 % family changes between cycles (incl. the last previous crop) | FAO + GBIF |
| `riesgo` | share of seasons that did not fail | NASA + FAO |
| `ingreso` | **not used — no sourced price/cost data** (declared gap); weights are re-normalised | — |

**Alternatives** = all 125 combinations of 3 crops are simulated; the 3 best scores with a different crop mix from the current rotation are returned.
**Semáforo:** green ≥ 90 % OK seasons · yellow ≥ 75 % · red below.
**Scenario:** `lluvia_pct` scales daily rain, `temp_c` shifts daily minimum temperature.

### Model assumptions (all in the `# ── DATOS ──` block, all shown to users)
| Assumption | Why | Shown in |
|---|---|---|
| Rainfed sowing on **1 July** | INIFAP sowing dates for Durango not found online | `riesgos` + `huecos` |
| Low end of FAO ranges for cycle length, water need and root depth | FAO: use the low value for short cycles; local early varieties | `riesgos` |
| Failure = expected yield loss ≥ 50 % | Definition of a "lost season" | this README |
| Stage split 25 % / 50 % / 25 % of the cycle | Approximation for frost stages | this README |
| Oats: strict water rule (no Ky source) | Not in FAO-56 Table 24 | `huecos` |
| Alfalfa: no frost rule (no source) | Not in FAO frost Table 4.5 | `huecos` |

### Results with real data (loam, no scenario)
| Crop | Seasons failed of 45 |
|---|---|
| Bean | 9 |
| Sorghum | 9 |
| Maize | 23 |
| Oats (strict rule) | 44 |
| Alfalfa (rainfed) | 44 |

## Modules
| File | What it does |
|---|---|
| `main.py` | FastAPI app (endpoints above) |
| `engine.py` | Rules engine + simulation. `recommend()`, `bad_year()`, `evaluate()`, `simulate()` — Role 3 can import them for bootstrap / calibration |
| `nasa_power.py` | Downloads NASA POWER daily climate → `data/nasa_power/`. `load_daily()` reads it offline |
| `crops.py` | Validates the crop table (`data/crops/`): **refuses any value without a source**. `load_crops()`, `load_soils()` |

```bash
python backend/nasa_power.py            # download climate (needs internet)
python backend/nasa_power.py --offline  # rebuild from saved CSV (Plan B)
python backend/crops.py                 # validate crop table + rebuild crops.json
```

## Deploy (Render, free plan)
| Setting | Value |
|---|---|
| Source | Public Git repository `https://github.com/JassJmz/rotahalcon` (branch `main`) |
| Root Directory | `backend` |
| Runtime | Python 3 (version from `backend/.python-version`) |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Health Check Path | `/` |

The engine reads `../data/` at startup, so no internet is needed at runtime and no secrets are required.
⚠️ Free instances sleep after ~15 min idle; the first request then takes ~1 min. **Open the URL a few minutes before the demo.**

## Next
- Read the latest SENSOR reading from Firebase (`nodos/agrisense-01/ultima`) → `sensor`
- Plug Role 3 calibration into the soil-moisture term
