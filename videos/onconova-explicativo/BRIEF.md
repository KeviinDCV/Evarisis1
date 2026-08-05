---
workflow: general-video
flow: companion
storyboard: yes
message: "El dato oncológico del HUV deja de estar encerrado en PDFs: se consulta, se analiza y se puede verificar contra el informe original"
destination: presentation
aspect: 1920x1080
language: es
audience: "profesionales sanitarios y de gestión del HUV"
length: 3m30s
angle: showcase
---

## Intent

Vídeo explicativo de ONCONOVA — Gestor Oncológico del Hospital Universitario del
Valle — para proyectar ante una sala de profesionales. Debe explicar qué hace la
aplicación, **cómo es su flujo de funcionamiento**, enseñar los datos y recorrer
la estructura del informe estadístico en PDF.

Tono profesional e institucional, no publicitario: la audiencia son clínicos y
gestores, no compradores. La credibilidad pesa más que el impacto — el vídeo
debe sonar a herramienta clínica seria, no a demo de producto.

Narración con voz natural, en español.

## Assets

- `~/Documents/ONCONOVA Cirugía Oncológica/Exportaciones Base de datos/Informes estadísticos/Informe_estadistico_ONCONOVA.pdf`
  — el informe estadístico real, 5 páginas. Es material AGREGADO y anónimo:
  se puede mostrar tal cual. Fuente de la escena 7.

## Customizations

- **Pantallas recreadas en HTML con identidades ficticias.** Decisión del
  usuario. La estructura, el número de columnas y la volumetría son las reales;
  los nombres y cédulas, inventados. Ninguna captura de la app real entra en el
  vídeo.
- **Voz: Kokoro `ef_dora`, local, velocidad 0,88.** Elegida por el usuario tras
  comparar las tres voces españolas del motor. Decisión deliberada de NO firmar
  en HeyGen: la síntesis corre en el equipo y ni el texto de la narración sale
  a la nube. Requiere `HYPERFRAMES_PYTHON="C:\Program Files\Python313\python.exe"`
  — el `python3` del PATH es el stub de la Store y no tiene las dependencias.
- **Páginas reales del informe en la escena 7.** El PDF es agregado y anónimo;
  se rasterizan sus 5 páginas a **2143×3031** (3,6×) en `assets/informe/`.
  **Regla de nitidez:** la hoja se maqueta a 1071×1515 — la MITAD exacta del
  PNG— y la cámara nunca pasa de escala 2,0. Ahí es 1:1 contra el origen; por
  encima el navegador estira el mapa de bits y el texto se vuelve papilla.
  Primera versión: hojas a 328 px ampliadas por la cámara → ilegible.
- **Montaje continuo: tres reglas, las tres aprendidas a golpes.**
  1. *La duración la manda la voz.* Dar a cada escena una «pausa de diseño» al
     final acumuló 25,24 s de silencio (11 % del vídeo; la apertura sola tenía
     5,4 s). Cada línea entra 0,35 s después de callar la anterior.
  2. *No desvanecer la escena saliente.* Encadenar dos fondos idénticos
     fundiendo uno mientras aparece el otro da `navy·(t+(1−t)²)`: a mitad del
     cruce el cuadro se oscurece un 25 %. La entrante es opaca y aparece
     ENCIMA; la saliente se retira sola al acabar su ventana.
  3. *Cero escalas en la transición.* Un empuje del 2 % en la saliente —o una
     entrada al 97,8 %— descuadra el cromo de esquina, que es idéntico en
     todas las escenas, y se ve como eco doble. Opacidad pura.
  Y el relevo en sí: cada escena **suelta su contenido** 0,55 s antes del
  cruce y se queda solo con el fondo. Como el fondo es el mismo navy en todas,
  en la costura la imagen no cambia: solo se releva lo que hay encima.
- **Un id CSS no puede empezar por dígito.** `#08-verificacion-escena` es un
  selector inválido y tira un error de consola que hace fallar el `check`.
  Para ids así, selector por atributo: `[id="08-verificacion-escena"]`.
- **El cromo nunca se solapa con contenido claro.** La escena 7 encierra el
  recorrido en un visor (80, 150, 1760×800) que no llega a las esquinas, así
  que los rótulos se apoyan siempre en el escenario navy. Antes las páginas
  invadían esa franja y se tapaban con un degradado: el parche se veía como
  una banda clara cruzando el cuadro. **No usar scrims para tapar; recortar.**

## Notes

- **Ley 1581 (Habeas Data).** Ningún dato identificable de paciente puede
  aparecer en pantalla. Las cifras agregadas (2.076 casos, 67,1 % malignos,
  22.547 estudios…) NO identifican a nadie y sí se muestran.
- **🔴 Incidente detectado y corregido — números de caso.** El primer boceto de
  la escena 5 usaba IHQ251204/217/233/248/261 como identificadores «ficticios».
  **Los cinco existen en la BD de producción** y pertenecen a pacientes reales
  con patología distinta a la proyectada (IHQ251204 es un schwannoma de
  orofaringe, no un carcinoma ductal de mama). Con una audiencia que tiene
  acceso al sistema, el nº de petición resuelve a una cédula real. Sustituidos
  por **IHQ259001–259005**, verificados libres contra la BD viva (el número real
  más alto es el 1526). Los nombres también se verificaron uno a uno contra los
  25.481 de la base.
  **Regla para cualquier material futuro:** un identificador inventado no es
  ficticio hasta que se comprueba contra la base de datos.
- **Los rótulos de la UI se leen del código, no de memoria.** Pestañas reales:
  Estadísticas Generales · Visualizador de Datos · Por Paciente · Biomarcadores ·
  Análisis de Malignidad. La vista Por Paciente tiene 6 columnas y **ninguna de
  nombre** (Cédula · Estudios · Órgano · Diagnóstico · Biomarcadores · Fecha) —
  un acierto de privacidad del producto que el vídeo debe mostrar tal cual.
- Las cifras en pantalla son las verificadas en la auditoría de la V6.9.91:
  765 PDFs · 22.547 estudios · 2.076 IHQ · 18.271 pacientes · 67,1 % malignos ·
  2.034 de 2.076 diagnósticos comprobados literalmente contra su PDF.
- **Cifras del informe, contrastadas contra el propio PDF (no de memoria):**
  página 1 → 2.076 casos · 67,1 % malignos · 195 categorías anatómicas ·
  122 biomarcadores. Página 2 → 2.004 con diagnóstico (1.568 tumores +
  436 no neoplásicos) y 72 sin diagnóstico específico.
  El primer guion decía «1.566 tumores / 74 sin diagnóstico»: **era falso** y se
  corrigió. En un vídeo cuyo remate es la verificabilidad, una cifra que
  contradiga el PDF en pantalla es el fallo más caro que existe.
- La tabla de la escena 6 reproduce la de la app (`enhanced_database_dashboard.py`
  → `update_malignancy_biomarker_table`), no una agregación hecha para el vídeo.
  Se muestran las 5 filas con dato; PDL-1 y «P16 %» salen a cero en las cuatro
  columnas —columnas duplicadas del esquema— y se omiten para no aparentar avería.
- No es una grabación de pantalla: HyperFrames renderiza desde HTML. Las
  pantallas son reconstrucciones fieles, decisión asumida por el usuario.
- Paleta tomada del propio producto (navy `#2d3e5e`) para que el vídeo y la
  aplicación se reconozcan como lo mismo.
