"""
RotaHalcón — NASA POWER climate downloader.

Downloads DAILY point data (community AG) from NASA POWER for one field,
1981 → today, and writes clean, documented files to data/nasa_power/:

    <site>_daily.csv       one row per day (NASA parameter names as columns)
    <site>_monthly.csv     monthly aggregates (for crop-window analysis)
    <site>_annual.csv      yearly summary + rain anomaly vs 1991–2020 normal
    <site>_metadata.json   source, exact request URL, units, notes, citation
    <site>_annual_rain.svg chart of annual rainfall (for web / pitch)

Usage (from the repo root):
    python backend/nasa_power.py              # download + build everything
    python backend/nasa_power.py --offline    # rebuild summaries from the saved daily CSV

Other modules can import `load_daily()` to read the saved CSV (no internet).
Only the Python standard library is used.
"""

# ── DATOS ──
SITE_ID = "durango"
SITE_NAME = "Durango, Mexico (example field)"
LAT, LON = 24.02, -104.65
START_DATE = "19810101"            # POWER daily data starts 1981-01-01
END_DATE = None                    # None = today (trailing days without data are trimmed)
COMMUNITY = "AG"
PARAMETERS = {                     # NASA name: (unit, short description)
    "PRECTOTCORR":       ("mm/day",      "Precipitation (bias corrected)"),
    "T2M":               ("°C",          "Air temperature at 2 m, daily mean"),
    "T2M_MAX":           ("°C",          "Air temperature at 2 m, daily max"),
    "T2M_MIN":           ("°C",          "Air temperature at 2 m, daily min"),
    "RH2M":              ("%",           "Relative humidity at 2 m"),
    "ALLSKY_SFC_SW_DWN": ("MJ/m²/day",   "All-sky surface shortwave radiation (from 1984)"),
    "GWETTOP":           ("0–1",         "Surface soil wetness (0–5 cm), fraction of saturation"),
    "GWETROOT":          ("0–1",         "Root-zone soil wetness (0–100 cm), fraction of saturation"),
    "GWETPROF":          ("0–1",         "Profile soil wetness (surface to bedrock), fraction of saturation"),
}
NORMAL_PERIOD = (1991, 2020)       # WMO standard climate normal
FROST_THRESHOLD_C = 0.0            # meteorological frost: T2M_MIN <= 0 °C
API_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
TIMEOUT_S = 180
RETRIES = 3
# ── FIN DATOS ──

import argparse
import csv
import json
import statistics
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "data" / "nasa_power"
FILL_VALUE = -999.0
CITATION = (
    "These data were obtained from the NASA Langley Research Center (LaRC) "
    "POWER Project funded through the NASA Earth Science/Applied Science Program."
)


def out_path(kind: str) -> Path:
    return OUT_DIR / f"{SITE_ID}_{kind}"


# ───────────────────────── download ─────────────────────────
def build_url(end: str) -> str:
    query = {
        "parameters": ",".join(PARAMETERS),
        "community": COMMUNITY,
        "longitude": LON,
        "latitude": LAT,
        "start": START_DATE,
        "end": end,
        "format": "JSON",
    }
    return f"{API_URL}?{urllib.parse.urlencode(query, safe=',')}"


def download() -> tuple[dict, str]:
    end = END_DATE or date.today().strftime("%Y%m%d")
    url = build_url(end)
    for attempt in range(1, RETRIES + 1):
        try:
            print(f"→ Requesting NASA POWER ({START_DATE}–{end}), attempt {attempt}…")
            with urllib.request.urlopen(url, timeout=TIMEOUT_S) as resp:
                return json.load(resp), url
        except Exception as exc:  # network errors at the venue are expected
            print(f"  ! {exc}")
            if attempt == RETRIES:
                raise SystemExit(
                    "NASA POWER did not respond. Use --offline with the saved CSV (Plan B)."
                )
            time.sleep(5 * attempt)


def to_rows(payload: dict) -> list[dict]:
    series = payload["properties"]["parameter"]
    missing = [p for p in PARAMETERS if p not in series]
    if missing:
        print(f"  ! Not returned by POWER (left empty): {', '.join(missing)}")
    days = sorted(next(iter(series.values())).keys())
    rows = []
    for d in days:
        dt = date(int(d[:4]), int(d[4:6]), int(d[6:]))
        row = {"date": dt.isoformat(), "year": dt.year, "month": dt.month,
               "day": dt.day, "doy": dt.timetuple().tm_yday}
        for p in PARAMETERS:
            v = series.get(p, {}).get(d)
            row[p] = None if v is None or v <= FILL_VALUE + 1e-6 else v
        rows.append(row)
    # trim trailing days with no data at all (POWER latency)
    while rows and all(rows[-1][p] is None for p in PARAMETERS):
        rows.pop()
    return rows


def write_daily(rows: list[dict]) -> None:
    with out_path("daily.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "year", "month", "day", "doy", *PARAMETERS])
        for r in rows:
            w.writerow([r["date"], r["year"], r["month"], r["day"], r["doy"],
                        *("" if r[p] is None else r[p] for p in PARAMETERS)])


# ───────────────────────── load (for the engine) ─────────────────────────
def load_daily(path: Path | None = None) -> list[dict]:
    """Read the saved daily CSV. Values are float or None (missing)."""
    path = path or out_path("daily.csv")
    with path.open(encoding="utf-8") as f:
        rows = []
        for r in csv.DictReader(f):
            row = {"date": r["date"], "year": int(r["year"]), "month": int(r["month"]),
                   "day": int(r["day"]), "doy": int(r["doy"])}
            for p in PARAMETERS:
                row[p] = float(r[p]) if r.get(p) not in (None, "") else None
            rows.append(row)
        return rows


# ───────────────────────── summaries ─────────────────────────
def _mean(values):
    v = [x for x in values if x is not None]
    return round(statistics.fmean(v), 2) if v else None


def _sum(values):
    v = [x for x in values if x is not None]
    return round(sum(v), 1) if v else None


def _min(values):
    v = [x for x in values if x is not None]
    return round(min(v), 2) if v else None


def _frost_days(values):
    return sum(1 for x in values if x is not None and x <= FROST_THRESHOLD_C)


def summarize(rows: list[dict], key) -> dict:
    groups = defaultdict(list)
    for r in rows:
        groups[key(r)].append(r)
    out = {}
    for k, g in sorted(groups.items()):
        col = lambda p: [r[p] for r in g]
        out[k] = {
            "days": len(g),
            "rain_missing_days": sum(1 for r in g if r["PRECTOTCORR"] is None),
            "PRECTOTCORR_sum_mm": _sum(col("PRECTOTCORR")),
            "T2M_mean_c": _mean(col("T2M")),
            "T2M_MAX_mean_c": _mean(col("T2M_MAX")),
            "T2M_MIN_mean_c": _mean(col("T2M_MIN")),
            "T2M_MIN_lowest_c": _min(col("T2M_MIN")),
            "frost_days": _frost_days(col("T2M_MIN")),
            "RH2M_mean_pct": _mean(col("RH2M")),
            "ALLSKY_SFC_SW_DWN_mean": _mean(col("ALLSKY_SFC_SW_DWN")),
            "GWETTOP_mean": _mean(col("GWETTOP")),
            "GWETROOT_mean": _mean(col("GWETROOT")),
        }
    return out


def write_csv(path: Path, key_cols: list[str], table: dict, extra=None) -> None:
    first = next(iter(table.values()))
    extra_cols = list(extra(next(iter(table)), first).keys()) if extra else []
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([*key_cols, *first.keys(), *extra_cols])
        for k, v in table.items():
            keys = k if isinstance(k, tuple) else (k,)
            ex = list(extra(k, v).values()) if extra else []
            w.writerow([*keys, *("" if x is None else x for x in v.values()),
                        *("" if x is None else x for x in ex)])


def build_annual(rows: list[dict]) -> tuple[dict, float | None]:
    annual = summarize(rows, key=lambda r: r["year"])
    for y, v in annual.items():
        full_len = 366 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 365
        v["complete"] = v["days"] == full_len and v["rain_missing_days"] == 0
    lo, hi = NORMAL_PERIOD
    normal_years = [v["PRECTOTCORR_sum_mm"] for y, v in annual.items()
                    if lo <= y <= hi and v["complete"]]
    normal = round(statistics.fmean(normal_years), 1) if len(normal_years) == hi - lo + 1 else None
    for v in annual.values():
        v["rain_anomaly_pct"] = (
            round(100 * (v["PRECTOTCORR_sum_mm"] - normal) / normal, 1)
            if normal and v["complete"] else None
        )
    return annual, normal


# ───────────────────────── chart ─────────────────────────
def write_svg(annual: dict, normal: float | None) -> None:
    years = [y for y, v in annual.items() if v["complete"]]
    rain = [annual[y]["PRECTOTCORR_sum_mm"] for y in years]
    worst = sorted(years, key=lambda y: annual[y]["PRECTOTCORR_sum_mm"])[:3]

    W, H = 960, 440
    ml, mr, mt, mb = 64, 24, 92, 56
    pw, ph = W - ml - mr, H - mt - mb
    top = max(rain) * 1.12
    step = 200 if top > 800 else 100
    ymax = step * (int(top // step) + 1)
    bw = pw / len(years)
    sy = lambda v: mt + ph - v / ymax * ph

    NAVY, GOLD, RED, INK, MUTED, GRID = "#0B1F3A", "#D4AF37", "#E5533D", "#F4F1E8", "#9AA8BD", "#1F3657"
    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
             f'font-family="Inter, Segoe UI, system-ui, sans-serif" role="img" '
             f'aria-label="Annual rainfall {years[0]}–{years[-1]}, NASA POWER">')
    s.append(f'<rect width="{W}" height="{H}" rx="16" fill="{NAVY}"/>')
    s.append(f'<text x="{ml}" y="40" fill="{INK}" font-size="22" font-weight="700">'
             f'Annual rainfall · {SITE_NAME.split(" (")[0]}</text>')
    s.append(f'<text x="{ml}" y="64" fill="{MUTED}" font-size="13">'
             f'{years[0]}–{years[-1]} · {LAT}°N, {abs(LON)}°W · PRECTOTCORR (mm/year)</text>')
    # source tag
    s.append(f'<rect x="{W - mr - 70}" y="24" width="70" height="26" rx="13" fill="none" stroke="{GOLD}"/>')
    s.append(f'<text x="{W - mr - 35}" y="42" fill="{GOLD}" font-size="12" font-weight="700" '
             f'text-anchor="middle" letter-spacing="1.5">NASA</text>')
    # grid + y labels
    for v in range(0, ymax + 1, step):
        y = sy(v)
        s.append(f'<line x1="{ml}" x2="{W - mr}" y1="{y:.1f}" y2="{y:.1f}" stroke="{GRID}"/>')
        s.append(f'<text x="{ml - 10}" y="{y + 4:.1f}" fill="{MUTED}" font-size="11" '
                 f'text-anchor="end">{v}</text>')
    # bars
    for i, (y, v) in enumerate(zip(years, rain)):
        x = ml + i * bw + bw * 0.15
        color = RED if y in worst else GOLD
        s.append(f'<rect x="{x:.1f}" y="{sy(v):.1f}" width="{bw * 0.7:.1f}" '
                 f'height="{mt + ph - sy(v):.1f}" rx="2" fill="{color}"><title>{y}: {v:.0f} mm</title></rect>')
        if y in worst:
            s.append(f'<text x="{x + bw * 0.35:.1f}" y="{sy(v) - 8:.1f}" fill="{RED}" font-size="11" '
                     f'font-weight="700" text-anchor="middle">{y}</text>')
        if y % 5 == 0:
            s.append(f'<text x="{x + bw * 0.35:.1f}" y="{mt + ph + 20}" fill="{MUTED}" font-size="11" '
                     f'text-anchor="middle">{y}</text>')
    # normal line
    if normal:
        y = sy(normal)
        s.append(f'<line x1="{ml}" x2="{W - mr}" y1="{y:.1f}" y2="{y:.1f}" stroke="{INK}" '
                 f'stroke-dasharray="6 5" stroke-width="1.5" opacity="0.8"/>')
        # legend in the header (keeps the plot area clean)
        lx = W - mr - 290
        s.append(f'<line x1="{lx}" x2="{lx + 28}" y1="60" y2="60" stroke="{INK}" '
                 f'stroke-dasharray="6 5" stroke-width="1.5"/>')
        s.append(f'<text x="{lx + 36}" y="64" fill="{INK}" font-size="12">'
                 f'1991–2020 normal · {normal:.0f} mm</text>')
        s.append(f'<rect x="{lx + 200}" y="53" width="12" height="12" rx="2" fill="{RED}"/>')
        s.append(f'<text x="{lx + 218}" y="64" fill="{INK}" font-size="12">Driest 3</text>')
    s.append(f'<text x="{ml}" y="{H - 16}" fill="{MUTED}" font-size="11">'
             f'Data: NASA LaRC POWER Project · daily, community AG · bias-corrected precipitation.</text>')
    s.append("</svg>")
    out_path("annual_rain.svg").write_text("\n".join(s), encoding="utf-8")


# ───────────────────────── metadata ─────────────────────────
def write_metadata(rows, annual, normal, url, payload_header, elevation) -> None:
    complete = [y for y, v in annual.items() if v["complete"]]
    meta = {
        "site": {"id": SITE_ID, "name": SITE_NAME, "lat": LAT, "lon": LON,
                 "elevation_m": elevation},
        "source": "NASA POWER (Prediction Of Worldwide Energy Resources), NASA LaRC",
        "label": "NASA",
        "temporal": "daily",
        "community": COMMUNITY,
        "request_url": url,
        "downloaded_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "period": {"first_day": rows[0]["date"], "last_day": rows[-1]["date"],
                   "complete_years": [complete[0], complete[-1]], "n_complete_years": len(complete)},
        "parameters": {p: {"unit": u, "description": d} for p, (u, d) in PARAMETERS.items()},
        "missing_values": {p: sum(1 for r in rows if r[p] is None) for p in PARAMETERS},
        "rain_normal_1991_2020_mm": normal,
        "fill_value_in_api": FILL_VALUE,
        "notes": [
            "Missing values are empty cells in the CSVs (API fill value -999 removed).",
            "ALLSKY_SFC_SW_DWN (radiation) is only available from 1984-01-01.",
            "GWETTOP/GWETROOT/GWETPROF are soil WETNESS as a fraction of saturation (0–1), "
            "not volumetric moisture %. Convert before comparing with the SENSOR reading.",
            "Satellite/model grid cell (~0.5° × 0.625°, MERRA-2): it represents the region, not the plot.",
            "Last days may be missing because of POWER data latency; they are trimmed.",
            f"frost_days = days with T2M_MIN <= {FROST_THRESHOLD_C} °C.",
        ],
        "api_header": payload_header,
        "citation": CITATION,
    }
    out_path("metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")


# ───────────────────────── main ─────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="rebuild summaries from the saved daily CSV")
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.offline:
        rows = load_daily()
        old = json.loads(out_path("metadata.json").read_text(encoding="utf-8"))
        url, header, elevation = old["request_url"], old.get("api_header"), old["site"]["elevation_m"]
        print(f"→ Offline: {len(rows)} days from {out_path('daily.csv').name}")
    else:
        payload, url = download()
        rows = to_rows(payload)
        header = payload.get("header")
        elevation = payload.get("geometry", {}).get("coordinates", [None, None, None])[2]
        write_daily(rows)

    monthly = summarize(rows, key=lambda r: (r["year"], r["month"]))
    write_csv(out_path("monthly.csv"), ["year", "month"], monthly)
    annual, normal = build_annual(rows)
    write_csv(out_path("annual.csv"), ["year"], annual)
    write_svg(annual, normal)
    write_metadata(rows, annual, normal, url, header, elevation)

    complete = [y for y, v in annual.items() if v["complete"]]
    driest = min(complete, key=lambda y: annual[y]["PRECTOTCORR_sum_mm"])
    print(f"✓ {len(rows)} days: {rows[0]['date']} → {rows[-1]['date']}")
    print(f"✓ {len(complete)} complete years ({complete[0]}–{complete[-1]}), "
          f"normal 1991–2020: {normal} mm/year")
    print(f"✓ Driest year: {driest} ({annual[driest]['PRECTOTCORR_sum_mm']} mm, "
          f"{annual[driest]['rain_anomaly_pct']}% vs normal)")
    print(f"✓ Files in {OUT_DIR.relative_to(REPO_ROOT)}/")


if __name__ == "__main__":
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    main()
