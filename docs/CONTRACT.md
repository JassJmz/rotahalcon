# API & data contract (contrato)
**Nadie cambia estos formatos sin avisar a todos.** Desde la hora 1, cada quien trabaja con **datos falsos (mock)** que respeten este formato, para no esperar a los demás.

### Firebase — lecturas del sensor (lo escribe Hardware y lo leen Backend y Web)
Ruta: `nodos/agrisense-01/lecturas/{timestamp}` y `nodos/agrisense-01/ultima`
```json
{ "ts": 1794700000, "humedad_pct": 24.1, "temp_c": 19.3, "ph": 7.2,
  "ce_uScm": 410, "n_mgkg": 32, "p_mgkg": 18, "k_mgkg": 145, "fuente": "SENSOR" }
```
(Las unidades se confirman con el modelo real del sensor; si cambian, avisar.)

### API del backend (la hace Backend/IA y la usa Web)
**`POST /recomendar`**
```json
{ "lat": 24.02, "lon": -104.65, "suelo": "franco",
  "cultivos_previos": ["frijol", "frijol"],
  "prioridades": { "agua": 0.4, "suelo": 0.3, "ingreso": 0.2, "riesgo": 0.1 },
  "escenario": { "lluvia_pct": 0, "temp_c": 0 } }
```
Respuesta:
```json
{ "estrategias": [
    { "id": "actual", "es_actual": true, "ciclos": ["frijol","frijol","frijol"],
      "semaforo": "rojo", "puntaje": 41,
      "resiliencia": { "anios_ok": 33, "anios_total": 42, "rango": [30, 35] },
      "peor_anio": { "anio": 2011, "motivo": "lluvia 45% abajo del promedio" },
      "porque": "texto corto", "beneficios": ["..."], "huecos": ["..."],
      "riesgos": ["..."], "fuentes": ["NASA POWER PRECTOTCORR", "FAO ..."] }
  ],
  "sensor": { "...última lectura...": "" },
  "calibracion": { "satelite_pct": 18, "sensor_pct": 24, "ajuste": 6, "error": 3, "modelo": "lineal" } }
```
**`GET /anio-malo?anio=2011&lat=..&lon=..`** devuelve lo mismo, pero solo para ese año.
**`POST /preguntar`** recibe `{ "pregunta": "...", "recomendacion": {...} }` y devuelve `{ "respuesta": "...", "fuentes": ["..."] }`.


> Spanish working version for the team; English version before final submission.
