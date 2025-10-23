# 🔄 Workflows Maestros del Sistema EVARISIS

**8 workflows completos para operaciones comunes**

---

## WORKFLOW 1: Procesamiento Completo de Caso Nuevo

```
1. Usuario procesa PDF → Sistema EVARISIS extrae datos

2. system-diagnostician verifica salud del sistema proactivamente

3. data-auditor ejecuta auditoría completa automáticamente:
   a. Valida TODOS los biomarcadores mencionados en PDF
   b. Valida IHQ_ORGANO (¿es órgano correcto o texto erróneo?)
   c. Valida DIAGNOSTICO_PRINCIPAL (¿es legible y correcto?)
   d. Valida FACTOR_PRONOSTICO (¿está completo o solo tiene Ki-67?)
   e. Valida IHQ_ESTUDIOS_SOLICITADOS (¿capturó todos los biomarcadores?)
   f. Calcula precisión REAL vs precisión reportada
   g. Detecta "falsa completitud" si el sistema reporta 100% pero hay errores

4. Si precisión REAL < 90% o hay campos críticos incorrectos:
   a. data-auditor identifica campos problemáticos con evidencia del PDF
   b. data-auditor proporciona sugerencias de corrección (archivo + función + regex)
   c. lm-studio-connector sugiere correcciones IA (dry-run)
   d. Usuario revisa errores críticos y aprueba correcciones
   e. lm-studio-connector aplica correcciones de alta confianza
   f. core-editor corrige extractores si hay patrones sistemáticos

5. data-auditor re-valida precisión post-corrección (todos los campos)

6. database-manager almacena caso validado
```

**Agentes:** system-diagnostician → data-auditor → lm-studio-connector → core-editor → database-manager

---

## WORKFLOW 2: Actualización de Versión + Documentación Completa

```
1. Usuario: "Actualiza a v6.0.3 con corrección del auditor"

2. Claude pregunta detalles:
   - ¿Qué cambios tiene v6.0.3?
   - ¿Contexto de esta iteración?
   - ¿Validación técnica?

3. Claude invoca version-manager:

   Acciones internas:
   a. Actualiza config/version_info.py → v6.0.3
   b. Actualiza README.md, CLAUDE.md (menciones de versión)
   c. Genera/Actualiza documentacion/CHANGELOG.md (ACUMULATIVO)
   d. Genera/Actualiza documentacion/BITACORA_DE_ACERCAMIENTOS.md (ACUMULATIVO)
   e. TERMINA

4. Claude reporta archivos actualizados

5. Claude pregunta: "¿Generar documentación completa de v6.0.3?"

6. Usuario: "Sí"

7. Claude invoca documentation-specialist-HUV:

   Acciones internas:
   a. Verifica que CHANGELOG.md y BITACORA.md existan
   b. Lee config/version_info.py → v6.0.3
   c. Lee CHANGELOG.md → Extrae cambios de v6.0.3
   d. Lee BITACORA.md → Extrae contexto
   e. Genera documentación completa (REESCRITURA):
      - INFORME_GLOBAL_PROYECTO.md
      - README.md
      - NOTEBOOK_LM_CONSOLIDADO_TECNICO.md
      - analisis/*.md (7 archivos)
      - comunicados/*.md (4 archivos)
   f. NO TOCA CHANGELOG ni BITACORA (generados por version-manager)
   g. TERMINA

8. Claude reporta resultado final con ubicación de archivos

9. FIN
```

**Agentes:** version-manager → documentation-specialist-HUV

**IMPORTANTE:**
- version-manager genera CHANGELOG/BITACORA (acumulativos)
- documentation-specialist-HUV genera RESTO (reescritura)

---

## WORKFLOW 3: Mantenimiento Preventivo Mensual

```
1. system-diagnostician ejecuta health check completo

2. system-diagnostician analiza complejidad ciclomática

3. system-diagnostician detecta code smells

4. Si CC > 10 en funciones críticas:
   a. core-editor sugiere refactorizaciones
   b. core-editor versiona archivos (backup)
   c. core-editor aplica refactorización
   d. system-diagnostician valida que no hay breaking changes

5. database-manager crea backup de BD

6. database-manager optimiza BD (VACUUM + ANALYZE)

7. data-auditor ejecuta auditoría completa de todos los casos

8. data-auditor analiza tendencias de errores

9. Si errores sistemáticos detectados:
   a. core-editor corrige extractores problemáticos
```

**Agentes:** system-diagnostician → core-editor → database-manager → data-auditor

---

## WORKFLOW 4: Agregar Nuevo Biomarcador al Sistema

```
1. Usuario: "Agrega BCL2 al sistema"

2. system-diagnostician verifica salud del sistema

3. database-manager verifica que columna IHQ_BCL2 no existe

4. core-editor ejecuta: --agregar-biomarcador BCL2 --variantes "BCL-2,BCL 2"

   Esto automáticamente:
   a. Agrega función extract_bcl2() a biomarker_extractor.py
   b. Agrega entrada al MAPEO_BIOMARCADORES
   c. Migra schema BD (nueva columna IHQ_BCL2)
   d. Genera test unitario

5. core-editor valida sintaxis Python

6. system-diagnostician verifica que no hay breaking changes

7. database-manager confirma que columna IHQ_BCL2 existe

8. Usuario procesa casos con BCL2

9. data-auditor valida que BCL2 se extrae correctamente
```

**Agentes:** system-diagnostician → database-manager → core-editor → data-auditor

---

## WORKFLOW 5: Búsqueda y Análisis de Casos Similares

```
1. Usuario: "Busca casos similares a IHQ250988 para comparar"

2. database-manager busca caso de referencia: --buscar IHQ250988

3. database-manager identifica características:
   - Órgano
   - Género
   - Edad
   - Biomarcadores

4. database-manager ejecuta búsqueda avanzada con criterios similares

5. database-manager muestra casos similares encontrados

6. Usuario solicita estadísticas de biomarcadores en esos casos

7. database-manager genera análisis de tendencias

8. data-auditor valida precisión de casos similares

9. database-manager exporta resultados a JSON/Excel
```

**Agentes:** database-manager → data-auditor

---

## WORKFLOW 6: Corrección IA Masiva con Validación

```
1. Usuario: "Aplica correcciones IA a los últimos 10 casos"

2. lm-studio-connector verifica que LM Studio está activo

3. database-manager lista últimos 10 casos procesados

4. lm-studio-connector ejecuta validación en lote (dry-run primero)

5. lm-studio-connector agrupa correcciones por criticidad:
   - CRITICA: Requiere revisión manual
   - IMPORTANTE: Confianza ≥ 0.90
   - OPCIONAL: Confianza ≥ 0.85

6. Usuario revisa correcciones CRITICAS manualmente

7. lm-studio-connector aplica correcciones IMPORTANTES y OPCIONALES aprobadas

8. data-auditor valida precisión post-corrección

9. database-manager actualiza estadísticas de completitud

10. system-diagnostician verifica integridad de BD
```

**Agentes:** lm-studio-connector → database-manager → data-auditor → system-diagnostician

---

## WORKFLOW 7: Rollback de Emergencia

```
1. Usuario reporta: "El último cambio rompió la extracción de HER2"

2. system-diagnostician ejecuta diagnóstico de componentes

3. core-editor identifica archivo modificado: biomarker_extractor.py

4. core-editor ejecuta rollback inmediato (restaura desde backups/)

5. database-manager restaura backup de BD (si necesario)

6. core-editor reprocesa casos afectados

7. data-auditor valida que HER2 ahora se extrae correctamente

8. system-diagnostician confirma sistema restaurado

9. core-editor analiza qué causó el problema

10. core-editor sugiere solución correcta con simulación previa
```

**Agentes:** system-diagnostician → core-editor → database-manager → data-auditor

---

## WORKFLOW 8: Debugging de Comportamiento IA Anómalo

```
1. Usuario reporta: "Ki-67 siempre se extrae mal, la IA no lo corrige bien"

2. Claude invoca lm-studio-connector para diagnóstico:
   - Verifica estado servidor LM Studio
   - Verifica modelo cargado
   - Verifica latencia y tokens/segundo
   - TERMINA con estado OK/ERROR

3. Claude invoca lm-studio-connector --analizar-prompts:
   - Lee prompts actuales
   - Analiza calidad (0-10): claridad, especificidad, ejemplos
   - Detecta contradicciones
   - Genera reporte en herramientas_ia/resultados/
   - TERMINA

4. Claude muestra problemas detectados:
   - Falta de ejemplos concretos
   - Contradicciones en instrucciones
   - Scores bajos en especificidad

5. Claude pregunta: "¿Simular mejora del prompt?"

6. Usuario: "Sí, simula primero"

7. Claude invoca lm-studio-connector --simular:
   - Crea prompt mejorado (en memoria)
   - Prueba extracción con caso problemático
   - Compara ANTES vs DESPUÉS
   - Genera reporte comparativo
   - Muestra mejora detectada
   - TERMINA

8. Usuario: "Sí, aplica los cambios"

9. Claude invoca lm-studio-connector --editar-prompt --aplicar:
   - Crea backup automático en backups/prompts/
   - Aplica cambios al prompt
   - Valida sintaxis
   - Reprocesa caso de prueba
   - Genera reporte de cambios
   - TERMINA

10. Claude pregunta: "¿Actualizar versión del sistema?"

11. Usuario: "Sí, actualiza a v6.0.4"

12. Claude invoca version-manager:
    - Lee reporte de cambios de lm-studio-connector
    - Actualiza VERSION_INFO a v6.0.4
    - Crea entrada en CHANGELOG.md
    - Actualiza README.md, CLAUDE.md
    - TERMINA

13. FIN
```

**Archivos generados:**
- backups/prompts/*.txt.bak (backup)
- core/prompts/*.txt (mejorado)
- herramientas_ia/resultados/analisis_prompts_*.json
- herramientas_ia/resultados/simulacion_*.md
- herramientas_ia/resultados/cambios_prompts_*.md
- config/version_info.py (actualizado)
- documentacion/CHANGELOG.md (actualizado)

**Agentes:** lm-studio-connector → version-manager

**IMPORTANTE:**
- lm-studio-connector diagnostica, simula y aplica cambios a prompts/IA
- SIEMPRE hace backup antes de modificar
- SIEMPRE simula antes de aplicar (dry-run)
- NO modifica extractores (responsabilidad de core-editor)

---

**Última actualización:** 2025-10-22
