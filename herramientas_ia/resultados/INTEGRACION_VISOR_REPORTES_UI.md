# 🔗 Guía de Integración: Visor de Reportes en UI Principal

**Versión:** 6.0.6
**Fecha:** 2025-10-24
**Objetivo:** Integrar el visor de reportes históricos en la interfaz principal

---

## 🎯 Opciones de Integración

### Opción 1: Nueva Pestaña en Notebook Principal (RECOMENDADA)

**Ubicación:** Junto a pestañas "Importación", "Gestión de PDFs", etc.

**Implementación en `ui.py`:**

```python
def _crear_pestanas(self):
    """Crear pestañas principales del sistema"""

    # ... pestañas existentes ...

    # NUEVA PESTAÑA: Reportes de Importación
    self._crear_tab_reportes_importacion()

def _crear_tab_reportes_importacion(self):
    """V6.0.6: Nueva pestaña para ver reportes históricos"""
    from core.visor_reportes_importacion import VisorReportesImportacion
    from pathlib import Path
    import json
    from datetime import datetime

    tab = ttkb.Frame(self.notebook)
    self.notebook.add(tab, text="📋 Reportes Importación")

    # Frame principal
    main_frame = ttkb.Frame(tab, padding=20)
    main_frame.pack(fill=BOTH, expand=YES)

    # Título
    ttkb.Label(
        main_frame,
        text="📊 Historial de Importaciones",
        font=("Segoe UI", 18, "bold"),
        bootstyle="info"
    ).pack(pady=(0, 10))

    # Descripción
    ttkb.Label(
        main_frame,
        text="Visualice y analice reportes de importaciones anteriores",
        font=("Segoe UI", 10),
        foreground="#666"
    ).pack(pady=(0, 20))

    # Frame para resumen rápido
    resumen_frame = ttkb.LabelFrame(
        main_frame,
        text="📈 Resumen Rápido",
        bootstyle="info",
        padding=15
    )
    resumen_frame.pack(fill=X, pady=(0, 20))

    # Cargar estadísticas rápidas
    reportes_dir = Path("data/reportes_importacion")
    if reportes_dir.exists():
        reportes = list(reportes_dir.glob("reporte_importacion_*.json"))
        total_reportes = len(reportes)

        # Último reporte
        if reportes:
            ultimo = sorted(reportes)[-1]
            try:
                with open(ultimo, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    timestamp = data.get('timestamp', '')
                    resumen = data.get('resumen', {})

                    fecha_obj = datetime.fromisoformat(timestamp)
                    fecha_str = fecha_obj.strftime("%d/%m/%Y %H:%M")

                    ttkb.Label(
                        resumen_frame,
                        text=f"Total de reportes guardados: {total_reportes}",
                        font=("Segoe UI", 10, "bold")
                    ).pack(anchor=W, pady=3)

                    ttkb.Label(
                        resumen_frame,
                        text=f"Última importación: {fecha_str}",
                        font=("Segoe UI", 10)
                    ).pack(anchor=W, pady=3)

                    ttkb.Label(
                        resumen_frame,
                        text=f"Casos procesados: {resumen.get('total', 0)}",
                        font=("Segoe UI", 10)
                    ).pack(anchor=W, pady=3)

                    ttkb.Label(
                        resumen_frame,
                        text=f"Tasa de éxito: {resumen.get('porcentaje_exito', 0):.1f}%",
                        font=("Segoe UI", 10)
                    ).pack(anchor=W, pady=3)
            except:
                pass
    else:
        ttkb.Label(
            resumen_frame,
            text="No hay reportes guardados aún",
            font=("Segoe UI", 10),
            foreground="#999"
        ).pack(pady=10)

    # Botón para abrir visor completo
    ttkb.Button(
        main_frame,
        text="🔍 Ver Todos los Reportes",
        command=lambda: self._abrir_visor_reportes(),
        bootstyle="info",
        width=30
    ).pack(pady=20)

def _abrir_visor_reportes(self):
    """Abrir ventana del visor de reportes"""
    from core.visor_reportes_importacion import mostrar_visor_reportes
    mostrar_visor_reportes(self)
```

**Ventajas:**
- Acceso permanente desde pestaña dedicada
- Resumen rápido visible sin abrir ventana
- Coherente con arquitectura actual

---

### Opción 2: Botón en Toolbar Principal

**Ubicación:** Junto a otros botones de acción rápida

**Implementación en `ui.py`:**

```python
def _crear_toolbar(self):
    """Crear toolbar con acciones rápidas"""

    toolbar = ttkb.Frame(self.root)
    toolbar.pack(fill=X, padx=10, pady=5)

    # ... botones existentes ...

    # NUEVO BOTÓN: Ver Reportes
    ttkb.Button(
        toolbar,
        text="📋 Reportes",
        command=self._abrir_visor_reportes,
        bootstyle="info-outline",
        width=15
    ).pack(side=LEFT, padx=5)

def _abrir_visor_reportes(self):
    """Abrir ventana del visor de reportes"""
    from core.visor_reportes_importacion import mostrar_visor_reportes
    mostrar_visor_reportes(self)
```

**Ventajas:**
- Acceso rápido con 1 click
- No ocupa espacio en pestañas
- Ideal para uso ocasional

---

### Opción 3: Menú Contextual en Pestaña Importación

**Ubicación:** Dentro de la pestaña de importación existente

**Implementación en `ui.py`:**

```python
def _crear_tab_importacion(self):
    """Crear pestaña de importación (mejorada)"""

    # ... código existente ...

    # Frame de acciones adicionales
    acciones_frame = ttkb.LabelFrame(
        tab,
        text="📊 Análisis e Historial",
        bootstyle="info",
        padding=10
    )
    acciones_frame.pack(fill=X, padx=20, pady=10)

    ttkb.Button(
        acciones_frame,
        text="📋 Ver Historial de Importaciones",
        command=self._abrir_visor_reportes,
        bootstyle="info-outline",
        width=40
    ).pack(pady=5)
```

**Ventajas:**
- Contexto claro (está en importación)
- No requiere nueva pestaña
- Fácil de descubrir

---

## 🚀 Implementación Paso a Paso

### Paso 1: Importar Módulos

Agregar al inicio de `ui.py`:

```python
# V6.0.6: Visor de reportes históricos
from core.visor_reportes_importacion import mostrar_visor_reportes
```

### Paso 2: Agregar Método Helper

```python
def _abrir_visor_reportes(self):
    """V6.0.6: Abrir ventana del visor de reportes de importación"""
    try:
        mostrar_visor_reportes(self)
    except Exception as e:
        logging.error(f"Error abriendo visor de reportes: {e}")
        messagebox.showerror(
            "Error",
            f"No se pudo abrir el visor de reportes:\n{str(e)}"
        )
```

### Paso 3: Elegir y Aplicar Opción

Elegir una de las 3 opciones anteriores y agregar el código correspondiente.

**Recomendación:** Opción 1 (pestaña dedicada) para máxima visibilidad.

---

## 🎨 Personalización Visual

### Tema Consistente

```python
# Usar mismos estilos que resto de UI
bootstyle="info"      # Para botones principales
bootstyle="success"   # Para acciones positivas
bootstyle="warning"   # Para advertencias
```

### Iconos Consistentes

```python
# Mantener iconos emoji coherentes
"📋" → Reportes/Documentos
"📊" → Estadísticas/Análisis
"🔍" → Ver/Buscar
"📈" → Gráficos/Tendencias
```

---

## 🔗 Flujo de Usuario

### Flujo Completo:

```
1. Usuario importa PDFs
   ↓
2. Se procesa importación
   ↓
3. Se muestra ventana de resultados (V6.0.6 con pestañas)
   ↓
4. Sistema guarda reporte automáticamente
   ↓
5. Usuario cierra ventana
   ↓
6. Más adelante, usuario quiere revisar
   ↓
7. Usuario va a pestaña "📋 Reportes Importación"
   ↓
8. Ve resumen rápido de última importación
   ↓
9. Click en "🔍 Ver Todos los Reportes"
   ↓
10. Se abre VisorReportesImportacion
    ↓
11. Usuario selecciona reporte de lista
    ↓
12. Ve detalles completos de importación anterior
```

---

## 📊 Ejemplo de Uso

### Escenario Real:

**Dr. Pérez necesita verificar una importación de hace 1 semana:**

```
1. Abre EVARISIS
2. Va a pestaña "📋 Reportes Importación"
3. Ve resumen:
   - Total reportes: 15
   - Última importación: 24/10/2025 15:30

4. Click en "🔍 Ver Todos los Reportes"
5. Aparece ventana con lista:
   #1  2025-10-24 15:30  Total: 15  Completos: 12
   #2  2025-10-23 10:15  Total: 8   Completos: 7
   #3  2025-10-17 14:45  Total: 20  Completos: 18  ← Hace 1 semana

6. Doble click en #3
7. Ve panel derecho con:
   - Resumen: 20 casos, 18 completos (90%)
   - Casos completos: Lista de 18
   - Casos incompletos: IHQ250015, IHQ250018
   - Correcciones: 12 correcciones en 8 casos

8. Confirma que todo se procesó correctamente
9. Cierra ventana
```

---

## 🧪 Testing Recomendado

### Casos de Prueba:

1. **Sin reportes guardados:**
   - Verificar mensaje "No hay reportes aún"
   - Botón deshabilitado o muestra ventana vacía

2. **Con 1 reporte:**
   - Resumen muestra datos correctos
   - Visor abre y muestra el reporte

3. **Con múltiples reportes (10+):**
   - Lista se muestra cronológicamente
   - Scroll funciona correctamente
   - Selección y visualización funciona

4. **Reporte corrupto:**
   - Sistema maneja error gracefully
   - Muestra mensaje de error
   - No bloquea apertura de otros reportes

---

## 📝 Consideraciones Adicionales

### Performance:

- **Carga lazy:** Reportes se cargan solo al abrir visor
- **Cache:** Considerar cachear lista de reportes
- **Límite:** Considerar mostrar solo últimos 50 reportes

### Almacenamiento:

- **Rotación:** Implementar limpieza automática (ej. mantener últimos 30 días)
- **Compresión:** Considerar comprimir reportes antiguos
- **Backup:** Incluir reportes en backup general del sistema

### Seguridad:

- **Acceso:** Mismos permisos que resto de sistema
- **GDPR:** Reportes contienen datos de pacientes (misma política que BD)
- **Auditoría:** Registrar quién ve qué reportes (opcional)

---

## 🎯 Mejoras Futuras

### Fase 2 (opcional):

1. **Exportación Excel:**
   ```python
   def exportar_reporte_excel(ruta_reporte):
       """Exportar reporte a Excel con formato"""
       # Pandas + openpyxl
   ```

2. **Comparación de Reportes:**
   ```python
   def comparar_reportes(reporte1, reporte2):
       """Comparar dos importaciones"""
       # Diferencias en tasa éxito, correcciones, etc.
   ```

3. **Gráficos Timeline:**
   ```python
   def grafico_timeline():
       """Gráfico de evolución de importaciones"""
       # Matplotlib/Plotly
   ```

4. **Filtros y Búsqueda:**
   ```python
   # Filtrar por fecha, tasa de éxito, número de casos
   # Buscar reportes que contengan caso específico
   ```

---

## ✅ Checklist de Integración

- [ ] Importar `mostrar_visor_reportes` en ui.py
- [ ] Agregar método `_abrir_visor_reportes()` en clase UI
- [ ] Elegir opción de integración (pestaña/botón/menú)
- [ ] Implementar código de la opción elegida
- [ ] Probar con 0 reportes
- [ ] Probar con 1 reporte
- [ ] Probar con múltiples reportes
- [ ] Verificar estilos visuales coherentes
- [ ] Actualizar documentación de usuario
- [ ] Agregar entry en CHANGELOG

---

## 📞 Soporte

**Archivo:** `herramientas_ia/resultados/INTEGRACION_VISOR_REPORTES_UI.md`
**Versión:** 6.0.6
**Fecha:** 2025-10-24

Para implementación completa, referirse a:
- Código visor: `core/visor_reportes_importacion.py`
- Código ventana: `core/ventana_resultados_importacion.py`
- Cambios detallados: `herramientas_ia/resultados/CAMBIOS_VENTANA_RESULTADOS_V6.0.6.md`

---

**FIN DE LA GUÍA**
