"""
RotaHalcón — rules engine + season-by-season simulation (1981 → last complete year).

For every crop and every past year it asks two questions, using real NASA data:
  1. WATER  — did the crop get the water it needs?
       supply = effective rain in the crop window (FAO formula on NASA PRECTOTCORR)
              + water stored in the root zone at sowing (FAO-56 soil & root values,
                scaled by how wet NASA GWETROOT says the soil was that year)
       need   = FAO seasonal crop water need
  2. FROST  — did air temperature (NASA T2M_MIN) reach the FAO critical damage
              temperature for the crop stage (germination / flowering / fruiting)?
A season FAILS if either answer is "no".

A rotation is 3 cycles (one rainfed crop per year, repeated). Its resilience is the
expected number of failed seasons over all simulated years (independent of which
cycle falls in which year). Then it is scored with the user's priorities.

Every model ASSUMPTION is in the DATOS block and is shown to users in "riesgos"/"huecos".
No agronomic number is written here: they all come from data/crops/ (with sources).
"""

# ── DATOS ──  (model assumptions, not agronomic values)
SOWING_MONTH, SOWING_DAY = 7, 1      # ASSUMPTION: rainfed sowing on 1 July (INIFAP date pending, gaps.csv)
PICK = {                             # which end of each FAO range the model uses
    "cycle_days": "min",             # FAO: short cycles → use the low end (local early varieties)
    "water_need_mm": "min",          # FAO TM3: "minimum value … when the growing period is short"
    "root_depth_m": "min",           # conservative: shallow roots store less water
    "taw_m3m3": "mid",               # soil available water: middle of the FAO range
    "frost": "warm",                 # warmer end of the critical range = conservative
}
STAGES = (("germination", 0.25), ("flowering", 0.75), ("fruiting", 1.0))  # share of cycle (approximation)
FAIL_YIELD_LOSS = 0.5                # ASSUMPTION: a season "fails" when expected yield loss >= 50 %
                                     # yield loss = Ky × (1 − water supply / need)   (FAO-33 via FAO-56 Table 24)
                                     # crops without a sourced Ky (oats): strict rule, fail if supply < need
SEMAFORO = {"verde": 0.90, "amarillo": 0.75}  # share of OK seasons for green / yellow, else red
SOIL_WEIGHTS = {"legume": 0.5, "family_change": 0.5}
NORMAL_PERIOD = (1991, 2020)
N_CYCLES = 3
N_ALTERNATIVES = 3
MIN_CROP_DIFF = 2                    # each alternative differs from the others in >= 2 of its 3 crops (variety)
NO_WORSE_THAN_CURRENT = True         # "do no harm": alternatives that fail MORE seasons than the
                                     # current rotation are only shown if nothing better exists
CONF_Z = 1.645                       # 90 % Wilson interval for the resilience range
SITE_MAX_DIST_DEG = 0.5              # farther than this from the data point → warn in "huecos"
DEFAULT_SOIL = "franco"
# ── FIN DATOS ──

import itertools
import math
from collections import Counter
import statistics
import unicodedata
from datetime import date, timedelta
from functools import lru_cache

import crops as crops_mod
import nasa_power

# ───────────────────────── data (loaded once) ─────────────────────────
CROPS = crops_mod.load_crops()
SOILS = crops_mod.load_soils()
SOURCES = crops_mod.load_sources()
CROP_IDS = list(CROPS)

_ROWS = nasa_power.load_daily()
_INDEX = {r["date"]: i for i, r in enumerate(_ROWS)}
_RAIN = [r["PRECTOTCORR"] for r in _ROWS]
_TMIN = [r["T2M_MIN"] for r in _ROWS]
_GWET = [r["GWETROOT"] for r in _ROWS]


def _complete_years() -> list[int]:
    counts = {}
    for r in _ROWS:
        if r["PRECTOTCORR"] is not None:
            counts[r["year"]] = counts.get(r["year"], 0) + 1
    full = lambda y: 366 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 365
    return [y for y, n in sorted(counts.items()) if n == full(y)]


YEARS = _complete_years()


def _pick(rng, mode):
    lo, hi = rng
    return {"min": lo, "max": hi, "mid": (lo + hi) / 2, "warm": max(lo, hi)}[mode]


def _val(crop_id, attr):
    v = CROPS[crop_id]["values"].get(attr)
    return None if v is None else v["value"]


def crop_name(crop_id) -> str:
    return _val(crop_id, "name_en").split(" (")[0]


def normalize_crop(name: str) -> str:
    s = unicodedata.normalize("NFKD", name.strip().lower())
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    if s not in CROPS:
        raise ValueError(f"Unknown crop '{name}'. Valid: {', '.join(CROP_IDS)}")
    return s


def normalize_soil(name: str) -> str:
    s = unicodedata.normalize("NFKD", (name or DEFAULT_SOIL).strip().lower().replace(" ", "_").replace("-", "_"))
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    if s not in SOILS:
        raise ValueError(f"Unknown soil '{name}'. Valid: {', '.join(SOILS)}")
    return s


def _window(year, crop_id):
    start = date(year, SOWING_MONTH, SOWING_DAY)
    i0 = _INDEX.get(start.isoformat())
    length = int(_pick(_val(crop_id, "cycle_days"), PICK["cycle_days"]))
    if i0 is None or i0 + length > len(_ROWS):
        return None
    return i0, length


# soil wetness at sowing, relative to its own history (0 = driest year, 1 = wettest)
_SOW_GWET = {y: _GWET[_INDEX[date(y, SOWING_MONTH, SOWING_DAY).isoformat()] - 1] for y in YEARS}
_GMIN, _GMAX = min(_SOW_GWET.values()), max(_SOW_GWET.values())


def _effective_rain(daily):
    """FAO TM3 ch.4: Pe = 0.8P-25 (P>75 mm/month) or 0.6P-10, on 30-day blocks, Pe >= 0."""
    total = 0.0
    for k in range(0, len(daily), 30):
        block = daily[k:k + 30]
        p_month = sum(block) * 30 / len(block)
        pe = 0.8 * p_month - 25 if p_month > 75 else 0.6 * p_month - 10
        total += max(0.0, pe) * len(block) / 30
    return total


@lru_cache(maxsize=None)
def _normal_rain(crop_id):
    vals = []
    for y in YEARS:
        if NORMAL_PERIOD[0] <= y <= NORMAL_PERIOD[1] and (w := _window(y, crop_id)):
            i0, n = w
            vals.append(sum(_RAIN[i0:i0 + n]))
    return statistics.fmean(vals)


@lru_cache(maxsize=None)
def evaluate(crop_id, year, soil_id, rain_pct=0.0, temp_c=0.0):
    """One crop, one season. Returns a dict with ok / cause / numbers for explanations."""
    w = _window(year, crop_id)
    if w is None:
        return None
    i0, n = w
    factor = 1 + rain_pct / 100
    rain = [x * factor for x in _RAIN[i0:i0 + n]]

    # water
    pe = _effective_rain(rain)
    taw = _pick(SOILS[soil_id]["taw_m3m3"], PICK["taw_m3m3"])
    zr = _pick(_val(crop_id, "root_depth_m"), PICK["root_depth_m"])
    wet = (_SOW_GWET[year] - _GMIN) / (_GMAX - _GMIN) if _GMAX > _GMIN else 0.5
    stored = taw * 1000 * zr * wet
    need = _pick(_val(crop_id, "water_need_mm"), PICK["water_need_mm"])
    ratio = (pe + stored) / need
    rain_anom = 100 * (sum(rain) - _normal_rain(crop_id)) / _normal_rain(crop_id)

    # frost (skipped when the crop has no sourced threshold → declared gap)
    frost = None
    thresholds = {s: _val(crop_id, f"frost_tc_{s}") for s, _ in STAGES}
    if all(thresholds.values()):
        for k in range(n):
            t = _TMIN[i0 + k]
            if t is None:
                continue
            t += temp_c
            frac = (k + 1) / n
            stage = next(s for s, cut in STAGES if frac <= cut)
            if t <= _pick(thresholds[stage], PICK["frost"]):
                frost = {"date": date(year, SOWING_MONTH, SOWING_DAY) + timedelta(days=k),
                         "tmin": round(t, 1), "stage": stage}
                break

    ky = _val(crop_id, "ky_seasonal")
    deficit = max(0.0, 1 - ratio)
    yield_loss = min(1.0, ky * deficit) if ky is not None else None
    water_ok = (yield_loss < FAIL_YIELD_LOSS) if ky is not None else ratio >= 1
    cause = None if water_ok and frost is None else ("frost" if frost else "drought")
    return {"crop": crop_id, "year": year, "ok": cause is None, "cause": cause,
            "water_ratio": round(ratio, 3), "supply_mm": round(pe + stored), "need_mm": need,
            "yield_loss": None if yield_loss is None else round(yield_loss, 3),
            "rain_mm": round(sum(rain)), "rain_anom_pct": round(rain_anom), "frost": frost}


def _motivo(e) -> str:
    name = crop_name(e["crop"])
    if e["cause"] == "frost":
        f = e["frost"]
        return f"frost {f['tmin']} °C on {f['date']:%d %b} during {name} {f['stage']}"
    if e["cause"] == "drought":
        loss = f", expected yield loss {e['yield_loss']:.0%}" if e["yield_loss"] is not None else ""
        return (f"drought: {name} got {e['water_ratio']:.0%} of the water it needs{loss} "
                f"(rain {e['rain_anom_pct']:+d}% vs normal)")
    return f"no failure ({name}: rain {e['rain_anom_pct']:+d}% vs normal)"


def _wilson(ok, n, z=CONF_Z):
    if n == 0:
        return [0, 0]
    p = ok / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [max(0, math.floor((c - h) * n)), min(n, math.ceil((c + h) * n))]


# ───────────────────────── rotation scoring ─────────────────────────
def simulate(ciclos, soil_id, rain_pct=0.0, temp_c=0.0):
    """Plant the rotation in order since the first year: year k grows ciclos[k % 3]."""
    seasons = []
    for k, y in enumerate(YEARS):
        e = evaluate(ciclos[k % len(ciclos)], y, soil_id, rain_pct, temp_c)
        if e:
            seasons.append(e)
    n = len(seasons)
    ok = sum(e["ok"] for e in seasons)
    fails_by = {"drought": sum(e["cause"] == "drought" for e in seasons),
                "frost": sum(e["cause"] == "frost" for e in seasons)}

    # climate risk of each crop over ALL years (phase independent, for texts and water score)
    crop_fails = {c: {"drought": 0, "frost": 0} for c in set(ciclos)}
    ratios = []
    for c in ciclos:
        for y in YEARS:
            e = evaluate(c, y, soil_id, rain_pct, temp_c)
            if e:
                ratios.append(min(1.0, e["water_ratio"]))
    for c in set(ciclos):
        for y in YEARS:
            e = evaluate(c, y, soil_id, rain_pct, temp_c)
            if e and not e["ok"]:
                crop_fails[c][e["cause"]] += 1

    failed = [e for e in seasons if not e["ok"]]
    worst = min(failed or seasons, key=lambda e: (e["cause"] != "frost", e["water_ratio"]))
    anios = []
    for e in seasons:
        item = {"anio": e["year"], "ok": e["ok"], "cultivo": e["crop"]}
        if not e["ok"]:
            item["motivo"] = _motivo(e)
        anios.append(item)
    return {
        "n": n, "ok": ok, "ok_share": ok / n,
        "rango": _wilson(ok, n),
        "peor_anio": {"anio": worst["year"], "motivo": _motivo(worst)},
        "fails_by": fails_by,
        "crop_fails": crop_fails,
        "water_score": 100 * statistics.fmean(ratios),
        "anios": anios,
    }


def soil_score(ciclos, previos):
    legume = sum(bool(_val(c, "fixes_nitrogen")) for c in ciclos) / len(ciclos)
    seq = ([previos[-1]] if previos else []) + list(ciclos) + [ciclos[0]]
    fams = [_val(c, "family") for c in seq]
    changes = sum(a != b for a, b in zip(fams, fams[1:])) / (len(fams) - 1)
    return 100 * (SOIL_WEIGHTS["legume"] * legume + SOIL_WEIGHTS["family_change"] * changes)


def _weights(prioridades):
    w = {k: max(0.0, float(prioridades.get(k, 0) or 0)) for k in ("agua", "suelo", "riesgo")}
    total = sum(w.values())
    return {k: v / total for k, v in w.items()} if total > 0 else {k: 1 / 3 for k in w}


def _semaforo(share):
    return "verde" if share >= SEMAFORO["verde"] else "amarillo" if share >= SEMAFORO["amarillo"] else "rojo"


def _texts(ciclos, sim, previos, site_far):
    names = [crop_name(c) for c in ciclos]
    total, fails = sim["n"], sim["n"] - sim["ok"]
    porque = (f"Would have failed {fails} of {total} seasons ({YEARS[0]}–{YEARS[-1]}): "
              f"{sim['fails_by']['drought']} by drought, {sim['fails_by']['frost']} by frost.")

    beneficios = []
    for c in dict.fromkeys(ciclos):
        if _val(c, "fixes_nitrogen"):
            beneficios.append(f"{crop_name(c).capitalize()} is a legume: it fixes nitrogen from the air (FAO).")
    fams = [_val(c, "family") for c in ciclos]
    if len(set(fams)) > 1:
        beneficios.append(f"Alternates plant families ({' / '.join(dict.fromkeys(fams))}).")
    if sim["fails_by"]["drought"] == 0:
        beneficios.append("Enough water in every simulated season (NASA rain + soil moisture).")

    riesgos = []
    for c, f in sim["crop_fails"].items():
        if f["frost"]:
            riesgos.append(f"Frost hit {crop_name(c)} in {f['frost']} of {total} seasons (NASA T2M_MIN): "
                           f"check the sowing date with an agronomist.")
        if f["drought"]:
            riesgos.append(f"{crop_name(c).capitalize()} lacked water in {f['drought']} of {total} seasons: "
                           f"review with an agronomist.")
    seq = ([previos[-1]] if previos else []) + list(ciclos)
    for a, b in zip(seq, seq[1:]):
        if _val(a, "family") == _val(b, "family"):
            riesgos.append(f"Repeats the {_val(a, 'family')} family in consecutive cycles: "
                           f"review pests and diseases with an agronomist.")
            break
    riesgos.append(f"Assumes rainfed sowing on {date(2000, SOWING_MONTH, SOWING_DAY):%d %B} and FAO global "
                   f"crop values: confirm with INIFAP or an agronomist.")

    huecos, seen = [], set()
    for c in ciclos:
        for g in CROPS[c]["gaps"]:
            text = g["detail"]
            if g["status"] == "group_value" or text in seen:
                continue
            if text not in seen:
                seen.add(text)
                huecos.append(text)
    if site_far:
        huecos.insert(0, "Climate data is from the example field in Durango, not from your exact location.")

    fuentes = ["NASA POWER PRECTOTCORR", "NASA POWER T2M_MIN", "NASA POWER GWETROOT"]
    used = {CROPS[c]["values"][a]["source_id"] for c in ciclos for a in CROPS[c]["values"]}
    used |= {"FAO_56", "FAO_TM3_PE"}
    fuentes += [SOURCES[s]["short"] for s in sorted(used) if s != "GBIF"]
    return porque, beneficios, huecos, riesgos, fuentes


def _strategy(id_, ciclos, sim, score, previos, site_far, es_actual):
    porque, beneficios, huecos, riesgos, fuentes = _texts(ciclos, sim, previos, site_far)
    return {
        "id": id_, "es_actual": es_actual, "ciclos": list(ciclos),
        "semaforo": _semaforo(sim["ok_share"]), "puntaje": round(score),
        "resiliencia": {"anios_ok": sim["ok"], "anios_total": sim["n"], "rango": sim["rango"]},
        "peor_anio": sim["peor_anio"],
        "porque": porque, "beneficios": beneficios, "huecos": huecos,
        "riesgos": riesgos, "fuentes": fuentes,
        "anios": sim["anios"],      # per-year results (Role 3 bootstrap, animation scene 7)
    }


def _site_far(lat, lon):
    meta_lat, meta_lon = nasa_power.LAT, nasa_power.LON
    return abs(lat - meta_lat) > SITE_MAX_DIST_DEG or abs(lon - meta_lon) > SITE_MAX_DIST_DEG


def recommend(lat, lon, suelo, cultivos_previos, prioridades, lluvia_pct=0.0, temp_c=0.0):
    """Current rotation + N best alternatives, in contract A4 format (estrategias list)."""
    soil = normalize_soil(suelo)
    previos = [normalize_crop(c) for c in (cultivos_previos or [])] or ["frijol"]
    actual = tuple(previos[i % len(previos)] for i in range(N_CYCLES))
    w = _weights(prioridades)
    far = _site_far(lat, lon)

    def score(ciclos):
        sim = simulate(ciclos, soil, lluvia_pct, temp_c)
        s = (w["agua"] * sim["water_score"] + w["suelo"] * soil_score(ciclos, previos)
             + w["riesgo"] * 100 * sim["ok_share"])
        return s, sim

    s_act, sim_act = score(actual)
    ranked = []
    for combo in itertools.product(CROP_IDS, repeat=N_CYCLES):
        if combo == actual:
            continue
        s, sim = score(combo)
        ranked.append((s, combo, sim))
    ranked.sort(key=lambda t: -t[0])

    def crop_diff(a, b):                    # how many crops of a are not in b (as multisets)
        return sum((Counter(a) - Counter(b)).values())

    act_fail = sim_act["n"] - sim_act["ok"]
    # passes, best first: (only rotations that fail <= current?, minimum crop difference)
    safe_first = [True, False] if NO_WORSE_THAN_CURRENT else [False]
    passes = [(safe, d) for safe in safe_first for d in sorted({MIN_CROP_DIFF, 1}, reverse=True)]
    picked = []
    for safe, min_diff in passes:
        for s, combo, sim in ranked:
            if len(picked) == N_ALTERNATIVES:
                break
            if safe and sim["n"] - sim["ok"] > act_fail:
                continue
            if any(crop_diff(combo, other) < min_diff for other in [p[1] for p in picked]):
                continue                     # too similar to an alternative already chosen
            if crop_diff(combo, actual) < 1 or any(combo == p[1] for p in picked):
                continue                     # same crops as the current rotation, in another order
            picked.append((s, combo, sim))
    picked.sort(key=lambda t: -t[0])

    out = [_strategy("actual", actual, sim_act, s_act, previos, far, True)]
    for k, (s, combo, sim) in enumerate(picked, start=1):
        out.append(_strategy(f"alt{k}", combo, sim, s, previos, far, False))
    return out


def bad_year(anio, lat, lon, suelo, cultivos_previos, prioridades, lluvia_pct=0.0, temp_c=0.0):
    """Same 4 strategies, evaluated only in one past year."""
    if anio not in YEARS:
        raise ValueError(f"Year must be between {YEARS[0]} and {YEARS[-1]}")
    soil = normalize_soil(suelo)
    strategies = recommend(lat, lon, suelo, cultivos_previos, prioridades, lluvia_pct, temp_c)
    for st in strategies:
        st.pop("anios", None)
        # "if a year like this came back": every cycle of the rotation faces it
        evs = [e for c in st["ciclos"] if (e := evaluate(c, anio, soil, lluvia_pct, temp_c))]
        frac = sum(not e["ok"] for e in evs) / len(evs)
        failed = [e for e in evs if not e["ok"]]
        worst = min(evs, key=lambda e: (e["ok"], e["water_ratio"]))
        st["semaforo"] = "verde" if frac == 0 else "amarillo" if frac < 0.5 else "rojo"
        st["resiliencia"] = {"anios_ok": 1 if frac == 0 else 0, "anios_total": 1,
                             "rango": [0 if frac > 0 else 1, 0 if frac == 1 else 1]}
        st["peor_anio"] = {"anio": anio, "motivo": _motivo(worst)}
        st["porque"] = (f"In {anio}, {len(failed)} of {len(evs)} cycles would fail"
                        + (f": {_motivo(worst)}." if failed else "."))
    return strategies
