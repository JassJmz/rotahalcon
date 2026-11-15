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
| `humedad_pct` | 43 | 43 | 43 | Confirmed by the team; stable during the test (integer resolution) |
| `temp_c` | 21 | 21 | 21 | Confirmed by the team; stable during the test (integer resolution) |

**Status:** all seven fields are confirmed by the team as correct readings. Moisture and temperature report whole numbers and stayed stable during the 3 h 20 min test. To use field moisture in the satellite calibration, set `CALIBRACION_SENSOR_CONFIRMADO=true` on the server (see `ia/README.md`). Readings are **indicative**, not a lab analysis.

Effect on the engine (real N ≈ 55 mg/kg, maize-maize history): alternatives that alternate families gain 1–3 soil
points (e.g. bean–bean–sorghum 74 → 75); the ranking does not change.
