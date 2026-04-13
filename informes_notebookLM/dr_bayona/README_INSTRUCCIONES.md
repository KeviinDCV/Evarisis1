# 📚 Instrucciones de Uso - Contenido NotebookLM para Dr. Juan Camilo Bayona

**Generado:** Noviembre 2025
**Audiencia:** Dr. Juan Camilo Bayona (Patólogo, Stakeholder Principal)
**Objetivo:** Demostrar avances, capacidades agénticas, precisión y complejidad del proyecto

---

## 📂 Estructura de Contenido

Este paquete contiene **7 formatos diferentes** (14 archivos totales) listos para usar en **Google NotebookLM**:

```
dr_bayona/
├── video/                          → Presentación visual narrada
├── audio/                          → 4 tipos de podcasts IA
│   ├── informacion_detallada/      → Conversación profunda (15-20 min)
│   ├── breve/                      → Resumen ejecutivo (2-3 min)
│   ├── critica/                    → Revisión experta (10-15 min)
│   └── debate/                     → Debate reflexivo (12-18 min)
├── cuestionario/                   → FAQ interactivo
└── reporte/                        → Briefing ejecutivo (1-2 páginas)
```

Cada carpeta contiene:

- **`fuente_X.md`** → Archivo fuente para subir a NotebookLM
- **`prompts_X.txt`** → Instrucciones de configuración

---

## 🚀 Guía Rápida de Uso

### Paso 1: Acceder a NotebookLM

1. Ve a: https://notebooklm.google.com
2. Crea un nuevo cuaderno (botón "+ Create")

### Paso 2: Subir Archivo Fuente

1. Haz clic en **"Add source"**
2. Selecciona **"Upload"** → **"Text"**
3. Arrastra o selecciona el archivo `fuente_X.md` del formato deseado
4. Espera a que NotebookLM procese el archivo (10-30 segundos)

### Paso 3: Configurar Formato

#### Para VIDEO:

1. En la sección **"Notebook guide"**, haz clic en **"Generate"**
2. Selecciona **"Video"** como formato
3. Abre el archivo `prompts_video.txt`
4. Copia la sección **"PROMPT DE ENFOQUE"**
5. Pégala en el campo de personalización
6. Copia la sección **"PROMPT DE ESTILO VISUAL"**
7. Selecciona el estilo visual personalizado
8. Haz clic en **"Generate video"**

#### Para AUDIO:

1. En la sección **"Notebook guide"**, haz clic en **"Generate"**
2. Selecciona **"Audio Overview"**
3. Abre el archivo `prompts_audio_[TIPO].txt` correspondiente
4. En **"Format"**, selecciona el tipo indicado (ej: "Información detallada")
5. En **"Idioma"**, selecciona **"español"**
6. En **"Duración"**, selecciona según el tipo:
   - **Información detallada**: Predeterminada
   - **Breve**: Corto
   - **Crítica**: Predeterminada
   - **Debate**: Predeterminada
7. Copia el **"PROMPT DE ENFOQUE"** del archivo .txt
8. Pégalo en el campo de personalización
9. Haz clic en **"Generate audio"**

#### Para CUESTIONARIO (FAQ):

1. Simplemente haz preguntas en el chat de NotebookLM
2. El sistema responderá basándose en el archivo fuente
3. Puedes usar las preguntas sugeridas del archivo `prompts_cuestionario.txt`

#### Para REPORTE:

1. En el chat, escribe: "Genera un briefing ejecutivo de 1-2 páginas"
2. O copia el prompt del archivo `prompts_reporte.txt` y pégalo en el chat
3. Exporta el resultado como PDF

---

## 🎯 Recomendaciones por Formato

### 📹 **VIDEO** (Recomendado para reunión presencial)

- **Duración:** 8-12 minutos
- **Uso:** Presentación ejecutiva en reunión con el Dr. Bayona
- **Ventajas:** Visual, profesional, destaca arquitectura y métricas clave
- **Cuándo usar:** Reunión presencial o virtual de 15-20 minutos

### 🎙️ **AUDIO - Información Detallada** (Recomendado para contexto completo)

- **Duración:** 15-20 minutos
- **Uso:** Escuchar durante viaje o tiempo libre
- **Ventajas:** Análisis profundo, cubre todos los aspectos del proyecto
- **Cuándo usar:** Primera presentación completa del proyecto

### 🎙️ **AUDIO - Breve** (Recomendado para introducción rápida)

- **Duración:** 2-3 minutos
- **Uso:** Resumen ejecutivo rápido antes de reunión
- **Ventajas:** Conciso, directo al grano, ideal para tiempo limitado
- **Cuándo usar:** Enviar por WhatsApp como teaser antes de reunión formal

### 🎙️ **AUDIO - Crítica** (Recomendado para feedback constructivo)

- **Duración:** 10-15 minutos
- **Uso:** Análisis balanceado de fortalezas y áreas de mejora
- **Ventajas:** Perspectiva objetiva, constructiva, profesional
- **Cuándo usar:** Después de presentación inicial, para validar decisiones técnicas

### 🎙️ **AUDIO - Debate** (Recomendado para exploración de dudas)

- **Duración:** 12-18 minutos
- **Uso:** Explorar preguntas clave desde múltiples perspectivas
- **Ventajas:** Cubre objeciones potenciales, responde preocupaciones
- **Cuándo usar:** Preparación para reunión con múltiples stakeholders

### ❓ **CUESTIONARIO** (Recomendado para consultas específicas)

- **Formato:** Chat interactivo
- **Uso:** Responder dudas específicas del Dr. Bayona
- **Ventajas:** Interactivo, busca información puntual
- **Cuándo usar:** Post-presentación, como manual de consulta

### 📄 **REPORTE** (Recomendado para documentación formal)

- **Formato:** PDF de 1-2 páginas
- **Uso:** Documento formal para archivo o compartir con terceros
- **Ventajas:** Profesional, conciso, exportable
- **Cuándo usar:** Como anexo formal a comunicaciones oficiales

---

## 📋 Secuencia Recomendada de Presentación

### Opción A: Primera Vez (Impacto Máximo)

1. **Email inicial:** Enviar **REPORTE** (lectura 5 min) ✉️
2. **Reunión presencial:** Presentar **VIDEO** (10 min) + Discusión (10 min) 🎥
3. **Post-reunión:** Compartir **AUDIO - Información Detallada** para profundizar 🎙️
4. **Seguimiento:** Dar acceso a **CUESTIONARIO** para dudas futuras ❓

### Opción B: Tiempo Limitado (Eficiencia)

1. **Pre-reunión:** Enviar **AUDIO - Breve** por WhatsApp (2-3 min) 📱
2. **Reunión corta:** Presentar **VIDEO** (8 min) + Q&A (7 min) 🎥
3. **Seguimiento:** Email con **REPORTE** para referencia formal 📄

### Opción C: Validación Técnica (Feedback)

1. **Contexto:** Compartir **AUDIO - Debate** (explora objeciones) 🎙️
2. **Análisis:** Compartir **AUDIO - Crítica** (análisis balanceado) 🎙️
3. **Reunión:** Discusión basada en contenido previo 💬
4. **Documentación:** **REPORTE** con conclusiones acordadas 📄

---

## ⏱️ Tiempos de Procesamiento en NotebookLM

| Formato | Tiempo de generación |
| ------- | -------------------- |
| Video   | 8-12 minutos         |
| Audio   | 3-5 minutos          |
| FAQ     | Instantáneo          |
| Reporte | 30-60 segundos       |

---

## 💡 Consejos Adicionales

### Para Máxima Calidad:

- ✅ **SÍ personalizar** los prompts según el archivo .txt de cada formato
- ✅ **SÍ seleccionar** el idioma español en configuración de audio
- ✅ **SÍ descargar** el contenido generado para compartir offline
- ❌ **NO omitir** la sección de prompts (reduce significativamente la calidad)
- ❌ **NO mezclar** fuentes de diferentes audiencias en el mismo cuaderno

### Para Compartir:

- **Video/Audio:** Descargar archivo MP4/MP3 y compartir vía email/Drive
- **Reporte:** Exportar chat como PDF desde NotebookLM
- **FAQ:** Compartir link del cuaderno NotebookLM (requiere cuenta Google)

---

## 🆘 Solución de Problemas

| Problema                                  | Solución                                             |
| ----------------------------------------- | ---------------------------------------------------- |
| NotebookLM no genera el contenido         | Verifica que el archivo .md se subió completamente   |
| Audio en inglés en vez de español         | Selecciona "español" en la configuración de idioma   |
| Video no coincide con el enfoque esperado | Asegúrate de copiar el PROMPT DE ENFOQUE del .txt    |
| FAQ no responde correctamente             | Reformula la pregunta o usa las preguntas del .txt   |
| Reporte muy largo o muy corto             | Especifica la longitud en el prompt (ej: "1 página") |

---

## 📞 Contacto

**Desarrollador:** Daniel Rodríguez
**Email:** innovacionydesarrollo@correohuv.gov.co
**Institución:** Hospital Universitario del Valle - Departamento de Patología
**Email institucional:** cirugiaoncologica@correohuv.gov.co

---

## 📊 Métricas del Contenido Generado

- **Total de palabras:** ~15,000 palabras
- **Total de archivos:** 14 archivos
- **Formatos disponibles:** 7 formatos diferentes
- **Tiempo total de contenido multimedia:** ~60-80 minutos
- **Precisión del proyecto:** >95% en validación semántica
- **Biomarcadores soportados:** 67 individuales + 4 pronósticos especiales
- **Casos procesados exitosamente:** 1000+ informes IHQ

---

**¡Listo para impresionar al Dr. Bayona!** 🎉
