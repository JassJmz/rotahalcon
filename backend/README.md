# RotaHalcón — Backend (FastAPI)

Owner: Role 2 (NASA data & engine). API format: [`docs/CONTRACT.md`](../docs/CONTRACT.md) (A4).

## 🌐 Public API
**https://rotahalcon.onrender.com** · interactive docs: **https://rotahalcon.onrender.com/docs**
Free plan: it sleeps after ~15 min idle and the first call takes ~1 min — open it before the demo.
⚠️ Deployed from the **public repo URL**, so it does **not** redeploy on push: after pushing backend changes, go to Render → *rotahalcon* → **Manual Deploy → Deploy latest commit**.

## Status
| Endpoint | Status |
|---|---|
| `GET /` | ✅ health check (years, crops, soils available) |
| `POST /recomendar` | ✅ **REAL** — current rotation + 3 alternatives, simulated on NASA climate 1981–2025 |
| `GET /anio-malo?anio=2011&lat=..&lon=..` | ✅ **REAL** — same 4 strategies replayed in one past year |
| `GET /sensor` | ✅ latest AGRISENSE reading from Firebase (or the flagged mock) — for Web's live soil card |
| `POST /preguntar` | stub only — the real assistant is `ia/api.py` (Role 3), port 8001 |

`calibracion` is still **mock** (until Role 3).

## SENSOR reading (Firebase)
`sensor.py` reads `nodos/agrisense-01/ultima` from **Firebase Realtime Database** over REST and puts it in `sensor` (and `GET /sensor`):
- real reading → contract fields + `"mock": false` + `"edad_s"` (seconds since the reading)
- not configured / unreachable / wrong format → mock reading + `"mock": true` + `"motivo_mock"` (why). The API never breaks.

**Configuration — never commit it:**
| Variable | Value |
|---|---|
| `FIREBASE_DB_URL` | e.g. `https://<project>-default-rtdb.firebaseio.com` (from Role 1) |
| `FIREBASE_AUTH` | optional — only if the database rules require auth |

Locally: create `backend/.env` (git-ignored) with those lines. On Render: *Service → Environment → Add Environment Variable*.
Test: `python backend/sensor.py`

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

**Rotation** = 3 cycles, one rainfed crop per year, **planted in order since 1981** (1981 = cycle 1, 1982 = cycle 2, 1983 = cycle 3, 1984 = cycle 1 …). Resilience = seasons OK / 45.
Each strategy carries **`anios`**: `[{"anio": 1981, "ok": true, "cultivo": "maiz"}, {"anio": 1989, "ok": false, "cultivo": "maiz", "motivo": "drought: …"}, …]` — used by Role 3 and by the animation (scene 7).
`rango` comes from **Role 3's bootstrap** (`ia/incertidumbre.py`, 2000 resamples, 5th–95th percentile, adds `resiliencia.metodo`). If that module is missing, a 90 % Wilson interval is used.
`/anio-malo` answers a different question — *"if a year like this came back, how many of my 3 cycles would fail?"* — so it has no `anios`.

**Score (`puntaje`, 0–100)** = weighted with the user's priorities:
| Priority | Score | Data |
|---|---|---|
| `agua` | average share of the water need that was covered | NASA + FAO |
| `suelo` | share of legumes (fix N) + family changes between cycles (incl. the last previous crop). 50/50 by default; with a **REAL sensor N** reading: low N → 70/30 towards legumes, high N → 30/70 towards rotation | FAO + GBIF + **SENSOR** + NOM-021 |
| `riesgo` | share of seasons that did not fail | NASA + FAO |
| `ingreso` | **not used — no sourced price/cost data** (declared gap); weights are re-normalised | — |

**Alternatives** = all 125 combinations of 3 crops are simulated and ranked by score, then picked in this order:
1. **Do no harm:** only rotations that fail **no more seasons than the current one**; worse ones are used only if nothing else is left.
2. **Variety:** each alternative differs from the others in ≥ 2 of its 3 crops (relaxed to 1 if needed); never the current crops in another order.

**Semáforo** depends **only on failed seasons**, never on the priorities: green ≥ 90 % OK · yellow ≥ 75 % · red below. Priorities only change `puntaje` and which alternatives are chosen.
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
| Soil N class from the field sensor uses NOM-021 lab classes (method AS-08, small-grain cereals) | Only official Mexican N interpretation found; the sensor is indicative | `riesgos` |
| N weights 70/30 · 50/50 · 30/70 | Model design: poor soil favours legumes | this README |

**Soil N (field truth):** the engine uses `n_mgkg` **only when the reading is real** (`sensor.mock == false`). It classifies it with **NOM-021-RECNAT-2000** (very low < 10 · low 10–20 · medium 20–40 · high 40–60 · very high > 60 mg/kg), changes the soil weights, and adds texts to `beneficios` / `riesgos`. Without a real reading it adds a gap to `huecos` and the soil score ignores N.

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
