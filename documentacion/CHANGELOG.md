# Changelog

## [6.9.103] - 2026-08-31 — «195 categorías anatómicas» eran 60: tabla de reserva de órgano

```
texto libre sin categorizar : 148 valores / 193 casos  ->  12 valores / 15 casos
categorías canónicas usadas :  47  ->  48
KPI del informe             : 195  ->  60
```

### Qué era ese 195

`normalizar_organo` devuelve el texto limpio cuando ninguna keyword canónica coincide —está
escrito así a propósito—, así que cada localización redactada a mano contaba como una
«categoría anatómica» propia. De las 195, **126 aparecían una sola vez** y no eran órganos:

```
REGION INTRADURAL (CAUDA EQUINA)      LECHO UNGUEAL DE HALLUX
CUELLO, LADO ESTACION 4 Y 5           MASA PERIAREOLAR SUPERIOR Y PROFUNDA
```

Además ensuciaba la cola del gráfico de distribución y fragmentaba: 37 variantes que
empiezan por «REGION», 16 por «MUCOSA», y duplicados por ortografía («GLANDULA LACRIMAL» /
«GLANDULA LAGRIMAL Y ORBITA»).

### La solución: segunda pasada, no más keywords en la tabla principal

`CATEGORIAS_ORGANO_RESERVA` se aplica **solo si el bucle principal no encontró nada**, así
que es estructuralmente incapaz de cambiar una categorización que hoy funciona. Añadir
esas palabras a `CATEGORIAS_ORGANO` sí habría podido: ahí manda `ORDEN_EVALUACION` y una
keyword nueva puede robarle un caso a otra categoría.

Cada entrada sale de un valor REAL medido en el corpus, no de inventar sinónimos. Y se
mapea solo lo inequívoco: **HOMBRO, RODILLA, CODO y MIEMBRO INFERIOR quedan fuera a
propósito**, porque ahí la biopsia puede ser de hueso o de tejido blando y adivinar sería
peor que dejarlo sin categorizar. Son 12 valores en 15 casos, y así se quedan.

Los restos de extracción que no son un órgano —`")"`, `"A"`, `"B-D"`, `"LOS HALLAZGOS
MORFOLOGICOS Y"`— pasan a SIN DATO en vez de contar como categoría.

### Trampa que costó dos corridas

`_kw_re` compila **sin `re.IGNORECASE`** y las keywords existentes están en MAYÚSCULAS,
igual que el texto que devuelve `normalizar_texto_basico`. La tabla de reserva escrita en
minúsculas no casaba NADA: 148 -> 139 en vez de 148 -> 12.

### Efecto secundario, y es bueno

`categorizar_diagnostico_con_organo` infiere el subtipo POR ÓRGANO, así que dar órgano a
178 casos que no lo tenían mejora también su categoría de diagnóstico. Cambian 10, y las
10 a mejor:

```
REGION PREAURICULAR -> PIEL     CARCINOMA ESCAMOCELULAR (OTRAS) -> DE PIEL
MUCOSA PREPILORICA  -> ESTOMAGO ADENOCARCINOMA (OTRAS)          -> GASTRICO
APENDICE CECAL      -> COLON    ADENOCARCINOMA (OTRAS)          -> COLORRECTAL
CUADRANTE SUP. EXT. -> MAMA     CARCINOMA (OTRAS)               -> DE MAMA
```

### Alcance

No toca la BD. `normalizar_organo` solo se usa en capas de presentación (informe
estadístico, dashboard, visor); el `normalizar_organo` que usa el extractor al escribir es
OTRA función, en `medical_extractor.py:3712`. El informe normaliza al dibujar, así que la
mejora es inmediata sin reprocesar nada.

---

## [6.9.101 / 6.9.102] - 2026-08-31 — Las tres familias pendientes: 48 valores recuperados, 0 regresiones

```
FRASE99D -> FAM3B     48 ganados   0 perdidos   6 cambiados
```
De los 6 cambiados: 3 son correcciones de polaridad que coinciden con la BD, 2 limpian
basura verificada contra el informe, y 1 es una discrepancia conocida (ver al final).

### Familia 1 — enunciados de lista donde solo llegaba el PRIMER elemento (V6.9.101)

La nota de memoria apuntaba a `biomarker_extractor.py:7549` y a ~46 casos. Al ir allí, el
patrón de esa zona ("presentan negatividad para") aparece **2 veces** en todo el corpus y
no trunca ninguna. Se dejó de perseguir la línea y se midió el SÍNTOMA: marcadores que el
informe enumera con polaridad clara y que no llegan a la extracción.

```
195 medidos  ->  98 reales   (los otros 97 eran artefactos: IHQ_PR, IHQ_ER, IHQ_P40
                              no son columnas de la BD)
reparto por posición en la lista: 35 en el ÚLTIMO lugar, 14 en el primero
```

No era el truncamiento de un patrón: son cabeceras de lista que nadie expande.

```
IHQ250040  "positividad para EMA, CKAE1/AE3, Beta catenina"
           -> EMA sí; CKAE1AE3 y BETACATENINA se perdían
IHQ250179  "son negativas para ACTINA DE MUSCULO LISO, DESMINA, CD34, CD117, DOG1, S100"
```

Se añade un bloque ADITIVO que expande seis cabeceras (`positividad/negatividad para`,
`son positivas/negativas para`, `marcación positiva/negativa para`) reutilizando TAL CUAL
las guardas de V6.9.99, que costaron seis versiones. Aquí la polaridad la da la cabecera,
no la negación previa — pero se comprueba igual, porque "SIN positividad para X" invierte.

**🛑 La guarda tiene que mirar HACIA ATRÁS, no solo al texto que casa.** Medido en
IHQ251228: "se observan CÉLULAS BASALES con positividad para CK34betaE12 y p63". En
próstata las basales positivas significan glándula BENIGNA y el tumor es NEGATIVO. La
guarda de población no tumoral ya cubría "células basales", pero esas palabras van ANTES
de la cabecera y quedaban fuera del match. Sin este arreglo: 2 polaridades invertidas.

**Y el matiz se pierde por LLEGAR ANTES, no por pisar.** Con el guarda `not in results`
puesto, este bloque seguía degradando 'POSITIVO (focal)' y 'POSITIVO (difusa)' a
'POSITIVO' en 7 casos: escribe primero un valor pelado y la capa que sabe conservar el
matiz se encuentra la clave ocupada. Se resuelve saltando la frase entera cuando hay un
matiz cerca (`_V99101_MATIZ`). Cuesta 13 de los 61 ganados iniciales, y vale la pena.

### Familia 2 — la errata ECADHEREINA (V6.9.102)

```
E-CADHERINA 128 · ECADHERINA 32 · E CADHERINA 11
ECADHEREINA  4  · E-CADHHERINA 1     <- no casaban con E[\s-]?CADHERINA
```
Los siete patrones pasan a `E[\s\-]?CADH{1,2}ERE?INA`, que cubre las cinco variantes. Es
una AMPLIACIÓN: casa todo lo que casaba antes y además las erratas. Las variantes se
añaden también a `name_mapping`, que compara por igualdad exacta.

### Familia 3 — "sin marcación membranosa" (V6.9.102)

El gemelo NEGATIVO de "E-CADHERINA con marcación membranosa positiva" no existía. Medido:
**1 sola aparición en todo el corpus**, IHQ251376. La nota hablaba de un radio de 153
casos: eso era el RIESGO de tocar el patrón genérico, no los casos afectados. Escrito
específico para el marcador, el radio es exactamente 1.

Detalle que costó una corrida: el grupo del patrón tiene que **capturar un token que
exista en `normalizacion`**. Sin capturar nada, el extractor guardaba el match entero
("E-CADHERINA SIN MARCACIÓN MEMBRANOSA") en vez de NEGATIVO.

### Lo aplicado a la BD

50 valores en 29 casos: 48 huecos rellenados (29 POSITIVO / 19 NEGATIVO) y 2 limpiezas
verificadas leyendo el informe:

```
IHQ250386 P40_ESTADO  'POSITIVAS PARA: P40'      -> POSITIVO
IHQ250882 WT1         'Y RECEPTOR DE ESTRÓGENOS' -> POSITIVO
```

### Discrepancia conocida, sin resolver

IHQ260420 CROMOGRANINA: la BD dice 'NEGATIVO (pérdida de expresión)' y el extractor ahora
dice POSITIVO. No es un fallo de ninguno de los dos: el informe se contradice consigo
mismo. El principal (19/05) reporta pérdida de expresión y un **INFORME ADICIONAL**
posterior (22/05) dice "positividad para cromogranina". La BD no se toca; queda para el
patólogo.

---

## [6.9.100] - 2026-08-31 — Multi-espécimen: el diagnóstico ya no se lo lleva el espécimen benigno

```
BASE -> FIX100D    0 ganados   0 perdidos   19 cambiados   (capa determinista, 2.077 casos)
pipeline COMPLETO  1 caso cambia de valor final
```

18 de los 19 cambios se verificaron contra el informe como mejora; 1 (IHQ251244) no es
verificable porque su sección viene cortada por un salto de página.

### El bug

`_det_seccion_diagnostico` tomaba el texto tras la ÚLTIMA mención de procedimiento. En un
informe con varios especímenes, el rótulo del espécimen B va DESPUÉS del diagnóstico del A,
así que la zona arrancaba pasado el cáncer:

```
IHQ250151  "A. Hígado … ADENOCARCINOMA METASTÁSICO / D. Omento … NEGATIVO PARA NEOPLASIA"
           zona elegida = "- NEGATIVO PARA NEOPLASIA."
IHQ250178  "C. … NEGATIVO PARA MALIGNIDAD / F. … ADENOCARCINOMA ACINAR 3+3"
           la zona traía los dos, pero se elegía el PRIMER enunciado (el benigno)
```

### Por qué esta vez no se repitieron las 92 regresiones de V6.9.63

Aquel intento usaba `_DET_FUERTE`, que matchea **"Tumor" dentro del propio rótulo**
("A. Mama derecha. Tumor. Biopsia…"), y devolvía el rótulo como diagnóstico. Y cambiaba la
elección SIEMPRE. Aquí:

- el vocabulario es **estricto** (CARCINOMA, SARCOMA, LINFOMA, GLEASON, METASTÁSICO):
  términos que no pueden aparecer en un rótulo;
- la rama **solo se activa** si hay ≥2 rótulos de espécimen (102 de 2.077 = 4,9%) y alguno
  es inequívocamente maligno. Los mono-espécimen no se tocan.

### Tres cosas que costó aprender, y que están en el código

1. **Casar por sufijo, no por palabra suelta.** Con `\bSARCOMA\b`, "CARCINOSARCOMA DEL
   OVARIO" NO casaba —no hay frontera de palabra ahí dentro— y en IHQ250254 el diagnóstico
   se lo llevaba el espécimen B. Igual pasaría con LIPOSARCOMA o GLIOBLASTOMA.
2. **Hay que quitar el rótulo DENTRO del bloque elegido.** El bloque empieza tras la letra
   ("A.") y aún arrastra "Hígado. Lesión. Biopsia. Estudio de inmunohistoquímica:". Sin
   quitarlo salían diagnósticos como "TUMOR . RESECCIÓN. ESTUDIO DE INMUNOHISTOQUÍMICA:
   CARCINOMA…" (5 casos medidos).
3. **Entre varios especímenes malignos manda el PRIMARIO, no la metástasis.** En IHQ260387
   el bloque A es el ganglio centinela ("MELANOMA METASTASICO (2/2)") y el B es el melanoma
   con toda la estadificación (Breslow 7,4 mm, Clark V). Quedarse con el primer bloque
   maligno tiraba el primario. Si TODOS son metastásicos se conserva el primero
   (IHQ251486: los cuatro especímenes son el mismo tumor metastásico).

### Alcance real, que es MENOR de lo que se creía

La nota anterior hablaba de ~49 casos. Medido ahora de punta a punta: la corrección cambia
el valor FINAL en **1 caso de 2.077**. Los otros 18 ya los resolvían otras capas del
pipeline —el determinista es un *fallback* y no llegaba a decidir— y la BD ya tenía el valor
bueno. Lo que se arregla es la RED DE SEGURIDAD: cuando en un PDF futuro la vía principal
falle, el fallback ya no se quedará con el espécimen benigno.

```
IHQ260174  BD  : CARCINOMA METASTASICO PROBABLEMENTE ORIGINADO EN LA MAMA
           dice: "LOS ESTUDIOS DE INMUNOHISTOQUÍMICA FAVORECEN UN CARCINOMA INVASIVO
                  DE TIPO NO ESPECIAL(DUCTAL)"
           BD corregida. Malignidad se mantiene MALIGNO.
```

---

## [6.9.99] - 2026-08-28 — «expresión para X»: 56 valores recuperados y 7 lecturas corregidas

```
DUR98B -> FRASE99D     56 ganados   0 perdidos   8 cambiados
```

De los 8 cambiados, 7 son correcciones verificadas contra el informe y 1 es un matiz
discutible con la MISMA polaridad. Cero regresiones.

### El hueco

Se descubrió persiguiendo CD45, pero no era cosa de CD45: la frase «expresión para X»
no la reconocía NINGUNA columna. Son 56 valores repartidos en 36 columnas distintas.

### Por qué esta entrada es sobre todo un aviso

La frase PARECE positiva. No lo es: de 170 menciones en el corpus, **71 (el 42%) llevan
una negación delante**. Hicieron falta SEIS versiones, y cada una salió de revisar a mano
la salida de la anterior. Las cinco primeras «parecían bien»:

```
v1  "expresion para X" -> POSITIVO siempre           15 polaridades INVERTIDAS
v2  la negacion decide el signo                       "siendo negativa LA expresion" se
                                                      colaba (4 mas); microambiente como tumor
v3  + determinante + guarda de poblacion              "No\ntienen" partido por el salto de
                                                      linea; "No hay evidencia de..." fuera
v4  + ventana que cruza saltos de linea               la lista no paraba en "SIN expresion
                                                      para" y se comia los negativos
v5  + la negacion corta la lista                      "capa basal" y "acompanada": la misma
                                                      poblacion con otra redaccion
v6  + guardas de intensidad y de perdida              LISTA
```

Si se hubiera implementado la v1 —que es la lectura obvia— habrían entrado **15
polaridades invertidas** en historias clínicas oncológicas.

### Los dos fallos más instructivos

**1. `pérdida` a secas no es una negación.** IHQ260329: «ganglio linfático con PÉRDIDA
PARCIAL DE LA ARQUITECTURA por una proliferación nodular que muestran expresión para
CD20, PAX5, CD10, BCL6». Eso es pérdida de ARQUITECTURA, no de expresión, y volteaba
CUATRO positivos a negativo de una vez. Ahora solo cuenta la pérdida referida a la
marcación.

**2. Llegar antes es tan destructivo como pisar.** La guarda `not in results` estaba
puesta, pero:
  · `results` convive con la clave pelada (`MSH2`) y con prefijo (`IHQ_MSH2`) según qué
    capa la escribiera —el post-filtro V6.4.89 comprueba las dos por esto mismo—, y
    mirando solo una se degradaban 34 valores;
  · aun con las dos, al rellenar PRIMERO, la capa buena se encuentra la clave ocupada y
    se calla. Así se degradaba `POSITIVO (EXPRESIÓN NUCLEAR INTACTA)` —la etiqueta
    canónica MMR de 535 filas— a un `POSITIVO` pelado.

De ahí las exclusiones: MMR (MLH1/MSH2/MSH6/PMS2), HER2 (su resultado es un score, no una
polaridad), toda frase que diga «nuclear» y toda frase que traiga su propia intensidad
(«FUERTE expresión para receptores de Estrógeno y Progesterona» perdía el «fuerte», y en
receptores hormonales la intensidad es dato clínico).

### Las correcciones verificadas

```
IHQ250608 CD34    POSITIVO -> NEGATIVO   "Blastos mieloides CD117+ ... sin expresion para CD34"
IHQ250787 CD117   POSITIVO -> NEGATIVO   "Sin expresion para CD117 y ciclina D1"
IHQ251308 CMYC    NEGATIVO -> POSITIVO   "hay expresion para CMYC y MUM1 en mas del 40%"
IHQ260210 NAPSIN  POS(focal) -> NEGATIVO "No se observa expresion para Napsina A"
IHQ260211 PROLACT POS(focal) -> NEGATIVO "no se detecto expresion para Prolactina, LH, TSH..."
IHQ251135 NAPSIN  ', CK20, Y CK19' -> NEGATIVO    (basura -> valor limpio)
IHQ260347 WT1     'NI GATA3' -> NEGATIVO          (basura -> valor limpio)
```

El octavo, IHQ260547 LH, pasa de `POSITIVO (focal)` a `POSITIVO`: el informe dice «El
perfil hormonal muestra expresión para LH y positividad focal débil para FSH» —el «focal»
es de FSH—, pero el diagnóstico resume «(LH y FSH focal)». Misma polaridad, matiz
discutible. Se deja anotado en vez de forzarlo.

---

## [6.9.98] - 2026-08-28 — Fuga entre frases: 38 patrones acotados, 10 lecturas falsas eliminadas

```
LCA97 -> DUR98B     0 ganados   10 perdidos   0 cambiados
```

Los 10 "perdidos" son 10 valores ERRONEOS que dejan de escribirse. Verificado contra la BD
uno a uno: **0 valores correctos perdidos, 0 cambiados**. El banco solo distingue vacio de
no-vacio, por eso los cuenta como perdida.

### El intento que fallo, primero

Se endurecieron los 92 patrones que la medida AISLADA aprobaba (fallos 621 -> 55, saldo
483 -> 882). De punta a punta el resultado fue el contrario:

```
LCA97 -> DUR98      0 ganados   92 perdidos   5 cambiados
                    de los 92:  68 eran CORRECTOS
```

**Se revirtio entero.** La leccion vale mas que el cambio: la medida aislada de un patron
NO sirve para decidir. Muchos de esos patrones son el ULTIMO que lee en su caso; al
acotarlos no leen mejor, es que no lee nadie y el valor desaparece. La medida aislada no
puede ver eso porque no conoce las otras capas.

### Lo que se hizo en su lugar

Se atribuyo cada una de las 97 diferencias observadas de punta a punta al patron
responsable (0 quedaron sin dueno) y se conservo SOLO el que no rompe nada por si mismo:

```
38 patrones no causan ninguna perdida  -> se conservan
   10 con beneficio medible
   28 neutros hoy
54 patrones causan perdidas            -> descartados
```

Los 28 neutros se mantienen a proposito: hoy no cambian ningun valor, pero quitan la fuga
de cara a los PDFs que vengan, que es la mitad del encargo.

### Las dos correcciones aplicadas

1. **Acotar el salto.** El comodin perezoso pasa a una clase templada con dos fronteras: el
   punto (frase/seccion) y otra marca de polaridad (clausula). El salto de linea se permite
   a proposito: las listas de marcadores se parten a mitad por el ancho del PDF.

2. **Frontera de palabra.** EMA casaba "ema" dentro de "sistEMA" (IHQ250785: "WHO grado 1
   para sistema"). Misma familia que AXILA dentro de MAXILAR.

### Los 10 valores falsos que desaparecen

```
IHQ250339 NEUN       borraba NEGATIVO   (es POSITIVO)
IHQ250594 DESMIN     borraba POSITIVO   (es NEGATIVO)
IHQ251246 CD4, CD8   borraba NEGATIVO   (son POSITIVO)
IHQ251252 CD56, CALPONINA, EMA          (los tres al reves)
IHQ251450 CD138      borraba NEGATIVO   (es POSITIVO)
IHQ251501 TTF1       borraba NEGATIVO   (es POSITIVO)
IHQ260254 CDX2       borraba NEGATIVO   (es POSITIVO)
```

En estos casos la BD ya tenia el valor bueno porque otra capa pisaba al patron con fuga.
Lo que se corrige es que el extractor deje de producir la lectura falsa.

### Lo que sigue abierto

Los **54 patrones descartados** siguen con la fuga. No se tocan porque acotarlos, hoy, borra
mas de lo que arregla: el valor correcto sale de ese mismo patron aunque lea por el camino
equivocado. Arreglarlos de verdad pide cubrir antes la frase con un patron NUEVO que lea
bien, y solo despues acotar el viejo. Es trabajo aditivo, no de recorte.

---

## [6.9.97] - 2026-08-27 — Fuga de polaridad entre frases: localizada, medida y acotada en LCA

**Impacto en produccion: NINGUNO.** Se dice primero para que nadie lo lea al reves.
La columna que se arregla, `IHQ_LCA`, esta VACIA en las 22.547 filas y en 0 registros del
modelo relacional: `map_to_database_format` la descarta al guardar. Lo que aqui se corrige
es un defecto latente y, sobre todo, lo que aparecio al investigarlo.

### El defecto

El cuarto patron de `BIOMARKER_DEFINITIONS['LCA']` llevaba un `.*?` SIN acotar, y el bloque
se compila con `re.DOTALL`. Resultado: se anclaba en cualquier "positivo/negativo ... para"
del documento entero y saltaba hasta el primer CD45, cruzando secciones.

En IHQ250166 se anclaba en las palabras "POSITIVO PARA TUMOR" — de la historia clinica, que
ni siquiera es un resultado de inmunohistoquimica — y se tragaba 419 caracteres pasando por
encima de DESCRIPCION MICROSCOPICA hasta el CD45. Disparaba asi en 18 de los 20 casos en que
`IHQ_LCA` e `IHQ_CD45` se contradecian.

```
patron actual, medido sobre 43 casos:  17 aciertos / 20 fallos  =  46%
```

Peor que una moneda, sobre un anticuerpo que es el mismo que CD45 con su nombre antiguo.

### El arreglo, y por que asi

Se acota el salto con dos fronteras, igual que hizo V6.6.6 con el patron hermano dos lineas
mas arriba (mismo bloque, mismo remedio, precedente documentado):

- el **punto**, frontera de frase/seccion — es lo que dejaba cruzar a la microscopica;
- **otra marca de polaridad**, frontera de clausula, para el caso muy frecuente
  "positivas para A, B, siendo negativas para C, CD45" (ahi CD45 es NEGATIVO).

El salto de linea SI se permite, a proposito: las listas de marcadores se parten a mitad por
el ancho del PDF, y prohibirlo dejaba el patron mudo en 19 casos. Se midieron cuatro
variantes ANTES de escribir nada:

```
variante                              acierta  falla    %
sin acotar (la actual)                     17     20   46%
bloquea salto de linea y punto             23      1   96%   (pero calla en 19)
bloquea punto y polaridad   <-- ELEGIDA    30      2   94%
bloquea solo el punto                      22     10   69%
```

La ultima fila es la que importa: sin la guarda de polaridad se queda en 69%. Lo decisivo no
es el punto, es no cruzar un cambio de signo.

### Regresion

```
FAM5 -> LCA97     2 ganados   8 perdidos   11 cambiados
```

**Las 21 diferencias caen TODAS en `IHQ_LCA`.** Ninguna otra columna se movio: la contencion
es total. Verificado uno a uno contra el informe:

- los 11 cambiados son 11 correcciones POSITIVO → NEGATIVO, todas correctas;
- de los 8 perdidos, 4 eran valores ERRONEOS que desaparecen (bien), 2 eran correctos pero
  `IHQ_CD45` ya los cubre, y 2 dejan hueco real (IHQ250368, IHQ251308);
- 1 ganado es correcto y **1 es un error nuevo** (IHQ250078): el patron lee bien
  ("positivas para CD45" → POSITIVO) pero el valor final sale NEGATIVO de otra capa. Se deja
  anotado en vez de taparlo.

Neto: 11 aciertos contra 1 error, en una columna que nadie lee.

### Lo que aparecio al investigar (esto si importa)

Ese `.*?` sin acotar NO es exclusivo de LCA. Un escaneo de `BIOMARKER_DEFINITIONS` encuentra
**179 patrones con la misma forma**, de los cuales **91 fugan** entre frases en el corpus,
sobre **56 columnas VIVAS** (P63, S100, PAX8, CD34, TTF1, CDX2, CD30, SINAPTOFISINA, EMA,
CKAE1AE3...). El 36% de sus disparos cruza un punto.

Antes de dar la alarma se midio lo unico concluyente — si la fuga LLEGA al valor guardado — y
la respuesta tranquiliza: de 881 disparos con fuga, 478 "contradicen" la BD, pero al leer los
informes **la BD tiene lo correcto y el patron lo incorrecto**. El patron fuga, pero PIERDE:
otra capa (narrativo directo, generico, "no hay marcacion") lo pisa. Es coherente con el
98-100% verbatim de la auditoria.

No se concluye que sea inofensivo: en LCA GANABA, y por eso habia 20 lecturas invertidas. Los
~450 valores de polaridad invertida que se corrigieron con la IA local son compatibles con que
gane de vez en cuando.

**No se ha tocado ni uno de esos 91.** Arreglarlos en bloque es exactamente lo que la Regla
Critica #1 prohibe, y ya hubo un intento generico revertido por mover 206 valores. El camino
es una campana por marcador, uno a uno con el banco.

Candidato siguiente: **EMA** (lineas 1855-1856), que acumula DOS defectos — la fuga y la falta
de frontera de palabra, que le hace casar "ema" dentro de "sistema" (IHQ250785: "WHO grado 1
para sistema"). Misma familia de errores de subcadena que AXILA dentro de MAXILAR.

### Hueco de vocabulario, independiente de todo lo anterior

Los 2 casos que quedan sin cubrir lo estan porque NINGUNA columna reconoce la frase:

```
IHQ250293  "una expresion para CD 45, CD 20, CD 79A"          -> POSITIVO, se pierde
IHQ251308  "Tampoco presenta marcacion para ... CD38 y CD45"  -> NEGATIVO, se pierde
IHQ250368  "Sin imnunoreactividad para CD45"                  -> NEGATIVO (y ojo: el
           informe escribe "imnuno", con la n y la m cambiadas)
```

"expresion para X", "Tampoco presenta marcacion para X" y "Sin inmunoreactividad para X" son
formas de frase generales: afectan a TODOS los biomarcadores, no solo a CD45.

---

## [6.9.96] - 2026-08-27 — Cinco familias de frase: 80 recuperados, 16 polaridades corregidas

Con 6.000 casos en la base, los incompletos se estabilizaron en torno al 6-9%. Un triaje
por CLAUSULA (no por ventana de caracteres) separo lo que es hueco del informe de lo que
es fallo nuestro, y lo segundo resulto ser CINCO formas de frase que ningun patron cubria.

```
BASE6000 -> FAM5     +80 ganados   0 perdidos   16 cambiados
```

Los 16 cambiados se verificaron UNO A UNO contra el informe: 15 son correcciones
inequivocas y 1 es un criterio razonado (ver abajo).

### El triaje, primero

La herramienta anterior preguntaba «.hay una palabra de resultado a menos de 130
caracteres?». Eso confunde la lista de solicitud con un resultado: marcaba 28 de 33
como fallo cuando eran ~20. La v3 mira que rodea a CADA mencion. Medida contra 22
marcadores leidos a mano del PDF:

```
precision sobre FALLO   11 de 11   100%    ninguna falsa alarma
recall                  11 de 14    79%
```

El sesgo es deliberado: falla POR DEFECTO. Se le escapa algun fallo real, pero nunca
manda a arreglar algo que no esta roto. Y en el examen **encontro dos errores mios**:
casos que yo habia clasificado como «solo solicitud» leyendo un fragmento, cuando el
informe traia mas adelante una clausula con resultado.

### Las cinco familias

**1. La polaridad va DETRAS de la lista.** «E-CADHERINA, P120 y Betacatenina con
marcacion membranosa positiva.» Todos los patrones vivos esperan «positivas PARA X».
La revision cambio la clase negada de 120 caracteres por una lista de TOKENS: la clase
negada se tragaba saltos de linea y sujetos NO tumorales («En el estroma adyacente,
SMA…»), atribuyendo al tumor marcaciones que no son suyas.
Guarda clave: tras la polaridad se exige FIN DE ORACION. El nucleo «con marcacion
positiva» sale 81 veces en el corpus y en 74 (91,4%) la lista va DETRAS — sin ese
terminador el patron INVERTIRIA esas 74. El rechazo ES el arreglo.

**2. «no muestra marcacion para X ni Y».** Cuatro huecos que se suman: el verbo
«muestra», la preposicion «de», el separador « ni », y una coletilla que impedia
normalizar «CK34BETA12 para celulas basales».
La revision RECHAZO la politica de escritura: sin `not in results` el bloque pisaba 25
valores, dos de ellos dano verificado en informes de DOS especimenes (negativo en A,
positivo en B; sobrescribir destruia B).

**3. «La expresion de A, B y C es parcheada».** Se le quitaron cinco ramas del
vocabulario (heterogenea, difusa, focal, granular, perinuclear): **no disparan ni una
vez** en los 2.077 informes y cuando lo hacen, hacen dano.

**4. «presentan inmunorreactividad para <lista>» en positivo.** Incluye la ortografia
de UNA r. La V6.9.94 arreglo el lado negativo pero el positivo se revirtio porque
degradaba calificadores. Aqui se consigue la ganancia con un patron nuevo especifico,
sin tocar los 13 patrones del lado positivo. Aditividad verificada BYTE A BYTE: el
fuente original queda entero dentro del resultado.

**5. Sueltos, y una trampa clinica.** «Sin perdida de expresion para CD7» NO es un
negativo: *sin perdida* significa CONSERVADA. Un patron ingenuo escribiria lo contrario.

### Las 16 correcciones

Las tres que mas importan, todas polaridades invertidas que estaban guardadas al reves:

```
IHQ250993 · ATRX          'NEGATIVO (perdida)' -> 'POSITIVO (conservada)'
   informe: "sin perdida de la expresion de ATRX"  ·  "ATRX NO MUTADO"
IHQ260279 · ATRX          'NEGATIVO'           -> 'POSITIVO (conservada)'
   informe: "sin perdida de la expresion de ATRX y con sobreexpresion de p53"
IHQ251204 · CD34/CD56/SMA 'POSITIVO (fuerte y difusa)' -> 'NEGATIVO'
   informe: "SMA, CD56 y CD34 con marcacion negativa esperada"
```

Y una que arregla DOS bugs a la vez: `IHQ251212 · WT1` pasa de
`POSITIVO (PATRON SALVAJE)` a `NEGATIVO`. El informe dice «No muestran
inmunoreactividad para CEA y WT1. El p53 presenta expresion de tipo salvaje» — el
calificador de p53 se habia pegado a WT1.

Tres mas eran basura estructural: `'E INHIBINA CON'`, `'NI PROGESTERONA'`,
`'ES PARCHEADA'` — frases sueltas guardadas como si fueran el valor.

### El unico discutible

`IHQ260685 · BCL2` pasa de POSITIVO a NEGATIVO. El informe afirma las dos cosas:
«centros germinales … sin expresion de Bcl-2» y «linfocitos T … con clara expresion de
CD3 y Bcl-2». En el estudio de un linfoma folicular lo diagnostico es el centro
germinal y los linfocitos T son control interno, asi que NEGATIVO parece lo correcto.
Pero es un criterio, no una lectura literal. Queda anotado por si el patologo discrepa.

### Lo que NO se aplico

Ninguno de los cinco patrones entro tal y como se diseno: **los cinco revisores
rechazaron la version original** y entregaron una endurecida. Uno lo resumio asi: «no
puedo refutar su medida, pero rechazo el entregable» — media bien y dejaba abiertos
canales de falso positivo.

## [6.9.95] - 2026-08-25 — Una sola letra: 35 biomarcadores recuperados y 4 polaridades corregidas

Tras procesar 796 casos mas, quedaron 45 incompletos. Un triaje determinista sobre los
debug_maps los separo en tres cubos: 5 marcadores que el informe **no nombra**, 7 que
solo aparecen en la lista de **solicitados** (ahi `N/A` es la respuesta correcta) y **47
nombrados CON resultado que se perdian**. Solo el tercero es trabajo.

Cinco agentes diagnosticaron una familia cada uno y una segunda ronda intento
refutarlos. **Rechazaron 3 de los 6 arreglos propuestos**, uno de ellos porque invertia
la polaridad de 20 marcadores. Lo que sigue es lo que sobrevivio y ademas paso el banco.

```
BASE995 -> FIX10     +35 ganados   0 perdidos   4 cambiados
```

Los 4 cambiados son correcciones, no danos (ver abajo).

### 1. Un candado ortografico de UNA letra — 27 patrones, 123 casos

Los informes escriben «inmuno**r**eactividad», con una r. Veintisiete patrones del
extractor exigen **dos**. En IHQ250277 eso dejaba sin procesar una lista de 18
marcadores.

Lo que lo convierte en anecdota del proyecto: el comentario de cabecera de ese patron
dice `V6.5.93 FIX IHQ250277`. **Se escribio para este caso exacto y no ha llegado a
ejecutarse ni una vez.**

Se amplia la ortografia a un superconjunto (`inmunorr?eactiv`) en las **14 lineas del
lado negativo**. Aditivo por construccion: lo que casaba antes casa igual.

Resultado: **+14 valores y 4 correcciones**, todas en IHQ250277:

```
IHQ_ALK           POSITIVO -> NEGATIVO
IHQ_CALRETININA   POSITIVO -> NEGATIVO
IHQ_P63           POSITIVO -> NEGATIVO
IHQ_P40_ESTADO    'POSITIVO (POSITIVA PARA: CD34 FOCAL, VIMENTINA...)' -> NEGATIVO
```

El informe dice «no presentan inmunoreactividad para: ... ALK 01, ... p63, ...
Calretinina». Estaban **invertidas**. La cuarta tenia una frase entera dentro del campo.

**Se probo extenderlo a las 13 lineas del lado positivo y se REVIRTIO.** Ganaba 2 y
arreglaba otro campo con basura, pero **degradaba 5**: `POSITIVO (marcacion
heterogenea)` se quedaba en `POSITIVO`. La polaridad seguia bien, pero el matiz clinico
no es adorno. Sin el banco de 995 casos no se habria visto.

### 2. Un patron hermano con dos puntos — 19 valores de un solo caso

El patron «No presentan expresion **para** [lista]» exige la palabra *para*. IHQ250880
escribe «No presentan expresion **a:** [lista]» y perdia los 19 marcadores de golpe.

Se anade un patron hermano detras, con el original intacto. Exigir los dos puntos es lo
que lo hace seguro: casa **1 caso de 2.078**.

⚠️ La clase de caracteres es `[óo]` (o-con-tilde y o), no `[oo]`. Ese typo estaba en la
propuesta original y cuesta 2 marcadores (CD56 y GATA3), que viven precisamente en la
ocurrencia acentuada, la de la lista mas larga.

**+19 ganados, 0 perdidos, 0 cambiados.**

### 3. El carril prefijado — con cinco candados

`narrative_biomarkers` devuelve claves MEZCLADAS: los patrones que trocean listas emiten
la clave ya con `IHQ_` delante y el resto el nombre pelado. El enrutado solo entiende
las peladas, asi que un valor **bien calculado, que sobrevive a las dos guardas**, se
tira al final porque su columna no tiene autoentrada en `biomarker_mapping` — y **112 de
135 no la tienen**.

🛑 La version obvia («si empieza por IHQ_, escribela») esta MEDIDA y es peligrosa: sobre
56 casos da **30 cambios con 15 polaridades invertidas**. Tampoco vale anadir la
autoentrada al dict: esa via no admite abstencion y escriben las dos claves, ganando la
ultima segun el orden de insercion.

Se anade un `elif` con lista blanca y cinco condiciones, la quinta de ellas no estetica:
**solo escribe NEGATIVOs**, porque el carril prefijado produce POSITIVOs contaminados
(el patron generico no corta en «sin marcacion para»). Un miogenina+ falso apunta a
rabdomiosarcoma: el coste de un falso positivo aqui no es simetrico.

**+2 ganados, 0 perdidos, 0 cambiados.** Cierra IHQ250414, que se habia resistido a
tres intentos.

### Un callejon sin salida que merece quedar escrito

Se diagnostico que «miogenina» se perdia porque `name_mapping` la enviaba a
`IHQ_MIOGENINA` (columna muerta, 0 valores) en vez de a `IHQ_MYOGENIN` (13). Encajaba.
Se aplico: **0 diferencias sobre 995 casos**. Motivo: `_col_canonica()` ya redirige
`IHQ_MIOGENINA -> IHQ_MYOGENIN` al final del pipeline. La ruta nunca estuvo rota, y el
valor se perdia mas adelante, en el carril prefijado. Revertido, con una nota en el
codigo para que nadie vuelva a «arreglar» eso.

### Lo que queda abierto

 · Truncamiento en `biomarker_extractor.py:7549` (46 casos). Trampa medida: relajar el
   terminador a secas **empeora** el caso, porque hoy `
(?=[A-Z]{2,})` es lo unico que
   hace encajar el patron.
 · Grafias sueltas: `CYCLINAD1`, `B-CATENINA`, `ACE`->CEA.
 · Frases sin cubrir: «presentan inmunorreactividad para», «la marcacion es homogenea
   ... para».
 · La lista blanca del carril prefijado tiene 2 entradas de las 112 posibles. Ampliarla
   exige volver a medir: el carril no es de fiar en general.

## [6.9.94] - 2026-08-25 — Patrones de biomarcador: 3 valores recuperados, 0 regresiones

Los 199 casos del reproceso salieron con 3 casos incompletos. Ninguno era un biomarcador sin dar de alta: los tres estaban registrados y FUNC-03 los rechazaba con `ERROR_YA_EXISTE`. Lo que fallaba eran los patrones de lectura, y cada uno por un motivo distinto.

### Validación antirregresión

En vez de los 3-5 casos de referencia que pide la Regla Crítica #1, se montó un banco con **los 199 casos del corpus**: el texto sale de `data/debug_maps` (`ocr.texto_consolidado`, el segmento exacto que vio el extractor, sin releer un PDF) y la IA de polaridad se apaga vía `_IA_POL_CACHE`. Una corrida completa tarda **71 s**, así que cada cambio se midió entero antes de pasar al siguiente.

```
ANTES                 1569 valores
FIX1 miogenina        +1   0 perdidos  0 alterados
FIX2 caldesmón        +1   0 perdidos  0 alterados
FIX3 e-cadherina      +1   0 perdidos  0 alterados
FIX4 letra suelta      0   0 perdidos  0 alterados
─────────────────────────────────────────────────
acumulado             +3   0 perdidos  0 alterados
```

Los 3 valores recuperados coinciden exactamente con los que se habían corregido a mano leyendo el PDF, y sobreviven a la capa de IA y a la guarda de cita verbatim con la configuración de producción.

### 1. `miogenina` en español no se reconocía — IHQ250140

`_ALIAS_PDF` tenía la clave `MIOGENINA`, pero el código consulta `_ALIAS_PDF.get(base)` con `base` sacado de la **columna**, y la columna viva es `IHQ_MYOGENIN` (`IHQ_MIOGENINA` existe pero está a 0). El vocabulario de MYOGENIN quedaba en `['MYOGENIN']` y un informe que escribiera «miogenina» se perdía. Medido: en la misma frase, `MyoD1` salía y `miogenina` no.

Se **añade** la clave correcta; la vieja se deja intacta. De las 5 claves huérfanas del mismo tipo (`CKAE1E3`, `KI67`, `CHROMOGRANINA`, `SYNAPTOFISINA`, `MIOGENINA`), las otras 4 son inocuas: su columna real ya tiene esos alias por `BIOMARKER_DEFINITIONS`.

### 2. La tilde rompía el caldesmón — IHQ250140

El mapa de nombres de `normalize_biomarker_name` se consulta por **igualdad exacta de cadena**, sin normalizar tildes. Tenía `CALDESMON`, `H-CALDESMÓN` y `H CALDESMÓN`, pero no `CALDESMÓN` a secas — y así es como lo escribe el informe. Medido: la misma frase con `caldesmon` daba POSITIVO y con `caldesmón` nada.

Irónicamente el arreglo V6.4.14 ya atacó **este mismo caso** y añadió la forma suelta… sin tilde.

### 3. `POSITIVO` pegado al nombre anulaba la lista — IHQ250128

El informe repite la polaridad dentro de la lista:

```
"son positivas para E-CADHERINA POSITIVO FUERTE Y DIFUSO EN UN 80%"
```

El regex captura bien la lista; el limpiador quita `FUERTE`, `DIFUSO` y `EN UN 80%` pero deja `POSITIVO`, así que a `normalize_biomarker_name` llegaba `E-CADHERINA POSITIVO` y se rechazaba. **No es cosa de la e-cadherina**: `SMA POSITIVO ...` también se perdía.

Se añade un fallback al final de la función que quita el sufijo de polaridad y vuelve a consultar **el mismo mapa**. No amplía el vocabulario ni un nombre — importante, porque ahí el rechazo es lo que sostiene la extracción (ver la nota V6.9.89, donde ampliarlo convirtió valores buenos en fragmentos de frase).

### 4. Alias de una sola letra casaban con media frase

Hallazgo colateral del barrido. KAPPA y LAMBDA declaran `K` y `L` como nombres alternativos (los símbolos κ y λ), y `_regex_marcador` los convertía en `\bK` y `\bL`, que casan con **cualquier palabra que empiece por esa letra**. Medido: LAMBDA constaba como «mencionado» en 190 de 199 casos y KAPPA en 79, con lo que la guarda de veracidad nunca podía descartar un valor suyo. Ya hay una víctima en la BD:

```
IHQ_KAPPA = 'POSITIVO (NO SE OBSERVA MARCACIÓN PARA CADENAS LIVIANAS KAPPA)'
```

Se exige frontera también al final **solo para alias de 1 carácter**; el resto queda idéntico. Es la misma familia que AXILA dentro de MAXILAR.

⚠️ Este cambio **no arregla ningún valor existente** (0 ganados, 0 perdidos): los 9 valores de lambda/kappa del corpus sí están nombrados de verdad. Cierra el agujero para lo que venga, y no toca la polaridad de esa fila mala, que es otra guarda.

### 5. La familia entera de tildes — hallazgo de la revisión adversarial

Tres agentes independientes localizaron las mismas causas raíz, y uno midió que el
arreglo 2 dejaba **la familia abierta**: el mapa se consulta por igualdad exacta,
así que cada clave necesita su gemela acentuada escrita a mano, y faltaban varias
que solo se ven cuando un informe las escribe:

```
ACTINA_MUSCULO_ESPECIFICA      ACTINA-MUSCULO-ESPECIFICA
ACTINA_MUSCULO_LISO            ACTINA-MUSCULO-LISO
ACTIMINA DE MUSCULO LISO       ANTIGENO LEUCOCITARIO COMUN
```

Y «actina de músculo específica» aparece en casi todos los informes.

Se añade un fallback general que reintenta sin tildes **sobre el mismo mapa**.
Verificado parseando el fuente con `ast`, no fiándose de la lista ajena:

```
claves únicas          447
con tilde o eñe         23
COLISIONES               0   ninguna pareja colapsa a destinos distintos
ganan tolerancia       266
```

`ANTÍGENO LEUCOCITARIO COMÚN` → `CD45` y `ACTINA_MÚSCULO_ESPECÍFICA` →
`ACTINA_MUSCULO_ESPECIFICA` ya resuelven. Y `CD34 (focal)` **sigue devolviendo
None**: el vocabulario no se amplió, que era el riesgo grave de la nota V6.9.89.

0 ganados y 0 perdidos en el corpus: estos 199 informes escriben las formas sin
tilde. Es preventivo, para los 50 tomos que faltan.

### Lo que queda sin cerrar

**El corpus de validación son 199 casos, no los 2.076 de antes** — esa BD se borró
y se reconstruyó. Un revisor simuló un arreglo alternativo contra el corpus viejo y
encontró casos como `IHQ250659 IHQ_E_CADHERINA` con valor rico
(`POSITIVO FUERTE Y DIFUSO EN UN 70%`) que ese arreglo degradaba a `POSITIVO`. Ese
arreglo **se rechazó** y no es el que está aquí. Pero conviene saberlo: el camino
narrativo sobrescribe con prioridad, y no puedo descartar con 199 casos lo que se
midió sobre 2.076. Comprobado de frente: con el arreglo actual, tanto
`E-CADHERINA: POSITIVO FUERTE Y DIFUSO EN UN 70%` como su forma de lista dan
`POSITIVO` — el mismo valor que daba el camino existente, así que no hay degradación
**relativa** al comportamiento previo.

También sigue abierta la asimetría de tildes en la rama de reserva
(`nombres_alternativos` escaneados con `...` sin normalizar): no rompe nada,
pero tampoco rescata.

### Lo que NO se tocó

`IHQ250007` sigue incompleto y es correcto: el informe pide 13 marcadores y reporta 12. La sinaptofisina —escrita `synaptofisina`— solo aparece en la lista de solicitados. `N/A` es la respuesta buena; el hueco es del informe, no del extractor.

## [6.9.92] - 2026-08-04 — «Ver comentario»: 2 diagnósticos recuperados y 29 que deben quedarse así

Se pidió arreglar los 31 diagnósticos atrapados en «VER DESCRIPCIÓN MICROSCÓPICA Y COMENTARIO». Leídos los 38 casos que contienen esa frase, uno a uno y con refutación adversarial: **solo 2 eran recuperables**.

### En 29 casos, «ver comentario» es la respuesta correcta

El comentario del patólogo no contiene un diagnóstico: contiene la explicación de por qué no lo hay.

```
IHQ250616  «NO SERÁ POSIBLE DETERMINAR UNA CONCLUSIÓN DIAGNÓSTICA»
IHQ250786  «hallazgos SUGESTIVOS PERO NO DIAGNÓSTICOS de micosis fungoide»
IHQ260258  «NO ES POSIBLE DETERMINAR DE MANERA CONFIABLE QUE CORRESPONDAN A UN ADENOCARCINOMA»
IHQ260513  «HUBO AGOTAMIENTO DEL TEJIDO POR LO QUE EL ESTUDIO NO ES CONCLUYENTE»
IHQ250578  «ESTUDIOS ... EN CURSO, SE REPORTARÁN EN UN INFORME ADICIONAL»
```

**Rellenarlos habría sido inventar una certeza que el informe se niega a dar** — exactamente por lo que se desactivó la capa de IA de diagnóstico. `SUGIERE`, `FAVORECE` y `PUEDE CORRESPONDER` son hipótesis, no conclusiones.

| | casos |
|---|--:|
| el patólogo DECLINA diagnosticar | 20 |
| ya traían diagnóstico (el «ver comentario» era un sufijo) | 7 |
| el informe solo escribe el rótulo del espécimen | 4 |
| estudio PENDIENTE de otro informe | 1 |
| 🟢 **diagnóstico recuperable** | **2** |

### Los 2 recuperados

```
IHQ250491  ->  ADENOCARCINOMA INVASIVO
   « LA MUESTRA PRESENTA UN PEQUEÑO FRAGMENTO CON ADENOCARCINOMA INVASIVO »
IHQ250643  ->  CARCINOMA ESCAMOCELULAR METASTASICO
   « B. HEMI-CUELLO IZQUIERDO. LESIÓN. BIOPSIA. … CARCINOMA ESCAMOCELULAR METASTÁSICO. »
```

`IHQ250643` estaba escondido por una **cabecera de página intercalada** en mitad del diagnóstico (`… FECHA INFORME : 20/06/2025 CARCINOMA ESCAMOSCELULAR METASTASICO`). Es el problema de segmentación multipágina que ya conocíamos, aquí en un caso concreto.

Malignidad recalculada en los dos (se mantiene MALIGNO, coherente con el nuevo dx).

### Los refutadores evitaron tres datos falsos

De 13 casos que un primer lector dio por concluyentes, **8 se cayeron**, y el motivo importa:

- `IHQ251041` — la cita era el **diagnóstico del laboratorio externo** que remitió el bloque, no la conclusión de este estudio. Y era factualmente falsa: proponía «parénquima renal sin alteraciones glomerulares» cuando el informe reporta esclerosis global en 1 de 6 glomérulos.
- `IHQ250899` — el diagnóstico propuesto estaba **ensamblado desde la cabecera del informe remitente**, que además pedía IHQ «para su adecuada clasificación».
- `IHQ250643` — la cita venía de la **descripción microscópica**, no del comentario; el refutador la tumbó y de paso encontró el diagnóstico verbatim de verdad, que es el que se escribió.
- `IHQ251241` y `IHQ251459` — la BD **ya guardaba el diagnóstico completo**; la propuesta lo habría sustituido por una paráfrasis.

### Por qué NO se tocó el extractor

La tentación era una regla «si el diagnóstico dice ver comentario, lee el comentario». Con estos datos, esa regla habría escrito **20 diagnósticos falsos** para ganar 2 verdaderos. No se implementa: el criterio para distinguir «FAVORECEN un glioma» de «CORRESPONDE A un adenocarcinoma» es comprensión de la frase, no un patrón.

```
casos IHQ sin diagnóstico útil : 31 -> 29
filas rojas, ambos caminos     : 56 y 56, diferencia 0
```

---

## [6.9.91] - 2026-08-04 — Auditoría del informe estadístico PDF contra los 765 PDFs

Tras 12 versiones tocando datos (columnas unificadas, 14 valores de IDH corregidos, 139 biomarcadores recuperados, 80 solicitudes fantasma retiradas), había que comprobar que el informe que se enseña sigue diciendo la verdad. **No se cambió nada: se verificó.**

### La aritmética es exacta

Cada cifra recalculada desde cero, sin usar el generador:

| | informe | recalculado |
|---|--:|--:|
| Total casos | 2.076 | **2.076** |
| % Malignos | 67,1 % | **67,1 %** |
| Categorías anatómicas | 195 | **195** |
| Biomarcadores distintos | 122 | **122** |
| Tumores analizados | 1.566 | **1.566** |
| Periodo | 07/01/2025 – 02/06/2026 | **idéntico** |

Y la tabla de cobertura **reconcilia al total**: 1.566 tumores + 436 no-neoplásicos + 74 sin diagnóstico = 2.076. El desglose por sexo también: 804 + 1.268 + 4 = 2.076, con sus porcentajes de malignidad correctos uno a uno.

### Contra los PDFs

```
diagnósticos guardados que están LITERALES en su PDF : 2.034 / 2.076   (98,0 %)
 + reformulados (todas sus palabras están en el PDF) :    37           (99,8 %)
 sin respaldo claro                                  :     5           ( 0,2 %)
```

Los 5 quedan anotados; cuatro son cuestión de acentos y saltos de línea, y el quinto (`IHQ250835`) es uno de los 31 casos cuyo diagnóstico quedó en «VER DESCRIPCIÓN MICROSCÓPICA Y COMENTARIO» — el informe sí trae el diagnóstico, en el comentario.

### Lo que el informe no puede enseñar

**42 de los 74 casos «sin diagnóstico específico» están marcados MALIGNO.** No es una incoherencia: son estudios IHQ *complementarios* cuya línea de diagnóstico reporta marcadores o celularidad —

```
IHQ250030  dx = "EXPRESIÓN DE CD117 Y CD56 NEGATIVA"      historia: "MIELOMA MÚLTIPLE"
IHQ250194  dx = "CELULARIDAD GLOBAL DEL 10 AL 20%"        comentario: "SÍNDROME MIELODISPLÁSICO"
```

— y la malignidad se derivó del contexto clínico, que sí lo dice. El informe los cuenta bien como «sin diagnóstico específico», pero **esos hasta 42 cánceres no aparecen en la tabla de diagnósticos más frecuentes**. Es una limitación de lo que se puede mostrar, no un error de cuenta.

### Tres notas menores

⚠️ **`LESIÓN BENIGNA / HIPERPLASIA` (69 casos) se cuenta como «tumor».** La etiqueta de la tabla dice «neoplasias benignas o malignas» y una hiperplasia no es una neoplasia. Es una categoría mixta heredada; separarla movería 69 casos entre dos filas del panorama.

⚠️ **3 casos con categoría no-neoplásica marcados MALIGNO** (`IHQ250850`, `IHQ251160`, `IHQ251342`). Los tres tienen dos hallazgos en la misma frase —inflamación **y** displasia de bajo grado / NIC I—: la categoría se quedó con la inflamación y la malignidad con la displasia. Ninguna de las dos es falsa. No se toca: está medido que cambiar `determine_malignancy` empeora.

⚠️ **Dos de mis tres comprobaciones daban falsos positivos y hubo que rehacerlas.** La de coherencia marcó 91 incoherencias de las que **88 eran mías**: mi patrón `MALIGN` casaba dentro de la categoría `NEGATIVO PARA MALIGNIDAD`, que es benigna. Y la de categorías exigía el término en el diagnóstico cuando el categorizador lo deriva legítimamente de **diagnóstico + órgano**, así que «CARCINOMA DE CÉRVIX» salía 8/36 sin que nada estuviera mal. La misma familia de subcadena de la V6.9.88, otra vez en mi código de verificación.

### Veredicto

El informe estadístico **es veraz**: sus cifras se sostienen contra la base y la base contra los PDFs. Lo que queda no son errores de cálculo sino los límites conocidos de la extracción — 31 diagnósticos en «ver comentario», 42 cánceres sin categoría propia y una categoría mixta.

---

## [6.9.90] - 2026-08-03 — IDH adjudicado contra el informe: 14 correcciones y la fusión desbloqueada

La V6.9.89 dejó `IDH`/`IDH1` sin fusionar porque los datos se contradecían. Adjudicados los 45 casos con IDH **leyendo el informe uno a uno**, la fusión ya está hecha.

### No eran 4 contradicciones, eran 11

El refutador encontró 4. Al barrer los 45 casos aparecieron **11 valores que dicen lo contrario que su informe**, más 3 de formato:

```
IHQ250187  BD 'POSITIVO (PATRÓN SALVAJE)'  ·  informe: "SON NEGATIVAS PARA IDH"
IHQ250376  BD 'POSITIVO'                   ·  informe: "IDH SIN SOBREEXPRESION"
IHQ250681  BD 'POSITIVO (PATRÓN SALVAJE)'  ·  informe: "EXPRESION DE TIPO WILD TYPE PARA IDH-1"   (las DOS columnas)
IHQ251259  BD 'POSITIVO'                   ·  informe: "LOS MARCADORES ... IDH ... SON NEGATIVOS"
IHQ251493  BD 'POSITIVO'                   ·  informe: "EXPRESION INTACTA, COMPATIBLE CON ESTADO NO MUTADO"
IHQ260182  BD 'POSITIVO (no mutado)'       ·  informe: "SIN EXPRESION PARA IDH1 (NO MUTADO)"
IHQ260228  BD 'POSITIVO (focal)'           ·  informe: "LA INMUNOTINCION PARA IDH1 R132H ES NEGATIVA"
```

Los valores como `'POSITIVO (PATRÓN SALVAJE)'` o `'POSITIVO (no mutado)'` se contradicen a sí mismos: en esta tinción **POSITIVO = MUTADO** y «patrón salvaje» es justo lo contrario. Varios venían de que el texto de P53 («EXPRESAN P53 TIPO SALVAJE») o de OLIG2 («POSITIVIDAD FOCAL PARA OLIG2») se derramó sobre IDH.

Todas quedan en NEGATIVO, con su cita, en `backups/backup_idh_*.json`.

### ⚠️ Un caso que no es ni positivo ni negativo

`IHQ250591` guardaba `NEGATIVO`. El informe dice:

> «IDH1 CON EXTENSO BACKGROUND QUE LIMITA LA EVALUACIÓN … **(NO CONTRIBUTIVO)**» y «EL ESTADO DE MUTACIÓN PARA IDH **NO FUE CONTRIBUTIVO** EN ESTE ESTUDIO»

La tinción **no fue evaluable**. `NEGATIVO` afirma wild-type, que es más de lo que el informe sostiene. Corregido a `NO VALORABLE`.

Y merece decirse: **mi propio clasificador determinista propuso `POSITIVO` para este caso**, engañado por la frase hipotética «para poder determinar SI corresponde a un astrocitoma IDH mutado». Habría inventado una mutación. Solo se evitó leyendo la frase entera.

### ⚠️ El clasificador falló en los dos sentidos

Además de lo anterior, marcó como «ambiguos» **4 casos inequívocos** porque su patrón de positivo `MUTACION PARA IDH` casaba **dentro** de «AUSENCIA DE MUTACION PARA IDH». Es la misma familia de errores por subcadena que el barrido de la V6.9.88: hizo falta mirar lo que va **delante** de la frase, no solo la frase.

De los 45 casos: **28 ya coincidían**, 14 corregidos, 3 de formato normalizados.

### La fusión

```
IHQ_IDH   45 -> 0 valores        IHQ_IDH1  ->  45
IDH / IDH1 / IDH-1 / ISOCITRATE DEHYDROGENASE  ->  todos a IHQ_IDH1
```

Las 6 parejas que quedaban con las dos columnas pobladas **coincidían en polaridad** y solo diferían en formato; se conserva la anotación clínica (`POSITIVO (MUTADA)`, `NEGATIVO (WILD TYPE)`). El script comprueba la coincidencia antes de tocar: si alguna hubiera discrepado, aborta.

### Verificación

```
contradicciones IDH restantes  : 0
banco del extractor            : 0 cambios FUERA del grupo IDH
modelo relacional              : CELDAS DISTINTAS 0
filas rojas, ambos caminos     : 56 y 56, diferencia 0
```

La regla que deja escrita este episodio, en `biomarcadores_canonicos.py`: **antes de fusionar dos columnas hay que comprobar que sus datos no se contradigan**, porque el merge elige ganador en silencio — y aquí la columna con más valores era la equivocada.

---

## [6.9.89] - 2026-08-03 — Un solo registro de alias: se acabó la causa de la mitad de los fallos

Las cinco tablas de alias mantenidas a mano se unifican en `core/alias_biomarcadores.py`. Es la raíz de seis fallos entre la V6.9.79 y la V6.9.88 —siempre el mismo: un arreglo aplicado en un sitio y no en su gemelo—.

```
unified_extractor      240 nombres        auditor_sistema     524
validation_checker     504                biomarker_extractor 505
columnas_huv_ia        102
                       -> 928 nombres distintos · 471 compartidos · 61 EN CONFLICTO
```

**61 nombres resolvían a columnas DISTINTAS según quién preguntara.** El auditor buscaba `IHQ_ACTINA_MUSCULO_LISO` —vaciada al unificar las actinas— mientras el verificador miraba `IHQ_SMA`: auditaba contra celdas vacías por un cambio nuestro.

### Cómo se resolvieron los 61

**50 mecánicos.** Una de las columnas no existe en el esquema o tiene 0 valores: gana la que tiene datos, sin juicio. (`CALRETININ`=0 vs `CALRETININA`=55; `CD45`=71 vs `LCA`=0; `CK56`=0 vs `CK5_6`=100…)

**11 clínicos** —6 parejas reales— leídos contra el corpus y después sometidos a un refutador que buscaba activamente un informe que los pidiera por separado:

| pareja | veredicto |
|---|---|
| mamoglobina / mamaglobina | **fusionar** → `IHQ_MAMAGLOBINA` (32 casos, 0 los listan como dos) |
| miogenina / myogenin | **fusionar** → `IHQ_MYOGENIN` (grafía castellana e inglesa) |
| glipican / GPC3 | **fusionar** → `IHQ_GPC3` (siempre el mismo panel hepático) |
| ALK / ALK-1 | **fusionar** → `IHQ_ALK` (ALK1 es el clon comercial del anti-ALK) |
| S100 / SOX10 | **separadas** — anticuerpos distintos |
| IDH / IDH1 | **fusión BLOQUEADA** — ver abajo |

`S100` y `SOX10` se piden y reportan por separado en el mismo panel («NEGATIVA PARA CK7, GAFP, SOX10, RECEPTOR DE PROGESTERONA Y S100»), y el patrón S100+/SOX10− es lo que discrimina lesión melanocítica. El alias `SOX100` que las enfrentaba era una errata: resuelve a `IHQ_SOX10`.

### ⚠️ El refutador paró una fusión que parecía obvia

`IDH` e `IDH1` **son** clínicamente el mismo anticuerpo (anti-IDH1 R132H). Aun así la fusión no se ejecutó: hay **4 casos donde las dos columnas se contradicen** (`IHQ250993`, `IHQ260182`, `IHQ260253`, `IHQ260279`) y, contrastados con el texto, **la columna con MÁS valores —la que se proponía como canónica— es la equivocada en 3 de los 4**:

```
IHQ260182  el informe: "SIN EXPRESION PARA IDH1 (NO MUTADO)"   ·  la BD: IHQ_IDH='NEGATIVO (MUTADO)'
IHQ260279  el informe: "SIN MARCACION PARA IDH (NO MUTADO)"    ·  la BD: IHQ_IDH1='POSITIVO'
```

Fusionar habría elegido ganador en silencio y cementado el valor falso. Y aquí IDH mutado frente a no mutado separa **ASTROCITOMA IDH-MUTANTE de GLIOBLASTOMA IDH-WILDTYPE**: grado y pronóstico OMS. Queda bloqueada con su razón escrita en el código hasta adjudicar esos 4 casos.

### ⚠️ Dónde NO se enchufa el registro, y por qué

El primer cableado lo puso también en `normalize_biomarker_name`, del extractor. Medido:

```
IHQ250011 · ER : 'NEGATIVO' -> ', CD68 Y PAX-8'
IHQ250005 · PR : 'NEGATIVO' -> 'Y WT1 NEGATIVOS'
IHQ250040 · PR : 'NEGATIVO' -> 'Y S100'
```

**Revertido.** Ahí el rechazo *es un filtro que sostiene la extracción*: devolver `None` ante un nombre desconocido es lo que descarta los fragmentos de frase que los patrones capturan por error. Al ampliar el vocabulario a 855 nombres, esos fragmentos pasaron a ser marcadores válidos y se quedaron con el texto como valor.

El registro manda donde un lookup de más es inocuo —el verificador y el auditor, que solo eligen **dónde mirar**— y no donde se decide **qué se acepta**. La distinción está escrita en ambos ficheros.

### Verificación

```
resolver / verificador / auditor sobre los 16 nombres que discrepaban : 0 discrepancias
banco del extractor, 2.076 casos : 0 cambios FUERA de los grupos fusionados
modelo relacional                : CELDAS DISTINTAS 0 · reconstrucción exacta
filas rojas, ambos caminos       : 59 y 59, diferencia 0
```

Consolidados además los datos de las 4 fusiones: 16 valores movidos a su canónica, 20 celdas alias vaciadas, 1 conflicto adjudicado contra el informe (`IHQ250988`, «No tienen expresión de ALK1» → NEGATIVO, que es lo que ya tenía la canónica).

### Para los PDFs futuros

Un alias nuevo se declara **una vez** en `core/alias_biomarcadores.py` y lo ven todos los consumidores. Ninguna tabla local puede volver a contradecir a otra, y todo destino pasa por `canonico()`, así que ninguna entrada puede apuntar a una columna alias ya vaciada.

---

## [6.9.88] - 2026-07-29 — Barrido de selección por subcadena: 1 fallo real de 14 sitios

Barrido sistemático del patrón que ha causado la mitad de los fallos de esta sesión. No se juzgó leyendo el código: cada condición se **ejecutó** contra las 190 columnas reales y contra el corpus.

| familia | sitios | resultado |
|---|--:|---|
| selección de **columnas** por subcadena | 14 | **1 fallo real**, 1 falso positivo, 12 limpios |
| `.str.contains()` sin frontera de palabra | 0 | — |
| subcadena dentro de **valores** | 8 listas marcadas | todas justificadas — ver abajo |

### El fallo: la tabla de correlación de Malignidad

`update_malignancy_biomarker_table` seleccionaba con `['her2','ki67','er','pr','p16']` y casaba **17 columnas**. Inserta una fila por columna, así que la tabla mostraba:

```
fila                        M+     M-     B+     B-
Factor pronostico          282    306     88     23   <-- NO es un biomarcador
Diagnostico Principal       41     46      5     95   <-- NO es un biomarcador
Numero de caso · Servicio · Primer nombre · Primer apellido ·
Genero · Procedimiento                                <-- NO son biomarcadores (en 0)
```

`Factor pronostico` daba **los números más grandes de toda la tabla**, leíbles como una correlación clínica real.

Y en el otro sentido colaba 5 marcadores por accidente —`'er'` dentro de cadh**er**ina, per**ox**idasa, EB**ER**; `'pr'` dentro de **pr**olactina— mientras **perdía dos de los cinco que pretendía mostrar**: Ki-67 (la clave era `'ki67'` y la columna es `IHQ_KI-67`) y el receptor de estrógenos.

Ahora la declaración de los destacados vive **una sola vez** (`BIOMARCADORES_DESTACADOS`) y la usan las dos pestañas, exigiendo además que la columna sea `IHQ_`:

```
antes  17 filas (8 basura, sin Ki-67, sin ER)
ahora   7 filas · todas IHQ_ · con Ki-67 y los dos receptores
```

### El falso positivo

`update_malignancy_analysis` busca `'diagnostico'` y casa también `Descripcion Diagnostico` — pero está bien escrito: prueba primero la coincidencia **exacta** `'diagnostico principal'` y solo cae a la subcadena si esa columna falta. Nunca se ejecuta. Se deja como está.

### Lo que NO se tocó, y por qué

Las 8 listas que buscan subcadenas dentro de valores están **justificadas**: encontrar `'ESTROGENO'` dentro de «RECEPTOR DE ESTROGENOS» es precisamente el objetivo cuando se busca en prosa.

La única clave corta real es **`'HER'`** (3 letras) en dos guardas de `extract_diagnostico_principal`. Medido sobre el corpus:

```
palabras con HER en los diagnósticos:
   HER2 125 · HER 88 · HER-2 65 · HER2/NEU 23 · HER/NEU 1     -> el marcador (302)
   ADHERENCIAS 2 · HERNIORRAFIA 2 · HERNIARIO 1 · HERNIA 1    -> falsos (6)
```

**No se cambia a `'HER2'`: rompería los 88 casos donde el informe escribe `HER` a secas.** Además la guarda es de *rechazo* —descarta un candidato, no inventa un diagnóstico— y los 4 casos afectados conservan su diagnóstico correcto (`CARCINOMA SEROSO DE ALTO GRADO`, `CARCINOMA DE CÉLULAS CLARAS DE OVARIO`…). Coste real: cero.

### El patrón de fondo

De los 6 fallos de esta familia encontrados en la sesión, **ninguno era la subcadena en sí**: todos eran **una definición duplicada que divergió** — un arreglo aplicado en un sitio y no en su gemelo. La subcadena solo decide cómo de feo es el síntoma.

---

## [6.9.87] - 2026-07-29 — Repaso de las 7 pestañas: dos fallos más de la misma familia

Antes de dar por buena ninguna vista se recalculó lo que muestra cada pestaña y se contrastó contra la BD. Cinco estaban bien; dos no.

### Estadísticas Generales: «Casos con Biomarcadores» decía 1.803, son 1.984

Seleccionaba las columnas por **subcadena del nombre**, con la lista `['her2','ki67','er','pr','pdl1','p16','gata','s100','cd',…]`. Es exactamente la lista que la **V6.9.17** ya había quitado de `update_biomarker_analysis` por este motivo — el arreglo se aplicó a una pestaña y no a su gemela.

```
casaba 48 columnas · 8 NO son biomarcador:
   Numero de caso · Servicio · Primer nombre · Primer apellido ·
   Genero · Procedimiento · Diagnostico Principal · Factor pronostico
```

Y a la vez **dejaba fuera ~90 columnas de biomarcador reales**, que es de donde salía el error grande. Ahora cuenta sobre las 146 columnas `IHQ_` explícitas, igual que la pestaña hermana: **1.984 de 2.076 (96 %)** en 0,22 s.

Contrastado con SQL independiente, que da 1.987. Los 3 de diferencia dan la razón al dashboard en 2 de ellos: `IHQ250107` e `IHQ250153` tienen todos sus valores en `'NO VALORABLE'`, que no es un resultado. El tercero destapa basura en la BD: `IHQ251135 · IHQ_NAPSIN = ', CK20, Y CK19'`, un trozo de lista guardado como valor.

### Exportaciones: abrir una BD exportada mostraba una tabla sin columnas

`load_database_content` pedía `numero_peticion`, `fecha_informe`, `paciente_nombre`… — nombres de un esquema anterior que **no existen**. `available_cols` quedaba vacía y el Treeview se construía con **0 columnas**.

Está **latente, no activo**: la carpeta de exportaciones existe pero está vacía, así que solo mordería la primera vez que se exporte una BD y se abra. Corregido con los nombres reales y, si el fichero trae otro esquema, cae a sus primeras columnas en vez de no mostrar nada. Probado contra una BD real: 7 columnas.

### Lo que sí estaba bien

| pestaña | comprobación |
|---|---|
| **Visualizador de Datos** | `Nombre Completo` recuperado (V6.9.84); columnas de actina unificadas |
| **Por Paciente** | nombres, agregados, filtro y biomarcadores (V6.9.84-86) |
| **Biomarcadores** | las 5 tarjetas seleccionan **solo** columnas `IHQ_`, sin colisiones: HER2 397 · Ki-67 580 · ER/PR 420 · P16 251 · PDL-1 0 · Otros 1.766 |
| **Análisis de Malignidad** | 1.394 malignos + 682 benignos = 2.076, sin indeterminados; cuadra con el total |
| **Importar Datos** | no muestra datos: es la acción de importar PDFs |

`PDL-1 = 0` es correcto y ya estaba documentado: es de las columnas que solo se **piden** y nunca se reportan.

Las coloraciones se excluyen del dashboard (V6.9.50), por eso todo esto va sobre 2.076 filas y no sobre 22.547.

### La misma familia, otra vez

Van cinco fallos con la misma forma: **un arreglo aplicado en un sitio y no en su gemelo**, o **selección por subcadena**. `_SIN_DATO`, las columnas alias, `Nombre Completo`, el filtro por fila de Por Paciente, y ahora este. La lección se repite: cuando dos sitios calculan lo mismo, tienen que compartir la definición, no copiarla.

---

## [6.9.86] - 2026-07-29 — Biomarcadores en la fila del paciente, y el interruptor que se contradecía

### Los biomarcadores vacíos: el 90 % es correcto, el resto no lo era

| | filas de paciente |
|---|--:|
| **solo coloraciones** — una tinción básica no lleva biomarcadores | **16.368 (90 %)** |
| un único estudio y es IHQ | 353 → **338 ahora los muestran** |
| varios estudios | 1.478 → siguen vacías |

Cuando el paciente tiene **un solo estudio**, la fila no agrega nada: **es** ese estudio, así que puede mostrar sus biomarcadores sin mezclar muestras. Con varios se deja vacío a propósito — unir los marcadores de muestras distintas daría una línea contradictoria (el mismo marcador con dos resultados) además de ilegible: mediana 129 caracteres, máximo 757.

Verificado: **0 filas** donde lo mostrado no sea literalmente la línea de su único estudio.

### ⚠️ «Solo con varios estudios» podía enseñar pacientes con un solo estudio

El interruptor funcionaba solo. Combinado con el buscador, no:

```
filtro 'lucelly' + interruptor ENCENDIDO  ->  25193142 aparecía con 1 estudio (tiene 2)
filtro 'balnca'  + interruptor ENCENDIDO  ->  38987974 aparecía con 1 estudio (tiene 2)
```

El filtro se evaluaba **fila a fila**, y hay **9 pacientes con el nombre escrito distinto entre sus propias filas** (`MARIA LUCELLY` / `MARIA LUCENY`, `BALNCA` / `BLANCA`). Buscar una grafía partía al paciente por la mitad, y el interruptor —que promete justo lo contrario— lo dejaba pasar.

Ahora se **agrupa primero y se filtra el grupo entero**: si cualquiera de sus filas casa, entra el paciente completo. Además de arreglar el interruptor es mejor búsqueda — teclear un nombre con errata trae la historia entera. Y el recuento del interruptor pasa a hacerse sobre el grupo ya construido, no sobre un contador global, para que no puedan volver a discrepar.

```
ENCENDIDO, sin filtro   3.071 pacientes · con un solo estudio: 0
ENCENDIDO + 'lucelly'       2 pacientes · con un solo estudio: 0   (antes: 1)
ENCENDIDO + 'balnca'        1 paciente  · con un solo estudio: 0   (antes: 1)
```

### Rendimiento

`_bio()` recorre 146 columnas, así que llamarla para los 18.199 pacientes costaba 0,3 s de más. No se llama para coloraciones —el 90 %, y nunca tienen biomarcadores—: **1,29 s → 1,13 s** con resultado idéntico (338 filas en ambos casos).

```
vista completa        1,13 s
solo varios estudios  0,61 s
con filtro            0,43 s
```

---

## [6.9.85] - 2026-07-29 — La fila del paciente deja de ir en blanco (sin afirmar nada que el informe no diga)

En la vista Por Paciente, las columnas **Órgano, Diagnóstico, Biomarcadores y Fecha** salían vacías. No era un fallo: la fila del paciente las dejaba en blanco **a propósito**, y el motivo sigue siendo bueno —

> elegir uno de sus estudios para «representar» al paciente afirmaría algo que el informe no dice.

El problema es de lectura, no de dato: cuatro de seis columnas en blanco parecen una tabla rota, y el usuario no tiene por qué saber que hay que desplegar la flecha.

### Qué se puede decir del paciente entero sin mentir

| columna | qué muestra ahora |
|---|---|
| **Órgano** | el **conjunto** de sus órganos (`MAMA · PIEL`, y `+N` si hay más), no uno elegido |
| **Diagnóstico** | solo si **todos** sus estudios dicen lo mismo; si difieren, sigue vacío |
| **Fecha** | la más reciente — un agregado honesto |
| **Biomarcadores** | sigue vacío: son de cada estudio, y juntarlos mezclaría resultados de muestras distintas en una línea ilegible |

```
filas de paciente        18.199
   sin Órgano                 0   (antes: todas)
   sin Diagnóstico        3.066   (17 % — sus estudios discrepan, es correcto)
   sin Fecha                  0   (antes: todas)
```

### La comprobación que importa

No basta con que se rellene: hay que probar que **nada de lo que muestra el padre contradice a sus hijos**. Verificado sobre los 18.199 pacientes, comparando cada fila con la de sus estudios:

```
filas de paciente que afirman algo que sus estudios no dicen: 0
```

Coste de la agregación: **0,048 s** sobre 18.199 pacientes.

⚠️ **Se descartó normalizar el diagnóstico antes de compararlo** (quitar puntuación y tildes para dar por iguales `'- MIXOMA CARDIACO.'` y `'MIXOMA CARDIACO'`). Medido: rellenaría **20 de 3.066** filas más, un 0,7 %, a cambio de arriesgarse a fundir diagnósticos que sí difieren. No compensa.

Eso sí, destapa un detalle de datos para otro día: algunos diagnósticos de coloración vienen con un guion inicial (`'- GLIOBLASTOMA.'`) que es residuo del formato del informe.

---

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
