# Mapa Mental — Arquitectura EVARISIS Gestor H.U.V v3.2

## 🏗️ NÚCLEO CENTRAL: EVARISIS Gestor H.U.V

### 📱 CAPA DE PRESENTACIÓN
```
🎨 Interfaz Usuario (ui.py)
├── TTKBootstrap Framework
├── Sistema Navegación Flotante
├── Gestión Temas (litera/darkly)
├── Threading No-bloqueante
└── Componentes Reutilizables
```

### 🔧 CAPA DE LÓGICA DE NEGOCIO
```
⚙️ Sistema Principal (huv_ocr_sistema_definitivo.py)
├── Coordinador Módulos
├── Gestión Dependencias
├── Patrón Mediator
└── Punto Entrada Único

🔍 Motor OCR (ocr_processing.py)
├── Estrategia Híbrida
│   ├── PyMuPDF (Texto Nativo)
│   └── Tesseract (Documentos Escaneados)
├── Configuración Adaptativa DPI
└── Multi-idioma

🧬 Procesador IHQ (procesador_ihq_biomarcadores.py)
├── Biomarcadores Críticos
│   ├── HER2
│   ├── Ki-67
│   ├── RE/RP
│   ├── PD-L1
│   └── P16
├── Pipeline Procesamiento
└── Validación Médica
```

### 💾 CAPA DE DATOS
```
🗃️ Gestor BD (database_manager.py)
├── SQLite Optimizado
├── Esquema 167 Campos
├── Control Duplicados
├── Transacciones ACID
└── Backups Automáticos
```

### 🤖 CAPA DE AUTOMATIZACIÓN
```
🌐 Bot Web (huv_web_automation.py)
├── Selenium WebDriver
├── ChromeDriver Management
├── Portal HUV Integration
├── Credenciales Seguras
└── Logs Detallados
```

### 📊 MÓDULOS ANALÍTICOS
```
📈 Dashboard Analytics
├── Matplotlib/Seaborn
├── KPIs Tiempo Real
├── Filtros Contextuales
├── Modo Pantalla Completa
└── Exportaciones Excel

📋 Visualización Datos
├── TreeView Estilizado
├── Búsqueda Dinámica
├── Detalles Registro
└── Actualización Automática
```

## 🔄 FLUJOS DE INFORMACIÓN

### Flujo Principal de Procesamiento
```
📄 PDFs → 🔍 OCR → 🧬 IHQ → 💾 SQLite → 📊 Dashboard
```

### Flujo de Automatización Web
```
👤 Usuario → 🌐 Portal HUV → 📄 Descarga → 🔍 Procesamiento → 💾 Almacenamiento
```

### Flujo de Análisis
```
💾 Base Datos → 📊 Procesamiento → 📈 Visualización → 📋 Reportes
```

## 🏢 ECOSISTEMA EXTERNO

### Integraciones
```
🏥 Portal HUV Patología
├── huvpatologia.qhorte.com
├── Autenticación Usuario
└── Descarga Automática PDFs

📊 Sistemas Hospitalarios
├── SERVINTE (Futuro)
├── Sistemas Auditoria
└── APIs Interoperabilidad
```

### Dependencias Tecnológicas
```
🐍 Python Ecosystem
├── TTKBootstrap (UI Framework)
├── Selenium (Web Automation)
├── PyMuPDF (PDF Processing)
├── Pandas (Data Manipulation)
├── Matplotlib (Visualizations)
└── SQLite (Database)
```

## 🎯 AUDIENCIAS Y BENEFICIOS

### Médicos Oncológicos
```
🏥 Dashboard Biomarcadores
├── HER2 Status
├── Ki-67 Index
├── Hormone Receptors
└── Decision Support
```

### Dirección Hospitalaria
```
📊 Métricas Operativas
├── Reducción Tiempo 85%
├── ROI Análisis
├── KPIs Rendimiento
└── Optimización Recursos
```

### Investigadores Clínicos
```
🔬 Dataset Científico
├── 167 Campos Estructurados
├── Trazabilidad Completa
├── Estudios Longitudinales
└── Publicaciones Científicas
```

### Equipo Desarrollo
```
👩‍💻 Arquitectura Modular
├── Código Mantenible
├── Documentación Completa
├── Versionamiento Semántico
└── Iteraciones Ágiles
```

## 🚀 EVOLUCIÓN ARQUITECTÓNICA

### v2.x → v3.2 (Actual)
```
📈 Mejoras Implementadas
├── CustomTkinter → TTKBootstrap
├── Navegación Flotante
├── Rendimiento +40%
├── Memoria -25%
└── Estabilidad ++
```

### Roadmap Futuro
```
🔮 v4.0+ Planned
├── API REST Completa
├── Integración SERVINTE
├── Motor Auditoría IA
├── Microservicios Architecture
└── Cloud Deployment
```

---

*Mapa Mental generado para visualizar la arquitectura completa del sistema EVARISIS Gestor H.U.V v3.2*  
*Hospital Universitario del Valle - Septiembre 2025*