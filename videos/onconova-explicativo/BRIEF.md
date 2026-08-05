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
- **El nombre del PDF no es su inventario.** `IHQ260001 al IHQ260050.pdf` no
  trae 50 casos: trae **82**, porque cada archivo arrastra casos de lotes
  vecinos. El árbol de la escena 6 llevaba «(50/50)» inventado; los reales son
  82 · 92 · 93 · 84, leídos de `auditoria/casos_por_pdf.json`. Lo mismo con los
  tamaños, las fechas y el «5 elementos» que se contradecía con la lista visible
  (la carpeta tiene 404). **Cualquier cifra de la carpeta se mide en disco.**
- **Una ventana del producto se cita entera: valor Y formato.** El resumen de
  importación mostraba «12 · 11 · 1 · 92 %», inventado, y además con un formato
  que la aplicación no usa: el badge es una f-string de Python
  (`f"{porcentaje_exito:.1f}%"`), o sea punto y un decimal. Y la barra de
  progreso cuenta ARCHIVOS (`Procesando (2/4)`) mientras el resumen cuenta
  REGISTROS: no son lo mismo, y el borrador los había mezclado.
- **🔴 `casos_por_pdf.json` no es la cifra buena — caí dos veces.** Es el barrido
  CRUDO del texto, con las referencias cruzadas a informes ajenos dentro; la
  intersección con el rango del nombre la hace `core/estado_pdfs.py` DESPUÉS.
  Corregí «(50/50)» por «(82/82)» creyendo que arreglaba una cifra falsa, y puse
  otra: el contador que el producto escribe es `({en_bd}/{total})` con el total
  ya intersecado, o sea **(45/45) (50/50) (50/50) (48/48)**. El 82 no puede
  aparecer en esa pantalla. Igual con el resumen: de los 347 casos que reuní así,
  **14 no existían como registro** y el checker los devolvía como «Registro no
  encontrado» — contados como incompletos. Aquello inflaba el fallo al triple.
  Lo real, sobre los dos PDF que el lote procesa de verdad: **98 · 96 · 2 ·
  98.0 %**. Regla: si una cifra imita una pantalla, la fuente es el código que
  la pinta o la BD, nunca un JSON de caché; y toda lista de casos se filtra
  contra `informes_ihq` antes de medir completitud.
- **Una pantalla no puede desmentir a la voz cuatro segundos después.** «Selec­-
  cionar pendientes» dejaba fuera, a la vista, las dos filas ✓ … y el lote
  arrancaba justo por esas dos, y contaba 4 cuando se habían marcado 12. La voz
  vende ese botón como el ahorro de trabajo de la semana, delante de quien lo va
  a usar. Ahora los únicos pendientes del árbol son los dos que se procesan.
- **Un estado escenificado se declara.** Hoy los cuatro PDF están COMPLETO en la
  base, así que el ◐ y el ● de la escena están puestos: sin pendientes no hay
  importación que enseñar. Escenificar el ESTADO es legítimo; inventarse los
  DENOMINADORES no lo es.
- **🔴 Un arreglo automático puede romper lo que no miraba.** El pase que escapó
  los `id` que empiezan por dígito (`#05-datos` → `[id="05-datos"]`) se comió
  también **nueve colores hexadecimales**: `stroke='#22304a'` acabó como
  `stroke='[id="22304a"]'`. Efecto: la lupa del buscador y un aro del donut
  invisibles, el cursor sin contorno, las cabeceras que nunca oscurecían y la
  pestaña pulsada que nunca se resaltaba. **Ninguno daba error**; salieron
  porque el verificador de contraste señaló los elementos que seguían apagados.
  Un `replace` con regex sobre HTML se audita después, siempre.
- **Escena nueva = escena que suelta su contenido.** Las cuatro escenas del
  recorrido se escribieron sin la suelta que ya tenían las nueve originales, y
  en la costura 7→8 se veían **dos interfaces superpuestas** y el marcador hecho
  un amasijo («078//133—LASSVISTAS» = «07 / 13 — LAS VISTAS» sobre
  «08 / 13 — LOS DATOS»). Toda escena apaga su contenido, su marca y su marcador
  antes del encadenado y se queda solo con el fondo navy, que es idéntico en las
  trece. Ese fondo común es lo que hace que la imagen no se corte nunca.
- **…y el relevo lo hace el MONTAJE, no cada escena.** Que cada escena apagara
  su contenido antes del cruce dejaba el cuadro **vacío**: se apagaba en
  `D−1,15`, justo cuando la siguiente empieza a aparecer desde opacidad cero.
  Medido con `signalstats` sobre el render: **cinco costuras** caían a navy
  pelado —las cinco en las que la escena saliente es una pantalla clara— y en
  una de ellas medio segundo largo de nada. Y quitar la suelta devolvía las dos
  interfaces superpuestas. La salida está en el montaje: **la saliente se
  desvanece en 0,45 s y la entrante llega en 0,55 s, las dos con `power2.out`**,
  arrancando a la vez. La suma de opacidades nunca baja de 0,9 —no hay hueco— y
  la saliente cae tan deprisa que la ventana en que se leen las dos dura ~0,15 s:
  un encadenado normal. Debajo no asoma nada raro porque `#root` es exactamente
  el mismo `#141d2b` que el fondo de las trece escenas.
- **Un tiempo escrito DENTRO de una escena no cae donde parece.** Las nueve
  originales reescalan su línea con `tl.duration(D)` al final, cada una con su
  factor. Ancié la suelta dividiendo por ese factor —tomado en el navegador con
  `tl.duration()` sin argumento— y aun así **02-encerrado se disparaba 0,9 s
  antes de tiempo**. Por eso la continuidad se resolvió arriba: el montaje es el
  único sitio donde el tiempo absoluto es el que se escribe. Regla: lo que deba
  ocurrir en un instante EXACTO del vídeo no se escribe dentro de una escena que
  reescala.
- **Un `check` en verde con el muestreo por defecto prueba poco.** Toma 9
  instantes en 339 s. La corrección de contraste a alpha 0,72 se había quedado
  en dos escenas de cinco y el verificador seguía dando 0 avisos, porque no cayó
  en los beats donde se ve ese texto. Para dar algo por bueno hay que muestrear
  los instantes que importan (`--at`), no confiar en la rejilla.
- **Un diálogo se abre opaco.** Fundir opacidad y escala juntas durante medio
  segundo deja ver el panel POR DEBAJO de la ventana modal — el mismo artefacto
  de «se ve lo de detrás» que ya nos costó una corrección en la marca de
  esquina. Opacidad en 0,16 s, escala en 0,5 s, por separado.
- No es una grabación de pantalla: HyperFrames renderiza desde HTML. Las
  pantallas son reconstrucciones fieles, decisión asumida por el usuario.
- Paleta tomada del propio producto (navy `#2d3e5e`) para que el vídeo y la
  aplicación se reconozcan como lo mismo.
