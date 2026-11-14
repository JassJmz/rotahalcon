"""
RotaHalcón — Grounded assistant (template mode).

Answers farmer questions using ONLY the data inside the recommendation JSON
(backend /recomendar output). It never produces agronomic numbers of its own.
This is also the fallback (plan B) when the LLM is unavailable.
"""

# ── DATOS ──────────────────────────────────────────────────────────────
IDIOMA_POR_DEFECTO = "en"          # "en" (judges / UI) or "es" (farmer)
AVISO = {
    "en": "This is decision support — confirm with an agronomist before deciding.",
    "es": "Esto es apoyo a la decisión: confírmalo con un agrónomo antes de decidir.",
}
SIN_DATO = {
    "en": "I don't have that data. Please confirm it with a local agronomist.",
    "es": "No tengo ese dato. Confírmalo con un agrónomo de tu zona.",
}
# Keywords that route a question to an answer type (lowercase, no accents needed)
INTENCIONES = {
    "peor":    ["worst", "bad year", "peor", "año malo", "anio malo", "sequia", "drought"],
    "porque":  ["why", "por que", "porque", "por qué", "razon", "reason"],
    "mejor":   ["best", "recommend", "mejor", "recomienda", "conviene", "que siembro", "what should"],
    "actual":  ["current", "mine", "my rotation", "actual", "mi rotacion", "la mia", "lo de siempre"],
    "suelo":   ["soil", "sensor", "nitrogen", "suelo", "nitrogeno", "humedad", "moisture", "ph"],
    "riesgo":  ["risk", "riesgo", "danger", "peligro", "frost", "helada"],
    "calibra": ["satellite", "satelite", "nasa", "calibra", "accurate", "precision"],
}
# ───────────────────────────────────────────────────────────────────────


def compactar(recomendacion: dict) -> dict:
    """Copy of the recommendation without the per-year lists (anios), which are
    long and only needed for the bootstrap. Keeps the LLM prompt small."""
    rec = {k: v for k, v in recomendacion.items() if not k.startswith("_")}
    rec["estrategias"] = [{k: v for k, v in e.items() if k != "anios"}
                          for e in recomendacion.get("estrategias", [])]
    return rec


def _normaliza(texto: str) -> str:
    tabla = str.maketrans("áéíóúñü", "aeiounu")
    return texto.lower().translate(tabla)


def _intencion(pregunta: str) -> str:
    p = _normaliza(pregunta)
    for nombre, claves in INTENCIONES.items():
        if any(_normaliza(c) in p for c in claves):
            return nombre
    return "desconocida"


def _ciclos(e: dict) -> str:
    return " → ".join(e.get("ciclos", []))


def _res(e: dict, idioma: str) -> str:
    r = e.get("resiliencia") or {}
    ok, tot, rango = r.get("anios_ok"), r.get("anios_total"), r.get("rango")
    if ok is None or tot is None:
        return ""
    fallas = tot - ok
    if idioma == "es":
        txt = f"funciona en {ok} de {tot} años (falla {fallas})"
        if rango:
            txt += f", rango {rango[0]}–{rango[1]}"
    else:
        txt = f"works in {ok} of {tot} years (fails {fallas})"
        if rango:
            txt += f", range {rango[0]}–{rango[1]}"
    return txt


def responder(pregunta: str, recomendacion: dict, idioma: str | None = None) -> dict:
    """Return {"respuesta": str, "fuentes": [str], "modo": "plantilla"}."""
    idioma = idioma if idioma in ("en", "es") else IDIOMA_POR_DEFECTO
    es = idioma == "es"
    estrategias = recomendacion.get("estrategias") or []
    if not estrategias:
        return {"respuesta": SIN_DATO[idioma], "fuentes": [], "modo": "plantilla"}

    actual = next((e for e in estrategias if e.get("es_actual")), None)
    mejor = max(estrategias, key=lambda e: e.get("puntaje", 0))
    sensor = recomendacion.get("sensor") or {}
    cal = recomendacion.get("calibracion") or {}
    fuentes: list[str] = []
    intencion = _intencion(pregunta)

    if intencion == "mejor":
        r = (f"La mejor opción para tus prioridades es {_ciclos(mejor)}: {_res(mejor, idioma)}. {mejor.get('porque', '')}"
             if es else
             f"The best option for your priorities is {_ciclos(mejor)}: {_res(mejor, idioma)}. {mejor.get('porque', '')}")
        fuentes = mejor.get("fuentes", [])

    elif intencion == "actual" and actual:
        r = (f"Tu rotación actual ({_ciclos(actual)}) {_res(actual, idioma)}. {actual.get('porque', '')}"
             if es else
             f"Your current rotation ({_ciclos(actual)}) {_res(actual, idioma)}. {actual.get('porque', '')}")
        if actual is not mejor:
            r += (f" En comparación, {_ciclos(mejor)} {_res(mejor, idioma)}."
                  if es else f" By comparison, {_ciclos(mejor)} {_res(mejor, idioma)}.")
        fuentes = actual.get("fuentes", [])

    elif intencion == "peor":
        pa = mejor.get("peor_anio") or {}
        if pa:
            r = (f"El peor año para {_ciclos(mejor)} fue {pa.get('anio')}: {pa.get('motivo', '')}."
                 if es else
                 f"The worst year for {_ciclos(mejor)} was {pa.get('anio')}: {pa.get('motivo', '')}.")
            if actual and actual is not mejor and actual.get("peor_anio"):
                pa2 = actual["peor_anio"]
                r += (f" Para tu rotación actual fue {pa2.get('anio')}: {pa2.get('motivo', '')}."
                      if es else f" For your current rotation it was {pa2.get('anio')}: {pa2.get('motivo', '')}.")
            fuentes = ["NASA POWER"]
        else:
            r = SIN_DATO[idioma]

    elif intencion == "porque":
        r = (f"Recomendamos {_ciclos(mejor)} porque: {mejor.get('porque', '')}"
             if es else f"We recommend {_ciclos(mejor)} because: {mejor.get('porque', '')}")
        ben = mejor.get("beneficios") or []
        if ben:
            r += (" Beneficios: " if es else " Benefits: ") + "; ".join(ben) + "."
        fuentes = mejor.get("fuentes", [])

    elif intencion == "riesgo":
        riesgos = mejor.get("riesgos") or []
        huecos = mejor.get("huecos") or []
        if riesgos or huecos:
            r = (f"Para {_ciclos(mejor)}, revisa con un agrónomo: " if es
                 else f"For {_ciclos(mejor)}, check with an agronomist: ") + "; ".join(riesgos) + "."
            if huecos:
                r += (" Lo que no sabemos: " if es else " What we don't know: ") + "; ".join(huecos) + "."
            fuentes = mejor.get("fuentes", [])
        else:
            r = SIN_DATO[idioma]

    elif intencion == "suelo" and sensor:
        campos = [("humedad_pct", "moisture", "humedad", "%"), ("n_mgkg", "N", "N", " mg/kg"),
                  ("p_mgkg", "P", "P", " mg/kg"), ("k_mgkg", "K", "K", " mg/kg"),
                  ("ph", "pH", "pH", ""), ("ce_uScm", "EC", "CE", " µS/cm")]
        partes = [f"{(es_n if es else en_n)} {sensor[k]}{u}" for k, en_n, es_n, u in campos if k in sensor]
        r = ("Lectura del sensor en tu parcela: " if es else "Sensor reading in your field: ") + ", ".join(partes) + "."
        r += (" Es una lectura indicativa, no un análisis de laboratorio." if es
              else " It is an indicative reading, not a lab analysis.")
        fuentes = ["SENSOR"]

    elif intencion == "calibra" and cal:
        r = (f"El satélite estima {cal.get('satelite_pct')}% de humedad y tu sensor mide {cal.get('sensor_pct')}%. "
             f"Ajustamos la simulación {cal.get('ajuste'):+} puntos (error ±{cal.get('error')}, modelo {cal.get('modelo')})."
             if es else
             f"The satellite estimates {cal.get('satelite_pct')}% moisture and your sensor reads {cal.get('sensor_pct')}%. "
             f"We adjust the simulation by {cal.get('ajuste'):+} points (error ±{cal.get('error')}, {cal.get('modelo')} model).")
        fuentes = ["NASA POWER", "SENSOR"]

    else:
        r = SIN_DATO[idioma]

    return {"respuesta": f"{r.strip()} {AVISO[idioma]}", "fuentes": fuentes, "modo": "plantilla"}
