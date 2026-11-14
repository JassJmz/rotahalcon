"""
RotaHalcón — AI service (local, port 8001). Endpoints: see docs/CONTRACT.md.

Run:   .venv/bin/uvicorn api:app --reload --port 8001
Docs:  http://localhost:8001/docs

/preguntar and /glosario live in rutas.py so the public backend can include them too.
"""
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()                                  # before importing modules that read env vars

from fastapi import FastAPI                    # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from pydantic import BaseModel                 # noqa: E402

import calibracion                             # noqa: E402
import incertidumbre                           # noqa: E402
import rutas                                   # noqa: E402

# ── DATOS ──────────────────────────────────────────────────────────────
ORIGENES_PERMITIDOS = ["*"]                    # hackathon: open CORS so the web can call us
# ───────────────────────────────────────────────────────────────────────

app = FastAPI(title="RotaHalcón AI", version="0.7.0")
app.add_middleware(CORSMiddleware, allow_origins=ORIGENES_PERMITIDOS,
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(rutas.router)               # POST /preguntar, GET /glosario


class Lecturas(BaseModel):
    lecturas: list[dict] | None = None  # [{"ts": unix | "fecha": "YYYY-MM-DD", "humedad_pct": 0-100}]; empty → EXAMPLE data


@lru_cache(maxsize=1)
def _calibracion_ejemplo() -> dict:
    return calibracion.calibrar(None)


@app.get("/salud")
def salud():
    return {"ok": True, "servicio": "ia", **rutas.info()}


@app.post("/incertidumbre")
def calcular_incertidumbre(recomendacion: dict):
    """Backend sends its /recomendar output with per-year results in each strategy
    (estrategia["anios"] = [{"anio": 1981, "ok": true}, ...]); we fill resiliencia.rango."""
    return incertidumbre.agregar_incertidumbre(recomendacion)


@app.get("/calibracion")
def calibracion_actual():
    """Calibration with EXAMPLE readings (cached) until the moisture probe is connected."""
    return _calibracion_ejemplo()


@app.post("/calibrar")
def calibrar(body: Lecturas):
    """Satellite (NASA GWETTOP) vs sensor moisture: linear vs random forest (LOO MAE).
    Without readings it uses EXAMPLE data and says so ("datos": "ejemplo")."""
    if not body.lecturas:
        return _calibracion_ejemplo()
    return calibracion.calibrar(body.lecturas)
