# EVARISIS Gestor H.U.V — Análisis Técnico por Componentes (v2.5)

**Ruta raíz Drive:** `DEBERES HUV\HUV_ONCOLOGIA\HUV_ONCOLOGIA`

## Tabla de componentes

| NN | Componente | Tipo | Rol (1 línea) | Principales dependencias |
|----|------------|------|---------------|-------------------------|
| 01 | `huv_ocr_sistema_definitivo.py` | código | Punto de entrada principal, configura Tesseract y lanza UI | `ui.py`, `pytesseract`, `config.ini` |
| 02 | `ui.py` | código | Orquestación CustomTkinter con 4 vistas y dashboard analítico | `procesador_ihq_biomarcadores`, `database_manager`, `matplotlib` |
| 03 | `ocr_processing.py` | código | Motor OCR híbrido (texto nativo + Tesseract) con limpieza | `PyMuPDF`, `pytesseract`, `PIL` |
| 04 | `procesador_ihq_biomarcadores.py` | código | Extracción especializada IHQ con normalización biomarcadores | `procesador_ihq.py` (LEGACY), `database_manager` |
| 05 | `database_manager.py` | código | Gestor SQLite con esquema 167 campos y control duplicados | `sqlite3`, `pandas` |
| 06 | `huv_web_automation.py` | código | Bot Selenium para portal huvpatologia.qhorte.com | `selenium`, `webdriver-manager`, `calendario.py` |
| 07 | `calendario.py` | código | Widget calendario modal con festivos colombianos | `tkinter`, `holidays`, `babel` |
| 08 | `huv_constants.py` | código | Constantes hospitalarias y patrones de extracción | Ninguna (constantes estáticas) |
| 09 | `config.ini` | configuración | Parámetros OCR, rutas Tesseract y configuración multi-OS | Leído por `huv_ocr_sistema_definitivo.py` |
| 10 | `esquema_sqlite.md` | esquema | Esquema base datos SQLite con 167 campos estructurados | Implementado por `database_manager.py` |

## Mapa relacional (dependencias internas)

```
huv_ocr_sistema_definitivo.py → ui.py
                              → config.ini
                              → pytesseract

ui.py → procesador_ihq_biomarcadores.py
      → database_manager.py  
      → huv_web_automation.py
      → matplotlib/seaborn

procesador_ihq_biomarcadores.py → ocr_processing.py
                                → database_manager.py
                                → huv_constants.py
                                → procesador_ihq.py (LEGACY)

huv_web_automation.py → calendario.py
                      → selenium

ocr_processing.py → config.ini (parámetros OCR)

database_manager.py → sqlite3
```

## Checklist de cobertura

- ✅ **Punto de entrada**: `huv_ocr_sistema_definitivo.py`
- ✅ **Núcleo negocio**: `procesador_ihq_biomarcadores.py`, `ocr_processing.py`
- ✅ **Integraciones**: `huv_web_automation.py`, `database_manager.py`
- ✅ **Config**: `config.ini`
- ✅ **Esquemas**: Esquema SQLite documentado
- ✅ **UI/Orquestación**: `ui.py`
- ✅ **Utilidades**: `calendario.py`, `huv_constants.py`
- 🔄 **LEGACY**: Análisis pendiente de procesadores heredados

## Notas y limitaciones

### Componentes analizados
- **Cobertura completa**: 10 componentes críticos identificados con código fuente disponible
- **Documentación**: Cada componente incluye análisis técnico profundo según plantilla estándar
- **Trazabilidad**: Referencias exactas a archivos/funciones/líneas de código

### Limitaciones identificadas
- **Procesadores LEGACY**: `procesador_ihq.py`, `procesador_biopsia.py`, `procesador_autopsia.py`, `procesador_revision.py` requieren análisis por separado si se necesita cobertura histórica completa
- **Archivos binarios**: Algunos `.xlsm` en `EXCEL/` sin contenido de macros exportado para análisis
- **Ejecutables**: `OCR_Medico.exe` y archivos en `build/` excluidos por ser artefactos compilados
- **Datos sensibles**: PDFs en `pdfs_patologia/` excluidos del análisis por contener información médica

### Próximos pasos sugeridos
- Análisis detallado de procesadores LEGACY si se requiere documentación de evolución histórica
- Exportación de macros VBA de archivos Excel para análisis completo de flujos de datos
- Documentación de casos de uso específicos por tipo de informe (Biopsia, Autopsia, Revisión)


