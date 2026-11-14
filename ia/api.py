"""
RotaHalcón — AI service. Endpoint: POST /preguntar (see docs/CONTRACT.md).

Run:   .venv/bin/uvicorn api:app --reload --port 8001
Docs:  http://localhost:8001/docs
"""
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import asistente
import asistente_llm
import asistente_ollama
import incertidumbre

# ── DATOS ──────────────────────────────────────────────────────────────
load_dotenv()
PROVEEDOR = os.getenv("ROTAHALCON_PROVEEDOR", "ollama")   # "ollama" (free, local) | "claude" | "plantilla"
# Hybrid: questions the templates recognize get the exact template answer (always correct);
# only free-form questions go to the LLM. Recommended with the small local model.
HIBRIDO = os.getenv("ROTAHALCON_HIBRIDO", "true").lower() == "true"
ORIGENES_PERMITIDOS = ["*"]                               # hackathon: open CORS so the web can call us
MOCK_PATH = Path(__file__).with_name("mock_recomendacion.json")
GLOSARIO_PATH = Path(__file__).with_name("glosario.json")
# ───────────────────────────────────────────────────────────────────────

RESPONDEDORES = {
    "ollama": asistente_ollama.responder,
    "claude": asistente_llm.responder,
    "plantilla": asistente.responder,
}

app = FastAPI(title="RotaHalcón AI", version="0.5.0")
app.add_middleware(CORSMiddleware, allow_origins=ORIGENES_PERMITIDOS,
                   allow_methods=["*"], allow_headers=["*"])


class Pregunta(BaseModel):
    pregunta: str
    recomendacion: dict | None = None   # backend /recomendar output; mock if missing
    idioma: str | None = None           # optional: "en" | "es"


@app.get("/salud")
def salud():
    return {
        "ok": True,
        "servicio": "ia",
        "proveedor": PROVEEDOR,
        "hibrido": HIBRIDO,
        "ollama": asistente_ollama.disponible(),
        "ollama_modelo": asistente_ollama.OLLAMA_MODELO,
        "claude_key": bool(os.getenv("ANTHROPIC_API_KEY")),
    }


@app.post("/preguntar")
def preguntar(p: Pregunta):
    rec = p.recomendacion or json.loads(MOCK_PATH.read_text())
    if HIBRIDO and PROVEEDOR != "plantilla" and asistente._intencion(p.pregunta) != "desconocida":
        return asistente.responder(p.pregunta, rec, p.idioma)
    responder = RESPONDEDORES.get(PROVEEDOR, asistente.responder)
    return responder(p.pregunta, rec, p.idioma)


@app.post("/incertidumbre")
def calcular_incertidumbre(recomendacion: dict):
    """Backend sends its /recomendar output with per-year results in each strategy
    (estrategia["anios"] = [{"anio": 1981, "ok": true}, ...]); we fill resiliencia.rango."""
    return incertidumbre.agregar_incertidumbre(recomendacion)


@app.get("/glosario")
def glosario(idioma: str = "en"):
    """Plain-language glossary for the web tooltips. ?idioma=en|es"""
    idioma = idioma if idioma in ("en", "es") else "en"
    datos = json.loads(GLOSARIO_PATH.read_text(encoding="utf-8"))
    return [{"id": t["id"], **t[idioma], "fuente": t["fuente"]} for t in datos["terminos"]]
