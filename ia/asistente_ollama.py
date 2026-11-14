"""
RotaHalcón — Grounded assistant, local LLM mode (Ollama).

Free, offline, no API key: a small model running on the laptop answers
free-form farmer questions using ONLY the recommendation JSON.
If Ollama is not running or the answer is invalid, we fall back to templates.
"""
import json
import os

import httpx
from dotenv import load_dotenv

from asistente import responder as responder_plantilla, AVISO, compactar, resumen_para_llm, detectar_idioma
from prompt import SISTEMA, ESQUEMA   # same grounding rules as the Claude mode

# ── DATOS ──────────────────────────────────────────────────────────────
load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODELO = os.getenv("OLLAMA_MODELO", "qwen2.5:7b")
TIMEOUT_S = float(os.getenv("OLLAMA_TIMEOUT", "60"))
TEMPERATURA = 0.2            # low = sticks to the data
# ───────────────────────────────────────────────────────────────────────


def _plantilla(pregunta: str, rec: dict, idioma: str, motivo: str) -> dict:
    r = responder_plantilla(pregunta, rec, idioma)
    r["motivo_plantilla"] = motivo
    return r


def disponible() -> bool:
    try:
        return httpx.get(f"{OLLAMA_URL}/api/version", timeout=2).status_code == 200
    except httpx.HTTPError:
        return False


def responder(pregunta: str, recomendacion: dict, idioma: str | None = None) -> dict:
    """Return {"respuesta", "fuentes", "modo": "ollama"|"plantilla"}."""
    idioma = idioma if idioma in ("en", "es") else detectar_idioma(pregunta)
    nombre_idioma = "English" if idioma == "en" else "Spanish (Mexico)"
    contenido = (
        f"RECOMMENDATION DATA:\n{resumen_para_llm(recomendacion)}\n\n"
        f"Reply in: {nombre_idioma}\n\nFarmer's question: {pregunta}"
    )
    cuerpo = {
        "model": OLLAMA_MODELO,
        "messages": [{"role": "system", "content": SISTEMA},
                     {"role": "user", "content": contenido}],
        "format": ESQUEMA,                       # Ollama structured output (JSON schema)
        "stream": False,
        "options": {"temperature": TEMPERATURA, "num_ctx": 8192},
    }
    try:
        r = httpx.post(f"{OLLAMA_URL}/api/chat", json=cuerpo, timeout=TIMEOUT_S)
        r.raise_for_status()
        datos = json.loads(r.json()["message"]["content"])
        respuesta = str(datos["respuesta"]).strip()
        fuentes = [str(f) for f in datos.get("fuentes", [])]
    except httpx.ConnectError:
        return _plantilla(pregunta, recomendacion, idioma, "ollama_apagado")
    except httpx.TimeoutException:
        return _plantilla(pregunta, recomendacion, idioma, "ollama_timeout")
    except (httpx.HTTPError, KeyError, ValueError):
        return _plantilla(pregunta, recomendacion, idioma, "respuesta_invalida")

    if not respuesta:
        return _plantilla(pregunta, recomendacion, idioma, "respuesta_vacia")
    if AVISO[idioma] not in respuesta:
        respuesta = f"{respuesta} {AVISO[idioma]}"
    return {"respuesta": respuesta, "fuentes": fuentes, "modo": "ollama"}
