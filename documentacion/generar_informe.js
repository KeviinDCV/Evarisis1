// Generador de informe profesional ONCONOVA Gestor Oncológico (HUV)
// Genera: Informe_Avance_Proyecto_HUV.docx

const fs = require('fs');
const path = require('path');
const {
    Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
    Header, Footer, AlignmentType, LevelFormat,
    TabStopType, TabStopPosition, HeadingLevel, BorderStyle, WidthType,
    ShadingType, VerticalAlign, PageNumber, PageBreak,
} = require('docx');

// ===== HELPERS =====

const BORDER_GRAY = { style: BorderStyle.SINGLE, size: 1, color: 'BFBFBF' };
const BORDERS_ALL = { top: BORDER_GRAY, bottom: BORDER_GRAY, left: BORDER_GRAY, right: BORDER_GRAY };
const NAVY = '1F3864';
const BLUE = '2E5599';
const LIGHT_BLUE = 'D9E2F3';
const LIGHT_GRAY = 'F2F2F2';
const GREEN = '385723';
const ORANGE = 'C65911';

function h1(text) {
    return new Paragraph({
        heading: HeadingLevel.HEADING_1,
        spacing: { before: 360, after: 180 },
        children: [new TextRun({ text, bold: true, color: NAVY, size: 32 })],
    });
}

function h2(text) {
    return new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 280, after: 140 },
        children: [new TextRun({ text, bold: true, color: BLUE, size: 26 })],
    });
}

function h3(text) {
    return new Paragraph({
        heading: HeadingLevel.HEADING_3,
        spacing: { before: 200, after: 100 },
        children: [new TextRun({ text, bold: true, color: BLUE, size: 22 })],
    });
}

function p(text, opts = {}) {
    return new Paragraph({
        spacing: { after: 120, line: 280 },
        alignment: opts.center ? AlignmentType.CENTER : AlignmentType.JUSTIFIED,
        children: [new TextRun({ text, size: opts.size || 22, bold: opts.bold || false, italics: opts.italics || false, color: opts.color || '000000' })],
    });
}

function pmix(...runs) {
    return new Paragraph({
        spacing: { after: 120, line: 280 },
        alignment: AlignmentType.JUSTIFIED,
        children: runs.map(r => typeof r === 'string'
            ? new TextRun({ text: r, size: 22 })
            : new TextRun({ size: 22, ...r })),
    });
}

function bullet(text, level = 0) {
    return new Paragraph({
        numbering: { reference: 'bullets', level },
        spacing: { after: 80, line: 280 },
        children: [new TextRun({ text, size: 22 })],
    });
}

function bulletMix(...runs) {
    return new Paragraph({
        numbering: { reference: 'bullets', level: 0 },
        spacing: { after: 80, line: 280 },
        children: runs.map(r => typeof r === 'string'
            ? new TextRun({ text: r, size: 22 })
            : new TextRun({ size: 22, ...r })),
    });
}

function cell(text, opts = {}) {
    return new TableCell({
        borders: BORDERS_ALL,
        width: { size: opts.width, type: WidthType.DXA },
        shading: opts.shading ? { fill: opts.shading, type: ShadingType.CLEAR } : undefined,
        verticalAlign: VerticalAlign.CENTER,
        margins: { top: 100, bottom: 100, left: 140, right: 140 },
        children: [
            new Paragraph({
                alignment: opts.align || AlignmentType.LEFT,
                children: [new TextRun({ text: String(text), bold: opts.bold || false, color: opts.color || '000000', size: 20 })],
            }),
        ],
    });
}

function table(columnWidths, rows, opts = {}) {
    const totalWidth = columnWidths.reduce((a, b) => a + b, 0);
    return new Table({
        width: { size: totalWidth, type: WidthType.DXA },
        columnWidths,
        rows: rows.map((row, idx) => new TableRow({
            children: row.map((cellData, colIdx) => {
                const isHeader = idx === 0;
                return cell(cellData, {
                    width: columnWidths[colIdx],
                    shading: isHeader ? LIGHT_BLUE : (idx % 2 === 0 ? LIGHT_GRAY : undefined),
                    bold: isHeader,
                    color: isHeader ? NAVY : undefined,
                });
            }),
        })),
    });
}

function spacer() {
    return new Paragraph({ spacing: { after: 120 }, children: [new TextRun('')] });
}

// ===== CONTENIDO DEL INFORME =====

const content = [];

// ---- PORTADA ----
content.push(
    new Paragraph({ spacing: { before: 2400, after: 240 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: 'HOSPITAL UNIVERSITARIO DEL VALLE', bold: true, size: 24, color: NAVY })] }),
    new Paragraph({ spacing: { after: 720 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: 'Oficina de Innovación y Desarrollo', size: 22, color: '595959' })] }),

    new Paragraph({ spacing: { before: 600, after: 200 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: 'INFORME DE AVANCE', bold: true, size: 48, color: NAVY })] }),
    new Paragraph({ spacing: { after: 600 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: 'Proyecto ONCONOVA Gestor Oncológico', bold: true, size: 36, color: BLUE })] }),
    new Paragraph({ spacing: { after: 1200 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: 'Sistema Inteligente de Gestión Oncológica con Inteligencia Artificial', italics: true, size: 22, color: '595959' })] }),

    new Paragraph({ spacing: { before: 2400, after: 120 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: 'Versión Actual del Sistema', bold: true, size: 22, color: '595959' })] }),
    new Paragraph({ spacing: { after: 480 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: 'V6.9.2 — Multi-Usuario LAN con Soporte de Modelos Reasoning', size: 22, color: NAVY })] }),

    new Paragraph({ spacing: { before: 480, after: 120 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: 'Fecha del Informe', bold: true, size: 22, color: '595959' })] }),
    new Paragraph({ spacing: { after: 120 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: '11 de mayo de 2026', size: 22 })] }),

    new Paragraph({ children: [new PageBreak()] }),
);

// ---- 1. RESUMEN EJECUTIVO ----
content.push(h1('1. Resumen Ejecutivo'));
content.push(p(
    'El presente informe documenta el avance del proyecto ONCONOVA Gestor Oncológico, una herramienta interna del Hospital Universitario del Valle (HUV) destinada a digitalizar, normalizar y centralizar la información clínica derivada de informes de inmunohistoquímica (IHQ) y patología oncológica. Durante el periodo cubierto por este informe, el sistema ha evolucionado desde un extractor tradicional basado en expresiones regulares hacia una plataforma híbrida que combina procesamiento de texto clásico con modelos de lenguaje de inteligencia artificial ejecutados localmente, garantizando en todo momento la confidencialidad de los datos médicos.'
));
content.push(p(
    'Los principales hitos alcanzados incluyen: la expansión del pipeline de extracción asistida por IA de tres a ciento ochenta y cuatro columnas clínicas, la migración de la base de datos desde un archivo local en SQLite hacia un servidor MySQL/MariaDB compartido en la red interna del hospital, y la generación de un ejecutable distribuible que permite a varios usuarios del HUV trabajar simultáneamente sobre el mismo conjunto de datos. Estos avances representan un salto cualitativo en la capacidad operativa del sistema, aunque persisten retos vinculados al hardware disponible y a las condiciones de suministro eléctrico, los cuales se documentan en las secciones correspondientes.'
));

// ---- 2. ESTADO AL RECIBIR EL PROYECTO ----
content.push(h1('2. Estado del Proyecto al Recibirlo'));

content.push(h2('2.1 Componentes existentes'));
content.push(p(
    'El proyecto se entregó como una aplicación de escritorio en Python con interfaz gráfica desarrollada en TTKBootstrap, orientada a uso individual. La extracción de información clínica se realizaba mediante un módulo OCR basado en Tesseract combinado con un conjunto extenso de expresiones regulares específicas para los formatos de informe del HUV. Los datos extraídos se almacenaban en una base de datos local de tipo SQLite, dentro del mismo equipo donde corría la aplicación.'
));

content.push(h2('2.2 Limitaciones detectadas al inicio'));
content.push(bullet('Hardware del equipo original sin tarjeta gráfica dedicada, con capacidad de cómputo reducida para tareas de procesamiento masivo o uso de modelos de inteligencia artificial.'));
content.push(bullet('Base de datos en formato de archivo único, lo cual impedía el trabajo concurrente entre varios profesionales y generaba riesgo de corrupción al compartirse en carpetas de red.'));
content.push(bullet('Cobertura parcial de los biomarcadores y entidades clínicas presentes en los informes reales del laboratorio. Aproximadamente seiscientos casos extraídos correctamente sobre cerca de mil esperados en el conjunto de prueba.'));
content.push(bullet('Categorización de diagnósticos con un volumen significativo de casos clasificados como "OTRO" o "SIN DIAGNÓSTICO ESPECÍFICO", lo que dificultaba la generación de reportes oncológicos consolidados confiables.'));
content.push(bullet('Ausencia de una capa intermedia que permitiera comparar la salida del extractor tradicional con un método alternativo, lo que dificultaba el control de calidad y la detección de errores sistemáticos.'));

// ---- 3. CAMBIOS Y MEJORAS ----
content.push(h1('3. Cambios y Mejoras Implementados'));
content.push(p(
    'Los avances del proyecto se organizaron en cuatro sprints versionados sucesivos, cada uno con un objetivo claro y validaciones cuantitativas previas a su despliegue. A continuación se presentan los principales hitos.'
));

content.push(h2('3.1 Sprint V6.6.x — Refinamiento del normalizador de diagnósticos'));
content.push(p(
    'Se realizó una intervención quirúrgica sobre el normalizador de diagnósticos, agregando nuevas categorías oncológicas (tumor filodes de mama, carcinoma papilar, lesiones escamosas intraepiteliales, carcinoma anexial cutáneo, entre otras), corrigiendo errores tipográficos frecuentes del patólogo en los informes ("CARICNOMA", "HISTOLOGIOS"), y reordenando la lógica de prioridad para evitar que patrones genéricos atraparan casos específicos antes de tiempo. Adicionalmente se implementó una nueva regla en el módulo de detección de malignidad para evitar que la historia clínica contaminara la clasificación cuando el diagnóstico principal era explícitamente benigno.'
));
content.push(p(
    'El sprint cubrió cinco versiones consecutivas validadas sobre ciento ochenta y ocho casos del rango IHQ250001–IHQ250200. La tasa de categorización oncológica pasó del sesenta y dos por ciento al ochenta y cinco coma seis por ciento, con cero regresiones detectadas en los casos de referencia previamente correctos.'
));

content.push(h2('3.2 Sprint V6.7.x — Pipeline alternativo de extracción con IA'));
content.push(p(
    'Se incorporó al sistema un nuevo botón denominado "Procesar con IA" que ejecuta un pipeline paralelo al extractor tradicional. Este pipeline toma el texto OCR completo de cada PDF, lo segmenta por informe IHQ individual, y lo envía a un modelo de lenguaje local ejecutado en LM Studio. La salida del modelo se valida contra un esquema JSON estricto que garantiza la estructura del resultado.'
));
content.push(p(
    'El sprint incluyó múltiples iteraciones para resolver problemas técnicos como la compatibilidad del formato de respuesta JSON entre distintos proveedores, la gestión de tokens de razonamiento que algunos modelos generan internamente, y la limpieza posterior de preámbulos y muletillas del patólogo en los diagnósticos. La versión final entregó una tasa de extracción cercana al noventa y siete por ciento sobre los casos procesados, con persistencia automática en una base de datos paralela para fines de auditoría.'
));

content.push(h2('3.3 Sprint V6.8.0 — Expansión a las ciento ochenta y cuatro columnas clínicas'));
content.push(p(
    'Hasta este punto, el pipeline de inteligencia artificial solo extraía tres campos por caso: número de petición, diagnóstico principal y órgano. En esta versión se expandió el alcance del esquema JSON para que el modelo extrajera la totalidad de las columnas clínicas mantenidas en la base de datos del HUV, incluyendo datos administrativos del paciente (EPS, edad, género, departamento, médico tratante), datos del procedimiento (fechas, patólogo, tipo de examen) y los aproximadamente ciento cuarenta y cinco biomarcadores de inmunohistoquímica registrados.'
));
content.push(p(
    'Adicionalmente, en esta versión se unificó la persistencia de los datos: a partir de V6.8.0 los resultados extraídos por la IA se escriben automáticamente en la base de datos principal del Visualizador, en paralelo a la base acumulativa de auditoría. Esto permite que los usuarios puedan elegir entre el extractor tradicional y el pipeline IA dependiendo del caso, sin que los datos queden aislados en repositorios distintos.'
));

content.push(h2('3.4 Sprint V6.9.x — Base de datos compartida en red y distribución ejecutable'));
content.push(p(
    'Esta fase representa el cambio arquitectural más importante del proyecto. La base de datos pasó de ser un archivo SQLite local a un servidor MySQL/MariaDB instalado mediante XAMPP en una de las máquinas del hospital. Esto habilita el acceso concurrente desde cualquier estación de trabajo dentro de la red local del HUV, eliminando los problemas de corrupción que ocurrían al compartir el archivo SQLite por carpetas de red y permitiendo que múltiples usuarios consulten o procesen información simultáneamente.'
));
content.push(p(
    'Se desarrolló además un adaptador de base de datos que mantiene compatibilidad con SQLite para escenarios de trabajo desconectado o presentaciones fuera de la red hospitalaria, controlado mediante una sola línea de configuración. Finalmente, se generó un ejecutable autocontenido mediante PyInstaller que permite distribuir la aplicación a otras estaciones del hospital sin necesidad de instalar Python ni configurar entornos virtuales. Cada equipo cliente solo debe editar su archivo de configuración para apuntar a la dirección IP del servidor.'
));

content.push(new Paragraph({ children: [new PageBreak()] }));

// ---- 4. MODELOS DE IA EVALUADOS ----
content.push(h1('4. Modelos de Inteligencia Artificial Evaluados'));
content.push(p(
    'Durante el desarrollo del pipeline de extracción con IA se evaluaron diversos modelos de lenguaje de código abierto, ejecutados localmente para garantizar la confidencialidad de los datos clínicos. La elección del modelo final responde a un compromiso entre calidad de extracción, velocidad de procesamiento y compatibilidad con el hardware disponible. A continuación se resume el proceso de evaluación.'
));

content.push(spacer());

// Tabla de modelos
content.push(table(
    [1900, 1100, 1100, 1500, 3760],
    [
        ['Modelo', 'Tamaño', 'Tipo', 'Resultado', 'Observaciones'],
        ['openai/gpt-oss-20b', '20B', 'Instruct', 'Descartado', 'Calidad media. Problemas frecuentes con formato JSON y alucinación de tokens. Tasa de extracción inicial de aproximadamente treinta por ciento.'],
        ['nvidia/nemotron-3-nano-omni', '30B', 'Multimodal', 'Descartado', 'Inicialmente muy lento; perdía tokens en razonamiento sin entregar respuesta final.'],
        ['google/gemma-4-26b-a4b', '26B', 'Instruct', 'No utilizable', 'No logró cargarse en el hardware actual debido al tamaño del modelo y la memoria gráfica disponible.'],
        ['qwen/qwen3.6-27b', '27B', 'Reasoning', 'Descartado', 'Modelo de razonamiento; el contenido final llegaba vacío porque todo se enviaba al canal interno de reasoning_content. Tiempos superiores a treinta minutos por caso.'],
        ['qwen2.5-32b-instruct', '32B', 'Instruct', 'Descartado', 'El modelo supera la capacidad de la memoria gráfica (ocho gigabytes), por lo cual gran parte se ejecuta en memoria RAM convencional, generando tiempos de espera superiores a diez minutos por consulta.'],
        ['qwen2.5-14b-instruct', '14B', 'Instruct', 'Validado', 'Calidad alta y cabe casi completo en la memoria gráfica disponible. Tiempo promedio de cinco a siete minutos por caso con esquema completo de ciento ochenta y cuatro campos.'],
        ['nvidia/nemotron-3-nano', '8B', 'Reasoning', 'En uso actual', 'Modelo más reciente, alta calidad de extracción, requiere tiempos de cinco a diez minutos por caso. Elegido por preferencia del equipo por la calidad de su salida.'],
    ]
));

content.push(spacer());
content.push(p(
    'Cabe señalar que los modelos de tipo reasoning (razonamiento explícito), como qwen3.6 y nemotron-3-nano, requieren tratamiento especial porque dirigen su salida al canal de razonamiento interno en lugar del campo de contenido habitual. El cliente HTTP del sistema fue ajustado para extender el tiempo máximo de espera a quince minutos por consulta, lo cual permite que estos modelos completen su razonamiento sin que el cliente cierre la conexión prematuramente.'
));

// ---- 5. INFRAESTRUCTURA Y HARDWARE ----
content.push(h1('5. Infraestructura y Hardware'));

content.push(h2('5.1 Estado anterior'));
content.push(p(
    'El equipo asignado inicialmente al proyecto era una estación de trabajo de gama media sin tarjeta gráfica dedicada, con procesador y memoria RAM ajustados al uso ofimático habitual del hospital. Bajo estas condiciones, la ejecución de modelos de lenguaje de gran tamaño era inviable, y todo el procesamiento debía recaer sobre el extractor basado en expresiones regulares, con sus limitaciones inherentes para abordar la variabilidad lingüística de los informes patológicos.'
));

content.push(h2('5.2 Estado actual'));
content.push(p(
    'El equipo dispone ahora de una tarjeta gráfica NVIDIA GeForce RTX 3050 OEM con ocho gigabytes de memoria de video, lo que ha habilitado la ejecución local de modelos de lenguaje sin enviar información a servicios externos. Esta mejora es fundamental para mantener el cumplimiento de la Ley 1581 de protección de datos personales y de las recomendaciones internacionales de manejo de información médica confidencial.'
));

content.push(h2('5.3 Limitaciones residuales'));
content.push(p(
    'A pesar del avance, la tarjeta RTX 3050 OEM es una unidad de gama básica orientada principalmente a tareas gráficas estándar. Su capacidad de ocho gigabytes de memoria de video resulta insuficiente para alojar completamente los modelos de mayor tamaño (treinta y dos mil millones de parámetros o más). Cuando un modelo supera el límite de memoria gráfica, parte de su procesamiento se traslada a la memoria RAM convencional del sistema, lo que reduce significativamente la velocidad de generación, en algunos casos hasta diez veces.'
));
content.push(p(
    'Adicionalmente, el volumen de información contenido en cada informe IHQ del HUV es considerable: un único caso clínico puede generar entre dos mil y cinco mil tokens de entrada para el modelo, y el esquema de respuesta exige aproximadamente dos mil quinientos tokens adicionales para las ciento ochenta y cuatro columnas clínicas. Procesar este volumen sobre un equipo de gama básica explica los tiempos de procesamiento que se documentan en la siguiente sección.'
));

// ---- 6. DIFICULTADES OPERATIVAS ----
content.push(h1('6. Dificultades Operativas Encontradas'));

content.push(h2('6.1 Interrupciones del suministro eléctrico'));
content.push(p(
    'Durante varios fines de semana del periodo del proyecto se presentaron cortes y caídas de tensión en las instalaciones del hospital. Estos eventos interrumpieron varias ejecuciones nocturnas o de fin de semana del procesamiento por lotes, dado que los modelos de lenguaje requieren tiempos extensos para completar la totalidad de los casos. Cada interrupción obliga a reiniciar el equipo, recargar el modelo en memoria gráfica (proceso que puede tardar varios minutos), y reanudar el procesamiento desde el último estado guardado, asumiendo que la base de datos haya quedado consistente.'
));
content.push(p(
    'Como recomendación operativa, se sugiere considerar la adquisición de un sistema de alimentación ininterrumpida (UPS) para la estación de trabajo dedicada al procesamiento, así como la coordinación con el área de infraestructura del hospital para anticipar mantenimientos eléctricos programados.'
));

content.push(h2('6.2 Tiempos de procesamiento extensos'));
content.push(p(
    'El volumen total de información a procesar comprende treinta y ocho archivos PDF que en conjunto suman cerca de mil casos clínicos. Con el hardware actual y el modelo en uso, los tiempos estimados son los siguientes.'
));

content.push(spacer());
content.push(table(
    [2400, 2000, 2000, 2960],
    [
        ['Modelo', 'Tiempo por caso', 'Tiempo por PDF (50 casos)', 'Tiempo total (38 PDFs)'],
        ['qwen2.5-7b-instruct', '1–2 minutos', '1–2 horas', 'Aproximadamente 1–2 días'],
        ['qwen2.5-14b-instruct', '5–7 minutos', '4–6 horas', 'Aproximadamente 5–7 días'],
        ['nvidia/nemotron-3-nano (uso actual)', '5–10 minutos', '4–8 horas', 'Aproximadamente 5–12 días'],
    ]
));

content.push(spacer());
content.push(p(
    'Estos tiempos contemplan ejecución continua veinticuatro horas al día, lo cual no siempre es posible debido a las interrupciones eléctricas mencionadas y a la necesidad de mantener disponible el equipo para otras tareas del área. En la práctica, el procesamiento real puede extenderse hasta el doble del tiempo proyectado.'
));

content.push(h2('6.3 Calidad versus velocidad'));
content.push(p(
    'La elección de mantener el modelo nvidia/nemotron-3-nano como motor actual responde a una decisión técnica del equipo basada en la calidad observada de sus extracciones, especialmente en los campos clínicos más sensibles como malignidad, biomarcadores específicos y diagnóstico principal. La alternativa de usar qwen2.5-7b-instruct reduciría sustancialmente los tiempos pero implicaría una ligera pérdida de precisión en casos clínicos complejos. Esta decisión podrá revisarse periódicamente conforme avance el procesamiento y se acumulen métricas reales de calidad.'
));

content.push(new Paragraph({ children: [new PageBreak()] }));

// ---- 7. LOGROS ----
content.push(h1('7. Logros Cuantitativos del Periodo'));

content.push(spacer());
content.push(table(
    [4200, 5160],
    [
        ['Indicador', 'Resultado'],
        ['Columnas clínicas extraídas por la IA', 'De 3 a 184 columnas'],
        ['Categorización oncológica del extractor tradicional', 'Mejora del 62% al 85,6%'],
        ['Tasa de éxito del pipeline IA (con qwen 14B + 184 campos)', 'Aproximadamente 97% por caso'],
        ['Soporte de usuarios simultáneos', 'De 1 usuario a múltiples usuarios en LAN'],
        ['Backend de base de datos', 'Migración de SQLite local a MySQL/MariaDB en red'],
        ['Distribución del software', 'Generación de ejecutable autocontenido (.exe, 115 MB)'],
        ['Versiones publicadas en el periodo', 'De V6.6.12 a V6.9.2 (más de 20 versiones documentadas)'],
        ['Casos validados al final del periodo', 'Aproximadamente 165 casos auditados con score promedio ≥ 96%'],
    ]
));

// ---- 8. PRÓXIMOS PASOS ----
content.push(h1('8. Próximos Pasos Recomendados'));
content.push(bullet('Completar el procesamiento por lotes de los treinta y ocho archivos PDF restantes con el modelo y la configuración actuales, manteniendo monitoreo de calidad cada cierto número de casos.'));
content.push(bullet('Distribuir el ejecutable generado a los demás profesionales del HUV que requieran consulta o procesamiento, ajustando en cada caso el archivo de configuración para que apunten al servidor MySQL central.'));
content.push(bullet('Evaluar la adquisición o asignación de una tarjeta gráfica de mayor capacidad de memoria (mínimo dieciséis gigabytes de VRAM), con el fin de habilitar modelos más grandes y rápidos sin recurrir a desbordamiento a memoria RAM.'));
content.push(bullet('Implementar un sistema de alimentación ininterrumpida (UPS) en la estación dedicada al procesamiento por lotes, para mitigar las interrupciones derivadas de caídas eléctricas.'));
content.push(bullet('Establecer una rutina automática de copia de seguridad nocturna de la base de datos MySQL, mediante tareas programadas de Windows con el utilitario mysqldump.'));
content.push(bullet('Definir junto con el equipo de patología un protocolo de auditoría periódica para validar muestras aleatorias de la extracción automática contra el contenido original del informe.'));
content.push(bullet('Documentar formalmente para los demás equipos del HUV el procedimiento de instalación y configuración del software en estaciones cliente.'));

// ---- 9. CONCLUSIONES ----
content.push(h1('9. Conclusiones'));
content.push(p(
    'El proyecto ONCONOVA Gestor Oncológico ha experimentado una evolución técnica significativa durante el periodo cubierto por este informe. Desde una herramienta de extracción local con cobertura parcial, se ha consolidado como una plataforma de procesamiento clínico asistido por inteligencia artificial, con capacidad de operación multi-usuario en la red interna del hospital y mecanismos de control de calidad incorporados al flujo de trabajo.'
));
content.push(p(
    'Los principales avances no se limitan al plano técnico: la sustitución de un esquema de tres campos por uno de ciento ochenta y cuatro columnas clínicas habilita por primera vez el aprovechamiento integral de los informes IHQ del HUV para tareas de investigación, generación de indicadores oncológicos y construcción de tableros de mando para la dirección del hospital. La centralización de la base de datos elimina los silos de información que existían cuando cada usuario trabajaba sobre su propio archivo local.'
));
content.push(p(
    'No obstante, los retos persisten. La capacidad de cómputo disponible, aunque mejorada respecto del estado inicial, sigue siendo el principal cuello de botella para escalar el procesamiento al ritmo deseado por el área asistencial. Las interrupciones eléctricas de fines de semana han retrasado en varias ocasiones la finalización de los lotes nocturnos, y es importante atender este factor desde el plano operativo y de infraestructura.'
));
content.push(p(
    'Se considera que el proyecto se encuentra en una etapa de madurez técnica suficiente para iniciar despliegues controlados con usuarios reales del área de patología y oncología, manteniendo en paralelo el ciclo de mejoras evolutivas que ha caracterizado el trabajo de los últimos meses. El equipo de Innovación y Desarrollo del HUV queda disponible para acompañar dicho despliegue y para presentar los resultados ante las instancias directivas que lo requieran.'
));

content.push(spacer());
content.push(spacer());

// Firma
content.push(new Paragraph({
    spacing: { before: 480 },
    children: [new TextRun({ text: '_____________________________________', size: 22 })]
}));
content.push(new Paragraph({
    children: [new TextRun({ text: 'Oficina de Innovación y Desarrollo', bold: true, size: 22 })]
}));
content.push(new Paragraph({
    children: [new TextRun({ text: 'Hospital Universitario del Valle', size: 22 })]
}));
content.push(new Paragraph({
    children: [new TextRun({ text: 'innovacionydesarrollo@correohuv.gov.co', italics: true, size: 20, color: '595959' })]
}));

// ===== DOCUMENTO =====

const doc = new Document({
    creator: 'Oficina de Innovación y Desarrollo - HUV',
    title: 'Informe de Avance - Proyecto ONCONOVA Gestor Oncológico',
    description: 'Informe ejecutivo sobre el estado del proyecto ONCONOVA, mejoras implementadas, modelos de IA evaluados y dificultades operativas encontradas.',
    styles: {
        default: {
            document: { run: { font: 'Calibri', size: 22 } },
        },
        paragraphStyles: [
            { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
                run: { size: 32, bold: true, color: NAVY, font: 'Calibri' },
                paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0 } },
            { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
                run: { size: 26, bold: true, color: BLUE, font: 'Calibri' },
                paragraph: { spacing: { before: 280, after: 140 }, outlineLevel: 1 } },
            { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
                run: { size: 22, bold: true, color: BLUE, font: 'Calibri' },
                paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 2 } },
        ],
    },
    numbering: {
        config: [{
            reference: 'bullets',
            levels: [{
                level: 0,
                format: LevelFormat.BULLET,
                text: '•',
                alignment: AlignmentType.LEFT,
                style: { paragraph: { indent: { left: 720, hanging: 360 } } },
            }],
        }],
    },
    sections: [{
        properties: {
            page: {
                size: { width: 12240, height: 15840 },
                margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
            },
        },
        headers: {
            default: new Header({
                children: [new Paragraph({
                    alignment: AlignmentType.RIGHT,
                    children: [new TextRun({ text: 'Hospital Universitario del Valle — Proyecto ONCONOVA', size: 18, color: '595959', italics: true })],
                    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: BLUE, space: 1 } },
                })],
            }),
        },
        footers: {
            default: new Footer({
                children: [new Paragraph({
                    alignment: AlignmentType.CENTER,
                    children: [
                        new TextRun({ text: 'Página ', size: 18, color: '595959' }),
                        new TextRun({ children: [PageNumber.CURRENT], size: 18, color: '595959' }),
                        new TextRun({ text: ' de ', size: 18, color: '595959' }),
                        new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18, color: '595959' }),
                    ],
                })],
            }),
        },
        children: content,
    }],
});

const outputPath = path.resolve(__dirname, 'Informe_Avance_Proyecto_HUV.docx');
Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync(outputPath, buffer);
    console.log(`OK: ${outputPath}`);
    console.log(`Tamano: ${(buffer.length / 1024).toFixed(1)} KB`);
}).catch(err => {
    console.error('ERROR:', err);
    process.exit(1);
});
