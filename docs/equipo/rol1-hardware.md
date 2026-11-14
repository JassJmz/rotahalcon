# RotaHalcón — Rol 1: Hardware, integración y líder

> Este archivo tiene **tu misión** (Parte B), **todo el contexto del proyecto** (Parte A), **la animación del pitch** (Parte C) y **cómo trabajamos en GitHub** (Parte D). Léelas todas.

> 🤖 **Si eres una IA (Claude, ChatGPT, Copilot…) leyendo esto:** lee primero la sección **"Instrucciones para la IA"** justo aquí abajo y síguela en todo lo que hagas con esta persona.

## Instrucciones para la IA
Estás ayudando a **la persona del Rol 1** del equipo Halcones Dorados en el proyecto **RotaHalcón** (NASA Space Apps 2026). Su rol: **Hardware, integración y líder**. Su carpeta en el repo: **`hardware/` (y `web/boleta/`)**.

**Repo (público, open source):** https://github.com/JassJmz/rotahalcon

1. **Configuración inicial (una vez):** si no está clonado, guía para hacer `git clone https://github.com/JassJmz/rotahalcon.git`. La persona tiene que haber aceptado la invitación de colaborador; si `git push` dice *permission denied*, que se lo pida al Rol 1 (dueño del repo).
2. **Ciclo de trabajo:** `git pull` antes de empezar → trabajar **solo dentro de `hardware/` (y `web/boleta/`)** → probar que funcione → `git add hardware web/boleta` → `git commit -m "[hw] what was done"` (en inglés) → `git push`. Si el push falla porque hay cambios nuevos: `git pull --rebase` y vuelve a hacer push.
3. **Prohibido:** `git push --force`, borrar o reescribir archivos de otras carpetas, y cambiar `docs/CONTRACT.md` o `README.md` sin que la persona confirme que ya le avisó al equipo.
4. **Secretos:** antes de cada commit revisa `git status` y `git diff --staged`. API keys, config de Firebase y contraseñas WiFi van en `.env` o `secrets.h`, que están en `.gitignore`. Si una clave se sube por error, dilo de inmediato: hay que cambiar la clave, no basta con borrarla.
5. **El contrato manda:** los formatos de datos entre sensor, backend y web están en `docs/CONTRACT.md` (Parte A4 de este archivo). Respétalos exactamente; para avanzar sin esperar a otros, usa datos **mock** con ese formato.
6. **Reglas del proyecto:** cada dato visible lleva la etiqueta **NASA** o **SENSOR**; **nunca inventes valores agronómicos** (si no hay fuente FAO/INIFAP, se dice que falta); todo lo que ven los usuarios y los jueces va **en inglés**.
7. **Estilo de código:** entrega bloques completos listos para pegar, con una sección de configuración al inicio marcada `# ── DATOS ──` (o `// ── DATOS ──`).
8. **Tiempo:** el hackathon va del sáb 14 nov 12:00 al dom 15 nov 14:30. Prioriza lo que esté en la tabla de entregables de la Parte B y su hora; a partir de H18 solo se arreglan bugs, ya no se agregan funciones.
9. **Al cerrar cada bloque de trabajo:** actualiza el `README.md` de su carpeta con qué funciona y cómo se corre, y haz commit.

# PARTE B — Lo que te toca

## Tu misión
Que el **nodo AGRISENSE** mande lecturas reales a Firebase, que la demo física funcione en la mesa de los jueces y que el equipo llegue a cada punto de control. Además te tocan el **anteproyecto**, la **boleta** (PDF/WhatsApp), el **borrador de la página del proyecto** y ser el **asesor técnico de la animación**: que lo que se dibuje del sensor sea correcto. La animación la construye el Rol 4.

## Entregables
| # | Entregable | Para cuándo |
|---|---|---|
| 1 | **Anteproyecto enviado** (usa `pasos/paso1-historia.pdf`, sección 4) | **Sáb antes de las 23:59** (mejor antes de H8) |
| 2 | **Repo público `rotahalcon` en GitHub** (ya creado, ver Parte D), con los 3 compañeros invitados como colaboradores | **Antes de H0** |
| 3 | Hoja de datos del sensor NPK + explicación de cómo mide y cómo viaja la señal, para el Rol 4 (escenas 1–5 de la animación) | H3 |
| 4 | Nodo AGRISENSE escribiendo en Firebase con el formato del **contrato A4** | H6 |
| 5 | Historial de lecturas (aunque sean pocas horas) para la calibración | H10 en adelante |
| 6 | **Boleta descargable** (PDF o texto para WhatsApp) con el plan, el plan B y el aviso, dentro de `web/boleta/` | H14 |
| 7 | Demo física: el nodo en una maceta con tierra seca y otra húmeda para mostrar el cambio en vivo | H14 |
| 8 | Revisión técnica de la animación (escenas 1–5) | H12 |
| 9 | Texto de **declaración de hardware preexistente + créditos AGRISENSE** + **borrador de la página del proyecto en inglés** | H18 |
| 10 | **Video de respaldo** de la demo completa (por si falla el WiFi) | H20 |

## Paso a paso
1. **H0–1:** confirmar que los 3 aceptaron la invitación al repo y que pueden hacer `git push` (Parte D2), pasarles su archivo de rol y revisar juntos el contrato A4 (10 min, no más).
2. **H1–2:** crear el proyecto Firebase (o reutilizar el de AGRISENSE). Compartir la config con Web y Backend **por chat, no en el repo**. Poner un mock en `nodos/agrisense-01/ultima` para que Web arranque ya.
3. **H1–3 (en ratos):** pasarle al Rol 4 la hoja de datos del sensor y un esquema simple: puntas → MAX485 (RS485/Modbus) → ESP32 → WiFi → Firebase.
4. **H2–6:** firmware: leer el sensor NPK por RS485 (Modbus) y escribir en Firebase cada 30–60 s. **Confirmar el modelo del sensor y sus unidades** y avisar si cambian.
5. **H6–8:** probar que Web ve la lectura en vivo → ✔ **primera integración**.
6. **H8–12:** enviar el anteproyecto (si no se envió), pasarle a IA el historial de lecturas y revisar el Acto 1 de la animación que hizo el Rol 4.
7. **H10–14:** la boleta (con los datos de `/recomendar`) y montar la demo física (macetas seca y húmeda) → ✔ **demo de punta a punta**.
8. **H14–18:** declaración de hardware + créditos y borrador de la página del proyecto en inglés (el Rol 4 lo revisa).
9. **H18–22:** grabar el video de respaldo de la demo y hacer el ensayo general.
10. **H22–26:** en el pitch, tú manejas el **nodo físico durante la demo en vivo** (slide 5) mientras el Rol 4 expone.

## Como líder
- En cada punto de control (H2, H8, H14 y H18) haces un **stand-up de 5 min**: qué funciona, qué está bloqueado y qué se corta.
- A partir de H18: **nada de funciones nuevas**. Si algo no está, se corta sin culpa.
- Si alguien se atora más de 45 min, se cambia a plan B (ver abajo).

## Plan B
- **Si el sensor falla:** se usan lecturas guardadas / mock en Firebase + el video, y se dice con honestidad.
- **Si no hay WiFi en la sede:** compartir datos desde el celular, o usar el GPS-GSM del equipo.

## Lo que te piden los demás
- **Web y Backend:** la config de Firebase y la lectura en vivo.
- **IA:** el historial de lecturas (humedad con su timestamp) para calibrar contra NASA POWER.
- **Rol 4:** la hoja de datos y el esquema del sensor para la animación.

---

# PARTE A — Contexto del proyecto (igual para los 4)

> Si usas una IA (Claude, ChatGPT, etc.) para ayudarte, **pégale este archivo completo**: tiene todo lo que necesita saber.

## A1. Qué es RotaHalcón
- **Evento:** NASA Space Apps Challenge 2026, sede Durango (UNIPOLI). Hackathon: **sáb 14 nov 12:00 → dom 15 nov 14:30** (entrega final y pitch).
- **Equipo:** Halcones Dorados (Mecatrónica, ITSRLL), 4 integrantes.
- **Reto:** *Field Shift: Adapting Farms with NASA Data*. Hay que hacer una herramienta de apoyo a la decisión que use datos de la NASA + información local para elegir **rotaciones de cultivo** que cuiden el suelo y el agua y aguanten el clima. **No es un sistema de riego.**

**El problema:** el agricultor de Durango elige qué sembrar cada ciclo sin saber cómo le iría a esa decisión en un año malo, y un año malo le puede costar la cosecha, el agua y el suelo.

**La solución:** RotaHalcón prueba cada rotación de cultivos contra **más de 40 años de clima real de la NASA**, la ajusta con un **sensor en la parcela** y le dice al agricultor, en palabras sencillas, **cuál aguanta mejor un año malo**.

**Los 3 golpes que nadie más tiene:**
1. **El peor año, no el promedio:** "esta rotación habría fallado 3 de 42 años; la tuya, 9".
2. **El satélite corregido por la tierra:** "la NASA dice 18% de humedad; tu parcela mide 24%. Ajustamos".
3. **Una IA que no inventa:** cada respuesta cita el dato NASA, la lectura del sensor o la fuente FAO/INIFAP.

## A2. Flujo del agricultor
1. Marca su parcela en el mapa, elige el tipo de suelo y los últimos 2 cultivos.
2. El nodo **AGRISENSE** lee su suelo: N, P, K, pH, salinidad (CE), humedad y temperatura.
3. RotaHalcón simula **su rotación actual + 3 alternativas** (3 ciclos cada una) en cada año desde 1981.
4. Ve el comparador: semáforo, cuántos años falla cada opción, el peor año, el porqué, beneficios, **huecos de información**, **riesgos a revisar con un agrónomo** y plan B.
5. Puede preguntarle al asistente IA, mover sliders (prioridades y "¿y si llueve 20% menos?") y descargar la boleta (PDF/WhatsApp).

**Cultivos:** frijol, maíz, avena, sorgo y alfalfa.

## A3. Arquitectura
```
[NASA POWER 1981→hoy] ─┐
[NDVI MODIS/VIIRS]   ──┤
[Nodo AGRISENSE] → Firebase ─┤→ [Backend Python/FastAPI] → [Página web]
[Datos del agricultor] ─┘        ├ Motor de reglas           ├ Mapa, suelo en vivo
                                 ├ Simulación 40 años        ├ Comparador, Tu año malo
                                 ├ Calibración e incertidumbre (IA) ├ Sliders, chat IA
                                 └ Asistente IA              └ Glosario, boleta
```
- **Nodo AGRISENSE:** ESP32 + sensor NPK por RS485 (MAX485) + Firebase. Es hardware **preexistente**, cedido y con permiso de sus autores (Alberto Ortega, Gabriel Jahir Landa, Lizzeth Avalos, Cecilia Reyes y Angel Moreno). **Se declara en la entrega y se les da crédito.**

## A4. EL CONTRATO (lo que permite trabajar en paralelo)
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

## A5. Reglas que NADIE puede romper
1. **Cada dato visible lleva su etiqueta:** **NASA** o **SENSOR**.
2. **No se inventan valores agronómicos** (agua que necesita cada cultivo, fijación de N, etc.). Todo sale de **FAO o INIFAP**, con la referencia guardada.
3. **Todo lo que se entrega va en INGLÉS:** la web, la página del proyecto, las slides y el video.
4. **El uso de IA se declara:** qué herramientas se usaron y para qué. Las imágenes generadas con IA (incluido el logo) llevan **marca de agua visible**. **No se usan logos de la NASA.**
5. **Todos los links son públicos**, sin contraseña.
6. **El proyecto es abierto (open source)**: todo va en el repo público de GitHub (Parte D). Commits chicos y seguido. **Nunca subir claves** (API keys, Firebase, WiFi).
7. **Un solo caso de ejemplo bien hecho** (una parcela de Durango) vale más que muchos a medias.

## A6. Calendario del equipo (H0 = sáb 12:00)
| Hora | Reloj aprox. | Qué pasa | Punto de control |
|---|---|---|---|
| H0–2 | sáb 12–14 | Repo, contrato, mocks y cada quien arranca | ✔ **Todos tienen el mock corriendo** |
| H2–8 | sáb 14–20 | Cada quien construye su parte por separado | ✔ **H8: primera integración** (sensor → web y API → web) |
| H8–14 | sáb 20 – dom 02 | Integrar todo + IA | ✔ **H14: demo completa de punta a punta** |
| H14–18 | dom 02–06 | Pulir, boleta, textos en inglés | ✔ **H18: CONGELAR FUNCIONES** (después solo se arreglan bugs) |
| H18–22 | dom 06–10 | Ensayos, video de respaldo, página del proyecto | ✔ **Entrega lista** |
| H22–26 | dom 10–14:30 | Pitch: ensayar 3 veces, entrega final | ✔ **14:30 entrega + jueces** |

**Pitch: 4 min + 3 min de preguntas.** Máximo 7 slides o video de 30 s. Llevar el nodo físico a la mesa. **Las slides 3 y 4 son una animación de cómo funciona el sensor y RotaHalcón** (ver Parte C).
**Anteproyecto: cierra el sáb 14 nov a las 23:59.** Sin él, hay descalificación.

## A7. Criterios con los que nos califican
Impacto · Creatividad · Validez (científicamente válido) · Pertinencia (responde al reto, es viable y usable) · Presentación · Diversidad.

---

# PARTE C — La animación del pitch (contexto para todos)

> **Objetivo:** que en el pitch (7 slides, 4 min) los jueces **vean** cómo funciona el sensor de suelo y cómo funciona RotaHalcón completo, con una animación espectacular, limpia y técnicamente correcta.
> **Dueño:** **Rol 4 (quien expone)**: storyboard, dibujos, construcción e integración en las slides. Como lo va a contar, lo construye. **Rol 1:** asesor técnico (hoja de datos del sensor; revisa que las escenas 1–5 sean correctas). **Roles 2 y 3:** pasan los números reales a H14.

## C1. Herramienta (decidida)
- **HTML + SVG + GSAP** (librería de animación web), dentro de `web/animacion/`.
  - Corre sin internet en el navegador, a pantalla completa.
  - Avanza **con clic o flecha** (una escena por clic), así se sincroniza con lo que se va diciendo.
  - La misma animación se reutiliza en la web como sección **"How it works"**.
- **Respaldo obligatorio:** grabarla en pantalla en MP4 (1080p) e insertar el video en las slides, por si el navegador falla.
- **Plan C, si a H12 no avanza:** Keynote *Magic Move* o PowerPoint *Morph* con los mismos dibujos SVG.
- **Estilo:** fondo azul marino `#0B1F3A`, dorado `#D4AF37` para el "dato", verde/amarillo/rojo para el semáforo. Corte transversal del suelo estilo ilustración plana, partículas con brillo suave y movimientos con *easing*. Nada de clipart.
- **Imágenes:** dibujar en SVG. Si algo se genera con IA, **lleva marca de agua visible**. **Nada de logos de la NASA** (un satélite genérico sí).
- **Texto en pantalla en inglés** y muy poco: los números grandes, las palabras chicas.

## C2. Storyboard (~60 s en total, 11 escenas)
**Acto 1: "From soil to cloud" (el sensor, ~25 s)**
| # | Escena | Texto en pantalla | Seg |
|---|---|---|---|
| 1 | Parcela de Durango en corte transversal, amanecer. El nodo AGRISENSE baja y se clava en la tierra | *A field in Durango* | 3 |
| 2 | Zoom dentro del suelo: granos, agua e iones (N, P, K) alrededor de las puntas del sensor. Las puntas emiten pulsos al medir | *N · P · K · pH · salinity · moisture* | 6 |
| 3 | La señal viaja por el cable → módulo **MAX485 (RS485/Modbus)** → el **ESP32** se ilumina | *Read every 60 s* | 4 |
| 4 | Ondas WiFi → nube **Firebase** → aparece la tarjeta *SENSOR · Moisture 24%* | *Live, from this field* | 4 |
| 5 | Se aleja la cámara: arriba, un satélite ve la zona como un **píxel gigante de varios km**. *NASA 18%* vs. *SENSOR 24%* chocan y se funden en *Calibrated* | *Satellite sees km. We see your field.* | 8 |

**Acto 2: "RotaHalcón" (el sistema, ~35 s)**
| # | Escena | Texto en pantalla | Seg |
|---|---|---|---|
| 6 | Desfila una línea de tiempo 1981 → 2026: cada año es una barra de lluvia (NASA POWER) | *42 years of real NASA climate* | 6 |
| 7 | 4 filas de rotaciones (la **actual** + 3), cada una con 3 fichas de cultivo. Los años pasan como una ola; cada año que falla se marca en rojo en su fila. La actual se llena de rojo | *Every rotation, every year* | 10 |
| 8 | Contadores: *Current: fails 9 / 42* vs. *Best: fails 3 / 42*. Se resalta el **peor año** | *The worst year, not the average* | 6 |
| 9 | Se mueven los sliders (agua, suelo, ingreso, riesgo) y el ranking se reordena en vivo | *Your priorities, your ranking* | 5 |
| 10 | Burbuja del asistente IA con etiquetas de fuente (NASA / SENSOR / FAO) → la boleta sale al celular del agricultor | *Explained. Sourced. In your pocket.* | 6 |
| 11 | Logo RotaHalcón + frase | *RotaHalcón — rotation as climate insurance* | 3 |

**Exactitud (Validez):**
- Los números de las escenas 4, 5 y 8 son **ilustrativos** hasta H14. Ahí se cambian por los resultados reales del motor (Rol 2) y de la calibración (Rol 3).
- El principio de medición del sensor (escena 2) se dibuja según la **hoja de datos del modelo real**. No se exagera: es una lectura indicativa, no un laboratorio.

## C3. Dónde va en las 7 slides y en los 4 min
| Slide | Contenido | Tiempo |
|---|---|---|
| 1 | Portada | 0:00–0:10 |
| 2 | El problema: Don José + hechos con fuente | 0:10–0:50 |
| 3 | **Animación Acto 1: el sensor** | 0:50–1:20 |
| 4 | **Animación Acto 2: RotaHalcón** | 1:20–2:00 |
| 5 | **Demo en vivo**: la web + el nodo en la maceta | 2:00–3:15 |
| 6 | Impacto + validez (fuentes e incertidumbre) | 3:15–3:50 |
| 7 | Cierre: equipo, créditos AGRISENSE, declaración de IA y link | 3:50–4:00 |

⚠️ **Confirmar con los organizadores:** si una animación o un video dentro de las 7 slides está permitido (la regla dice "7 slides **o** video de 30 s"). Si no se permite, la animación se convierte en el **video de 30 s** (versión corta: escenas 2, 4, 5, 7, 8 y 11) y la sección "How it works" queda en la web.

---

# PARTE D — Proyecto abierto en GitHub (para todos)

> Idea del asesor: RotaHalcón es **open source**. Todo va en un repo **público** de GitHub para que cualquiera conozca el proyecto, lo use en su región y aporte. Además suma en Impacto (escalable) y cumple la regla de links públicos.

## D1. El repo
- **Dueño:** cuenta de GitHub del Rol 1. Repo público: https://github.com/JassJmz/rotahalcon. Los otros 3 entran como **colaboradores** (pueden subir directo).
- **Ya preparado:**
  - `README.md` en inglés (problema, solución, diagrama, fuentes, créditos AGRISENSE, roadmap abierto).
  - `LICENSE`: MIT para el código; docs, imágenes y animación en CC BY 4.0.
  - `CONTRIBUTING.md`: cómo aportar.
  - `.gitignore`: bloquea claves y secretos.
  - Plantillas de issues (idea, bug, dato de cultivo con fuente).
  - `docs/CONTRACT.md`: el contrato A4.
- **Carpetas por rol:**

| Carpeta | Rol |
|---|---|
| `hardware/` | Rol 1 |
| `backend/` y `data/` | Rol 2 |
| `ia/` | Rol 3 |
| `web/` (incluye `web/animacion/`) | Rol 4 (`web/boleta/`: Rol 1) |
| `docs/` | Todos |

## D2. Cómo suben cosas (modo rápido para el hackathon)
1. Crear tu cuenta de GitHub (si no tienes) y pasarle tu **usuario** al Rol 1.
2. Aceptar la invitación que te llega por correo.
3. Clonar una vez: `git clone https://github.com/JassJmz/rotahalcon.git`
4. Antes de empezar: `git pull`
5. Al terminar algo que funcione: `git add <tu carpeta>` → `git commit -m "qué hiciste"` → `git push`
6. **Trabaja solo en tu carpeta.** Si vas a tocar `README.md` o `docs/CONTRACT.md`, avisa primero.
7. Si `git push` falla por cambios de otro: `git pull` y vuelve a hacer `git push`.

## D3. Reglas del repo abierto
- 🔒 **Nunca subir claves:** WiFi, Firebase, API keys. Van en `.env` o `secrets.h`, que el `.gitignore` ya bloquea. Si se sube una por error, **avisar y cambiarla de inmediato** (borrarla del repo no basta).
- 📄 No subir documentos de terceros (PDF de la NASA, memoria de AGRISENSE) sin permiso para publicarlos. **Se enlazan, no se suben.**
- 🌾 Todo dato agronómico se sube con su fuente.
- 🇬🇧 README, issues y commits en inglés (o en español con resumen en inglés).
- ⏰ **Commits seguidos:** el historial muestra que se trabajó durante el evento, y eso protege al equipo.

## D4. Después del evento
- Abrir issues con el roadmap (más cultivos, más regiones, traducciones, validación) para que la gente aporte.
- Compartir el link en redes con #NASASpaceApps (también cuenta para People's Choice).
