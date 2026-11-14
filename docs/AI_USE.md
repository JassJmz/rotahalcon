# AI use declaration — RotaHalcón

NASA Space Apps 2026 asks teams to declare how AI tools were used. We separate two things:
**(A) AI inside the product** (what the farmer and the judges see working) and
**(B) AI tools the team used to build it**. Each role fills in its own part of (B).

> Short version for the submission form is at the end of this file.

---

## A. AI inside RotaHalcón

| Component | What it does | Model / method | Where | Status |
|---|---|---|---|---|
| **Grounded assistant** (`POST /preguntar`) | Answers farmer questions about the recommendation in plain English or Spanish | **Hybrid:** recognized questions → deterministic templates (exact numbers, instant); free-form questions → **local LLM `qwen2.5:7b` via Ollama** (open-weight, Apache-2.0, runs offline on the laptop, no data leaves the device). Optional, off by default: Claude API (`claude-opus-5-5`) | `ia/asistente.py`, `ia/asistente_ollama.py`, `ia/asistente_llm.py`, `ia/rutas.py` | ✅ |
| Grounding rules | The LLM only receives a labeled summary of the engine output (strategies, NASA-based resilience, sensor reading, calibration) and must: use only that data, never invent agronomic numbers or prices, say "I don't have that data" otherwise, cite NASA / SENSOR / FAO, and recommend confirming with an agronomist. Output is forced into a JSON schema; if the LLM is unavailable or answers badly, the template answers instead | System prompt in `ia/prompt.py` | ✅ |
| **Satellite ↔ sensor calibration** | Learns how the field's soil moisture differs from NASA POWER `GWETTOP` (≈50 km cell) | **Linear regression vs random forest** (scikit-learn), compared by leave-one-out MAE; best one is used. Fewer than 5 overlapping days → simple difference | `ia/calibracion.py` | ✅ method · ⚠️ **example data** until field moisture readings reach Firebase |
| **Uncertainty of the resilience score** | Turns "works in 36 of 45 seasons" into a range (e.g. 31–40) | **Bootstrap** over the simulated years (2000 resamples, 5th–95th percentile, fixed seed) — statistics, not AI | `ia/incertidumbre.py` | ✅ |
| Spanish answers | Translates the engine's English sentences by fixed patterns (no AI, never guesses unknown text) | Regex patterns | `ia/traduccion.py` | ✅ |

**What is NOT AI:** the rotation engine and the 45-season simulation (`backend/engine.py`) are deterministic rules on NASA data and FAO / NOM-021 values — see [`VALIDITY.md`](VALIDITY.md).

**Limits we state openly**
- The local 7B model can still word things imprecisely on free-form questions; that is why recognized questions use templates and every answer carries "decision support — confirm with an agronomist".
- Calibration numbers shown today come from **synthetic example readings** (labeled `"datos": "ejemplo"` in the API and "EXAMPLE DATA" in the web) until real moisture readings are stored.
- `qwen2.5:3b` (faster alternative) is under the Qwen Research License; the default `qwen2.5:7b` is Apache-2.0.

---

## B. AI tools used by the team to build the project

### Role 3 — AI
- **Claude (Anthropic), via Claude Code**: helped plan the project, write documentation, and write and test code in `ia/` (assistant, calibration, uncertainty, glossary, translation). All code was run and tested by the team member; design decisions and approvals were the team's.
- **Glossary texts** (`ia/glosario.json`): drafted with AI assistance, reviewed by the team; definitions only, no agronomic values.

### Role 1 — Hardware
- _To complete: AI tools used (if any) for firmware, wiring, Firebase setup, project-page draft._

### Role 2 — Data & backend
- _To complete: AI tools used (if any) for the engine, NASA data download, tests, VALIDITY.md._

### Role 4 — Web, animation & pitch
- _To complete: AI tools used (if any) for the web, the animation, slides, video._
- **Images / video generated with AI must carry a visible watermark** ("AI-generated"), including the logo if it was made with AI. No NASA logos.

---

## Short version (for the submission form)

> RotaHalcón uses AI in three places: (1) a grounded farmer assistant — deterministic templates for common questions and a local open-weight LLM (qwen2.5:7b via Ollama, offline) for free-form ones, constrained to answer only from our engine's NASA-based results and to cite sources; (2) satellite-vs-sensor soil-moisture calibration comparing linear regression and random forest (scikit-learn, leave-one-out error), currently demonstrated with labeled example readings; (3) bootstrap uncertainty ranges for the resilience score (statistics). The rotation engine itself is rule-based on NASA POWER, FAO and NOM-021 data. The team used Claude (Anthropic) via Claude Code to help plan, document and write code; all code was run and tested by the team. [Roles 1, 2, 4: add your tools.] AI-generated images carry a visible watermark.
