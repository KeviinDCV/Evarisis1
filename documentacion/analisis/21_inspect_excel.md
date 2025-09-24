# Analisis: scripts/inspect_excel.py

Propósito
- Facilitar la inspección rápida de archivos Excel para consumo por una IA o para revisar su estructura de forma amigable (columnas, primera fila, conteo de columnas), entregando un JSON legible por herramientas.

Ubicación
- `scripts/inspect_excel.py`

Qué hace hoy
- Busca dos archivos de ejemplo en la raíz del proyecto:
  - `EJEMPLO DE LO QUE TENGO.xlsx`
  - `BD_JULIO PARA ENSAYO IA.xlsx` (lee con `header=1` para saltar una fila de encabezado)
- Lee cada archivo si existe y construye un diccionario con:
  - `*_columns`: lista de nombres de columnas (como texto)
  - `*_first_row`: primera fila (como dict) cuando aplica
  - `*_ncols`: cantidad de columnas (según archivo)
  - `*_error`: mensaje de error o `missing` si no existe
- Imprime el resultado como JSON (UTF-8) en `stdout`.

Uso básico
```bash
python scripts/inspect_excel.py > resumen.json
```
- El archivo `resumen.json` contendrá un objeto JSON con la estructura anterior, listo para ser enviado a una IA o inspeccionado desde un editor.

Ejemplo de salida (resumido)
```json
{
  "ejemplo_columns": ["Col1", "Col2", "Col3"],
  "ejemplo_first_row": {"Col1": "A", "Col2": "B", "Col3": "C"},
  "bdjulio_columns": ["Fecha", "Peticion", "Servicio", "..."],
  "bdjulio_ncols": 55
}
```

Limitaciones actuales
- Rutas de entrada están fijas a dos archivos en la raíz.
- Sin parámetros para hoja (`sheet_name`) ni para elegir cabeceras (`header`).
- No muestra tipos de datos ni estadísticas rápidas.

Sugerencias de mejora (no disruptivas)
- Aceptar rutas por CLI: `python scripts/inspect_excel.py --file archivo.xlsx [--header 0] [--sheet Hoja1]` y permitir múltiples `--file`.
- Exportar también:
  - `shape` (filas, columnas)
  - 5 primeras filas (`head`) y 5 últimas (`tail`) opcionales con `--preview`.
  - Inferencia simple de tipos (numérico, fecha, texto).
- Controlar tamaño de salida (`--max-cols`, `--max-chars` por celda) para prompts más compactos.

Buenas prácticas al compartir con IA
- Anonimizar identificadores sensibles antes de exportar (documentos, nombres, teléfonos).
- Evitar adjuntar hojas completas si no es necesario; usar un extracto representativo.
- Mantener una “ficha técnica” del archivo (origen, fecha, responsable) junto al JSON.
