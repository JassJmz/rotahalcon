"""
RotaHalcón — crop table loader and validator.

Source of truth (edit these, never the JSON):
    data/crops/crop_values.csv   one row per value, each with source_id + exact table/row
    data/crops/sources.csv       full citations (FAO, GBIF…)
    data/crops/gaps.csv          what is missing and why (shown to users as "huecos")

Rule A5: a value without a source does not enter. `validate()` enforces it.

Usage (from the repo root):
    python backend/crops.py      # validate + print table + write data/crops/crops.json

In code:
    from crops import load_crops
    crops = load_crops()          # dict by crop_id, ranges as [min, max]
"""

# ── DATOS ──
CROP_IDS = ["frijol", "maiz", "avena", "sorgo", "alfalfa"]
REQUIRED = [                       # every crop needs each one, or a row in gaps.csv
    "name_en", "scientific_name", "family", "fixes_nitrogen",
    "water_need_mm", "drought_sensitivity", "cycle_days",
    "frost_tc_germination", "frost_tc_flowering", "frost_tc_fruiting", "root_depth_m",
    "ky_seasonal",
]
RANGE_ATTRS = {"water_need_mm", "cycle_days", "frost_tc_germination",
               "frost_tc_flowering", "frost_tc_fruiting", "root_depth_m"}
# ── FIN DATOS ──

import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CROP_DIR = REPO_ROOT / "data" / "crops"


def _read(name: str) -> list[dict]:
    with (CROP_DIR / name).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _num(x: str) -> float | int:
    v = float(x)
    return int(v) if v.is_integer() else v


def validate() -> tuple[list[str], list[dict], dict, list[dict]]:
    """Return (errors, values, sources_by_id, gaps)."""
    sources = {s["source_id"]: s for s in _read("sources.csv")}
    values = _read("crop_values.csv")
    gaps = _read("gaps.csv")
    errors = []

    seen = set()
    for i, r in enumerate(values, start=2):  # line 1 = header
        where = f"crop_values.csv line {i} ({r['crop_id']}.{r['attribute']})"
        if r["crop_id"] not in CROP_IDS:
            errors.append(f"{where}: unknown crop_id")
        if not r["source_id"]:
            errors.append(f"{where}: NO SOURCE — value not allowed (rule A5)")
        elif r["source_id"] not in sources:
            errors.append(f"{where}: source_id '{r['source_id']}' not in sources.csv")
        if not r["where_in_source"]:
            errors.append(f"{where}: missing where_in_source (table/row/page)")
        if r["attribute"] in RANGE_ATTRS:
            try:
                lo, hi = _num(r["value_min"]), _num(r["value_max"])
                if lo > hi:
                    errors.append(f"{where}: value_min > value_max")
            except ValueError:
                errors.append(f"{where}: range needs numeric value_min and value_max")
        elif not r["value"]:
            errors.append(f"{where}: empty value")
        key = (r["crop_id"], r["attribute"])
        if key in seen:
            errors.append(f"{where}: duplicated")
        seen.add(key)

    def in_gaps(crop, attr):
        for g in gaps:
            crop_ok = g["crop_id"] in (crop, "*")
            a = g["attribute"]
            attr_ok = a == attr or (a.endswith("*") and attr.startswith(a[:-1]))
            if crop_ok and attr_ok:
                return True
        return False

    for c in CROP_IDS:
        for a in REQUIRED:
            if (c, a) not in seen and not in_gaps(c, a):
                errors.append(f"{c}.{a}: missing and not declared in gaps.csv")
    return errors, values, sources, gaps


def build(values: list[dict], sources: dict, gaps: list[dict]) -> dict:
    crops = {c: {"id": c, "values": {}, "gaps": []} for c in CROP_IDS}
    for r in values:
        s = sources[r["source_id"]]
        if r["attribute"] in RANGE_ATTRS:
            val = [_num(r["value_min"]), _num(r["value_max"])]
        elif r["value"] in ("true", "false"):
            val = r["value"] == "true"
        elif r["attribute"] == "ky_seasonal":
            val = _num(r["value"])
        else:
            val = r["value"]
        crops[r["crop_id"]]["values"][r["attribute"]] = {
            "value": val,
            "unit": r["unit"] or None,
            "source": f"{s['short']}, {r['where_in_source']}",
            "source_id": r["source_id"],
            "note": r["note"] or None,
        }
    for g in gaps:
        targets = CROP_IDS if g["crop_id"] == "*" else [g["crop_id"]]
        for c in targets:
            crops[c]["gaps"].append({k: g[k] for k in ("attribute", "status", "detail", "next_step")})
    return {
        "crops": crops,
        "sources": {k: {"citation": v["citation"], "url": v["url"], "accessed": v["accessed"]}
                    for k, v in sources.items()},
        "rule": "Every value has a source (FAO / GBIF). Missing values are listed in 'gaps', never invented.",
    }


def load_crops() -> dict:
    """Validated crop table for the engine. Raises if any value lacks a source."""
    errors, values, sources, gaps = validate()
    if errors:
        raise ValueError("Crop table invalid:\n  " + "\n  ".join(errors))
    return build(values, sources, gaps)["crops"]


def load_soils() -> dict:
    """Soil water table (FAO-56 Table 19) by soil_id. Raises if a row has no source."""
    sources = {s["source_id"]: s for s in _read("sources.csv")}
    soils = {}
    for r in _read("soils.csv"):
        if r["source_id"] not in sources or not r["where_in_source"]:
            raise ValueError(f"soils.csv: '{r['soil_id']}' has no valid source (rule A5)")
        s = sources[r["source_id"]]
        soils[r["soil_id"]] = {
            "name_en": r["name_en"],
            "taw_m3m3": [_num(r["taw_min"]), _num(r["taw_max"])],
            "source": f"{s['short']}, {r['where_in_source']}",
        }
    return soils


def load_sources() -> dict:
    return {s["source_id"]: s for s in _read("sources.csv")}


def _fmt(v: dict | None) -> str:
    if v is None:
        return "— gap —"
    x = v["value"]
    if isinstance(x, list):
        return f"{x[0]} – {x[1]}"
    if isinstance(x, bool):
        return "yes" if x else "no"
    return str(x)


def main() -> None:
    errors, values, sources, gaps = validate()
    if errors:
        print("✗ Crop table INVALID:")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    data = build(values, sources, gaps)
    out = CROP_DIR / "crops.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    cols = [("Crop", 15, "name_en"), ("Family", 10, "family"), ("Fixes N", 8, "fixes_nitrogen"),
            ("Water mm", 11, "water_need_mm"), ("Drought", 12, "drought_sensitivity"),
            ("Cycle d", 10, "cycle_days"), ("Frost flower °C", 15, "frost_tc_flowering")]
    print("  ".join(h.ljust(w) for h, w, _ in cols))
    print("  ".join("─" * w for _, w, _ in cols))
    for c, d in data["crops"].items():
        print("  ".join(_fmt(d["values"].get(a)).ljust(w) for _, w, a in cols))
    n_gaps = sum(len(d["gaps"]) for d in data["crops"].values())
    print(f"\n✓ {len(values)} values, all sourced ({len(sources)} sources). "
          f"{n_gaps} gaps declared. → {out.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    main()
