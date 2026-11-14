"""
RotaHalcón — latest SENSOR reading from Firebase Realtime Database (AGRISENSE node).

Reads  <FIREBASE_DB_URL>/nodos/agrisense-01/ultima.json  (REST, standard library only)
and returns it in the contract format (docs/CONTRACT.md):
    { "ts", "humedad_pct", "temp_c", "ph", "ce_uScm", "n_mgkg", "p_mgkg", "k_mgkg", "fuente": "SENSOR" }
plus  "mock": false, "edad_s": seconds since the reading.

If Firebase is not configured, unreachable, or the reading is malformed, it returns the
MOCK reading with "mock": true — the API never breaks during the demo.

Configuration (never in the repo):
    FIREBASE_DB_URL   e.g. https://<project>-default-rtdb.firebaseio.com
    FIREBASE_AUTH     optional: database secret or ID token, if the rules require auth
Set them as environment variables (Render → Environment) or in backend/.env (git-ignored).
"""

# ── DATOS ──
NODE_PATH = "nodos/agrisense-01/ultima"
TIMEOUT_S = 4                 # keep /recomendar fast even if Firebase is slow
CACHE_S = 30                  # sensor reads every 60 s, no need to ask more often
REQUIRED_FIELDS = ["ts", "humedad_pct", "temp_c", "ph", "ce_uScm", "n_mgkg", "p_mgkg", "k_mgkg"]
MOCK_READING = {
    "ts": 1794700000, "humedad_pct": 24.1, "temp_c": 19.3, "ph": 7.2,
    "ce_uScm": 410, "n_mgkg": 32, "p_mgkg": 18, "k_mgkg": 145, "fuente": "SENSOR",
}
# ── FIN DATOS ──

import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path

_ENV_FILE = Path(__file__).resolve().parent / ".env"
_cache = {"at": 0.0, "value": None}


def _config() -> tuple[str | None, str | None]:
    if _ENV_FILE.exists():                       # tiny .env reader (KEY=value lines)
        for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    url = os.environ.get("FIREBASE_DB_URL", "").strip().rstrip("/")
    return (url or None), (os.environ.get("FIREBASE_AUTH", "").strip() or None)


def _mock(reason: str) -> dict:
    return {**MOCK_READING, "mock": True, "motivo_mock": reason}


def _validate(raw) -> dict:
    if not isinstance(raw, dict):
        raise ValueError("no reading at " + NODE_PATH)
    missing = [f for f in REQUIRED_FIELDS if f not in raw]
    if missing:
        raise ValueError("missing fields: " + ", ".join(missing))
    out = {f: float(raw[f]) for f in REQUIRED_FIELDS}
    out["ts"] = int(out["ts"])
    out["fuente"] = "SENSOR"
    return out


def latest_reading(force: bool = False) -> dict:
    """Latest sensor reading (contract format) or the mock, never raises."""
    now = time.time()
    if not force and _cache["value"] and now - _cache["at"] < CACHE_S:
        return _cache["value"]

    url, auth = _config()
    if not url:
        value = _mock("Firebase not configured (FIREBASE_DB_URL)")
    else:
        full = f"{url}/{NODE_PATH}.json"
        if auth:
            full += "?" + urllib.parse.urlencode({"auth": auth})
        try:
            with urllib.request.urlopen(full, timeout=TIMEOUT_S) as resp:
                value = _validate(json.load(resp))
            value["mock"] = False
            value["edad_s"] = max(0, int(now) - value["ts"])
        except Exception as exc:                 # network, auth (401), bad JSON, bad format
            value = _mock(f"Firebase read failed: {type(exc).__name__}: {str(exc)[:120]}")

    _cache.update(at=now, value=value)
    return value


if __name__ == "__main__":
    print(json.dumps(latest_reading(force=True), indent=2, ensure_ascii=False))
