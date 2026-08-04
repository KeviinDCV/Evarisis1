# Design spec — ONCONOVA explicativo

## Concepto

**Una sala de lectura clínica.** El documento y el dato comparten el mismo
escritorio oscuro: el informe habla en tipografía institucional, y el dato le
responde en monoespaciada. Todo el vídeo es esa conversación — prosa que se
convierte en campos.

## Paleta

Una sola familia (azul institucional del propio producto) y **un solo acento**.

| Token          | Valor                    | Uso                                                     |
| -------------- | ------------------------ | ------------------------------------------------------- |
| `--stage`      | `#141d2b`                | fondo único de todas las escenas                        |
| `--navy`       | `#2d3e5e`                | azul del producto: cromo de paneles, cabeceras, plintos |
| `--panel`      | `#f4f6fa`                | pantallas claras que flotan sobre el escenario          |
| `--panel-ink`  | `#22304a`                | texto sobre panel claro                                 |
| `--ink`        | `#e9eef7`                | texto sobre escenario                                   |
| `--muted`      | `#8296b5`                | texto secundario, etiquetas                             |
| `--accent`     | `#e9a33c`                | **el foco, y nada más**                                 |
| `--rule`       | `rgba(233,238,247,.14)`  | hairlines                                               |

Ni `#000` ni `#fff` puros. El acento ámbar no es decoración: es el subrayador
— marca el dato encontrado, la estación activa, la frase que sostiene la cifra.
Un elemento ámbar por escena, nunca dos.

## Tipografía

| Voz              | Familia            | Pesos     | Habla de                                              |
| ---------------- | ------------------ | --------- | ----------------------------------------------------- |
| La institución   | **Montserrat**     | 900 / 400 | titulares, narración en pantalla, la marca            |
| La máquina       | **IBM Plex Mono**  | 700 / 400 | nº de caso, campos, columnas, cifras, etiquetas       |

**Por qué chocan:** la institución habla en geométrica de señalética — la
tipografía de un letrero de hospital, tranquila y oficial. La máquina contesta
en monoespaciada — campos, identificadores, columnas. El vídeo trata
exactamente de convertir lo primero en lo segundo, así que la tensión
tipográfica *es* el argumento.

Ambas van embebidas por el compilador (sin fetch, sin warning de lint).

- Titulares 72–110px · cuerpo 28–34px · etiquetas de dato 18–22px
- Tracking `-0.03em` en display; `line-height` +0.05 por fondo oscuro
- `font-variant-numeric: tabular-nums` en **toda** cifra
- Peso extremo: 900 contra 400, nunca 700 contra 400

## Composición

**Foco.** Un elemento por escena lleva el ámbar y llega primero:

| Escena | Foco                                    |
| ------ | --------------------------------------- |
| 1      | el cursor que parpadea                  |
| 2      | el contador                             |
| 3      | el plinto bajo el lockup                |
| 4      | la estación activa                      |
| 5      | el campo de búsqueda                    |
| 6      | el KPI de malignidad                    |
| 7      | la página que se nombra                 |
| 8      | la frase resaltada del PDF              |
| 9      | el plinto bajo el lockup                |

**Anclas de borde.** Un esqueleto idéntico en todas las escenas: arriba a la
izquierda `ONCONOVA · Gestor Oncológico HUV` en mono; abajo a la derecha el
marcador de sección `04 / 09 — EL CIRCUITO`. **Excepción deliberada:** en las
escenas 1 y 2 la marca *no* aparece — la aplicación todavía no se ha
presentado. El esqueleto entra con el lockup en la escena 3, y ese cambio de
estado es parte del relato.

**Detalle de apoyo.** Las pantallas y el PDF se muestran como paneles claros
flotando sobre el escenario, con sombra suave y una barra de cromo navy de 1px.
Leen como «una pantalla sobre un escritorio», nunca a sangre.

**Fondo.** Escenario plano `--stage` + tres decorativos con una única
respiración lenta compartida: un radial navy muy tenue del lado del foco, una
retícula de 40px al 4% (el registro de una tabla de datos) y una hairline
horizontal a la altura del texto. Nada más.

## Audio

Colchón grave y muy bajo, continuo. Clics discretos solo en la escena 5
(interacción real). **En la escena 8 la música cae y queda la voz sola** — es
la escena de la verificación, y el silencio la subraya. Narración TTS en
español.

## Restricciones

- Ley 1581 (Habeas Data): ningún dato identificable de paciente en pantalla.
  Identidades ficticias; cifras agregadas reales.
- Todas las cifras en pantalla son las verificadas en la auditoría V6.9.91.
  Ninguna cifra se inventa para rellenar un hueco: si no está verificada, el
  bloque se muestra sin números.
