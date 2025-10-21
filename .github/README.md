# 📁 Carpeta .github

## Propósito

Esta carpeta contiene configuraciones para GitHub y herramientas de desarrollo, específicamente para GitHub Copilot.

## Archivos

### `copilot-instructions.md`

**Propósito**: Instrucciones automáticas para GitHub Copilot al trabajar en este proyecto.

**Funcionamiento**: GitHub Copilot lee automáticamente este archivo cuando:
- Abres el proyecto en VS Code
- Usas el chat de Copilot
- Generas código con Copilot
- Solicitas explicaciones o ayuda

**Contenido**: 
- Reglas estrictas del proyecto
- Comandos CLI disponibles
- Estructura del proyecto
- Flujos de trabajo correctos
- Prohibiciones y mejores prácticas

**Versión**: Sincronizada con la versión 4.2.1 del sistema

## Archivos Fuente

Las instrucciones de Copilot se generaron consolidando:
- `herramientas_ia/REGLAS_ESTRICTAS_IA.md`
- `herramientas_ia/GUIA_COMPORTAMIENTO_IA.md`
- `herramientas_ia/GUIA_TECNICA_COMPLETA.md`
- `herramientas_ia/README.md`

## Actualización

Cuando se actualicen las guías en `herramientas_ia/`, se debe actualizar también `copilot-instructions.md` para mantener la sincronización.

## Ubicaciones del Archivo

El archivo existe en dos ubicaciones para compatibilidad:
1. `.github/copilot-instructions.md` (ubicación estándar)
2. `.copilot-instructions.md` (raíz del proyecto, respaldo)

---

**Última actualización**: 4 de octubre de 2025  
**Sistema**: EVARISIS Gestor Oncológico HUV v4.2.1
