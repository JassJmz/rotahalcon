# RotaHawk — guion del pitch en español (4 minutos)

Versión local. La versión internacional está en `PITCH_SCRIPT.md` (inglés).
**Solo Jass habla. El pitch puede durar de 3 a 5 minutos; este guion es de 4:00.** Para llegar a 3:30, acorta la slide 4 (omite la explicación del chat, −15 s) y la última frase de la slide 6 (−10 s). Si tienes hasta 5:00, deja correr la animación dos veces o abre la web en vivo para los jueces.

Slides en español: `web/slides/es.html` (clic o flechas; F = pantalla completa; Ctrl+P = exportar a PDF). La animación en español va incluida (`?lang=es`).
Los números de las slides y la animación salen de `web/animacion/data.js` (resultado del motor). **Si el motor cambia, correr `python build_data.py` en `web/animacion/` y revisar los números de abajo.**
Ejemplo actual (agricultor de maíz, Durango, 45 temporadas 1981–2025): la rotación actual falla **23**; la mejor alternativa (frijol, frijol, sorgo) falla **9**; peor año **1997**, lluvia 56 % por debajo de lo normal.

| Slide | Tiempo | Quién |
|---|---|---|
| 1 Portada | 0:00–0:10 | Jass |
| 2 El problema | 0:10–0:50 | Jass |
| 3 Animación (~30 s, se reproduce sola) | 0:50–1:25 | Jass (la frase de la IA va sobre la escena del asistente) |
| 4 El resultado (capturas de la web) | 1:25–2:15 | Jass |
| 5 Prototipo en vivo | 2:15–3:00 | Jass narra; Jean clava el nodo en la maceta, sin hablar |
| 6 Impacto y validez | 3:00–3:40 | Jass |
| 7 Cierre | 3:40–4:00 | Jass |

La web completa y el chat en vivo se muestran **solo si los jueces preguntan** (escanear el QR de la slide 7 o abrir el sitio).

## Guion

**1 · Portada (10 s)**
"Buenos días. Somos Halcones Dorados, de Durango. Esto es RotaHawk: la rotación inteligente de cultivos para la resiliencia climática."

**2 · El problema (40 s)**
"Les presento a don José, un agricultor de ejemplo en Durango. Siembra maíz en cada ciclo. Cada temporada decide qué sembrar sin saber cómo le iría con esa decisión en un año malo. Y un solo año malo le puede costar la cosecha, el agua y su suelo.
Los datos del clima de la NASA son gratuitos, pero cubren kilómetros, no su parcela, y son difíciles de interpretar.
Entonces nos hicimos una pregunta simple: con 45 años de datos reales de la NASA, ¿cuántas veces le habría fallado el maíz a don José? La respuesta: 23 temporadas de 45."

**3 · Animación (35 s) — se reproduce sola**
"Nuestro nodo AGRISENSE es un sensor de suelo NPK: una lectura indicativa, no de laboratorio, que se manda a la nube cada minuto. Un satélite ve un píxel de varios kilómetros; nosotros vemos este campo, y corregimos al satélite con la tierra. En esta demostración esa calibración son datos de ejemplo: es nuestro próximo módulo. Después probamos cada rotación en cada uno de los 45 años de datos de la NASA. Rojo significa que el cultivo falla. [Cuando corre la escena del asistente:] «Nuestro asistente nunca inventa números: responde solo con datos de la NASA, del sensor y de la FAO, y cuando no sabe, lo dice.»"

**4 · El resultado (50 s)**
"El maíz de don José falla en 23 de 45 temporadas. Frijol, frijol y sorgo: 9. Y mostramos el peor año, 1997, no el promedio. Le preguntamos al asistente cuánto va a ganar por hectárea. Responde: «No tengo ese dato. Confírmalo con un agrónomo de tu zona.» No tenemos precios con fuente para Durango, así que no se inventa uno."

**5 · Prototipo en vivo (45 s)**
"Ahora lo real. [Jean clava el nodo en la maceta, sin hablar.] En pantalla, la lectura del suelo de nuestro prototipo, con la etiqueta SENSOR. [SI LA LECTURA MUESTRA GUIONES, decir: "El nodo está conectado y enviando datos, pero la sonda no está leyendo suelo en este momento. Mostramos guiones y no ceros porque nunca mostramos un número en el que no podemos confiar. En el campo, aquí aparecen los valores del suelo." Luego continuar.] Es una lectura indicativa, no un análisis de laboratorio, y viaja a la nube cada minuto."

**6 · Impacto y validez (40 s)**
"Por qué se puede confiar: 45 temporadas reales de NASA POWER, reglas de agua y helada de cultivos de la FAO, y un rango en lugar de un solo número: la mejor opción funciona en 36 de 45 temporadas, rango de 31 a 40. Calibrar el satélite con nuestro sensor de campo es el próximo módulo: hoy son datos de ejemplo, y lo decimos. Lo que no sabemos, lo mostramos: fechas locales de siembra y precios.
Es código abierto: cualquier región puede conectar sus propios cultivos y su clima. Y es apoyo a la decisión: no sustituye a un agrónomo."

**7 · Cierre (20 s)**
"RotaHawk: rotación inteligente de cultivos para la resiliencia climática. Pueden probarlo ahora: escaneen el código o entren a jassjmz.github.io/rotahalcon. Gracias al equipo de AGRISENSE, cuyo nodo hizo esto posible. El código está abierto en GitHub. Gracias."

## Plan B
- **La lectura de la slide 5 muestra guiones (la sonda devuelve ceros):** no la escondas. Di la frase de las notas de la slide 5, señala el nodo sobre la mesa y pasa a la slide 6. El nodo sigue contando como conectado: los guiones son la página negándose a mostrar un número en el que no confía.
- Sin red: la web usa su respuesta real guardada (aviso OFFLINE SNAPSHOT); la animación corre con archivos locales.
- Si falla la animación: reproducir el MP4 (`animacion/index.html?short=1&lang=es`, grabado en pantalla a 1080p; sirve también como el video de 30 segundos si no permiten diapositivas con animación).
- Preguntas probables de los jueces:
  - *¿El sensor es en vivo?* — El nodo lee suelo real; la calibración con el satélite en la demo son datos de ejemplo y así está etiquetado. Es el próximo módulo.
  - *¿Por qué en 1997 fallaron las dos rotaciones?* — El motor dice que ese año fue demasiado seco para ambas. El punto es 9 fallos en lugar de 23, no cero.
  - *¿De dónde salen los números de los cultivos?* — De reglas de agua y helada de la FAO; los huecos están listados (costo de semilla, precios, fechas de siembra locales).
  - *¿El asistente inventa cosas?* — Solo responde con los datos del reporte y cita NASA, SENSOR o FAO/INIFAP; si falta una fuente, lo dice.
  - *¿Podemos probarlo?* — Sí: escaneen el QR de la slide 7. Ahí están la web, la comparación, el año malo y el chat en vivo.
