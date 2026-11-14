"""
RotaHalcón — Uncertainty of the resilience score (bootstrap over years).

Instead of a single "works in 37 of 42 years", we report a range:
"works in 37 of 42 years (range 33–40)". We resample the simulated years
with replacement many times and take percentiles of the number of OK years.
Pure Python, no extra dependencies.
"""
import random

# ── DATOS ──────────────────────────────────────────────────────────────
N_REMUESTREOS = 2000        # bootstrap resamples
PERCENTILES = (5, 95)       # 90% interval
SEMILLA = 42                # fixed seed = same range every run (stable demo)
# ───────────────────────────────────────────────────────────────────────


def _percentil(valores_ordenados: list[int], p: float) -> int:
    k = (len(valores_ordenados) - 1) * p / 100
    return valores_ordenados[round(k)]


def rango_resiliencia(resultados: list[bool], n: int = N_REMUESTREOS,
                      percentiles: tuple[int, int] = PERCENTILES,
                      semilla: int = SEMILLA) -> dict:
    """resultados: one bool per simulated year (True = rotation did OK that year).

    Returns {"anios_ok", "anios_total", "rango": [lo, hi], "metodo"}.
    """
    total = len(resultados)
    ok = sum(1 for r in resultados if r)
    if total == 0:
        return {"anios_ok": 0, "anios_total": 0, "rango": [0, 0], "metodo": "bootstrap"}
    rng = random.Random(semilla)
    conteos = sorted(sum(rng.choices(resultados, k=total)) for _ in range(n))
    lo, hi = (_percentil(conteos, p) for p in percentiles)
    return {"anios_ok": ok, "anios_total": total, "rango": [lo, hi],
            "metodo": f"bootstrap n={n}, p{percentiles[0]}–p{percentiles[1]}"}


def agregar_incertidumbre(recomendacion: dict) -> dict:
    """Fill estrategia["resiliencia"] (incl. "rango") for every strategy that
    carries per-year results in estrategia["anios"] = [{"anio": 1981, "ok": true}, ...].
    Strategies without "anios" are left untouched."""
    for e in recomendacion.get("estrategias", []):
        anios = e.get("anios")
        if anios:
            e["resiliencia"] = rango_resiliencia([bool(a.get("ok")) for a in anios])
    return recomendacion


if __name__ == "__main__":
    # Quick demo with made-up years (NOT real results): 37 OK out of 42.
    demo = [True] * 37 + [False] * 5
    print(rango_resiliencia(demo))
