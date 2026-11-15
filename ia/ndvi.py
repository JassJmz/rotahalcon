"""
RotaHalcón — What NASA MODIS NDVI says about the example field.

1. Annual cycle: median NDVI per calendar month (2000 → today).
2. Bare-soil months: the lowest third of the field's OWN annual cycle
   (relative to this field — no fixed NDVI threshold invented).
3. Anomalous drops: 16-day composites far below the normal for that month
   (z-score vs same-month history).
4. Cross-check with NASA POWER: growing-season NDVI vs rainy-season rain,
   year by year — do the satellites agree on the bad years?

Only pixels with MODIS reliability 0 (good) or 1 (marginal) are used.
Pure Python (stdlib) so the public backend can serve it too.
"""
import csv
import statistics
from datetime import date
from pathlib import Path

# ── DATOS ──────────────────────────────────────────────────────────────
CARPETA = Path(__file__).resolve().parent
NDVI_CSV = CARPETA / "datos" / "ndvi_durango.csv"
POWER_MENSUAL = CARPETA.parent / "data" / "nasa_power" / "durango_monthly.csv"
CALIDAD_OK = {"0", "1"}                  # MODIS pixel reliability: good, marginal
Z_CAIDA = -1.5                           # composite this many std below its month = anomalous drop
MESES_LLUVIA = (6, 7, 8, 9)              # rainy season rain (Jun–Sep)
MESES_TEMPORADA = (8, 9, 10)             # growing-season NDVI (Aug–Oct, greening lags the rain)
MAX_CAIDAS = 8
NOMBRES_MES = {"en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
               "es": ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]}
# ───────────────────────────────────────────────────────────────────────


def cargar() -> list[tuple[date, float]]:
    serie = []
    with NDVI_CSV.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["ndvi"] != "" and str(r["calidad"]) in CALIDAD_OK:
                serie.append((date.fromisoformat(r["fecha"]), float(r["ndvi"])))
    return serie


def _lluvia_temporada() -> dict[int, float]:
    por_anio: dict[int, float] = {}
    with POWER_MENSUAL.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if int(r["month"]) in MESES_LLUVIA and r["PRECTOTCORR_sum_mm"] not in ("", None):
                por_anio[int(r["year"])] = por_anio.get(int(r["year"]), 0.0) + float(r["PRECTOTCORR_sum_mm"])
    return por_anio


def _pearson(x: list[float], y: list[float]) -> float | None:
    if len(x) < 5:
        return None
    mx, my = statistics.fmean(x), statistics.fmean(y)
    sx = sum((a - mx) ** 2 for a in x) ** 0.5
    sy = sum((b - my) ** 2 for b in y) ** 0.5
    return round(sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy), 2) if sx and sy else None


def analizar(idioma: str = "en") -> dict:
    idioma = idioma if idioma in ("en", "es") else "en"
    serie = cargar()
    por_mes: dict[int, list[float]] = {m: [] for m in range(1, 13)}
    for d, v in serie:
        por_mes[d.month].append(v)

    # 1. annual cycle
    ciclo = [{"mes": m, "nombre": NOMBRES_MES[idioma][m - 1],
              "ndvi_mediana": round(statistics.median(v), 3) if v else None, "n": len(v)}
             for m, v in por_mes.items()]

    # 2. bare-soil months = lowest third of this field's cycle
    validos = sorted((c for c in ciclo if c["ndvi_mediana"] is not None), key=lambda c: c["ndvi_mediana"])
    desnudos = sorted(validos[:4], key=lambda c: c["mes"])

    # 3. anomalous drops vs same-month history
    stats_mes = {m: (statistics.fmean(v), statistics.pstdev(v)) for m, v in por_mes.items() if len(v) > 2}
    caidas = []
    for d, v in serie:
        media, sd = stats_mes.get(d.month, (None, 0))
        if media is not None and sd > 0:
            z = (v - media) / sd
            if z <= Z_CAIDA:
                caidas.append({"fecha": d.isoformat(), "ndvi": v, "normal": round(media, 3), "z": round(z, 2)})
    caidas.sort(key=lambda c: c["z"])

    # 4. growing season NDVI vs NASA POWER rain
    temporada: dict[int, list[float]] = {}
    for d, v in serie:
        if d.month in MESES_TEMPORADA:
            temporada.setdefault(d.year, []).append(v)
    lluvia = _lluvia_temporada()
    anios = sorted(a for a in temporada if a in lluvia and len(temporada[a]) >= 3)
    ndvi_anual = {a: statistics.fmean(temporada[a]) for a in anios}
    media_ndvi = statistics.fmean(ndvi_anual.values()) if ndvi_anual else None
    por_anio = [{"anio": a, "ndvi_temporada": round(ndvi_anual[a], 3),
                 "anomalia_pct": round(100 * (ndvi_anual[a] / media_ndvi - 1), 1),
                 "lluvia_jun_sep_mm": round(lluvia[a], 1)} for a in anios]
    peores = sorted(por_anio, key=lambda x: x["ndvi_temporada"])[:5]
    r = _pearson([ndvi_anual[a] for a in anios], [lluvia[a] for a in anios])

    nombres = ", ".join(c["nombre"] for c in desnudos)
    if idioma == "es":
        resumen = (f"Desde el satélite, los meses con suelo más desnudo en esta parcela son {nombres}: ahí conviene "
                   f"pensar en cubrir el suelo. Los años con la vegetación más baja en temporada fueron "
                   f"{', '.join(str(p['anio']) for p in peores[:3])}.")
        if r is not None:
            resumen += f" El verdor de temporada sigue a la lluvia de NASA POWER (correlación {r})."
    else:
        resumen = (f"From space, the barest-soil months at this field are {nombres}: that is when covering the "
                   f"soil matters most. The lowest growing-season vegetation years were "
                   f"{', '.join(str(p['anio']) for p in peores[:3])}.")
        if r is not None:
            resumen += f" Season greenness follows NASA POWER rainfall (correlation {r})."

    return {
        "resumen": resumen,
        "meses_suelo_desnudo": [{"mes": c["mes"], "nombre": c["nombre"], "ndvi_mediana": c["ndvi_mediana"]} for c in desnudos],
        "ciclo_mensual": ciclo,
        "caidas_anomalas": caidas[:MAX_CAIDAS],
        "temporada_por_anio": por_anio,
        "peores_anios": peores,
        "correlacion_ndvi_lluvia": r,
        "periodo": [serie[0][0].isoformat(), serie[-1][0].isoformat()] if serie else None,
        "n_compuestos": len(serie),
        "fuentes": ["NASA MODIS MOD13Q1 v061 NDVI (250 m, 16-day) via ORNL DAAC", "NASA POWER PRECTOTCORR"],
        "metodo": (f"Bare soil = lowest 4 months of this field's median annual NDVI cycle; drops = composites with "
                   f"z ≤ {Z_CAIDA} vs same-month history; season NDVI = mean Aug–Oct vs Jun–Sep rain. "
                   f"Only MODIS reliability 0–1 pixels."),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(analizar("es"), indent=1, ensure_ascii=False)[:3000])
