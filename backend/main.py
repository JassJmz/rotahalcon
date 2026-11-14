"""
RotaHalcón backend — FastAPI.

Endpoints follow docs/CONTRACT.md (A4):
    POST /recomendar   current rotation + 3 alternatives, simulated on NASA climate 1981–2025
    GET  /anio-malo    the same 4 strategies, in one past year
    POST /preguntar    stub only — the real assistant is ia/api.py (Role 3)

`sensor` and `calibracion` are still MOCK until Hardware (Firebase) and IA (calibration) plug in.

Run:  uvicorn main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""

# ── DATOS ──
MOCK_MODE = False                     # True = fixed mock answers (contract format), no engine
DEFAULT_LAT, DEFAULT_LON = 24.02, -104.65   # example field, Durango
ALLOWED_ORIGINS = ["*"]               # open CORS for the hackathon (Web on any host)
# ── FIN DATOS ──

import copy
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import engine

app = FastAPI(title="RotaHalcón API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Request models (contract A4) ----------
class Prioridades(BaseModel):
    agua: float = 0.4
    suelo: float = 0.3
    ingreso: float = 0.2
    riesgo: float = 0.1


class Escenario(BaseModel):
    lluvia_pct: float = Field(0, ge=-90, le=200)   # e.g. -20 = 20 % less rain
    temp_c: float = Field(0, ge=-10, le=10)        # shift applied to daily minimum temperature


class RecomendarIn(BaseModel):
    lat: float = DEFAULT_LAT
    lon: float = DEFAULT_LON
    suelo: str = "franco"
    cultivos_previos: List[str] = Field(default_factory=lambda: ["frijol", "frijol"])
    prioridades: Prioridades = Field(default_factory=Prioridades)
    escenario: Escenario = Field(default_factory=Escenario)


class PreguntarIn(BaseModel):
    pregunta: str
    recomendacion: Optional[Dict] = None


# ---------- Still mock (other roles) ----------
MOCK_SENSOR = {
    "ts": 1794700000, "humedad_pct": 24.1, "temp_c": 19.3, "ph": 7.2,
    "ce_uScm": 410, "n_mgkg": 32, "p_mgkg": 18, "k_mgkg": 145, "fuente": "SENSOR",
    "mock": True,
}
MOCK_CALIBRACION = {
    "satelite_pct": 18, "sensor_pct": 24, "ajuste": 6, "error": 3, "modelo": "lineal",
}


def _envelope(estrategias: List[Dict]) -> Dict:
    return {
        "estrategias": estrategias,
        "sensor": copy.deepcopy(MOCK_SENSOR),
        "calibracion": copy.deepcopy(MOCK_CALIBRACION),
    }


# ---------- Endpoints ----------
@app.get("/")
def salud():
    return {
        "ok": True, "service": "RotaHalcón API", "mock": MOCK_MODE,
        "years": [engine.YEARS[0], engine.YEARS[-1]],
        "crops": engine.CROP_IDS, "soils": list(engine.SOILS),
    }


@app.post("/recomendar")
def recomendar(datos: RecomendarIn):
    try:
        estrategias = engine.recommend(
            datos.lat, datos.lon, datos.suelo, datos.cultivos_previos,
            datos.prioridades.model_dump(), datos.escenario.lluvia_pct, datos.escenario.temp_c,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return _envelope(estrategias)


@app.get("/anio-malo")
def anio_malo(
    anio: int = Query(2011, description="Past year to replay"),
    lat: float = DEFAULT_LAT,
    lon: float = DEFAULT_LON,
    suelo: str = "franco",
    cultivos_previos: str = Query("frijol,frijol", description="Comma separated, e.g. maiz,frijol"),
    lluvia_pct: float = Query(0, ge=-90, le=200),
    temp_c: float = Query(0, ge=-10, le=10),
):
    previos = [c for c in cultivos_previos.split(",") if c.strip()]
    try:
        estrategias = engine.bad_year(anio, lat, lon, suelo, previos,
                                      Prioridades().model_dump(), lluvia_pct, temp_c)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return _envelope(estrategias)


@app.post("/preguntar")
def preguntar(datos: PreguntarIn):
    # Owned by Role 3 (IA): ia/api.py on port 8001. Stub kept so Web never breaks.
    return {
        "respuesta": "The assistant runs in the IA service (port 8001).",
        "fuentes": ["MOCK"],
    }
