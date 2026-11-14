# Data

Owner: Role 2. Every dataset here states its **source** and carries a **NASA** or **SENSOR** label.

| Folder / file | Content | Source | Label |
|---|---|---|---|
| [`nasa_power/`](nasa_power/) | Daily climate 1981 → today for the example field (Durango) | NASA POWER | **NASA** |
| [`crops/`](crops/) | Bean, maize, oats, sorghum, alfalfa: every value with its source | FAO / GBIF (INIFAP pending) | — |

---

## `nasa_power/` — Durango example field

![Annual rainfall 1981–2025, Durango (NASA POWER)](nasa_power/durango_annual_rain.svg)

**Location:** 24.02°N, 104.65°W · elevation 2,065 m · **Period:** 1981-01-01 → latest available day (45 complete years: 1981–2025).
**Request:** NASA POWER daily point API, community **AG**. The exact URL and download date are in `durango_metadata.json`.

| File | Rows | What it is |
|---|---|---|
| `durango_daily.csv` | 1 per day | Raw daily values, NASA parameter names as columns |
| `durango_monthly.csv` | 1 per month | Rain total, temperature means/min, frost days, soil wetness |
| `durango_annual.csv` | 1 per year | Same + `complete` flag + rain anomaly vs 1991–2020 normal |
| `durango_metadata.json` | — | Source, request URL, units, missing-value counts, notes, citation |
| `durango_annual_rain.svg` | — | Chart above (navy/gold project palette, ready for web & pitch) |

### Parameters (daily)
| Column | Unit | Meaning |
|---|---|---|
| `PRECTOTCORR` | mm/day | Precipitation, bias corrected |
| `T2M` / `T2M_MAX` / `T2M_MIN` | °C | Air temperature at 2 m: mean / max / min |
| `RH2M` | % | Relative humidity at 2 m |
| `ALLSKY_SFC_SW_DWN` | MJ/m²/day | Solar radiation at the surface — **only from 1984** |
| `GWETTOP` | 0–1 | Surface soil wetness (0–5 cm) |
| `GWETROOT` | 0–1 | Root-zone soil wetness (0–100 cm) |
| `GWETPROF` | 0–1 | Whole-profile soil wetness |

### Key facts (from this data)
- **Rain normal 1991–2020:** 519.5 mm/year.
- **Driest year:** **2011** — 259.9 mm, **−50 %** vs normal. Next: 1994 (−37 %), 1999 (−35 %), 1998 (−35 %).
- Rain and temperature have **no missing days**. Radiation is empty before 1984.

### ⚠️ Read before using
- **Soil wetness ≠ sensor moisture.** `GWET*` is a fraction of saturation (0–1), not volumetric moisture %. Convert it before comparing with the SENSOR reading (calibration, Role 3).
- **One pixel, not the plot.** POWER values come from a model grid cell (MERRA-2, ~50 km). They describe the region; the sensor describes the field.
- **Empty cell = missing value.** The API fill value `-999` is removed.
- `frost_days` = days with `T2M_MIN ≤ 0 °C`.
- The year count is **45**, not 42: the pitch and the UI should use the number from `durango_annual.csv`.

### Regenerate
```bash
python backend/nasa_power.py            # download again (needs internet)
python backend/nasa_power.py --offline  # rebuild summaries/chart from the saved CSV (Plan B)
```

### Citation
> These data were obtained from the NASA Langley Research Center (LaRC) POWER Project funded through the NASA Earth Science/Applied Science Program.

---

## `crops/` — crop table with sources

**Rule A5:** no agronomic value without a source. Each row of `crop_values.csv` names its source **and the exact table/row** where it was read. `backend/crops.py` refuses to load a value without a source.

| Crop | Family | Fixes N | Water need (mm/cycle) | Drought sensitivity | Cycle (days) | Frost damage at flowering (°C) |
|---|---|---|---|---|---|---|
| Bean (dry) · *Phaseolus vulgaris* | Fabaceae | ✅ yes | 300 – 500 | medium-high | 95 – 110 | −2 to −3 |
| Maize (grain) · *Zea mays* | Poaceae | no | 500 – 800 | medium-high | 125 – 180 | −1 to −2 |
| Oats · *Avena sativa* | Poaceae | no | 450 – 650 ¹ | low-medium ¹ | 120 – 150 ¹ | −1 to −2 |
| Sorghum (grain) · *Sorghum bicolor* | Poaceae | no | 450 – 650 ² | low | 120 – 130 | −1 to −2 |
| Alfalfa · *Medicago sativa* | Fabaceae | ✅ yes | 800 – 1600 | low-medium | 100 – 365 (perennial) | **gap — no source** |

¹ FAO group value for barley/oats/wheat · ² FAO group value for sorghum/millet.
Frost values for germination and fruiting stages are also in the CSV.

| Crop | Root depth (m) · FAO-56 T22 | Ky (yield response to water) · FAO-56 T24 |
|---|---|---|
| Bean | 0.6 – 0.9 | 1.15 |
| Maize | 1.0 – 1.7 | 1.25 |
| Oats | 1.0 – 1.5 | **gap — not in Table 24** |
| Sorghum | 1.0 – 2.0 | 0.9 |
| Alfalfa | 1.0 – 2.0 | 1.1 |

**Soils** (`soils.csv`, FAO-56 Table 19): available water (θFC − θWP) per m of soil — sandy 0.05–0.11 · sandy loam 0.11–0.15 · loam 0.13–0.18 · silt loam 0.13–0.19 · clay 0.12–0.20 m³/m³.
**Soil N classes** (`soil_n_classes.csv`, NOM-021-RECNAT-2000, method AS-08): very low 0–10 · low 10–20 · medium 20–40 · high 40–60 · very high > 60 mg/kg inorganic N. The norm states they refer to small-grain cereals and to the lab method — the field sensor reading is indicative.
**Effective rain:** FAO TM3 ch. 4 — `Pe = 0.8·P − 25` if P > 75 mm/month, else `0.6·P − 10` (never negative).

### Sources
| ID | Used for | Reference |
|---|---|---|
| `FAO_TM3` | Water need, drought sensitivity, cycle length | Brouwer & Heibloem (1986), *Irrigation Water Management: Training Manual No. 3 — Irrigation Water Needs*, FAO, ch. 3, Tables 6 & 14 · [link](https://www.fao.org/4/s2022e/s2022e07.htm) |
| `FAO_FROST` | Critical frost damage temperatures | Snyder & de Melo-Abreu (2005), *Frost Protection: fundamentals, practice and economics*, Vol. 1, FAO Env. & Nat. Resources Series 10, Table 4.5 · [link](https://www.fao.org/4/y7223e/y7223e0a.htm) |
| `FAO_56` | Soil available water, root depth, Ky | Allen et al. (1998), *Crop evapotranspiration*, FAO Irrigation and Drainage Paper 56, Tables 19, 22, 24 · [link](https://www.fao.org/4/x0490e/x0490e00.htm) |
| `FAO_TM3_PE` | Effective rainfall formula | Brouwer & Heibloem (1986), FAO TM3, ch. 4 · [link](https://www.fao.org/4/s2022e/s2022e08.htm) |
| `NOM021` | Soil inorganic-N classes | SEMARNAT (2002), NOM-021-RECNAT-2000, DOF 31-12-2002, method AS-08 · [link](https://sidof.segob.gob.mx/notas/docFuente/717582) |
| `FAO_BNF` | Nitrogen fixation (bean, alfalfa) | AFNETA alley farming training manual, Vol. 2, Technical paper 2: *Biological nitrogen fixation* (FAO Knowledge Repository) · [link](https://openknowledge.fao.org/server/api/core/bitstreams/b447cf68-d3f5-4733-940c-f33591e0588a/content/x5546e05.htm) |
| `GBIF` | Scientific name & botanical family | GBIF Backbone Taxonomy (species match API) · [link](https://api.gbif.org/v1/species/match) |

### Gaps (`gaps.csv`) — shown to users as *"huecos"*
- **Alfalfa frost tolerance:** not in FAO Table 4.5 → the engine must not invent a frost rule for alfalfa.
- **Oats Ky:** not in FAO-56 Table 24 → the engine uses the strictest water rule for oats.
- **Sowing window in Durango (rainfed):** INIFAP data not found online → pending (INIFAP Campo Experimental Valle del Guadiana).
- **Local varieties** (e.g. *Pinto Saltillo* bean) may have shorter cycles than FAO global ranges → pending INIFAP.
- **Seed cost / crop price:** no source → the *income* priority has no data yet.

### ⚠️ Read before using
- FAO ranges are **global indicative values**, not Durango measurements. Use the low end for short cycles.
- Frost critical temperatures are **plant-tissue** temperatures. NASA `T2M_MIN` is **air at 2 m**; FAO warns that buds and flowers are usually colder than air, so the threshold should be applied with margin.
- `fixes_nitrogen = false` for grasses is derived from the botanical family (Poaceae, not legumes).

### Files
| File | Edit it? | What |
|---|---|---|
| `crop_values.csv` | ✅ source of truth | one value per row: value or min/max, unit, source_id, where in source, note |
| `sources.csv` | ✅ | full citations + URL + access date |
| `gaps.csv` | ✅ | missing data, status and next step |
| `crops.json` | ❌ generated | `python backend/crops.py` validates the CSVs and rebuilds it |
