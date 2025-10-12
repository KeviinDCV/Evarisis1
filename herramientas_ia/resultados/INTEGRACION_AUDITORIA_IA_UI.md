# 🔧 INTEGRACIÓN DE AUDITORÍA IA EN UI.PY

## 📋 Resumen

Este documento explica **EXACTAMENTE** cómo integrar el sistema de auditoría con IA en el flujo normal de procesamiento de `ui.py`.

---

## 🎯 FLUJO ACTUAL VS FLUJO CON IA

### **FLUJO ACTUAL** (sin IA)

```python
def procesar_pdfs():
    for pdf in pdfs_seleccionados:
        # 1. OCR
        texto = pdf_to_text_enhanced(pdf)

        # 2. Consolidar y segmentar
        segmentos = consolidate_text_by_ihq(texto)

        # 3. Extraer datos
        for ihq, texto_ihq in segmentos.items():
            datos = extract_ihq_data(texto_ihq)

            # 4. Guardar en BD
            insert_or_update_registro(datos)

    # 5. Mostrar mensaje completado
    messagebox.showinfo("Procesamiento completado")

    # 6. Ir a visualizador
    mostrar_visualizador()
```

### **FLUJO NUEVO** (con Auditoría IA)

```python
def procesar_pdfs():
    casos_procesados = []  # NUEVO: Lista para auditoría

    for pdf in pdfs_seleccionados:
        # 1. OCR
        texto = pdf_to_text_enhanced(pdf)

        # 2. Consolidar y segmentar
        segmentos = consolidate_text_by_ihq(texto)

        # 3. Extraer datos
        for ihq, texto_ihq in segmentos.items():
            datos = extract_ihq_data(texto_ihq)

            # 4. NUEVO: Generar debug map
            debug_map = crear_debug_map(ihq, texto_ihq, datos)

            # 5. Guardar en BD (versión inicial)
            insert_or_update_registro(datos)

            # 6. NUEVO: Preparar para auditoría
            casos_procesados.append({
                'numero_peticion': ihq,
                'debug_map': debug_map,
                'datos_bd': get_registro_by_peticion(ihq)
            })

    # 7. NUEVO: Mostrar ventana de auditoría IA
    mostrar_ventana_auditoria_ia(
        casos_a_auditar=casos_procesados,
        callback_completado=lambda resultados: finalizar_procesamiento(resultados)
    )

def finalizar_procesamiento(resultados_auditoria):
    # 8. Mostrar resumen ya se muestra en ventana auditoria
    # 9. Ir a visualizador (con datos corregidos)
    mostrar_visualizador()
```

---

## 📝 CÓDIGO A AGREGAR EN UI.PY

### **1. Imports al inicio del archivo**

```python
# Agregar después de los imports existentes (línea ~35)

# === IMPORTS PARA AUDITORÍA IA ===
from core.debug_mapper import DebugMapper
from core.ventana_auditoria_ia import mostrar_ventana_auditoria
from core.database_manager import get_registro_by_peticion
```

### **2. Modificar la función de procesamiento de PDFs**

Busca la función que procesa los PDFs (probablemente se llama `procesar_pdfs_thread` o similar en ui.py).

**ANTES:**
```python
def procesar_pdfs_thread(self):
    # ... código OCR y extracción ...

    for segmento_ihq in segmentos:
        datos = extract_ihq_data(texto_consolidado)
        insert_or_update_registro(datos)

    # Mostrar completado
    self.after(0, lambda: messagebox.showinfo("Completado", "Procesamiento finalizado"))
    self.after(0, self.ir_a_visualizador)
```

**DESPUÉS:**
```python
def procesar_pdfs_thread(self):
    casos_para_auditoria = []  # NUEVO

    # ... código OCR y extracción ...

    for numero_ihq, texto_consolidado in segmentos.items():
        # Crear debug mapper
        mapper = DebugMapper()
        mapper.iniciar_sesion(numero_ihq, pdf_path)

        # Registrar OCR
        mapper.registrar_ocr(
            texto_original=texto_ocr_completo,
            texto_consolidado=texto_consolidado
        )

        # Extraer datos
        datos = extract_ihq_data(texto_consolidado)

        # Registrar extracción
        mapper.registrar_extractor("unified", datos)

        # Guardar en BD
        insert_or_update_registro(datos)

        # Obtener datos guardados
        datos_bd = get_registro_by_peticion(numero_ihq)

        # Registrar BD en mapper
        mapper.registrar_base_datos(datos_bd)

        # Guardar debug map y obtener dict completo
        mapper.guardar_mapa()
        debug_map_completo = mapper.current_map

        # Agregar a lista de auditoría
        casos_para_auditoria.append({
            'numero_peticion': numero_ihq,
            'debug_map': debug_map_completo,
            'datos_bd': datos_bd
        })

    # NUEVO: Mostrar ventana de auditoría IA
    def callback_auditoria_completada(resultados):
        # Cuando termine la auditoría, ir al visualizador
        self.ir_a_visualizador()

    self.after(0, lambda: mostrar_ventana_auditoria(
        self,
        casos_para_auditoria,
        callback_auditoria_completada
    ))
```

---

## 🔑 PUNTOS CLAVE DE INTEGRACIÓN

### **1. Creación del Debug Map**

```python
from core.debug_mapper import DebugMapper

# Para cada caso IHQ procesado:
mapper = DebugMapper()
mapper.iniciar_sesion(numero_ihq, pdf_path)
mapper.registrar_ocr(texto_original, texto_consolidado)
mapper.registrar_extractor("unified", datos_extraidos)
mapper.registrar_base_datos(datos_guardados_bd)
mapper.guardar_mapa()

# Obtener el mapa completo como dict
debug_map_dict = mapper.current_map
```

### **2. Preparación de Datos para Auditoría**

```python
# Lista de casos a auditar
casos_para_auditoria = []

for cada_caso_procesado:
    casos_para_auditoria.append({
        'numero_peticion': 'IHQ250001',
        'debug_map': debug_map_completo_dict,
        'datos_bd': get_registro_by_peticion('IHQ250001')
    })
```

### **3. Mostrar Ventana de Auditoría**

```python
from core.ventana_auditoria_ia import mostrar_ventana_auditoria

def cuando_termine_auditoria(resultados):
    # Aquí puedes procesar resultados si quieres
    # o simplemente ir al visualizador
    self.ir_a_visualizador()

mostrar_ventana_auditoria(
    self,  # parent window
    casos_para_auditoria,
    cuando_termine_auditoria
)
```

---

## ⚙️ CONFIGURACIÓN NECESARIA

### **1. LM Studio debe estar corriendo**

La auditoría IA **funciona automáticamente** si LM Studio está activo.
Si NO está activo:
- La ventana mostrará un mensaje de advertencia
- Se omitirá la auditoría
- El flujo continúa normal (sin correcciones)

### **2. No requiere configuración adicional**

El sistema detecta automáticamente:
- ✅ Si LM Studio está activo (puerto 1234)
- ✅ Qué modelo está cargado
- ✅ Si puede hacer inferencia

### **3. Manejo de errores**

Si hay error durante auditoría:
- Se muestra mensaje al usuario
- Se guarda log de error
- El flujo continúa (datos quedan como estaban)

---

## 📊 EJEMPLO COMPLETO DE INTEGRACIÓN

```python
# En ui.py, dentro de la clase principal

def procesar_pdfs_seleccionados(self):
    """Procesa los PDFs seleccionados con auditoría IA"""

    # Iniciar en thread para no bloquear UI
    thread = threading.Thread(
        target=self._procesar_pdfs_thread_con_auditoria,
        daemon=True
    )
    thread.start()

def _procesar_pdfs_thread_con_auditoria(self):
    """Thread de procesamiento con auditoría integrada"""

    casos_para_auditoria = []

    for pdf_path in self.pdfs_seleccionados:
        # 1. OCR
        texto_ocr = pdf_to_text_enhanced(pdf_path)

        # 2. Consolidar
        segmentos = consolidate_text_by_ihq(texto_ocr)

        # 3. Procesar cada caso
        for numero_ihq, texto_consolidado in segmentos.items():

            # === GENERAR DEBUG MAP ===
            mapper = DebugMapper()
            mapper.iniciar_sesion(numero_ihq, pdf_path)
            mapper.registrar_ocr(texto_ocr, texto_consolidado)

            # === EXTRAER DATOS ===
            datos_extraidos = extract_ihq_data(texto_consolidado)
            mapper.registrar_extractor("unified", datos_extraidos)

            # === GUARDAR EN BD ===
            insert_or_update_registro(datos_extraidos)
            datos_bd = get_registro_by_peticion(numero_ihq)
            mapper.registrar_base_datos(datos_bd)

            # === GUARDAR DEBUG MAP ===
            mapper.guardar_mapa()

            # === PREPARAR PARA AUDITORÍA ===
            casos_para_auditoria.append({
                'numero_peticion': numero_ihq,
                'debug_map': mapper.current_map,
                'datos_bd': datos_bd
            })

    # === MOSTRAR VENTANA DE AUDITORÍA IA ===
    self.after(0, lambda: self._iniciar_auditoria_ia(casos_para_auditoria))

def _iniciar_auditoria_ia(self, casos):
    """Inicia la auditoría con ventana emergente"""

    def on_auditoria_completada(resultados):
        # Auditoría terminada, ir a visualizador
        self.ir_a_visualizador()

    # Mostrar ventana de auditoría
    mostrar_ventana_auditoria(
        self,
        casos,
        on_auditoria_completada
    )
```

---

## 🎨 CARACTERÍSTICAS DE LA VENTANA DE AUDITORÍA

### **Diseño**
- ✅ Ventana modal (bloquea interacción con ventana principal)
- ✅ Centrada en pantalla
- ✅ No se puede cerrar con X (para evitar interrupciones)
- ✅ Logo/icono de IA
- ✅ Barra de progreso animada

### **Información Mostrada**
- 📊 Progreso total (0-100%)
- 📋 Casos procesados (X / Total)
- 🔧 Correcciones aplicadas
- 📝 Mensaje de estado actual

### **Al Finalizar**
- ✅ Mensaje de resumen con estadísticas
- ✅ Cierra automáticamente
- ✅ Llama al callback para continuar flujo

---

## 🧪 TESTING

### **1. Test sin LM Studio (auditoría omitida)**

```python
# LM Studio NO está activo

# Resultado esperado:
# - Ventana muestra: "⚠️ LM Studio no está activo"
# - MessageBox: "Auditoría IA no disponible"
# - Flujo continúa normal sin correcciones
```

### **2. Test con LM Studio (auditoría completa)**

```python
# LM Studio SÍ está activo

# Resultado esperado:
# - Ventana muestra progreso: "Auditando caso 1/5..."
# - Barra de progreso se actualiza
# - Al finalizar: "✅ Auditoría completada - X correcciones aplicadas"
# - BD actualizada con correcciones
```

### **3. Test con múltiples casos**

```python
casos_test = [
    {'numero_peticion': 'IHQ250001', 'debug_map': {...}, 'datos_bd': {...}},
    {'numero_peticion': 'IHQ250002', 'debug_map': {...}, 'datos_bd': {...}},
    {'numero_peticion': 'IHQ250003', 'debug_map': {...}, 'datos_bd': {...}},
]

# Resultado esperado:
# - Procesa los 3 casos secuencialmente
# - Muestra progreso: 0% -> 33% -> 66% -> 100%
# - Resumen final con correcciones totales
```

---

## 📁 ARCHIVOS MODIFICADOS/CREADOS

### **Archivos Nuevos Creados**
1. ✅ `core/auditoria_ia.py` - Sistema de auditoría
2. ✅ `core/ventana_auditoria_ia.py` - Ventana emergente
3. ✅ `core/debug_mapper.py` - Generador de mapas
4. ✅ `core/llm_client.py` - Cliente LLM

### **Archivos a Modificar**
1. ⚠️ `ui.py` - Agregar integración (según instrucciones arriba)
2. ✅ `core/database_manager.py` - Ya modificado (funciones agregadas)

---

## ✅ CHECKLIST DE INTEGRACIÓN

- [ ] Importar módulos necesarios en ui.py
- [ ] Modificar función de procesamiento de PDFs
- [ ] Crear lista `casos_para_auditoria` dentro del loop
- [ ] Generar debug_map para cada caso
- [ ] Llamar a `mostrar_ventana_auditoria` al finalizar procesamiento
- [ ] Definir callback para cuando termine auditoría
- [ ] Probar con LM Studio activo
- [ ] Probar con LM Studio inactivo
- [ ] Verificar que correcciones se apliquen a BD
- [ ] Verificar que flujo continúe al visualizador

---

## 🚀 SIGUIENTE PASO

1. **Ubicar la función de procesamiento en ui.py**
   - Buscar donde se hace el OCR y extracción
   - Probablemente en un método como `procesar_pdfs()` o similar

2. **Aplicar las modificaciones**
   - Seguir el código de ejemplo de arriba
   - Adaptar nombres de variables según tu código

3. **Probar**
   - Primero SIN LM Studio (debe mostrar advertencia)
   - Luego CON LM Studio (debe hacer auditoría)

---

**¿Necesitas ayuda con la integración?**

Dime en qué parte específica de ui.py está el procesamiento de PDFs y te ayudo a hacer la integración exacta.

---

*EVARISIS Gestor HUV - Sistema de Auditoría con IA v1.0.0*
*Integración en UI - Octubre 2025*
