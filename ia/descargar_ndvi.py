"""
RotaHalcón — Download the MODIS NDVI time series for the example field.

Source: NASA MODIS Terra MOD13Q1 v061 (250 m, 16-day composites), served by the
ORNL DAAC MODIS Web Service (public, no login): https://modis.ornl.gov/data/modis_webservice.html
Bands: 250m_16_days_NDVI (scale 0.0001) + 250m_16_days_pixel_reliability
(0 good, 1 marginal, 2 snow/ice, 3 cloudy, -1 no data).

Run once:  .venv/bin/python descargar_ndvi.py      → ia/datos/ndvi_durango.csv
"""
import csv
import json
import time
from pathlib import Path

import httpx

# ── DATOS ──────────────────────────────────────────────────────────────
LAT, LON = 24.02, -104.65                      # same example field as NASA POWER
PRODUCTO = "MOD13Q1"
BANDA_NDVI = "250m_16_days_NDVI"
BANDA_CALIDAD = "250m_16_days_pixel_reliability"
API = "https://modis.ornl.gov/rst/api/v1"
FECHAS_POR_PETICION = 10                       # service limit
DESDE = "2016-01-01"                           # last ~10 years (the service is slow: ~40 s per request)
REINTENTOS = 25                                # the service is often busy (502/503)
SALIDA = Path(__file__).resolve().parent / "datos" / "ndvi_durango.csv"
CACHE = Path(__file__).resolve().parent / "datos" / "ndvi_cache.json"   # resume after failures
# ───────────────────────────────────────────────────────────────────────

cliente = httpx.Client(timeout=120, headers={"Accept": "application/json"})


def _get(url: str, params: dict) -> dict:
    for i in range(REINTENTOS):
        try:
            r = cliente.get(url, params=params)
            if r.status_code == 200:
                return r.json()
        except (httpx.HTTPError, ValueError):
            pass
        time.sleep(min(60, 10 * (i + 1)))      # back off, max 1 min
    raise RuntimeError(f"MODIS service failed after {REINTENTOS} tries: {params}")


def fechas() -> list[dict]:
    return _get(f"{API}/{PRODUCTO}/dates", {"latitude": LAT, "longitude": LON})["dates"]


def banda(nombre: str, inicio: str, fin: str) -> dict[str, float]:
    d = _get(f"{API}/{PRODUCTO}/subset", {
        "latitude": LAT, "longitude": LON, "band": nombre,
        "startDate": inicio, "endDate": fin, "kmAboveBelow": 0, "kmLeftRight": 0})
    return {s["calendar_date"]: s["data"][0] for s in d["subset"]}


def main():
    SALIDA.parent.mkdir(exist_ok=True)
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    todas = cache.get("_fechas") or fechas()
    cache["_fechas"] = todas
    todas = [f for f in todas if f["calendar_date"] >= DESDE]
    filas = {}
    for i in range(0, len(todas), FECHAS_POR_PETICION):
        bloque = todas[i:i + FECHAS_POR_PETICION]
        ini, fin = bloque[0]["modis_date"], bloque[-1]["modis_date"]
        clave = f"{ini}-{fin}"
        if clave not in cache:
            cache[clave] = {"ndvi": banda(BANDA_NDVI, ini, fin), "cal": banda(BANDA_CALIDAD, ini, fin)}
            CACHE.write_text(json.dumps(cache))
        ndvi, cal = cache[clave]["ndvi"], cache[clave]["cal"]
        for f in bloque:
            c = f["calendar_date"]
            v = ndvi.get(c)
            filas[c] = {"fecha": c,
                        "ndvi": round(v * 0.0001, 4) if v is not None and v > -3000 else "",
                        "calidad": cal.get(c, "")}
        print(f"{min(i + FECHAS_POR_PETICION, len(todas))}/{len(todas)} dates", flush=True)
    with SALIDA.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["fecha", "ndvi", "calidad"])
        w.writeheader()
        w.writerows(filas[k] for k in sorted(filas))
    print(f"saved {len(filas)} rows → {SALIDA}")


if __name__ == "__main__":
    main()
