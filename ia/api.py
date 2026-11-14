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

# ── DATOS ──────────────────────────────────────────────────────────────
load_dotenv()
PROVEEDOR = os.getenv("ROTAHALCON_PROVEEDOR", "ollama")   # "ollama" (free, local) | "claude" | "plantilla"
ORIGENES_PERMITIDOS = ["*"]                               # hackathon: open CORS so the web can call us
MOCK_PATH = Path(__file__).with_name("mock_recomendacion.json")
# ───────────────────────────────────────────────────────────────────────

RESPONDEDORES = {
    "ollama": asistente_ollama.responder,
    "claude": asistente_llm.responder,
    "plantilla": asistente.responder,
}

app = FastAPI(title="RotaHalcón AI", version="0.3.0")
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
        "ollama": asistente_ollama.disponible(),
        "ollama_modelo": asistente_ollama.OLLAMA_MODELO,
        "claude_key": bool(os.getenv("ANTHROPIC_API_KEY")),
    }


@app.post("/preguntar")
def preguntar(p: Pregunta):
    rec = p.recomendacion or json.loads(MOCK_PATH.read_text())
    responder = RESPONDEDORES.get(PROVEEDOR, asistente.responder)
    return responder(p.pregunta, rec, p.idioma)
