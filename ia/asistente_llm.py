"""
RotaHalcón — Grounded assistant, LLM mode (Claude API).

Claude answers free-form farmer questions using ONLY the recommendation JSON.
If the key is missing, the API fails, or Claude declines, we fall back to the
template assistant (asistente.responder), so the chat never breaks.
"""
import json
import os

import anthropic
from dotenv import load_dotenv

from asistente import responder as responder_plantilla, AVISO, compactar, resumen_para_llm, detectar_idioma

# ── DATOS ──────────────────────────────────────────────────────────────
load_dotenv()                                   # reads ia/.env (git-ignored): ANTHROPIC_API_KEY=...
MODELO = os.getenv("ROTAHALCON_MODELO", "claude-opus-5-5")
ESFUERZO = os.getenv("ROTAHALCON_ESFUERZO", "low")   # chat: low is fast and enough
MAX_TOKENS = 2000
TIMEOUT_S = 30.0
# ───────────────────────────────────────────────────────────────────────

from prompt import SISTEMA, ESQUEMA   # shared grounding rules

_cliente: anthropic.Anthropic | None = None


def _get_cliente() -> anthropic.Anthropic | None:
    global _cliente
    if _cliente is None and os.getenv("ANTHROPIC_API_KEY"):
        _cliente = anthropic.Anthropic(timeout=TIMEOUT_S, max_retries=1)
    return _cliente


def _plantilla(pregunta: str, rec: dict, idioma: str, motivo: str) -> dict:
    r = responder_plantilla(pregunta, rec, idioma)
    r["motivo_plantilla"] = motivo
    return r


def responder(pregunta: str, recomendacion: dict, idioma: str | None = None) -> dict:
    """Return {"respuesta", "fuentes", "modo": "llm"|"plantilla"}."""
    idioma = idioma if idioma in ("en", "es") else detectar_idioma(pregunta)
    cliente = _get_cliente()
    if cliente is None:
        return _plantilla(pregunta, recomendacion, idioma, "no_api_key")

    nombre_idioma = "English" if idioma == "en" else "Spanish (Mexico)"
    contenido = (
        f"RECOMMENDATION DATA:\n{resumen_para_llm(recomendacion)}\n\n"
        f"Reply in: {nombre_idioma}\n\nFarmer's question: {pregunta}"
    )
    try:
        resp = cliente.beta.messages.create(
            model=MODELO,
            max_tokens=MAX_TOKENS,
            system=SISTEMA,
            messages=[{"role": "user", "content": contenido}],
            output_config={"effort": ESFUERZO, "format": {"type": "json_schema", "schema": ESQUEMA}},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
    except anthropic.AuthenticationError:
        return _plantilla(pregunta, recomendacion, idioma, "api_key_invalida")
    except anthropic.RateLimitError:
        return _plantilla(pregunta, recomendacion, idioma, "rate_limit")
    except anthropic.APIStatusError as e:
        return _plantilla(pregunta, recomendacion, idioma, f"api_error_{e.status_code}")
    except anthropic.APIConnectionError:
        return _plantilla(pregunta, recomendacion, idioma, "sin_conexion")

    if resp.stop_reason in ("refusal", "max_tokens"):
        return _plantilla(pregunta, recomendacion, idioma, resp.stop_reason)
    try:
        texto = next(b.text for b in resp.content if b.type == "text")
        datos = json.loads(texto)
    except (StopIteration, json.JSONDecodeError):
        return _plantilla(pregunta, recomendacion, idioma, "respuesta_invalida")

    respuesta = datos["respuesta"].strip()
    if AVISO[idioma] not in respuesta:
        respuesta = f"{respuesta} {AVISO[idioma]}"
    return {"respuesta": respuesta, "fuentes": datos["fuentes"], "modo": "llm"}
