# Field readings — AGRISENSE node

## `agrisense-01_2026-11-14.csv`
200 readings from node `agrisense-01`, one per minute, **14 Nov 2026 19:56–23:15 (UTC-6)**, probe in soil.
Exported by Role 1 from Firebase (`nodos/agrisense-01/lecturas`). Columns follow `docs/CONTRACT.md` (+ `edad_s`, `nodo`).

| Field | Min | Max | Mean | Note |
|---|---|---|---|---|
| `n_mgkg` | 47 | 67 | 54.9 | Varies → live. NOM-021 class: **high** (40–60), up to **very high** (> 60) |
| `p_mgkg` | 22 | 27 | 24.0 | Varies → live |
| `k_mgkg` | 175 | 193 | 185.1 | Varies → live |
| `ph` | 6.34 | 6.48 | 6.41 | Varies → live |
| `ce_uScm` | 1217 | 1318 | 1260 | Varies → live |
| `humedad_pct` | 43 | 43 | 43 | ⚠️ **Exactly constant for 200 readings** |
| `temp_c` | 21 | 21 | 21 | ⚠️ **Exactly constant for 200 readings** |

**Status:** N, P, K, pH and EC behave like live readings. Moisture and temperature never change by even one unit
in 3 h 20 min, so their Modbus registers are **not confirmed** yet (they may be wrong registers or a fixed value).
Until Role 1 confirms the register map in soil/water, moisture is **not** used for the satellite calibration
(`CALIBRACION_SENSOR_CONFIRMADO=false`, see `ia/README.md`). Readings are **indicative**, not a lab analysis.

Effect on the engine (real N ≈ 55 mg/kg, maize-maize history): alternatives that alternate families gain 1–3 soil
points (e.g. bean–bean–sorghum 74 → 75); the ranking does not change.
