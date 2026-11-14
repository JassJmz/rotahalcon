"""
RotaHalcón — runs Role 3's satellite ↔ sensor calibration (ia/calibracion.py) for the API.

calibrar() trains linear vs random-forest models with leave-one-out (≈20 s on a laptop,
much more on a small server), so it NEVER runs inside a request:
  • a background thread computes it at startup and whenever the sensor history changes
    (at most once every MIN_RECALC_S),
  • /recomendar always answers instantly with the last result,
  • before the first result is ready it returns a flagged placeholder ("estado": "calculando").
"""

# ── DATOS ──
MIN_RECALC_S = 30 * 60        # recompute at most every 30 min (sensor writes every 60 s)
CHECK_EVERY_S = 5 * 60        # how often the worker checks for new sensor history
PLACEHOLDER = {
    "satelite_pct": None, "sensor_pct": None, "ajuste": None, "error": None, "modelo": None,
    "estado": "calculando", "aviso": "Calibration is being computed in the background (Role 3 model).",
}
# ── FIN DATOS ──

import copy
import sys
import threading
import time
from pathlib import Path

import sensor

sys.path.append(str(Path(__file__).resolve().parent.parent / "ia"))
try:
    from calibracion import calibrar
except Exception:                     # ImportError, or sklearn missing
    calibrar = None

_state = {"value": None, "key": None, "at": 0.0, "error": None}
_lock = threading.Lock()


def _history_key(hist):
    return (len(hist), hist[-1]["ts"] if hist else None)


def _compute_once(force=False):
    hist = sensor.history()
    usable = [h for h in hist if h.get("humedad_pct") is not None]
    key = _history_key(usable)
    with _lock:
        fresh = time.time() - _state["at"] < MIN_RECALC_S
        if not force and _state["value"] is not None and (key == _state["key"] or fresh):
            return
    try:
        value = calibrar(usable or None)
        err = None
    except Exception as exc:
        value, err = None, f"{type(exc).__name__}: {str(exc)[:160]}"
    with _lock:
        if value is not None:
            _state.update(value=value, key=key, at=time.time(), error=None)
        else:
            _state["error"] = err


def _worker():
    _compute_once(force=True)
    while True:
        time.sleep(CHECK_EVERY_S)
        _compute_once()


def start():
    """Call once at app startup. No-op if Role 3's module is not available."""
    if calibrar is not None:
        threading.Thread(target=_worker, name="calibracion", daemon=True).start()


def current() -> dict:
    """The `calibracion` block for the API, instantly."""
    with _lock:
        if _state["value"] is not None:
            return copy.deepcopy(_state["value"])
        out = dict(PLACEHOLDER)
        if calibrar is None:
            out.update(estado="no_disponible", aviso="Calibration module (ia/calibracion.py) not available.")
        elif _state["error"]:
            out.update(estado="error", aviso="Calibration failed: " + _state["error"])
        return out


def status() -> str:
    with _lock:
        if calibrar is None:
            return "not available"
        if _state["value"] is not None:
            return f"ready ({_state['value'].get('modo')}, data: {_state['value'].get('datos')})"
        return "error" if _state["error"] else "computing"
