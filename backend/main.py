"""
RotaHalcón backend — FastAPI.

Stage 1 (H2): every endpoint returns MOCK data that follows docs/CONTRACT.md (A4)
exactly, so the Web team can build against it right now.
Mock values are illustrative only — they are NOT agronomic results.

Run:  uvicorn main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""

# ── DATOS ──
MOCK_MODE = True                      # True = fixed mock answers (contract format)
DEFAULT_LAT, DEFAULT_LON = 24.02, -104.65   # example field, Durango
ALLOWED_ORIGINS = ["*"]               # open CORS for the hackathon (Web on any host)
CULTIVOS = ["frijol", "maiz", "avena", "sorgo", "alfalfa"]
SUELOS = ["arenoso", "franco", "arcilloso"]
# ── FIN DATOS ──

import copy
from typing import Dict, List, Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="RotaHalcón API", version="0.1.0-mock")
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
    lluvia_pct: float = 0   # e.g. -20 = 20% less rain
    temp_c: float = 0       # e.g. +1.5 °C


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


# ---------- Mock data (contract format, illustrative numbers) ----------
MOCK_SENSOR = {
    "ts": 1794700000, "humedad_pct": 24.1, "temp_c": 19.3, "ph": 7.2,
    "ce_uScm": 410, "n_mgkg": 32, "p_mgkg": 18, "k_mgkg": 145, "fuente": "SENSOR",
}

MOCK_CALIBRACION = {
    "satelite_pct": 18, "sensor_pct": 24, "ajuste": 6, "error": 3, "modelo": "lineal",
}

MOCK_HUECO = "MOCK data: real values pending (engine not connected yet)"

MOCK_ESTRATEGIAS = [
    {
        "id": "actual", "es_actual": True, "ciclos": ["frijol", "frijol", "frijol"],
        "semaforo": "rojo", "puntaje": 41,
        "resiliencia": {"anios_ok": 33, "anios_total": 42, "rango": [30, 35]},
        "peor_anio": {"anio": 2011, "motivo": "rain 45% below average"},
        "porque": "Repeating the same crop family every cycle (MOCK).",
        "beneficios": ["Known crop, known market (MOCK)"],
        "huecos": [MOCK_HUECO, "We don't know the seed cost in your area"],
        "riesgos": ["Review soil disease build-up with an agronomist (MOCK)"],
        "fuentes": ["NASA POWER PRECTOTCORR", "MOCK"],
    },
    {
        "id": "alt1", "es_actual": False, "ciclos": ["frijol", "avena", "maiz"],
        "semaforo": "verde", "puntaje": 78,
        "resiliencia": {"anios_ok": 39, "anios_total": 42, "rango": [37, 40]},
        "peor_anio": {"anio": 2011, "motivo": "rain 45% below average"},
        "porque": "Rotates families and alternates water demand (MOCK).",
        "beneficios": ["Breaks the bean disease cycle (MOCK)"],
        "huecos": [MOCK_HUECO],
        "riesgos": ["Check oat frost window with an agronomist (MOCK)"],
        "fuentes": ["NASA POWER PRECTOTCORR", "NASA POWER T2M_MIN", "MOCK"],
    },
    {
        "id": "alt2", "es_actual": False, "ciclos": ["sorgo", "frijol", "avena"],
        "semaforo": "verde", "puntaje": 72,
        "resiliencia": {"anios_ok": 38, "anios_total": 42, "rango": [36, 40]},
        "peor_anio": {"anio": 1999, "motivo": "frost inside the crop window"},
        "porque": "Sorghum handles dry years better (MOCK).",
        "beneficios": ["Lower water need in the first cycle (MOCK)"],
        "huecos": [MOCK_HUECO],
        "riesgos": ["Confirm sorghum market price locally (MOCK)"],
        "fuentes": ["NASA POWER PRECTOTCORR", "MOCK"],
    },
    {
        "id": "alt3", "es_actual": False, "ciclos": ["alfalfa", "alfalfa", "maiz"],
        "semaforo": "amarillo", "puntaje": 60,
        "resiliencia": {"anios_ok": 36, "anios_total": 42, "rango": [33, 38]},
        "peor_anio": {"anio": 2011, "motivo": "rain 45% below average"},
        "porque": "Legume improves soil, but needs more water (MOCK).",
        "beneficios": ["Adds nitrogen to the soil (MOCK)"],
        "huecos": [MOCK_HUECO],
        "riesgos": ["High water demand in dry years (MOCK)"],
        "fuentes": ["NASA POWER PRECTOTCORR", "MOCK"],
    },
]


def mock_respuesta(cultivos_previos: Optional[List[str]] = None) -> Dict:
    estrategias = copy.deepcopy(MOCK_ESTRATEGIAS)
    if cultivos_previos:
        # "current" rotation = keep repeating the farmer's last crop
        estrategias[0]["ciclos"] = [cultivos_previos[-1]] * 3
    return {
        "estrategias": estrategias,
        "sensor": copy.deepcopy(MOCK_SENSOR),
        "calibracion": copy.deepcopy(MOCK_CALIBRACION),
    }


# ---------- Endpoints ----------
@app.get("/")
def salud():
    return {"ok": True, "service": "RotaHalcón API", "mock": MOCK_MODE}


@app.post("/recomendar")
def recomendar(datos: RecomendarIn):
    return mock_respuesta(datos.cultivos_previos)


@app.get("/anio-malo")
def anio_malo(
    anio: int = Query(2011, ge=1981),
    lat: float = DEFAULT_LAT,
    lon: float = DEFAULT_LON,
):
    resp = mock_respuesta()
    for e in resp["estrategias"]:
        e["resiliencia"] = {"anios_ok": 0 if e["es_actual"] else 1, "anios_total": 1, "rango": [0, 1]}
        e["peor_anio"] = {"anio": anio, "motivo": e["peor_anio"]["motivo"]}
    return resp


@app.post("/preguntar")
def preguntar(datos: PreguntarIn):
    # Owned by Rol 3 (IA). Mock so Web can wire the chat UI.
    return {
        "respuesta": "MOCK answer: the assistant is not connected yet.",
        "fuentes": ["MOCK"],
    }
