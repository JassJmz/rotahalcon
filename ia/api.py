"""
RotaHalcón — AI service. Endpoint: POST /preguntar (see docs/CONTRACT.md).

Run:   .venv/bin/uvicorn api:app --reload --port 8001
Docs:  http://localhost:8001/docs
"""
import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from asistente_llm import responder   # LLM mode; falls back to templates automatically

# ── DATOS ──────────────────────────────────────────────────────────────
ORIGENES_PERMITIDOS = ["*"]                 # hackathon: open CORS so the web can call us
MOCK_PATH = Path(__file__).with_name("mock_recomendacion.json")
# ───────────────────────────────────────────────────────────────────────

app = FastAPI(title="RotaHalcón AI", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=ORIGENES_PERMITIDOS,
                   allow_methods=["*"], allow_headers=["*"])


class Pregunta(BaseModel):
    pregunta: str
    recomendacion: dict | None = None   # backend /recomendar output; mock if missing
    idioma: str | None = None           # optional: "en" | "es"


@app.get("/salud")
def salud():
    import os
    return {"ok": True, "servicio": "ia", "llm": bool(os.getenv("ANTHROPIC_API_KEY"))}


@app.post("/preguntar")
def preguntar(p: Pregunta):
    rec = p.recomendacion or json.loads(MOCK_PATH.read_text())
    return responder(p.pregunta, rec, p.idioma)
