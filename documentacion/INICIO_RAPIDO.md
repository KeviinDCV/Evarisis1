# EVARISIS Gestor H.U.V — Inicio Rápido

**EVARISIS Gestor H.U.V** digitaliza informes PDF de patología oncológica del Hospital Universitario del Valle convirtiéndolos en datos estructurados para análisis clínico inmediato. Dirigido especialmente al equipo de oncología, investigadores clínicos y personal de gestión de información que requiere procesamiento eficiente de biomarcadores y KPIs operativos.

## Acceso al sistema

**Apertura desde EVARISIS Dashboard**: 
```bash
python huv_ocr_sistema_definitivo.py
```

**Perfiles/roles de usuario**:
- **Médico oncólogo**: Acceso completo a dashboard analítico y procesamiento IHQ
- **Investigador clínico**: Visualización de datos, exportación y análisis de biomarcadores  
- **Técnico GDI**: Administración, automatización portal web y mantenimiento sistema

## Requisitos previos

### Verificación de dependencias críticas
```bash
# Verificar Tesseract OCR disponible
tesseract --version

# Verificar librerías Python instaladas
python -c "import pytesseract, fitz, pandas, customtkinter, selenium"

# Verificar Google Chrome (requerido para automatización web)
# Chrome debe estar actualizado para compatibilidad con ChromeDriver
```

### Accesos y configuración
- **Archivo de configuración**: `config.ini` debe contener ruta válida de Tesseract para el SO
- **Credenciales portal**: Para automatización web, tener credenciales `huvpatologia.qhorte.com`
- **Carpetas de trabajo**: Permisos escritura en directorio del proyecto para `huv_oncologia.db`
- **Red institucional**: Acceso a portal HUV para descarga automatizada (opcional)

## Primer flujo completo (procesamiento IHQ)

### Paso 1: Lanzar aplicación
```bash
python huv_ocr_sistema_definitivo.py
```
**Resultado esperado**: Interfaz CustomTkinter con 4 pestañas: Procesar PDFs, Visualizar Datos, Dashboard Analítico, Automatizar BD Web  
**Dónde verlo**: Ventana principal maximizada con tema oscuro por defecto

### Paso 2: Procesar PDFs IHQ
1. Clic en pestaña **"Procesar PDFs"**
2. Botón **"Seleccionar Archivos PDF"** → elegir uno o más PDFs IHQ
3. **"Procesar Archivos Seleccionados"** → observar log en tiempo real
4. Esperar mensaje **"✓ Registros guardados exitosamente"**

**Resultado esperado**: N registros insertados en base SQLite, log detallado por PDF procesado  
**Dónde verlo**: Panel de log con timestamps y contador final de registros

### Paso 3: Visualizar datos procesados
1. Clic en pestaña **"Visualizar Datos"** 
2. Botón **"Cargar/Actualizar Datos"** → tabla maestra se llena automáticamente
3. Usar **buscador** para filtrar por número petición o apellido paciente
4. **Clic en fila** → panel derecho muestra detalles completos del informe

**Resultado esperado**: Tabla con informes procesados, búsqueda funcional, vista detallada  
**Dónde verlo**: Tabla central + panel lateral con metadatos completos

### Paso 4: Explorar dashboard analítico
1. Clic en pestaña **"Dashboard Analítico"**
2. **Aplicar filtros** (fecha, servicio, malignidad) usando controles superiores  
3. **Explorar visualizaciones**: KPIs, histogramas biomarcadores, boxplots tiempos
4. **Doble clic en gráfico** → modo pantalla completa para análisis detallado

**Resultado esperado**: Dashboard interactivo con gráficos actualizados según filtros  
**Dónde verlo**: Múltiples widgets gráficos con datos en tiempo real

### Paso 5: Automatizar consulta portal (opcional)
1. Clic en pestaña **"Automatizar BD Web"**
2. **Ingresar credenciales** portal huvpatologia.qhorte.com
3. **Seleccionar rango fechas** usando botón "Elegir Fechas" (calendario inteligente)
4. **"Iniciar Automatización"** → bot Selenium ejecuta consulta automática

**Resultado esperado**: Navegador Chrome abre portal con consulta configurada y ejecutada  
**Dónde verlo**: Ventana Chrome con resultados listos para descarga manual

## Archivos de entrada y salida

| Tipo | Ruta relativa | Formato | Descripción |
|------|---------------|---------|-------------|
| **Entrada** | `pdfs_patologia/*.pdf` | PDF | Informes IHQ del portal institucional |
| **Configuración** | `config.ini` | INI | Rutas Tesseract y parámetros OCR |
| **Salida principal** | `huv_oncologia.db` | SQLite | Base datos con 167 campos estructurados |
| **Logs debug** | `EXCEL/DEBUG_OCR_OUTPUT_*.txt` | TXT | Texto extraído para depuración OCR |
| **Exportaciones** | `EXCEL/Informes_HUV_*.xlsx` | Excel | Reportes generados (manual desde UI) |

## Problemas comunes y solución rápida

### 1. "Tesseract not found" 
**Verificación**: `tesseract --version` en terminal  
**Solución**: Ajustar ruta en `config.ini:[PATHS]` o agregar Tesseract al PATH del sistema

### 2. Error Selenium/Chrome incompatible
**Verificación**: Google Chrome actualizado, internet disponible  
**Solución**: Reiniciar aplicación para descarga automática ChromeDriver actualizado

### 3. OCR calidad deficiente 
**Verificación**: Revisar archivos `DEBUG_OCR_OUTPUT_*.txt` generados  
**Solución**: Incrementar `OCR_SETTINGS.DPI` en `config.ini` o mejorar calidad PDF fuente

### 4. "Registro duplicado" al procesar
**Verificación**: PDF reutiliza mismo número de petición procesado previamente  
**Solución**: Control esperado, verificar en "Visualizar Datos" si registro ya existe

### 5. Dashboard sin datos o filtros
**Verificación**: Base datos contiene registros (pestaña "Visualizar Datos")  
**Solución**: Procesar al menos un PDF IHQ antes de usar dashboard analítico

### 6. Interfaz UI no responde durante procesamiento
**Verificación**: Operación normal, threading en segundo plano  
**Solución**: Esperar finalización observando log en tiempo real, NO cerrar aplicación

## Dónde pedir ayuda

**Contacto técnico principal**: Área de Gestión de la Información (GDI) - Hospital Universitario del Valle  
**Desarrollador**: Ing. Daniel Restrepo (Área de Innovación y Desarrollo)  
**Validación médica**: Dr. Juan Camilo Bayona (Oncología HUV)

**Recursos de documentación**:
- Documentación técnica completa: `documentacion/README.md`
- Análisis detallado por módulo: `documentacion/analisis/README.md`  
- Histórico de cambios: `documentacion/CHANGELOG.md`
- Bitácora de reuniones médicas: `documentacion/BITACORA_DE_ACERCAMIENTOS.md`
