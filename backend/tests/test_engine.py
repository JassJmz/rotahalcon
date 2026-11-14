"""
RotaHalcón backend — regression tests (standard library only, no internet).

Run from the repo root:
    python -m unittest discover -s backend/tests -v

They lock the REAL results the team presents (pitch, VALIDITY.md). If a change in the
engine or the data moves one of these numbers, a test fails on purpose: update the
pitch / docs together with the test, never silently.
"""
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# ── DATOS ── (numbers the team presents — change only together with pitch/docs)
EXPECTED_CROP_FAILS_LOAM = {"frijol": 9, "maiz": 23, "sorgo": 9, "avena": 44, "alfalfa": 44}
PITCH_FARMER = ["maiz", "maiz"]
PITCH_CURRENT_FAILS = 23
PITCH_BEST = ["frijol", "frijol", "sorgo"]
PITCH_BEST_FAILS = 9
DRIEST_YEAR, DRIEST_MM = 2011, 259.9
DEFAULT_PRIORITIES = {"agua": 0.4, "suelo": 0.3, "ingreso": 0.2, "riesgo": 0.1}
# ── FIN DATOS ──

BACKEND = Path(__file__).resolve().parent.parent
REPO = BACKEND.parent
sys.path.insert(0, str(BACKEND))
sys.path.append(str(REPO / "ia"))
os.environ["FIREBASE_DB_URL"] = ""          # no network: sensor falls back to the flagged mock

import crops          # noqa: E402
import engine         # noqa: E402
import main           # noqa: E402
import nasa_power     # noqa: E402
import sensor         # noqa: E402

LAT, LON = nasa_power.LAT, nasa_power.LON


def fails(strategy):
    r = strategy["resiliencia"]
    return r["anios_total"] - r["anios_ok"]


def rec(previos, prioridades=None, **kw):
    return engine.recommend(LAT, LON, "franco", previos, prioridades or DEFAULT_PRIORITIES, **kw)


class TestData(unittest.TestCase):
    def test_every_crop_value_has_a_source(self):
        errors, values, sources, gaps = crops.validate()
        self.assertEqual(errors, [])
        self.assertTrue(all(v["source_id"] in sources for v in values))

    def test_unsourced_value_is_rejected(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            for f in crops.CROP_DIR.iterdir():
                shutil.copy(f, tmp / f.name)
            with (tmp / "crop_values.csv").open("a", encoding="utf-8") as fh:
                fh.write("alfalfa,frost_tc_flowering,,-3,-2,°C,,,invented\n")
            old, crops.CROP_DIR = crops.CROP_DIR, tmp
            try:
                errors = crops.validate()[0]
            finally:
                crops.CROP_DIR = old
            self.assertTrue(any("NO SOURCE" in e for e in errors))
        finally:
            shutil.rmtree(tmp)

    def test_climate_years_and_driest_year(self):
        self.assertEqual(engine.YEARS[0], 1981)
        self.assertEqual(engine.YEARS[-1], 2025)
        self.assertEqual(len(engine.YEARS), 45)
        totals = {}
        for r in nasa_power.load_daily():
            if r["year"] in engine.YEARS and r["PRECTOTCORR"] is not None:
                totals[r["year"]] = totals.get(r["year"], 0) + r["PRECTOTCORR"]
        driest = min(totals, key=totals.get)
        self.assertEqual(driest, DRIEST_YEAR)
        self.assertAlmostEqual(totals[driest], DRIEST_MM, delta=0.5)

    def test_soil_n_classes_nom021(self):
        self.assertEqual(engine.n_class(5)["class_id"], "muy_bajo")
        self.assertEqual(engine.n_class(15)["class_id"], "bajo")
        self.assertEqual(engine.n_class(20)["class_id"], "medio")
        self.assertEqual(engine.n_class(50)["class_id"], "alto")
        self.assertEqual(engine.n_class(80)["class_id"], "muy_alto")
        self.assertIsNone(engine.n_class(None))


class TestEngineResults(unittest.TestCase):
    def test_crop_failures_on_loam(self):
        for crop, expected in EXPECTED_CROP_FAILS_LOAM.items():
            got = sum(not engine.evaluate(crop, y, "franco")["ok"] for y in engine.YEARS)
            self.assertEqual(got, expected, f"{crop}: {got} failed seasons, expected {expected}")

    def test_pitch_case(self):
        out = rec(PITCH_FARMER)
        self.assertEqual(out[0]["ciclos"], ["maiz", "maiz", "maiz"])
        self.assertEqual(fails(out[0]), PITCH_CURRENT_FAILS)
        self.assertEqual(out[1]["ciclos"], PITCH_BEST)
        self.assertEqual(fails(out[1]), PITCH_BEST_FAILS)

    def test_per_year_results_match_totals(self):
        for s in rec(PITCH_FARMER):
            self.assertEqual(len(s["anios"]), 45)
            self.assertEqual(sum(a["ok"] for a in s["anios"]), s["resiliencia"]["anios_ok"])
            self.assertTrue(all("motivo" in a for a in s["anios"] if not a["ok"]))

    def test_do_no_harm(self):
        for previos in (["maiz", "maiz"], ["frijol", "frijol"], ["maiz", "frijol"], ["alfalfa", "alfalfa"]):
            out = rec(previos)
            for alt in out[1:]:
                self.assertLessEqual(fails(alt), fails(out[0]), f"{previos}: {alt['ciclos']} is worse")

    def test_alternatives_are_distinct_from_current(self):
        out = rec(PITCH_FARMER)
        current = sorted(out[0]["ciclos"])
        self.assertTrue(all(sorted(a["ciclos"]) != current for a in out[1:]))
        self.assertEqual(len({tuple(a["ciclos"]) for a in out[1:]}), 3)

    def test_semaforo_ignores_priorities(self):
        a = rec(["avena", "frijol"], {"agua": 0, "suelo": 0, "ingreso": 1, "riesgo": 0})
        b = rec(["avena", "frijol"], {"agua": 0, "suelo": 0, "ingreso": 0, "riesgo": 1})
        self.assertEqual(a[0]["semaforo"], b[0]["semaforo"])
        for s in a + b:
            share = s["resiliencia"]["anios_ok"] / s["resiliencia"]["anios_total"]
            expected = "verde" if share >= 0.9 else "amarillo" if share >= 0.75 else "rojo"
            self.assertEqual(s["semaforo"], expected)

    def test_less_rain_never_helps(self):
        base = sum(not engine.evaluate("frijol", y, "franco")["ok"] for y in engine.YEARS)
        dry = sum(not engine.evaluate("frijol", y, "franco", -20, 0)["ok"] for y in engine.YEARS)
        self.assertGreaterEqual(dry, base)

    def test_bad_year_2011_fails_everything(self):
        for s in engine.bad_year(2011, LAT, LON, "franco", PITCH_FARMER, DEFAULT_PRIORITIES):
            self.assertEqual(s["semaforo"], "rojo")
            self.assertNotIn("anios", s)

    def test_contract_fields(self):
        keys = {"id", "es_actual", "ciclos", "semaforo", "puntaje", "resiliencia", "peor_anio",
                "porque", "beneficios", "huecos", "riesgos", "fuentes", "anios"}
        for s in rec(PITCH_FARMER):
            self.assertTrue(keys <= set(s), keys - set(s))
            self.assertTrue({"anio", "motivo"} <= set(s["peor_anio"]))


class TestSensorAndApi(unittest.TestCase):
    def test_mock_n_is_never_used(self):
        reading = sensor.latest_reading(force=True)
        self.assertTrue(reading["mock"])
        self.assertIsNone(main._real_n(reading))
        out = rec(PITCH_FARMER, sensor_n=main._real_n(reading))
        self.assertTrue(any("No live soil N reading" in h for h in out[0]["huecos"]))

    def test_real_low_n_favours_legumes(self):
        out = rec(PITCH_FARMER, sensor_n=12)
        self.assertIn("SENSOR n_mgkg", out[1]["fuentes"])
        self.assertTrue(any(_ in out[1]["ciclos"] for _ in ("frijol", "alfalfa")))

    def test_partial_npk_reading_is_accepted(self):
        r = sensor._validate({"ts": 1794700000, "n_mgkg": 14, "p_mgkg": 18, "k_mgkg": 150,
                              "humedad_pct": None, "ph": None})
        self.assertEqual(r["n_mgkg"], 14.0)
        self.assertIsNone(r["humedad_pct"])

    def _reading_from_firebase(self, raw):
        """Run latest_reading() with a fake Firebase answer (no network)."""
        old_get, old_url = sensor._get_json, os.environ.get("FIREBASE_DB_URL")
        sensor._get_json = lambda path, params=None: raw
        os.environ["FIREBASE_DB_URL"] = "https://fake.example"
        try:
            return sensor.latest_reading(force=True)
        finally:
            sensor._get_json = old_get
            os.environ["FIREBASE_DB_URL"] = old_url or ""
            sensor._cache.update(at=0.0, value=None)

    def test_test_data_is_never_field_truth(self):
        r = self._reading_from_firebase({"ts": 1794695592, "n_mgkg": 32, "fuente": "TEST"})
        self.assertEqual(r["fuente"], "TEST")          # label kept, never relabelled as SENSOR
        self.assertTrue(r["mock"])
        self.assertIsNone(main._real_n(r))

    def test_real_sensor_reading_is_used(self):
        r = self._reading_from_firebase({"ts": 1794695592, "n_mgkg": 14, "fuente": "SENSOR"})
        self.assertFalse(r["mock"])
        self.assertEqual(main._real_n(r), 14.0)

    def test_all_zero_reading_is_a_sensor_failure(self):
        r = self._reading_from_firebase({"ts": 1794695841, "n_mgkg": 0, "p_mgkg": 0, "k_mgkg": 0,
                                         "humedad_pct": 0.0, "temp_c": 0.0, "ph": 0.0, "ce_uScm": 1000,
                                         "fuente": "SENSOR"})
        self.assertTrue(r["mock"])
        self.assertIn("all zeros", r["motivo_mock"])
        self.assertIsNone(main._real_n(r))

    def test_a_single_zero_is_still_a_measurement(self):
        r = self._reading_from_firebase({"ts": 1794695841, "n_mgkg": 0, "p_mgkg": 12, "k_mgkg": 140,
                                         "fuente": "SENSOR"})
        self.assertFalse(r["mock"])

    def test_unlabeled_reading_is_not_real(self):
        r = self._reading_from_firebase({"ts": 1794695592, "n_mgkg": 14})
        self.assertTrue(r["mock"])

    def test_ms_timestamp_is_converted(self):
        self.assertEqual(sensor._validate({"ts": 1794700000123, "n_mgkg": 1})["ts"], 1794700000)

    def test_empty_reading_is_rejected(self):
        with self.assertRaises(ValueError):
            sensor._validate({"ts": 1, "humedad_pct": None})

    def test_recomendar_endpoint(self):
        out = main.recomendar(main.RecomendarIn(cultivos_previos=PITCH_FARMER))
        self.assertEqual(len(out["estrategias"]), 4)
        self.assertIn("calibracion", out)
        self.assertTrue(out["sensor"]["mock"])
        if main.agregar_incertidumbre:
            self.assertIn("metodo", out["estrategias"][0]["resiliencia"])

    def test_unknown_crop_is_rejected(self):
        with self.assertRaises(ValueError):
            rec(["papa"])


# English fragments produced by engine.py / gaps.csv that Role 3 must translate in Spanish answers.
ENGLISH_ENGINE_FRAGMENTS = [
    "Would have failed", "by drought", "by frost", "lacked water", "Frost hit", "Repeats the",
    "Assumes rainfed", "is a legume", "Alternates plant families", "Enough water in every",
    "Your soil N reads", "Soil N comes from", "No live soil N reading", "Climate data is from",
    "of the water it needs", "expected yield loss", "vs normal", "review with an agronomist",
    "were not found online", "No sourced seed cost",
]


class TestSpanishTranslation(unittest.TestCase):
    """Role 3 translates engine sentences by pattern: a reworded sentence would leak English."""

    def test_every_gap_text_is_translated(self):
        """Reads data/crops/gaps.csv live: a NEW gap row without a Spanish pattern fails here."""
        try:
            import traduccion
        except Exception:
            self.skipTest("ia/traduccion.py not available")
        import csv
        with (crops.CROP_DIR / "gaps.csv").open(encoding="utf-8") as f:
            details = [r["detail"] for r in csv.DictReader(f)]
        untranslated = [d for d in details if traduccion.traducir_es(d) == d]
        self.assertEqual(untranslated, [], "gaps.csv rows without Spanish translation "
                                           "(tell Role 3 to add them to ia/traduccion.py)")

    def test_spanish_answers_have_no_english_engine_text(self):
        try:
            import rutas
        except Exception:
            self.skipTest("ia/rutas.py not available")
        cases = [
            rec(PITCH_FARMER),
            rec(["frijol", "frijol"]),
            rec(PITCH_FARMER, sensor_n=12),            # low real N texts
            rec(PITCH_FARMER, temp_c=-4),              # frost texts
        ]
        questions = ["¿Qué me conviene sembrar?", "¿Por qué mi rotación actual está en rojo?",
                     "¿Qué falta saber?", "¿Cuál falla menos?", "¿Cuál fue el peor año?"]
        for estrategias in cases:
            recomendacion = main._envelope(estrategias, sensor.latest_reading())
            for q in questions:
                ans = rutas.preguntar(rutas.Pregunta(pregunta=q, recomendacion=recomendacion))["respuesta"]
                leaked = [f for f in ENGLISH_ENGINE_FRAGMENTS if f in ans]
                self.assertEqual(leaked, [], f"{q!r} leaked English: {leaked}\n{ans}")


if __name__ == "__main__":
    unittest.main()
