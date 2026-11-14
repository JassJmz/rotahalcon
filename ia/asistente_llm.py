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

from asistente import responder as responder_plantilla, AVISO

# ── DATOS ──────────────────────────────────────────────────────────────
load_dotenv()                                   # reads ia/.env (git-ignored): ANTHROPIC_API_KEY=...
MODELO = os.getenv("ROTAHALCON_MODELO", "claude-opus-5-5")
ESFUERZO = os.getenv("ROTAHALCON_ESFUERZO", "low")   # chat: low is fast and enough
MAX_TOKENS = 2000
TIMEOUT_S = 30.0
# ───────────────────────────────────────────────────────────────────────

SISTEMA = """You are the assistant inside RotaHalcón, a crop-rotation decision-support tool for small farmers in Durango, Mexico.

You receive a RECOMMENDATION JSON produced by our engine. It contains rotation strategies (the farmer's current one, flagged es_actual, plus alternatives) simulated against NASA POWER climate since 1981, the latest in-field soil SENSOR reading, and a satellite-vs-sensor calibration.

How to answer:
- Use only facts present in the JSON. Never introduce agronomic numbers, prices, yields, dates or crop requirements that are not in it.
- If the answer is not in the JSON, say plainly that you don't have that data and suggest confirming with a local agronomist.
- Speak to a farmer: short, plain words, no jargon. Two to five sentences.
- When you cite a number, say where it comes from: NASA (climate/satellite) or SENSOR (field reading). Treat sensor values as indicative, not lab results.
- Compare against the farmer's current rotation when it helps.
- The tool supports the farmer's decision; it does not replace their judgment or an agronomist's.
- Reply in the language requested.

Return the answer text and the list of sources you actually used, copied from the JSON's "fuentes" fields or written as "NASA POWER" / "SENSOR"."""

ESQUEMA = {
    "type": "object",
    "properties": {
        "respuesta": {"type": "string"},
        "fuentes": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["respuesta", "fuentes"],
    "additionalProperties": False,
}

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
    idioma = idioma if idioma in ("en", "es") else "en"
    cliente = _get_cliente()
    if cliente is None:
        return _plantilla(pregunta, recomendacion, idioma, "no_api_key")

    nombre_idioma = "English" if idioma == "en" else "Spanish (Mexico)"
    contenido = (
        f"RECOMMENDATION JSON:\n{json.dumps(recomendacion, ensure_ascii=False, sort_keys=True)}\n\n"
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
