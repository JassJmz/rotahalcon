"""
RotaHalcón — AI routes as a FastAPI router, so the public backend can serve them too.

    # backend/main.py
    sys.path.append(".../ia")
    from rutas import router as ia_router
    app.include_router(ia_router)          # adds POST /preguntar and GET /glosario

Works with only fastapi + pydantic installed (Render): if Ollama / httpx / dotenv
are missing or Ollama is not running, /preguntar answers in template mode.
On the demo laptop (Ollama running) the same code answers with the local LLM.
"""
import json
import os
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

import asistente

try:                                    # optional: local LLM (needs httpx; Ollama running)
    import asistente_ollama
except ImportError:
    asistente_ollama = None
try:                                    # optional: Claude API (needs anthropic + key)
    import asistente_llm
except ImportError:
    asistente_llm = None

# ── DATOS ──────────────────────────────────────────────────────────────
PROVEEDOR = os.getenv("ROTAHALCON_PROVEEDOR", "ollama")   # "ollama" | "claude" | "plantilla"
HIBRIDO = os.getenv("ROTAHALCON_HIBRIDO", "true").lower() == "true"
CARPETA = Path(__file__).resolve().parent
MOCK_PATH = CARPETA / "mock_recomendacion.json"           # real /recomendar snapshot
GLOSARIO_PATH = CARPETA / "glosario.json"
# ───────────────────────────────────────────────────────────────────────

router = APIRouter(tags=["ia"])


class Pregunta(BaseModel):
    pregunta: str
    recomendacion: dict | None = None   # /recomendar output; snapshot if missing
    idioma: str | None = None           # "en" | "es"


def _responder_llm():
    if PROVEEDOR == "ollama" and asistente_ollama is not None:
        return asistente_ollama.responder
    if PROVEEDOR == "claude" and asistente_llm is not None:
        return asistente_llm.responder
    return None


def info() -> dict:
    """Status for health endpoints."""
    return {
        "proveedor": PROVEEDOR,
        "hibrido": HIBRIDO,
        "ollama_instalado": asistente_ollama is not None,
        "ollama": bool(asistente_ollama and asistente_ollama.disponible()),
        "ollama_modelo": getattr(asistente_ollama, "OLLAMA_MODELO", None),
        "claude_key": bool(os.getenv("ANTHROPIC_API_KEY")),
    }


@router.post("/preguntar")
def preguntar(p: Pregunta):
    """Grounded assistant. Known questions → exact template answer; free-form →
    local LLM (Ollama) when available, else template. Never invents numbers."""
    rec = p.recomendacion or json.loads(MOCK_PATH.read_text(encoding="utf-8"))
    llm = _responder_llm()
    if llm is None or (HIBRIDO and asistente._intencion(p.pregunta) != "desconocida"):
        return asistente.responder(p.pregunta, rec, p.idioma)
    return llm(p.pregunta, rec, p.idioma)


@router.get("/glosario")
def glosario(idioma: str = "en"):
    """Plain-language glossary for the web tooltips. ?idioma=en|es"""
    idioma = idioma if idioma in ("en", "es") else "en"
    datos = json.loads(GLOSARIO_PATH.read_text(encoding="utf-8"))
    return [{"id": t["id"], **t[idioma], "fuente": t["fuente"]} for t in datos["terminos"]]
