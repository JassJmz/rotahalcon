# RotaHawk — 4-minute pitch script (Jass presents)

**Only Jass speaks. The pitch may last 3 to 5 minutes; this script is 4:00.** To land on 3:30, shorten slide 4 (skip the explanation of the chat, −15 s) and the last sentence of slide 6 (−10 s). If you have up to 5:00, let the animation play twice or open the web live for the judges.

Slides: `web/slides/index.html` (click or arrow keys; F = fullscreen; Ctrl+P = export PDF).
Numbers on the slides and in the animation come from `web/animacion/data.js` (engine output). **If the engine changes, run `python build_data.py` in `web/animacion/` and re-check the numbers below.**
Current example (maize farmer, Durango, 45 seasons 1981–2025): current rotation fails **23**; best alternative (beans, beans, sorghum) fails **9**; worst year **1997**, rainfall 56% below normal.

| Slide | Time | Who |
|---|---|---|
| 1 Cover | 0:00–0:10 | Jass |
| 2 Problem | 0:10–0:50 | Jass |
| 3 Animation (~30 s, plays by itself) | 0:50–1:25 | Jass (the AI sentence goes over the assistant scene) |
| 4 The result (web captures) | 1:25–2:15 | Jass |
| 5 Live prototype | 2:15–3:00 | Jass narrates; Jean plants the node in the pot, without speaking |
| 6 Impact and validity | 3:00–3:40 | Jass |
| 7 Close | 3:40–4:00 | Jass |

The full web and the live chat are shown **only if the judges ask** (scan the QR on slide 7 or open the site).

## Script

**1 · Cover (10 s)**
"Good morning. We are Halcones Dorados, from Durango. This is RotaHawk: smart crop rotation for climate resilience."

**2 · Problem (40 s)**
"Meet Don José, an example farmer in Durango. He grows maize every cycle. Every season he decides what to plant without knowing how that choice would do in a bad year. And one bad year can cost him the harvest, the water and his soil.
NASA climate data is free, but it covers kilometers, not his field, and it is hard to read.
So we asked a simple question: over the last 45 years of real NASA data, how often would Don José's maize have failed? The answer: 23 seasons out of 45."

**3 · Animation (35 s) — plays by itself**
"Our AGRISENSE node is an NPK soil sensor: an indicative reading, not a lab test, sent to the cloud every minute. A satellite sees one pixel that is several kilometers wide; we see this field, and we correct the satellite with the ground. In this demo that calibration is example data: it is our next module. Then we test every rotation in each of the 45 years of NASA data. Red means the crop fails. [When the assistant scene plays:] "Our assistant never invents numbers: it answers only from NASA data, the sensor and FAO, and when it does not know, it says so.""

**4 · The result (50 s)**
"Don José's maize fails in 23 of 45 seasons. Beans, beans and sorghum: 9. And we show the worst year, 1997, not the average. We asked the assistant how much he would earn per hectare. It answers: 'I don't have that data. Confirm it with a local agronomist.' We have no sourced prices for Durango, so it does not make one up."

**5 · Live prototype (45 s)**
"Now the real thing. [Jean plants the node in the pot, without speaking.] On screen, the soil reading from our prototype, labeled SENSOR. [IF THE READING SHOWS DASHES, say: "The node is connected and sending data, but the probe is not reading soil right now. We show dashes instead of zeros because we never show a number we cannot trust. In the field, the soil values appear here." Then continue.] It is an indicative reading, not a lab analysis, and it goes to the cloud every minute."

**6 · Impact and validity (40 s)**
"Why you can trust it: 45 real seasons from NASA POWER, crop water and frost rules from FAO, and a range instead of a single number: the best option works in 36 of 45 seasons, range 31 to 40. Calibrating the satellite against our field sensor is the next module: today it is example data, and we say so. What we do not know, we show: local sowing dates and prices.
It is open source. Any region can plug in its own crops and climate. And it is decision support: it does not replace an agronomist."

**7 · Close (20 s)**
"RotaHawk: Smart Crop Rotation for Climate Resilience. You can try it now: scan the code, or go to jassjmz.github.io/rotahalcon. Thanks to the AGRISENSE team whose node made this possible. The code is open on GitHub. Thank you."

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
