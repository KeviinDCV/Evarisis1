# Changelog

## [6.9.84] - 2026-07-29 — «(sin nombre)»: la columna calculada que la lectura relacional se dejó atrás

Los pacientes salían como **«(sin nombre)»** con su cédula al lado. El dato nunca se perdió: estaba en la base, repartido en `Primer nombre`, `Segundo nombre`, `Primer apellido` y `Segundo apellido`. Lo que faltaba era quien lo compusiera.

```
BD  ->  JASSIEL | ALBEIRO | CAICEDO | MAZONEZ
vista ->  (sin nombre)
```

`Nombre Completo` **no es una columna del esquema**: se calcula al leer. Y ese cálculo vivía dentro de la rama que consulta la tabla plana, así que al activar el modelo relacional (**V6.9.76**) la lectura empezó a devolver un DataFrame sin ella. La vista pedía una columna que ya no venía y mostraba el hueco.

### No era solo la vista Por Paciente

`Nombre Completo` está en `COLS_TO_SHOW` **y en `COLS_SIEMPRE`** —las que nunca se ocultan—, así que el **Visualizador principal** llevaba también esa columna vacía desde la misma versión. Se veía menos porque allí hay 40 columnas más donde mirar.

### El arreglo, donde no puede volver a divergir

La derivación pasa a `_derivar_columnas(df)`, aplicada en el **único punto por el que salen los dos caminos de lectura**. Cualquier columna calculada que haga falta mañana va ahí y la ven los dos.

Vectorizada a propósito: el `df.apply(..., axis=1)` original sobre 22.547 filas cuesta más que la lectura entera. Medido: **0,13 s**, lectura completa 0,90 s.

Y comprobado que es **equivalente**, no parecida: contrastada fila a fila contra `build_clean_full_name()` en 4.000 registros → **0 diferencias**.

```
Nombre Completo presente          : sí
con nombre real                   : 22.547 / 22.547
pacientes que saldrían sin nombre :      0   (antes: los 18.199)
filas rojas, ambos caminos        :     57   (sin cambios, diferencia 0)
```

### ⚠️ La tercera de la misma familia

Van tres fallos con el mismo origen desde la fase 1: **la lectura relacional no reproducía algo que la tabla plana sí hacía**.

| | |
|---|---|
| V6.9.79 | `'N/A'` contra `NULL` → 2 filas rojas por un camino y 237 por el otro |
| V6.9.82 | valores escritos en una columna alias → invisibles para la lectura relacional |
| V6.9.84 | `Nombre Completo` no se calculaba → «(sin nombre)» en toda la app |

Las tres se arreglan igual: **una sola definición que ven los dos caminos**. Cuando algo se calcula o se normaliza al leer, tiene que estar en el punto por el que ambos pasan, no dentro de una de las ramas.

---

## [6.9.83] - 2026-07-29 — Segundo modelo local: 139 de 154 recuperados, filas rojas 77 → 57

`ministral-3-14b-instruct-2512` sobre los 38 que quedaban, con la misma guarda y la misma regla: **se escribe solo donde coincide con la lectura verificada**.

```
38 pendientes

COINCIDE con la lectura   23   -> escritos
no se pronuncia           14   -> cola del patólogo
DISCREPA                   1   -> cola del patólogo
```

### El segundo modelo desempata, no manda

De los 23 escritos, **21 son casos donde el primer modelo se abstuvo**: ahí ministral rompe el empate a favor de la lectura y quedan dos lectores de acuerdo, que es la regla de siempre.

Los otros 2 son más interesantes, porque el primer modelo **discrepaba**:

```
IHQ250688 · CK5/6        «PIERDEN EXPRESION DE CELULAS MIOEPITELIALES (P63, CK 5-6)»
IHQ260353 · E-CADHERINA  «E-CADHERINA Y P120 CON MARCACION MEMBRANOSA NEGATIVA»
```

Los dos son NEGATIVO. Con ministral queda **2 contra 1** a favor de la lectura, y coincide con lo que el informe dice literalmente. Eran justo los dos que `mistral-nemo` había leído como POSITIVO — las trampas de «pierde expresión» y de la negación al final de la frase que el propio módulo advierte en su cabecera.

Que un modelo se equivoque en esas dos y el otro no **es el argumento de todo el diseño**: ninguno es de fiar por sí solo, y por eso nada se escribe con un único lector.

### Lo que no gana el modelo grande

14B frente a los 12B de nemo, y **más lento por llamada** (38 valores tardaron lo que 110 con nemo). No sustituye al primero: lo complementa donde se abstiene. La configuración del programa sigue apuntando a `mistral-nemo-instruct-2407`; el segundo modelo se pasó explícito a `_llm_local_call`, sin tocar `config.ini`.

### Estado

```
biomarcadores en BD   11.708 -> 11.731
filas rojas               77 ->     57     (ambos caminos: 57, diferencia 0)
de los 154 del informe   139 dentro · 15 pendientes
valores atrapados en columna alias : 0     (esta vez se canonizó al escribir)
```

El rojo, en cinco versiones: **237 → 165 → 150 → 77 → 57**.

### Las 15 que quedan, y por qué

| motivo | |
|---|--:|
| ninguno de los dos modelos se pronuncia | 12 |
| el valor no es una polaridad (un `%`, «no valorable») — ningún modelo puede confirmarlo | 2 |
| un modelo confirma y el otro discrepa | 1 |

`herramientas_ia/resultados/cola_revision_ia.csv` trae una línea por valor con **lo que dijo cada lector y las dos citas**, para adjudicar sin abrir el PDF. Es el residuo esperado: el proyecto ya tenía medido que el 100 % automático no existe con esta GPU, y estas 15 son exactamente eso — no un fallo del método, sino su frontera.

---

## [6.9.82] - 2026-07-29 — La IA local resuelve la cola: 96 valores más, filas rojas 150 → 77

Lo que un regex no pudo —y costó una reversión medida demostrarlo— lo resuelve la comprensión de la frase. **116 de los 154 valores** que el informe reporta están ya en la base de datos.

### Dos lectores independientes, y solo se escribe cuando coinciden

La IA local **no es la autoridad**: es un segundo lector. La cola ya traía, para cada valor, la lectura de un revisor con verificación adversarial y su cita comprobada literal en el PDF. Ahora se compara con el veredicto del modelo local, y solo se escribe donde los dos dicen lo mismo.

Se reutilizó tal cual la capa de la V6.9.61 (`core/extractors/biomarcador_polaridad_ia`), sin tocar una línea: clasificación **cerrada** (POSITIVO | NEGATIVO | NO_DICE), vocabulario limitado a marcadores que ya sabemos que el informe nombra, y **cita obligatoria verificada literal** — si la cita no está en el texto, el veredicto se descarta. Una alucinación no puede sobrevivir a esa guarda.

`mistralai/mistral-nemo-instruct-2407`, endpoint validado como local antes de cada llamada. Los informes no salieron del equipo.

```
133 pendientes · 110 casos · 13 min

COINCIDEN            96   72 %   -> escritos
no se pronuncia      34   26 %   -> siguen en cola
DISCREPAN             3    2 %   -> decide el patólogo
```

### Las 3 discrepancias las falla la IA, no la lectura

Vale la pena mirarlas, porque justifican el diseño:

```
IHQ250688 · CK5/6        «PIERDEN EXPRESION DE CELULAS MIOEPITELIALES (P63, CK 5-6)»
                          lectura NEGATIVO · IA POSITIVO
IHQ260353 · E-CADHERINA  «E-CADHERINA Y P120 CON MARCACION MEMBRANOSA NEGATIVA»
                          lectura NEGATIVO · IA POSITIVO
IHQ250471 · KI-67        «…ES MENOR AL 5%…»  no es una polaridad, es un porcentaje
```

Las dos primeras son exactamente la trampa que el propio módulo advierte en su cabecera: «pierde expresión» y una negación al final de la frase. Con un solo lector se habrían escrito invertidas. **El acuerdo de los dos es lo que hace segura la escritura**, no la confianza en el modelo.

### Estado

```
biomarcadores en BD   11.612 -> 11.708
filas rojas              150 ->     77     (ambos caminos de lectura: 77, diferencia 0)
de los 154 del informe   116 dentro · 38 pendientes (6 con polaridad invertida)
```

Recorrido completo del rojo en tres versiones: **237 → 165 → 150 → 77**.

Las dos colas para el patólogo:
- `herramientas_ia/resultados/cola_revision_ia.csv` — 37 líneas, cada una con **las dos citas** (la de la lectura y la de la IA) para poder adjudicar sin abrir el PDF.
- `herramientas_ia/resultados/valores_en_pdf_no_extraidos.csv` — los 38 que siguen sin valor.

### ⚠️ Un fallo propio, detectado por el invariante

Tras escribir los 96, los dos caminos de lectura dejaron de coincidir (77 contra 78). Causa: la cola se construyó **antes** de unificar las columnas duplicadas, así que traía `IHQ_ACTINA_MUSCULO_LISO`, y el script escribió ahí sin canonizar. El valor quedaba visible en la tabla plana e **invisible en la lectura de la app**, porque el modelo relacional ya no registra las columnas alias.

Un solo caso (`IHQ251368`), movido a `IHQ_SMA`. Lo relevante es que **el invariante de la V6.9.79 lo cazó al instante**: para eso se puso. Toda escritura a una columna de biomarcador debe pasar por `canonico()`.

---

## [6.9.81] - 2026-07-29 — 78 resultados recuperados del PDF, y un patrón genérico que hubo que revertir

De los 154 valores que el informe reporta y la base de datos no tenía, **21 ya están dentro**, más **62 recuperados** por un camino que apareció al investigarlos. Las filas rojas bajan de 165 a **150**.

### Los 154 no eran un problema, eran tres

Primera medición, antes de tocar nada: la BD se llenó con código anterior, así que parte del trabajo podía estar hecho.

| | |
|---|--:|
| el extractor de hoy **ya los produce** (solo faltaba escribirlos) | 31 |
| no reconoce el nombre que usa el informe (alias) | 1 |
| reconoce el nombre pero **ningún patrón casa la frase** | 122 |

### De los 31 «gratis», solo 16 lo eran

Contrastar la polaridad del extractor con la cita verificada del informe destapó que **15 de los 31 la tienen invertida**:

```
«NO SE OBSERVA MARCACION PARA … CICLYNA-D1»        → el extractor dice POSITIVO
«MARCACION NEGATIVA PARA PAX8, CK7, CEA, CA19.9»   → el extractor dice POSITIVO
«SIN MARCACION PARA: … CK5-6 …»                    → el extractor dice POSITIVO
```

Escribirlos a ciegas habría metido 15 polaridades falsas en una BD clínica. Se escribieron **16**, cada uno con la frase del informe que lo respalda; los 15 quedan en la cola con la marca de por qué no se tocan.

### La notación de signo: 62 valores más

Investigando por qué fallaba E-cadherina apareció que sus 6 patrones exigen el marcador **pegado** a la palabra de polaridad (`E-CADHERINA: POSITIVO`), y el informe escribe otra cosa. Entre las formas no cubiertas había una que sí se puede reconocer sin ambigüedad, porque **la polaridad está escrita, no deducida**:

```
"WT1 (+ DEBIL), CALRRETININ (+ FOCAL), PAX-8 (-)"
"SALL-4 (+), OCT-4 (+), D2-40 (+), CD30 (-), AFP (-) Y CKAE1/AE3 (-)"
```

Patrón nuevo, aditivo (solo rellena marcadores sin valor). Medido sobre los 2.076 casos:

```
+60 valores nuevos · -0 desaparecen · 4 cambian   (los 4, basura -> valor real)
```

Y verificado uno a uno contra el PDF de forma independiente: **60 de 60** tienen la notación literal en su informe con **el signo correcto, 0 discrepancias de polaridad**. Los 4 cambios sustituyen la etiqueta del campo por el resultado (`'R. ESTROGENO' → 'POSITIVO'`, `'(-) Y TTF1 (-)' → 'NEGATIVO'`).

En BD: **19 celdas vacías rellenadas y 43 `NO MENCIONADO` sustituidos**. Ese literal no es un resultado —es la marca de «se pidió y el informe no lo reporta»— y aquí está probado que sí lo reporta. Mismo criterio que `fusionar()` en el registro canónico.

Más el alias que faltaba: el informe escribe `CALRRETININ` (doble R, sin -A final), combinación que no estaba.

### ⚠️ El patrón genérico: revertido

El grueso de los 122 responde a una sola forma —`PRESENTAN <marcación> PARA <lista>`— y se implementó con todas las precauciones que este archivo ha aprendido a golpes: **sin `re.DOTALL`**, acotado a la frase con `[^.\n]`, aditivo, y con la polaridad decidida por la cláusula que gobierna. Medido:

```
+808 valores nuevos (se buscaban 122) · 206 CAMBIAN DE VALOR
IHQ250213: CDX2, CK7, CK20, CKAE1AE3, GATA3, PAX8 y TTF1 pasaban de NEGATIVO a POSITIVO
```

**Revertido**, y confirmado con el banco que la vuelta atrás es exacta (`+0 / -0 / 0 cambios`). El motivo está escrito en el propio archivo para que nadie lo reintente igual: ser aditivo no basta, porque al entrar antes que los patrones específicos gana la carrera y el valor bueno ya no se escribe. Y el sustantivo suelto («marcación … para …») describe en el informe tanto el resultado del tumor como **el control, el tejido normal acompañante o el panel solicitado**. Un regex no distingue eso, y aquí la diferencia es POSITIVO contra NEGATIVO en un informe oncológico.

Lo que haría falta no es otro patrón sino resolver la frase con la IA local + guarda de cita verbatim, que es la vía ya medida al 98 % en la V6.9.61.

### Estado

```
biomarcadores en BD   11.577 -> 11.612
filas rojas              165 ->    150
de los 154 del informe    21 dentro · 133 pendientes (15 con polaridad invertida)
```

La cola actualizada, con la frase literal de cada caso y por qué está pendiente, en `herramientas_ia/resultados/valores_en_pdf_no_extraidos.csv`.

⚠️ **Encontrado de paso, sin tocar:** `IHQ260474 · IHQ_P63` vale `POSITIVO` en la BD y el informe escribe `P63 (-)`. Sobrescribir una polaridad real no lo decide un script; queda señalado para el patólogo.

---

## [6.9.80] - 2026-07-29 — El marcador fantasma: la guarda de veracidad, también fuera

Las filas rojas bajan de **237 a 165** sin tocar un solo criterio del verificador. Las 72 que desaparecen nunca debieron estar: señalaban un biomarcador que el patólogo jamás pidió.

### No era el patrón de prefijo, era dónde acaba la guarda

La hipótesis de partida —un patrón que confunde `CD38`→`CD138` y cualquier `CK`→pancitoqueratina— era correcta en el síntoma y equivocada en el sitio. Trazado sobre `IHQ250076`, cuyo informe solo nombra CK7 y CK20:

```
extract_biomarkers   (con la guarda V6.9.60)  ->  CK7, CK20            ✓ correcto
extract_ihq_data                              ->  + IHQ_CKAE1AE3=POSITIVO   ✗
map_to_database_format                        ->  + CKAE1AE3 en solicitados ✗
```

La guarda de veracidad **ya existía y funcionaba**. El problema es que `extract_ihq_data` vuelve a inyectar biomarcadores *después* de ella —pase final, sincronización desde Factor Pronóstico, extractor narrativo— y esa segunda cosecha no la atravesaba.

Y de ahí salta a la lista de estudios: cuando el informe no trae lista propia, `map_to_database_format` la rellena **con los biomarcadores que tienen valor**. Un valor fantasma se convertía así en un estudio solicitado inexistente, y la fila salía en rojo por un marcador que nadie pidió.

La guarda se aplica ahora también en la salida de `extract_ihq_data`, reutilizando la misma función —no se reimplementa el criterio, que es justo como se desincronizan las cosas en este código—.

⚠️ **Hizo falta un segundo intento.** La primera versión filtraba solo las claves con prefijo `IHQ_` y el fantasma resucitaba igual: la clave viva era la minúscula `ckae1ae3`, que `map_to_database_format` convierte en columna una etapa más tarde. Ahora se juzgan las dos formas.

### Radio medido antes de aplicar

No se puede medir re-extrayendo: `extract_ihq_data` tarda >30 s por caso sobre el texto completo (~17 h el corpus). Pero la BD la produjo ese mismo pipeline, así que basta con pasar el oráculo de la guarda por todo lo guardado:

```
valores de biomarcador en BD      : 11.577
los que la guarda descartaría     :     14   (0,12 %)
```

Verificados **uno a uno**: 13 no tienen ni una aparición del marcador en su informe (`IHQ250405` guarda `RECEPTOR_ESTROGENOS=POSITIVO` y el informe solo nombra CK7 y CK20; `IHQ260324` guarda el literal `'Y RP'`). El 14º es `IHQ260343 · KAPPA`, la inferencia clínica que ya quedó anotada en la V6.9.78 a criterio del patólogo. No es una regresión: es la misma limpieza, alcanzando donde antes no llegaba.

### Las 80 entradas fantasma ya guardadas

El arreglo evita que vuelva a pasar; el dato viejo hay que quitarlo aparte. **80 entradas retiradas** de `IHQ_ESTUDIOS_SOLICITADOS` (43 `CD138`, 37 `CKAE1AE3`), con doble evidencia independiente: barrido determinista con frontera de palabra y todas las grafías del informe, más la lectura de los informes por agentes con verificación adversarial.

```
entradas CD138/CKAE1AE3 en la BD  ->  463 legítimas (intactas) · 80 fantasma (retiradas)
casos que quedan sin ningún estudio solicitado : 0
listas malformadas tras la edición             : 0
```

### Lo que NO se tocó, y por qué

El barrido inicial proponía **107** retiradas. Se aplicaron 80. Las otras 27 se quedan porque los dos oráculos discrepan: `_marcador_mencionado` no reconoce `MIOGENINA` frente a su columna `IHQ_MYOGENIN`, ni `ACTINA DE MÚSCULO LISO` frente a `IHQ_SMA`. Borrar por un oráculo con huecos destruye solicitudes legítimas, y aquí se prefiere un rojo de más que un dato de menos.

⚠️ **Dos trampas de método, para que no se repitan.** La primera versión de la comprobación quitaba `SMA` en 57 casos: `_resolver_columna('SMA')` devolvía `IHQ_AML` —la columna alias que la V6.9.79 vació— y el informe dice «SMA», no «AML». Corregido: el verificador resuelve ya a la columna canónica. La segunda: al contrastar «¿está el marcador en el texto?» sin frontera de palabra, `CD3` daba positivo dentro de `CD38`. Es la familia de errores de subcadena que este proyecto arrastra desde la V6.9.72, y esta vez el que cayó fui yo comprobando.

### Estado del rojo

```
V6.9.78   2 rojas (medidas mal, contra un SQLite desfasado)
V6.9.79 237 rojas — ambos caminos de lectura por fin coinciden
V6.9.80 165 rojas — fuera las que señalaban un estudio inexistente
```

De esas 165, la mayoría siguen escondiendo **valores que el informe sí reporta y no supimos extraer**: 154 identificados con su cita literal en `herramientas_ia/resultados/valores_en_pdf_no_extraidos.csv`. Ese es el trabajo que queda.

---

## [6.9.79] - 2026-07-28 — Fase 3: un anticuerpo, una columna

`SMA` es la sigla inglesa de «actina de músculo liso»: la misma tinción. El esquema tenía **cuatro** columnas para ella, y el informe elige un nombre u otro sin criterio fijo, así que el valor caía en una y quien lo buscaba miraba en otra.

### Primero: cuáles son duplicados y cuál no

La lista que se iba a fusionar incluía `ACTINA_MUSCULO_ESPECIFICA`. **Es otro anticuerpo** —MSA/HHF35 marca además la esquelética y la cardíaca— y el PDF lo demuestra: hay informes que piden las dos en la misma frase.

```
IHQ250123: «…myogenina, ACTINA DE MUSCULO LISO, ACTINA MUSCULO ESPECÍFICA, KI-67 y S100»
IHQ250140: «positivas para ACTINA DE MÚSCULO ESPECIFICA, SMA y caldesmón»
```

Fusionarlas habría destruido información clínica. La prueba contraria, en un solo informe:

```
IHQ251122: «Sin marcación para desmina, ACTINA DE MÚSCULO LISO y S100.
             CD34 y SMA negativos»          <- mismo patólogo, mismo resultado, dos nombres
```

Y seis casos más donde el informe **pide con un nombre y reporta con el otro** (IHQ250149, 250324, 250488, 250696, 250903, 250997).

| grupo | columnas | valor real |
|---|---|--:|
| actina músculo **liso** (SMA) | `IHQ_SMA` · `IHQ_ACTINA_MUSCULO_LISO` · `IHQ_AML` · `IHQ_ACTIN` | 66 · 20 · 0 · 0 |
| actina músculo **específica** (MSA) | `IHQ_ACTINA_MUSCULO_ESPECIFICA` · `IHQ_MSA` | 2 · 0 |

`IHQ_AML` no contenía un solo resultado: solo el aviso «NO MENCIONADO».

### La causa de fondo no era la extracción

La equivalencia estaba declarada —cuando lo estaba— en **cinco tablas mantenidas a mano**: el extractor, `unified_extractor`, el verificador de completitud, el auditor y la configuración de IA. La V6.4.24 arregló el extractor y nadie tocó el resto; incluso dejó escrito *«Actina de músculo liso (NO confundir con SMA que es biomarcador independiente)»*, que es clínicamente falso. Dos líneas más abajo, el mismo diccionario se contradecía: `'SMOOTH MUSCLE ACTIN': 'ACTINA_MUSCULO_LISO'` junto a `'SMA': 'SMA'`.

Ahora hay **un solo sitio**, `core/biomarcadores_canonicos.py`, con la frase del informe que justifica cada equivalencia. Un grupo sin esa evidencia no entra.

### Qué cambió

```
IHQ_SMA                    82 -> 100      IHQ_ACTINA_MUSCULO_LISO  23 -> 0
IHQ_AML                     2 ->   0      IHQ_ACTIN                 0 -> 0
IHQ_ACTINA_MUSCULO_ESPECIFICA  2 ->   2   <- intacta, es otro anticuerpo
```

Los 7 que «faltan» son los casos que tenían dos columnas rellenas a la vez y ahora son una. **0 conflictos**: en ningún caso las dos columnas decían cosas distintas. Las columnas alias se quedan vacías, no se borran del esquema: hay `.exe` instalados en otros equipos contra este MySQL.

Regla al fusionar: un resultado real gana a «NO MENCIONADO», que no es un hallazgo sino la marca de «se pidió y el informe no lo reporta». Si dos columnas tuvieran resultados reales distintos, la fila no se toca y se reporta — eso lo decide el patólogo.

### Verificación

Banco anti-regresión sobre los 2.076 casos, antes y después:

```
+16 nuevos · -18 desaparecen · 0 cambian de valor
casos del grupo con pérdida de valor         : 0
casos con cambios FUERA del grupo            : 0
```

Y de punta a punta: BD y lectura de la app coinciden (100/0/0/0/2/0), el modelo relacional reconstruye con **0 celdas distintas**, y el registro `biomarcadores` pasa de 146 a 142 filas — una por anticuerpo, no por nombre.

Dos guardas para que no vuelva: `save_records()` canoniza antes de escribir (la fase 2 demostró que es el único punto de escritura, así que cubre también la ruta de IA y el auditor, que conservan sus mapeos viejos), y el modelo relacional **avisa** si un valor aparece en una columna alias en vez de corregirlo en silencio.

---

## Las filas rojas ya no dependen de por dónde se lea

`_columna_detectada` no tenía `'N/A'` en su lista de vacíos: contaba el literal como *detectado* y un `NULL` como *ausente*. El modelo relacional normaliza `'N/A' → NULL` (276.781 celdas), así que el mismo registro con el mismo verificador daba dos respuestas:

```
antes  ·  tabla plana cruda   :   2 filas rojas
          lectura de la app   : 237 filas rojas
ahora  ·  ambos caminos       : 237 filas rojas     (diferencia: 0 casos)
```

Entró con la **V6.9.76** y llevaba vivo desde entonces. El peligro no era el número sino el interruptor: `usar_modelo_relacional = false` es la vuelta atrás documentada, y activarlo hacía desaparecer 235 avisos de calidad clínica sin decir nada.

**Qué decidió cuál de los dos números era el bueno.** Un censo de las 303.096 celdas de biomarcador de las filas IHQ:

| contenido de la celda | veces | |
|---|--:|--:|
| `N/A` | 272.808 | **90,0 %** |
| `<NULL>` | 18.711 | 6,2 % |
| POSITIVO / NEGATIVO / valor | 9.651 | 3,2 % |
| `NO MENCIONADO` | 931 | 0,3 % |

Cada fila IHQ lleva entre **111 y 137 de sus 146** columnas de biomarcador puestas a `'N/A'` (mediana 132). Es el relleno por defecto, no una decisión por marcador: tratarlo como «el sistema lo resolvió» era falso. `'NO MENCIONADO'` sí es deliberado —«se pidió y el informe no lo reporta»— y **sigue contando como detectado**.

El arreglo no es añadir `'N/A'` a mano —también divergían `NA`, `NULL`, `-` y `--`, que hoy aparecen 0 veces pero volverían— sino un invariante: **`_SIN_DATO` contiene todo lo que el modelo relacional considera vacío**, derivándolo de él. Así los dos caminos no pueden separarse otra vez. Verificado sin importar el orden de carga de los módulos (no hay import circular).

### Y lo que el rojo estaba diciendo era falso en un 88 %

Que ambos caminos coincidan no significa que las 237 estén justificadas. Se leyeron **los 280 pares (caso, marcador) contra el texto del informe**, con verificación adversarial y una comprobación determinista posterior: cada cita tiene que aparecer **literal** en el PDF y la columna tiene que estar realmente vacía en la BD.

| qué pasa de verdad | pares | |
|---|--:|--:|
| 🔴 el informe **SÍ da el resultado** y no lo extrajimos | **157** | 56 % |
| 🔴 el marcador **nunca se pidió** (solicitud inventada) | 89 | 32 % |
| ✅ se pidió y el informe calla — el rojo es correcto | 34 | **12 %** |

```
citas comprobadas LITERALMENTE en el PDF   : 154 / 157
columna vacia en BD, como se afirmaba      : 154 / 154   (0 afirmaciones falsas)
```

Las 3 restantes son de `IHQ250880`, donde la cita venía abreviada con «...» y el contraste literal la rechaza — correctamente.

**Hay 154 resultados de biomarcador escritos en los informes que no están en la base de datos.** Los más frecuentes: E-CADHERINA (23), SINAPTOFISINA (16), CICLINA D1 (14), IDH1 (11), CK5/6 (9). Lista completa con la frase del informe en `herramientas_ia/resultados/valores_en_pdf_no_extraidos.csv`.

Por caso: de las 237 filas rojas, **126 esconden al menos un valor recuperable del PDF** y **79 son rojo injustificado** (solo solicitud fantasma). Solo 28 lo son por el motivo que el rojo dice significar.

El mecanismo de las fantasma:

```
IHQ250351  el informe dice CD38   ->  la BD solicita CD138     (43 de 43 casos)
IHQ250019  el informe pide CK5/6  ->  la BD solicita CKAE1AE3  (35 de 35 casos)
```

Es la **misma causa que quedó abierta en la V6.9.78**: un patrón que adjudica por prefijo y confunde `CD38`→`CD138` y cualquier `CK`→pancitoqueratina. Allí se vio contaminando resultados; aquí, la lista de estudios solicitados. Listado en `herramientas_ia/resultados/solicitudes_fantasma.csv`.

**Nada de esto se ha tocado.** Son dos trabajos con su propio banco de medición —el patrón genérico por un lado, 154 valores por extraer por otro— y este cambio era el del rojo. Pero conviene saberlo antes de mirar esa pantalla: hoy el rojo no significa «el laboratorio no lo reportó» sino, cuatro de cada cinco veces, «nosotros no lo leímos o nunca se pidió».

⚠️ **Corrección de la V6.9.78:** allí se dijo que había «299 filas rojas, 81 por SMA». Era falso: esa medición llamaba al verificador sin pasarle el registro, y por esa vía lee un SQLite de 2.073 filas que va desfasado. Lo que el usuario ve son las 237 de arriba.

---

## [6.9.78] - 2026-07-28 — Verificación completa contra los PDFs · biomarcadores 99,97 % respaldados

Verificación **independiente del extractor** de todo lo que hay en la BD contra los 765 PDFs, y corrección de lo que apareció. Las reglas de re-lectura se escribieron aparte a propósito: usando el mismo código, la comparación no probaría nada.

### La lectura del PDF no es OCR
```
765 PDFs · 36.243 páginas · 69,5 M caracteres · 0 páginas sin capa de texto
```
El código usa el texto nativo si la página trae más de 50 caracteres y solo entonces recurre a tesseract. Como **ninguna** página baja de ese umbral, la rama de OCR nunca se ejecuta. Por eso los fallos de extracción son siempre de *lógica* —qué trozo del texto se toma—, nunca de *lectura*.

⚠️ **Tesseract NO está instalado** en el equipo (`TesseractNotFoundError`), y ese error no se captura: reventaría el PDF entero. Hoy da igual porque el HUV genera PDFs digitales, pero el sistema no es tolerante, es afortunado. Y hay una asimetría: los IHQ pasan por el lector con respaldo OCR; las **coloraciones leen con PyMuPDF directo, sin ningún respaldo** — una coloración escaneada saldría vacía en silencio.

### Campos de cabecera: 22.764 casos comparados uno a uno
| campo | coincide | difiere |
|---|--:|--:|
| género, edad, fecha informe, EPS, fecha ingreso | 22.764 | **0** |
| cédula | 22.691 | **0** |
| nombre | 22.760 | 4 → corregidos |
| servicio | 22.086 | 16 *(regla de negocio V5.3.8)* |

Diagnóstico comprobado aparte: **292 de 293 con todas sus líneas literales en el PDF (99,7 %)**; el único fallo es un dx de 4 páginas que quedó pegado al salto arrastrando la letra del siguiente espécimen.

### Las coloraciones no leían 5 campos que el informe SÍ trae
`extraer_demografia` capturaba 8 campos y se detenía ahí — el propio docstring decía *"demografía mínima"*. Resultado: 20.471 filas (el **91 % de la BD**) con esos campos vacíos aunque estuvieran impresos.

| campo | antes | ahora |
|---|--:|--:|
| EPS | 0,1 % | **100 %** |
| Médico tratante | 0,1 % | **100 %** |
| Servicio | 0,1 % | **100 %** |
| Fecha de ingreso | 0,1 % | **100 %** |
| Patólogo | 0,1 % | **83,5 %** |

**98.854 celdas rellenadas**, solo donde estaban vacías; ningún valor existente se pisó. Más **14 correcciones de identidad** que destaparon bugs viejos: la cédula guardada como nombre (`'42159318' → 'NAYIVE'`, 5 casos), la edad pegada al apellido (`'DE GAMBA 78'`, 4 casos) y un dígito perdido en una cédula (`M2511941: 6218273 → 62182273`).

⚠️ **El patólogo salía mal en la primera versión.** El informe pone el nombre en la línea *anterior* a la etiqueta:
```
ARMANDO CORTES BUELVAS       <- el nombre
Responsable del análisis:
MD Patólogo                  <- lo que capturaba la primera versión
```
De haberse aplicado habría escrito 17.000 veces el cargo en vez del nombre.

### Iniciales del nombre (`name_splitter`)
El filtro `len(t) > 1` descartaba **toda palabra de una letra**, y con ella las iniciales: `ELISA DE C ECHETO` perdía la "C". Ahora se conserva si es una letra; se siguen descartando dígitos sueltos y signos, que es para lo que estaba el filtro.

### Biomarcadores: 11.586 valores contra el PDF
Tres comprobaciones de fuerza distinta, reportadas por separado porque mezclarlas daría una cifra engañosa.

| | |
|---|--:|
| **presencia** — el marcador se menciona en el informe | **11.583 / 11.586 (99,97 %)** |
| **valor numérico** — el `%` o el score está literal en el texto | **512 / 512 (100 %)** |
| **polaridad** | ver abajo |

Se ampliaron los alias con las formas que usan los informes reales: `AE1/3`, `CK AE1/3`, `AE1/AE2` (errata recurrente del propio informe), `GLYPICAN` a secas, y `KAPPA`/`LAMBDA`, que no figuraban en `_ALIAS_PDF`.

**Borrados 2 valores sin respaldo** (`IHQ250345` y `IHQ260591`, `IHQ_CKAE1AE3`): el informe nombra CK7 y CK20 pero **nunca AE1/AE3**. Un patrón genérico de `CK` estaba adjudicando a la pancitoqueratina el resultado de otras citoqueratinas. Evidencia en `backup_borrado_bio_20260728_134951.json`. La causa de fondo —ese patrón genérico— **sigue abierta**.

Queda un tercer caso sin borrar, `IHQ260343 · KAPPA = NEGATIVO`: el informe dice *"restricción a cadenas lambda"*, de lo que se deduce, pero no lo afirma. Es una inferencia clínica, no un error de lectura; se deja a criterio del patólogo.

⚠️ **La polaridad NO se verificó aquí.** Es el 85 % de los valores y va en prosa libre; la comprobación determinista da 22,7 % de coherencia, cifra que mide el método y no los datos. Lo válido sigue siendo el trabajo de V6.9.61 (IA local + guarda de cita, 98 % medido): **585 correcciones esperando la firma del patólogo** en `cola_revision_polaridad.csv`, cada una con la frase literal del informe.

### Por qué hay filas en rojo en el Visualizador
No es un error: el rojo (`#FFE5E5`) marca los casos donde el patólogo **solicitó** un biomarcador y el informe **no reporta su resultado**. Los 11 campos de datos están completos en esas filas. Es control de calidad, no un fallo — salvo cuando el resultado sí está y no supimos leerlo (`IHQ250013`, SMA: *"FOCAL POSITIVIDAD PARA SMA"*).

---

## [6.9.77] - 2026-07-28 — Modelo relacional: fase 2 (escritura incremental)

`save_records()` resultó ser el **único** punto de escritura: por ahí pasan la importación de PDFs, las coloraciones, la reconciliación, el extractor y las tres llamadas de `ui.py`.

En vez de replicar ahí la lógica de UPSERT parcial —que abre la puerta a que los dos modelos diverjan en silencio— la tabla plana se escribe como siempre y después se **re-leen de ella los casos recién tocados**. Es imposible que difieran: la fuente sigue mandando y el relacional es su proyección exacta.

```
save_records            0,17 s   (escritura + propagación incremental)
lectura tras escribir   0,67 s   SIN repoblado   (antes: 5,6 s de repoblado completo)
```

Tres redes de seguridad en capas: si la propagación falla no se propaga el error (el dato ya está guardado); la huella lo caza en la lectura siguiente; y si el modelo no está disponible se lee la tabla plana. Verificado tras aplicar: `CELDAS DISTINTAS: 0`.

---

## [6.9.76] - 2026-07-28 — Modelo relacional: fase 1 (lectura)

`get_all_records_as_dataframe()` lee del modelo relacional manteniendo su contrato —el mismo DataFrame de 189 columnas—, así que dashboard, informe PDF, auditor, exportaciones y vista Por Paciente siguen funcionando sin tocarlos.

| | |
|---|--:|
| lectura hoy | 1,08 s · 171,7 MB |
| **lectura nueva** | **0,64 s · 70,8 MB** |
| equivalencia | **0 celdas distintas de 4.238.836** |

**2,4x menos datos por la red** en cada arranque, que importa porque los `.exe` corren en otros equipos contra este MySQL.

⚠️ El riesgo real no era el rendimiento sino **servir datos obsoletos**. La huella que existía —`(COUNT, MAX(Fecha Ingreso Base de Datos))`— no valía: esa columna está **100 % vacía**, así que solo comparaba el número de filas y un `UPDATE` en sitio pasaba desapercibido. Ahora usa `CHECKSUM TABLE ... EXTENDED` (95 ms), que detecta cualquier cambio. Probado: un `UPDATE` directo por fuera de la app se detecta y resincroniza solo.

**Medición que corrigió el plan:** se esperaba que el pivot de 146 biomarcadores fuera el cuello de botella y que hubiera que materializar. Las dos cosas eran falsas — la vista rinde (1,65 s) y materializar es lo **peor** (1,57 s + 4,08 s por escritura). Lo mejor es **no pivotar en SQL**: dos consultas y el pivot en pandas.

Reversible con `usar_modelo_relacional = false` en `config/config.ini`.

---

## [6.9.75] - 2026-07-28 — Modelo relacional: fase 0 (esquema y volcado)

La BD era **una** tabla de 22.547 × 189 sin claves foráneas, con **3.291.862 celdas de biomarcador para 11.586 valores reales (0,35 % de ocupación)** y el paciente repetido en cada fila.

| tabla | filas |
|---|--:|
| `pacientes` | 18.271 |
| `estudios` | 22.547 |
| `biomarcadores` | 146 |
| `resultados_biomarcador` | **11.586** |

Con 3 claves foráneas donde antes había 0. `informes_ihq` **no se tocó**.

**Dos decisiones que salieron de medir, no de suponer:**

1. Los datos demográficos **no son constantes por paciente**: el nombre varía en 9 pacientes con la misma cédula, el género en 2, el documento en 19 y la edad en 203. Una tabla `pacientes` ingenua habría **perdido datos**. Cada estudio conserva los suyos tal como los registró ese informe —que además es lo correcto: el informe es un documento legal— y `pacientes` guarda solo la identidad para agrupar.
2. Hay **dos formas de vacío**: `NULL` (3.003.477 celdas) y el literal `'N/A'` (276.799). Ningún código los distingue, así que la reconstrucción normaliza a `NULL` y la verificación lo reporta aparte.

Verificación: se reconstruye la tabla plana desde el modelo y se compara celda a celda → **0 diferencias**, 22.547 / 22.547.

---

## [6.9.74] - 2026-07-27 — Ficha del paciente: toda la información del informe

La ficha omitía **23 campos con dato** en un caso IHQ y 11 en una coloración: edad, género, documento, patólogo, sede, EPS, especialidad, departamento, municipio, CUPS, tipo de examen y las tres fechas.

Ahora hay tres bloques nuevos: cabecera con los datos del paciente, contexto del estudio, y un cajón final **«Otros datos del informe»** con cualquier campo poblado que no haya salido antes — para que nada quede invisible aunque mañana se añada una columna. Verificado: **0 campos con dato ocultos**.

Y se corrigió el silencio que causó la confusión: cuando un estudio no tiene biomarcadores, la sección no desaparece, dice por qué (*"las coloraciones son tinciones básicas y no llevan biomarcadores"*).


## [6.9.73] - 2026-07-27 — Auditoría del informe estadístico: 7 bugs de clasificación · vista Por Paciente · rótulos de coloración

Cuatro frentes: auditoría del **Informe estadístico (PDF)**, arreglos en el diagnóstico principal, una vista nueva agrupada por paciente, y el rótulo del espécimen que se guardaba como diagnóstico en las coloraciones.

---

### 1. Informe estadístico: la aritmética estaba bien, la clasificación no

Auditoría con 14 agentes (7 recalculando cada bloque contra los datos crudos + 7 escépticos intentando tumbar cada hallazgo): **29 hallazgos confirmados, 6 descartados**.

**76 cifras verificadas una a una y todas cuadran**: periodo, los 2.076 casos, el 68,8 %, las 89 filas de la tabla maestra con sus columnas Hombres/Mujeres, las 22 no oncológicas, los 12 órganos, los 12 biomarcadores. Los bloques *Resumen por sexo* y *Órganos/Biomarcadores* salieron limpios al 100 %.

El problema no era el cálculo: era **qué se cuenta y cómo se etiqueta**.

| KPI | antes | ahora |
|---|--:|--:|
| **% MALIGNOS** | 68,8 % | **67,1 %** |
| **TUMORES ANALIZADOS** | 1.613 | **1.566** |
| Casos CON diagnóstico | 1.950 (93,9 %) | **2.002 (96,4 %)** |
| Casos SIN diagnóstico | 126 (6,1 %) | **74 (3,6 %)** |
| Carcinoma de pulmón | 40 | **48** |
| Linfoma Hodgkin | 12 | **15** |
| «Estudio IHQ de marcadores» | 71 | **18** |

**169 casos recategorizados** y **35 malignidades corregidas**.

#### Los siete bugs

1. **Primarios contados como metástasis.** `ORIGEN PULMONAR` era patrón de *carcinoma metastásico*: 8 adenocarcinomas primarios de pulmón, en muestras **de pulmón**, contaban como metástasis. Ahora se exige que el dx diga metástasis **o** que el órgano no coincida con el origen declarado.
2. **La falta de ortografía decidía la categoría.** `HODKING` (3 casos) y `CEULAS`/`CELUULAS` (5) mandaban linfomas a la bolsa genérica mientras los bien escritos iban a su categoría.
3. **8 informes que DESCARTABAN linfoma contaban como linfoma** — y los 8 estaban marcados `MALIGNO`. Faltaban todas las formas negativas (`SIN COMPROMISO POR LINFOMA`, `NEGATIVO PARA INFILTRACIÓN LINFOMATOSA`).
4. **La bolsa «SIN TUMOR CLASIFICADO» se evaluaba antes que los tumores**, así que la sola palabra «inmunohistoquímica» ganaba a `LINFOMA T ANAPLÁSICO`. Ahora es último recurso: se anota y se sigue buscando un tumor real. **55 casos recuperados**, 11 de ellos carcinomas ductales de mama.
5. **PitNET / adenoma de hipófisis**: la misma entidad recibía tres categorías y dos malignidades según cómo la escribiera el patólogo. Unificada (2 → 20 casos) y corregidos los 17 marcados `MALIGNO` — son tumores benignos.
6. **`LESION BENIGNA / HIPERPLASIA` mezclaba dos cosas.** 77 hiperplasias reactivas, adenosis y pólipos inflamatorios contaban como tumores. Partida en dos; las neoplasias benignas (fibroadenoma, papiloma, adenoma, lipoma) se quedan como oncológicas.
7. **`AXILA` casaba dentro de `MAXILAR`** — y al arreglarlo aparecieron cuatro hermanos del mismo bug de subcadena:

| valor real | iba a | ahora |
|---|---|---|
| `RETROPERITONEO` (14 casos) | Peritoneo / Epiplón | **Retroperitoneo** |
| `GLÁNDULA ADRENAL` (7) | Riñón *(por «RENAL»)* | **Glándula suprarrenal** |
| `MAXILAR` (4) | Ganglio linfático | **Hueso** |
| `PARATIROIDES` (1) | Tiroides | **Paratiroides** |
| `SILLA TURCA` (1) | Leucemia linfoide aguda *(por «LLA »)* | **Tumor neuroendocrino** |

*Ganglio Linfático* baja de 201 a 195 casos. La tabla declaraba «lo más específico primero» y tres pares estaban invertidos.

#### Verificación de las 35 malignidades
Revisión **ciega** por 4 revisores que no veían la propuesta: **35 confirmadas, 0 discrepancias**, 3 declaradas AMBIGUAS (NIC I, displasia biliar de bajo grado) y **no tocadas** — mismo criterio que con las 942 de V6.9.71. Backup con evidencia en `backup_malig38_20260727_083121.json`.

#### Un guarda que hizo falta
La primera versión de la regla marcaba BENIGNO a `IHQ251066` — *"granuloma abierto sin amastigotes **y carcinoma basocelular trabecular y nodular infiltrante**"*. Un mismo espécimen puede traer las dos cosas. Ahora **nunca se degrada a benigno un informe que nombra un cáncer**.

#### Lo que NO se tocó, a propósito
**66 casos sin diagnóstico** (26 «ver descripción microscópica», 24 médula ósea solo morfología, 16 marcadores sueltos) conservan su etiqueta binaria de malignidad. Escribir `BENIGNO` ahí sería inventar exactamente igual que dejar `MALIGNO`: el informe no dice nada. La solución honesta es un tercer estado y sacarlos del denominador — decisión de esquema, pendiente.

Quedan también sin tocar los puntos de **presentación** que la auditoría marcó como engañosos: la columna «Órgano principal» (46 de 89 filas deciden la moda con n≤3 o con empate), `CARCINOMA METASTÁSICO` como cajón de sastre (128 de 175 sí dicen el origen), y el KPI «192 categorías anatómicas» (~74 son órganos reales).

---

### 2. Diagnóstico principal: 6 arreglos en el extractor

| | inicio | ahora |
|---|--:|--:|
| aciertos en el banco de 44 casos difíciles | 27 | **36** |
| coincidencia con la BD (2.076) | 2.054 | **2.057** |
| regresiones | — | **0** |

La errata `FAVORCEN` del propio informe, siete formas de basura que el guarda dejaba pasar como diagnóstico (encabezados de página, la técnica suelta, paréntesis truncados), cortes de frontera (`BORDES DE RESECCIÓN`, `BLOQUE A3`, `VER` colgando) y el retroceso al **espécimen A** cuando la zona del diagnóstico queda vacía.

**Cuatro «regresiones» resultaron ser correcciones:** la BD guardaba el *antecedente entre paréntesis* como diagnóstico — `(historia de linfoma de Hodgkin)` → `'LINFOMA DE HODGKIN)'` — cuando el informe decía `PROLIFERACIÓN LINFOIDE ATÍPICA DE CÉLULAS T`.

⚠️ Un intento intermedio devolvía en `IHQ251205` *"NEGATIVO PARA LESIÓN INTRAEPITELIAL"* (espécimen B) cuando el espécimen A sí tenía una lesión NIC I. Corregido: el retroceso va siempre al primer espécimen.

---

### 3. Vista «Por Paciente» (pestaña nueva)

El Visualizador es una fila por **estudio** —correcto para estadística y exportación—, pero dejaba los estudios de un mismo paciente dispersos por la lista. La pestaña nueva los agrupa: **18.271 pacientes · 22.547 estudios**, una fila por paciente que se despliega.

```
› ACENETH SUAREZ PINEDA  66991337  2 · 1 IHQ + 1 coloración
   🔬 IHQ250221  IHQ         MAMA  CARCINOMA INVASIVO DE TIPO NO ESPECIAL (DUCTAL)  HER2: NEGATIVO (0) · KI-67: 30% · …
   🎨 M2515312   Coloración  MAMA  CARCINOMA INVASIVO DE TIPO NO ESPECIAL (DUCTAL).
```

Columnas: Cédula · Estudios · Órgano · Diagnóstico · **Biomarcadores** · Fecha. La columna de biomarcadores muestra **solo los que ese estudio tiene**, en una línea, en vez de 125 columnas casi siempre vacías; los `NO MENCIONADO` se conservan (son señal real de calidad del dato) pero van al final. Doble clic abre la ficha completa del paciente.

Incluye buscador en vivo por nombre o cédula y un interruptor **«Solo con varios estudios»** (3.071 de 18.271).

**Se agrupa SOLO por cédula.** Las filas sin cédula fiable salen sueltas, marcadas `(sin cédula)`: agrupar por nombre fusionaría homónimos, y mezclar la historia clínica de dos pacientes distintos es un error grave, no un detalle de presentación.

**La fila del paciente deja Órgano y Diagnóstico vacíos** a propósito: elegir el diagnóstico de un estudio para «representar» al paciente sería afirmar algo que el informe no dice.

Construirla tardaba 10,2 s leyendo el DataFrame fila a fila; volcando las columnas a listas bajó a **0,3 s**.

⚠️ El mismo árbol **no** se pudo montar sobre la tabla del Visualizador: `tree_build` de tksheet revienta con `KeyError: 0` al reutilizar esa hoja. Descartadas ocho condiciones (datos, kwargs, `grid`, `enable_bindings`, ventana dibujada, pestaña no visible, `safety`, resets) — fuera de la app funciona siempre, dentro falla siempre. Sobre una **hoja nueva creada en modo árbol** funciona sin problema, que es como está hecha esta vista. La tabla del Visualizador quedó sin tocar.

También se probó **quitar los biomarcadores del Visualizador** (139 → 17 columnas). Revertido a petición del usuario: es donde se comparan biomarcadores entre casos. El interruptor `MOSTRAR_BIOMARCADORES_EN_TABLA` queda en `core/columnas_visor.py` por si se quiere apagar en otro momento; afecta a la vez a la tabla Tkinter y al visor Qt, para no romper la paridad buscada en V6.9.50.

---

### 4. Coloraciones: el rótulo del espécimen se guardaba como diagnóstico

La sección DIAGNÓSTICO empieza describiendo la muestra, y se guardaba el bloque entero:

```
A. Mama izquierda. Tumor. Cuadrantectomía.        ← rótulo (lo que se leía en la tabla)
CARCINOMA INVASIVO DE TIPO NO ESPECIAL (DUCTAL).  ← el diagnóstico, debajo
GRADO HISTOLÓGICO NOTTINGHAM GRADO 2.
```

Corregidas **16.002 filas**: 15.247 de coloración + 755 filas IHQ que llevan copia del mismo texto. Se limpian las dos, o la reconciliación dejaría de reconocerlas como el mismo diagnóstico.

| | |
|---|--:|
| filas corregidas | **16.002** |
| líneas de rótulo quitadas | 19.960 |
| líneas quitadas que contenían un diagnóstico | **0** |
| filas rechazadas por el control de integridad | **0** |

Solo se borran **líneas completas**, nunca fragmentos, y únicamente si la línea **termina** nombrando el procedimiento **y no contiene ningún término diagnóstico**. Si al quitar el rótulo no quedaría nada, se conserva el original (pasó en 1 caso: `M2513836`). Respaldo con antes/después/líneas quitadas en `backup_rotulos_coloracion_20260727_143811.json`.

🔴 **Acoplamiento que casi cuesta 13.839 procedimientos.** El rótulo es la **única fuente** del campo Procedimiento (`…Biopsia por endoscopia` → `BIOPSIA`), y lo consumen `extraer_procedimiento()` y `clasificar_malignidad()`. Quitarlo dentro de `extraer_diagnostico` los habría borrado en silencio — el 68 % de las filas de coloración. Ahora el bloque completo sigue alimentando las derivaciones y el rótulo se quita **solo al guardar el campo**, en `agrupar_y_extraer`. Verificado tras aplicar: Procedimiento intacto en **20.049/20.471 (97,9 %)**.

---

### Archivos
```
core/normalizador_diagnosticos.py        categorizador: 6 de los 7 bugs
core/normalizador_organos.py             bugs de subcadena + orden de evaluación
core/unified_extractor.py                dx principal + malignidad coherente
core/extractors/coloracion_extractor.py  rótulo del espécimen
core/columnas_visor.py                   interruptor de biomarcadores en tabla
core/enhanced_database_dashboard.py      pestaña Por Paciente
ui.py                                    vista Por Paciente
```


## [6.9.71] - 2026-07-27 — Malignidad de coloraciones: las 942 adjudicadas, 229 corregidas

Adjudicación completa de las **942 discrepancias** de Malignidad en las 20.471 filas de coloración, con doble verificación ciega contra el informe.

### Pasada 1 — adjudicación (36 agentes, 941 casos)
| | |
|---|--:|
| La BD **ya estaba bien** | **547** (58%) |
| **AMBIGUO** (displasias, NIC III, "a clasificar") | **163** (17%) |
| **Errores propuestos** | **231** (25%) |

### Pasada 2 — verificación CIEGA (10 agentes, sin ver la propuesta previa)
| | |
|---|--:|
| **Confirmados por ambos revisores** | **229** |
| 2º revisor dice AMBIGUO → no se aplica | 2 |
| **Discrepan los dos revisores** | **0** |

Concordancia del **99,1%**. Aplicadas **229** con backup y la cita del informe por cada cambio (`evidencia_malig942_20260727_071119.json`). Verificado: 229/229 escritas.

**Reparto:** 209 `MALIGNO → BENIGNO` (falsos positivos de cáncer: *"Cicatriz, negativo para lesión neoplásica"*, *"Epitelio exocervical sin displasia"*, *"Hiperplasia endometrial sin atipia"*) y **20 `BENIGNO → MALIGNO`** — los clínicamente graves: `GLIOBLASTOMA`, `CARCINOMA BASOCELULAR`, `TERATOMA POSPUBERAL con componente germinal maligno`.

**Distribución final coloraciones: 17.024 benignos / 3.447 malignos.**

### Lo que NO se tocó, a propósito
Los **163 AMBIGUOS** son premalignos reales (displasias, NIC II/III, lesión intraepitelial de alto grado, hiperplasia con atipia, "proliferación hematolinfoide a clasificar"). Forzarlos a maligno o benigno sería inventar un dato clínico. Se quedan como están.

### Los KPIs no se movieron
El dashboard **excluye las filas M**, así que Estadísticas Generales sigue en 2.076 casos IHQ / 1.429 malignos. BD íntegra: 22.547 filas, **0 filas vacías**.

⚠️ **La doble pasada era necesaria, no ceremonia:** mi verificador determinista inicial acertaba el 32% frente al 68% de la BD (marcaba malignos `TUMOR DE WARTHIN`, `QUERATOSIS SEBORREICA`, `AMELOBLASTOMA`). Aplicar las 942 sin adjudicar habría destruido ~640 valores correctos.


## [6.9.70] - 2026-07-27 — Estadísticas Generales: 2 bugs de conteo + 4 malignidades incoherentes

Verificación de la pestaña **Estadísticas Generales** tras cargar las 22.547 filas.

### ✅ Lo que ya estaba bien
El dashboard **SÍ excluye las filas M** (coloraciones) de la analítica oncológica — lo arregló V6.9.50. Con 20.471 filas M en la BD, contarlas habría inflado todo. Comprobado: `self.df` se filtra con `~str.match(r"^[Mm]\d")`.

### 🔴 Bug 1: "Días de Datos: 0"
`update_general_stats` tomaba la **primera** columna de fecha de su lista de prioridad —`Fecha de toma`— que existe pero está **entera en "SIN DATO"**, y se rendía con 0. Nunca probaba `Fecha de ingreso` ni `Fecha Informe`.
**Fix:** recorre TODAS las columnas candidatas hasta encontrar una parseable, y dentro de cada una se queda con el formato que parsea más filas.
**Resultado: 497 días** (02/01/2025 → 14/05/2026) en vez de 0.

### 🔴 Bug 2: 4 malignidades incoherentes con su diagnóstico — **causadas por mí**
Al corregir 17 diagnósticos en V6.9.68 **no recalculé `Malignidad`**, que es un campo DERIVADO del dx:

| Caso | Dx | Malignidad tenía |
|---|---|---|
| IHQ250879 | `CARCINOMA INVASIVO (DUCTAL)` | BENIGNO ❌ |
| IHQ260725 | `CARCINOMA INVASIVO (DUCTAL)` | BENIGNO ❌ |
| IHQ260711 | `SARCOMA HISTIOCÍTICO` | BENIGNO ❌ |
| IHQ251333 | `NEGATIVO PARA CARCINOMA` | MALIGNO ❌ |

Verificado con la función oficial del proyecto `_malignidad_coherente` (V6.9.42), no con un regex ad-hoc: **2.076 IHQ → 1.683 coherentes, 389 ambiguos (no opina), 4 discrepan**. Corregidos con backup.
**Casos Malignos: 1427 → 1429** (distribución final: 1429 malignos / 647 benignos).

⚠️ **Lección:** al corregir un dx hay que **recalcular los campos derivados** (Malignidad, y revisar Órgano/categoría). Un fix parcial deja la BD internamente incoherente.

Nota metodológica: mi primer chequeo con regex propio dio 9 "incoherencias", pero 3 eran **falsos positivos míos** (`HEMANGIOBLASTOMA WHO 1` y `CONDROBLASTOMA` son tumores BENIGNOS; mi patrón "blastoma" los marcaba malignos). La función oficial del proyecto era la referencia correcta.

### Claridad: "Total Registros" → "Casos IHQ (sin coloraciones)"
La tarjeta mostraba `2076` mientras la barra de estado decía `22547 registros`. No era un error —el dashboard es analítica IHQ— pero parecía uno. La etiqueta ahora lo dice.

### Malignidad en coloraciones: 12 corregidas, ~300 estimadas, causa raíz medida
Al derivar Malignidad del dx en las 20.471 filas M salieron **942 discrepancias**. Adjudicadas 48 a ciegas contra el informe:

| | acierto |
|---|--:|
| La BD (`determine_malignancy`) | **68%** |
| `_malignidad_coherente(dx)` | 24% |
| Idem quitando antecedentes | **19%** (peor) |

**12 errores reales confirmados y corregidos** (casi todos BENIGNO marcado MALIGNO: `HIPERPLASIA SIN ATIPIA`, `CERVICITIS`, `GANGLIOS NEGATIVOS`, `TUMOR DE WARTHIN`). Estimación: **~300 filas M** afectadas (1,5%).

**Causa raíz** (`medical_extractor.py:3762`): `combined_text` incluye `full_text`, así que un antecedente (*"Historia de adenocarcinoma ductal"*) marca MALIGNO aunque el dx sea `CONDICIÓN FIBROQUÍSTICA`.
⚠️ **NO se cambió el código: se probó quitar los antecedentes y EMPEORA (68% → 19%).** La lógica actual es la mejor de las tres opciones automáticas probadas.

**Impacto acotado:** son filas M, y el dashboard las **excluye** de la analítica oncológica → los KPIs de Estadísticas Generales NO están afectados.

⚠️ **Nota metodológica:** mi verificador acertaba menos que la BD (32% vs 68%). Marcaba como malignos `TUMOR DE WARTHIN`, `QUERATOSIS SEBORREICA` y `AMELOBLASTOMA`, que son BENIGNOS. Sin la adjudicación por revisores habría "corregido" 942 valores y destrozado ~640 correctos.

### Calidad de las 9.889 filas nuevas de coloración
Igual o mejor que las anteriores: dx 100%, órgano 100%, malignidad 100%, género 100%, edad 99,6%, procedimiento 97,8% (vs 98,0% de las viejas).

## [6.9.69] - 2026-07-23 — Auditoría completa BD ↔ PDFs (13.355 filas · 82.167 valores)

Auditoría de veracidad de **toda** la BD contra los 765 PDFs: ¿cada dato transcrito está REALMENTE en su informe?

### Resultado
| | |
|---|--:|
| Valores revisados | **82.167** |
| Filas sin texto de respaldo | **0** |
| Descripciones macro/micro revisadas | 28.808 |
| Descripciones con discrepancia | **0** |
| **Nombres, cédula, edad, EPS, género, médico tratante** | **0 fallos — 100% verbatim** |

Las 2.051 "discrepancias" restantes NO son errores:
- **2.035 `Sede`** — campo DERIVADO (constante "HUV"), no transcrito: la etiqueta no existe en el PDF.
- **16 `Servicio`** — corrección deliberada del `validador_medico_servicio` (V5.3.8): el médico es cirujano oncólogo → el servicio se corrige a "UNIDAD DE ONCOLOGIA COEX" aunque el PDF diga otra cosa. Todas del mismo médico. **Decisión de negocio existente, no un bug** (revisable si se quiere priorizar el literal del PDF).

### Corregido: 4 géneros sobrescritos
El PDF decía `INDETERMINADO` / `AMBOS` / `TRANSGENERO` y la BD tenía `FEMENINO`/`MASCULINO`. Residuo de la versión antigua que **adivinaba el sexo por el nombre de pila** (listas `_NOM_FEM/_NOM_MASC`, eliminadas en V6.9.44). **El extractor actual ya respeta los cuatro** — verificado reprocesándolos. Corregidos en BD con backup (`backup_genero_20260723_064952.json`).

### Tres bugs del AUDITOR, no de los datos
La auditoría solo fue fiable tras arreglar el instrumento — cada versión daba un número plausible y falso:
1. **Trocear por nº de caso** partía el informe (el nº aparece en encabezado, tabla y pie) → 9.740 falsos "el apellido no está en el PDF".
2. **Quedarse con un solo bloque** por caso perdía media página: la página de `IHQ250001` menciona también `M2409633` (su coloración previa) y el corte se comía la DESCRIPCIÓN MICROSCÓPICA → 5.440 falsos positivos.
   **Solución:** segmentar por PÁGINA (`"CASO Copia|Final Pag. N de M"`), que es la unidad real del documento.
3. **Solo aceptar "Copia Pag"**: hay dos variantes de cabecera (`Copia` y `Final`) → 811 casos se quedaban sin texto.

Y un cuarto ajuste conceptual: las descripciones `… Coloracion` de un caso IHQ vienen del **informe M vinculado** (la app fusiona coloración + IHQ del mismo paciente), así que no están en el bloque del IHQ. Verificado: 31 de 40 aparecen literalmente en otro informe del corpus; las 9 restantes son estudios de 2024 cuyo PDF no está en la carpeta.

### Procesados los 198 PDFs que faltaban
Coloraciones 2025 (`M2500001`–`M2502xxx`) + sueltos pendientes: **198 PDFs, 9.256 filas nuevas, 0 errores, 42 s**. La reconciliación enlazó **724 pacientes** (869 IHQ actualizados con su coloración).

**Estado final: 765/765 PDFs procesados · BD 22.547 filas · 0 filas vacías.**

**Auditoría repetida sobre la BD completa:** 131.495 valores revisados, **48.499 descripciones con 0 discrepancias**. Los 9.256 casos nuevos **no añadieron ni un solo fallo** (siguen siendo los mismos 2.051: Sede derivada + 16 de la regla médico-servicio).

### Corregido: nombre con la cédula pegada (`name_splitter`)
`IHQ251481` era la única fila sin paciente. Causa: el informe trae `Nombre : 16856154 DIEGO PEREA OBONAGA` — la cédula delante del nombre. El número contaba como token y ocupaba el puesto del primer nombre, dejando la fila **sin nombre ni apellido**. `split_full_name` ahora descarta los tokens puramente numéricos (el nº de identificación tiene su propio campo). Verificado sin regresión en nombres de 2, 3 y 4 tokens.

## [6.9.68] - 2026-07-21 — Los "3 incompletos" eran falsa alarma… y destaparon un fallo grave

**Reporte del usuario:** importó 77 coloraciones → 74 completas, 3 incompletas ("falta Diagnostico Coloracion"). Quería saber por qué no el 100%.

### 1. Los 3 incompletos: FALSA ALARMA (el dato estaba)
Verificado contra el PDF y la BD: **los 77 tienen su diagnóstico**. M2604451 tenía `CARCINOMA PAPILAR DE TIROIDES ENCAPSULADO` correctamente extraído. El problema era **en qué columna**:

| Origen del PDF | Ruta | Columna |
|---|---|---|
| Lote `M 2604451 AL 2604500.pdf` | coloración | `Diagnostico Coloracion 2` |
| Un solo caso `M2604451.pdf` | general | `Diagnostico Principal` |

`_completitud_coloracion` exigía solo `Diagnostico Coloracion 2` → marcaba incompletos casos perfectamente extraídos. **El informe de importación mentía, no se perdió ningún dato.** Ahora acepta el dx en cualquiera de las columnas válidas.

Causa de fondo: `_is_coloracion_file` detecta coloración por el patrón `M … AL …` o por indicios en el texto; un PDF de **un solo caso** (`M2604451.pdf`) no encaja y se procesa por la ruta general. No se cambió el enrutado (afectaría a stats y al visor); se corrigió el validador, que era quien informaba mal.

### 2. 🔴 FALLO GRAVE encontrado de paso: filas fantasma marcadas como analizadas
Al revisar aparecieron **6 casos con la fila VACÍA** (todo `N/A`: sin nombre, sin órgano, sin dx) cuyos PDFs **sí tienen contenido** — `M2604476.pdf` trae paciente y un dVIN diagnosticado.

**El detector de V6.9.67 los daba por analizados** (la fila existe → cuenta), así que el PDF salía **en azul** y el usuario se lo saltaría → **informe perdido**. Es exactamente la dirección de error que el diseño quería evitar.

**Corregido:** existir la fila NO basta. Se exige **contenido real** (nombre, apellido o algún diagnóstico). Los 6 pasan a NUEVO y entran en «Seleccionar pendientes». En la BD hay 7 filas fantasma de este tipo.

### Estado real de la carpeta
Con los PDFs que añadió el usuario, ahora hay **765 archivos**: **271 analizados / 494 pendientes**, correctamente detectados.

## [6.9.67] - 2026-07-21 — El estado del PDF se lee del CONTENIDO, no del nombre

**Síntoma reportado:** el usuario procesó los PDFs naranjas, terminó bien… y siguieron naranjas.

**No era un fallo de refresco: el color mentía.** V6.9.66 daba por hecho que `IHQ260701 al IHQ260750.pdf` contenía 50 casos. Contiene **12**. Se calculaba 12/50 → "a medias" cuando estaba **completo**. El nombre es una **etiqueta de rango, no un inventario** — el patólogo agrupa lo que emitió esa semana.

### Ahora se lee el PDF
`casos_reales_del_pdf()` extrae del texto los casos que el archivo trae de verdad (PyMuPDF, capa nativa). Con dos correcciones que salieron al medir:

1. **Referencias cruzadas.** El texto nombra casos de OTROS informes (*"estudio ligado al reporte IHQ250486 y M2507467"*). Contarlos hacía parecer incompleto un PDF completo (`IHQ260701` daba 15/26). Se cruzan los casos del texto con los que al archivo le **corresponden por su nombre**: el texto dice qué hay, el nombre dice qué le toca.
2. **Umbral del 90% eliminado.** Existía para tolerar los huecos del rango inventado. Comparando contenido real, deben estar **todos**.

**Caché** por (tamaño, fecha) en `auditoria/casos_por_pdf.json`: 31 s la primera vez, **0,2 s** después. Se reconstruye sola si el PDF cambia.

**Resultado verificado en la app:** los 193 PDFs salen **COMPLETO**, que es la verdad — todo lo que hay está procesado. Los cuatro que el usuario reprocesó ahora muestran `(39/39)`, `(22/22)`, `(18/18)`, `(12/12)` en azul. El estado NUEVO se revalidó con casos inexistentes.

**Lección:** el detector daba un número plausible y equivocado. Solo se cazó porque el usuario reprocesó y el color no cambió — la BD (8.816 filas, sin cambios) confirmó que el procesamiento no tenía nada que añadir.

## [6.9.66] - 2026-07-21 — Ver de un vistazo qué PDFs ya están analizados

**Problema:** en «Archivos disponibles» se ven todos los PDFs de la carpeta, pero no cuáles ya se procesaron. Con cientos de archivos, la única forma de saberlo era seleccionarlos y lanzarlos.

### Cómo se sabe si un PDF ya está analizado
La BD **no guarda el archivo de origen** ni hay registro de procesados. Se deduce del NOMBRE (que codifica el rango de casos) y se consulta cuántos de esos casos están en la BD. `core/estado_pdfs.py` entiende los tres formatos reales:
- `IHQ DEL 001 AL 050.pdf` → IHQ250001…IHQ250050 (el año sale de la carpeta `2025/`)
- `IHQ260001 al IHQ260050.pdf` → IHQ260001…IHQ260050
- `M 2503754 AL 2503803.pdf` → M2503754…M2503803
- también PDFs de un solo caso (`IHQ251391.pdf`) y enumeraciones (`IHQ260782 y IHQ260795.pdf`)

⚠️ **`y` NO es lo mismo que `al`:** `"IHQ260782 y IHQ260795"` son DOS casos, no un rango de 14. Tratarlo como rango daba PARCIAL 2/14 en un PDF completo.

**Criterio prudente:** ante la duda **nunca** se marca como analizado. Marcar de más haría que el usuario se saltara un PDF sin procesar (pérdida de datos); marcar de menos solo cuesta un reproceso, que es inofensivo.

### En la UI
- **✓ azul** = ya analizado · **◐ naranja** = a medias · **● verde** = sin analizar, con el conteo `(47/58)` al lado, que dice de un vistazo por dónde se quedó.
- Leyenda de colores bajo la lista.
- **Botón «🎯 Seleccionar pendientes»**: marca solo lo que falta (sin analizar + a medias) y deja fuera lo ya hecho. Con 193 PDFs seleccionó los 7 pendientes y descartó 186 de un clic.

**Verificado en la app real** (no solo en tests): los 193 PDFs se clasifican en 186 COMPLETO / 7 PARCIAL / 0 sin interpretar. El estado NUEVO se validó con nombres sintéticos de casos inexistentes.

**Bug encontrado al probar en pantalla:** `_seleccionar_pendientes` llamaba a `self._log_message`, que no existe en `ui.py` → diálogo de error. Sustituido por un resumen visible (cuántos pendientes, cuántos quedaron fuera). Los tests de sintaxis no lo habrían detectado.

## [6.9.65] - 2026-07-17 — Reproceso completo en modo verificado + checkpoint reanudable

**Reproceso de los 2.077 casos** con la capa de polaridad IA (mistral-nemo), modo lote: 1 lente + `revisar_todos=ON`. **646 min, 0 errores.**

- **585 polaridades corregidas por la IA**, cada una con su **cita del informe**.
- **120** cambiaron un valor en la BD; las otras 465 ya coincidían con lo corregido en sesiones previas → la BD **converge** (224+428 de antes ya estaban bien).
- **Las 585 quedaron en la cola de revisión** (`auditoria/polaridad_revision.jsonl`), ninguna dada por buena en silencio. Exportadas a `cola_revision_polaridad.csv` (Excel) para el patólogo.
- BD íntegra tras el reproceso: 8.816 filas / 2.076 casos IHQ. Backup previo: `backup_COMPLETO_pre_lote_20260716_151245.json`. Evidencia: `evidencia_reproceso_20260717_174100.json`.

### Checkpoint reanudable (a raíz de un apagón)
Un corte de luz mató el primer intento a las 2,6 h (600/2.077). La BD quedó **intacta** (el script escribía solo al final), pero se perdió el cómputo. **Fallo de diseño corregido:** `reproceso_final.py` ahora anexa cada caso a `reproceso_ckpt.jsonl` al terminarlo; si se corta la luz se reanuda donde iba (se pierden segundos, no horas). Verificado en el relanzamiento.

### Por qué el lote usa 1 lente (no consenso)
Con `revisar_todos=ON` **todo** cambio va a la cola, así que el humano ve los dudosos igual. El consenso a 2 lentes duplicaría el tiempo (10h→23h) sin añadir cobertura en este modo. En **producción (PDFs nuevos)** el consenso sigue activo vía `config.ini`.

## [6.9.64] - 2026-07-16 — IA de diagnóstico: construida, medida y RECHAZADA (no se cablea)

Petición: arreglar el dx multi-espécimen con IA + cita, igual que se hizo con la polaridad.

### Primero: establecer la VERDAD (y menos mal)
Antes de construir nada se adjudicaron **a ciegas** los 49 casos discordantes contra el informe (los revisores no sabían qué opción venía de la BD y cuál del extractor):

| | |
|---|--:|
| Tiene razón la **BD** → el extractor falla | 26 |
| **Tiene razón el EXTRACTOR → la BD está MAL** | **18** |
| Ninguna de las dos (informes ligados, sin sección DIAGNÓSTICO) | 5 |

**Dos correcciones a lo dicho antes:**
- El extractor falla en **31/2.077 = 1,5%**, no 2,4%.
- **"La BD es mejor que un reproceso" era FALSO para el dx: tiene 18 diagnósticos malos.** Si se hubiera construido la IA para imitar la BD, se habrían copiado esos 18 errores.

**Trampa descubierta:** la regla intuitiva *"en multi-espécimen quédate con el maligno"* **es falsa**. Si el estudio es de ganglios y dice "sin evidencia de tumor", ESE es el dx — el cáncer que aparece es el antecedente del paciente (`Historia de carcinoma ductal`), no un hallazgo de la muestra.

### `core/extractors/dx_principal_ia.py` — ⛔ NO CABLEADO
Diseño correcto y **la guarda funciona**: la IA **selecciona** (no redacta) y se verifica que el dx esté **literal** en el informe. Probado: acepta `CARCINOMA INVASIVO DE TIPO NO ESPECIAL DUCTAL` (literal), rechaza `CARCINOMA DUCTAL INFILTRANTE DE MAMA` (redactado) y `ADENOCARCINOMA DE PROSTATA` (inventado). **Una alucinación no puede sobrevivir por construcción.**

**Pero el resultado no da:**

| Sobre 44 casos con verdad establecida | |
|---|--:|
| Opina | 27 |
| **Acierta** | 20 (**74%**) |
| Falla | 7 |
| Se abstiene | 17 |
| Mejora | 6 |
| **ROMPE casos que el regex ya resolvía** | **5** |

74% es insuficiente para el campo más crítico y romper 5 dx correctos es inaceptable. **No se conecta.** El módulo queda documentado con el banco de pruebas listo (`dx_verdad.json` + `test_dx_ia.py`) para re-medir si mejora el hardware.

### La lección, medida TRES veces el mismo día
Reforzar el prompt **no mejora el juicio** de este modelo:
1. Polaridad, regla de población no tumoral → cobertura 46→26 (peor).
2. Dx, regla del ganglio corregida → **no movió los casos clave**.
3. Rótulo por reglas → 92 regresiones → revertido.

**El techo no está en el diseño: está en mistral-nemo 12B Q3**, lo máximo que entra en una RTX 3050 de 8 GB. Q3 es donde la calidad degrada. **Vía real: GPU con más VRAM.**

### Estado del dx
Se queda el extractor determinista (V6.9.53). Falla **1,5%** (31/2.077). Los **18 dx malos de la BD** tienen su verdad establecida en `dx_verdad.json` y se pueden corregir.

## [6.9.63] - 2026-07-16 — Modo 100% verificado: consenso + auditoría con cita + cola de revisión

**Objetivo pedido:** *"que extraiga de manera perfecta al 100%, a prueba de errores y con auditorías completas"*.

### La verdad medida: el 100% AUTOMÁTICO no existe con este hardware
Cinco enfoques probados hoy sobre el mismo banco de casos difíciles (adjudicados a ciegas contra el informe):

| Enfoque | Acierto |
|---|--:|
| Regex | 40% |
| Parser de cláusulas | 60% |
| IA local, una lente | 82% |
| IA local + guardas de cita/población | 88% |
| IA local + consenso a 2 lentes | **aún 22% de datos FALSOS** |

La medición decisiva: sobre 90 casos difíciles, el consenso redujo los errores de 45 a 20 — pero **escribió 20 datos falsos (22%)** aun declarando "confianza ALTA". **La seguridad que declara el modelo local NO es un aval válido para dato clínico.**

Causa: los 652 valores correctos de la BD no los produjo el extractor, sino someter cada cambio a **revisores de nivel Claude**. Dentro de la app corre mistral-nemo 12B en **cuantización Q3** (lo máximo que entra en una RTX 3050 de 8 GB), donde la calidad ya degrada.

### Cómo SÍ se llega al 100%: automatizar + confirmar
**Regla:** si la IA quiere CAMBIAR una polaridad, un humano lo confirma. Siempre — no solo cuando duda, porque su "seguridad" no es fiable.

1. **Consenso a 2 lentes** (`_PROMPT` + `_PROMPT_LENTE_B`): la misma IA con dos encuadres. A temperatura 0 hay que cambiar el *prompt*, no la semilla. El **desacuerdo es la señal de "no sé"**.
2. **El valor se escribe** (la IA acierta 82% vs 40% del regex) **pero nunca en silencio**.
3. **Auditoría completa** — `auditoria/polaridad_auditoria.jsonl`, cada dato con la cita literal del informe:
   `IHQ251114 IHQ_WT1: POSITIVO -> NEGATIVO «No presentan marcación para WT1»`
   Permite verificar cualquier valor contra el PDF **sin reprocesar**.
4. **Cola de revisión** — `auditoria/polaridad_revision.jsonl`, con dos clases:
   - `CAMBIO_APLICADO_PENDIENTE_DE_CONFIRMAR` → la IA lo cambió; confírmalo.
   - `LENTES_DISCREPAN_NO_SE_TOCO` → la IA no supo; el valor sigue intacto.
5. **Herramienta:** `herramientas_ia/cola_revision.py` (`--revision`, `--auditoria`, `--caso IHQ…`, `--csv` para Excel).

**Volumen:** ~522 marcadores sobre 2.077 casos (25%), con la cita al lado.

### Flags nuevos — `config.ini [llm]`
- `usar_consenso_polaridad = true` — doble lente (2 llamadas al LLM por lote, ~2x tiempo).
- `revisar_todos_los_cambios = true` — modo 100%: encola TODO cambio. En `false` solo los dudosos (cola más corta, pero **no es 100%**).

### Notas de implementación
- La auditoría viaja en `__AUDIT_POLARIDAD__` y se **extrae antes** de mapear a BD: nunca llega a la tabla.
- El nº de caso se toma de `numero_peticion` (`Numero de caso` aún no existe en ese punto — sin esto la auditoría salía con caso `"?"` y no servía para rastrear).
- Fallo de auditoría **nunca** rompe la extracción.

### 🔬 Modelo alternativo: PROBADO Y RECHAZADO
Hipótesis: mistral-nemo está en **Q3_K_L (3,4 bits/parámetro)**; un modelo más nuevo a **Q4_K_M (4,8 bits)** con la misma VRAM debería ganar. **Se descargó Qwen3.5-9B Q4_K_M y se midió sobre el mismo banco de dx. FALSA:**

| | mistral-nemo 12B Q3 | Qwen3.5-9B Q4 |
|---|--:|--:|
| opina | 27/44 | **12/44** |
| acierta | 20 (74%) | 8 (**67%**) |
| MEJORA / ROMPE | 6 / 5 | 4 / **2** |
| tiempo | ~20 s/caso | **115 s/caso** |

**Causa (importante para elegir modelo aquí):** Qwen3.5 es un modelo de **RAZONAMIENTO**, y eso lo hace PEOR para esta tarea. Al razonar **reformula** el texto en vez de copiarlo → su respuesta no coincide literal con el informe → **la guarda de cita la rechaza**. Se abstiene en el **73%** de los casos. Además, con `max_tokens` bajo se queda sin presupuesto pensando y devuelve `content` vacío (`finish_reason='length'`): parece roto y no lo está.

⚠️ **Regla:** para este proyecto NO usar modelos de razonamiento. La tarea exige copia literal verificable; razonar es lo contrario.
⚠️ **Trampa:** Qwen3.5 acertó en la prueba de humo el caso multi-espécimen que mistral falla, y parecía la solución. En el banco completo fue peor. **Un caso no es una medición.**

Se restauró mistral-nemo. **Sigue SIN probarse** un modelo más grande (27B+ a Q4) en una GPU de 24 GB: la hipótesis "mejor cuantización con la misma VRAM" se midió y falló, así que **no se puede prometer que una GPU nueva lo arregle**.

## [6.9.62] - 2026-07-16 — El fix de Órgano NUNCA estuvo conectado al extractor

**Bug grave detectado al verificar (no al programar).** Antes de responder "¿puedo reprocesar?" se comparó lo que produce el extractor contra la BD. Resultado: **el reproceso cambiaría el Órgano en 1.183 casos** — y a peor:

| BD actual (normalizada) | Lo que producía el extractor |
|---|---|
| `PULMON` | `BX DE PLEURA + BX DE PULMON` |
| `MAMA` | `BX LESION MAMA IZQUIERDA` |
| `CERVIX` | `BX EXOCERVIX` |
| `ESTOMAGO` | `BX LESION GASTRICA` |

**Causa raíz:** `normalizar_organo` existe desde V6.9.54 y se usó para corregir los ~2.075 casos históricos en BD… pero **nunca se conectó a `map_to_database_format`**, que es lo que ESCRIBE en la tabla:
```python
organo_db = extracted_data.get('organo', '') or extracted_data.get('ihq_organo', '')
db_record["Organo"] = organo_db      # ← crudo, sin normalizar
```
Se arregló el dato histórico y se dio el bug por cerrado, pero **seguía vivo para cada PDF nuevo**: era exactamente el fallo original que reportó el usuario (`Organo = "TIROIDECTOMIA TOTAL"`). La función solo se invocaba desde `enhanced_database_dashboard.py` e `informe_estadistico.py`, es decir, al MOSTRAR — no al guardar.

**Fix:** llamar a `normalizar_organo` en `map_to_database_format`. Es conservadora: si el valor no trae procedimiento, lo devuelve tal cual.

### 🔴 BUG ABIERTO (NO resuelto): el dx se pierde en informes MULTI-ESPÉCIMEN — ~49 casos
Detectado en la misma verificación. **Es el bug más grave que queda y afecta también a PDFs nuevos.**

**Síntoma:** el extractor devuelve basura o el espécimen equivocado donde hay un cáncer:
| El informe dice | El extractor produce |
|---|---|
| `CARCINOMA INVASIVO DE TIPO NO ESPECIAL DUCTAL…` | `INMUNOHISTOQUÍMICA` |
| `LINFOMA T/NK DE ALTO GRADO` | `INMUNOHISTOQUÍMICA` |
| `SARCOMA HISTIOCITICO` | `N/A` |
| A: *NEGATIVO PARA MALIGNIDAD* · **B: ADENOCARCINOMA (GLEASON 3+3)** | `NEGATIVO PARA MALIGNIDAD` (¡el espécimen benigno!) |

**Causa raíz (localizada):** en `_det_seccion_diagnostico`,
```python
ims = list(_DET_PROC_SKIP.finditer(cuerpo))
zona = cuerpo[ims[-1].end():] if ims else cuerpo   # ← la ÚLTIMA coincidencia
```
Para saltar el rótulo del espécimen se toma el texto tras la **última** mención de procedimiento. En informes multi-espécimen el rótulo del espécimen B (`"B. … Resección."`) aparece **después** del diagnóstico del A → la zona arranca pasado el cáncer y se pierde.

**Intento de fix REVERTIDO.** Se probó saltar solo los rótulos anteriores al primer término dx fuerte. Medido sobre los 2.077: **92 REGRESIONES** — devolvía el rótulo como diagnóstico (`LESIÓN. BIOPSIA. ESTUDIO DE INMUNOHISTOQUÍMICA` pisando `INFLAMACIÓN CRÓNICA GRANULOMATOSA`), porque `_DET_FUERTE` matchea la palabra **"Tumor" que está dentro del propio rótulo**. Revertido según la regla anti-regresión. **Verificado tras revertir: 2.077 sin cambio, 0 regresiones.**

**Qué hace falta:** distinguir rótulo de diagnóstico sin depender de `_DET_FUERTE`, y en multi-espécimen elegir el diagnóstico **maligno** (el clínicamente principal), no el primero. Requiere sesión dedicada + harness (`dx_regres.py`, 2.077 casos en ~140 s con la IA de polaridad desactivada).

**Impacto mientras tanto:** ~49/2.077 = **2,4%**. La BD tiene los valores CORRECTOS (no tocar). Los PDFs nuevos con esta estructura pueden salir con dx erróneo → **revisar el dx de los casos multi-espécimen al procesarlos**.

### Validación del fix de Órgano
**2.070 de 2.071** coinciden con los valores ya validados en BD.
- Se probó además partir los multi-espécimen por `+`: **mucho peor** (119 → 29 coincidencias). Descartado: la mayoría de multi-espécimen no traen procedimiento (`PARED ABDOMINAL + OMENTO`) y deben quedar intactos.
- ⚠️ **Limitación conocida (1 caso):** `HISTERECTOMÍA + SALPINGECTOMÍA + GANGLIOS PARAÓRTICOS + OMENTO` → `GANGLIO`. La regla órgano-primero toma el sustantivo de un espécimen posterior. Es una cirugía de estadificación multi-órgano donde no hay un órgano único correcto. 0,05%.

## [6.9.61] - 2026-07-14 — Polaridad de biomarcadores con IA local + guarda de cita

**Sprint:** La polaridad (POSITIVO/NEGATIVO) de los biomarcadores era el punto más débil del extractor. No era un problema de OCR — se midió: **14.633/14.633 páginas (100%) se leen de la capa de texto nativa del PDF, 0% pasa por tesseract**. El texto se lee exacto; lo que fallaba era **interpretarlo**.

### El fallo, medido contra el informe por revisores independientes
| Zona | Valores | Error del regex |
|---|--:|--:|
| Donde regex y un parser de cláusulas **discrepan** | 755 | **~60%** |
| Donde **coinciden** (coinciden porque se equivocan igual) | 1.947 | **~17%** |
| **Total polaridades** | ~2.700 | **~29% mal** |

Acertar exige **comprender la frase**, no reconocer un patrón:
- *"**sin pérdida de expresión** de CD2 y CD7"* → CD7 es **POSITIVO** (la frase contiene "pérdida")
- *"El CD34 **resalta los vasos** … **sin marcación dentro de la lesión**"* → **NEGATIVO** (contiene "resalta")
- *"positividad para PSA … **con negatividad para** CK7, CK20"* → cruce de polaridad en una frase
- el mismo marcador con dos polaridades según el compartimento (tumor vs epitelio benigno)

Tres intentos por reglas fracasaron: el regex original (40% de acierto), una guarda de polaridad (destruyó 251 valores válidos → revertida) y un parser de cláusulas afinado (60%).

### Solución: `core/extractors/biomarcador_polaridad_ia.py`
IA **LOCAL** (LM Studio/Ollama) que clasifica POSITIVO / NEGATIVO / NO_DICE. **100% de acierto sobre lo que afirma** (60 casos adjudicados: el subconjunto más ambiguo del corpus).

Lo que la hace segura —a diferencia de la IA de diagnóstico, que se desactivó por alucinar—:
1. **Clasificación cerrada**: no genera texto libre, elige entre tres valores.
2. **Vocabulario cerrado**: solo opina sobre marcadores que el informe nombra.
3. **Guarda de cita**: debe devolver el fragmento del informe que la sustenta; se verifica que esté **literal** en el texto y que **exprese un resultado** (la frase del panel solicitado no vale). Si no pasa → se descarta y **se conserva el valor del regex**.
4. **Solo corrige**: nunca crea biomarcadores nuevos.
5. **Endpoint obligatoriamente local** (Ley 1581 / Habeas Data): si la URL no es localhost, **se rehúsa la llamada**.

Sin LLM disponible, el extractor se comporta exactamente como antes. Se apaga con `usar_ia_polaridad = false` en `config.ini [llm]`.

### Corrección de la BD
**224 polaridades corregidas** (97 cambiaron valor; el resto ya estaba bien), cada una con la cita del informe como evidencia. Ruta de cada corrección: IA la propone → la guarda verifica la cita contra el PDF → **46 revisores independientes** intentan refutarla. **226/236 sobrevivieron (95,8%)**; el desempate a dos lentes **descartó 8 propuestas erróneas de la IA** que habrían corrompido la BD.

Backup: `backups/backup_polaridad_ia_20260714_111535.json` · Evidencia: `backups/evidencia_polaridad_ia_20260714_111535.json`

### Segunda guarda: POSITIVO de una población que NO es el tumor
La verificación adversarial cazó 8 errores de la IA; **6 tenían la misma causa**: el marcador tiñe algo que no es el tumor y la IA lo daba por positivo *del* tumor.
- *"Positividad en las **paredes vasculares** para CD34"* → CD34 es NEGATIVO en el tumor
- *"positividad **estromal** difusa para S100"* → S100 NEGATIVO en el tumor
- *"p40 positivo en los **queratinocitos basales**"* → p40 NEGATIVO en el tumor

Se intentó arreglar **reforzando el prompt** y salió mal: el modelo se volvió tan cauto que la cobertura cayó de 46 a 26 sobre 60 (y solo arregló 1 de 8) → **peor en neto**, porque lo que abandona vuelve al regex (40% de acierto). Un modelo al que le insistes en tener cuidado no se vuelve más listo, se vuelve más callado.

**Se resolvió en CÓDIGO** (`_positivo_de_otra_poblacion`): se rechaza el POSITIVO cuya cita atribuye la marcación a vasos/estroma/basales sin mencionar el tumor. Determinista y verificable.

⚠️ **`linfocitos` queda FUERA de la guarda a propósito**, aunque 2 de los 8 fallos eran de linfocitos: en un LINFOMA el tumor **son** los linfocitos, y rechazar *"linfocitos B positivos para CD20"* destruiría positivos legítimos. Mejor cazar 3 de 8 con seguridad que 5 de 8 rompiendo los linfomas.

### Precisión: la cifra honesta
Sobre los 60 casos adjudicados (el subconjunto **más ambiguo** del corpus, por construcción): **96–100% de acierto sobre lo que afirma**, frente al **40% del regex**. No es un 100% sostenible: el modelo tiene variabilidad entre corridas aun a temperatura 0.

**Consecuencia operativa:** como un ~4% de las correcciones puede fallar, los cambios **no se escriben a ciegas** en la BD. El procedimiento es: extractor → verificación adversarial de los cambios propuestos → aplicar solo los confirmados. Fue así como se descartaron 8 propuestas erróneas de las 236.

### Reproceso completo de los 2.077 casos (2026-07-16)
Reprocesados los 2.077 IHQ con el extractor V6.9.61: **555 min, 0 errores** → **522 polaridades a cambiar** (POS→NEG 351, NEG→POS 171: el regex sobre-declaraba positivos, como predecía el diagnóstico).

**Las 522 se verificaron una a una** (no una muestra) con adjudicación **ciega** contra el informe — los revisores no sabían qué proponía la máquina:

| | |
|---|--:|
| Confirmadas en 1ª pasada (revisión ciega) | 415 |
| Confirmadas en desempate a 2 lentes | 13 |
| **Aplicadas en BD** | **428** |
| **Rechazadas** (el revisor defiende el valor actual) | **94** |

**Verificado en BD: 428/428 escritas correctamente.**
Backup: `backups/backup_reproceso_20260716_065005.json` · Evidencia: `backups/evidencia_reproceso_20260716_065005.json`

Las **94 rechazadas son el valor de este paso**: sin la verificación se habrían escrito 94 valores erróneos. Patrón dominante en los rechazos — LAMBDA, KAPPA, PAX5, CD20, CD10 en **linfomas**: la IA quería pasarlos a NEGATIVO y los revisores confirmaron que el POSITIVO de la BD era el correcto. Coincide con la decisión de dejar `linfocitos` fuera de la guarda de población no tumoral.

⚠️ **Limitación conocida:** parte del desempate no pudo ejecutarse (límite de sesión). Eso **no compromete lo aplicado** (las 428 salen de la 1ª pasada completa, 522/522), pero deja algunas de las 94 sin dictamen definitivo — se conservó el valor actual, que es el comportamiento seguro. Revisables más adelante.

### Columnas siempre en N/A: auditado, NO es un bug
El reproceso avisó de 10 columnas que difieren en los 2.076 casos (`IHQ_PDL-1`, `IHQ_EBER`, `IHQ_CK56`…). Se auditó por si eran datos perdidos. **No lo son:**

1. **Cero columnas huérfanas** — el extractor nunca emite un valor a una columna inexistente (148 columnas `IHQ_` en la tabla, 129 que llena, 0 huérfanas). No se pierde ningún dato.
2. Las 19 columnas muertas son **duplicados del esquema**: `IHQ_CK56`→`IHQ_CK5_6`, `IHQ_DESMINA`→`IHQ_DESMIN`, `IHQ_LCA`→`IHQ_CD45`, `IHQ_34BETA`/`IHQ_CK34BE12`/`IHQ_CK34BETA12`→`IHQ_CK34BETAE12`… El dato va a la canónica. La UI ya las oculta desde V6.9.57.
3. **PD-L1 y EBER están vacíos porque en este corpus solo se PIDEN, nunca se reportan.** Verificadas las 31 menciones (18 PD-L1 + 13 EBER): **100% son recomendaciones** (*"Requiere estudio de inmunohistoquímica para la proteína PDL1 (22C3)"*, *"Se recomienda complementar estudios con FISH para EBER"*). **Cero traen resultado.** El extractor acierta al no capturarlos: hacerlo sería inventar un resultado que el patólogo nunca dio.

La diferencia que disparó el aviso (`''` del extractor vs `'N/A'` de la BD) es **cosmética**: ambos significan "sin dato". No se tocó nada.

⚠️ **Corrección a la cifra de "773 biomarcadores perdidos"** de la auditoría previa: cuenta menciones sin distinguir petición de resultado, así que está **inflada** por este mismo efecto. Antes de "recuperar" nada, hay que filtrar las menciones de panel solicitado/recomendación.

### Otros arreglos
- `_cita_respaldada`: probaba solo la **primera** ocurrencia de la frase ancla y abandonaba → rechazaba citas válidas (era el 25% de los rechazos).
- Alias de nombres: la IA responde `CKAE1E3`/`IDH` donde la columna es `CKAE1AE3`/`IDH1`.
- JSON truncado por `max_tokens` → se rescatan los objetos completos + troceo en lotes de 8 marcadores (mejora la calidad de la respuesta).
- `import os` faltaba en el módulo → el `except` del extractor lo silenciaba y la capa **no corría** (el resultado parecía bien porque el regex acertaba por casualidad). Detectado por el cronómetro: 1 s en vez de 20 s.

## [6.9.58] - 2026-07-14 — Ficha del Paciente (agrupa IHQ + Coloraciones)

**Sprint:** Un paciente puede tener varios estudios (hasta **9**: IHQ + coloraciones) y en la tabla plana quedaban dispersos. La **Ficha del Paciente** los agrupa en la VISTA — **sin tocar el DATO**: cada estudio sigue siendo su propia fila (fuente de verdad, sin duplicar).

### Datos que motivaron el cambio
| | |
|---|--:|
| Pacientes únicos | 7.521 |
| Solo IHQ / Solo Coloración | 1.278 / 5.690 |
| **IHQ + Coloración** (los que hay que agrupar) | **553** |
| Pacientes con **más de 1 IHQ** | **210** |
| Pacientes con el **mismo dx de coloración DUPLICADO** en varias filas IHQ | **91** ⚠️ |

Los 91 duplicados son el síntoma del modelo actual: `reconciliar_coloraciones` pega el dx de la coloración en "la fila IHQ" del paciente, pero **asume 1 IHQ por paciente**. Con 5 IHQ (médula, ganglio…, fechas distintas) los 5 reciben el MISMO texto de coloración.

### Added
- **Ficha del Paciente (`_mostrar_ficha_paciente` / `_render_ficha` en `ui.py`)** — doble clic en cualquier fila del Visualizador abre la ficha del PACIENTE (por cédula) con **todos sus estudios en orden cronológico**, cada uno en su propia sección: tipo (🔬 IHQ / 🎨 Coloración), código, fecha, órgano, procedimiento, malignidad, diagnóstico, biomarcadores solicitados y resultados, y descripciones. Marca cuál era el registro que abriste. Botón "Copiar ficha".
  - El **diagnóstico se lee del campo correcto según el tipo**: coloración → `Diagnostico Coloracion 2`; IHQ → `Diagnostico Principal`. En la sección IHQ **NO** se repite el texto concatenado de las coloraciones (ya aparecen como secciones propias) → se elimina el duplicado visual.
  - Reutiliza el doble clic ya existente (`_abrir_detalle_fila`); si el registro no tiene cédula fiable, cae al detalle de registro de siempre.

## [6.9.57] - 2026-07-09 — Visualizador: encabezados claros + adiós al mar de "N/A"

**Sprint:** Correcciones de usabilidad en el Visualizador de Datos (aplican a AMBAS vistas: tabla tksheet de `ui.py` y visor Qt, vía la fuente única `core/columnas_visor.py`).

### Added (V6.9.57)
- **`filas_para_display(df)`** — las celdas SIN DATO se muestran **VACÍAS** en vez de "N/A". Ocultar la *columna* solo sirve cuando NINGÚN paciente de la vista tiene ese biomarcador; en la vista completa la columna se queda y el resto de celdas quedaba lleno de "N/A". Ahora se limpia la **celda**.
  - Efecto: **237.419 celdas "N/A" → en blanco**. La tabla pasa a **91,2 % de celdas vacías / 8,8 % con dato real** → solo salta a la vista lo que existe.
  - **`NO MENCIONADO` SÍ se conserva** (911 celdas): significa que el biomarcador se SOLICITÓ pero no aparece en el informe → es un dato real (señal de calidad), no un "no aplica".
  - Solo afecta al DISPLAY: la BD, la búsqueda, el ordenamiento y la exportación conservan su valor.
  - Rendimiento: comparación EXACTA (`isin`) en vez de normalizar 1,2 M de celdas → **0,70 s → 0,21 s** (columnas + celdas).

### Fixed
- **Encabezados de macro/micro se cortaban** → no se distinguía cuál era la del IHQ y cuál la de la Coloración. Se acortaron y el ORIGEN va primero: `Descripcion Macroscopica Coloracion` (35 chars, se cortaba a 350 px) → **`COLORACIÓN · Macroscópica`** (25 chars). Igual para las 4 columnas (`IHQ · Macroscópica`, `IHQ · Microscópica`, `COLORACIÓN · Macroscópica`, `COLORACIÓN · Microscópica`).

### Added
- **`columnas_visibles(df, cols)`** — el Visualizador ahora muestra **solo las columnas que APLICAN**. Con ~130 columnas de biomarcadores la tabla era un mar de "N/A" inútiles. Una columna se OCULTA cuando NINGUNA fila mostrada tiene un valor real; en cuanto un paciente sí tiene ese biomarcador, la columna reaparece sola. Las columnas de identidad del caso (`COLS_SIEMPRE`: Numero de caso, Nombre, Procedimiento, Organo, Malignidad, Diagnostico Principal…) nunca se ocultan.
  - Efecto medido: **un solo caso pasa de 141 → 11 columnas** (130 N/A ocultas). BD completa (8.816 filas): 141 → 136. Costo: 0,28 s.
  - Se recalcula automáticamente al buscar/filtrar (el filtro re-puebla la tabla).

## [6.9.54] - 2026-07-09 — Normalización de Órgano (procedimiento→órgano)

**Sprint:** El campo `Organo` (columna "Organo" de la tabla "Estudios solicitados") a veces traía el **procedimiento/cirugía** ("Tiroidectomía total", "Biopsia de mama derecha", "Hemicolectomía") en vez del órgano. Nueva función `normalizar_organo()` que deriva el órgano de forma **verídica** (sin re-OCR — el órgano es derivable del propio valor).

### Impact
| Aspecto | Antes | Ahora (V6.9.54) |
|---|---|---|
| Casos con procedimiento en `Organo` | 2.094 | corregidos **2.075** (backup) |
| Falsos-mapeos (verificación programática) | — | **0** (los 4 "sospechosos" eran correctos: typos/abreviaturas) |
| Residuales sin resolver (typos OCR de procedimiento) | — | **27** (MASECTOMIA, GASTECTOMIA… — OCR corrupto) |

### Root cause / fix
- **`normalizar_organo()`** (`core/extractors/medical_extractor.py`): (1) ÓRGANO-PRIMERO — si el texto nombra un órgano (tiroidea/mamaria/hueso…) ese gana al procedimiento (evita `ISTMOLOBECTOMIA TIROIDEA → PULMON` y `COLECISTECTOMIA → VEJIGA`); (2) mapa procedimiento→órgano (`TIROIDECTOMIA → TIROIDES`, `MASTECTOMIA → MAMA`, `HEMICOLECTOMIA → COLON`…); (3) limpia prefijo (BIOPSIA/BX/PRODUCTO/PIEZA) y lateralidad; CBC/CEC + zonas faciales → PIEL.
- Conectado en `normalize_organ_name` (IHQ) y `coloracion_extractor.extraer_organo` (estudios M) → PDFs futuros salen correctos.

### Data
- BD MySQL `informes_ihq`: **2.075 valores de `Organo`** normalizados (backup `backups/backup_organo_*.json`). Solo se tocó el campo `Organo`.

## [6.9.53] - 2026-07-09 — Extractor de Diagnóstico Determinista (fix causa raíz + validación anti-regresión 2076 casos)

**Sprint:** Revalidación exhaustiva de la calidad del diagnóstico principal de los 2.076 casos IHQ (auditoría caso-por-caso contra el PDF real) y corrección de raíz del extractor de diagnóstico. Se identificaron **132 diagnósticos erróneos (6,4%)** y se corrigieron las 6 causas raíz mediante un **extractor determinista** (sin IA, que alucinaba) que lee la sección DIAGNÓSTICO real del informe. **Verificado con banco anti-regresión sobre los 2.076 casos (reproceso fiel sin re-OCR) + doble verificación adversarial de veracidad (31 agentes contrastando cada dx cambiado contra el PDF).**

### Impact
| Aspecto | Antes | Ahora (V6.9.53) |
|---|---|---|
| Diagnósticos "malos" (encabezado/basura/truncado/preámbulo) | 246 | **88** (−158) |
| Diagnósticos inventados (texto no presente en el PDF) | 6 | **0** (verificación adversarial) |
| Inversiones de negación (negativo→positivo, peligroso) | varias | **0** |
| Fidelidad de los cambios (verificada contra PDF) | — | **220/226 (97,3%)** fieles o aceptables |
| Regresiones sobre casos correctos | — | **0** |
| Diagnósticos corregidos en BD MySQL producción | — | **191 + 6 auditados + 1 malignidad** |

### Root causes fixed (extract_diagnostico_principal + fallback determinista)
- **Encabezado como dx** ("ESTUDIO DE INMUNOHISTOQUÍMICA") → fallback determinista lee la sección DIAGNÓSTICO real (recupera NEUROFIBROMA, CARCINOSARCOMA, HEMANGIOBLASTOMA, SIALOADENITIS…).
- **Truncado** — se eliminó 'IN SITU' de `keywords_estudio_m` (recupera CARCINOMA DUCTAL **IN SITU**); captura a través del salto de línea (OCR envuelve el dx).
- **Prefijo perdido** — `[A-ZÁÉÍÓÚÑ]*SARCOMA`/`*CARCINOMA` (OSTEO/LIPO/ANGIOSARCOMA ya no caen a "SARCOMA").
- **Inversión de negación** (crítico) — extracción negación-aware: "NEGATIVO PARA SARCOMA DE KAPOSI" ya no se reporta como "SARCOMA DE KAPOSI".
- **Sección equivocada** — selección por posición + campo sinóptico "Tipo histológico:" (espécimen A) + guardas contra referencias a otros bloques/preliminares.
- **Dx diferido** — devuelve "VER DESCRIPCIÓN MICROSCÓPICA Y COMENTARIO" honesto (no inventa).

### Files modified
- `core/unified_extractor.py` — NUEVO extractor determinista `_dx_determinista()` (+ helpers `_det_buscar_sinoptico`, `_det_buscar_en_zona`, `_det_seccion_diagnostico`, `_dp_sospechoso`, `_det_trim`, `_det_cand_valido`). Corre ANTES de la capa IA (desactivada por alucinar) => 100% determinista y verídico. Parte A: fix 'IN SITU' + prefijo en ESTRATEGIA 4/5. Guardas V6.9.53: respetar el diferido honesto contra el override de la capa Coloración y de la descripción microscópica (que inventaban dx).

### Fixed
- **Capa Coloración / descripción microscópica pisaban "VER COMENTARIO":** el post-proceso V6.9.37/41 sustituía el diferido honesto del extractor por el dx de un estudio de coloración distinto o por una descripción microscópica → afirmaba diagnósticos NO presentes en el informe IHQ. Ahora se respeta el diferido.

### Data
- BD MySQL `huv_oncologia` (tabla `informes_ihq`): **191 diagnósticos + 6 correcciones auditadas** actualizados (backup `backups/backup_dx_extractor_*.json`). Actualización quirúrgica de SOLO `Diagnostico Principal` + `Malignidad` (no toca nombres/biomarcadores).

## [6.9.48] - 2026-06-26 — Coloraciones Básicas (estudios M) + Reconciliación por Cédula + Performance Visualizador

**Sprint:** Incorporación de un pipeline AUTÓNOMO para los PDFs de "Coloraciones básicas" (estudios `M…`, tinciones tipo H&E) que conviven con el flujo IHQ sin contaminarlo, más reconciliación coloración↔IHQ por cédula independiente del orden de importación, optimizaciones de rendimiento del Visualizador y dos fixes de extracción/división de nombres. El sprint cubre cuatro versiones consecutivas (V6.9.45 → V6.9.48). **Verificado en producción contra la BD MySQL `huv_oncologia` (tabla `informes_ihq`): la tabla pasó de 2.076 a 8.816 filas** tras la carga inicial de coloraciones.

### Impact
| Aspecto | Antes (V6.9.5) | Ahora (V6.9.48) |
|---|---|---|
| Tipos de PDF soportados | Solo IHQ | **IHQ + Coloraciones básicas (M…)** |
| Filas en `informes_ihq` | 2.076 | **8.816** (139 PDFs de coloración → 6.806 coloraciones) |
| Diagnóstico de coloración | No capturado | **Columna `Diagnostico Coloracion 2` (TEXT)** |
| Reconciliación coloración↔IHQ | — | **`reconciliar_coloraciones()` idempotente, independiente del orden** |
| Filas M en estadísticas/dashboard/KPIs | — | **Excluidas (filtro `^[Mm]\d`)** |
| Filas M en Visualizador | — | **Visibles y buscables por cédula/nombre** |
| `_apply_row_colors` (coloreado tabla) | ~13.300 ms (freeze ~13 s al abrir) | **~280 ms** |
| Auto-refresh 60 s | Recarga completa siempre (freeze ~1 s/min) | **Huella barata `get_db_fingerprint()`, se salta si no cambió** |

### Files modified
- `core/extractors/coloracion_extractor.py` (NUEVO) — Extractor dedicado para PDFs de coloraciones (estudios M autónomos). Extrae SOLO el diagnóstico. V6.9.48 FIX M2506212: `_RE_NOMBRE` con salto de línea OPCIONAL antes de "N. peticion".
- `core/coloracion_processor.py` (NUEVO) — Procesador AISLADO del IHQ. Cada coloración se guarda como su propia fila `M######` (fuente de verdad, nunca se pisa ni se pierde).
- `core/database_manager.py` — Nueva columna `Diagnostico Coloracion 2` (TEXT) en schema y mapeo (líneas ~176, ~249, ~896). Nueva función `get_db_fingerprint()` (COUNT+MAX) para detección barata de cambios (V6.9.47).
- `ui.py` — Router `_is_coloracion_file()`/`_process_coloracion_file()` en "Procesar seleccionados" detecta PDFs "M … AL …" y los enruta sin tocar el flujo IHQ (V6.9.45). `reconciliar_coloraciones()` invocada tras cada importación (V6.9.46). Ocultamiento en DISPLAY de filas M redundantes (single-merged) sin borrarlas de BD (V6.9.46). `_apply_row_colors` vectorizado (V6.9.47). Auto-refresh con `get_db_fingerprint()` (V6.9.47). Exclusión de filas M en KPIs y Dashboard analítico (V6.9.45).
- `core/informe_estadistico.py` — El informe estadístico es SOLO de IHQ → excluye filas de coloración (V6.9.45).
- `core/utils/name_splitter.py` — Divisor de nombres COMPARTIDO con IHQ: corregido bug que duplicaba el primer token cuando `primer_apellido_idx == 0` (líneas ~152-156).

### Added
- **Pipeline de Coloraciones básicas (V6.9.45 / V6.9.46)** — PDFs de tinciones tipo H&E ("M … AL …") detectados automáticamente en "Procesar seleccionados" y enrutados a un flujo dedicado que extrae SOLO el diagnóstico a la columna `Diagnostico Coloracion 2` (TEXT). Carga inicial: 139 PDFs → 6.806 coloraciones. Las filas usan clave `M######`.
- **`reconciliar_coloraciones()` (V6.9.46)** — Función idempotente que, tras CADA importación (IHQ o coloración), deriva por cédula la columna `Diagnostico Coloracion 2` de la fila IHQ del paciente: 1 coloración → el diagnóstico; varias → los N diagnósticos CONCATENADOS y numerados en la columna. Funciona igual empiece el PDF de coloración o el de IHQ.
- **`get_db_fingerprint()` (V6.9.47)** — Huella barata (COUNT+MAX) usada por el auto-refresh de 60 s para evitar recargas completas innecesarias.

### Changed
- Columna `Diagnostico Coloracion 2` migrada de `VARCHAR(500)` a `TEXT` para evitar truncado de diagnósticos largos (recuperó diagnósticos de hasta 2.176 caracteres).
- Las filas de coloración (clave `M######`) se EXCLUYEN de estadísticas, dashboard y KPIs (filtro `^[Mm]\d`) pero permanecen visibles y buscables en el Visualizador por cédula/nombre.
- El Visualizador oculta del DISPLAY las filas M redundantes (single-merged, cuyo diagnóstico ya está reflejado en la fila IHQ) sin borrarlas de la BD.
- `_apply_row_colors`: coloreado de la tabla vectorizado con `drop_duplicates`/`to_dict('records')` (en vez de `groupby` + `iloc[0].to_dict()`); clasificación sobre arrays (en vez de `iterrows`); solo evalúa filas IHQ. De ~13.300 ms a ~280 ms (elimina el congelamiento de ~13 s al abrir el Visualizador).
- Auto-refresh de 60 s usa la huella `get_db_fingerprint()` y se salta la recarga completa si la BD no cambió (elimina el freeze periódico de ~1 s/min).

### Fixed
- **V6.9.48 — Extracción de nombres en coloraciones (caso M2506212):** `_RE_NOMBRE` en `coloracion_extractor.py` ahora trata como OPCIONAL el salto de línea antes de "N. peticion" → recupera ~490 nombres que salían en N/A. 0 regresiones (10.460/10.460).
- **División de nombres (compartida con IHQ):** corregido bug en `core/utils/name_splitter.py` que duplicaba el primer token cuando `primer_apellido_idx == 0` ("HECTOR ERNESTO MORA" → "HECTOR HECTOR ERNESTO MORA"). Corrigió 358 coloraciones (0 artefactos; las 173 restantes son apellidos repetidos REALES) y 69 nombres IHQ preexistentes (backup en `backups/backup_nombres_ihq_dup69.json`).

### Decisiones técnicas

#### 1. Pipeline de coloraciones AISLADO del IHQ
El extractor y el procesador de coloraciones viven en archivos propios (`coloracion_extractor.py`, `coloracion_processor.py`) y nunca tocan el flujo IHQ. Cada coloración es su propia fila `M######` y constituye la fuente de verdad: nunca se pierde ni se pisa, independientemente de cuándo llegue su IHQ correspondiente.

#### 2. Reconciliación independiente del orden e idempotente
`reconciliar_coloraciones()` corre tras CADA importación (IHQ o coloración) y deriva por cédula la columna `Diagnostico Coloracion 2` en la fila IHQ. Por ser idempotente, converge al mismo punto fijo sin importar si el PDF de coloración o el de IHQ se procesó primero. Verificado: 553 pacientes coloración∩IHQ enlazados, 0 enlaces espurios, 0 marcadores incorrectos, reconciliación en punto fijo.

#### 3. Separación entre dato persistido y dato mostrado
Las filas M siempre persisten en BD (auditabilidad). El Visualizador decide en tiempo de DISPLAY cuáles ocultar (M redundantes single-merged) sin borrar nada. Las estadísticas/dashboard/KPIs filtran las claves `^[Mm]\d` para no contaminar las métricas oncológicas, que son SOLO de IHQ.

#### 4. `TEXT` en lugar de `VARCHAR(500)` para diagnósticos de coloración
Los diagnósticos de coloración pueden superar largamente los 500 caracteres (se observaron hasta 2.176). La columna se migró a `TEXT` para evitar truncado silencioso.

#### 5. Rendimiento por vectorización, no por reescritura de la lógica
Las mejoras de `_apply_row_colors` y del auto-refresh se lograron vectorizando con pandas/NumPy y agregando una huella barata de cambio, sin alterar la semántica del coloreado ni la lógica de negocio.

### Validation
- ✅ Verificado en producción contra MySQL `huv_oncologia` / `informes_ihq`: 2.076 → 8.816 filas.
- ✅ Carga inicial de coloraciones: 139 PDFs → 6.806 coloraciones.
- ✅ Reconciliación: 553 pacientes coloración∩IHQ enlazados, 0 enlaces espurios, 0 marcadores incorrectos, punto fijo confirmado.
- ✅ Fix `_RE_NOMBRE`: ~490 nombres recuperados, 0 regresiones (10.460/10.460).
- ✅ Fix `name_splitter`: 358 coloraciones + 69 IHQ corregidas, 0 artefactos (173 apellidos repetidos restantes son reales), backup `backups/backup_nombres_ihq_dup69.json`.
- ✅ `_apply_row_colors`: ~13.300 ms → ~280 ms. Auto-refresh sin freeze periódico.

---

## [6.9.0] - 2026-05-11 — MySQL/MariaDB Multi-User LAN Support

**Sprint:** Migración del backend de BD de SQLite (single-user, file-based) a MySQL/MariaDB (multi-user, cliente-servidor) usando XAMPP. Permite que **múltiples usuarios en la red LAN del HUV** vean y modifiquen los MISMOS datos en tiempo real, sin conflictos de file-locking ni corrupción.

### Impact
| Aspecto | V6.8.x (SQLite) | V6.9.0 (MySQL) |
|---|---|---|
| Backend | Archivo `.db` local | Servidor MySQL/MariaDB centralizado |
| Concurrencia | 1 usuario | **N usuarios simultáneos** |
| Ubicación de datos | PC individual | **Servidor compartido en LAN** |
| Sincronización | Manual (compartir archivo) | **Automática (mismo servidor)** |
| Corrupción por SMB | Frecuente | Eliminada |
| Setup adicional | Ninguno | XAMPP + 5 min config |
| Compatibilidad legacy | — | **SQLite sigue funcionando** (toggle por config) |

### Files modified
- `core/db_adapter.py` (NUEVO) — Abstracción SQLite ↔ MySQL. Funciones: `get_connection()`, `cursor_ctx()`, `dialect()`, `ph()`, `quote_ident()`, `upsert_sql()`, `column_type()`, `get_existing_columns()`, `add_column_if_missing()`.
- `core/database_manager.py` — Detección de dialecto en `init_db()`, `save_records()`, `get_all_records_as_dataframe()`, `get_registro_by_peticion()`. Nueva función `_create_table_mysql()` con schema adaptado (VARCHAR PK + TEXT para resto, índices con prefijo).
- `core/diagnosticos_ia_db.py` — Igual: branching por dialecto en todas las operaciones. Tabla `diagnosticos_ia` ahora en la misma BD `huv_oncologia` (junto a `informes_ihq`).
- `config/config.ini` — Nueva sección `[database]`:
  ```ini
  tipo = mysql
  host = 192.168.2.172
  puerto = 3306
  usuario = huv_app
  password = huv2026
  base_datos = huv_oncologia
  charset = utf8mb4
  ```

### Decisiones técnicas

#### 1. Schema MySQL: TEXT + VARCHAR(50) para PK
MariaDB limita row size a 65,535 bytes (excluyendo TEXT/BLOB). Con 184 columnas VARCHAR(500) × utf8mb4 (4 bytes/char) = 368,000 bytes (excede). Solución: `Numero de caso VARCHAR(50) PRIMARY KEY` y resto `TEXT` (almacenado fuera de la fila). Índices secundarios con prefijo (ej: `Malignidad`(20)`).

#### 2. UPSERT con `INSERT ... ON DUPLICATE KEY UPDATE`
MySQL no tiene `INSERT OR REPLACE` como SQLite. Se construye el UPSERT con sintaxis nativa, actualizando todas las columnas presentes en el `record` y preservando las ausentes (`VALUES()` función especial).

#### 3. Compatibilidad backwards
El código detecta `dialect()` en runtime y bifurca. Si `tipo = sqlite` en config, el flujo legacy con archivo `.db` sigue intacto (útil para desarrollo offline).

#### 4. Doble destino IA → ambas BDs
"Procesar con IA" sigue guardando en `informes_ihq` (Visualizador) y `diagnosticos_ia` (histórico audit). Ahora ambas tablas viven en la misma BD MySQL → un solo backup las cubre.

### Setup multi-cliente (instrucciones para PCs adicionales)

Para que **otros usuarios del HUV** vean los mismos datos:

1. **En el servidor (esta PC, IP 192.168.2.172)**:
   - XAMPP corriendo con MySQL/MariaDB
   - Firewall Windows: permitir entrada TCP puerto 3306 (perfil LAN)
   - Usuario `huv_app@%` ya creado (permite conexión desde cualquier IP de la LAN)

2. **En cada PC cliente**:
   - Instalar la app HUV
   - En `config/config.ini` cambiar el host:
     ```ini
     [database]
     tipo = mysql
     host = 192.168.2.172   ; IP del servidor
     puerto = 3306
     usuario = huv_app
     password = huv2026
     base_datos = huv_oncologia
     ```
   - Al abrir la app, se conectará automáticamente al servidor

3. **Volver a single-user (modo offline)**: cambiar `tipo = sqlite` en config.

### Comparativa de operaciones (medidas en LAN local)
| Operación | SQLite local | MySQL LAN |
|---|---|---|
| init_db (idempotente) | ~50ms | ~80ms |
| save_records (1 caso) | ~20ms | ~30ms |
| save_records (50 casos batch) | ~600ms | ~900ms |
| get_all_records (995 casos) | ~250ms | ~400ms |
| Conexiones simultáneas | 1 práctica | **Hasta 151 (default MariaDB)** |

### Seguridad — pendiente (a hacer antes de producción)
- ⚠️ Password `huv2026` es solo para pruebas. Cambiar a uno fuerte vía phpMyAdmin antes de uso real.
- Considerar restringir `huv_app@%` a `huv_app@192.168.2.%` (solo LAN del hospital).
- Backup automático con tarea programada (`mysqldump` nocturno).

---

## [6.8.0] - 2026-05-08 — IA Pipeline 184-Column Full Schema + BD Unification

**Sprint:** Expansión del pipeline "Procesar con IA" desde 3 columnas (numero_peticion, diagnostico, organo) a **184 columnas** (todas las clínicas de la BD principal). Unificación: ahora el botón "Procesar con IA" escribe DIRECTAMENTE a la BD principal `huv_oncologia_NUEVO.db` (tabla `informes_ihq`), de modo que el resultado aparece en el **Visualizador de Datos**, en paralelo con "Procesar seleccionados" (extractor tradicional).

### Impact
| Aspecto | V6.7.x | V6.8.0 |
|---|---|---|
| Columnas extraídas por IA | 3 | **184** |
| Schema JSON LLM | 3 campos | **184 campos** |
| BD `diagnosticos_ia.db` | 7 cols | **188 cols** (184 + 4 metadata) |
| Tabla del modal IA | 3 cols visibles | **187 cols** (3 alias + 184 BD) con scroll H+V |
| Copia/CSV export | 3 cols | 187 cols con headers BD |
| Destino BD | Solo `diagnosticos_ia.db` | **Doble: `diagnosticos_ia.db` + `informes_ihq` (principal)** |
| Visualizador de Datos | No reflejaba casos IA | **Refresh automático tras procesar IA** |

### Files modified
- `core/columnas_huv_ia.py` (NUEVO) — Mapeo de 184 columnas BD ↔ aliases JSON-safe del LLM. Funciones: `build_json_schema()`, `build_json_schema_pasada_1/2()`, `detectar_biomarcadores_en_ocr()`, `llm_response_to_db_dict()`.
- `core/diagnosticos_ia_db.py` — Schema expandido a 188 columnas. Nueva función `save_caso_completo(datos_columnas, ...)` que recibe dict completo. PK cambió de `numero_peticion` → `Numero de caso`. ALTER TABLE para migrar BDs viejas.
- `ui.py` — Prompt del LLM expandido con instrucciones por categoría (admin, dx, biomarcadores). Worker `_process_files_ia_worker` ahora guarda en AMBAS BDs (acumulativa IA + principal) y dispara `refresh_data_and_table()` al finalizar. Tabla del modal con scroll H+V mostrando las 187 columnas. Copia/CSV adaptados.

### Decisiones técnicas

#### 1. Modelo recomendado: `qwen2.5-14b-instruct`
Tras pruebas con varios modelos:
- `qwen3.6-27b` (reasoning) → todo va a `reasoning_content`, requiere esperar reasoning largo, ~30 min/IHQ con 184 campos (no viable)
- `qwen2.5-32b-instruct` → no cabe en 8GB VRAM (offload masivo), timeout >10 min
- `qwen2.5-14b-instruct` → cabe casi completo, **~7 min/IHQ con schema strict de 184 campos** (~5 días para 995 casos) ✓

#### 2. Schema `strict: True, additionalProperties: False`
`additionalProperties: True` con 184 fields rompe el grammar engine de llama.cpp ("number of rules exceeds sane defaults"). Strict es obligatorio.

#### 3. Doble persistencia (IA + principal)
La IA escribe en `diagnosticos_ia.db` (histórico/audit) Y en `informes_ihq` (BD principal). UPSERT por "Numero de caso" en ambas: si el caso ya existe, se reemplaza. Permite usar "Procesar con IA" y "Procesar seleccionados" sobre los mismos casos para comparar o iterar.

### Workflow del usuario
1. Selecciona PDFs → click "🤖 Procesar con IA"
2. Modal muestra tabla con 187 columnas en vivo
3. Cada caso se guarda en `informes_ihq` mientras se procesa
4. Al finalizar, el Visualizador de Datos se refresca automáticamente
5. Si después corre "Procesar seleccionados" sobre los mismos PDFs, esos datos REEMPLAZAN los de IA (y viceversa)

### Notas
- Tiempo total para 995 IHQs con qwen2.5-14b-instruct: ~5 días (procesamiento batch nocturno o fin de semana)
- Calidad observada: ~80% campos correctos en una sola pasada. Algunos errores ocasionales (alucinaciones en edad, mismatches entre descripcion_microscopica/diagnostico_principal) que requieren post-procesamiento o revisión humana.
- BD `data/diagnosticos_ia.db` puede borrarse en cualquier momento sin afectar la BD principal — es solo un histórico.

---

## [6.7.20] - 2026-05-08 — IA Pipeline UI Show-Full-Dx

**Sprint:** Bug fix de presentación. La V6.7.19 ya extraía y guardaba todos los dx completos en BD, pero la UI los truncaba visualmente a 200 chars + "..." haciendo parecer que la extracción estaba rota. Esto era un falso positivo que generaba percepción equivocada de calidad.

### Verificación
Auditoría directa a `data/diagnosticos_ia.db` confirmó que los 3 casos testigo "truncados" estaban completos en BD:
- IHQ250100: 262 chars (`...CATEGORÍAS 4 Y 2 RESPECTIVAMENTE BANFF 2022)`)
- IHQ250160: 222 chars (`...DE ASPECTO PLASMOCITOIDE NI BLÁSTICO`)
- IHQ250178: 235 chars (`...INVASIÓN LINFOVASCULAR NO IDENTIFICADA`)

### Files modified
- `ui.py` — `_poll_processing_progress_ia()`: removido bloque `if len(dx) > 200: dx = dx[:200] + "..."` antes del insert al Treeview.

### Trade-off
Los dx muy largos (>300 chars) ahora ocupan más espacio horizontal en la tabla. Aceptable: el usuario explícitamente prefiere ver toda la info clínica.

---

## [6.7.19] - 2026-05-07 — IA Pipeline Zero-Truncation

**Sprint:** Eliminación definitiva de truncamientos en dx con scoring extenso. Decisión clínica: cada IHQ es único, no se acepta pérdida de información en favor de velocidad.

### Impact (cualitativo)
| Métrica | V6.7.18 (1500/2500) | V6.7.19 (3000/4000) |
|---|---|---|
| Truncamientos remanentes | 5-6 casos extremos | **0** |
| Tiempo por chunk (qwen 27B) | ~10s | ~13s (~30% más) |
| Calidad de extracción | ~97% | **~99-100%** |

### Files modified
- `ui.py` — `_llamar_llm_con_retry()`: max_tokens 1500/2500 → 3000/4000.

### Casos testigo recuperados (vs V6.7.18)
| IHQ | V6.7.18 (truncado) | V6.7.19 (completo) |
|---|---|---|
| IHQ250100 | `... RECHAZO ACTIVO MEDIADO...` | RECHAZO Banff completo |
| IHQ250160 | `... DE ASPECTO PLA...` | médula ósea histología completa |
| IHQ250178 | `... INVASIÓN PERINEURAL... INV...` | próstata Gleason + cores + % completo |
| IHQ250275 | `... MODERADOS D...` | BIOPSIA INJERTO Banff 2022 completo |
| IHQ250389 | `... HER 2 POSIT...` | mama Nottingham + molecular completa |
| IHQ250401 | `... SCORE 0...` | mama receptores hormonales completos |

### Trade-off
Cada chunk tarda ~3s extra (10s → 13s con qwen3.6-27b en RTX 3050 OEM 8GB). Para un PDF de 50 IHQs: ~2 min extra por PDF. Aceptable para procesamiento batch nocturno.

---

## [6.7.18] - 2026-05-07 — IA Pipeline json_schema + Prompt-Driven Extraction

**Sprint:** Pipeline alternativo de extracción IA (`Procesar con IA`) refinado de cero a producción. Se eliminaron las "muletas" en código (post-procesamiento agresivo, mapeos hardcoded de adjetivos, typos del modelo) en favor de un enfoque **prompt-driven**: el modelo capaz (qwen 27B) + prompt detallado + json_schema estricto = extracción limpia sin código de saneamiento.

### Impact (cualitativo)
| Métrica | gpt-oss-20b (V6.7.0-14) | qwen3.6-27b (V6.7.18) |
|---|---|---|
| Tasa de extracción | ~30% (arrays vacíos frecuentes) | **~97% perfectos** |
| Truncamientos `…?` en dx | Frecuentes | 2 casos extremos (max_tokens) |
| Mismatch dx ↔ órgano | 3-5/50 | 0/165 |
| Preámbulos del patólogo | No strippeados | Strippeados por el modelo |
| HTTP 400 en LM Studio | Constante | Resuelto (json_schema) |
| Alucinación de tokens | Sí (IHQ023, 055) | Cero |

### Files modified
- `core/llm_client.py` — Nuevo parámetro `json_schema` en `completar()`. Cuando se pasa, usa `response_format: json_schema` (compatible con gpt-oss-20b y qwen, fuerza estructura a nivel de decoder). Parser `_extraer_json_robusto` mejorado para tolerar tokens harmony de gpt-oss (`<|channel|>analysis|...|<|message|>...<|end|>`).
- `ui.py` — Pipeline IA completo: prompt detallado con stripping de preámbulos como instrucción del LLM (no como regex post-procesamiento), schema con `minItems: 1, maxItems: 1` para forzar 1 entrada por chunk, max_tokens=1500/2500 para dx con scoring extenso (Banff, Gleason, médula ósea histology). Cleanup post-LLM mantenido SOLO para typos residuales y normalización de tildes.
- `core/diagnosticos_ia_db.py` — Nueva BD SQLite acumulativa (`data/diagnosticos_ia.db`) para persistir diagnósticos extraídos a lo largo de múltiples sesiones de procesamiento.

### Decisiones técnicas clave

#### 1. `json_object` → `json_schema`
gpt-oss-20b (LM Studio) rechaza `response_format: json_object` con HTTP 400 (`'response_format.type' must be 'json_schema' or 'text'`). El cliente caía a retry sin format, y sin la restricción el modelo emitía razonamiento mezclado con JSON, rompiendo el parser. Migrar a `json_schema` con strict=true forzó la estructura a nivel de generación de tokens.

#### 2. `minItems: 1, maxItems: 1`
Tras resolver el parsing, gpt-oss-20b empezó a devolver `{"diagnosticos":[]}` cuando no encontraba dx claro (~70% de chunks). Con `minItems: 1, maxItems: 1` el modelo está obligado a extraer exactamente 1 entrada por chunk. Tasa de extracción saltó de 30% a 100%.

#### 3. Cambio de modelo: gpt-oss-20b → qwen3.6-27b
Aún con json_schema + minItems, gpt-oss-20b mostraba problemas residuales:
- Truncamientos arbitrarios del dx (`...`)
- Mismatches dx ↔ órgano
- Alucinación de tokens (`…?…OCR…`)
- Typos del modelo (`PARIETO`, `MEDIANTE`, `MESA MEDIASTINAL`)
qwen3.6-27b cabe parcialmente en RTX 3050 OEM 8GB con offload a RAM (más lento ~10s/chunk vs ~3s) pero entrega calidad superior consistentemente.

#### 4. Preámbulos: prompt > código
En vez de mantener regex de stripping en post-procesamiento (`stripear_preambulos`), se trasladó la regla al prompt del LLM como instrucción explícita con ejemplos. Resultado: qwen respeta la regla y devuelve dx limpios sin necesidad de regex.

### Roadmap V6.7
- V6.7.0: Botón "Procesar con IA" inicial
- V6.7.3-7.5: Cleanup regex post-LLM (post-procesamiento agresivo — descartado en V6.7.15+)
- V6.7.8-7.13: Chunking IHQ-aware (1 IHQ por chunk)
- V6.7.14: Workaround typos gpt-oss
- V6.7.15: json_schema + parser harmony tokens
- V6.7.16: minItems/maxItems + tilde stripping
- V6.7.17: max_tokens 800 → 1200 (scoring Banff)
- V6.7.18: max_tokens 1200 → 1500 (médula ósea, Gleason)

### Casos testigo recuperados (vs gpt-oss-20b)
| IHQ | Antes | Ahora |
|---|---|---|
| IHQ250023 | `NEOPLASIA EN PATRON … …?…OCR…???..?` (basura) | `NEOPLASIA EN PATRON ACINAR CON CAMBIOS ONCOCITICOS DE PROBABLE ORIGEN RENAL` |
| IHQ250037 | `- HALLAZGOS` | `COLITIS AGUDA Y CRÓNICA NO ESPECÍFICA` |
| IHQ250043 | `GLIOSIS REACTIVA` / `ESTOMAGO` (mismatch) | `GLIOSIS REACTIVA` / `CEREBRO` |
| IHQ250045 | órgano `CUELLO` | órgano `GANGLIO LINFATICO` |
| IHQ250056 | órgano `CERVIX` (mismatch para LINFOMA FOLICULAR) | órgano `GANGLIO LINFATICO` |
| IHQ250076 | `LOS HALLAZGOS MORFOLOGICOS Y DE IHQ SUGIEREN UN ADENOCARCINOMA…` | `ADENOCARCINOMA DE ORIGEN EN EL TRACTO GENITAL FEMENINO` (preámbulo strippeado por modelo) |
| IHQ250095 | `HALLAZGOS DE INMUNOHISTIQUÍMICA COMPATIBLES CON LINFOMA…` | `LINFOMA DIFUSO DE CÉLULAS B GRANDES, FENOTIPO CENTROGERMINAL` |
| IHQ250096 | `LOS HALLAZGOS FAVORECEN UN LINFOMA LINFOBLÁSTICO T` | `LINFOMA LINFOBLÁSTICO DE CÉLULAS T` |

### Notas
- Hardware constraint: RTX 3050 OEM 8GB VRAM. qwen3.6-27b requiere offload parcial → ~10s por chunk. Aceptable para extracción batch nocturna.
- Pipeline NO modifica BD principal (`huv_oncologia_NUEVO.db`). Es paralelo: persiste en `data/diagnosticos_ia.db` como referencia para comparar cobertura del extractor tradicional (588 IHQs detectados) vs IA (995 IHQs esperados en el set total).

---

## [6.6.16] - 2026-05-04 — Diagnosis Categorization Sprint

**Sprint:** Refinamiento masivo del normalizador de diagnósticos (`core/normalizador_diagnosticos.py`) y un fix crítico de detección de malignidad en `core/extractors/medical_extractor.py`. El sprint cubre seis versiones consecutivas (V6.6.12 → V6.6.16) aplicadas como cambios quirúrgicos validados con auditoría cuantitativa sobre 188 casos del rango IHQ250001-200.

### Impact (cuantitativo)
| Métrica | Antes | Después | Mejora |
|---|---|---|---|
| Diagnósticos oncológicos categorizados | 62/100 (62.0%) | 161/188 (85.6%) | **+23.6 pts** |
| Casos problemáticos (OTRO + SIN DX) | 28/100 (28.0%) | 27/188 (14.4%) | **−13.6 pts** |
| Distribución MALIGNO/BENIGNO | 73/27 | 75/25 | sin desbalance |
| Regresiones detectadas | — | 0 | limpio |

### Files modified
- `core/normalizador_diagnosticos.py` — cambios mayores: typos del patólogo, 6 categorías nuevas/extendidas, stripping de preámbulos, reordenamientos de prioridad, ampliación de inferencia por órgano.
- `core/extractors/medical_extractor.py` (función `determine_malignancy`, líneas ~3641-3686) — nueva PRIORIDAD -2 que aísla negaciones explícitas en `Diagnostico Principal` para evitar contaminación por historia clínica.

### Changes by version

#### V6.6.12 — Typo del patólogo "CARICNOMA"
- `normalizar_texto()`: corregido typo "CARICNOMA" → "CARCINOMA" en preprocesamiento.
- **Caso piloto:** IHQ250060.
- **Impacto:** 1 caso recuperado (OTRO/NO CATEGORIZADO → CARCINOMA → refinado por órgano a OTRO CARCINOMA DE MAMA).

#### V6.6.13 — Categorías faltantes en el diccionario
- Agregadas 4 categorías nuevas: **TUMOR FILODES DE MAMA**, **CARCINOMA PAPILAR DE MAMA**, **NEOPLASIA DE CELULAS FUSIFORMES / FUSOCELULAR**, **LESION ESCAMOSA INTRAEPITELIAL / NIC**.
- Extendida **LINFOMA NO HODGKIN B** con patrones OMS 2022 ("NEOPLASIA DE CELULAS B MADURAS").
- **Casos piloto:** IHQ250071, IHQ250081, IHQ250066, IHQ250126, IHQ250107, IHQ250116.
- **Impacto:** 6 casos recuperados.

#### V6.6.14 — Stripping de preámbulos del patólogo + reordenamiento
- Nueva función `stripear_preambulos()` con 11 preámbulos típicos del patólogo del HUV (ej. "RESULTADO IHQ COMPATIBLE CON…").
- `categorizar_diagnostico()` modificada para invocar el stripping antes del matching.
- **Reordenamientos críticos** (resolver cortocircuitos contra patrones genéricos):
  - `ADENOCARCINOMA (SIN ORIGEN)` y `CARCINOMA (OTRO)` ANTES de `RESULTADO IHQ`.
  - `LEUCEMIA MIELOIDE` y `LEUCEMIA LINFOIDE AGUDA` ANTES de `LINFOMA (OTRO/INESPECIFICO)`.
- Nueva categoría: **CARCINOMA ANEXIAL CUTANEO**.
- **LINFOMA NO HODGKIN B** extendido con "ZONA MARGINAL".
- **LEUCEMIA LINFOIDE AGUDA** extendida con "LEUCEMIA/LINFOMA LINFOBLASTICO".
- **Casos piloto:** IHQ250026, IHQ250028, IHQ250041, IHQ250087, IHQ250091, IHQ250099, IHQ250105, IHQ250140, IHQ250147, IHQ250158, IHQ250164, IHQ250166, IHQ250174.
- **Impacto:** 15 casos recuperados (13 por preámbulos + 2 por sufijo SOBREEXPRESIÓN).

#### V6.6.14 (cont.) — Mini-fix RECTAL en INFERENCIA_POR_ORGANO_ADENO
- El patrón "RECTO" no matcheaba "RECTAL" como substring.
- **Caso piloto:** IHQ250159.
- **Impacto:** 1 caso recuperado.

#### V6.6.15 — Fix CRÍTICO Malignidad (PRIORIDAD -2 en `determine_malignancy`)
- **Problema:** la PRIORIDAD -1 evaluaba `combined_text = diagnostico + macroscopica + microscopica + full_text`. La historia clínica con "Historia de carcinoma de mama" disparaba MALIGNO aunque el dx final fuera benigno (ej. INFLAMACIÓN AGUDA SIN EVIDENCIA DE LESIÓN NEOPLÁSICA).
- **Solución:** nueva PRIORIDAD -2 que evalúa SOLO el `Diagnostico Principal` para negaciones explícitas. Si tiene negación y NO tiene también keyword maligno (caso multi-muestra), retorna BENIGNO.
- **Casos piloto:** IHQ250106 (target — crítico clínicamente), IHQ250065 (bonus).
- **Impacto:** 2 casos recuperados.

#### V6.6.16 — Mini-fixes basados en audit cuantitativo
- Typo "HISTOLOGIOS" → "HISTOLOGICOS" en `normalizar_texto` (caso IHQ250026 MELANOMA).
- Nueva categoría **INFLAMACION / PROCESO INFECCIOSO** (cubre IHQ250037 colitis, IHQ250075 peritonitis, IHQ250061 Hirschsprung).
- `INFERENCIA_POR_ORGANO_ESCAMO` ampliado con: LABIO, BOCA, FARINGE, HIPOFARINGE, NASOFARINGE, ESOFAGO, ANO, VULVA, VAGINA.
- **Impacto:** 4+ casos recuperados.

### Validation
- 75+ casos validados manualmente con resultados esperados (todos OK).
- 54 self-tests internos del normalizador (54/54 OK).
- 12 casos de regresión específicos para `determine_malignancy` (12/12 OK).
- Audit cuantitativo sobre 188 casos del período IHQ250001-200 (**0 regresiones**).

### Anti-regression notes (REGLA CRÍTICA #1)
Todos los cambios siguen el patrón "patrón específico nuevo ANTES + fallback genérico ORIGINAL preservado". Ningún patrón existente fue eliminado o sobrescrito; todas las extensiones se agregaron como ramas adicionales o reordenamientos de prioridad. Comentarios `V6.6.XX FIX IHQYYYYY` en el código documentan la trazabilidad caso-por-caso.

---

## [6.0.0] - 2025-10-20

### Changed
- Consolidación 19→6 archivos core
- 7 workflows maestros implementados
- version-manager gestiona CHANGELOG+BITÁCORA acumulativos
- documentation-specialist simplificado (solo lee CHANGELOG)
- 4 herramientas densas (4665 líneas)
- 5 agentes especializados (2066 líneas)

---

Changelog

Este proyecto sigue versionamiento semantico.

[Unreleased]
- **CONSOLIDACIÓN COMPLETA SYSTEMPROMPT**: Finalización protocolo análisis SYSTEMPROMPT con reporte navegación ChatGPT.
- **REPORTE_CHATGPT.md completo**: Mapa navegable proyecto con rutas absolutas Drive, componentes principales, flujos pipeline y comandos navegación.
- **28 Plantillas NotebookLM**: Contenido especializado para 4 audiencias (Médico oncológico, Desarrollo, Dirección, Investigadores) en formatos audio, video y cuestionarios.
- **Navegación IA Externa**: Estructura optimizada para ChatGPT con referencias exactas archivo:línea y flujos consulta típicos por dominio técnico/médico.
- Integracion completa de Biopsia/Autopsia al flujo persistente y dashboards.
- Sincronizacion incremental con Power BI y agendas clinicas.
- Hardening de pruebas automaticas de extraccion y visualizacion.

2025-09-22 — docs - SYSTEMPROMPT Analysis
- **DOCUMENTACIÓN TÉCNICA MODULAR COMPLETA**: Análisis exhaustivo de 10 componentes críticos del sistema siguiendo protocolo SYSTEMPROMPT con 12 secciones por componente.
- **Análisis técnico evidence-based**: Documentación con referencias exactas archivo:línea para cada componente del pipeline OCR.
- **Arquitectura médica especializada**: Documentación profunda del dominio oncológico HUV con vocabulario biomarcadores, patrones extracción y flujos clínicos.
- **Componentes analizados**: 
  - `01_huv_ocr_sistema_definitivo.md` - Entry point y configuración Tesseract
  - `02_ui.md` - Interfaz CustomTkinter 1299 líneas con 4 tabs especializados
  - `03_ocr_processing.md` - Engine OCR híbrido PyMuPDF/Tesseract con limpieza médica
  - `04_procesador_ihq_biomarcadores.md` - Extractor biomarcadores HER2/Ki-67/RE/RP/PD-L1 
  - `05_database_manager.md` - Gestor SQLite con esquema 167 campos transaccional
  - `06_huv_web_automation.md` - Automatización portal Selenium con error recovery
  - `07_calendario.md` - Scheduler interno tareas automatizadas con threading
  - `08_huv_constants.md` - Vocabulario médico centralizado y patrones regex
  - `09_config.ini.md` - Configuración multiplataforma con detección OS
  - `10_test_sistema.py.md` - Suite pruebas automatizadas con fixtures médicas
- **Gestión técnica**: Identificación riesgos médicos críticos, deuda técnica, puntos extensión y estrategias optimización por componente.
- **Cobertura completa**: Desde entry point hasta testing, incluyendo seguridad datos médicos, performance OCR y mantenibilidad arquitectura.
- **Documentación ONCONOVA**: Actualización README.md, INFORME_GLOBAL_PROYECTO.md, INICIO_RAPIDO.md con nueva arquitectura v2.5.

2025-09-20 — docs
- Generado/actualizado `documentacion/REPORTE_CHATGPT.md` con el mapa del proyecto.
- Enlace agregado en `documentacion/README.md`.
 - Documentado `scripts/inspect_excel.py` en `documentacion/analisis/21_inspect_excel.md`.
 - Limpieza de binarios: movidos a `utilidades/binarios/` y `.gitignore` ampliado (EXCEL/, pdfs_patologia/, huv_oncologia.db, *.exe).
 - Ejecutable probado con PyInstaller (`dist/OCR_Medico.exe`).

2025-09-15 – v2.5.0
- Rediseno de la aplicacion de escritorio con CustomTkinter: navegacion por Procesar PDFs, Visualizar Datos, Dashboard Analitico y Automatizar BD Web.
- Canalizacion persistente: `procesador_ihq_biomarcadores` segmenta multiples informes por PDF, normaliza biomarcadores y guarda resultados en `huv_oncologia.db` mediante `database_manager`.
- Dashboard analitico integrado (Matplotlib/Seaborn) con filtros dinamicos, comparador parametrizado y modo pantalla completa.
- Automatizacion del portal `huvpatologia.qhorte.com` con Selenium (`huv_web_automation.py`) para consultas guiadas desde la aplicacion.
- Widget `CalendarioInteligente` (Babel + holidays) para seleccionar rangos de fecha con contexto de festivos.
- Documentacion actualizada para arquitectura 2.5 e incorporacion de analisis de `database_manager`, `huv_web_automation` y `calendario.py`.

2025-09-10 – v1.1.0
- Version estable v1.1 liberada.
- Nuevo analisis avanzado de IHQ accesible desde la UI (boton "Analizar Biomarcadores IHQ (v1.1)") que genera un Excel separado con HER2, Ki-67, RE/ER, RP/PR, PD-L1, P16 (estado/porcentaje) y "Estudios Solicitados".
- Documentacion actualizada: `INFORME_GLOBAL_PROYECTO.md`, `README.md`, `INICIO_RAPIDO.md` y bitacora.

2025-09-10
- Rebranding y reestructuracion documental al ecosistema "ONCONOVA Gestor H.U.V".
- Creacion de `BITACORA_DE_ACERCAMIENTOS.md` y carpeta `comunicados/` (cinco artefactos).
- Ajustes de analisis: documentacion de extensiones IHQ y activos de datos.

2025-09-05 – v1.0.0
- Fundacion y validacion: motor OCR + app de escritorio.
- Procesadores especializados: Autopsia, IHQ, Biopsia, Revision.
- Exportacion validada a Excel (55 columnas) con formato profesional.

2025-08-20 – v0.1.0
- Inicio del desarrollo: estructura base, OCR y primeras reglas de extraccion.
