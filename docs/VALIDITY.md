# RotaHalcón — Scientific validity

**What we claim:** for one example field in Durango (24.02° N, 104.65° W), RotaHalcón replays every crop rotation against **45 real seasons of NASA climate (1981–2025)** and counts how many seasons each rotation would have lost. Every number comes from NASA, an official reference (FAO, NOM-021) or the field sensor — **nothing agronomic is invented**, and what is missing is shown to the farmer as a gap.

Live API: https://rotahalcon.onrender.com/docs · Code and data: this repository (`backend/`, `data/`, `ia/`).

---

## 1. Data sources

| What | Source | Label | Where |
|---|---|---|---|
| Daily rain, temperature, humidity, radiation, soil wetness 1981 → today | **NASA POWER** daily point API, community AG (`PRECTOTCORR`, `T2M`, `T2M_MAX`, `T2M_MIN`, `RH2M`, `ALLSKY_SFC_SW_DWN`, `GWETTOP`, `GWETROOT`, `GWETPROF`) | NASA | [`data/nasa_power/`](../data/nasa_power/) |
| Crop water need, drought sensitivity, cycle length | FAO — Brouwer & Heibloem (1986), *Irrigation Water Management TM3*, Tables 6 & 14 | — | [`data/crops/`](../data/crops/) |
| Effective rainfall formula | FAO TM3, ch. 4 | — | `engine.py` |
| Soil available water, root depth, yield response factor Ky | FAO — Allen et al. (1998), *FAO-56*, Tables 19, 22, 24 | — | `soils.csv`, `crop_values.csv` |
| Frost damage temperatures | FAO — Snyder & de Melo-Abreu (2005), *Frost Protection*, Table 4.5 | — | `crop_values.csv` |
| Nitrogen fixation (bean, alfalfa) | Biological nitrogen fixation, technical paper (FAO Knowledge Repository) | — | `crop_values.csv` |
| Soil nitrogen classes | **NOM-021-RECNAT-2000** (SEMARNAT, DOF 31-12-2002), method AS-08 | — | `soil_n_classes.csv` |
| Botanical family | GBIF Backbone Taxonomy | — | `crop_values.csv` |
| Soil N, P, K in the field | **AGRISENSE node** (ESP32 + RS485 NPK probe) → Firebase | SENSOR | `GET /sensor` |

Every crop value has its **source and exact table/row** in [`data/crops/crop_values.csv`](../data/crops/crop_values.csv). `backend/crops.py` **refuses to load any value without a source**.

## 2. Method (one season)

For every crop, every year, with real NASA data:

1. **Water** — `supply = effective rain in the crop window (FAO formula) + water stored in the root zone at sowing (FAO-56 soil × root depth × NASA GWETROOT that year)`.
   `expected yield loss = Ky × (1 − supply / need)` (FAO-33 via FAO-56 Table 24).
   The season **fails by drought** when the expected yield loss is **≥ 50 %**.
2. **Frost** — the season **fails by frost** if NASA `T2M_MIN` reaches the FAO critical damage temperature of the crop stage (germination / flowering / fruiting).

A **rotation** (3 crops, one rainfed crop per year) is planted in order since 1981. **Resilience = seasons OK / 45**. The **worst year** and its cause are reported.

## 3. Uncertainty

`resiliencia.rango` is a **bootstrap interval** over the 45 seasons (2000 resamples, 5th–95th percentile, fixed seed; `ia/incertidumbre.py`).
Example: bean every year → **36 of 45 seasons OK, range 31–40**.

## 4. Sanity checks (from our own data)

- **2011 is the driest year in the NASA record for this field: 260 mm, −50 % vs the 1991–2020 normal (519.5 mm).** Replaying 2011 (`/anio-malo?anio=2011`) fails every rotation tested — the engine reacts to the real bad year.
- Crops that need more water fail more: alfalfa (800–1600 mm need) fails 44 / 45 seasons rainfed; maize (500–800 mm) 23 / 45; bean (300–500 mm) 9 / 45.
- Sensitivity tests behave as expected: −20 % rain raises bean failures from 9 to 15; −2 °C brings the first frost failures (maize, longest cycle); sandy soil (less stored water) raises maize failures from 23 to 28.
- **Do no harm:** an alternative is never proposed if it fails more seasons than the farmer's current rotation (when a safer one exists).

## 5. Example result (pitch case)

Farmer who grows **maize every year**, loam soil:

| Rotation | Seasons OK / 45 | Range | Worst year |
|---|---|---|---|
| Current: maize · maize · maize | **22** (fails 23) | 17–27 | 1997 — maize got 21 % of its water |
| Best: bean · bean · sorghum | **36** (fails 9) | 31–40 | 2023 — bean got 26 % of its water |

## 6. Assumptions (shown to the farmer as risks)

| Assumption | Why |
|---|---|
| Rainfed sowing on **1 July** | INIFAP sowing dates for Durango not available online yet |
| Low end of FAO ranges (cycle, water need, root depth) | FAO: use the low value for short cycles / early varieties |
| Failure = expected yield loss ≥ 50 % | Definition of a "lost season" |
| Frost stages = 25 % / 50 % / 25 % of the cycle | Approximation |
| Soil-score weights 50/50 (legumes / family change); 70/30 or 30/70 with a real sensor N reading | Model design |

## 7. Limitations and gaps (shown to the farmer as "huecos")

- **One pixel, not the plot:** NASA values describe a ~50 km grid cell; the sensor describes the field.
- **Global, not local crop values:** FAO ranges are worldwide; local INIFAP data (sowing window, Pinto Saltillo bean cycle) are pending.
- **No source → no rule:** alfalfa has no FAO frost value and oats has no FAO Ky, so the engine applies no frost rule to alfalfa and the strictest water rule to oats.
- **No income data:** there is no sourced seed cost or crop price for Durango, so the *income* priority is shown as a gap and not used.
- **Sensor is indicative:** the NPK probe is not a lab analysis; NOM-021 classes are for lab method AS-08. The engine uses N only from a **real** reading and tells the farmer to confirm with a soil lab.
- **Calibration is an example** until the node has a moisture probe (Role 3 method shown with labeled synthetic readings).
- **Decision support, not a prescription:** every answer ends with "confirm with an agronomist".

## 8. Reproduce

```bash
python backend/nasa_power.py --offline   # rebuild climate summaries from the saved NASA CSV
python backend/crops.py                  # validate that every crop value has a source
uvicorn main:app --port 8000             # (in backend/) then POST /recomendar
```

*NASA POWER acknowledgement: These data were obtained from the NASA Langley Research Center (LaRC) POWER Project funded through the NASA Earth Science/Applied Science Program.*
