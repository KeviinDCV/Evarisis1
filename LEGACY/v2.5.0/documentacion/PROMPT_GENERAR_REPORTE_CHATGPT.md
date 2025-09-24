# PROMPT — Generar REPORTE_CHATGPT.md para este proyecto

Este archivo es un prompt reutilizable para que un agente (ChatGPT/Codex CLI) genere un reporte técnico-navegable del proyecto actual. Cópielo tal cual en `documentacion/` de cualquier proyecto y pídale al agente: “Lee y ejecuta PROMPT_GENERAR_REPORTE_CHATGPT.md”.

—

## Instrucciones para el agente (ejecútame)

Objetivo: crear/actualizar `documentacion/REPORTE_CHATGPT.md` con un mapa completo del proyecto (rutas, módulos, flujos, integraciones, configuración, empaquetado) que permita a ChatGPT navegar y localizar con precisión cada pieza del repositorio o del Drive asociado.

Entregables:
- `documentacion/REPORTE_CHATGPT.md` (nuevo o actualizado) con las secciones y formato indicados abajo.
- Actualizar `documentacion/README.md` para enlazar este reporte (si no está enlazado).
- Crear/actualizar `documentacion/CHANGELOG.md` con una entrada “Generado/actualizado REPORTE_CHATGPT.md” y la fecha.

Alcance y supuestos:
- Escanea el repositorio desde la raíz actual. Si existe `AGENTS.md`, respeta sus lineamientos.
- No copies secretos (tokens, contraseñas). Si encuentras claves, documenta la clave por su nombre, no su valor.
- Si el proyecto usa múltiples apps/paquetes, documenta cada una como subsección.

Estrategia (pasos sugeridos):
1) Inventario rápido
   - Lista directorios clave, archivos de entrada/salida, scripts ejecutables, configuraciones (`.env`, `config.*`, `*.ini`, `pyproject.toml`, `package.json`, `Dockerfile`, specs de empaquetado) y documentación existente.
   - Identifica módulos de negocio, UI, API/servicios, tareas por lotes, integraciones externas.
2) Derivar el mapa de responsabilidades
   - Qué hace cada componente, cómo se llama (nombre de archivo) y con qué depende.
   - Rutas de salida (artefactos, reportes generados, bundles, builds) y dónde se guardan.
3) Reconstruir flujos/pipelines
   - Para cada proceso, resume entrada → pasos → salida; nombra funciones/archivos clave.
4) Integraciones externas
   - APIs (endpoints/SDK), servicios (Notion, Google, etc.), autenticación/credenciales (sin valores), webhooks.
5) Configuración y despliegue
   - Variables de entorno/archivos de config, cómo correr local, pruebas, empaquetado (PyInstaller, Docker, etc.).
6) Redactar el reporte final siguiendo el “Formato de salida” (más abajo).
7) Enlazar desde `documentacion/README.md` y anotar en `documentacion/CHANGELOG.md`.

Formato y estilo del reporte:
- Encabezado con nombre del proyecto (si se detecta), versión (si hay), y fecha de generación.
- Usa secciones y viñetas; evita tablas pesadas.
- Rutas y archivos en backticks con rutas relativas (para ser clicables en IDE): `src/app.py`, `documentacion/README.md`.
- Estructura mínima (ajusta según proyecto):
  1. Estructura de carpetas y rutas clave
  2. Componentes y responsabilidades (mapa de módulos)
  3. Flujos/pipelines (entradas, pasos, salidas)
  4. Integraciones externas (APIs/SDKs/servicios)
  5. Configuración (archivos/variables) y seguridad
  6. Dependencias y herramientas (build/test/runner)
  7. Empaquetado/Despliegue (Docker, PyInstaller, CI/CD)
  8. Artefactos de salida y almacenamiento
  9. Convenciones de búsqueda en Drive/infra (si aplica)
  10. Glosario de archivos

Criterios de calidad:
- Precisión sobre suposiciones: no inventes. Si hay ambigüedad, indícalo como “No determinado” y referencia dónde investigar.
- Cobertura: menciona todas las piezas relevantes; enlaza a archivos reales.
- Portabilidad: evita detalles específicos de una máquina salvo que sean requeridos por el proyecto.

Plantilla de encabezado (inclúyela y rellénala):
```
# REPORTE EXCLUSIVO PARA ChatGPT — <NombreProyecto> <versión opcional> (<FECHA>)

<1 párrafo objetivo del proyecto>
```

Secciones recomendadas (plantilla de contenido):
- Estructura de carpetas y rutas clave (lista de directorios/archivos vitales)
- Componentes y responsabilidades (por archivo/módulo)
- Flujos/pipelines (entrada→proceso→salida, funciones/archivos involucrados)
- Integraciones externas (APIs/SDKs, endpoints, credenciales NOMBRADAS, no valores)
- Configuración y seguridad (qué archivos, qué claves, dónde ubicarlos)
- Dependencias y herramientas (frameworks, librerías, versiones si detectables)
- Empaquetado/Despliegue (comandos, specs, CI, contenedores)
- Artefactos y almacenamiento (carpetas de salida, nombres de archivos)
- Convenciones de búsqueda (en Drive/infra si aplica)
- Glosario rápido de archivos

Actualizaciones colaterales:
- Si `documentacion/README.md` no enlaza el reporte, añádelo en una viñeta.
- En `documentacion/CHANGELOG.md`, agrega sección con fecha:
  - “Generado/actualizado REPORTE_CHATGPT.md con el mapa del proyecto”.

Consideraciones de seguridad:
- Si detectas secretos (API keys, contraseñas), NO incluyas valores; documenta solo el nombre de la variable/clave y su propósito.
- Señala archivos sensibles para no subir a repos públicos.

Checklist de aceptación (márcalo mentalmente al terminar):
- Existe `documentacion/REPORTE_CHATGPT.md` con todas las secciones clave.
- Enlaces de archivos son rutas relativas y funcionan en el IDE.
- `documentacion/README.md` enlaza al reporte.
- `documentacion/CHANGELOG.md` registra la generación/actualización.

— Fin del prompt —

