# RotaHalcón — guion del pitch en español (4 minutos)

Versión local. La versión internacional está en `PITCH_SCRIPT.md` (inglés).
Slides en español: `web/slides/es.html` (clic o flechas; F = pantalla completa; Ctrl+P = exportar a PDF). La animación en español va incluida (`?lang=es`).
Los números de las slides y la animación salen de `web/animacion/data.js` (resultado del motor). **Si el motor cambia, correr `python build_data.py` en `web/animacion/` y revisar los números de abajo.**
Ejemplo actual (agricultor de maíz, Durango, 45 temporadas 1981–2025): la rotación actual falla **23**; la mejor alternativa (frijol, frijol, sorgo) falla **9**; peor año **1997**, lluvia 56 % por debajo de lo normal.

| Slide | Tiempo | Quién |
|---|---|---|
| 1 Portada | 0:00–0:10 | Quien expone |
| 2 El problema | 0:10–0:50 | Quien expone |
| 3 Animación, parte 1 (sensor, ~13 s) | 0:50–1:10 | Se reproduce sola |
| 4 Animación, parte 2 (el sistema, ~14 s) | 1:10–1:35 | Se reproduce sola |
| 5 Demostración en vivo | 1:35–3:15 | Quien expone maneja la web; Rol 1 maneja el nodo |
| 6 Impacto y validez | 3:15–3:50 | Quien expone |
| 7 Cierre | 3:50–4:00 | Quien expone |

## Guion

**1 · Portada (10 s)**
"Buenos días. Somos Halcones Dorados, de Durango. Esto es RotaHalcón: la rotación de cultivos como seguro contra el clima."

**2 · El problema (40 s)**
"Les presento a don José, un agricultor de ejemplo en Durango. Siembra maíz en cada ciclo. Cada temporada decide qué sembrar sin saber cómo le iría con esa decisión en un año malo. Y un solo año malo le puede costar la cosecha, el agua y su suelo.
Los datos del clima de la NASA son gratuitos, pero cubren kilómetros, no su parcela, y son difíciles de interpretar.
Entonces nos hicimos una pregunta simple: con 45 años de datos reales de la NASA, ¿cuántas veces le habría fallado el maíz a don José? La respuesta: 23 temporadas de 45."

**3 · Animación, parte 1 (20 s) — se reproduce sola (suelo, calibración)**
"Nuestro nodo AGRISENSE lee el suelo: nitrógeno, fósforo, potasio, pH, salinidad y humedad, y lo manda a la nube cada minuto. Un satélite ve un píxel de varios kilómetros; nosotros vemos este campo. Corregimos al satélite con la tierra. En esta demostración esa calibración son datos de ejemplo: es nuestro próximo módulo."

**4 · Animación, parte 2 (25 s) — se reproduce sola (cada rotación, peor año)**
"Después probamos cada rotación en cada uno de los 45 años de datos de la NASA. Rojo significa que el cultivo falla. El maíz de don José falla en 23 temporadas. Frijol, frijol y sorgo, en 9. Y mostramos el peor año, 1997, no el promedio. Vamos a verlo en vivo."

**5 · Demostración en vivo (1:40)**
"Vamos a usarlo. Marco la parcela en el mapa. Aquí está el suelo, en vivo desde nuestro nodo [el Rol 1 toca la sonda]. Aquí hay cuatro rotaciones, lado a lado. La actual de don José está en rojo: funciona en 22 de 45 años. Esta funciona en 36, con un rango, porque no afirmamos tener certeza.
Elijo un año malo, 1997. Miren lo que habría pasado con cada rotación.
Ahora muevo los sliders: más peso al agua, y el ranking cambia. Fíjense en el slider de ingreso: dice hueco de información. No tenemos un costo de semilla ni un precio del cultivo con fuente para Durango, y lo decimos en lugar de fingir.
Pregunto: '¿Por qué mi rotación está en rojo?' La respuesta cita a la NASA y a la FAO, y enumera lo que no sabemos."

**6 · Impacto y validez (35 s)**
"Por qué se puede confiar: 45 temporadas reales de NASA POWER, reglas de agua y helada de cultivos de la FAO, y un rango en lugar de un solo número. Lo que no sabemos, lo mostramos: fechas locales de siembra, precios y la calibración del sensor.
Es código abierto: cualquier región puede conectar sus propios cultivos y su clima. Y es apoyo a la decisión: no sustituye a un agrónomo."

**7 · Cierre (10 s)**
"RotaHalcón: la rotación como seguro contra el clima. Gracias al equipo de AGRISENSE, cuyo nodo hizo esto posible. El código está abierto en GitHub. Gracias."

## Plan B
- Sin red: la web usa su respuesta real guardada (aviso OFFLINE SNAPSHOT); la animación corre con archivos locales.
- Si falla la animación: reproducir el MP4 (`animacion/index.html?short=1&lang=es`, grabado en pantalla a 1080p; sirve también como el video de 30 segundos si no permiten diapositivas con animación).
- Preguntas probables de los jueces:
  - *¿El sensor es en vivo?* — El nodo lee suelo real; la calibración con el satélite en la demo son datos de ejemplo y así está etiquetado. Es el próximo módulo.
  - *¿Por qué en 1997 fallaron las dos rotaciones?* — El motor dice que ese año fue demasiado seco para ambas. El punto es 9 fallos en lugar de 23, no cero.
  - *¿De dónde salen los números de los cultivos?* — De reglas de agua y helada de la FAO; los huecos están listados (costo de semilla, precios, fechas de siembra locales).
  - *¿El asistente inventa cosas?* — Solo responde con los datos del reporte y cita NASA, SENSOR o FAO/INIFAP; si falta una fuente, lo dice.
