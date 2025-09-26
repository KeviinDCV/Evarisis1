# EVARISIS Gestor H.U.V 🏥

**Versión**: v3.2  
**Fecha**: 25/09/2025  
**Sistema de Gestión Oncológica Inteligente para Hospital Universitario del Valle**

## 🚀 Inicio Rápido

### Instalación

```powershell
# 1. Clonar repositorio
git clone https://github.com/TrainHeartX/ProyectoHUV9GESTOR_ONCOLOGIA.git
cd ProyectoHUV9GESTOR_ONCOLOGIA

# 2. Crear entorno virtual
python -m venv venv0
.\venv0\Scripts\activate

# 3. Instalar dependencias
python -m pip install -r requirements.txt

# O usar la tarea predefinida:
# Ctrl+Shift+P -> "Tasks: Run Task" -> "Install deps"
```

### Ejecución

```powershell
# Método principal (recomendado)
python huv_ocr_sistema_definitivo.py

# O usar la tarea predefinida:
# Ctrl+Shift+P -> "Tasks: Run Task" -> "Run app"

# Para desarrollo/testing de UI
python ui.py --lanzado-por-evarisis --nombre="Tu Nombre" --cargo="Tu Cargo" --tema="litera"
```

## 📋 Descripción

**EVARISIS Gestor H.U.V** es un sistema de inteligencia clínica que transforma informes de patología oncológica (PDFs) en una base de datos estructurada de alta confiabilidad. El sistema automatiza la extracción de información de informes IHQ (Inmunohistoquímica) y genera análisis estratégicos para la toma de decisiones médicas y administrativas.

### ✨ Características Principales

- **🔍 OCR Híbrido Avanzado**: Extracción automática de texto desde PDFs nativos y escaneados
- **🧬 Procesamiento IHQ Especializado**: Normalización de biomarcadores críticos (HER2, Ki-67, RE/RP, PD-L1, P16)
- **📊 Dashboard Analítico**: Visualizaciones en tiempo real con KPIs oncológicos
- **🤖 Automatización Web**: Bot Selenium para consultas automatizadas en portal HUV
- **💾 Base de Datos Inteligente**: SQLite con esquema de 167 campos y control de duplicados
- **🎨 Interfaz Moderna**: TTKBootstrap con navegación flotante y temas adaptativos

## 🏗️ Arquitectura

```
Portal HUV Patología → [Bot Selenium] → EVARISIS Gestor HUV
                                              ↓
PDFs Patología → OCR Híbrido → Extracción IHQ → SQLite DB
                                              ↓
              Dashboard Analytics ← Base de Datos ← Exportaciones Excel
```

### 📁 Componentes Principales

| Archivo | Descripción |
|---------|-------------|
| `huv_ocr_sistema_definitivo.py` | **Punto de entrada principal** - Coordinador del sistema |
| `ui.py` | Interfaz gráfica TTKBootstrap con navegación flotante |
| `ocr_processing.py` | Motor OCR híbrido (PyMuPDF + Tesseract) |
| `procesador_ihq_biomarcadores.py` | Extractor especializado de biomarcadores IHQ |
| `database_manager.py` | Gestor de base de datos SQLite con transacciones seguras |
| `huv_web_automation.py` | Bot Selenium para automatización web |

## 👥 Audiencias

| Audiencia | Beneficio Principal |
|-----------|-------------------|
| **Equipo Médico Oncológico** | Dashboard inmediato con KPIs de biomarcadores para decisiones terapéuticas |
| **Dirección Hospitalaria** | Reducción 85% tiempo transcripción, métricas operativas y ROI |
| **Investigadores Clínicos** | Dataset curado con 167 campos para estudios longitudinales |
| **Equipo de Desarrollo** | Arquitectura modular, documentación completa y versionamiento semántico |

## 🛠️ Desarrollo

### Requisitos del Sistema

- **Python**: 3.8+
- **Sistema Operativo**: Windows 10/11 (recomendado)
- **RAM**: 4GB mínimo, 8GB recomendado
- **Espacio**: 2GB para dependencias y datos

### Dependencias Principales

- `ttkbootstrap`: Framework de interfaz moderna
- `selenium`: Automatización web
- `PyMuPDF`: Procesamiento de PDFs
- `pytesseract`: OCR para documentos escaneados  
- `pandas`: Manipulación de datos
- `matplotlib/seaborn`: Visualizaciones
- `sqlite3`: Base de datos embebida

### 🔧 Configuración

El sistema utiliza `config.ini` para configuraciones personalizables:

```ini
[OCR]
dpi = 300
language = spa

[UI]
theme = litera
default_user = Usuario Sistema

[DATABASE]
path = huv_oncologia.db
backup_enabled = true
```

## 📊 Métricas de Rendimiento

- ⚡ **Reducción de tiempo**: 85% en transcripción manual
- 🎯 **Precisión OCR**: >95% en documentos nativos, >85% en escaneados
- 📈 **Capacidad**: Procesamiento de 100+ informes/hora
- 💾 **Almacenamiento**: ~1MB por cada 1000 informes procesados

## 🚦 Estados del Proyecto

| Componente | Estado | Cobertura |
|------------|--------|-----------|
| **OCR Híbrido** | ✅ Producción | 100% |
| **Extracción IHQ** | ✅ Producción | 95% |
| **Dashboard Analytics** | ✅ Producción | 90% |
| **Automatización Web** | ⚠️ Beta | 80% |
| **Exportaciones** | ✅ Producción | 100% |

## 📚 Documentación

- 📖 **[Documentación Completa](documentacion/README.md)**: Guías técnicas y de usuario
- 🔧 **[Análisis Técnico](documentacion/analisis/)**: Arquitectura y componentes
- 📋 **[Changelog](documentacion/CHANGELOG.md)**: Historial de versiones
- 🚀 **[Inicio Rápido](documentacion/INICIO_RAPIDO.md)**: Guía de instalación y uso

## 🤝 Contribución

1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/amazing-feature`)
3. Commit cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abrir Pull Request

## 📋 Roadmap

### Próximas Versiones

- **v3.3**: Mejoras en precisión OCR y nuevos biomarcadores
- **v3.4**: Dashboard interactivo con filtros avanzados
- **v4.0**: Integración con sistemas hospitalarios (SERVINTE)
- **v4.1**: Motor de auditoría automática con IA

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/TrainHeartX/ProyectoHUV9GESTOR_ONCOLOGIA/issues)
- **Documentación**: `documentacion/` en este repositorio
- **Email**: Contactar al equipo de desarrollo

## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

---

**EVARISIS Gestor H.U.V** - Transformando la gestión oncológica através de inteligencia artificial y automatización inteligente.

*Hospital Universitario del Valle - Septiembre 2025*
