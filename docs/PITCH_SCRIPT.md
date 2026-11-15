# RotaHawk — 4-minute pitch script (Jass presents)

**Only Jass speaks. The pitch may last 3 to 5 minutes; this script is 4:00.** To land on 3:30, shorten slide 4 (skip the explanation of the chat, −15 s) and the last sentence of slide 6 (−8 s). If you have up to 5:00, let the animation play twice or open the web live for the judges.

Slides: `web/slides/index.html` (click or arrow keys; F = fullscreen; Ctrl+P = export PDF).
Numbers on the slides and in the animation come from `web/animacion/data.js` (engine output). **If the engine changes, run `python build_data.py` in `web/animacion/` and re-check the numbers below.**
Current example (maize farmer, Durango, 45 seasons 1981–2025): current rotation fails **23**; best alternative (beans, beans, sorghum) fails **9**; worst year **1997**, rainfall 56% below normal.

| Slide | Time | Who |
|---|---|---|
| 1 Cover | 0:00–0:10 | Jass |
| 2 Problem | 0:10–0:55 | Jass |
| 3 Animation (~30 s, plays by itself) | 0:55–1:30 | Jass (the AI sentence goes over the assistant scene) |
| 4 The result (web captures) | 1:30–2:20 | Jass |
| 5 Live prototype | 2:20–3:00 | Jass narrates; Jean plants the node in the pot, without speaking |
| 6 Impact and validity | 3:00–3:45 | Jass |
| 7 Close | 3:45–4:00 | Jass |

The full web and the live chat are shown **only if the judges ask** (scan the QR on slide 7 or open the site).

## Script

**1 · Cover (10 s)**
"[▶ Slide 1] Good morning. We are Halcones Dorados, from Durango. This is RotaHawk: Smart Crop Rotation for Climate Resilience. [click ▶ slide 2]"

**2 · Problem (45 s)**
"[▶ Slide 2] Meet Don José, an example farmer in Durango. He grows maize every cycle, and every season he chooses what to plant without knowing how it would do in a bad year. One bad year can cost him the harvest, the water and his soil.
But there is data that does exist: NASA has climate data since 1981. [point at the blue NASA box] With NASA POWER we took, for Don José's field, daily rain, minimum temperature and root-zone soil moisture: more than 16 thousand days, 45 full years.
So we asked: in those 45 years of real data, how many times would his maize have failed? [point at the chart: red bars are the years it fails] The answer: [point at the big 23] 23 seasons out of 45. [click ▶ slide 3]"

**3 · Animation (35 s) — plays by itself**
"[▶ Slide 3: the animation plays by itself, do not touch anything] [soil and cloud scenes] Our RotaHawk node is an NPK soil sensor: an indicative reading, not a lab test, sent to the cloud every minute. [satellite scene] The NASA data covers a cell tens of kilometers wide; we measure this field, and we correct the NASA data with the ground. [“Calibrated” appears with the EXAMPLE · NEXT MODULE label] Today that calibration is example data: it is our next module. [grid of years in red and green] Then we test every rotation in each of the 45 years from NASA. Red means the crop fails. [the worst year is marked] [assistant scene:] "Our assistant never invents numbers: it answers only from NASA data, the sensor and FAO, and when it does not know, it says so." [when it ends, it moves on to slide 4 by itself]"

**4 · The result (50 s)**
"[▶ Slide 4] Don José's maize fails in 23 of 45 seasons [point at the red card, on the left]. Beans, beans and sorghum: 9 [point at the yellow card, on the right]. And we show the worst year, not the average: 1997, when the growing season had 56% less rain than normal [point at the “Worst year” line]. And we did not invent normal: it is the 1991–2020 average of the same NASA data [point at the note below]. Every number on screen carries its label: NASA, sensor or FAO [point at the blue NASA tags].
[point at the chat capture, bottom left] We asked the assistant how much he would earn per hectare. It answers: “I don't have that data. Confirm it with a local agronomist.” We have no sourced prices for Durango, so it does not make one up. [click ▶ slide 5]"

**5 · Live prototype (40 s)**
"[▶ Slide 5] Now the real thing. [Jean plants the node in the pot, without speaking.] [point at the “Soil reading” panel with N, P and K] On screen, the soil reading from our prototype, labeled SENSOR. [IF THE READING SHOWS DASHES, say: "The node is connected and sending data, but the probe is not reading soil right now. We show dashes instead of zeros because we never show a number we cannot trust. In the field, the soil values appear here." Then continue.] It is an indicative reading, and it goes to the cloud every minute. [click ▶ slide 6]"

**6 · Impact and validity (45 s)**
"[▶ Slide 6] [point at the first pillar, “Real data”] Why you can trust it: everything starts from real NASA data: rain, minimum temperature and soil moisture, every day since 1981, 45 full seasons. On top of it we apply FAO crop water and frost rules, [point at the second pillar, “Honest”] and we give a range instead of a single number: the best option works in 36 of 45 seasons, range 31 to 40. Calibrating the NASA data against our field sensor is the next module: today it is example data, and we say so. [point at the third pillar, “Open”] It is open source. [point at the strip below] What we do not know, we show: local sowing dates and prices. And it is decision support: it does not replace an agronomist. [click ▶ slide 7]"

**7 · Close (15 s)**
"[▶ Slide 7] RotaHawk: Smart Crop Rotation for Climate Resilience. Try it now: [point at the QR code] scan the code, or go to jassjmz.github.io/rotahalcon. [point at the team photos] Thanks to NASA's open data. Thank you."

## Backup plan
- **The slide-5 reading shows dashes (probe returns zeros):** do not hide it. Say the sentence in the notes of slide 5, point at the node on the table, and move on to slide 6. The node still counts as connected: the dashes are the page refusing to show a number it cannot trust.
- No network: the web uses its saved real response (OFFLINE SNAPSHOT banner); the animation runs from local files.
- Animation fails: play the MP4 (`animacion/index.html?short=1`, screen-recorded at 1080p; the same file works as the 30-second video if slides are not allowed).
- Likely judge questions → answers
  - *"Is the sensor live?"* — The node reads real soil; the satellite calibration in the demo is example data and is labelled so. That is the next module.
  - *"Why did both rotations fail in 1997?"* — The engine says that year was too dry for both. The point is 9 failures instead of 23, not zero.
  - *"Where do the crop numbers come from?"* — FAO crop-water and frost rules; gaps are listed (seed cost, prices, local sowing dates).
  - *"Is the assistant making things up?"* — It only answers from the data in the report and cites NASA, SENSOR or FAO/INIFAP; when a source is missing it says so.
  - *Can we try it?* — Yes: scan the QR on slide 7. The web, the comparison, the bad-year view and the live chat are there.
