"""
RotaHalcón — Satellite ↔ sensor soil-moisture calibration.

NASA POWER GWETTOP = surface soil wetness, 0 (dry) … 1 (saturated), ~50 km cell.
Field sensor (capacitive, two-point calibrated: dry air = 0 %, water = 100 %)
gives the same idea — relative wetness 0–100 % — but for THIS field.

We learn how the field differs from the satellite cell and compare two models:
  1) linear regression (statistics)   2) random forest (machine learning)
scored with leave-one-out cross-validation (honest with few days of data).

  ≥ MIN_DIAS distinct days with both values → "regresion" mode (models compared)
  fewer days                                → "diferencia" mode (simple offset)
  no readings at all                        → EXAMPLE data, always labeled as such

STATUS: the node's moisture probe is the next hardware module. Until it is
connected, outputs come from EXAMPLE readings and say so ("datos": "ejemplo").
"""
import csv
import random
import statistics
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# ── DATOS ──────────────────────────────────────────────────────────────
NASA_CSV = Path(__file__).resolve().parent.parent / "data" / "nasa_power" / "durango_daily.csv"
MIN_DIAS = 5                 # distinct days needed to fit models
N_ARBOLES = 200              # random forest size
SEMILLA = 42
# Example generator (synthetic, ONLY for demonstrating the method):
EJEMPLO_DIAS = 30
EJEMPLO_PENDIENTE = 0.85     # hypothetical: field = 0.85 × satellite + 12 points
EJEMPLO_OFFSET = 12.0
EJEMPLO_RUIDO = 2.5          # ± noise, percentage points
# ───────────────────────────────────────────────────────────────────────


def cargar_nasa(path: Path = NASA_CSV) -> dict[date, float]:
    """{day: GWETTOP × 100} from the backend's NASA POWER download."""
    serie: dict[date, float] = {}
    with path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            v = r.get("GWETTOP")
            if v not in (None, "", "-999", "-999.0"):
                serie[date.fromisoformat(r["date"])] = float(v) * 100
    return serie


def _dia(lectura: dict) -> date:
    if "fecha" in lectura:
        return date.fromisoformat(str(lectura["fecha"])[:10])
    return datetime.fromtimestamp(float(lectura["ts"]), tz=timezone.utc).date()


def lecturas_ejemplo(nasa: dict[date, float], dias: int = EJEMPLO_DIAS) -> list[dict]:
    """Synthetic sensor readings built from real NASA days + a hypothetical field
    relation + noise. FOR DEMONSTRATION ONLY — never present as field data."""
    rng = random.Random(SEMILLA)
    ultimos = sorted(nasa)[-dias:]
    out = []
    for d in ultimos:
        v = EJEMPLO_PENDIENTE * nasa[d] + EJEMPLO_OFFSET + rng.uniform(-EJEMPLO_RUIDO, EJEMPLO_RUIDO)
        out.append({"fecha": d.isoformat(), "humedad_pct": round(min(100.0, max(0.0, v)), 1)})
    return out


def _pares(lecturas: list[dict], nasa: dict[date, float]) -> list[tuple[date, float, float]]:
    """Daily mean of sensor readings joined with the same NASA day."""
    por_dia: dict[date, list[float]] = {}
    for l in lecturas:
        h = l.get("humedad_pct")
        if h is None:
            continue
        por_dia.setdefault(_dia(l), []).append(float(h))
    return [(d, nasa[d], statistics.fmean(v)) for d, v in sorted(por_dia.items()) if d in nasa]


def _loo_mae(modelo_factory, X, y) -> float:
    errores = []
    for i in range(len(X)):
        m = modelo_factory()
        m.fit([x for j, x in enumerate(X) if j != i], [v for j, v in enumerate(y) if j != i])
        errores.append(abs(m.predict([X[i]])[0] - y[i]))
    return statistics.fmean(errores)


def calibrar(lecturas: list[dict] | None = None) -> dict:
    """Return the `calibracion` block for /recomendar (docs/CONTRACT.md) + details.

    lecturas: [{"ts": unix_seconds | "fecha": "YYYY-MM-DD", "humedad_pct": 0–100}, ...]
    """
    nasa = cargar_nasa()
    ultimo_dia_nasa = max(nasa)
    satelite_hoy = round(nasa[ultimo_dia_nasa], 1)

    datos = "sensor"
    if not lecturas or all(l.get("humedad_pct") is None for l in lecturas):
        lecturas, datos = lecturas_ejemplo(nasa), "ejemplo"

    pares = _pares(lecturas, nasa)
    validas = [l for l in lecturas if l.get("humedad_pct") is not None]
    sensor_ultimo = round(float(sorted(validas, key=_dia)[-1]["humedad_pct"]), 1)
    base = {
        "satelite_pct": satelite_hoy,
        "satelite_fecha": ultimo_dia_nasa.isoformat(),
        "sensor_pct": sensor_ultimo,
        "datos": datos,
        "n_dias": len(pares),
        "fuentes": ["NASA POWER GWETTOP", "SENSOR humedad_pct" if datos == "sensor" else "EXAMPLE readings (synthetic)"],
    }
    if datos == "ejemplo":
        base["aviso"] = ("EXAMPLE DATA: synthetic sensor readings used to demonstrate the method. "
                         "The node's moisture probe is the next hardware module.")

    # ── Mode 1: not enough days → simple difference against NASA ──
    if len(pares) < MIN_DIAS:
        # Compare against the latest NASA day available (NASA lags ~3 days)
        ajuste = round(sensor_ultimo - satelite_hoy, 1)
        return {**base, "modo": "diferencia", "ajuste": ajuste, "error": None,
                "modelo": "difference (needs ≥ %d days for regression)" % MIN_DIAS,
                "comparacion": []}

    # ── Mode 2: regression, linear vs random forest (leave-one-out) ──
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LinearRegression

    X = [[s] for _, s, _ in pares]
    y = [f for _, _, f in pares]
    candidatos = {
        "lineal": lambda: LinearRegression(),
        "random_forest": lambda: RandomForestRegressor(n_estimators=N_ARBOLES, random_state=SEMILLA, min_samples_leaf=2),
    }
    comparacion = [{"modelo": n, "mae": round(_loo_mae(f, X, y), 2)} for n, f in candidatos.items()]
    mejor = min(comparacion, key=lambda c: c["mae"])
    modelo = candidatos[mejor["modelo"]]()
    modelo.fit(X, y)
    corregido = float(modelo.predict([[satelite_hoy]])[0])

    detalle = {}
    if mejor["modelo"] == "lineal":
        detalle = {"pendiente": round(float(modelo.coef_[0]), 3), "intercepto": round(float(modelo.intercept_), 2)}

    return {**base, "modo": "regresion",
            "satelite_corregido_pct": round(corregido, 1),
            "ajuste": round(corregido - satelite_hoy, 1),
            "error": mejor["mae"],
            "modelo": mejor["modelo"],
            "comparacion": comparacion,
            **detalle}


if __name__ == "__main__":
    import json
    print(json.dumps(calibrar(), indent=1, ensure_ascii=False))
