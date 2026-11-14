# Contributing to RotaHalcón

Thanks for wanting to help! 🦅🌱 This project is open so farmers anywhere can benefit from NASA data.

## Ways to help
- 💡 **Ideas & feedback** — open an issue with the *Idea* template.
- 🌾 **Agronomic data** — crop values for your region, **always with a citable source** (FAO, INIFAP, a national agency, a paper).
- 🌍 **Translations** — Spanish, English, indigenous languages.
- 🐛 **Bugs** — open an issue with the *Bug* template.
- 🧑‍🌾 **Field validation** — tell us whether the recommendations make sense where you farm.
- 💻 **Code** — firmware, backend, AI, web.

## Ground rules
1. **No invented agronomic values.** Every crop number needs a source in the PR.
2. **Label every value** shown to users as **NASA** or **SENSOR** (or its source).
3. **Never commit secrets** (API keys, Firebase config, Wi-Fi passwords). Use `.env` files — they're ignored.
4. Small, focused pull requests with a clear description.
5. Be kind. We follow the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).

## Workflow
**External contributors:** fork → branch → pull request to `main`.

**Team members during the hackathon (speed mode):**
- Each person works **only in their folder** (`hardware/`, `backend/`, `ia/`, `web/`), so there are no conflicts.
- `git pull` before starting, commit often, `git push` to `main`.
- Shared files (`README.md`, the API contract) → tell the team before editing.

## API contract
The data formats between the sensor, the backend and the web live in `docs/CONTRACT.md`. Don't change them without opening an issue first.
