"""
RotaHalcón — Spanish version of the engine's English texts (for the farmer chat).

The backend writes porque / beneficios / riesgos / huecos / motivo in English
(deliverables rule). For answers in Spanish we translate the known sentence
patterns here. Unknown text is returned unchanged (never guessed).
Patterns mirror backend/engine.py — if the engine wording changes, update here.
"""
import copy
import re

# ── DATOS ──────────────────────────────────────────────────────────────
CULTIVOS = {"bean": "frijol", "maize": "maíz", "corn": "maíz", "oats": "avena", "oat": "avena",
            "sorghum": "sorgo", "alfalfa": "alfalfa"}
CLASES_N = {"VERY LOW": "MUY BAJO", "LOW": "BAJO", "MEDIUM": "MEDIO", "HIGH": "ALTO", "VERY HIGH": "MUY ALTO"}
MESES = {"January": "enero", "February": "febrero", "March": "marzo", "April": "abril", "May": "mayo",
         "June": "junio", "July": "julio", "August": "agosto", "September": "septiembre",
         "October": "octubre", "November": "noviembre", "December": "diciembre",
         "Jan": "ene", "Feb": "feb", "Mar": "mar", "Apr": "abr", "Jun": "jun", "Jul": "jul",
         "Aug": "ago", "Sep": "sep", "Oct": "oct", "Nov": "nov", "Dec": "dic"}
EXACTOS = {
    "Climate data is from the example field in Durango, not from your exact location.":
        "Los datos de clima son de la parcela de ejemplo en Durango, no de tu ubicación exacta.",
    "No live soil N reading from the field sensor yet: the soil score does not use N.":
        "Todavía no hay lectura de nitrógeno del sensor: el puntaje de suelo no usa N.",
    "Rainfed sowing dates for Durango (INIFAP Campo Experimental Valle del Guadiana) were not found online":
        "No encontramos en línea las fechas de siembra de temporal para Durango (INIFAP, Campo Experimental Valle del Guadiana)",
    "FAO cycle lengths are global ranges; local varieties (e.g. Pinto Saltillo bean) may differ":
        "Las duraciones de ciclo de la FAO son rangos globales; las variedades locales (p. ej. frijol Pinto Saltillo) pueden variar",
    "No sourced seed cost or crop price for Durango":
        "No tenemos con fuente el costo de semilla ni el precio de venta en Durango",
    "Oats is not listed in FAO-56 Table 24 (seasonal Ky)":
        "La avena no aparece en la Tabla 24 de FAO-56 (Ky estacional)",
    "Alfalfa is not listed in FAO frost Table 4.5":
        "La alfalfa no aparece en la Tabla 4.5 de heladas de la FAO",
}
# ───────────────────────────────────────────────────────────────────────


def _c(nombre: str) -> str:
    return CULTIVOS.get(nombre.lower(), nombre)


def _clase(c: str) -> str:
    return CLASES_N.get(c.strip().upper(), c)


PATRONES = [
    (r"Would have failed (\d+) of (\d+) seasons \((\d{4})–(\d{4})\): (\d+) by drought, (\d+) by frost\.",
     lambda m: f"Habría fallado {m[1]} de {m[2]} temporadas ({m[3]}–{m[4]}): {m[5]} por sequía, {m[6]} por helada."),
    (r"drought: (\w+) got (\d+)% of the water it needs(?:, expected yield loss (\d+)%)? \(rain ([+-]?\d+)% vs normal\)",
     lambda m: f"sequía: el {_c(m[1])} recibió {m[2]}% del agua que necesita"
               + (f", pérdida de cosecha esperada {m[3]}%" if m[3] else "") + f" (lluvia {m[4]}% vs lo normal)"),
    (r"frost (-?[\d.]+) °C on (\d+) (\w+) during (\w+) (\w+)",
     lambda m: f"helada de {m[1]} °C el {m[2]} de {MESES.get(m[3], m[3])} durante el {_c(m[4])} (etapa {m[5]})"),
    (r"no failure \((\w+): rain ([+-]?\d+)% vs normal\)",
     lambda m: f"sin falla ({_c(m[1])}: lluvia {m[2]}% vs lo normal)"),
    (r"(\w+) is a legume: it fixes nitrogen from the air \(FAO\)\.",
     lambda m: f"El {_c(m[1])} es leguminosa: fija nitrógeno del aire (FAO)."),
    (r"Alternates plant families \((.+?)\)\.",
     lambda m: f"Alterna familias de plantas ({m[1]})."),
    (r"Your soil N reads (.+?) \(([\d.]+) mg/kg, SENSOR; NOM-021 class\): the legume in this rotation adds nitrogen\.",
     lambda m: f"Tu suelo marca nitrógeno {_clase(m[1])} ({m[2]} mg/kg, SENSOR; clase NOM-021): "
               f"la leguminosa de esta rotación aporta nitrógeno."),
    (r"Your soil N reads (.+?) \(([\d.]+) mg/kg, SENSOR\) and this rotation has no legume: review fertilization with an agronomist\.",
     lambda m: f"Tu suelo marca nitrógeno {_clase(m[1])} ({m[2]} mg/kg, SENSOR) y esta rotación no tiene "
               f"leguminosa: revisa la fertilización con un agrónomo."),
    (r"Frost hit (\w+) in (\d+) of (\d+) seasons \(NASA T2M_MIN\): check the sowing date with an agronomist\.",
     lambda m: f"La helada afectó al {_c(m[1])} en {m[2]} de {m[3]} temporadas (NASA T2M_MIN): "
               f"revisa la fecha de siembra con un agrónomo."),
    (r"(\w+) lacked water in (\d+) of (\d+) seasons: review with an agronomist\.",
     lambda m: f"Al {_c(m[1])} le faltó agua en {m[2]} de {m[3]} temporadas: revísalo con un agrónomo."),
    (r"Repeats the (\w+) family in consecutive cycles: review pests and diseases with an agronomist\.",
     lambda m: f"Repite la familia {m[1]} en ciclos seguidos: revisa plagas y enfermedades con un agrónomo."),
    (r"Assumes rainfed sowing on (\d+) (\w+) and FAO global crop values: confirm with INIFAP or an agronomist\.",
     lambda m: f"Supone siembra de temporal el {m[1]} de {MESES.get(m[2], m[2])} y valores globales de la FAO: "
               f"confírmalo con el INIFAP o un agrónomo."),
    (r"In (\d{4}), (\d+) of (\d+) cycles would fail",
     lambda m: f"En {m[1]}, fallarían {m[2]} de {m[3]} ciclos"),
]
_COMPILADOS = [(re.compile(p), f) for p, f in PATRONES]


def traducir_es(texto: str) -> str:
    if not isinstance(texto, str):
        return texto
    if texto in EXACTOS:
        return EXACTOS[texto]
    out = texto
    for rx, fn in _COMPILADOS:
        out = rx.sub(fn, out)
    return out


def recomendacion_es(recomendacion: dict) -> dict:
    """Copy of the recommendation with the engine's texts in Spanish."""
    rec = copy.deepcopy(recomendacion)
    for e in rec.get("estrategias", []):
        if "porque" in e:
            e["porque"] = traducir_es(e["porque"])
        for k in ("beneficios", "riesgos", "huecos"):
            if isinstance(e.get(k), list):
                e[k] = [traducir_es(x) for x in e[k]]
        if isinstance(e.get("peor_anio"), dict) and "motivo" in e["peor_anio"]:
            e["peor_anio"]["motivo"] = traducir_es(e["peor_anio"]["motivo"])
    return rec
