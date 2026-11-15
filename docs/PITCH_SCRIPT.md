# RotaHalcón — 4-minute pitch script (Role 4 presents)

Slides: `web/slides/index.html` (click or arrow keys; F = fullscreen; Ctrl+P = export PDF).
Numbers on the slides and in the animation come from `web/animacion/data.js` (engine output). **If the engine changes, run `python build_data.py` in `web/animacion/` and re-check the numbers below.**
Current example (maize farmer, Durango, 45 seasons 1981–2025): current rotation fails **23**; best alternative (beans, beans, sorghum) fails **9**; worst year **1997**, rainfall 56% below normal.

| Slide | Time | Who |
|---|---|---|
| 1 Cover | 0:00–0:10 | Presenter |
| 2 Problem | 0:10–0:50 | Presenter |
| 3 Animation, part 1 (sensor, ~13 s) | 0:50–1:10 | Plays by itself |
| 4 Animation, part 2 (the system, ~14 s) | 1:10–1:35 | Plays by itself |
| 5 Live demo | 1:35–3:15 | Presenter drives the web, Role 1 handles the node |
| 6 Impact and validity | 3:15–3:50 | Presenter |
| 7 Close | 3:50–4:00 | Presenter |

## Script

**1 · Cover (10 s)**
"Good morning. We are Halcones Dorados, from Durango. This is RotaHalcón: crop rotation as climate insurance."

**2 · Problem (40 s)**
"Meet Don José, an example farmer in Durango. He grows maize every cycle. Every season he decides what to plant without knowing how that choice would do in a bad year. And one bad year can cost him the harvest, the water and his soil.
NASA climate data is free, but it covers kilometres, not his plot, and it is hard to read.
So we asked a simple question: over the last 45 years of real NASA data, how often would Don José's maize have failed? The answer: 23 seasons out of 45."

**3 · Animation, part 1 (20 s) — plays by itself (soil, calibration)**
"Our AGRISENSE node is an NPK soil sensor. It gives an indicative reading, not a lab test, and sends it to the cloud every minute. A satellite sees one pixel that is several kilometres wide; we see this field. We correct the satellite with the ground. In this demo that calibration is example data: it is our next module."

**4 · Animation, part 2 (25 s) — plays by itself (every rotation, worst year)**
"Then we test every rotation in each of the 45 years of NASA data. Red means the crop fails. Don José's maize fails in 23 seasons. Beans, beans and sorghum, in 9. And we show the worst year, 1997, not the average. Let's see it live."

**5 · Live demo (1:40)**
"Let's use it. I mark the plot on the map. Here is the soil, live from our node [Role 1 touches the probe]. [IF THE CARD SHOWS DASHES, say: "The node is connected and sending data, but the probe is not reading soil right now. We show dashes instead of zeros because we never show a number we cannot trust. In the field, the soil values appear here." Then continue.] Here are four rotations, side by side. Don José's current one is red: it works in 22 of 45 years. This one works in 36, with a range, because we do not claim certainty.
I pick a bad year, 1997. Look what each rotation would have done.
Now I move the sliders: more weight on water, and the ranking changes live. Notice the income slider: it says information gap. We do not have a sourced seed cost or crop price for Durango, and we say so instead of pretending.
I ask: 'Why is my rotation red?' The answer cites NASA and FAO, and lists what we do not know."

**6 · Impact and validity (35 s)**
"Why you can trust it: 45 real seasons from NASA POWER, crop water and frost rules from FAO, and a range instead of a single number. What we do not know, we show: local sowing dates, prices, and the sensor calibration.
It is open source. Any region can plug in its own crops and climate. And it is decision support: it does not replace an agronomist."

**7 · Close (10 s)**
"RotaHalcón: rotation as climate insurance. Thanks to the AGRISENSE team whose node made this possible. The code is open on GitHub. Thank you."

## Backup plan
- **The soil card shows dashes (probe returns zeros):** do not hide it or touch the web. Say the sentence in slide 5's notes, point at the node on the table, and move on to the comparison. The node still counts as connected: the dashes are the web refusing to show a number it cannot trust.
- No network: the web uses its saved real response (OFFLINE SNAPSHOT banner); the animation runs from local files.
- Animation fails: play the MP4 (`animacion/index.html?short=1`, screen-recorded at 1080p; the same file works as the 30-second video if slides are not allowed).
- Likely judge questions → answers
  - *"Is the sensor live?"* — The node reads real soil; the satellite calibration in the demo is example data and is labelled so. That is the next module.
  - *"Why did both rotations fail in 1997?"* — The engine says that year was too dry for both. The point is 9 failures instead of 23, not zero.
  - *"Where do the crop numbers come from?"* — FAO crop-water and frost rules; gaps are listed (seed cost, prices, local sowing dates).
  - *"Is the assistant making things up?"* — It only answers from the data in the report and cites NASA, SENSOR or FAO/INIFAP; when a source is missing it says so.
