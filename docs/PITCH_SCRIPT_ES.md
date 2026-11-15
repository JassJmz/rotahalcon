# RotaHawk — guion del pitch en español (4 minutos)

Versión local. La versión internacional está en `PITCH_SCRIPT.md` (inglés).
**Solo Jass habla. El pitch puede durar de 3 a 5 minutos; este guion es de 4:00.** Para llegar a 3:30, acorta la slide 4 (omite la explicación del chat, −15 s) y la última frase de la slide 6 (−8 s). Si tienes hasta 5:00, deja correr la animación dos veces o abre la web en vivo para los jueces.

Slides en español: `web/slides/es.html` (clic o flechas; F = pantalla completa; Ctrl+P = exportar a PDF). La animación en español va incluida (`?lang=es`).
Los números de las slides y la animación salen de `web/animacion/data.js` (resultado del motor). **Si el motor cambia, correr `python build_data.py` en `web/animacion/` y revisar los números de abajo.**
Ejemplo actual (agricultor de maíz, Durango, 45 temporadas 1981–2025): la rotación actual falla **23**; la mejor alternativa (frijol, frijol, sorgo) falla **9**; peor año **1997**, lluvia 56 % por debajo de lo normal.

| Slide | Tiempo | Quién |
|---|---|---|
| 1 Portada | 0:00–0:10 | Jass |
| 2 El problema | 0:10–0:55 | Jass |
| 3 Animación (~30 s, se reproduce sola) | 0:55–1:30 | Jass (la frase de la IA va sobre la escena del asistente) |
| 4 El resultado (capturas de la web) | 1:30–2:20 | Jass |
| 5 Prototipo en vivo | 2:20–3:00 | Jass narra; Jean clava el nodo en la maceta, sin hablar |
| 6 Impacto y validez | 3:00–3:45 | Jass |
| 7 Cierre | 3:45–4:00 | Jass |

La web completa y el chat en vivo se muestran **solo si los jueces preguntan** (escanear el QR de la slide 7 o abrir el sitio).

## Guion

**1 · Portada (10 s)**
"Buenos días. Somos Halcones Dorados, de Durango. Esto es RotaHawk: la rotación inteligente de cultivos para la resiliencia climática."

**2 · El problema (45 s)**
"Les presento a don José, un agricultor de ejemplo en Durango. Siembra maíz en cada ciclo, y cada temporada decide qué sembrar sin saber cómo le iría en un año malo. Un solo año malo le puede costar la cosecha, el agua y su suelo.
Pero hay un dato que sí existe: la NASA tiene datos del clima desde 1981. Con NASA POWER tomamos, para el campo de don José, datos diarios de lluvia, temperatura mínima y humedad del suelo en la zona de raíces: más de 16 mil días, 45 años completos.
Entonces preguntamos: en esos 45 años de datos reales, ¿cuántas veces le habría fallado el maíz? La respuesta: 23 temporadas de 45."

**3 · Animación (35 s) — se reproduce sola y avanza sola a la slide 4**
"Nuestro nodo RotaHawk es un sensor de suelo NPK: una lectura indicativa, no de laboratorio, que se manda a la nube cada minuto. El dato de la NASA cubre una celda de decenas de kilómetros; nosotros medimos este campo y corregimos el dato de la NASA con la tierra. Hoy esa calibración son datos de ejemplo: es nuestro próximo módulo. Luego probamos cada rotación en cada uno de los 45 años de la NASA. Rojo significa que el cultivo falla. «Nuestro asistente nunca inventa números: responde solo con datos de la NASA, del sensor y de la FAO, y cuando no sabe, lo dice.»"

**4 · El resultado (50 s)**
"El maíz de don José falla en 23 de 45 temporadas. Frijol, frijol y sorgo: 9. Y mostramos el peor año, no el promedio: 1997, cuando en la temporada llovió 56 % menos de lo normal. Y lo normal no lo inventamos: es el promedio 1991–2020 de los mismos datos de la NASA. Cada número en pantalla lleva su etiqueta: NASA, sensor o FAO.
 Le preguntamos al asistente cuánto va a ganar por hectárea. Responde: «No tengo ese dato. Confírmalo con un agrónomo de tu zona.» No tenemos precios con fuente para Durango, así que no se inventa uno."

**5 · Prototipo en vivo (40 s) — Jean clava el nodo en la maceta, sin hablar**
"Ahora lo real. En pantalla, la lectura del suelo de nuestro prototipo, con la etiqueta SENSOR. Es una lectura indicativa y viaja a la nube cada minuto."

**6 · Impacto y validez (45 s)**
"Por qué se puede confiar: todo parte de datos reales de la NASA: lluvia, temperatura mínima y humedad del suelo, todos los días desde 1981, 45 temporadas completas. Con ellos aplicamos reglas de agua y helada de cultivos de la FAO, y damos un rango en lugar de un solo número: la mejor opción funciona en 36 de 45 temporadas, rango de 31 a 40. Calibrar el dato de la NASA con nuestro sensor de campo es el próximo módulo: hoy son datos de ejemplo, y lo decimos. Es código abierto. Lo que no sabemos, lo mostramos: fechas locales de siembra y precios. Y es apoyo a la decisión: no sustituye a un agrónomo."

**7 · Cierre (15 s)**
"RotaHawk: rotación inteligente de cultivos para la resiliencia climática. Pruébenlo ahora: escaneen el código o entren a jassjmz.github.io/rotahalcon. Gracias a los datos abiertos de la NASA. Gracias."

## Plan B
- **El nodo en vivo no lee suelo en la slide 5:** la slide muestra sola la **última lectura real grabada** (prueba del 14 de noviembre, con la sonda en el suelo), rotulada como grabada. Di: «Esta es la última lectura real de nuestro nodo, de una prueba de más de tres horas con la sonda en el suelo. En este momento el nodo en vivo no está leyendo, y por eso la marcamos como grabada.» Pasa a la slide 6.
- Sin red: la web usa su respuesta real guardada (aviso OFFLINE SNAPSHOT); la animación corre con archivos locales.
- Si falla la animación: reproducir el MP4 (`animacion/index.html?short=1&lang=es`, grabado en pantalla a 1080p; sirve también como el video de 30 segundos si no permiten diapositivas con animación).
- Preguntas probables de los jueces:
  - *¿El sensor es en vivo?* — El nodo lee suelo real; la calibración con el satélite en la demo son datos de ejemplo y así está etiquetado. Es el próximo módulo.
  - *¿Por qué en 1997 fallaron las dos rotaciones?* — El motor dice que ese año fue demasiado seco para ambas. El punto es 9 fallos en lugar de 23, no cero.
  - *¿De dónde salen los números de los cultivos?* — De reglas de agua y helada de la FAO; los huecos están listados (costo de semilla, precios, fechas de siembra locales).
  - *¿El asistente inventa cosas?* — Solo responde con los datos del reporte y cita NASA, SENSOR o FAO/INIFAP; si falta una fuente, lo dice.
  - *¿Podemos probarlo?* — Sí: escaneen el QR de la slide 7. Ahí están la web, la comparación, el año malo y el chat en vivo.
