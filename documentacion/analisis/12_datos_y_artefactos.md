Datos y Artefactos del Ecosistema (v2.5)

Activos clave
- Base operativa SQLite: `huv_oncologia.db` (tabla `informes_ihq`).
- Esquema maestro HUV (167 campos) como referencia para futuras ampliaciones.
- Plantillas legacy (Excel 55 columnas) disponibles solo para comparacion en `LEGACY/`.

Fuentes primarias
- Portal de Patologia H.U.V: `https://huvpatologia.qhorte.com/index.php` (intranet).
- Descargas automatizadas via `huv_web_automation.py` (Selenium).

Fuentes de conocimiento
- CAP, Pathology Outlines, OMS (Libros Azules) para estandarizar nomenclaturas.

Carpetas y archivos relevantes
- `documentacion/`: guias, informes y comunicados.
- `LEGACY/`: version 1.x del pipeline (Excel).
- `pdfs_patologia/`: ejemplos de entrada (asegurar anonimizacion).
- `EXCEL/`: artefactos de exportaciones historicas (mantener solo como fixtures, ahora ignorado en git).
- `utilidades/binarios/`: binarios pesados movidos desde la raíz (p. ej., `sqliteodbc_w64.exe`, `PBIDesktopSetup_x64.exe`, `spa.traineddata`).

Buenas practicas
- Evitar versionar nuevos excels generados; usar exportaciones bajo demanda o adjuntar como evidencia en carpetas temporales.
- Realizar respaldos periodicos de `huv_oncologia.db` antes de pruebas masivas.
- Documentar origen y fecha de los PDFs utilizados para entrenamiento o validacion.

Actualizacion (limpieza de binarios y .gitignore)
- Se movieron a `utilidades/binarios/` binarios previamente en la raíz: `sqliteodbc_w64.exe`, `PBIDesktopSetup_x64.exe`, `spa.traineddata`.
- `.gitignore` ampliado para ignorar `EXCEL/`, `pdfs_patologia/`, `huv_oncologia.db`, `utilidades/binarios/` y `*.exe`.
- Nota sobre `spa.traineddata`: Tesseract usa su propia carpeta `tessdata`. Mantener el idioma instalado en el sistema; el archivo local es solo de referencia.
