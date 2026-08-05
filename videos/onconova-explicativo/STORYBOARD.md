---
format: 1920x1080
duration: 5m33s
message: "El dato oncológico del HUV deja de estar encerrado en PDFs: se consulta, se analiza y se puede verificar contra el informe original — y esto es la aplicación que lo hace, pantalla por pantalla"
arc: "Membrete institucional → El dato encerrado → ONCONOVA → El circuito → La aplicación abre → De la carpeta a la base → Las siete vistas → Los datos → El análisis → El Dashboard → El informe → La verificación → Cierre"
audience: "profesionales sanitarios y de gestión del HUV"
mode: collaborative
---

> **El número del archivo NO es el número de la escena.** Al insertar las cuatro
> escenas del recorrido por la aplicación no se renombraron los archivos que ya
> existían, porque el nombre es también el `data-composition-id` y la clave de
> `window.__timelines`: renombrarlos habría roto el montaje y los sidecars. Así
> que `05-datos.html` es la escena **8** y `07-informe.html` la **11**. Manda el
> orden de esta lista, y el mismo orden manda en `montar.py`.

> **Continuidad.** No hay un solo corte ni barrido: trece escenas encadenadas
> con opacidad pura. El relevo lo hace el **montaje**, no cada escena: la
> saliente se va en 0,45 s y la entrante llega en 0,55 s, ambas con
> `power2.out`, arrancando a la vez. Los dos extremos se pagan caros —soltar el
> contenido antes deja el cuadro vacío (medido: cinco costuras caían a navy
> pelado) y no soltarlo deja dos interfaces superpuestas—; con estas dos curvas
> la suma de opacidades nunca baja de 0,9 y la ventana en que se leen las dos
> dura ~0,15 s. La voz manda las duraciones: cada línea entra 0,35 s después de
> callar la anterior. Silencio total: 4,2 s en doce respiraciones.

## Frame 1 — Apertura institucional

- status: built
- src: compositions/frames/01-pregunta.html
- duration: 8.14s
- transition_in: —
- scene: Cartela institucional del HUV: membrete de la casa, sin más.
- blueprint: titlecard-reveal
- voiceover: "Hospital Universitario del Valle, Evaristo García. Área de Oncología Quirúrgica."

Abre con la marca del Hospital Universitario del Valle sobre el escenario navy:
isotipo, nombre de la casa, plinto ámbar y área. Nada más. Se quitaron
las tres preguntas que abrían el vídeo: la sala son los profesionales del propio
servicio y no necesitan que se les cuente su trabajo. Lo que justifica el programa
son las cifras de la escena 2, que son un hecho y no una interpelación.

## Frame 2 — El dato existe, pero está encerrado

- status: built
- src: compositions/frames/02-encerrado.html
- duration: 17.72s
- transition_in: crossfade
- scene: 765 informes en PDF se acumulan hasta rodear el encuadre.
- blueprint: overwhelm-surround
- voiceover: "El servicio produce setecientos sesenta y cinco informes: treinta y seis mil páginas de patología. Cada diagnóstico, cada biomarcador y cada paciente está escrito ahí dentro. Pero está en PDF. Y un PDF se lee, no se consulta."

Miniaturas de informes entran desde los bordes y se acumulan por capas hasta cerrar
el centro. Contador que sube: 765 informes · 36.243 páginas · 22.547 estudios.
Termina claustrofóbico, con el contador congelado.

## Frame 3 — ONCONOVA

- status: built
- src: compositions/frames/03-onconova.html
- duration: 12.47s
- transition_in: crossfade
- scene: La marca se compone y la promesa aparece en una línea.
- blueprint: logo-assemble-lockup
- voiceover: "ONCONOVA lee esos informes y los convierte en una base de datos consultable. Lo que estaba encerrado en un documento pasa a ser una pregunta con respuesta."

Sobre el vacío se compone el lockup ONCONOVA · Gestor Oncológico HUV con su
isotipo y, debajo, la línea de valor. Es el respiro del vídeo: poca animación,
mucho aire. Aquí entra el esqueleto de marca que rige de la 3 a la 12.

## Frame 4 — El circuito de funcionamiento

- status: built
- src: compositions/frames/04-circuito.html
- duration: 39.59s
- transition_in: crossfade
- scene: La cámara recorre las cinco estaciones del flujo, de PDF a pantalla.
- blueprint: spatial-pan-stations
- voiceover: "El circuito tiene cinco pasos. Uno: se cargan los informes en PDF del servicio. Dos: el programa lee la capa de texto del documento. No fotografía el papel: lee el texto que el propio informe lleva dentro. Tres: separa el documento en casos, uno por informe. Cuatro: de cada caso extrae el paciente, el órgano, el diagnóstico y los biomarcadores, cada uno a su campo. Y cinco: lo guarda en una base de datos que vive en el hospital. Nada sale de la red del hospital."

Viaja EL DOCUMENTO. Una hoja entra, un haz le despega el texto del papel dejándolo
fantasma, el bloque se parte en tres casos, de uno salen los campos a sus casillas
y esas casillas se compactan en una fila que se apila. La cámara persigue al objeto.
En LECTURA se marca el dato que importa: «36.243 páginas · 0 sin capa de texto».
Cierra con un plano de conjunto: las cinco estaciones alineadas sobre una línea
ámbar y el pie «CINCO PASOS · DEL PDF A LA PREGUNTA CON RESPUESTA».

## Frame 5 — La aplicación abre

- status: built
- src: compositions/frames/05-abre.html
- duration: 17.51s
- transition_in: crossfade
- scene: El programa arranca a pantalla completa y se despliega el panel de navegación.
- blueprint: cursor-ui-demo
- voiceover: "Así abre el programa: a pantalla completa, sin instalación y sin contraseña. Esta es la pantalla de bienvenida. Y abajo a la izquierda, el botón que despliega el panel de navegación. Desde ahí se llega a todo: Inicio, Base de Datos y Dashboard."

Primera vez que se ve el producto, así que respira: la ventana se asienta, aparece
la bienvenida y el cursor va al botón flotante de abajo a la izquierda (`#eef1f6`,
el de verdad). El panel se despliega con sus cuatro entradas. La cuarta,
«Interoperabilidad QHORTE», **se ve** porque está en la aplicación real, pero la
voz no la nombra: no está implementada y nombrarla sería prometer.

## Frame 6 — De la carpeta a la base de datos

- status: built
- src: compositions/frames/06-cargar.html
- duration: 33.42s
- transition_in: crossfade
- scene: El explorador de la carpeta real, la selección, y el procesado de punta a punta.
- blueprint: cursor-ui-demo
- voiceover: "El trabajo empieza en la carpeta donde el servicio deja los informes, ordenados por año. Se eligen los archivos, o la carpeta entera. El programa marca cuáles ya analizó, cuáles van a medias y cuáles están sin tocar, y con un botón selecciona solo los pendientes. Se pulsa Procesar seleccionados. A partir de ahí no hay que hacer nada más: lee cada informe, lo separa en casos y lo guarda. Al terminar avisa de cuántos quedaron completos y cuántos incompletos."

Escenario fijo: la cámara no viaja, conduce el cursor y la interfaz responde.
Explorador → se abre `2026` → se eligen archivos y luego la carpeta → pestaña
Importar Datos → «Seleccionar pendientes» marca los ◐ y ● → **el botón verde de
procesar es el foco ámbar de la escena** → ventana de progreso → ventana de
resultados.

**Todo lo que se ve medido, nada supuesto:** la carpeta tiene 404 elementos y los
PDF pesan 16,4 / 20,8 / 19,9 / 16,7 MB con fecha 27/05/2026. Los contadores del
árbol son los que el producto escribe —`({en_bd}/{total})` con el total ya
intersecado con el rango del nombre por `core/estado_pdfs.py`— es decir
**(45/45) (50/50) (50/50) (48/48)**; el barrido crudo de `casos_por_pdf.json`
(82 · 92 · 93 · 84) incluye referencias cruzadas a informes ajenos y no llega
nunca a esa pantalla. El resumen final — **98 · 96 · 2 · 98.0 %** — se midió con
`core.validation_checker.analizar_batch_registros`, la que llama la propia
aplicación, sobre los dos PDF que el lote procesa de verdad y filtrando antes
contra la base. El porcentaje va con punto y un decimal porque el badge del
producto es una f-string de Python.

**El estado mixto está escenificado y se declara:** hoy los cuatro PDF constan
COMPLETO en la base. Se escenifica porque la escena enseña una importación y sin
pendientes no hay nada que importar; los denominadores, en cambio, son los que
el producto puede escribir. Los únicos pendientes del árbol son los dos que el
botón marca y el lote procesa: la pantalla ya no desmiente a la voz.

## Frame 7 — Las siete vistas de la base de datos

- status: built
- src: compositions/frames/07-pestanas.html
- duration: 44.52s
- transition_in: crossfade
- scene: Las siete pestañas, una a una, con una miniatura de lo que hay en cada una.
- blueprint: cursor-ui-demo
- voiceover: "La base de datos tiene siete vistas. Estadísticas Generales: los indicadores del servicio y los diagnósticos más frecuentes. Visualizador de Datos: la tabla completa, estudio por estudio, con buscador y filtros. Por Paciente: los estudios agrupados por cédula. Biomarcadores: cuántos se pidieron y con qué positividad. Análisis de Malignidad: el cruce entre cada biomarcador y el resultado del caso. Importar Datos, que es por donde acabamos de entrar. Y Exportaciones, donde queda todo lo que se ha generado."

La escena más larga del vídeo, y a propósito: es la que contesta «¿qué tiene cada
pestaña?». Siete paradas, un rótulo y una miniatura viva por parada. Los literales
salen de `ui.py`, no de memoria. El árbol de Importar Datos es la misma carpeta de
la escena anterior. La tabla de Análisis de Malignidad lleva sus cinco filas reales
auditadas y ninguna de relleno.

## Frame 8 — Los datos

- status: built
- src: compositions/frames/05-datos.html ← escena 8, no 5
- duration: 30.18s
- transition_in: crossfade
- scene: Un cursor recorre el Visualizador y abre la ficha de un paciente.
- blueprint: cursor-ui-demo
- voiceover: "Así se ve el resultado. Cada fila es un estudio, con sus ciento ochenta y nueve campos. Se busca, se ordena y se filtra. Y como un paciente puede volver, la vista Por Paciente los agrupa por cédula: dieciocho mil doscientos setenta y un pacientes, con toda su historia en una sola línea. Al abrir uno se ve su ficha completa: los datos del informe, el diagnóstico y los biomarcadores de cada estudio."

Recreación del Visualizador con identidades ficticias (Ley 1581) y números de caso
del rango IHQ259xxx, verificado libre en producción. El cursor teclea en el buscador,
la tabla filtra, cambia a Por Paciente y despliega un paciente con tres estudios.
Clic discreto en cada interacción.

## Frame 9 — El análisis

- status: built
- src: compositions/frames/06-analisis.html ← escena 9, no 6
- duration: 27.96s
- transition_in: crossfade
- scene: Los KPIs cuentan hacia arriba y el panel de biomarcadores se completa.
- blueprint: dataviz-countup
- voiceover: "Sobre esos datos, el programa calcula. Dos mil setenta y seis casos de inmunohistoquímica. Sesenta y siete por ciento malignos. Ciento noventa y cinco categorías anatómicas. Ciento veintidós biomarcadores distintos. Y el análisis de malignidad cruza los biomarcadores clave con el resultado del caso: cuántos malignos dieron positivo y cuántos negativo, y lo mismo en los benignos."

Tarjetas KPI con count-up escalonado sobre el fondo navy. La cámara empuja hasta la
tarjeta de malignidad y de ahí se abre la tabla de correlación biomarcador-malignidad,
cuyas filas entran en cascada.

## Frame 10 — El Dashboard gráfico

- status: built
- src: compositions/frames/10-dashboard.html
- duration: 14.30s
- transition_in: crossfade
- scene: Las cinco vistas del Dashboard, en un apunte rápido.
- blueprint: dataviz-countup
- voiceover: "Y aparte de la base de datos está el Dashboard, con cinco vistas de gráficos: el panorama general, los biomarcadores, los tiempos de proceso, la calidad del dato, y un comparador que se arma a medida."

La escena más corta: es un apunte, no una lección. Como aquí los emoji a color de
las pestañas compiten con el acento, el foco ámbar es un **aro cerrado de contorno
con halo**, no un subrayado tenue — si no, deja de mandar en el encuadre.

Dos correcciones de fidelidad sobre la rejilla del Overview. La rosquilla de
«Distribución de Malignidad» tiene **dos** sectores, no tres: en producción la
columna Malignidad solo toma dos valores (MALIGNO 1.390 = 67,0 % y BENIGNO 686 =
33,0 %) y `_g_pie_malignidad` agrupa en OTROS solo lo que baja del 2,5 %, así que
un tercer sector no puede existir — y con el dominante en el 67 % el espectador
lee la cifra real, de modo que un tercero le estaría enseñando una categoría
inventada. Y «Top Servicios» se dibuja en **columnas verticales**, igual que «Top
Órganos»: en la aplicación las dos tarjetas son el mismo `ax.bar` con las
etiquetas giradas 30°, no una de barras horizontales.

## Frame 11 — El informe estadístico

- status: built
- src: compositions/frames/07-informe.html ← escena 11, no 7
- duration: 48.99s
- transition_in: crossfade
- scene: Recorrido vertical por las cinco páginas reales del PDF.
- blueprint: transcript-scroll-artifact-reveal
- voiceover: "Todo eso se exporta en un informe de cinco páginas. La primera es el vistazo: los indicadores, el reparto por sexo y los tres diagnósticos más frecuentes de cada uno. La segunda abre el panorama: de los dos mil setenta y seis casos, dos mil cuatro tienen diagnóstico. Mil trescientos cincuenta son malignos y seiscientos cincuenta y cuatro, benignos. Setenta y dos se quedaron sin diagnóstico específico. Las páginas tres y cuatro son el detalle: cada categoría neoplásica con su órgano principal, sus casos y su reparto por sexo. Y la quinta cierra con lo no oncológico. Es un informe determinista: sin inteligencia artificial, las mismas cifras siempre."

El PDF real, rasterizado a 3,6× para que se lea de verdad, aparece como documento
continuo y la cámara recorre sus cinco páginas de arriba abajo, deteniéndose en cada
bloque mientras se nombra. En la parada de la página 2 se resalta la tabla de
cobertura. Cierra alejándose para ver las cinco páginas juntas.

## Frame 12 — Y se puede comprobar

- status: built
- src: compositions/frames/08-verificacion.html ← escena 12, no 8
- duration: 29.35s
- transition_in: crossfade
- scene: Una cifra del informe se traza hasta la frase literal de su PDF de origen.
- blueprint: comparison-split
- voiceover: "Y hay una última cosa, que es la que importa en un dato clínico: se puede comprobar. Cada diagnóstico guardado se contrastó contra el texto de su propio informe. Dos mil treinta y cuatro de dos mil setenta y seis aparecen literalmente en el PDF de origen. El resto están anotados uno a uno, con el motivo. La cifra que se proyecta en una reunión se puede seguir hasta la frase que la sostiene."

Pantalla partida: a la izquierda una fila del informe; a la derecha el fragmento del
PDF original con la frase resaltada. Una línea las une. Debajo, el marcador
2.034 / 2.076 · 98 %. **Aquí la música cae y queda solo la voz** — la caída va
escrita en la automatización del colchón, no en el montaje, y se deriva de la voz
para que no pueda desalinearse.

## Frame 13 — Cierre

- status: built
- src: compositions/frames/09-cierre.html ← escena 13, no 9
- duration: 22.70s
- transition_in: crossfade
- scene: Lockup final, firma del hospital y nota de confidencialidad.
- blueprint: titlecard-reveal
- voiceover: "ONCONOVA. El dato oncológico del Hospital Universitario del Valle: consultable, analizable y verificable. Dentro del hospital, y sin que ningún dato de paciente salga de él. Área de Oncología Quirúrgica. Hospital Universitario del Valle, Evaristo García."

Vuelve el lockup, ahora acompañado de la línea de cierre y del sello discreto
«Documento confidencial — Ley 1581 (Habeas Data)», el mismo que lleva el informe.
Sin marca de esquina ni marcador: la tarjeta de cierre *es* la marca a tamaño
completo. Fundido a navy.
