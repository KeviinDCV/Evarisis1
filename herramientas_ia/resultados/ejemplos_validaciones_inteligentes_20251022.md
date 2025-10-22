# GUÍA DE USO: Validaciones Inteligentes - auditor_sistema.py

**Fecha**: 2025-10-22
**Autor**: core-editor (agente especializado)
**Propósito**: Ejemplos prácticos de uso de las 3 funciones de validación implementadas

---

## INTRODUCCIÓN

Las 3 funciones de validación inteligente implementadas permiten detectar errores críticos en campos clave de la base de datos, comparando semánticamente contra el contenido real del PDF. Esta guía proporciona ejemplos prácticos de uso.

---

## FUNCIÓN 1: _validar_diagnostico_coloracion_inteligente()

### Caso de Uso 1: Caso de Mama con Componentes Completos

**Entrada**:
```python
datos_bd = {
    'DIAGNOSTICO_COLORACION': None  # Campo no existe aún
}

texto_ocr = '''
DIAGNÓSTICO
CARCINOMA DUCTAL INFILTRANTE, GRADO II DE NOTTINGHAM.
INVASIÓN LINFOVASCULAR: NEGATIVA
INVASIÓN PERINEURAL: NEGATIVA
'''

resultado = auditor._validar_diagnostico_coloracion_inteligente(datos_bd, texto_ocr)
```

**Salida Esperada**:
```json
{
  "estado": "OK",
  "componentes_validos": ["diagnostico_base", "grado_nottingham", "invasion_linfovascular", "invasion_perineural"],
  "componentes_faltantes": ["carcinoma_in_situ"],
  "sugerencia": "Diagnóstico coloración detectado con 4/5 componentes. Crear columna DIAGNOSTICO_COLORACION en BD (FASE 2)."
}
```

### Caso de Uso 2: Caso con Componentes Incompletos

**Entrada**:
```python
texto_ocr = '''
DIAGNÓSTICO
ADENOCARCINOMA MODERADAMENTE DIFERENCIADO
'''

resultado = auditor._validar_diagnostico_coloracion_inteligente(datos_bd, texto_ocr)
```

**Salida Esperada**:
```json
{
  "estado": "WARNING",
  "componentes_validos": ["diagnostico_base"],
  "componentes_faltantes": ["grado_nottingham", "invasion_linfovascular", "invasion_perineural", "carcinoma_in_situ"],
  "sugerencia": "Diagnóstico coloración parcial (1/5 componentes). Verificar PDF."
}
```

### Interpretación de Estados

| Estado | Condición | Acción Recomendada |
|--------|-----------|-------------------|
| **OK** | ≥3/5 componentes | Preparar FASE 2: Crear columna DIAGNOSTICO_COLORACION |
| **WARNING** | 1-2/5 componentes | Verificar PDF, ajustar función de detección |
| **ERROR** | 0/5 componentes | Verificar OCR, revisar estructura del PDF |
| **PENDING** | Campo no existe en BD | Normal, se creará en FASE 2 |

---

## FUNCIÓN 2: _validar_diagnostico_principal_inteligente()

### Caso de Uso 1: Diagnóstico Correcto (Sin Contaminación)

**Entrada**:
```python
datos_bd = {
    'Diagnostico Principal': 'CARCINOMA DUCTAL INFILTRANTE'
}

texto_ocr = '''
DIAGNÓSTICO
1. CARCINOMA DUCTAL INFILTRANTE
2. GRADO II DE NOTTINGHAM
3. INVASIÓN LINFOVASCULAR: NEGATIVA
'''

resultado = auditor._validar_diagnostico_principal_inteligente(datos_bd, texto_ocr)
```

**Salida Esperada**:
```json
{
  "estado": "WARNING",
  "valor_bd": "CARCINOMA DUCTAL INFILTRANTE",
  "valor_esperado": "1. CARCINOMA DUCTAL INFILTRANTE",
  "tiene_contaminacion": false,
  "linea_correcta_pdf": 1,
  "sugerencia": "DIAGNOSTICO_PRINCIPAL parcialmente correcto (diferencia en numeración)."
}
```

### Caso de Uso 2: Diagnóstico Contaminado (ERROR CRÍTICO)

**Entrada**:
```python
datos_bd = {
    'Diagnostico Principal': 'CARCINOMA DUCTAL INFILTRANTE GRADO II DE NOTTINGHAM. INVASIÓN LINFOVASCULAR: NEGATIVA'
}

texto_ocr = '''
DIAGNÓSTICO
1. CARCINOMA DUCTAL INFILTRANTE
2. GRADO II DE NOTTINGHAM
3. INVASIÓN LINFOVASCULAR: NEGATIVA
'''

resultado = auditor._validar_diagnostico_principal_inteligente(datos_bd, texto_ocr)
```

**Salida Esperada**:
```json
{
  "estado": "ERROR",
  "valor_bd": "CARCINOMA DUCTAL INFILTRANTE GRADO II DE NOTTINGHAM. INVASIÓN LINFOVASCULAR: NEGATIVA",
  "valor_esperado": "CARCINOMA DUCTAL INFILTRANTE",
  "tiene_contaminacion": true,
  "contaminacion_detectada": ["NOTTINGHAM", "GRADO", "INVASIÓN LINFOVASCULAR"],
  "linea_correcta_pdf": 1,
  "sugerencia": "DIAGNOSTICO_PRINCIPAL contaminado con datos del estudio M: NOTTINGHAM, GRADO, INVASIÓN LINFOVASCULAR.\nDebe contener SOLO el diagnóstico histológico sin grado ni invasiones.\nCorrección: Modificar extractor extract_principal_diagnosis() en medical_extractor.py"
}
```

### Interpretación de Contaminación

**Keywords Prohibidos en DIAGNOSTICO_PRINCIPAL**:
- `NOTTINGHAM` → Indica grado (pertenece al estudio M)
- `GRADO` → Pertenece al estudio M
- `INVASIÓN LINFOVASCULAR` → Pertenece al estudio M
- `INVASIÓN PERINEURAL` → Pertenece al estudio M
- `INVASIÓN VASCULAR` → Pertenece al estudio M

**DIAGNOSTICO_PRINCIPAL debe contener SOLO**:
- Diagnóstico histológico principal
- Ejemplo: "CARCINOMA DUCTAL INFILTRANTE"
- Ejemplo: "ADENOCARCINOMA MODERADAMENTE DIFERENCIADO"

---

## FUNCIÓN 3: _validar_factor_pronostico_inteligente()

### Caso de Uso 1: Factor Pronóstico Correcto (100% Cobertura)

**Entrada**:
```python
datos_bd = {
    'Factor pronostico': 'HER2 (0), Receptor de Estrógeno (100%), Receptor de Progesterona (100%), Ki-67 (20%)'
}

texto_ocr = '''
DESCRIPCIÓN MICROSCÓPICA
HER2: 0
Receptor de Estrógeno: 100% (intensidad fuerte)
Receptor de Progesterona: 100% (intensidad fuerte)
Ki-67: 20%
'''

resultado = auditor._validar_factor_pronostico_inteligente(datos_bd, texto_ocr)
```

**Salida Esperada**:
```json
{
  "estado": "OK",
  "tiene_contaminacion": false,
  "biomarcadores_pdf": ["HER2", "Receptor de Estrógeno", "Receptor de Progesterona", "Ki-67"],
  "biomarcadores_en_bd": ["HER2", "Receptor de Estrógeno", "Receptor de Progesterona", "Ki-67"],
  "cobertura": 100.0,
  "sugerencia": "FACTOR_PRONOSTICO con buena cobertura (100%)"
}
```

### Caso de Uso 2: Factor Pronóstico Contaminado (ERROR CRÍTICO)

**Entrada**:
```python
datos_bd = {
    'Factor pronostico': 'GRADO II DE NOTTINGHAM. INVASIÓN LINFOVASCULAR: NEGATIVA. HER2 (0), Ki-67 (20%)'
}

texto_ocr = '''
DESCRIPCIÓN MICROSCÓPICA
HER2: 0
Ki-67: 20%
'''

resultado = auditor._validar_factor_pronostico_inteligente(datos_bd, texto_ocr)
```

**Salida Esperada**:
```json
{
  "estado": "ERROR",
  "tiene_contaminacion": true,
  "contaminacion_detectada": ["NOTTINGHAM", "GRADO", "INVASIÓN LINFOVASCULAR"],
  "biomarcadores_pdf": ["HER2", "Ki-67"],
  "biomarcadores_en_bd": ["HER2", "Ki-67"],
  "cobertura": 100.0,
  "sugerencia": "FACTOR_PRONOSTICO contaminado con datos del estudio M: NOTTINGHAM, GRADO, INVASIÓN LINFOVASCULAR.\nDebe contener SOLO biomarcadores de IHQ.\nCorrección: Modificar extractor extract_factor_pronostico() en medical_extractor.py para filtrar datos del estudio M"
}
```

### Caso de Uso 3: Factor Pronóstico Vacío con Biomarcadores en PDF (ERROR)

**Entrada**:
```python
datos_bd = {
    'Factor pronostico': 'N/A'
}

texto_ocr = '''
DESCRIPCIÓN MICROSCÓPICA
HER2: 0
Ki-67: 20%
'''

resultado = auditor._validar_factor_pronostico_inteligente(datos_bd, texto_ocr)
```

**Salida Esperada**:
```json
{
  "estado": "ERROR",
  "valor_bd": "N/A",
  "biomarcadores_pdf": ["HER2", "Ki-67"],
  "biomarcadores_en_bd": [],
  "cobertura": 0.0,
  "sugerencia": "FACTOR_PRONOSTICO vacío pero se detectaron 2 biomarcadores en PDF:\nHER2, Ki-67\nCorrección: Modificar extractor extract_factor_pronostico() en medical_extractor.py"
}
```

### Interpretación de Cobertura

| Cobertura | Estado | Significado |
|-----------|--------|-------------|
| ≥80% | **OK** | Buena cobertura, sistema extrae correctamente |
| 50-79% | **WARNING** | Cobertura media, algunos biomarcadores faltan |
| <50% | **ERROR** | Cobertura baja, problema crítico de extracción |

### Keywords Prohibidos en FACTOR_PRONOSTICO

- `NOTTINGHAM`
- `GRADO`
- `INVASIÓN LINFOVASCULAR`
- `INVASIÓN PERINEURAL`
- `BIEN DIFERENCIADO`
- `MODERADAMENTE DIFERENCIADO`
- `POBREMENTE DIFERENCIADO`

**FACTOR_PRONOSTICO debe contener SOLO**:
- Biomarcadores de IHQ con sus valores
- Ejemplo: "HER2 (0), Ki-67 (20%)"
- Ejemplo: "Receptor de Estrógeno (100%), Receptor de Progesterona (80%)"

---

## INTEGRACIÓN EN AUDITORÍA PRINCIPAL

### Ejemplo de Integración Completa

```python
def auditar_caso(self, numero_caso: str, nivel: str = 'basico') -> Dict:
    """Audita un caso completo incluyendo validaciones inteligentes"""

    # 1. Obtener datos de BD
    datos_bd = self._obtener_datos_bd(numero_caso)

    # 2. Obtener texto OCR del PDF
    texto_ocr = self._leer_ocr_completo(numero_caso)

    # 3. Ejecutar validaciones inteligentes
    validaciones = {}

    if texto_ocr:
        # Validación 1: DIAGNOSTICO_COLORACION
        validaciones['diagnostico_coloracion'] = self._validar_diagnostico_coloracion_inteligente(
            datos_bd, texto_ocr
        )

        # Validación 2: DIAGNOSTICO_PRINCIPAL
        validaciones['diagnostico_principal'] = self._validar_diagnostico_principal_inteligente(
            datos_bd, texto_ocr
        )

        # Validación 3: FACTOR_PRONOSTICO
        validaciones['factor_pronostico'] = self._validar_factor_pronostico_inteligente(
            datos_bd, texto_ocr
        )

    # 4. Detectar errores críticos
    errores_criticos = []
    if validaciones['diagnostico_principal']['estado'] == 'ERROR':
        errores_criticos.append({
            'campo': 'DIAGNOSTICO_PRINCIPAL',
            'tipo': 'CONTAMINACION' if validaciones['diagnostico_principal']['tiene_contaminacion'] else 'VACIO',
            'sugerencia': validaciones['diagnostico_principal']['sugerencia']
        })

    if validaciones['factor_pronostico']['estado'] == 'ERROR':
        errores_criticos.append({
            'campo': 'FACTOR_PRONOSTICO',
            'tipo': 'CONTAMINACION' if validaciones['factor_pronostico']['tiene_contaminacion'] else 'COBERTURA_BAJA',
            'sugerencia': validaciones['factor_pronostico']['sugerencia']
        })

    # 5. Generar reporte
    return {
        'numero_caso': numero_caso,
        'validaciones_inteligentes': validaciones,
        'errores_criticos': errores_criticos,
        'estado_general': 'ERROR' if errores_criticos else 'OK'
    }
```

### Ejemplo de Salida Completa

```json
{
  "numero_caso": "IHQ250980",
  "validaciones_inteligentes": {
    "diagnostico_coloracion": {
      "estado": "OK",
      "componentes_validos": ["diagnostico_base", "grado_nottingham", "invasion_linfovascular", "invasion_perineural"],
      "componentes_faltantes": ["carcinoma_in_situ"]
    },
    "diagnostico_principal": {
      "estado": "WARNING",
      "tiene_contaminacion": false,
      "valor_bd": "CARCINOMA DUCTAL INFILTRANTE",
      "valor_esperado": "1. CARCINOMA DUCTAL INFILTRANTE"
    },
    "factor_pronostico": {
      "estado": "OK",
      "tiene_contaminacion": false,
      "cobertura": 100.0
    }
  },
  "errores_criticos": [],
  "estado_general": "OK"
}
```

---

## CASOS DE USO POR TIPO DE CÁNCER

### Cáncer de Mama
**Biomarcadores típicos**: HER2, Receptor de Estrógeno, Receptor de Progesterona, Ki-67
**Componentes estudio M**: Grado Nottingham (I-III), Invasión linfovascular, Invasión perineural

**Validación crítica**: Separar diagnóstico histológico de grado e invasiones

### Cáncer de Pulmón
**Biomarcadores típicos**: TTF-1, CK7, CK20, p53, Ki-67
**Componentes estudio M**: Grado de diferenciación, Invasión vascular, Invasión perineural

**Validación crítica**: Diferenciar adenocarcinoma/carcinoma escamoso de grado y invasiones

### Tumores Neuroendocrinos
**Biomarcadores típicos**: Sinaptofisina, Cromogranina A, CD56, Ki-67
**Componentes estudio M**: Grado tumoral (G1-G3), Invasión linfovascular

**Validación crítica**: Separar diagnóstico neuroendocrino de grado Ki-67 y invasiones

---

## COMANDOS DE PRUEBA RÁPIDA

### Probar Validación DIAGNOSTICO_COLORACION
```bash
python -c "
from herramientas_ia.auditor_sistema import AuditorSistema
auditor = AuditorSistema()
datos_bd = {}
texto_ocr = 'DIAGNÓSTICO\nCARCINOMA DUCTAL INFILTRANTE GRADO II DE NOTTINGHAM.\nINVASIÓN LINFOVASCULAR: NEGATIVA'
resultado = auditor._validar_diagnostico_coloracion_inteligente(datos_bd, texto_ocr)
print(resultado)
"
```

### Probar Validación DIAGNOSTICO_PRINCIPAL
```bash
python -c "
from herramientas_ia.auditor_sistema import AuditorSistema
auditor = AuditorSistema()
datos_bd = {'Diagnostico Principal': 'CARCINOMA DUCTAL INFILTRANTE'}
texto_ocr = 'DIAGNÓSTICO\n1. CARCINOMA DUCTAL INFILTRANTE'
resultado = auditor._validar_diagnostico_principal_inteligente(datos_bd, texto_ocr)
print(resultado)
"
```

### Probar Validación FACTOR_PRONOSTICO
```bash
python -c "
from herramientas_ia.auditor_sistema import AuditorSistema
auditor = AuditorSistema()
datos_bd = {'Factor pronostico': 'HER2 (0), Ki-67 (20%)'}
texto_ocr = 'DESCRIPCIÓN MICROSCÓPICA\nHER2: 0\nKi-67: 20%'
resultado = auditor._validar_factor_pronostico_inteligente(datos_bd, texto_ocr)
print(resultado)
"
```

---

## TROUBLESHOOTING

### Problema 1: Componentes del Estudio M No Se Detectan

**Síntoma**: `componentes_faltantes` tiene 4-5 elementos
**Causa**: Función de detección `_detectar_diagnostico_coloracion_inteligente()` necesita ajustes
**Solución**: Verificar formato del PDF (lista numerada vs párrafo continuo), ajustar patrones regex

### Problema 2: Falsos Positivos en Contaminación

**Síntoma**: `tiene_contaminacion: true` pero el campo está correcto
**Causa**: Keywords demasiado genéricos (ej: "GRADO" puede aparecer en otros contextos)
**Solución**: Refinar lista de keywords prohibidos, agregar contexto (ej: "GRADO DE NOTTINGHAM" en lugar de solo "GRADO")

### Problema 3: Cobertura Siempre 0%

**Síntoma**: `cobertura: 0.0` incluso con biomarcadores presentes
**Causa**: Lista de `biomarcadores_conocidos` no incluye variantes del caso
**Solución**: Expandir lista de biomarcadores conocidos, agregar variantes (ej: "ER" además de "Receptor de Estrógeno")

---

## CONCLUSIÓN

Las 3 funciones de validación inteligente proporcionan un mecanismo robusto para detectar errores críticos en campos clave de la base de datos. Su integración en la auditoría principal permitirá:

1. **Detección automática** de contaminación cruzada entre estudios
2. **Validación semántica** de diagnósticos y factores pronósticos
3. **Sugerencias específicas** de corrección para cada error detectado
4. **Preparación para FASE 2** con validación de DIAGNOSTICO_COLORACION

**Estado**: Funciones implementadas y probadas exitosamente
**Próximo paso**: Integrar en `auditar_caso()` para auditoría completa

---

**Autor**: core-editor (agente especializado)
**Fecha**: 2025-10-22
**Versión**: 6.0.0
