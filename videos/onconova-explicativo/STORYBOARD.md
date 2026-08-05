---
format: 1920x1080
duration: 3m52s
message: "El dato oncológico del HUV deja de estar encerrado en PDFs: se consulta, se analiza y se puede verificar contra el informe original"
arc: "Membrete institucional → El dato encerrado → ONCONOVA → El circuito → Los datos → El análisis → El informe → La verificación → Cierre"
audience: "profesionales sanitarios y de gestión del HUV"
mode: collaborative
---

## Frame 1 — Apertura institucional

- status: built
- src: compositions/frames/01-pregunta.html
- duration: 13s
- transition_in: cut
- scene: Cartela institucional del HUV: membrete de la casa, sin más.
- blueprint: titlecard-reveal
- voiceover: "Hospital Universitario del Valle, Evaristo García. Área de Cirugía Oncológica. Servicio de Patología."

Abre con la marca del Hospital Universitario del Valle sobre el escenario navy:
isotipo, nombre de la casa, plinto ámbar, área y servicio. Nada más. Se quitaron
las tres preguntas que abrían el vídeo: la sala son los profesionales del propio
servicio y no necesitan que se les cuente su trabajo. Lo que justifica el programa
son las cifras de la escena 2, que son un hecho y no una interpelación.

## Frame 2 — El dato existe, pero está encerrado

- status: built
- src: compositions/frames/02-encerrado.html
- duration: 19s
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
- duration: 13s
- transition_in: wipe
- scene: La marca se compone y la promesa aparece en una línea.
- blueprint: logo-assemble-lockup
- voiceover: "ONCONOVA lee esos informes y los convierte en una base de datos consultable. Lo que estaba encerrado en un documento pasa a ser una pregunta con respuesta."

Un barrido limpia la acumulación de golpe. Sobre el vacío se compone el lockup
ONCONOVA · Gestor Oncológico HUV y, debajo, la línea de valor. Es el respiro del
vídeo: poca animación, mucho aire.

## Frame 4 — El circuito de funcionamiento

- status: built
- src: compositions/frames/04-circuito.html
- duration: 33s
- transition_in: crossfade
- scene: La cámara recorre las cinco estaciones del flujo, de PDF a pantalla.
- blueprint: spatial-pan-stations
- voiceover: "El circuito tiene cinco pasos. Uno: se cargan los informes en PDF del servicio. Dos: el programa lee la capa de texto del documento. No fotografía el papel: lee el texto que el propio informe lleva dentro. Tres: separa el documento en casos, uno por informe. Cuatro: de cada caso extrae el paciente, el órgano, el diagnóstico y los biomarcadores, cada uno a su campo. Y cinco: lo guarda en una base de datos que vive en el hospital. Nada sale de la red del hospital."

Ya no es un lienzo de cinco tarjetas quietas: viaja EL DOCUMENTO. Una hoja
entra, un haz le despega el texto del papel dejandolo fantasma, el bloque se
parte en tres casos, de uno salen los campos a sus casillas y esas casillas se
compactan en una fila que se apila. La camara persigue al objeto.
En LECTURA se marca el dato que importa: "36.243 paginas · 0 sin capa de texto".
Cierra con un plano de conjunto (30,35s-33s): las cinco estaciones alineadas
sobre una linea ambar y el pie "CINCO PASOS · DEL PDF A LA PREGUNTA CON
RESPUESTA", para que quede el esquema completo en la retina.

## Frame 5 — Los datos

- status: built
- src: compositions/frames/05-datos.html
- duration: 29s
- transition_in: cut
- scene: Un cursor recorre el Visualizador y abre la ficha de un paciente.
- blueprint: cursor-ui-demo
- voiceover: "Así se ve el resultado. Cada fila es un estudio, con sus ciento ochenta y nueve campos. Se busca, se ordena y se filtra. Y como un paciente puede volver, la vista Por Paciente los agrupa por cédula: dieciocho mil doscientos setenta y un pacientes, con toda su historia en una sola línea. Al abrir uno se ve su ficha completa: los datos del informe, el diagnóstico y los biomarcadores de cada estudio."

Recreación del Visualizador con datos ficticios. El cursor teclea en el buscador,
la tabla filtra, cambia a la pestaña Por Paciente y despliega un paciente con tres
estudios. Sonido de clic discreto en cada interacción.

## Frame 6 — El análisis

- status: built
- src: compositions/frames/06-analisis.html
- duration: 29s
- transition_in: crossfade
- scene: Los KPIs cuentan hacia arriba y el panel de biomarcadores se completa.
- blueprint: dataviz-countup
- voiceover: "Sobre esos datos, el programa calcula. Dos mil setenta y seis casos de inmunohistoquímica. Sesenta y siete coma uno por ciento malignos. Ciento noventa y cinco categorías anatómicas. Ciento veintidós biomarcadores distintos. Y el análisis de malignidad cruza los biomarcadores clave con el resultado del caso: cuántos malignos dieron positivo y cuántos negativo, y lo mismo en los benignos."

Tarjetas KPI con count-up escalonado sobre el fondo navy. La cámara empuja hasta la
tarjeta de malignidad y de ahí se abre la tabla de correlación biomarcador-malignidad,
cuyas filas entran en cascada.

## Frame 7 — El informe estadístico

- status: built
- src: compositions/frames/07-informe.html
- duration: 47s
- transition_in: cut
- scene: Recorrido vertical por las cinco páginas reales del PDF.
- blueprint: transcript-scroll-artifact-reveal
- voiceover: "Todo eso se exporta en un informe de cinco páginas. La primera es el vistazo: los indicadores, el reparto por sexo y los tres diagnósticos más frecuentes de cada uno. La segunda abre el panorama: de los dos mil setenta y seis casos, dos mil cuatro tienen diagnóstico. Mil quinientos sesenta y ocho son tumores y cuatrocientos treinta y seis, hallazgos no neoplásicos. Setenta y dos se quedaron sin diagnóstico específico. Las páginas tres y cuatro son el detalle: cada categoría neoplásica con su órgano principal, sus casos y su reparto por sexo. Y la quinta cierra con lo no oncológico. Es un informe determinista: sin inteligencia artificial, las mismas cifras siempre."

El PDF real aparece como documento continuo y la cámara recorre sus cinco páginas
de arriba abajo, deteniéndose en cada bloque mientras se nombra. En la parada de la
página 2 se resalta la tabla de cobertura. Cierra alejándose para ver las cinco
páginas juntas.

## Frame 8 — Y se puede comprobar

- status: built
- src: compositions/frames/08-verificacion.html
- duration: 29s
- transition_in: wipe
- scene: Una cifra del informe se traza hasta la frase literal de su PDF de origen.
- blueprint: comparison-split
- voiceover: "Y hay una última cosa, que es la que importa en un dato clínico: se puede comprobar. Cada diagnóstico guardado se contrastó contra el texto de su propio informe. Dos mil treinta y cuatro de dos mil setenta y seis aparecen literalmente en el PDF de origen. El resto están anotados uno a uno, con el motivo. La cifra que se proyecta en una reunión se puede seguir hasta la frase que la sostiene."

Pantalla partida: a la izquierda una fila del informe; a la derecha el fragmento del
PDF original con la frase resaltada. Una línea las une. Debajo, el marcador
2.034 / 2.076 · 98 %. Aquí la música cae y queda solo la voz.

## Frame 9 — Cierre

- status: built
- src: compositions/frames/09-cierre.html
- duration: 20s
- transition_in: crossfade
- scene: Lockup final, firma del hospital y nota de confidencialidad.
- blueprint: titlecard-reveal
- voiceover: "ONCONOVA. El dato oncológico del Hospital Universitario del Valle: consultable, analizable y verificable. Dentro del hospital, y sin que ningún dato de paciente salga de él. Área de Cirugía Oncológica. Hospital Universitario del Valle, Evaristo García."

Vuelve el lockup, ahora acompañado de la línea de cierre y del sello discreto
"Documento confidencial — Ley 1581 (Habeas Data)", el mismo que lleva el informe.
Fundido a navy.
