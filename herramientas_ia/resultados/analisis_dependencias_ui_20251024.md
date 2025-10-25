# ANÁLISIS PROFUNDO DE DEPENDENCIAS UI - EVARISIS v6.0.5

**Generado:** 2025-10-24
**Nivel:** VERY THOROUGH

## VARIABLES CRÍTICAS EN App (ui.py)

### NUNCA CAMBIAR ESTOS NOMBRES:

1.  - DataFrame maestro, USADO POR export_system.py línea 445
2.  - Tabla principal, USADO POR export_system.py línea 437
3.  - Sheet widget, asignado a tree
4.  - Sistema exportación
5.  - Dashboard, USADO POR export_system líneas 373-376
6.  - USADO POR ventana_resultados
7.  - USADO POR ventana_auditoria_ia línea 838

## MÉTODOS CRÍTICOS

### NUNCA RENOMBRAR NI CAMBIAR FIRMA:

1.  - USADO POR process_with_audit.py línea 290
2.  - Debe aceptar DataFrame
3.  - Callback auditoría
4.  - USADO POR export_system línea 358
5.  - USADO POR export_system línea 890
6.  en EnhancedExportSystem - USADO POR ui línea 4314
7.  en EnhancedExportSystem - USADO POR ui línea 4383

## WIDGETS CRÍTICOS EN EnhancedDatabaseDashboard

1.  - USADO POR export_system línea 376
2.  - USADO POR ui líneas 1932, 1945

## BINDINGS CRÍTICOS

### NUNCA MODIFICAR:

1. 
2. 
3. Todos los bindings de scroll en ventanas emergentes

## REGLAS ABSOLUTAS

❌ PROHIBIDO:
- Renombrar variables críticas listadas
- Cambiar firmas de métodos públicos
- Eliminar atributos usados por otros módulos
- Modificar bindings de eventos críticos

✅ PERMITIDO (con precaución):
- Añadir métodos nuevos con nombres no conflictivos
- Añadir atributos opcionales
- Modificar UI interna sin afectar API pública

## CHECKLIST ANTES DE MODIFICAR UI

- [ ] He verificado que NO afecto variables críticas
- [ ] He verificado que NO cambio firmas de métodos públicos
- [ ] He verificado que NO modifico bindings
- [ ] He probado exportación, dashboard y ventanas emergentes

---

**NOTA FINAL:** Si dudas sobre un cambio, NO LO HAGAS.
