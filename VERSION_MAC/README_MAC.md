# 🍎 EVARISIS CIRUGÍA ONCOLÓGICA - VERSIÓN MAC

**Versión**: 2.1.6
**Compatible con**: macOS 10.14+ (Mojave o superior)
**Python**: 3.8 o superior

---

## 📋 Requisitos Previos

### 1. Python 3.8+
```bash
# Verificar versión
python3 --version

# Si no está instalado, descargar desde:
https://www.python.org/downloads/macos/
```

### 2. Homebrew (recomendado)
```bash
# Instalar Homebrew si no lo tienes
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 3. Tesseract OCR
```bash
# Instalar Tesseract
brew install tesseract

# Instalar idiomas adicionales
brew install tesseract-lang
```

### 4. Tkinter (viene con Python en Mac)
```bash
# Verificar que funciona
python3 -m tkinter
# Debe abrir una ventana pequeña
```

---

## 🚀 Instalación y Uso

### Método 1: Script Automático (Recomendado)

```bash
# 1. Navegar a la carpeta del proyecto
cd /ruta/al/proyecto

# 2. Dar permisos de ejecución al script
chmod +x VERSION_MAC/iniciar_python_mac.sh

# 3. Ejecutar
./VERSION_MAC/iniciar_python_mac.sh
```

El script automáticamente:
- ✅ Crea virtual environment (`venv_mac/`)
- ✅ Instala todas las dependencias
- ✅ Ejecuta la aplicación

### Método 2: Manual

```bash
# 1. Crear virtual environment
python3 -m venv venv_mac

# 2. Activar venv
source venv_mac/bin/activate

# 3. Actualizar pip
pip install --upgrade pip

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar aplicación
python3 ui.py

# 6. Al terminar, desactivar venv
deactivate
```

---

## 🔧 Configuración Específica de Mac

### LM Studio
```bash
# Descargar LM Studio para Mac
https://lmstudio.ai/

# Modelos recomendados (Apple Silicon)
- GPT-OSS-20B (12 GB) - Modelo médico
- Llama 3.2 3B (si tienes Mac Intel)

# Configuración GPU (Apple Silicon)
- Metal GPU: Habilitado
- GPU Layers: 20-25 (M1/M2)
- Context: 8192
```

### Tesseract Paths
```python
# El sistema detecta automáticamente, pero si falla:
# Homebrew (Apple Silicon)
/opt/homebrew/bin/tesseract

# Homebrew (Intel)
/usr/local/bin/tesseract
```

### Permisos de Carpetas
```bash
# Si hay errores de permisos
chmod -R 755 pdfs_patologia/
chmod -R 755 data/
chmod -R 755 EXCEL/
```

---

## 📊 Rendimiento en Mac

### Apple Silicon (M1/M2/M3)
```
✅ Excelente rendimiento
- OCR: 2-3 seg/página
- Auditoría PARCIAL: 5-10 seg/lote
- Auditoría COMPLETA: 30-60 seg/lote
- LM Studio con Metal GPU: Muy rápido
```

### Intel Mac
```
⚠️ Rendimiento moderado
- OCR: 5-7 seg/página
- Auditoría PARCIAL: 15-20 seg/lote
- Auditoría COMPLETA: 60-90 seg/lote
- Usar modelos más pequeños (3B-7B)
```

---

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'tkinter'"
```bash
# Reinstalar Python con framework Tkinter
brew install python-tk@3.11

# O usar Python oficial que incluye Tkinter
https://www.python.org/downloads/
```

### Error: "pytesseract.pytesseract.TesseractNotFoundError"
```bash
# Verificar instalación
which tesseract

# Si no está, instalar
brew install tesseract
```

### Error: "Permission denied" al ejecutar script
```bash
# Dar permisos de ejecución
chmod +x VERSION_MAC/iniciar_python_mac.sh
```

### Error: LM Studio no conecta
```bash
# Verificar servidor
curl http://localhost:1234/v1/models

# Reiniciar LM Studio
# Verificar firewall no bloquea puerto 1234
```

### App no abre (macOS Gatekeeper)
```bash
# Si macOS bloquea la app
# Sistema > Seguridad y Privacidad > Permitir app

# O desde terminal
xattr -cr /ruta/al/proyecto
```

---

## 📁 Estructura de Carpetas (Mac)

```
ProyectoHUV9GESTOR_ONCOLOGIA_automatizado/
├── ui.py                          # Aplicación principal
├── requirements.txt               # Dependencias
├── iniciar_python.bat            # Para Windows
│
├── VERSION_MAC/                   # ⭐ Archivos específicos Mac
│   ├── iniciar_python_mac.sh    # Launcher Mac
│   └── README_MAC.md            # Esta guía
│
├── venv_mac/                      # Virtual env Mac (auto-creado)
├── venv0/                         # Virtual env Windows (ignorar)
│
├── core/                          # Módulos principales
├── config/                        # Configuración
├── data/                          # Base de datos
├── pdfs_patologia/               # PDFs de entrada
├── EXCEL/                         # Exports Excel
└── documentacion_actualizada/    # Documentación
```

---

## 🔒 Seguridad en Mac

### FileVault
```bash
# Si usas FileVault, la BD está cifrada automáticamente
# No necesitas configuración adicional
```

### Permisos de Acceso
```bash
# macOS pedirá permisos para:
✅ Acceso a archivos (PDFs)
✅ Acceso a carpetas del sistema
✅ Acceso a red (LM Studio)

# Aceptar cuando se solicite
```

---

## 🎨 Temas y Apariencia

### Modo Oscuro
```
El sistema detecta automáticamente el tema de macOS:
- Modo Oscuro macOS → Tema 'darkly'
- Modo Claro macOS → Tema 'litera'
```

### Retina Display
```
✅ La UI se adapta automáticamente a pantallas Retina
✅ Fuentes escaladas correctamente
✅ Iconos en alta resolución
```

---

## 📦 Compilar para Mac (Opcional)

```bash
# Instalar PyInstaller
pip install pyinstaller

# Compilar aplicación
pyinstaller --onefile --windowed \
  --name "EVARISIS HUV" \
  --icon=imagenes/icon.icns \
  --add-data "config:config" \
  --add-data "core:core" \
  ui.py

# Resultado: dist/EVARISIS HUV.app
```

---

## 🔄 Actualización

```bash
# Actualizar código
git pull origin main

# Actualizar dependencias
source venv_mac/bin/activate
pip install --upgrade -r requirements.txt
deactivate

# Ejecutar
./VERSION_MAC/iniciar_python_mac.sh
```

---

## 📝 Notas Importantes

### Apple Silicon (M1/M2/M3)
- ✅ Usa Rosetta 2 si instalas Python x86
- ✅ Mejor rendimiento con Python ARM nativo
- ✅ LM Studio con Metal GPU muy rápido

### Intel Mac
- ⚠️ Usa modelos LLM más pequeños (3B-7B)
- ⚠️ OCR puede ser más lento
- ✅ Todo funciona correctamente

### macOS Monterey+
- ✅ Compatibilidad completa
- ✅ Modo oscuro nativo
- ✅ Notificaciones del sistema

---

## 🆘 Soporte

### Logs del Sistema
```bash
# Ver logs de Python
python3 ui.py 2>&1 | tee app.log

# Logs de Tesseract
tesseract --version

# Información del sistema
system_profiler SPSoftwareDataType
```

### Reportar Problemas
```
Si encuentras problemas específicos de Mac:
1. Versión de macOS
2. Tipo de Mac (Intel/Apple Silicon)
3. Logs de error
4. Captura de pantalla
```

---

## ✅ Checklist de Instalación

- [ ] Python 3.8+ instalado
- [ ] Homebrew instalado
- [ ] Tesseract OCR instalado
- [ ] LM Studio descargado y configurado
- [ ] Modelo GPT-OSS-20B descargado
- [ ] Script `iniciar_python_mac.sh` con permisos
- [ ] Virtual environment creado (`venv_mac/`)
- [ ] Dependencias instaladas
- [ ] Aplicación ejecuta correctamente

---

**Versión Mac**: 2.1.6
**Última actualización**: 7 de octubre de 2025
**Estado**: ✅ Completamente funcional en macOS
